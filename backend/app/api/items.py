from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
import httpx
import asyncio
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.item import Item

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter()

# GW2 API configuration
GW2_API_BASE = "https://api.guildwars2.com/v2"
TIMEOUT = httpx.Timeout(30.0, connect=10.0)  # 30s read timeout, 10s connect timeout

# --- New global variables for Future-based synchronization ---
item_futures = {}  # Stores asyncio.Future for item_ids currently being fetched/stored
item_futures_lock = asyncio.Lock() # Protects access to item_futures
# ---

async def fetch_item_from_api(item_id: int) -> Optional[dict]:
    """Fetch item data from the GW2 API"""
    url = f"{GW2_API_BASE}/items/{item_id}"
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.get(url)
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()

def create_item_from_api_data(api_data: dict) -> Item:
    """Create an Item model instance from GW2 API data"""
    # Extract base fields
    base_fields = {
        "id": api_data["id"],
        "name": api_data["name"],
        "description": api_data.get("description"),
        "type": api_data["type"],
        "level": api_data["level"],
        "rarity": api_data["rarity"],
        "vendor_value": api_data["vendor_value"],
        "game_types": api_data.get("game_types", []),
        "flags": api_data.get("flags", []),
        "restrictions": api_data.get("restrictions", [])
    }
    
    # Move all other fields to details
    details = dict(api_data)
    for field in base_fields.keys():
        details.pop(field, None)
    
    return Item(
        **base_fields,
        details=details
    )

async def _get_or_create_item_from_db(item_id: int, db: Session) -> Item:
    """
    Core logic: Gets an item from DB. If not found, fetches from API, stores in DB,
    and ensures only one concurrent operation per item_id using a Future.
    Returns the persisted Item model instance. Raises HTTPException or other exceptions on failure.
    """
    # 1. Initial DB check (non-critical section for lock)
    item_model = db.query(Item).filter(Item.id == item_id).first()
    if item_model:
        return item_model

    # 2. Future management for fetching/creating
    active_future: asyncio.Future
    is_leader = False

    async with item_futures_lock:
        if item_id in item_futures:
            active_future = item_futures[item_id]
        else:
            active_future = asyncio.Future()
            item_futures[item_id] = active_future
            is_leader = True
    
    if is_leader:
        try:
            logger.info(f"Leader for item {item_id}: Fetching from API and storing.")
            api_data = await fetch_item_from_api(item_id)
            if not api_data:
                exc = HTTPException(status_code=404, detail=f"Item {item_id} not found in API")
                active_future.set_exception(exc)
                raise exc

            persisted_item = create_item_from_api_data(api_data)
            db.add(persisted_item)
            try:
                db.commit()
                db.refresh(persisted_item)
                active_future.set_result(persisted_item)
                return persisted_item
            except IntegrityError:
                db.rollback()
                logger.warning(f"Leader for item {item_id} encountered IntegrityError during commit. Re-querying from DB.")
                item_after_conflict = db.query(Item).filter(Item.id == item_id).first()
                if item_after_conflict:
                    active_future.set_result(item_after_conflict)
                    return item_after_conflict
                else:
                    exc = HTTPException(status_code=500, detail=f"DB conflict for item {item_id}, but item not retrievable post-conflict.")
                    active_future.set_exception(exc)
                    raise exc
        except Exception as e:
            if not active_future.done():
                active_future.set_exception(e)
            raise
        finally:
            async with item_futures_lock:
                if item_id in item_futures and item_futures[item_id] is active_future:
                    del item_futures[item_id]
    else:
        # Follower awaits the future resolved by the leader
        logger.info(f"Follower for item {item_id}: Awaiting leader's result.")
        try:
            awaited_item_model = await active_future
            return awaited_item_model
        except Exception as e:
            logger.error(f"Follower for item {item_id} received error from future: {type(e).__name__} - {str(e)}")
            # Re-raise the exception so the caller (endpoint handler) can process it
            raise

@router.get("/items/{item_id}")
async def get_item(item_id: int, db: Session = Depends(get_db)):
    """Get a single item by ID. Fetches from API and stores if not found."""
    logger.info(f"Endpoint /items/{item_id} requested.")
    # _get_or_create_item_from_db can raise HTTPException or other errors.
    # FastAPI will handle these appropriately (e.g., return 404, 500).
    item_model = await _get_or_create_item_from_db(item_id, db)
    return item_model.to_dict()

@router.get("/items")
async def get_items(ids: str = None, db: Session = Depends(get_db)):
    """Get multiple items by IDs. Fetches from API and stores if not found."""
    if not ids:
        raise HTTPException(status_code=400, detail="No item IDs provided")
    
    requested_item_ids_ordered: List[int] = []
    try:
        requested_item_ids_ordered = [int(id_str) for id_str in ids.split(',')]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid item ID format")

    # Process unique IDs to avoid redundant tasks, but preserve order for final output
    unique_item_ids = sorted(list(set(requested_item_ids_ordered)))

    logger.info(f"Endpoint /items?ids=... requested for {len(requested_item_ids_ordered)} items (unique: {len(unique_item_ids)}).")

    # Create tasks for fetching each unique item
    tasks_for_unique_ids = [_get_or_create_item_from_db(uid, db) for uid in unique_item_ids]
    
    # Execute all tasks concurrently and get results (Item models or exceptions)
    results_for_unique_ids = await asyncio.gather(*tasks_for_unique_ids, return_exceptions=True)

    # Map results back to unique IDs for easy lookup
    processed_results_map = {uid: result for uid, result in zip(unique_item_ids, results_for_unique_ids)}
        
    # Build the final list in the originally requested order
    final_response_list = []
    for req_id in requested_item_ids_ordered:
        result = processed_results_map.get(req_id)
        
        if isinstance(result, Item):
            final_response_list.append(result.to_dict())
        elif isinstance(result, HTTPException) and result.status_code == 404:
            logger.info(f"Item {req_id} not found (404) for bulk request via _get_or_create_item_from_db.")
            final_response_list.append(None)
        elif isinstance(result, Exception): # Includes other HTTPErrors or any other exception
            logger.error(f"Error processing item {req_id} in bulk: {type(result).__name__} - {str(result)}. Returning None for this item.")
            final_response_list.append(None)
        else: # Should ideally not happen if gather returns items or exceptions
            logger.warning(f"Unexpected result type for item {req_id} in bulk: {type(result)}. Returning None.")
            final_response_list.append(None)
            
    return final_response_list

@router.get("/items/search")
async def search_items(
    query: str,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Search items by name"""
    logger.info(f"Searching items with query: {query}")
    
    items = db.query(Item).filter(
        Item.name.ilike(f"%{query}%")
    ).limit(limit).all()
    
    return [item.to_dict() for item in items] 