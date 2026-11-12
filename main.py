import logging
import os
import time

import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("bolsillou")

app = FastAPI(title="BolsilloU API", version="1.1.3")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

LAT_UNI, LNG_UNI = 4.6017, -74.0662
FOTO_DEFECTO = "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=600&q=80"

# Definición de menús con variedad de precios (incluyendo opciones mayores a $20.000)
MENU_OPCIONES = [
    {
        "foto": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=600&q=80",
        "platos": [
            {"nombre": "Menú Ejecutivo del Día", "precio": 12000, "descripcion": "Sopa, plato principal con carne o pollo, arroz, ensalada y jugo."},
            {"nombre": "Parrillada Especial de la Casa", "precio": 24000, "descripcion": "Corte de res a la parrilla, chorizo, papa criolla, arepa y chimichurri."}
        ],
        "resenas": [
            {"usuario": "Sofía G. (Derecho)", "estrellas": 5, "comentario": "¡Excelente porción y súper económico!"}
        ]
    },
    {
        "foto": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=600&q=80",
        "platos": [
            {"nombre": "Bowl Universitario", "precio": 15000, "descripcion": "Base de arroz o quinua, proteína a elección y aguacate."},
            {"nombre": "Hamburguesa Artesanal Doble", "precio": 22000, "descripcion": "Doble carne angus, queso cheddar fundido, tocineta y papas rústicas."}
        ],
        "resenas": [
            {"usuario": "Daniel M. (Ingeniería)", "estrellas": 5, "comentario": "La hamburguesa vale totalmente la pena cuando hay presupuesto."}
        ]
    },
    {
        "foto": "https://images.unsplash.com/photo-1543353071-10c8ba85a904?auto=format&fit=crop&w=600&q=80",
        "platos": [
            {"nombre": "Pasta Casera Boloñesa", "precio": 14000, "descripcion": "Porción generosa de pasta con salsa de carne tradicional y queso parmesano."},
            {"nombre": "Lomo de Cerdo en Salsa BBQ", "precio": 21000, "descripcion": "Jugoso lomo bañado en salsa BBQ artesanal con puré de papa."}
        ],
        "resenas": [
            {"usuario": "Juan K. (Diseño)", "estrellas": 5, "comentario": "La pasta boloñesa es increíblemente barata y rica."}
        ]
    },
    {
        "foto": "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?auto=format&fit=crop&w=600&q=80",
        "platos": [
            {"nombre": "Salchipapa Estudiantil", "precio": 11000, "descripcion": "Papas doradas, trozos de salchicha, queso costeño y salsas."},
            {"nombre": "Perro Caliente con Queso", "precio": 9500, "descripcion": "Pan artesanal, salchicha alemana, papa fosforito y queso fundido."}
        ],
        "resenas": [
            {"usuario": "Felipe R. (Ing. Sistemas)", "estrellas": 4, "comentario": "Salvavidas total cuando el presupuesto está bajo a fin de mes."}
        ]
    }
]

NIVELES_PRECIO = {
    "PRICE_LEVEL_FREE": "Gratis",
    "PRICE_LEVEL_INEXPENSIVE": "$",
    "PRICE_LEVEL_MODERATE": "$$",
    "PRICE_LEVEL_EXPENSIVE": "$$$",
    "PRICE_LEVEL_VERY_EXPENSIVE": "$$$$",
}

EXCLUIR = ("universidad", "edificio", "tienda d1")
CACHE_TTL = 300
_cache: dict[str, tuple[float, list]] = {}

@app.get("/")
def ruta_raiz():
    return {"mensaje": "¡BolsilloU API con fotos reales activa!"}

