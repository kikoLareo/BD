from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.models import Championship
from schemas.championship import ChampionshipCreate, ChampionshipUpdate, ChampionshipResponse
from db.database import get_db
from logging_config import logger
from typing import List


router = APIRouter(
    prefix="/championships",
    tags=["championships"]
)

# Endpoint para obtener todos los campeonatos
@router.get("/", response_model=List[ChampionshipResponse])
async def get_all_championships(db: Session = Depends(get_db)):
    championships = db.query(Championship).all()
    logger.info("Campeonatos obtenidos exitosamente")
    return championships

# Endpoint para obtener un campeonato específico por ID
@router.get("/{championship_id}", response_model=ChampionshipResponse)
async def get_championship(championship_id: int, db: Session = Depends(get_db)):
    championship = db.query(Championship).filter(Championship.id == championship_id).first()
    if not championship:
        logger.error(f"Campeonato con ID {championship_id} no encontrado")
        raise HTTPException(status_code=404, detail="Campeonato no encontrado")
    
    logger.info(f"Campeonato '{championship.name}' obtenido exitosamente")
    return championship


# Endpoint para crear un campeonato
@router.post("/create", response_model=ChampionshipResponse)
async def create_championship(championship_data: ChampionshipCreate, db: Session = Depends(get_db)):
    try:
        new_championship = Championship(
            name=championship_data.name,
            location=championship_data.location,
            date=championship_data.date
        )
        db.add(new_championship)
        db.commit()
        db.refresh(new_championship)
        logger.info(f"Campeonato '{new_championship.name}' creado exitosamente")
        return new_championship
    except Exception as e:
        logger.error(f"Error al crear el campeonato: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

# Endpoint para actualizar un campeonato
@router.put("/update/{championship_id}", response_model=ChampionshipResponse)
async def update_championship(championship_id: int, championship_data: ChampionshipUpdate, db: Session = Depends(get_db)):
    championship = db.query(Championship).filter(Championship.id == championship_id).first()
    if not championship:
        logger.error(f"Campeonato con ID {championship_id} no encontrado")
        raise HTTPException(status_code=404, detail="Campeonato no encontrado")

    if championship_data.name:
        championship.name = championship_data.name
    if championship_data.location:
        championship.location = championship_data.location
    if championship_data.date:
        championship.date = championship_data.date

    db.commit()
    db.refresh(championship)
    logger.info(f"Campeonato '{championship.name}' actualizado exitosamente")
    return championship

# Endpoint para eliminar un campeonato
@router.delete("/delete/{championship_id}", response_model=dict)
async def delete_championship(championship_id: int, db: Session = Depends(get_db)):
    championship = db.query(Championship).filter(Championship.id == championship_id).first()
    if not championship:
        logger.error(f"Campeonato con ID {championship_id} no encontrado")
        raise HTTPException(status_code=404, detail="Campeonato no encontrado")

    db.delete(championship)
    db.commit()
    logger.info(f"Campeonato '{championship.name}' eliminado exitosamente")
    return {"message": "Campeonato eliminado exitosamente"}