from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from models import User
from security import SECRET_KEY, ALGORITHM

# Points at the login route, so Swagger UI knows where to get a token.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # 1. Decode the JWT to get the payload
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # 2. Fetch the user from MongoDB via Beanie
    user = await User.find_one(User.email == email)

    # 3. Ensure the user still exists and is active
    if user is None or not user.is_active:
        raise credentials_exception

    # 4. Hand the document to the endpoint
    return user
