from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
import httpx
import asyncio

from app.database import get_db
from app.models.item import Item

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter()

# GW2 API configuration
GW2_API_BASE = "https://api.guildwars2.com/v2"
TIMEOUT = httpx.Timeout(30.0, connect=10.0)  # 30s read timeout, 10s connect timeout

async def fetch_item_from_api(item_id: int) -> dict:
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

@router.get("/items/{item_id}")
async def get_item(item_id: int, db: Session = Depends(get_db)):
    """Get a single item by ID"""
    logger.info(f"Fetching item {item_id}")
    
    # Try to get from database first
    item = db.query(Item).filter(Item.id == item_id).first()
    if item:
        return item.to_dict()
    
    # If not in database, fetch from API
    logger.info(f"Item {item_id} not found in database, fetching from API")
    api_data = await fetch_item_from_api(item_id)
    if not api_data:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    
    # Create and save the item
    item = create_item_from_api_data(api_data)
    db.add(item)
    db.commit()
    
    return item.to_dict()

@router.get("/items")
async def get_items(ids: str = None, db: Session = Depends(get_db)):
    """Get multiple items by IDs"""
    if not ids:
        raise HTTPException(status_code=400, detail="No item IDs provided")
    
    try:
        item_ids = [int(id_str) for id_str in ids.split(',')]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid item ID format")
    
    logger.info(f"Fetching {len(item_ids)} items")
    
    # Get all items that exist in database
    items = {
        item.id: item 
        for item in db.query(Item).filter(Item.id.in_(item_ids)).all()
    }
    
    # Fetch missing items from API
    missing_ids = [id for id in item_ids if id not in items]
    if missing_ids:
        logger.info(f"Fetching {len(missing_ids)} missing items from API")
        async with httpx.AsyncClient() as client:
            responses = await asyncio.gather(*[
                fetch_item_from_api(item_id)
                for item_id in missing_ids
            ])
            
            for api_data in responses:
                if api_data:  # Skip if API returned None (404)
                    item = create_item_from_api_data(api_data)
                    items[item.id] = item
                    db.add(item)
            
            db.commit()
    
    # Return items in the same order as requested
    return [items[id].to_dict() if id in items else None for id in item_ids]

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