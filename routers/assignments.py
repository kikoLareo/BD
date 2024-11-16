# routers/assignments.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.models import ChampionshipAssignment
from schemas.assignments import ChampionshipAssignmentCreate, ChampionshipAssignmentResponse
from db.database import get_db
from logging_config import logger
from typing import List


router = APIRouter(
    prefix="/assignments",
    tags=["assignments"]
)


# Endpoint para obtener todas las asignaciones
@router.get("", response_model=List[ChampionshipAssignmentResponse])
async def get_all_assignments(db: Session = Depends(get_db)):
    assignments = db.query(ChampionshipAssignment).all()
    logger.info("Asignaciones obtenidas exitosamente")
    return assignments

# Endpoint para obtener una asignación específica por ID
@router.get("/{assignment_id}", response_model=ChampionshipAssignmentResponse)
async def get_assignment(assignment_id: int, db: Session = Depends(get_db)):
    assignment = db.query(ChampionshipAssignment).filter(ChampionshipAssignment.id == assignment_id).first()
    if not assignment:
        logger.error(f"Asignación con ID {assignment_id} no encontrada")
        raise HTTPException(status_code=404, detail="Asignación no encontrada")
    
    logger.info(f"Asignación con ID {assignment_id} obtenida exitosamente")
    return assignment


# Endpoint para asignar un usuario a un campeonato
@router.post("/create", response_model=ChampionshipAssignmentResponse)
async def create_assignment(assignment_data: ChampionshipAssignmentCreate, db: Session = Depends(get_db)):
    try:
        new_assignment = ChampionshipAssignment(
            user_id=assignment_data.user_id,
            championship_id=assignment_data.championship_id,
            job_position_id=assignment_data.job_position_id,
            hours_worked=assignment_data.hours_worked
        )
        db.add(new_assignment)
        db.commit()
        db.refresh(new_assignment)
        logger.info(f"Usuario {assignment_data.user_id} asignado al campeonato {assignment_data.championship_id} con el puesto {assignment_data.job_position_id}")
        return new_assignment
    except Exception as e:
        logger.error(f"Error al asignar el usuario: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

# Endpoint para actualizar una asignación
@router.put("/update/{user_id}/{championship_id}", response_model=ChampionshipAssignmentResponse)
async def update_assignment(user_id: int, championship_id: int, assignment_data: ChampionshipAssignmentCreate, db: Session = Depends(get_db)):
    try:
        assignment = db.query(ChampionshipAssignment).filter(
            ChampionshipAssignment.user_id == user_id,
            ChampionshipAssignment.championship_id == championship_id
        ).first()

        if not assignment:
            logger.error(f"Asignación no encontrada para el usuario {user_id} y el campeonato {championship_id}")
            raise HTTPException(status_code=404, detail="Asignación no encontrada")

        assignment.job_position_id = assignment_data.job_position_id
        assignment.hours_worked = assignment_data.hours_worked
        db.commit()
        db.refresh(assignment)

        logger.info(f"Asignación actualizada para el usuario {user_id} en el campeonato {championship_id}")
        return assignment
    except Exception as e:
        logger.error(f"Error al actualizar la asignación: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

# Endpoint para eliminar una asignación
@router.delete("/delete/{user_id}/{championship_id}", response_model=dict)
async def delete_assignment(user_id: int, championship_id: int, db: Session = Depends(get_db)):
    try:
        assignment = db.query(ChampionshipAssignment).filter(
            ChampionshipAssignment.user_id == user_id,
            ChampionshipAssignment.championship_id == championship_id
        ).first()

        if not assignment:
            logger.error(f"Asignación no encontrada para el usuario {user_id} y el campeonato {championship_id}")
            raise HTTPException(status_code=404, detail="Asignación no encontrada")

        db.delete(assignment)
        db.commit()
        logger.info(f"Asignación eliminada para el usuario {user_id} en el campeonato {championship_id}")
        return {"message": "Asignación eliminada exitosamente"}
    except Exception as e:
        logger.error(f"Error al eliminar la asignación: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")