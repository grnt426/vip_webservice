from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any, Optional, List, Tuple
import logging

from app import models
from app.schemas import user_schemas
from app.database import get_db
from app.gw2_client import GW2Client
import httpx

router = APIRouter()
logger = logging.getLogger(__name__)

EXPECTED_API_KEY_PERMISSIONS = ["account", "guilds", "characters"]

async def _get_gw2_account_and_permissions(api_key: str, gw2_client: GW2Client) -> Tuple[Optional[str], List[str], Optional[str]]:
    """Fetches account details from /v2/account and permissions from /v2/tokeninfo."""
    account_name: Optional[str] = None
    permissions: List[str] = []
    account_id: Optional[str] = None # GW2 Account GUID

    # 1. Fetch account details from /v2/account
    account_url = f"{gw2_client.base_url}/account"
    headers = {"Authorization": f"Bearer {api_key}"}
    logger.info(f"Fetching account data from: {account_url}")
    try:
        async with httpx.AsyncClient(timeout=gw2_client.timeout) as client:
            response = await client.get(account_url, headers=headers)
        
        if response.status_code != 200:
            error_detail = "Failed to fetch account details from GW2 (non-200_STATUS_CODE)."
            try:
                raw_response_text = response.text
                logger.error(f"GW2 API /account error. Status: {response.status_code}, Response: {raw_response_text}")
                error_detail = response.json().get("text", error_detail)
            except Exception as json_exc:
                logger.error(f"GW2 API /account error. Status: {response.status_code}, Could not parse JSON: {raw_response_text}. Error: {json_exc}")
            # Don't raise immediately, try to get permissions first if this fails
        else:
            account_data = response.json()
            account_name = account_data.get("name") # This is the In-Game Name User.1234
            account_id = account_data.get("id") # This is the account GUID
            logger.info(f"GW2 API /account success. Account Name: '{account_name}', Account ID: '{account_id}'")

    except httpx.RequestError as exc:
        logger.error(f"Error communicating with GW2 API /account: {str(exc)}", exc_info=True)
        # Allow to proceed to fetch permissions, but account_name might be None
    except Exception as e:
        logger.error(f"Unexpected error during GW2 API /account call: {str(e)}", exc_info=True)
        # Allow to proceed to fetch permissions

    # 2. Fetch permissions from /v2/tokeninfo
    token_info_url = f"{gw2_client.base_url}/tokeninfo"
    logger.info(f"Fetching token info from: {token_info_url}")
    try:
        async with httpx.AsyncClient(timeout=gw2_client.timeout) as client:
            response = await client.get(token_info_url, headers=headers) # headers are the same
        
        if response.status_code != 200:
            error_detail = "Invalid API key or GW2 API error (non-200_STATUS_CODE for /tokeninfo)."
            try:
                raw_response_text = response.text
                logger.error(f"GW2 API /tokeninfo error. Status: {response.status_code}, Response: {raw_response_text}")
                error_detail = response.json().get("text", error_detail)
            except Exception as json_exc:
                logger.error(f"GW2 API /tokeninfo error. Status: {response.status_code}, Could not parse JSON: {raw_response_text}. Error: {json_exc}")
            # If /account also failed and account_name is still None, this is a critical failure.
            if not account_name:
                 raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to validate API key with GW2: {error_detail}")
            # Otherwise, we have account_name but failed to get permissions. Log and continue, permission check will fail later.
            logger.warning(f"Could not retrieve permissions for API key (ending ...{api_key[-4:]}). Account name '{account_name}' was retrieved. Permission check will likely fail.")
        else:
            token_data = response.json()
            permissions = token_data.get("permissions", [])
            api_key_label = token_data.get("name", "N/A") # This is the API key's own name/label
            logger.info(f"GW2 API /tokeninfo success. API Key Label: '{api_key_label}', Permissions: {permissions}")
            
    except httpx.RequestError as exc:
        logger.error(f"Error communicating with GW2 API /tokeninfo: {str(exc)}", exc_info=True)
        if not account_name: # If /account also failed
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Error communicating with Guild Wars 2 API (/tokeninfo): {str(exc)}")
    except Exception as e:
        logger.error(f"Unexpected error during GW2 API /tokeninfo call: {str(e)}", exc_info=True)
        if not account_name: # If /account also failed
             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred while validating API key details.")

    # If account_name is still None after trying /account, the key is fundamentally problematic for our needs.
    if not account_name:
        logger.error(f"Could not retrieve Guild Wars 2 account name using API key (ending ...{api_key[-4:]}). Both /account and /tokeninfo might have failed or /account did not return a name.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not retrieve your Guild Wars 2 account name using this API key. Please ensure it is a valid key with 'account' permission.")

    return account_name, permissions, account_id

