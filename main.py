from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import os

app = FastAPI(
    title="BolsilloU API",
    description="Backend con coordenadas reales de Google Places",
    version="1.0.5"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

RESTAURANTES_RESPALDO = [
    {
        "nombre": "La Nena Restaurante",
        "direccion": "Calle 19A # 1-28, Bogotá (Cerca a UniAndes)",
        "calificacion": 4.6,
        "total_reviews": 128,
        "precio_aprox": 13000,
        "id_lugar": "fallback_1",
        "abierto": True,
        "lat": 4.6025,
        "lng": -74.0665
    },
    {
        "nombre": "El Gato Gris",
        "direccion": "Cra. 2 # 12-40, La Candelaria, Bogotá",
        "calificacion": 4.5,
        "total_reviews": 310,
        "precio_aprox": 18000,
        "id_lugar": "fallback_2",
        "abierto": True,
        "lat": 4.5985,
        "lng": -74.0705
    },
    {
        "nombre": "Wok & Bowl Universitario",
        "direccion": "Calle 20 # 2-30, Bogotá",
        "calificacion": 4.7,
        "total_reviews": 95,
        "precio_aprox": 16000,
        "id_lugar": "fallback_3",
        "abierto": True,
        "lat": 4.6015,
        "lng": -74.0650
    },
    {
        "nombre": "Rápidos del Campus",
        "direccion": "Cra. 1 Este # 18A-12, Bogotá",
        "calificacion": 4.2,
        "total_reviews": 64,
        "precio_aprox": 9000,
        "id_lugar": "fallback_4",
        "abierto": True,
        "lat": 4.6020,
        "lng": -74.0640
    }
]

@app.get("/")
def ruta_raiz():
    return {"mensaje": "¡BolsilloU API con coordenadas reales activa!"}

@app.get("/api/restaurantes")
def obtener_restaurantes(query: str = "almuerzo"):
    if not GOOGLE_API_KEY:
        return RESTAURANTES_RESPALDO

    url = "https://places.googleapis.com/v1/places:searchText"
    
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_API_KEY,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.rating,places.userRatingCount,places.priceLevel,places.id,places.businessStatus,places.location"
    }

    body = {
        "textQuery": f"{query} cerca a Universidad de los Andes Bogota",
        "locationBias": {
            "circle": {
                "center": {
                    "latitude": 4.6017,
                    "longitude": -74.0662
                },
                "radius": 1500.0
            }
        },
        "languageCode": "es"
    }

    try:
        response = requests.post(url, json=body, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            places = data.get("places", [])
            
            if places:
                resultados_reales = []
                for place in places:
                    price_str = place.get("priceLevel", "PRICE_LEVEL_MODERATE")
                    multiplicador = 1 if "INEXPENSIVE" in price_str else (2 if "MODERATE" in price_str else 3)
                    precio_estimado = multiplicador * 6000 + 7000

                    nombre_lugar = place.get("displayName", {}).get("text", "Restaurante cercano")
                    
                    # Extraemos las coordenadas reales devueltas por Google Maps
                    location = place.get("location", {})
                    lat = location.get("latitude", 4.6017)
                    lng = location.get("longitude", -74.0662)
                    
                    resultados_reales.append({
                        "nombre": nombre_lugar,
                        "direccion": place.get("formattedAddress", "Cerca al campus universitario"),
                        "calificacion": place.get("rating", 4.3),
                        "total_reviews": place.get("userRatingCount", 12),
                        "precio_aprox": precio_estimado,
                        "id_lugar": place.get("id"),
                        "abierto": place.get("businessStatus", "OPERATIONAL") == "OPERATIONAL",
                        "lat": lat,
                        "lng": lng
                    })
                return resultados_reales
                
    except Exception:
        pass

    return RESTAURANTES_RESPALDO