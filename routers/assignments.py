from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from models.models import ChampionshipAssignment, JobPosition, Championship, User
from schemas.assignments import ChampionshipAssignmentCreate, ChampionshipAssignmentUpdate, ChampionshipAssignmentResponse
from db.database import get_db
from logging_config import logger
from typing import List
from db.CRUD.crud import get_user
from utils.error_handling import (
    handle_exceptions, 
    CommonErrors, 
    APIError, 
    ErrorCodes
)

router = APIRouter(
    prefix="/assignments",
    tags=["assignments"]
)

# 🔧 Función para enriquecer una asignación
def serialize_assignment(assignment: ChampionshipAssignment, db: Session):
    """
    Enriquecer una asignación con datos adicionales (username, job_position_name, championship_name).
    """
    data = assignment.__dict__.copy()

    # Limpiar el atributo que genera problemas al serializar
    data.pop("_sa_instance_state", None)

    # Obtener el usuario
    user = db.query(User).filter(User.id == data["user_id"]).first()
    data["username"] = user.username if user else None

    # Obtener el puesto
    job_position = db.query(JobPosition).filter(JobPosition.id == data["job_position_id"]).first()
    data["job_position_name"] = job_position.title if job_position else None

    # Obtener el campeonato
    championship = db.query(Championship).filter(Championship.id == data["championship_id"]).first()
    data["championship_name"] = championship.name if championship else None

    return data


# ✅ Endpoint para obtener todas las asignaciones
@router.get("", response_model=List[ChampionshipAssignmentResponse])
async def get_all_assignments(db: Session = Depends(get_db)):
    """
    Obtiene todas las asignaciones.
    """
    logger.info("Iniciando obtención de todas las asignaciones")
    try:
        assignments = db.query(ChampionshipAssignment).all()
        logger.info(f"Asignaciones obtenidas exitosamente: {len(assignments)} encontradas")

        result = [serialize_assignment(assignment, db) for assignment in assignments]

        return result

    except SQLAlchemyError as e:
        logger.error(f"Error de base de datos al obtener asignaciones: {str(e)}")
        raise APIError(
            code=ErrorCodes.DATABASE_ERROR,
            message="Error al obtener las asignaciones",
            status_code=500,
            details=f"Error de base de datos: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error inesperado al obtener asignaciones: {str(e)}")
        raise APIError(
            code=ErrorCodes.INTERNAL_ERROR,
            message="Error interno del servidor",
            status_code=500,
            details=f"Error inesperado: {str(e)}"
        )


# ✅ Endpoint para obtener todas las asignaciones de un campeonato específico
@router.get("/championship/{championship_id}", response_model=List[ChampionshipAssignmentResponse])
@handle_exceptions
async def get_assignments_by_championship(championship_id: int, db: Session = Depends(get_db)):
    assignments = db.query(ChampionshipAssignment).filter(
        ChampionshipAssignment.championship_id == championship_id
    ).all()
    
    if not assignments:
        logger.error(f"No se encontraron asignaciones para el campeonato {championship_id}")
        raise CommonErrors.not_found("Asignaciones", f"campeonato {championship_id}")

    logger.info(f"Asignaciones obtenidas exitosamente para el campeonato {championship_id}")

    result = [serialize_assignment(assignment, db) for assignment in assignments]

    return result


# ✅ Endpoint para obtener una asignación específica por user_id y championship_id
@router.get("/{user_id}/{championship_id}", response_model=ChampionshipAssignmentResponse)
@handle_exceptions
async def get_assignment(user_id: int, championship_id: int, db: Session = Depends(get_db)):
    assignment = db.query(ChampionshipAssignment).filter(
        ChampionshipAssignment.user_id == user_id,
        ChampionshipAssignment.championship_id == championship_id
    ).first()

    if not assignment:
        logger.error(f"Asignación no encontrada para el usuario {user_id} y el campeonato {championship_id}")
        raise CommonErrors.not_found("Asignación", f"usuario {user_id}, campeonato {championship_id}")

    logger.info(f"Asignación obtenida exitosamente para el usuario {user_id} en el campeonato {championship_id}")

    return serialize_assignment(assignment, db)


