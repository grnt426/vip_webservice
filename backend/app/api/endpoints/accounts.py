from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging

from app import models
from app.schemas import account_schemas
from app.database import get_db
from app.services.account_merge import AccountMergeService

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/accounts/search", response_model=List[account_schemas.AccountSearchResult])
async def search_accounts(
    name: str,
    db: Session = Depends(get_db)
):
    """
    Search for accounts by name (current or historical).
    This is useful for finding accounts that may have changed names.
    """
    if len(name) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query must be at least 3 characters long"
        )
    
    accounts = AccountMergeService.find_accounts_by_name(db, name)
    
    return [
        account_schemas.AccountSearchResult(
            id=account.id,
            current_account_name=account.current_account_name,
            has_user=account.user is not None,
            guild_count=len(account.memberships),
            name_history=[
                account_schemas.AccountNameHistoryItem(
                    account_name=history.account_name,
                    valid_from=history.valid_from,
                    valid_to=history.valid_to
                )
                for history in account.name_history
            ]
        )
        for account in accounts
    ]

@router.post("/accounts/merge", response_model=account_schemas.AccountMergeResponse)
async def merge_accounts(
    payload: account_schemas.AccountMergeRequest,
    db: Session = Depends(get_db),
    # TODO: Add authentication/authorization check here
    # current_user: models.User = Depends(get_current_user_with_role("officer"))
):
    """
    Merge two accounts when a name change is detected.
    The new account (with the new name) will be merged into the old account.
    
    Requires officer privileges.
    """
    # TODO: Check if current user has officer role
    # if "officer" not in current_user.roles and not current_user.is_superuser:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Only officers can merge accounts"
    #     )
    
    success, message = AccountMergeService.merge_accounts(
        db,
        old_account_id=payload.old_account_id,
        new_account_id=payload.new_account_id,
        # merged_by=current_user.username
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return account_schemas.AccountMergeResponse(
        success=success,
        message=message
    )

@router.get("/accounts/{account_id}", response_model=account_schemas.AccountDetail)
async def get_account_details(
    account_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific account."""
    account = db.query(models.Account).filter(models.Account.id == account_id).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account with ID {account_id} not found"
        )
    
    return account_schemas.AccountDetail(
        id=account.id,
        current_account_name=account.current_account_name,
        created_at=account.created_at,
        updated_at=account.updated_at,
        has_user=account.user is not None,
        user_username=account.user.username if account.user else None,
        guilds=[
            account_schemas.GuildMembershipInfo(
                guild_id=membership.guild_id,
                guild_name=membership.guild.name if membership.guild else "Unknown",
                rank=membership.rank,
                joined=membership.joined,
                wvw_member=membership.wvw_member
            )
            for membership in account.memberships
        ],
        name_history=[
            account_schemas.AccountNameHistoryItem(
                account_name=history.account_name,
                valid_from=history.valid_from,
                valid_to=history.valid_to
            )
            for history in account.name_history
        ]
    ) 