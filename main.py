from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from routers import users, roles, auth, logs, championships, jobs_position, assignments, discipline, organizers
from sqlalchemy.orm import Session
from db.database import get_db, engine, Base
from models.models import User, Role, UserRole, Permission, role_permission_association
from utils.hash import hash_password
from utils.validation_errors import register_exception_handlers
from logging_config import logger
import os
from dotenv import load_dotenv
from datetime import datetime
from db.database import Base, engine  # o el path correcto según tu estructura

Base.metadata.create_all(bind=engine)


# Cargar variables de entorno
load_dotenv()

app = FastAPI(
    title="Sistema de Gestión de Usuarios y Roles",
    description="API para la gestión de usuarios, roles y permisos",
    version="1.0.0",
    root_path="/api",
)

# Configuración de CORS
origins = [
    "http://localhost:5173",  # Frontend development server
    "http://localhost:5174",  # Frontend development server (alternative port)
    "http://localhost:3000",  # Alternative frontend port
    "http://localhost",
    "https://wavestudio-backend.com",  # Production domain
    "http://wavestudio-backend.com",   # Production domain (HTTP)
    "https://wavestudio-backend.com/*",  # Production domain with wildcard
    "http://wavestudio-backend.com/*",   # Production domain with wildcard
]

# Función para obtener los orígenes permitidos
def get_allowed_origins():
    # Si estamos en modo debug, permitimos todos los orígenes
    if os.getenv("DEBUG", "False").lower() == "true":
        logger.info("Modo DEBUG activado: permitiendo todos los orígenes en CORS")
        return ["*"]
    # En producción, solo permitimos orígenes específicos
    logger.info(f"Configurando CORS con orígenes específicos: {origins}")
    return origins

# Manejador personalizado para HTTPException que preserva los headers CORS
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from starlette.requests import Request

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Manejador personalizado para HTTPException que preserva los headers CORS.
    """
    response = JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )
    
    # Añadir headers CORS a la respuesta
    origin = request.headers.get("origin")
    if origin and origin in origins:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Content-Type", "Authorization", "Accept", "X-Requested-With"],
    expose_headers=["Content-Length"],
    max_age=600,  # Cache preflight requests for 10 minutes
)

# Función para crear un usuario Master inicial si no existe ninguno
def create_initial_master_user(db: Session):
    # Verificar si ya existen usuarios
    users_count = db.query(User).count()
    if users_count > 0:
        logger.info("Ya existen usuarios en la base de datos, no se creará el usuario Master inicial")
        return
    
    # Obtener credenciales desde variables de entorno
    master_username = os.getenv("MASTER_USERNAME", "admin")
    master_email = os.getenv("MASTER_EMAIL", "admin@admin.com")
    # Use a strong default password with mixed case, numbers, and special characters
    # In production, always set MASTER_PASSWORD in environment variables
    master_password = os.getenv("MASTER_PASSWORD", "P@ssw0rd_S3cure!2024")
    
    # Verificar si ya existe el rol "master"
    master_role = db.query(Role).filter(Role.name == "master").first()
    
    # Si no existe, crear el rol "master"
    if not master_role:
        logger.info("Creando rol 'master'...")
        master_role = Role(name="master", description="Usuario con todos los permisos")
        db.add(master_role)
        db.commit()
        db.refresh(master_role)
    
    # Crear el usuario Master
    logger.info(f"Creando usuario Master inicial: {master_username}")
    hashed_password = hash_password(master_password)
    
    master_user = User(
        username=master_username,
        email=master_email,
        password_hash=hashed_password,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(master_user)
    db.commit()
    db.refresh(master_user)
    
    # Asignar el rol "master" al usuario
    user_role = UserRole(user_id=master_user.id, role_id=master_role.id)
    db.add(user_role)
    db.commit()
    
    logger.info(f"Usuario Master inicial creado con ID: {master_user.id}")

# Evento de inicio de la aplicación
@app.on_event("startup")
async def startup_event():
    logger.info("Iniciando la aplicación...")
    # Crear tablas si no existen
    Base.metadata.create_all(bind=engine)
    
    # Registrar manejadores de excepciones personalizados
    register_exception_handlers(app)
    logger.info("Manejadores de excepciones personalizados registrados")
    
    # Obtener una sesión de base de datos
    db = next(get_db())
    try:
        # Crear usuario Master inicial
        create_initial_master_user(db)
    finally:
        db.close()

# Registrar los routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(roles.router)
app.include_router(logs.router)
app.include_router(championships.router)
app.include_router(jobs_position.router)
app.include_router(assignments.router)
app.include_router(discipline.router)
app.include_router(organizers.router)

@app.get("/")
async def root():
    return {
        "message": "Bienvenido a la API de Gestión de Usuarios y Roles",
        "version": "1.0.0",
        "documentation": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
