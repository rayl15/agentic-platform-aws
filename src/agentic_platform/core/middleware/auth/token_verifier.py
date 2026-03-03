import jwt
from jwt.exceptions import PyJWKClientError, InvalidKeyError
import os
import logging
from typing import Any, Optional
from abc import ABC, abstractmethod
from fastapi import HTTPException
logger = logging.getLogger(__name__)

REGION = os.getenv('AWS_DEFAULT_REGION')
USER_POOL_ID = os.getenv('COGNITO_USER_POOL_ID')

class TokenVerifier(ABC):
    @abstractmethod
    def validate_token(self, token: str) -> Optional[Any]:
        pass

class CognitoTokenVerifier(TokenVerifier):
    def __init__(self):
        '''
        Initialize the CognitoTokenVerifier

        PyJWKCLient automatically caches the JWKS set.
        '''
        self.jwks_url = f'https://cognito-idp.{REGION}.amazonaws.com/{USER_POOL_ID}/.well-known/jwks.json'
        self.jwks_client = jwt.PyJWKClient(self.jwks_url)

    def validate_token(self, token) -> Optional[Any]:
        try:
            # PyJWKClient automatically fetches the key matching the token's kid
            signing_key = self.jwks_client.get_signing_key_from_jwt(token)
            
            # Use the signing key to decode and validate the token
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],  # Specify the algorithms you expect
                options={"verify_aud": False}  # Customize verification options as needed
            )
            return payload
        except PyJWKClientError as e:
            # Handle JWKS client errors (e.g., key not found)
            logger.error(f"JWKS client error: {e}")
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        except InvalidKeyError as e:
            # Handle key validation errors
            logger.error(f"Invalid key error: {e}")
            raise HTTPException(status_code=401, detail="Invalid token signature")
        except jwt.PyJWTError as e:
            # Handle general JWT errors
            logger.error(f"JWT validation error: {e}")
            raise HTTPException(status_code=401, detail=str(e))
