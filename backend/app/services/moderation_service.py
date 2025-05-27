from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import logging

from app.models.account import Account
from app.models.account_name_history import AccountNameHistory
from app.models.mod_action import ModAction
from app.models.guild_standing import GuildStanding
from app.config.moderation import (
    get_action_type_info, get_violation_info, get_points_for_violation,
    should_auto_disable, should_suggest_temp_ban, POINT_THRESHOLDS
)

logger = logging.getLogger(__name__)

class ModerationService:
    """Service for handling moderation actions and point system."""
    
    @staticmethod
    def create_mod_action(
        db: Session,
        account_name: str,
        action_type: str,
        reason: str,
        created_by_user_id: int,
        violation_type: Optional[str] = None,
        points: Optional[int] = None,
        duration_hours: Optional[int] = None,
        severity: Optional[int] = None,
        details: Optional[str] = None
    ) -> ModAction:
        """Create a moderation action, creating account if needed."""
        
        # Get action type info
        action_info = get_action_type_info(action_type)
        
        # Handle points
        points_to_add = None
        if violation_type:
            # Get points from violation type
            points_to_add = get_points_for_violation(violation_type)
        elif points is not None:
            # Use explicitly provided points
            points_to_add = points
        elif action_info.get("requires_points"):
            raise ValueError(f"Action type '{action_type}' requires points or violation type")
        
        # Try to find or create the account
        account = db.query(Account).filter(
            Account.current_account_name == account_name
        ).first()
        
        if not account:
            # Create a "tracked" account even if not in guild
            logger.info(f"Creating new account for moderation: {account_name}")
            account = Account(
                current_account_name=account_name,
                account_source="moderation",
                created_at=datetime.utcnow()
            )
            db.add(account)
            db.flush()
            
            # Add name history
            history = AccountNameHistory(
                account_id=account.id,
                account_name=account_name,
                valid_from=account.created_at
            )
            db.add(history)
            db.flush()
        
        # Get or create standing
        standing = db.query(GuildStanding).filter(
            GuildStanding.account_id == account.id
        ).first()
        
        if not standing:
            standing = GuildStanding(account_id=account.id)
            db.add(standing)
            db.flush()
        
        # Calculate expiration
        expires_at = None
        if duration_hours:
            expires_at = datetime.utcnow() + timedelta(hours=duration_hours)
        
        # Create the mod action
        mod_action = ModAction(
            account_id=account.id,
            account_name=account_name,
            action_type=action_type,
            violation_type=violation_type,
            points_added=points_to_add,
            severity=severity or action_info["severity"],
            reason=reason,
            details=details,
            created_by_user_id=created_by_user_id,
            expires_at=expires_at
        )
        
        # Add points and check for auto-disable
        auto_disabled = False
        if points_to_add:
            standing.current_points += points_to_add
            
            # Check if we should auto-disable
            if should_auto_disable(standing.current_points) and not standing.is_disabled:
                standing.is_disabled = True
                auto_disabled = True
                logger.warning(f"Account {account_name} auto-disabled at {standing.current_points} points")
            
            # Check if we should suggest temp ban
            elif should_suggest_temp_ban(standing.current_points):
                logger.info(f"Account {account_name} has reached temp ban threshold ({standing.current_points} points)")
        
        mod_action.auto_disabled_account = auto_disabled
        
        db.add(mod_action)
        db.commit()
        
        logger.info(
            f"Created {action_type} for {account_name} "
            f"(points: {'+' + str(points_to_add) if points_to_add else 'none'}, "
            f"total: {standing.current_points})"
        )
        
        return mod_action
    
    @staticmethod
    def lift_mod_action(
        db: Session,
        mod_action_id: int,
        lifted_by_user_id: int
    ) -> ModAction:
        """Lift a moderation action."""
        mod_action = db.query(ModAction).filter(ModAction.id == mod_action_id).first()
        
        if not mod_action:
            raise ValueError(f"Mod action {mod_action_id} not found")
        
        if not mod_action.is_active:
            raise ValueError(f"Mod action {mod_action_id} is already inactive")
        
        # If this action added points, we don't remove them
        # Points are only reduced through decay
        
        # If this action auto-disabled the account, check if we can re-enable
        if mod_action.auto_disabled_account:
            standing = db.query(GuildStanding).filter(
                GuildStanding.account_id == mod_action.account_id
            ).first()
            
            if standing and not should_auto_disable(standing.current_points):
                standing.is_disabled = False
                logger.info(f"Re-enabled account {mod_action.account_name} after lifting action")
        
        mod_action.lift(lifted_by_user_id)
        db.commit()
        
        logger.info(f"Lifted mod action {mod_action_id} by user {lifted_by_user_id}")
        
        return mod_action
    
    @staticmethod
    def check_account_standing(db: Session, account_name: str) -> Dict:
        """Check if an account can perform actions (join guild, etc)."""
        account = db.query(Account).filter(
            Account.current_account_name == account_name
        ).first()
        
        if not account:
            return {
                "allowed": True,
                "is_banned": False,
                "is_disabled": False,
                "current_points": 0,
                "active_blocks": [],
                "warnings": []
            }
        
        active_blocks = []
        warnings = []
        
        for action in account.active_punishments:
            action_data = {
                "id": action.id,
                "type": action.action_type,
                "violation_type": action.violation_type,
                "points_added": action.points_added,
                "reason": action.reason,
                "created_at": action.created_at,
                "expires_at": action.expires_at,
                "severity": action.severity
            }
            
            if action.is_blocking:
                active_blocks.append(action_data)
            else:
                warnings.append(action_data)
        
        standing = account.standing
        
        return {
            "allowed": len(active_blocks) == 0 and (not standing or not standing.is_disabled),
            "is_banned": len(active_blocks) > 0,
            "is_disabled": standing.is_disabled if standing else False,
            "current_points": standing.current_points if standing else 0,
            "active_blocks": active_blocks,
            "warnings": warnings,
            "account_id": account.id,
            "last_decay_at": standing.last_decay_at if standing else None
        }
    
    @staticmethod
    def get_account_moderation_history(
        db: Session,
        account_name: str,
        include_expired: bool = True,
        limit: Optional[int] = None
    ) -> List[ModAction]:
        """Get moderation history for an account."""
        account = db.query(Account).filter(
            Account.current_account_name == account_name
        ).first()
        
        if not account:
            return []
        
        query = db.query(ModAction).filter(
            ModAction.account_id == account.id
        )
        
        if not include_expired:
            query = query.filter(ModAction.is_active == True)
        
        query = query.order_by(ModAction.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @staticmethod
    def get_recent_mod_actions(
        db: Session,
        limit: int = 50,
        action_type: Optional[str] = None,
        active_only: bool = False
    ) -> List[ModAction]:
        """Get recent moderation actions across all accounts."""
        query = db.query(ModAction)
        
        if action_type:
            query = query.filter(ModAction.action_type == action_type)
        
        if active_only:
            query = query.filter(ModAction.is_active == True)
        
        query = query.order_by(ModAction.created_at.desc()).limit(limit)
        
        return query.all()
    
    @staticmethod
    def expire_old_actions(db: Session) -> int:
        """Mark expired temporary actions as inactive. Returns count of expired actions."""
        now = datetime.utcnow()
        
        expired_actions = db.query(ModAction).filter(
            ModAction.is_active == True,
            ModAction.expires_at != None,
            ModAction.expires_at <= now
        ).all()
        
        count = 0
        for action in expired_actions:
            action.is_active = False
            count += 1
        
        if count > 0:
            db.commit()
            logger.info(f"Expired {count} moderation actions")
        
        return count 