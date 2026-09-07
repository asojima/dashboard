from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from database import SessionLocal, Sale
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
import hashlib
import os

app = FastAPI(title="Sales API with JWT Authentication")

# Конфиг JWT
SECRET_KEY = os.getenv("SECRET_KEY", "mysecretkey123456789")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Простая функция хеширования (вместо bcrypt)
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Модели данных
class SaleOut(BaseModel):
    id: int
    product: str
    category: str
    price: float
    quantity: int
    date: datetime

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    username: str

class UserCreate(BaseModel):
    username: str
    password: str

# База пользователей (с SHA256 хешами)
fake_users_db = {
    "admin": {
        "username": "admin",
        "hashed_password": hash_password("admin123"),
        "role": "admin"
    },
    "user": {
        "username": "user", 
        "hashed_password": hash_password("user123"),
        "role": "user"
    }
}

# Функции для работы с JWT
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def authenticate_user(username: str, password: str):
    user = fake_users_db.get(username)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user

# Защита эндпоинтов
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Невалидный токен",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = fake_users_db.get(username)
    if user is None:
        raise credentials_exception
    return user

# Эндпоинты
@app.post("/login", response_model=Token)
async def login(user: UserLogin):
    db_user = authenticate_user(user.username, user.password)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.username})
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "username": user.username
    }

@app.post("/register")
async def register(user: UserCreate):
    if user.username in fake_users_db:
        raise HTTPException(status_code=400, detail="Пользователь уже существует")
    
    fake_users_db[user.username] = {
        "username": user.username,
        "hashed_password": hash_password(user.password),
        "role": "user"
    }
    return {"message": f"Пользователь {user.username} создан"}

@app.get("/sales", response_model=List[SaleOut])
async def get_sales(
    current_user: dict = Depends(get_current_user),
    limit: Optional[int] = 100, 
    skip: Optional[int] = 0
):
    db = SessionLocal()
    sales = db.query(Sale).offset(skip).limit(limit).all()
    db.close()
    return sales

@app.get("/sales/by_category")
async def sales_by_category(current_user: dict = Depends(get_current_user)):
    db = SessionLocal()
    from sqlalchemy import func
    result = db.query(
        Sale.category, 
        func.sum(Sale.price * Sale.quantity).label('total')
    ).group_by(Sale.category).all()
    db.close()
    return [{"category": cat, "total": float(total)} for cat, total in result]

@app.get("/sales/top_products")
async def top_products(
    current_user: dict = Depends(get_current_user),
    limit: int = 5
):
    db = SessionLocal()
    from sqlalchemy import func
    result = db.query(
        Sale.product, 
        func.sum(Sale.quantity).label('total_sold')
    ).group_by(Sale.product).order_by(func.sum(Sale.quantity).desc()).limit(limit).all()
    db.close()
    return [{"product": p, "total_sold": int(q)} for p, q in result]

@app.get("/sales/stats")
async def get_stats(current_user: dict = Depends(get_current_user)):
    db = SessionLocal()
    from sqlalchemy import func
    total_revenue = db.query(func.sum(Sale.price * Sale.quantity)).scalar() or 0
    total_orders = db.query(func.count(Sale.id)).scalar() or 0
    db.close()
    return {
        "total_revenue": float(total_revenue),
        "total_orders": total_orders,
        "avg_order_value": float(total_revenue / total_orders) if total_orders > 0 else 0
    }

@app.get("/sales/my_profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    return {
        "username": current_user["username"],
        "role": current_user["role"],
        "message": "Добро пожаловать в защищенный дашборд!"
    }

@app.get("/")
async def root():
    return {
        "message": "Sales API with JWT Authentication",
        "endpoints": {
            "login": "POST /login",
            "register": "POST /register",
            "sales": "GET /sales (protected)",
            "stats": "GET /sales/stats (protected)",
            "profile": "GET /sales/my_profile (protected)"
        },
        "test_users": {
            "admin": "admin123",
            "user": "user123"
        }
    }