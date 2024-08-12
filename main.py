# shortener_app/main.py

from fastapi import FastAPI, HTTPException
import secrets
from pydantic import BaseSettings
from sqlalchemy import create_engine
from functools import lru_cache
from fastapi.responses import RedirectResponse
from fastapi import Depends, FastAPI, HTTPException, Request
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from sqlalchemy import Boolean, Column, Integer, String
import validators

class Settings(BaseSettings):
	env_name: str = "Local"
	base_url: str = "http://localhost:8000"
	db_url: str = "sqlite:///./shortener.db"
	class Config:
		env_file = ".env"

class URLBase(BaseModel):
    target_url: str

class URL(URLBase):
    is_active: bool
    clicks: int

    class Config:
        orm_mode = True

class URLInfo(URL):
    url: str
    admin_url: str



app = FastAPI()


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    print(f"Loading settings for: {settings.env_name}")
    return settings

engine = create_engine(
    get_settings().db_url, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)
Base = declarative_base()



class URL(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True, index=True)
    secret_key = Column(String, unique=True, index=True)
    target_url = Column(String, index=True)
    is_active = Column(Boolean, default=True)
    clicks = Column(Integer, default=0)
	
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
	
def raise_bad_request(message):
    raise HTTPException(status_code=400, detail=message)

def raise_not_found(request):
    message = f"URL '{request.url}' doesn't exist"
    raise HTTPException(status_code=404, detail=message)
	
@app.get("/")
def read_root():
    return "Welcome to the URL shortener API :)"



@app.post("/url", response_model=URLInfo)
def create_url(url: URLBase, db: Session = Depends(get_db)):
    if not validators.url(url.target_url):
        raise_bad_request(message="Your provided URL is not valid")

    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    key = "".join(secrets.choice(chars) for _ in range(5))
    secret_key = "".join(secrets.choice(chars) for _ in range(8))
    db_url = URL(
        target_url=url.target_url, key=key, secret_key=secret_key
    )
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    db_url.url = key
    db_url.admin_url = secret_key

    return db_url

@app.get("/{url_key}")
def forward_to_target_url(
        url_key: str,
        request: Request,
        db: Session = Depends(get_db)
    ):
    db_url = (
        db.query(URL)
        .filter(URL.key == url_key, URL.is_active)
        .first()
    )
    if db_url:
        return RedirectResponse(db_url.target_url)
    else:
        raise_not_found(request)