from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.models import Discipline
from schemas.discipline import DisciplineCreate, DisciplineUpdate, DisciplineResponse
from db.database import get_db
from logging_config import logger
from typing import List

router = APIRouter(
    prefix="/disciplines",
    tags=["disciplines"]
)

# Obtener todas las disciplinas
@router.get("/", response_model=List[DisciplineResponse])
async def get_all_disciplines(db: Session = Depends(get_db)):
    disciplines = db.query(Discipline).all()
    logger.info("Disciplinas obtenidas exitosamente")
    return disciplines

# Obtener una disciplina por ID
@router.get("/{discipline_id}", response_model=DisciplineResponse)
async def get_discipline(discipline_id: int, db: Session = Depends(get_db)):
    discipline = db.query(Discipline).filter(Discipline.id == discipline_id).first()
    if not discipline:
        logger.error(f"Disciplina con ID {discipline_id} no encontrada")
        raise HTTPException(status_code=404, detail="Disciplina no encontrada")
    logger.info(f"Disciplina con ID {discipline_id} obtenida exitosamente")
    return discipline

# Crear una nueva disciplina
@router.post("/create", response_model=DisciplineResponse)
async def create_discipline(discipline_data: DisciplineCreate, db: Session = Depends(get_db)):
    try:
        new_discipline = Discipline(**discipline_data.dict())
        db.add(new_discipline)
        db.commit()
        db.refresh(new_discipline)
        logger.info(f"Disciplina '{new_discipline.name}' creada exitosamente")
        return new_discipline
    except Exception as e:
        logger.error(f"Error al crear disciplina: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

# Actualizar una disciplina
@router.put("/{discipline_id}/update", response_model=DisciplineResponse)
async def update_discipline(discipline_id: int, discipline_data: DisciplineUpdate, db: Session = Depends(get_db)):
    discipline = db.query(Discipline).filter(Discipline.id == discipline_id).first()
    if not discipline:
        logger.error(f"Disciplina con ID {discipline_id} no encontrada")
        raise HTTPException(status_code=404, detail="Disciplina no encontrada")
    for key, value in discipline_data.dict(exclude_unset=True).items():
        setattr(discipline, key, value)
    db.commit()
    db.refresh(discipline)
    logger.info(f"Disciplina con ID {discipline_id} actualizada exitosamente")
    return discipline

# Eliminar una disciplina
@router.delete("/{discipline_id}/delete", response_model=dict)
async def delete_discipline(discipline_id: int, db: Session = Depends(get_db)):
    discipline = db.query(Discipline).filter(Discipline.id == discipline_id).first()
    if not discipline:
        logger.error(f"Disciplina con ID {discipline_id} no encontrada")
        raise HTTPException(status_code=404, detail="Disciplina no encontrada")
    db.delete(discipline)
    db.commit()
    logger.info(f"Disciplina con ID {discipline_id} eliminada exitosamente")
    return {"message": "Disciplina eliminada exitosamente"}