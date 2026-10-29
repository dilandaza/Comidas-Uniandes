from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(
    title="BolsilloU API",
    description="Backend optimizado con platos y fotos para BolsilloU",
    version="1.0.7"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Base de datos robusta y detallada orientada 100% a restaurantes universitarios cerca a UniAndes
RESTAURANTES_DETALLADOS = [
    {
        "nombre": "La Nena Restaurante",
        "direccion": "Calle 19A # 1-28, Bogotá",
        "calificacion": 4.6,
        "total_reviews": 128,
        "id_lugar": "rest_1",
        "abierto": True,
        "lat": 4.6025,
        "lng": -74.0665,
        "foto": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=600&q=80",
        "platos": [
            {"nombre": "Menú Ejecutivo de Pollo", "precio": 13000, "descripcion": "Sopa del día, pechuga a la plancha, arroz, frijol, ensalada y jugo."},
            {"nombre": "Sobrebarriga en Salsa", "precio": 15000, "descripcion": "Carne tierna en salsa criolla con yuca, papa cocida y arepa."}
        ]
    },
    {
        "nombre": "El Gato Gris",
        "direccion": "Cra. 2 # 12-40, La Candelaria, Bogotá",
        "calificacion": 4.5,
        "total_reviews": 310,
        "id_lugar": "rest_2",
        "abierto": True,
        "lat": 4.5985,
        "lng": -74.0705,
        "foto": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=600&q=80",
        "platos": [
            {"nombre": "Bowl Vegano de la Casa", "precio": 18000, "descripcion": "Quinua, falafel de garbanzo, aguacate, tomates cherry y tahini."},
            {"nombre": "Crepes de Espinaca", "precio": 16000, "descripcion": "Rellenos de espinacas salteadas, ricotta y gratinados con mozzarella."}
        ]
    },
    {
        "nombre": "Wok & Bowl Universitario",
        "direccion": "Calle 20 # 2-30, Bogotá",
        "calificacion": 4.7,
        "total_reviews": 95,
        "id_lugar": "rest_3",
        "abierto": True,
        "lat": 4.6015,
        "lng": -74.0650,
        "foto": "https://images.unsplash.com/photo-1543353071-10c8ba85a904?auto=format&fit=crop&w=600&q=80",
        "platos": [
            {"nombre": "Teriyaki Bowl de Pollo", "precio": 16000, "descripcion": "Arroz jaspeado, pollo glaseado en salsa teriyaki y vegetales salteados."},
            {"nombre": "Bowl de Tofú Crocante", "precio": 15000, "descripcion": "Tofú marinado, edamame, zanahoria y base de arroz integral."}
        ]
    },
    {
        "nombre": "Rápidos del Campus",
        "direccion": "Cra. 1 Este # 18A-12, Bogotá",
        "calificacion": 4.2,
        "total_reviews": 64,
        "id_lugar": "rest_4",
        "abierto": True,
        "lat": 4.6020,
        "lng": -74.0640,
        "foto": "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?auto=format&fit=crop&w=600&q=80",
        "platos": [
            {"nombre": "Perro Caliente Universitario", "precio": 9000, "descripcion": "Salchicha premium, queso fundido, papa fosforito y salsas."},
            {"nombre": "Salchipapa Express", "precio": 11000, "descripcion": "Papas a la francesa doradas, trozos de salchicha y queso costeño."}
        ]
    },
    {
        "nombre": "Cafetería Central UniAndes",
        "direccion": "Cra. 1 # 18A-12 (Interior Campus)",
        "calificacion": 4.8,
        "total_reviews": 420,
        "id_lugar": "rest_5",
        "abierto": True,
        "lat": 4.6017,
        "lng": -74.0662,
        "foto": "https://images.unsplash.com/photo-1554118811-1e0d58224f24?auto=format&fit=crop&w=600&q=80",
        "platos": [
            {"nombre": "Almuerzo del Estudiante", "precio": 11000, "descripcion": "Sopa, seco económico del día (carne o pollo) y panela."},
            {"nombre": "Empanada casera + Jugo", "precio": 5500, "descripcion": "Dos empanadas de carne o pollo con ají y jugo natural."}
        ]
    }
]

@app.get("/")
def ruta_raiz():
    return {"mensaje": "¡BolsilloU API lista!"}

@app.get("/api/restaurantes")
def obtener_restaurantes(query: str = "almuerzo"):
    if query and query != "almuerzo":
        filtrados = [
            r for r in RESTAURANTES_DETALLADOS 
            if query.lower() in r["nombre"].lower() or any(query.lower() in p["nombre"].lower() for p in r["platos"])
        ]
        return filtrados if filtrados else RESTAURANTES_DETALLADOS
    
    return RESTAURANTES_DETALLADOS