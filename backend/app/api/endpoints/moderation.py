from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app import models
from app.schemas import moderation_schemas
from app.database import get_db
from app.services.moderation_service import ModerationService
from app.config.moderation import MOD_ACTION_TYPES

router = APIRouter()
logger = logging.getLogger(__name__)

# TODO: Replace with actual authentication when implemented
def get_current_user_stub(db: Session = Depends(get_db)) -> models.User:
    """Temporary stub for getting current user. Replace with real auth."""
    # For now, return the first user or create a test user
    user = db.query(models.User).first()
    if not user:
        # Create a test admin user
        test_account = models.Account.get_or_create(db, "TestAdmin.1234", source="test")
        user = models.User(
            username="TestAdmin.1234",
            account_id=test_account.id,
            roles=["admin", "officer"],
            is_superuser=True
        )
        user.set_password("testpassword")
        user.set_api_key("test-api-key")
        db.add(user)
        db.commit()
    return user

@router.post("/action", response_model=moderation_schemas.ModActionResponse)
async def create_moderation_action(
    payload: moderation_schemas.ModActionCreateRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_stub)
):
    """
    Create a new moderation action.
    Requires officer privileges.
    """
    # Check permissions
    if "officer" not in current_user.roles and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Officer role required."
        )
    
    try:
        action = ModerationService.create_mod_action(
            db=db,
            account_name=payload.account_name,
            action_type=payload.action_type,
            reason=payload.reason,
            created_by_user_id=current_user.id,
            duration_hours=payload.duration_hours,
            severity=payload.severity,
            details=payload.details
        )
        
        return moderation_schemas.ModActionResponse(**action.to_dict())
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating mod action: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create moderation action"
        )

@router.post("/lift", response_model=moderation_schemas.ModActionResponse)
async def lift_moderation_action(
    payload: moderation_schemas.ModActionLiftRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_stub)
):
    """
    Lift (cancel) a moderation action.
    Requires officer privileges.
    """
    # Check permissions
    if "officer" not in current_user.roles and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Officer role required."
        )
    
    try:
        action = ModerationService.lift_mod_action(
            db=db,
            mod_action_id=payload.mod_action_id,
            lifted_by_user_id=current_user.id
        )
        
        return moderation_schemas.ModActionResponse(**action.to_dict())
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error lifting mod action: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to lift moderation action"
        )

@router.get("/check/{account_name}", response_model=moderation_schemas.AccountStandingResponse)
async def check_account_standing(
    account_name: str,
    db: Session = Depends(get_db)
):
    """
    Check if an account is banned or has restrictions.
    This is a public endpoint used during registration/login.
    """
    standing = ModerationService.check_account_standing(db, account_name)
    return moderation_schemas.AccountStandingResponse(**standing)

@router.get("/history/{account_name}", response_model=moderation_schemas.ModActionHistoryResponse)
async def get_moderation_history(
    account_name: str,
    include_expired: bool = Query(True, description="Include expired/lifted actions"),
    limit: Optional[int] = Query(None, ge=1, le=100, description="Limit number of results"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_stub)
):
    """
    Get moderation history for an account.
    Requires authentication.
    """
    actions = ModerationService.get_account_moderation_history(
        db=db,
        account_name=account_name,
        include_expired=include_expired,
        limit=limit
    )
    
    return moderation_schemas.ModActionHistoryResponse(
        actions=[moderation_schemas.ModActionResponse(**action.to_dict()) for action in actions],
        total=len(actions)
    )

@router.get("/recent", response_model=moderation_schemas.ModActionHistoryResponse)
async def get_recent_mod_actions(
    limit: int = Query(50, ge=1, le=100, description="Number of actions to return"),
    action_type: Optional[str] = Query(None, description="Filter by action type"),
    active_only: bool = Query(False, description="Only show active actions"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_stub)
):
    """
    Get recent moderation actions across all accounts.
    Requires officer privileges.
    """
    # Check permissions
    if "officer" not in current_user.roles and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Officer role required."
        )
    
    actions = ModerationService.get_recent_mod_actions(
        db=db,
        limit=limit,
        action_type=action_type,
        active_only=active_only
    )
    
    return moderation_schemas.ModActionHistoryResponse(
        actions=[moderation_schemas.ModActionResponse(**action.to_dict()) for action in actions],
        total=len(actions)
    )

@router.get("/action-types", response_model=moderation_schemas.ModActionTypesResponse)
async def get_action_types():
    """
    Get available moderation action types and their properties.
    Public endpoint.
    """
    action_types = {}
    for name, info in MOD_ACTION_TYPES.items():
        action_types[name] = moderation_schemas.ModActionTypeInfo(
            name=name,
            **info
        )
    
    return moderation_schemas.ModActionTypesResponse(action_types=action_types)

@router.post("/expire-actions")
async def expire_old_actions(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_stub)
):
    """
    Manually trigger expiration of old temporary actions.
    This is usually done automatically but can be triggered manually.
    Requires admin privileges.
    """
    # Check permissions
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Admin role required."
        )
    
    count = ModerationService.expire_old_actions(db)
    
    return {
        "message": f"Expired {count} moderation actions",
        "count": count
    } 