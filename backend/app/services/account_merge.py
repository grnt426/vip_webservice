from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, Tuple
import logging

from app.models.account import Account
from app.models.account_name_history import AccountNameHistory
from app.models.guild_membership import GuildMembership
from app.models.user import User

logger = logging.getLogger(__name__)

class AccountMergeService:
    """Service for handling account merges when name changes are detected."""
    
    @staticmethod
    def merge_accounts(
        db: Session,
        old_account_id: int,
        new_account_id: int,
        merged_by: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Merge new_account into old_account, preserving guild memberships and history.
        
        Args:
            db: Database session
            old_account_id: The ID of the account to keep (original account)
            new_account_id: The ID of the account to merge and delete
            merged_by: Optional username of who performed the merge
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Get both accounts
            old_account = db.query(Account).filter(Account.id == old_account_id).first()
            new_account = db.query(Account).filter(Account.id == new_account_id).first()
            
            if not old_account:
                return False, f"Old account with ID {old_account_id} not found"
            if not new_account:
                return False, f"New account with ID {new_account_id} not found"
            
            logger.info(f"Merging account '{new_account.current_account_name}' (ID: {new_account_id}) "
                       f"into '{old_account.current_account_name}' (ID: {old_account_id})")
            
            # Step 1: Update account name history
            # Close the old name's validity period
            current_history = db.query(AccountNameHistory).filter(
                AccountNameHistory.account_id == old_account_id,
                AccountNameHistory.valid_to.is_(None)
            ).first()
            
            if current_history:
                current_history.valid_to = datetime.utcnow()
            
            # Add the new name to the old account's history
            new_history = AccountNameHistory(
                account_id=old_account_id,
                account_name=new_account.current_account_name,
                valid_from=datetime.utcnow()
            )
            db.add(new_history)
            
            # Step 2: Handle guild memberships
            old_memberships = {m.guild_id: m for m in old_account.memberships}
            new_memberships = list(new_account.memberships)  # Create a list copy
            
            merged_guilds = []
            moved_guilds = []
            
            for new_membership in new_memberships:
                if new_membership.guild_id in old_memberships:
                    # Both accounts are in this guild - keep the better membership
                    old_membership = old_memberships[new_membership.guild_id]
                    
                    # Compare and update if new membership has better data
                    if AccountMergeService._should_use_new_membership(old_membership, new_membership):
                        old_membership.rank = new_membership.rank
                        old_membership.joined = new_membership.joined
                        old_membership.wvw_member = new_membership.wvw_member
                    
                    merged_guilds.append(new_membership.guild_id)
                    # Delete the duplicate new membership
                    db.delete(new_membership)
                else:
                    # Only new account is in this guild - move membership
                    new_membership.account_id = old_account_id
                    moved_guilds.append(new_membership.guild_id)
            
            # Step 3: Handle user account if exists
            if new_account.user:
                if old_account.user:
                    # Both have user accounts - this is a conflict
                    return False, (f"Both accounts have user registrations. "
                                 f"Old account user: {old_account.user.username}, "
                                 f"New account user: {new_account.user.username}")
                else:
                    # Move user account to old account
                    new_account.user.account_id = old_account_id
                    logger.info(f"Moved user account '{new_account.user.username}' to account ID {old_account_id}")
            
            # Step 4: Update the old account's current name
            old_account.current_account_name = new_account.current_account_name
            old_account.updated_at = datetime.utcnow()
            
            # Step 5: Delete the new account (cascades to delete any remaining relationships)
            db.delete(new_account)
            
            # Commit all changes
            db.commit()
            
            message = (f"Successfully merged account '{new_account.current_account_name}' into "
                      f"'{old_account.current_account_name}'. "
                      f"Merged {len(merged_guilds)} guild memberships, "
                      f"moved {len(moved_guilds)} guild memberships.")
            
            logger.info(message)
            return True, message
            
        except Exception as e:
            db.rollback()
            error_msg = f"Failed to merge accounts: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg
    
    @staticmethod
    def _should_use_new_membership(old_membership: GuildMembership, new_membership: GuildMembership) -> bool:
        """
        Determine if the new membership data is better than the old.
        
        This is a simple heuristic - you can customize based on your needs.
        """
        # If one has a join date and the other doesn't, prefer the one with join date
        if new_membership.joined and not old_membership.joined:
            return True
        if old_membership.joined and not new_membership.joined:
            return False
        
        # If both have join dates, prefer the earlier one (they joined first with that account)
        if new_membership.joined and old_membership.joined:
            if new_membership.joined < old_membership.joined:
                return True
        
        # Could add more logic here based on rank hierarchy, WvW status, etc.
        return False
    
    @staticmethod
    def find_accounts_by_name(db: Session, account_name: str) -> list[Account]:
        """
        Find all accounts that have ever used this account name.
        
        Args:
            db: Database session
            account_name: The account name to search for
            
        Returns:
            List of Account objects that have used this name
        """
        # First check current names
        current_accounts = db.query(Account).filter(
            Account.current_account_name == account_name
        ).all()
        
        # Then check historical names
        historical_accounts = db.query(Account).join(AccountNameHistory).filter(
            AccountNameHistory.account_name == account_name
        ).distinct().all()
        
        # Combine and deduplicate
        all_accounts = list({account.id: account for account in current_accounts + historical_accounts}.values())
        
        return all_accounts 