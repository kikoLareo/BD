from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime  # Importa DateTime
from sqlalchemy.orm import relationship
from db.database import Base

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)

    permissions = relationship("RolePermission", back_populates="role")
    users = relationship("UserRole", back_populates="role")

class Permission(Base):
    __tablename__ = "permissions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)

    roles = relationship("RolePermission", back_populates="permission")

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    roles = relationship("UserRole", back_populates="user")
    assignments = relationship("ChampionshipAssignment", back_populates="user")


class UserRole(Base):
    __tablename__ = 'user_roles'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    role_id = Column(Integer, ForeignKey('roles.id'), primary_key=True)
    user = relationship("User", back_populates="roles")
    role = relationship("Role", back_populates="users")


class RolePermission(Base):
    __tablename__ = "role_permissions"
    role_id = Column(Integer, ForeignKey("roles.id"), primary_key=True)
    permission_id = Column(Integer, ForeignKey("permissions.id"), primary_key=True)

    role = relationship("Role", back_populates="permissions")
    permission = relationship("Permission", back_populates="roles")


# Tabla de Campeonatos
class Championship(Base):
    __tablename__ = "championships"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    location = Column(String)
    date = Column(DateTime)
    assignments = relationship("ChampionshipAssignment", back_populates="championship")

# Tabla de Puestos de Trabajo
class JobPosition(Base):
    __tablename__ = "job_positions"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True, index=True)
    description = Column(String)
    assignments = relationship("ChampionshipAssignment", back_populates="job_position")

# Tabla de Asignación de Usuarios a Campeonatos
class ChampionshipAssignment(Base):
    __tablename__ = "championship_assignments"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    championship_id = Column(Integer, ForeignKey("championships.id"), primary_key=True)
    job_position_id = Column(Integer, ForeignKey("job_positions.id"))
    hours_worked = Column(Float)

    user = relationship("User", back_populates="assignments")
    championship = relationship("Championship", back_populates="assignments")
    job_position = relationship("JobPosition", back_populates="assignments")