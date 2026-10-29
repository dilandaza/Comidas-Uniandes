from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(
    title="BolsilloU API",
    description="Backend con detalles de platos y precios para BolsilloU",
    version="1.0.6"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lista completa con platos detallados para cada restaurante cerca a UniAndes
RESTAURANTES_CON_PLATOS = [
    {
        "nombre": "La Nena Restaurante",
        "direccion": "Calle 19A # 1-28, Bogotá (Cerca a UniAndes)",
        "calificacion": 4.6,
        "total_reviews": 128,
        "id_lugar": "fallback_1",
        "abierto": True,
        "lat": 4.6025,
        "lng": -74.0665,
        "platos": [
            {
                "nombre": "Menú Ejecutivo de Pollo",
                "precio": 13000,
                "descripcion": "Incluye sopa del día, pechuga a la plancha, arroz, frijol, ensalada y bebida."
            },
            {
                "nombre": "Sobrebarriga en Salsa",
                "precio": 15000,
                "descripcion": "Carne tierna en salsa criolla con yuca, papa cocida, arroz y arepa."
            }
        ]
    },
    {
        "nombre": "El Gato Gris",
        "direccion": "Cra. 2 # 12-40, La Candelaria, Bogotá",
        "calificacion": 4.5,
        "total_reviews": 310,
        "id_lugar": "fallback_2",
        "abierto": True,
        "lat": 4.5985,
        "lng": -74.0705,
        "platos": [
            {
                "nombre": "Bowl Vegano de la Casa",
                "precio": 18000,
                "descripcion": "Base de quinua, falafel de garbanzo, aguacate, tomates cherry y aderezo de tahini."
            },
            {
                "nombre": "Crepes de Espinaca y Queso",
                "precio": 16000,
                "descripcion": "Masa artesanal rellena de espinacas salteadas, ricotta y gratinado con queso mozzarella."
            }
        ]
    },
    {
        "nombre": "Wok & Bowl Universitario",
        "direccion": "Calle 20 # 2-30, Bogotá",
        "calificacion": 4.7,
        "total_reviews": 95,
        "id_lugar": "fallback_3",
        "abierto": True,
        "lat": 4.6015,
        "lng": -74.0650,
        "platos": [
            {
                "nombre": "Teriyaki Bowl de Pollo",
                "precio": 16000,
                "descripcion": "Arroz jaspeado, trozos de pollo glaseados en salsa teriyaki, vegetales salteados y ajonjolí."
            },
            {
                "nombre": "Bowl Vegetariano de Tofu",
                "precio": 15000,
                "descripcion": "Tofú crocante marinado, edamame, zanahoria, pepino y base de arroz integral."
            }
        ]
    },
    {
        "nombre": "Rápidos del Campus",
        "direccion": "Cra. 1 Este # 18A-12, Bogotá",
        "calificacion": 4.2,
        "total_reviews": 64,
        "id_lugar": "fallback_4",
        "abierto": True,
        "lat": 4.6020,
        "lng": -74.0640,
        "platos": [
            {
                "nombre": "Perro Caliente Universitario",
                "precio": 9000,
                "descripcion": "Salchicha premium, queso fundido, papa fosforito y salsas de la casa."
            },
            {
                "nombre": "Salchipapa Express",
                "precio": 11000,
                "descripcion": "Papas a la francesa doradas, trozos de salchicha ranchera y queso costeño rallado."
            }
        ]
    }
]

@app.get("/")
def ruta_raiz():
    return {"mensaje": "¡BolsilloU API con platos y menús activos!"}

@app.get("/api/restaurantes")
def obtener_restaurantes(query: str = "almuerzo"):
    if query and query != "almuerzo":
        filtrados = [r for r in RESTAURANTES_CON_PLATOS if query.lower() in r["nombre"].lower() or any(query.lower() in p["nombre"].lower() for p in r["platos"])]
        return filtrados if filtrados else RESTAURANTES_CON_PLATOS
    
    return RESTAURANTES_CON_PLATOS