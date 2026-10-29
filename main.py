import logging
import os
import time

import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("bolsillou")

app = FastAPI(title="BolsilloU API", version="1.1.0")

# Sin allow_credentials: no usamos cookies. En producción cambia "*" por tu dominio.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# La clave se lee de la variable de entorno GOOGLE_API_KEY (Render -> Environment).
GOOGLE_API_KEY = os.getenv("AIzaSyBegmQYvWqHaiLfrb9lpiTZnWsqYBJAzMU")

LAT_UNI, LNG_UNI = 4.6017, -74.0662
FOTO_DEFECTO = "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=600&q=80"
FOTOS = [
    FOTO_DEFECTO,
    "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=600&q=80",
    "https://images.unsplash.com/photo-1543353071-10c8ba85a904?auto=format&fit=crop&w=600&q=80",
    "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?auto=format&fit=crop&w=600&q=80",
]

NIVELES_PRECIO = {
    "PRICE_LEVEL_FREE": "Gratis",
    "PRICE_LEVEL_INEXPENSIVE": "$",
    "PRICE_LEVEL_MODERATE": "$$",
    "PRICE_LEVEL_EXPENSIVE": "$$$",
    "PRICE_LEVEL_VERY_EXPENSIVE": "$$$$",
}

# Datos de EJEMPLO (solo para cuando Google no responde). Los platos son ilustrativos.
RESTAURANTES_RESPALDO = [
    {
        "nombre": "La Nena Restaurante", "direccion": "Calle 19A # 1-28, Bogotá",
        "calificacion": 4.6, "total_reviews": 128, "id_lugar": "rest_1", "abierto": True,
        "lat": 4.6025, "lng": -74.0665, "foto": FOTOS[0], "nivel_precio": "$$", "es_ejemplo": True,
        "platos": [
            {"nombre": "Menú Ejecutivo del Día", "precio": 13000, "descripcion": "Sopa, plato principal, arroz, ensalada y jugo."},
            {"nombre": "Almuerzo Vegetariano", "precio": 12000, "descripcion": "Proteína vegetal, granos, vegetales y bebida."},
        ],
    },
    {
        "nombre": "El Gato Gris", "direccion": "Cra. 2 # 12-40, La Candelaria, Bogotá",
        "calificacion": 4.5, "total_reviews": 310, "id_lugar": "rest_2", "abierto": True,
        "lat": 4.5985, "lng": -74.0705, "foto": FOTOS[1], "nivel_precio": "$$", "es_ejemplo": True,
        "platos": [
            {"nombre": "Bowl Universitario", "precio": 16000, "descripcion": "Arroz o quinua, proteína, aguacate y vegetales."},
            {"nombre": "Wrap de Pollo y Queso", "precio": 14000, "descripcion": "Tortilla tostada con pollo, vegetales y salsa."},
        ],
    },
    {
        "nombre": "Rápidos del Campus", "direccion": "Cra. 1 Este # 18A-12, Bogotá",
        "calificacion": 4.2, "total_reviews": 64, "id_lugar": "rest_4", "abierto": True,
        "lat": 4.6020, "lng": -74.0640, "foto": FOTOS[3], "nivel_precio": "$", "es_ejemplo": True,
        "platos": [
            {"nombre": "Salchipapa Estudiantil", "precio": 11000, "descripcion": "Papas, salchicha, queso y salsas."},
            {"nombre": "Perro Caliente con Queso", "precio": 9500, "descripcion": "Pan artesanal, salchicha, papa fosforito y queso."},
        ],
    },
]

# Caché simple en memoria (5 min) para ahorrar llamadas a Google.
CACHE_TTL = 300
_cache: dict[str, tuple[float, list]] = {}

EXCLUIR = ("universidad", "edificio", "tienda d1")


@app.get("/")
def ruta_raiz():
    return {"mensaje": "¡BolsilloU API activa!", "google_configurado": bool(GOOGLE_API_KEY)}


@app.get("/api/restaurantes")
def obtener_restaurantes(query: str = "almuerzo"):
    query = query.strip()[:80] or "almuerzo"

    if not GOOGLE_API_KEY:
        log.warning("GOOGLE_API_KEY no está definida; devolviendo datos de ejemplo")
        return RESTAURANTES_RESPALDO

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
            "places.businessStatus,places.location"
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
            log.error("Google Places respondió %s: %s", resp.status_code, resp.text[:300])
            return RESTAURANTES_RESPALDO

        resultados = []
        for i, place in enumerate(resp.json().get("places", [])):
            nombre = place.get("displayName", {}).get("text", "Restaurante cercano")
            if any(x in nombre.lower() for x in EXCLUIR):
                continue
            loc = place.get("location", {})
            resultados.append({
                "nombre": nombre,
                "direccion": place.get("formattedAddress", "Cerca al campus"),
                "calificacion": place.get("rating", "N/D"),
                "total_reviews": place.get("userRatingCount", 0),
                "id_lugar": place.get("id", str(i)),
                "abierto": place.get("businessStatus", "OPERATIONAL") == "OPERATIONAL",
                "lat": loc.get("latitude", LAT_UNI),
                "lng": loc.get("longitude", LNG_UNI),
                "foto": FOTOS[i % len(FOTOS)],  # foto decorativa, no del lugar real
                "nivel_precio": NIVELES_PRECIO.get(place.get("priceLevel", ""), "N/D"),
                "es_ejemplo": False,
                "platos": [],  # no inventamos menús para lugares reales
            })

        if resultados:
            _cache[clave] = (ahora, resultados)
            return resultados
    except Exception:
        log.exception("Error consultando Google Places")

    return RESTAURANTES_RESPALDO