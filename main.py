from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import os

app = FastAPI(
    title="BolsilloU API",
    description="Backend para la gestión de presupuesto y recomendación de restaurantes cerca a UniAndes",
    version="1.0.0"
)

# Configurar CORS para permitir peticiones desde tu frontend (GitHub Pages o local)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción puedes restringirlo a tu URL de GitHub Pages
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Reemplaza esto con tu API Key real de Google Places
GOOGLE_API_KEY = "AIzaSyBEsYS9HvN7BibwqkUSOMSfI9zuOxrQCKE"

@app.get("/")
def ruta_raiz():
    return {"mensaje": "¡Bienvenido al backend de BolsilloU! El servidor está activo."}

@app.get("/api/restaurantes")
def obtener_restaurantes(query: str = "almuerzo"):
    """
    Busca restaurantes cercanos a la Universidad de los Andes utilizando Google Places API.
    """
    # Coordenadas aproximadas de la Universidad de los Andes en Bogotá
    lat = 4.6017
    lng = -74.0662
    radio = 1500  # Radio de búsqueda en metros (1.5 km alrededor del campus)

    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    
    params = {
        "query": f"{query} cerca a Universidad de los Andes Bogotá",
        "location": f"{lat},{lng}",
        "radius": radio,
        "key": GOOGLE_API_KEY,
        "language": "es"
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if response.status_code != 200 or "results" not in data:
            raise HTTPException(status_code=500, detail="Error al consultar la API de Google Places")

        resultados_limpios = []
        for place in data.get("results", []):
            # Nivel de precio en Google (1 a 4). Si no existe, asignamos un valor por defecto (1)
            price_level = place.get("price_level", 1)
            # Fórmula estimada en COP adaptada al presupuesto estudiantil
            precio_estimado = price_level * 6000 + 7000 

            resultados_limpios.append({
                "nombre": place.get("name"),
                "direccion": place.get("formatted_address", "Cerca al campus universitario"),
                "calificacion": place.get("rating", 4.0),
                "total_reviews": place.get("user_ratings_total", 0),
                "precio_aprox": precio_estimado,
                "id_lugar": place.get("place_id"),
                "abierto": place.get("business_status", "OPERATIONAL") == "OPERATIONAL"
            })

        return resultados_limpios

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))