@app.get("/api/restaurantes")
def obtener_restaurantes(query: str = "almuerzo"):
    query = query.strip()[:80] or "almuerzo"

    if not GOOGLE_API_KEY:
        return [
            {
                "nombre": "La Nena Restaurante", "direccion": "Calle 19A # 1-28, Bogotá",
                "calificacion": 4.6, "total_reviews": 128, "id_lugar": "rest_1", "abierto": True,
                "lat": 4.6025, "lng": -74.0665, "foto": FOTO_DEFECTO, "nivel_precio": "$$", "es_ejemplo": True,
                "platos": [
                    {"nombre": "Menú Ejecutivo", "precio": 12000, "descripcion": "Sopa, seco y jugo."},
                    {"nombre": "Parrillada Especial", "precio": 24000, "descripcion": "Corte de res con acompañamientos."}
                ],
                "resenas": [{"usuario": "Sofía G.", "estrellas": 5, "comentario": "¡Excelente!"}]
            }
        ]

    ahora = time.time()
    clave = query.lower()
    if clave in _cache and ahora - _cache[clave][0] < CACHE_TTL:
        return _cache[clave][1]

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_API_KEY,
        "X-Goog-FieldMask": (
            "places.displayName,places.formattedAddress,places.rating,"
            "places.userRatingCount,places.priceLevel,places.id,"
            "places.businessStatus,places.location,places.photos"
        ),
    }
    body = {
        "textQuery": f"{query} restaurante cerca a Universidad de los Andes Bogotá",
        "locationBias": {"circle": {"center": {"latitude": LAT_UNI, "longitude": LNG_UNI}, "radius": 1500.0}},
        "languageCode": "es",
    }

    try:
        resp = requests.post(
            "https://places.googleapis.com/v1/places:searchText",
            json=body, headers=headers, timeout=10,
        )
        if resp.status_code != 200:
            return []

        resultados = []
        for i, place in enumerate(resp.json().get("places", [])):
            nombre = place.get("displayName", {}).get("text", "Restaurante cercano")
            if any(x in nombre.lower() for x in EXCLUIR):
                continue
            
            loc = place.get("location", {})
            
            # Banco interno de fotos variadas para evitar repetir la misma imagen
            FOTOS_VARIADAS = [
                "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=600&q=80",
                "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=600&q=80",
                "https://images.unsplash.com/photo-1543353071-10c8ba85a904?auto=format&fit=crop&w=600&q=80",
                "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?auto=format&fit=crop&w=600&q=80",
                "https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=600&q=80",
                "https://images.unsplash.com/photo-1552566626-52f8b828add9?auto=format&fit=crop&w=600&q=80"
            ]

            # Intentamos extraer la foto real de Google Places si viene en la respuesta
            foto_url = None
            photos = place.get("photos", [])
            if photos and len(photos) > 0:
                photo_name = photos[0].get("name")
                if photo_name:
                    foto_url = f"https://places.googleapis.com/v1/{photo_name}/media?maxHeightPx=600&maxWidthPx=600&key={GOOGLE_API_KEY}"

            # Si Google no trae foto para este lugar específico, usamos una variada del banco rotativo
            if not foto_url:
                foto_url = FOTOS_VARIADAS[i % len(FOTOS_VARIADAS)]

            # Asignamos menús rotativos según el índice para que cada local tenga variedad y precios altos (>20k)
            menu_asignado = MENU_OPCIONES[i % len(MENU_OPCIONES)]

            resultados.append({
                "nombre": nombre,
                "direccion": place.get("formattedAddress", "Cerca al campus"),
                "calificacion": place.get("rating", 4.5),
                "total_reviews": place.get("userRatingCount", 20),
                "id_lugar": place.get("id", str(i)),
                "abierto": place.get("businessStatus", "OPERATIONAL") == "OPERATIONAL",
                "lat": loc.get("latitude", LAT_UNI),
                "lng": loc.get("longitude", LNG_UNI),
                "foto": foto_url,
                "nivel_precio": NIVELES_PRECIO.get(place.get("priceLevel", ""), "$$"),
                "es_ejemplo": False,
                "platos": menu_asignado["platos"],
                "resenas": menu_asignado["resenas"]
            })

        if resultados:
            _cache[clave] = (ahora, resultados)
            return resultados
    except Exception:
        log.exception("Error consultando Google Places")

    return []