async def _get_validated_account_from_api_key(
    api_key: str, 
    db: Session, 
    gw2_client: GW2Client,
    check_existing_user: bool = True,
    expected_account_name: Optional[str] = None
) -> models.Account:
    # Use the helper function to get account details
    actual_account_name, permissions, _ = await _get_gw2_account_and_permissions(api_key, gw2_client)

    # The rest of the logic uses actual_account_name (which is the in-game name)
    if not actual_account_name:
        # This case should be caught by the helper, but as a safeguard:
        logger.warning(f"API key validation failed: No actual account name returned. API Key ending: ...{api_key[-4:]}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="API key is invalid or did not provide an identifiable Guild Wars 2 account name."
        )
    
    if expected_account_name and actual_account_name != expected_account_name:
        logger.warning(f"API key validation failed: Account name mismatch. Expected: '{expected_account_name}', Got from /v2/account: '{actual_account_name}'. API Key ending: ...{api_key[-4:]}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"API key is valid, but it is for account '{actual_account_name}', not the expected account '{expected_account_name}'. Please use the correct API key or re-validate."
        )

    missing_permissions = [p for p in EXPECTED_API_KEY_PERMISSIONS if p not in permissions]
    if missing_permissions:
        logger.warning(f"API key validation failed for account '{actual_account_name}': Missing permissions: {missing_permissions}. API Key ending: ...{api_key[-4:]}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"API key for '{actual_account_name}' is missing required permissions: {', '.join(missing_permissions)}. Please ensure it has at least 'account', 'guilds', and 'characters' permissions."
        )
    
    logger.info(f"API key validated for account '{actual_account_name}' with sufficient permissions. Checking database...")

    # Check if the account exists in our database
    account = db.query(models.Account).filter(models.Account.current_account_name == actual_account_name).first()
    if not account:
        logger.warning(f"API key validation failed for account '{actual_account_name}': No Account found in DB with this name. API Key ending: ...{api_key[-4:]}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No account found in our database with the name '{actual_account_name}'. Please ensure you are a member of a registered guild and your account has been scanned."
        )

    # Check if the account has any guild memberships
    if not account.memberships:
        logger.warning(f"API key validation failed for account '{actual_account_name}': Account exists but has no guild memberships. API Key ending: ...{api_key[-4:]}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account '{actual_account_name}' exists but is not a member of any registered guilds."
        )

    if check_existing_user:
        if account.user:
            logger.warning(f"API key validation failed for account '{actual_account_name}': Account already has a user registration. API Key ending: ...{api_key[-4:]}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A user account already exists for '{actual_account_name}'."
            )
    
    logger.info(f"Account '{actual_account_name}' found in DB and eligible (or existence check skipped).")
    return account

@router.post("/validate-api-key", response_model=user_schemas.APIKeyValidateResponse)
async def validate_api_key(
    payload: user_schemas.APIKeyValidateRequest,
    db: Session = Depends(get_db),
    gw2_client: GW2Client = Depends(GW2Client)
):
    account = await _get_validated_account_from_api_key(
        api_key=payload.api_key, 
        db=db, 
        gw2_client=gw2_client,
        check_existing_user=True
    )
    return user_schemas.APIKeyValidateResponse(
        username=account.current_account_name, 
        message="API key is valid and account is eligible for registration."
    )

@router.post("/register", response_model=user_schemas.UserResponse)
async def register_user(
    payload: user_schemas.UserCreateRequest,
    db: Session = Depends(get_db),
    gw2_client: GW2Client = Depends(GW2Client)
):
    account = await _get_validated_account_from_api_key(
        api_key=payload.api_key,
        db=db,
        gw2_client=gw2_client,
        check_existing_user=True,
        expected_account_name=payload.username
    )

    new_user = models.User(
        username=account.current_account_name, 
        account_id=account.id
    )
    new_user.set_password(payload.password)
    new_user.set_api_key(payload.api_key)
    # Consider setting default roles: new_user.roles = ["member"]

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user 