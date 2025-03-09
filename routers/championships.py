from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from schemas.championship import ChampionshipCreate, ChampionshipUpdate, ChampionshipDetailResponse
from db.database import get_db
from logging_config import logger
from db.CRUD.championship_crud import *
from typing import List
from utils.error_handling import (
    handle_exceptions, 
    CommonErrors, 
    APIError, 
    ErrorCodes
)
from utils.sqlalchemy_errors import handle_sqlalchemy_error
from models.models import Organizer, Discipline

router = APIRouter(
    prefix="/championships",
    tags=["championships"]
)

# 🔧 Función auxiliar para serializar un campeonato con nombres adicionales
def serialize_championship(championship, db: Session):
    item = championship.__dict__.copy()

    # Limpiar instancia de SQLAlchemy
    item.pop("_sa_instance_state", None)

    # Buscar el nombre del organizador
    organizer = db.query(Organizer).filter(Organizer.id == championship.organizer_id).first()
    item["organizer_name"] = organizer.name if organizer else None

    # Buscar el nombre de la disciplina
    discipline = db.query(Discipline).filter(Discipline.id == championship.discipline_id).first()
    item["discipline_name"] = discipline.name if discipline else None

    return item


# ✅ Obtener todos los campeonatos
@router.get("/", response_model=List[ChampionshipDetailResponse])
async def get_championships(db: Session = Depends(get_db)):
    """
    Obtiene todos los campeonatos con el nombre del organizador y disciplina.
    """
    logger.info("Iniciando obtención de todos los campeonatos")
    try:
        championships = get_all_championships(db)
        logger.info(f"Campeonatos obtenidos exitosamente: {len(championships)} encontrados")

        # Serializar campeonatos agregando organizer_name y discipline_name
        result = [serialize_championship(championship, db) for championship in championships]

        return result
    except SQLAlchemyError as e:
        logger.error(f"Error de base de datos al obtener campeonatos: {str(e)}")
        raise APIError(
            code=ErrorCodes.DATABASE_ERROR,
            message="Error al obtener los campeonatos",
            status_code=500,
            details=f"Error de base de datos: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error inesperado al obtener campeonatos: {str(e)}")
        raise APIError(
            code=ErrorCodes.INTERNAL_ERROR,
            message="Error interno del servidor",
            status_code=500,
            details=f"Error inesperado: {str(e)}"
        )


# ✅ Obtener un campeonato específico
@router.get("/{championship_id}", response_model=ChampionshipDetailResponse)
@handle_exceptions
async def get_championship(championship_id: int, db: Session = Depends(get_db)):
    try:
        championship = get_championship_by_id(db, championship_id)
        if not championship:
            logger.error(f"Campeonato con ID {championship_id} no encontrado")
            raise CommonErrors.not_found("Campeonato", championship_id)

        logger.info(f"Campeonato '{championship.name}' obtenido exitosamente")

        # Serializar el campeonato con nombres adicionales
        result = serialize_championship(championship, db)
        return result
    except APIError:
        raise
    except SQLAlchemyError as e:
        raise handle_sqlalchemy_error(e, "Campeonato")
    except Exception as e:
        raise CommonErrors.internal_error(f"Error al obtener el campeonato: {str(e)}")


# ✅ Crear un campeonato
@router.post("/create", response_model=ChampionshipDetailResponse)
@handle_exceptions
async def create_new_championship(championship_data: ChampionshipCreate, db: Session = Depends(get_db)):
    try:
        logger.info(f'Creando nuevo campeonato: {championship_data.name}')

        existing_championship = db.query(Championship).filter(Championship.name == championship_data.name).first()
        if existing_championship:
            logger.error(f"Ya existe un campeonato con el nombre '{championship_data.name}'")
            raise APIError(
                code=ErrorCodes.DUPLICATE_ENTRY,
                message="El campeonato ya existe",
                status_code=400,
                details=f"Ya existe un campeonato con el nombre '{championship_data.name}'"
            )

        new_championship = create_championship(db, championship_data)
        logger.info(f"Campeonato '{new_championship.name}' creado exitosamente")

        result = serialize_championship(new_championship, db)
        return result
    except APIError:
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Error de integridad al crear campeonato: {str(e)}")
        raise handle_sqlalchemy_error(e, "Campeonato")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error de base de datos al crear campeonato: {str(e)}")
        raise handle_sqlalchemy_error(e, "Campeonato")
    except Exception as e:
        db.rollback()
        logger.error(f"Error inesperado al crear campeonato: {str(e)}")
        raise CommonErrors.internal_error(f"Error al crear el campeonato: {str(e)}")


# ✅ Actualizar un campeonato
@router.put("/update/{championship_id}", response_model=ChampionshipDetailResponse)
@handle_exceptions
async def update_existing_championship(championship_id: int, championship_data: ChampionshipUpdate, db: Session = Depends(get_db)):
    try:
        championship = get_championship_by_id(db, championship_id)
        if not championship:
            logger.error(f"Campeonato con ID {championship_id} no encontrado")
            raise CommonErrors.not_found("Campeonato", championship_id)

        if championship_data.name and championship_data.name != championship.name:
            existing_championship = db.query(Championship).filter(Championship.name == championship_data.name).first()
            if existing_championship:
                logger.error(f"Ya existe un campeonato con el nombre '{championship_data.name}'")
                raise APIError(
                    code=ErrorCodes.DUPLICATE_ENTRY,
                    message="El nombre del campeonato ya está en uso",
                    status_code=400,
                    details=f"Ya existe un campeonato con el nombre '{championship_data.name}'"
                )

        updated_championship = update_championship(db, championship_id, championship_data)
        logger.info(f"Campeonato '{updated_championship.name}' actualizado exitosamente")

        result = serialize_championship(updated_championship, db)
        return result
    except APIError:
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Error de integridad al actualizar campeonato: {str(e)}")
        raise handle_sqlalchemy_error(e, "Campeonato")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error de base de datos al actualizar campeonato: {str(e)}")
        raise handle_sqlalchemy_error(e, "Campeonato")
    except Exception as e:
        db.rollback()
        logger.error(f"Error inesperado al actualizar campeonato: {str(e)}")
        raise CommonErrors.internal_error(f"Error al actualizar el campeonato: {str(e)}")


# ✅ Eliminar un campeonato
@router.delete("/delete/{championship_id}", response_model=dict)
@handle_exceptions
async def delete_existing_championship(championship_id: int, db: Session = Depends(get_db)):
    try:
        championship = get_championship_by_id(db, championship_id)
        if not championship:
            logger.error(f"Campeonato con ID {championship_id} no encontrado")
            raise CommonErrors.not_found("Campeonato", championship_id)

        delete_championship(db, championship_id)
        logger.info(f"Campeonato con ID {championship_id} eliminado exitosamente")

        return {
            "message": "Campeonato eliminado exitosamente",
            "code": "SUCCESS",
            "details": {
                "id": championship_id,
                "name": championship.name
            }
        }
    except APIError:
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Error de integridad al eliminar campeonato: {str(e)}")
        raise APIError(
            code=ErrorCodes.INTEGRITY_ERROR,
            message="No se puede eliminar el campeonato",
            status_code=400,
            details="Este campeonato tiene asignaciones u otros registros asociados. Elimine primero esas relaciones."
        )
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error de base de datos al eliminar campeonato: {str(e)}")
        raise handle_sqlalchemy_error(e, "Campeonato")
    except Exception as e:
        db.rollback()
        logger.error(f"Error inesperado al eliminar campeonato: {str(e)}")
        raise CommonErrors.internal_error(f"Error al eliminar el campeonato: {str(e)}")

