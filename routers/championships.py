from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.championship import ChampionshipCreate, ChampionshipUpdate, ChampionshipDetailResponse
from db.database import get_db
from logging_config import logger
from db.CRUD.championship_crud import *
from typing import List

router = APIRouter(
    prefix="/championships",
    tags=["championships"]
)

# Endpoint para obtener todos los campeonatos
@router.get("/", response_model=List[ChampionshipDetailResponse])
async def get_championships(db: Session = Depends(get_db)):
    championships = get_all_championships(db)
    logger.info("Campeonatos obtenidos exitosamente")
    return championships

# Endpoint para obtener un campeonato específico por ID
@router.get("/{championship_id}", response_model=ChampionshipDetailResponse)
async def get_championship(championship_id: int, db: Session = Depends(get_db)):
    championship = get_championship_by_id(db, championship_id)
    if not championship:
        logger.error(f"Campeonato con ID {championship_id} no encontrado")
        raise HTTPException(status_code=404, detail="Campeonato no encontrado")
    
    logger.info(f"Campeonato '{championship.name}' obtenido exitosamente")
    return championship

# Endpoint para crear un campeonato
@router.post("/create", response_model=ChampionshipDetailResponse)
async def create_new_championship(championship_data: ChampionshipCreate, db: Session = Depends(get_db)):
    try:
        new_championship = create_championship(db, championship_data)
        logger.info(f"Campeonato '{new_championship.name}' creado exitosamente")
        return new_championship
    except Exception as e:
        logger.error(f"Error al crear el campeonato: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

# Endpoint para actualizar un campeonato
@router.put("/update/{championship_id}", response_model=ChampionshipDetailResponse)
async def update_existing_championship(championship_id: int, championship_data: ChampionshipUpdate, db: Session = Depends(get_db)):
    try:
        updated_championship = update_championship(db, championship_id, championship_data)
        logger.info(f"Campeonato '{updated_championship.name}' actualizado exitosamente")
        return updated_championship
    except ValueError as e:
        logger.error(str(e))
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error al actualizar el campeonato: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

# Endpoint para eliminar un campeonato
@router.delete("/delete/{championship_id}", response_model=dict)
async def delete_existing_championship(championship_id: int, db: Session = Depends(get_db)):
    try:
        delete_championship(db, championship_id)
        logger.info(f"Campeonato con ID {championship_id} eliminado exitosamente")
        return {"message": "Campeonato eliminado exitosamente"}
    except ValueError as e:
        logger.error(str(e))
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error al eliminar el campeonato: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")