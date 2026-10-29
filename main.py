from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="BolsilloU API",
    description="Backend para la gestión de presupuesto y recomendación de restaurantes cerca a UniAndes",
    version="1.0.3"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lista de restaurantes garantizada para el proyecto de Design Thinking
RESTAURANTES_FIJOS = [
    {
        "nombre": "La Nena Restaurante",
        "direccion": "Calle 19A # 1-28, Bogotá (Cerca a UniAndes)",
        "calificacion": 4.6,
        "total_reviews": 128,
        "precio_aprox": 13000,
        "id_lugar": "fallback_1",
        "abierto": True
    },
    {
        "nombre": "El Gato Gris",
        "direccion": "Cra. 2 # 12-40, La Candelaria, Bogotá",
        "calificacion": 4.5,
        "total_reviews": 310,
        "precio_aprox": 18000,
        "id_lugar": "fallback_2",
        "abierto": True
    },
    {
        "nombre": "Wok & Bowl Universitario",
        "direccion": "Calle 20 # 2-30, Bogotá",
        "calificacion": 4.7,
        "total_reviews": 95,
        "precio_aprox": 16000,
        "id_lugar": "fallback_3",
        "abierto": True
    },
    {
        "nombre": "Rápidos del Campus",
        "direccion": "Cra. 1 Este # 18A-12, Bogotá",
        "calificacion": 4.2,
        "total_reviews": 64,
        "precio_aprox": 9000,
        "id_lugar": "fallback_4",
        "abierto": True
    }
]

@app.get("/")
def ruta_raiz():
    return {"mensaje": "¡BolsilloU API activa y funcionando!"}

@app.get("/api/restaurantes")
def obtener_restaurantes(query: str = "almuerzo"):
    # Filtra de manera opcional si el usuario escribe algo en el buscador, o devuelve todos
    if query and query != "almuerzo":
        filtrados = [r for r in RESTAURANTES_FIJOS if query.lower() in r["nombre"].lower() or query.lower() in r["direccion"].lower()]
        return filtrados if filtrados else RESTAURANTES_FIJOS
    
    return RESTAURANTES_FIJOS