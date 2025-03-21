from sqlalchemy.orm import Session
from models.models import Championship
from schemas.championship import ChampionshipCreate, ChampionshipUpdate

def get_all_championships(db: Session):
    return db.query(Championship).all()

def get_championship_by_id(db: Session, championship_id: int):
    return db.query(Championship).filter(Championship.id == championship_id).first()

def create_championship(db: Session, championship_data: ChampionshipCreate):
    # Usamos el esquema ChampionshipCreate para asegurarnos de que los datos sean válidos
    new_championship = Championship(
        name=championship_data.name,
        location=championship_data.location,
        start_date=championship_data.start_date,
        end_date=championship_data.end_date,
        organizer_id=championship_data.organizer_id,
        discipline_id=championship_data.discipline_id,
        description=championship_data.description
    )
    db.add(new_championship)
    db.commit()
    db.refresh(new_championship)
    return new_championship

def update_championship(db: Session, championship_id: int, championship_data: ChampionshipUpdate):
    # Usamos ChampionshipUpdate para actualizar los datos
    championship = db.query(Championship).filter(Championship.id == championship_id).first()
    if not championship:
        raise ValueError(f"Campeonato con ID {championship_id} no encontrado")

    if championship_data.name is not None:
        championship.name = championship_data.name
    if championship_data.location is not None:
        championship.location = championship_data.location
    if championship_data.start_date is not None:
        championship.start_date = championship_data.start_date
    if championship_data.end_date is not None:
        championship.end_date = championship_data.end_date
    if championship_data.organizer_id is not None:
        championship.organizer_id = championship_data.organizer_id
    if championship_data.discipline_id is not None:
        championship.discipline_id = championship_data.discipline_id
    if championship_data.description is not None:
        championship.description = championship_data.description

    db.commit()
    db.refresh(championship)
    return championship

def delete_championship(db: Session, championship_id: int):
    championship = db.query(Championship).filter(Championship.id == championship_id).first()
    if not championship:
        raise ValueError(f"Campeonato con ID {championship_id} no encontrado")

    db.delete(championship)
    db.commit()