# ✅ Endpoint para asignar un usuario a un campeonato
@router.post("/create", response_model=ChampionshipAssignmentResponse)
@handle_exceptions
async def create_assignment(assignment_data: ChampionshipAssignmentCreate, db: Session = Depends(get_db)):
    try:
        # Verificar si la asignación ya existe
        existing_assignment = db.query(ChampionshipAssignment).filter(
            ChampionshipAssignment.user_id == assignment_data.user_id,
            ChampionshipAssignment.championship_id == assignment_data.championship_id
        ).first()
        
        if existing_assignment:
            logger.error(f"Ya existe una asignación para el usuario {assignment_data.user_id} en el campeonato {assignment_data.championship_id}")
            raise APIError(
                code=ErrorCodes.DUPLICATE_ENTRY,
                message="La asignación ya existe",
                status_code=400,
                details=f"Ya existe una asignación para el usuario {assignment_data.user_id} en el campeonato {assignment_data.championship_id}"
            )
        
        # Crear la nueva asignación
        new_assignment = ChampionshipAssignment(
            user_id=assignment_data.user_id,
            championship_id=assignment_data.championship_id,
            job_position_id=assignment_data.job_position_id,
            hours_worked=assignment_data.hours_worked,
            start_date=assignment_data.start_date,
            end_date=assignment_data.end_date
        )
        
        db.add(new_assignment)
        db.commit()
        db.refresh(new_assignment)
        
        logger.info(f"Usuario {assignment_data.user_id} asignado al campeonato {assignment_data.championship_id} con el puesto {assignment_data.job_position_id}")
        return serialize_assignment(new_assignment, db)

    except IntegrityError as e:
        db.rollback()
        logger.error(f"Error de integridad al crear asignación: {str(e)}")
        raise APIError(
            code=ErrorCodes.INTEGRITY_ERROR,
            message="Error de integridad en la base de datos",
            status_code=400,
            details="Uno o más de los IDs proporcionados (usuario, campeonato o puesto) no existen en la base de datos"
        )
    except APIError:
        db.rollback()
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error de base de datos al crear asignación: {str(e)}")
        raise CommonErrors.database_error(f"Error al crear la asignación: {str(e)}")
    except Exception as e:
        db.rollback()
        logger.error(f"Error inesperado al crear asignación: {str(e)}")
        raise CommonErrors.internal_error(f"Error al crear la asignación: {str(e)}")


# ✅ Endpoint para actualizar una asignación
@router.put("/update/{user_id}/{championship_id}", response_model=ChampionshipAssignmentResponse)
@handle_exceptions
async def update_assignment(user_id: int, championship_id: int, assignment_data: ChampionshipAssignmentUpdate, db: Session = Depends(get_db)):
    try:
        assignment = db.query(ChampionshipAssignment).filter(
            ChampionshipAssignment.user_id == user_id,
            ChampionshipAssignment.championship_id == championship_id
        ).first()

        if not assignment:
            logger.error(f"Asignación no encontrada para el usuario {user_id} y el campeonato {championship_id}")
            raise CommonErrors.not_found("Asignación", f"usuario {user_id}, campeonato {championship_id}")

        if assignment_data.job_position_id is not None:
            assignment.job_position_id = assignment_data.job_position_id
        if assignment_data.hours_worked is not None:
            assignment.hours_worked = assignment_data.hours_worked
        if assignment_data.start_date is not None:
            assignment.start_date = assignment_data.start_date
        if assignment_data.end_date is not None:
            assignment.end_date = assignment_data.end_date

        db.commit()
        db.refresh(assignment)

        logger.info(f"Asignación actualizada para el usuario {user_id} en el campeonato {championship_id}")

        return serialize_assignment(assignment, db)

    except IntegrityError as e:
        db.rollback()
        logger.error(f"Error de integridad al actualizar asignación: {str(e)}")
        raise APIError(
            code=ErrorCodes.INTEGRITY_ERROR,
            message="Error de integridad en la base de datos",
            status_code=400,
            details="El puesto de trabajo especificado no existe en la base de datos"
        )
    except APIError:
        db.rollback()
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error de base de datos al actualizar asignación: {str(e)}")
        raise CommonErrors.database_error(f"Error al actualizar la asignación: {str(e)}")
    except Exception as e:
        db.rollback()
        logger.error(f"Error inesperado al actualizar asignación: {str(e)}")
        raise CommonErrors.internal_error(f"Error al actualizar la asignación: {str(e)}")


# ✅ Endpoint para eliminar una asignación
@router.delete("/delete/{user_id}/{championship_id}", response_model=dict)
@handle_exceptions
async def delete_assignment(user_id: int, championship_id: int, db: Session = Depends(get_db)):
    try:
        assignment = db.query(ChampionshipAssignment).filter(
            ChampionshipAssignment.user_id == user_id,
            ChampionshipAssignment.championship_id == championship_id
        ).first()

        if not assignment:
            logger.error(f"Asignación no encontrada para el usuario {user_id} y el campeonato {championship_id}")
            raise CommonErrors.not_found("Asignación", f"usuario {user_id}, campeonato {championship_id}")

        db.delete(assignment)
        db.commit()

        logger.info(f"Asignación eliminada para el usuario {user_id} en el campeonato {championship_id}")

        return {
            "message": "Asignación eliminada exitosamente",
            "code": "SUCCESS",
            "details": {
                "user_id": user_id,
                "championship_id": championship_id
            }
        }

    except APIError:
        db.rollback()
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error de base de datos al eliminar asignación: {str(e)}")
        raise CommonErrors.database_error(f"Error al eliminar la asignación: {str(e)}")
    except Exception as e:
        db.rollback()
        logger.error(f"Error inesperado al eliminar asignación: {str(e)}")
        raise CommonErrors.internal_error(f"Error al eliminar la asignación: {str(e)}")

