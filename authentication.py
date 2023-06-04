from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
from pydantic import BaseModel
import secrets

app = FastAPI()
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
JWT_SECRET = secrets.token_urlsafe(32)
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION = timedelta(hours=1)


# User model and storage functions
class User(BaseModel):
  username: str
  password: str


# In-memory user storage
users_db = {
  "john": {
    "username": "john",
    "password":
    "$2b$12$lo9L.vavkQqR4DR3HhH8/.TPgAfKrNj7LcSbkV6G9jUKr.CMvQSS2"  # Hashed password: password123
  },
  "jane": {
    "username": "jane",
    "password":
    "$2b$12$5BOdJr0qM.rULUIviGBQvOvl0wEGQGc2rOS9fQe/ASUVeHLhlUqyy"  # Hashed password: qwerty456
  }
}


def get_user(username: str):
  if username in users_db:
    return User(**users_db[username])
  return None


def verify_password(plain_password: str, hashed_password: str):
  return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(username: str, password: str):
  user = get_user(username)
  if not user:
    return False
  if not verify_password(password, user.password):
    return False
  return user


# Authentication endpoints
@app.post("/login")
def login(user: User):
  authenticated_user = authenticate_user(user.username, user.password)
  if not authenticated_user:
    raise HTTPException(status_code=401, detail="Invalid username or password")
  token = generate_token(authenticated_user)
  return {"access_token": token}


def generate_token(user: User):
  payload = {"sub": user.username, "exp": datetime.utcnow() + JWT_EXPIRATION}
  token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
  return token


if __name__ == "__main__":
  import uvicorn
  uvicorn.run(app, host="0.0.0.0", port=8000)
