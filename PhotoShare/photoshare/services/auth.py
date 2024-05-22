from typing import Optional

from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from photoshare.database.models import User

from photoshare.database.db import get_db
from photoshare.repository import users as repository_users
# from photoshare.conf.config import settings


class Auth:
    """
    Class containing authentication related methods.
    """

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = "secret_key"
    ALGORITHM = "HS256"
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

    def verify_password(self, plain_password, hashed_password):
        """
        Verifies if the provided plain password matches the hashed password.

        Parameters:
        - plain_password (str): The plain password.
        - hashed_password (str): The hashed password.

        Returns:
        - bool: True if passwords match, False otherwise.
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        Generates the hash for the provided password.

        Parameters:
        - password (str): The password to hash.

        Returns:
        - str: The hashed password.
        """
        return self.pwd_context.hash(password)

    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        Generates a new access token.

        Parameters:
        - data (dict): The payload data to encode in the token.
        - expires_delta (Optional[float]): Optional expiration time for the token in seconds.

        Returns:
        - str: The encoded access token.
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.now() + timedelta(minutes=15)
        to_encode.update(
            {"iat": datetime.now(), "exp": expire, "scope": "access_token"})
        encoded_access_token = jwt.encode(
            to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_access_token

    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        Generates a new refresh token.

        Parameters:
        - data (dict): The payload data to encode in the token.
        - expires_delta (Optional[float]): Optional expiration time for the token in seconds.

        Returns:
        - str: The encoded refresh token.
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.now() + timedelta(days=7)
        to_encode.update(
            {"iat": datetime.now(), "exp": expire, "scope": "refresh_token"})
        encoded_refresh_token = jwt.encode(
            to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_refresh_token

    async def decode_refresh_token(self, refresh_token: str):
        """
        Decodes the provided refresh token and retrieves the email from its payload.

        Parameters:
        - refresh_token (str): The refresh token to decode.

        Returns:
        - str: The email address extracted from the token payload.

        Raises:
        - HTTPException: If the token cannot be validated.
        """
        try:
            payload = jwt.decode(
                refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'refresh_token':
                email = payload['sub']
                return email
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not validate credentials')

    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
        """
        Retrieves the current user based on the provided access token.

        Parameters:
        - token (str): The access token.
        - db (Session): The database session.

        Returns:
        - User: The current user.

        Raises:
        - HTTPException: If the token cannot be validated or the user cannot be found.
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            # Decode JWT
            payload = jwt.decode(token, self.SECRET_KEY,
                                 algorithms=[self.ALGORITHM])
            if payload['scope'] == 'access_token':
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception

        user = await repository_users.get_user_by_email(email, db)
        if user is None:
            raise credentials_exception
        return user
    
    def get_current_user_roles(self, required_roles: list):
        async def roles_verifier(current_user: User = Depends(self.get_current_user), db: Session = Depends(get_db)):
            if current_user.role not in required_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions"
                )
            return current_user
        return roles_verifier

    # def create_email_token(self, data: dict):
    #     """
    #     Generates a token for email verification.

    #     Parameters:
    #     - data (dict): The payload data to encode in the token.

    #     Returns:
    #     - str: The encoded email verification token.
    #     """
    #     to_encode = data.copy()
    #     expire = datetime.utcnow() + timedelta(days=7)
    #     to_encode.update({"iat": datetime.utcnow(), "exp": expire})
    #     token = jwt.encode(to_encode, self.SECRET_KEY,
    #                        algorithm=self.ALGORITHM)
    #     return token

    # async def get_email_from_token(self, token: str):
    #     """
    #     Retrieves the email address from the provided email verification token.

    #     Parameters:
    #     - token (str): The email verification token.

    #     Returns:
    #     - str: The email address extracted from the token payload.

    #     Raises:
    #     - HTTPException: If the token cannot be validated.
    #     """
    #     try:
    #         payload = jwt.decode(token, self.SECRET_KEY,
    #                              algorithms=[self.ALGORITHM])
    #         email = payload["sub"]
    #         return email
    #     except JWTError as e:
    #         print(e)
    #         raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    #                             detail="Invalid token for email verification")



auth_service = Auth()

# def get_current_user_roles(required_roles: list):
#     def roles_verifier(current_user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
#         if current_user.role not in required_roles:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="Not enough permissions"
#             )
#         return current_user
#     return roles_verifier

# def get_current_admin_user(current_user: User = Depends(auth_service.get_current_user)):
#     if current_user.role != "admin":
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
#         )
#     return current_user

# def get_current_user_roles(required_roles: list):
#     def roles_verifier(current_user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
#         if current_user.role not in required_roles:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="Not enough permissions"
#             )
#         return current_user
#     return roles_verifier


# def get_current_moder_or_admin(current_user: User = Depends(auth_service.get_current_user)):
#     if current_user.role not in {"moderator", "admin"}:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
#         )
#     return current_user
