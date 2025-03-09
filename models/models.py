from sqlalchemy import Column, Date, Integer, String, ForeignKey, DateTime, Float, Table
from sqlalchemy.orm import relationship
from db.database import Base

# Tabla intermedia para la relación muchos-a-muchos entre roles y permisos
role_permission_association = Table(
    "role_permission_association",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id"), primary_key=True)
)

# Modelo de Usuario
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    roles = relationship("UserRole", back_populates="user")
    assignments = relationship("ChampionshipAssignment", back_populates="user")

# Modelo de Rol
class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    permissions = relationship("Permission", secondary=role_permission_association, back_populates="roles")
    users = relationship("UserRole", back_populates="role")

# Modelo de Permiso
class Permission(Base):
    __tablename__ = "permissions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String)
    roles = relationship("Role", secondary=role_permission_association, back_populates="permissions")

# Tabla intermedia para la relación muchos-a-muchos entre usuarios y roles
class UserRole(Base):
    __tablename__ = "user_roles"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    role_id = Column(Integer, ForeignKey("roles.id"), primary_key=True)
    user = relationship("User", back_populates="roles")
    role = relationship("Role", back_populates="users")

class Championship(Base):
    __tablename__ = "championships"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    location = Column(String)
    start_date = Column(Date)  # Cambiado de DateTime a Date
    end_date = Column(Date)    # Cambiado de DateTime a Date
    organizer_id = Column(Integer, ForeignKey("organizers.id"))
    discipline_id = Column(Integer, ForeignKey("disciplines.id"))
    description = Column(String, nullable=True)  # Añadido campo de descripción

    organizer = relationship("Organizer", back_populates="championships")
    discipline = relationship("Discipline", back_populates="championships")
    assignments = relationship("ChampionshipAssignment", back_populates="championship")

# Modelo de Puesto de Trabajo
class JobPosition(Base):
    __tablename__ = "job_positions"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True, index=True, nullable=False)
    description = Column(String)
    assignments = relationship("ChampionshipAssignment", back_populates="job_position")

# Modelo de Asignación de Usuarios a Campeonatos
class ChampionshipAssignment(Base):
    __tablename__ = "championship_assignments"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    championship_id = Column(Integer, ForeignKey("championships.id"), primary_key=True)
    job_position_id = Column(Integer, ForeignKey("job_positions.id"))
    hours_worked = Column(Float)
    start_date = Column(Date, nullable=True)  # Fecha de inicio de la asignación
    end_date = Column(Date, nullable=True)    # Fecha de fin de la asignación

    user = relationship("User", back_populates="assignments")
    championship = relationship("Championship", back_populates="assignments")
    job_position = relationship("JobPosition", back_populates="assignments")

# Modelo de Organizador
class Organizer(Base):
    __tablename__ = "organizers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    placement = Column(String, nullable=True)  # Ubicación física
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    website = Column(String, nullable=True)
    championships = relationship("Championship", back_populates="organizer")

# Modelo de Disciplina
class Discipline(Base):
    __tablename__ = "disciplines"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    category = Column(String) 
    championships = relationship("Championship", back_populates="discipline")
