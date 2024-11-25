from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from logging_config import logger
from typing import List
from schemas.location import LocationCreate, LocationResponse

router = APIRouter(
    prefix="/locations",
    tags=["locations"]
)



@router.post("/create", response_model=LocationResponse)
def create_location(location: LocationCreate, db: Session = Depends(get_db)):
    new_location = Location(**location.dict())
    db.add(new_location)
    db.commit()
    db.refresh(new_location)
    return new_location

@router.get("", response_model=List[LocationResponse])
def get_locations(db: Session = Depends(get_db)):
    return db.query(Location).all()