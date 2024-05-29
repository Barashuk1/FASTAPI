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
from photoshare.conf.config import settings


class Auth:
    """
    Class containing authentication related methods.
    """
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = settings.secret_key
    ALGORITHM = settings.algorithm
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

    def verify_password(
        self,
        plain_password: str,
        hashed_password: str
    ) -> bool:
        """
        Verifies if the provided plain password matches the hashed password.

        :param plain_password: The plain password.
        :param hashed_password: The hashed password.
        :return: True if passwords match, False otherwise.
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """
        Generates the hash for the provided password.

        :param password: The password to hash.
        :return: The hashed password.
        """
        return self.pwd_context.hash(password)

    async def create_access_token(
        self,
        data: dict,
        expires_delta: Optional[float] = None
    ) -> str:
        """
        Generates a new access token.

        :param data: The payload data to encode in the token.
        :param expires_delta: Optional expiration time for the token in seconds.
        :return: The encoded access token.
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

    async def create_refresh_token(
        self,
        data: dict,
        expires_delta: Optional[float] = None
    ) -> str:
        """
        Generates a new refresh token.

        :param data: The payload data to encode in the token.
        :param expires_delta: Optional expiration time for the token in seconds.
        :return: The encoded refresh token.
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

    async def decode_refresh_token(self, refresh_token: str) -> str:
        """
        Decodes the provided refresh token and retrieves the email from its payload.

        :param refresh_token: The refresh token to decode.
        :raise HTTPException: If the token cannot be validated or the scope is invalid.
        :return: The email address extracted from the token payload.
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

    async def get_current_user(
        self,
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
    ) -> User:
        """
        Retrieves the current user based on the provided access token.

        :param token: The access token.
        :param db: The database session.
        :raise HTTPException: If the token cannot be validated or the user does not exist.
        :return: The current user.
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            # Decode JWT
            payload = jwt.decode(
                token, self.SECRET_KEY, algorithms=[self.ALGORITHM]
            )
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

    def get_current_user_roles(self, required_roles: list) -> callable:
        """
        Returns a dependency that verifies if the current user has the required roles.

        :param required_roles: The list of required roles.
        :return: The dependency function.
        """
        async def roles_verifier(
                current_user: User = Depends(self.get_current_user),
                db: Session = Depends(get_db)
        ) -> User:
            """
            Verifies if the current user has the required roles.

            :param current_user: The current user.
            :param db: The database session.
            :raise HTTPException: If the user does not have the required roles.
            :return: The current user.
            """
            if current_user.role not in required_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions"
                )
            return current_user
        return roles_verifier


auth_service = Auth()
