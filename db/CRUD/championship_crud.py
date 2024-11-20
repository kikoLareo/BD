from sqlalchemy.orm import Session
from models.models import Championship
from schemas.championship import ChampionshipCreate, ChampionshipUpdate

def get_all_championships(db: Session):
    return db.query(Championship).all()

def get_championship_by_id(db: Session, championship_id: int):
    return db.query(Championship).filter(Championship.id == championship_id).first()

def create_championship(db: Session, championship_data: ChampionshipCreate):
    # Usamos el esquema ChampionshipCreate para asegurarnos de que los datos sean válidos
# Suponiendo que el esquema incluye más campos, como 'start_date', 'end_date', 'organizer', 'discipline', etc.
    new_championship = Championship(
        name=championship_data.name,
        location=championship_data.location,
        start_date=championship_data.start_date,  # Campo añadido
        end_date=championship_data.end_date,      # Campo añadido
        organizer_id=championship_data.organizer_id,  # Cambia esto
        discipline=championship_data.discipline   # Campo añadido
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
    if championship_data.date is not None:
        championship.date = championship_data.date

    db.commit()
    db.refresh(championship)
    return championship

def delete_championship(db: Session, championship_id: int):
    championship = db.query(Championship).filter(Championship.id == championship_id).first()
    if not championship:
        raise ValueError(f"Campeonato con ID {championship_id} no encontrado")

    db.delete(championship)
    db.commit()