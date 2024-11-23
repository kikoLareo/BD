from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import users, roles, auth, logs, championships, jobs_position, assignments, discipline, organizers

app = FastAPI()

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambia esto a tu dominio de GitHub Pages
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    return {"message": "Bienvenido a la API de Gestión de Usuarios y Roles"}