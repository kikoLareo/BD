from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.models import JobPosition
from schemas.jobs import JobPositionCreate, JobPositionUpdate, JobPositionResponse
from db.database import get_db
from logging_config import logger
from typing import List


router = APIRouter(
    prefix="/job-positions",
    tags=["job_positions"]
)


# Endpoint para obtener todos los puestos de trabajo
@router.get("", response_model=List[JobPositionResponse])
async def get_all_job_positions(db: Session = Depends(get_db)):
    job_positions = db.query(JobPosition).all()
    logger.info("Puestos de trabajo obtenidos exitosamente")
    return job_positions

# Endpoint para obtener un puesto de trabajo específico por ID
@router.get("/{job_position_id}", response_model=JobPositionResponse)
async def get_job_position(job_position_id: int, db: Session = Depends(get_db)):
    job_position = db.query(JobPosition).filter(JobPosition.id == job_position_id).first()
    if not job_position:
        logger.error(f"Puesto de trabajo con ID {job_position_id} no encontrado")
        raise HTTPException(status_code=404, detail="Puesto de trabajo no encontrado")

    logger.info(f"Puesto de trabajo con ID {job_position_id} obtenido exitosamente")    
    return job_position

# Endpoint para crear un puesto de trabajo
@router.post("/create", response_model=JobPositionResponse)
async def create_job_position(job_data: JobPositionCreate, db: Session = Depends(get_db)):
    try:
        new_job_position = JobPosition(
            title=job_data.title,
            description=job_data.description
        )
        db.add(new_job_position)
        db.commit()
        db.refresh(new_job_position)
        logger.info(f"Puesto de trabajo '{new_job_position.title}' creado exitosamente")
        return new_job_position
    except Exception as e:
        logger.error(f"Error al crear el puesto de trabajo: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

# Endpoint para actualizar un puesto de trabajo
@router.put("/update/{job_position_id}", response_model=JobPositionResponse)
async def update_job_position(job_position_id: int, job_data: JobPositionUpdate, db: Session = Depends(get_db)):
    job_position = db.query(JobPosition).filter(JobPosition.id == job_position_id).first()
    if not job_position:
        logger.error(f"Puesto de trabajo con ID {job_position_id} no encontrado")
        raise HTTPException(status_code=404, detail="Puesto de trabajo no encontrado")

    if job_data.title:
        job_position.title = job_data.title
    if job_data.description:
        job_position.description = job_data.description

    db.commit()
    db.refresh(job_position)
    logger.info(f"Puesto de trabajo '{job_position.title}' actualizado exitosamente")
    return job_position

# Endpoint para eliminar un puesto de trabajo
@router.delete("/delete/{job_position_id}", response_model=dict)
async def delete_job_position(job_position_id: int, db: Session = Depends(get_db)):
    job_position = db.query(JobPosition).filter(JobPosition.id == job_position_id).first()
    if not job_position:
        logger.error(f"Puesto de trabajo con ID {job_position_id} no encontrado")
        raise HTTPException(status_code=404, detail="Puesto de trabajo no encontrado")

    db.delete(job_position)
    db.commit()
    logger.info(f"Puesto de trabajo '{job_position.title}' eliminado exitosamente")
    return {"message": "Puesto de trabajo eliminado exitosamente"}