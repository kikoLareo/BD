from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.models import Organizer
from schemas.organizer import OrganizerCreate, OrganizerUpdate, OrganizerResponse
from db.database import get_db
from logging_config import logger
from typing import List

router = APIRouter(
    prefix="/organizers",
    tags=["organizers"]
)

# Obtener todos los organizadores
@router.get("/", response_model=List[OrganizerResponse])
async def get_all_organizers(db: Session = Depends(get_db)):
    organizers = db.query(Organizer).all()
    logger.info("Organizadores obtenidos exitosamente")
    return organizers

# Obtener un organizador por ID
@router.get("/{organizer_id}", response_model=OrganizerResponse)
async def get_organizer(organizer_id: int, db: Session = Depends(get_db)):
    organizer = db.query(Organizer).filter(Organizer.id == organizer_id).first()
    if not organizer:
        logger.error(f"Organizador con ID {organizer_id} no encontrado")
        raise HTTPException(status_code=404, detail="Organizador no encontrado")
    logger.info(f"Organizador con ID {organizer_id} obtenido exitosamente")
    return organizer

# Crear un nuevo organizador
@router.post("/create", response_model=OrganizerResponse)
async def create_organizer(organizer_data: OrganizerCreate, db: Session = Depends(get_db)):
    try:
        new_organizer = Organizer(**organizer_data.dict())
        db.add(new_organizer)
        db.commit()
        db.refresh(new_organizer)
        logger.info(f"Organizador '{new_organizer.name}' creado exitosamente")
        return new_organizer
    except Exception as e:
        logger.error(f"Error al crear organizador: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

# Actualizar un organizador
@router.put("/{organizer_id}/update", response_model=OrganizerResponse)
async def update_organizer(organizer_id: int, organizer_data: OrganizerUpdate, db: Session = Depends(get_db)):
    organizer = db.query(Organizer).filter(Organizer.id == organizer_id).first()
    if not organizer:
        logger.error(f"Organizador con ID {organizer_id} no encontrado")
        raise HTTPException(status_code=404, detail="Organizador no encontrado")
    for key, value in organizer_data.dict(exclude_unset=True).items():
        setattr(organizer, key, value)
    db.commit()
    db.refresh(organizer)
    logger.info(f"Organizador con ID {organizer_id} actualizado exitosamente")
    return organizer

# Eliminar un organizador
@router.delete("/{organizer_id}/delete", response_model=dict)
async def delete_organizer(organizer_id: int, db: Session = Depends(get_db)):
    organizer = db.query(Organizer).filter(Organizer.id == organizer_id).first()
    if not organizer:
        logger.error(f"Organizador con ID {organizer_id} no encontrado")
        raise HTTPException(status_code=404, detail="Organizador no encontrado")
    db.delete(organizer)
    db.commit()
    logger.info(f"Organizador con ID {organizer_id} eliminado exitosamente")
    return {"message": "Organizador eliminado exitosamente"}