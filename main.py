from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import os

app = FastAPI(
    title="BolsilloU API",
    description="Backend híbrido con Google Places y platos detallados",
    version="1.0.8"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GOOGLE_API_KEY = os.getenv("AIzaSyBegmQYvWqHaiLfrb9lpiTZnWsqYBJAzMU")

# Fotos e ideas de platos rotativos para asignar a los restaurantes que traiga Google
FOTOS_Y_PLATOS = [
    {
        "foto": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=600&q=80",
        "platos": [
            {"nombre": "Menú Ejecutivo del Día", "precio": 13000, "descripcion": "Incluye sopa, plato principal con carne o pollo, arroz, ensalada y jugo."},
            {"nombre": "Almuerzo Vegetariano", "precio": 12000, "descripcion": "Opción saludable con proteína vegetal, granos, vegetales al vapor y bebida."}
        ]
    },
    {
        "foto": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=600&q=80",
        "platos": [
            {"nombre": "Bowl Universitario", "precio": 16000, "descripcion": "Base de arroz o quinua, proteína a elección, aguacate y vegetales frescos."},
            {"nombre": "Wrap de Pollo y Queso", "precio": 14000, "descripcion": "Tortilla de trigo tostada rellena de pollo desmenuzado, vegetales y salsa de la casa."}
        ]
    },
    {
        "foto": "https://images.unsplash.com/photo-1543353071-10c8ba85a904?auto=format&fit=crop&w=600&q=80",
        "platos": [
            {"nombre": "Pasta Casera Boloñesa", "precio": 15000, "descripcion": "Porción generosa de pasta con salsa de carne tradicional y queso parmesano."},
            {"nombre": "Pechuga Gratinada", "precio": 17000, "descripcion": "Pechuga de pollo jugosa cubierta con queso fundido, acompañada de papas a la francesa."}
        ]
    },
    {
        "foto": "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?auto=format&fit=crop&w=600&q=80",
        "platos": [
            {"nombre": "Salchipapa Estudiantil", "precio": 11000, "descripcion": "Papas doradas, trozos de salchicha, queso costeño y salsas."},
            {"nombre": "Perro Caliente con Queso", "precio": 9500, "descripcion": "Pan artesanal, salchicha alemana, papa fosforito y queso fundido."}
        ]
    }
]

RESTAURANTES_RESPALDO = [
    {
        "nombre": "La Nena Restaurante",
        "direccion": "Calle 19A # 1-28, Bogotá",
        "calificacion": 4.6,
        "total_reviews": 128,
        "id_lugar": "rest_1",
        "abierto": True,
        "lat": 4.6025,
        "lng": -74.0665,
        "foto": FOTOS_Y_PLATOS[0]["foto"],
        "platos": FOTOS_Y_PLATOS[0]["platos"]
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
        "foto": FOTOS_Y_PLATOS[1]["foto"],
        "platos": FOTOS_Y_PLATOS[1]["platos"]
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
        "foto": FOTOS_Y_PLATOS[2]["foto"],
        "platos": FOTOS_Y_PLATOS[2]["platos"]
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
        "foto": FOTOS_Y_PLATOS[3]["foto"],
        "platos": FOTOS_Y_PLATOS[3]["platos"]
    }
]

@app.get("/")
def ruta_raiz():
    return {"mensaje": "¡BolsilloU API híbrida activa!"}

@app.get("/api/restaurantes")
def obtener_restaurantes(query: str = "restaurante económico"):
    if not GOOGLE_API_KEY:
        return RESTAURANTES_RESPALDO

    url = "https://places.googleapis.com/v1/places:searchText"
    
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_API_KEY,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.rating,places.userRatingCount,places.priceLevel,places.id,places.businessStatus,places.location"
    }

    body = {
        "textQuery": f"restaurante almuerzo cerca a Universidad de los Andes Bogota",
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
                for i, place in enumerate(places):
                    nombre_lugar = place.get("displayName", {}).get("text", "Restaurante cercano")
                    
                    # Evitamos incluir edificios institucionales o tiendas que no sean restaurantes
                    nombre_lower = nombre_lugar.lower()
                    if "universidad" in nombre_lower or "edificio" in nombre_lower or "tienda d1" in nombre_lower:
                        continue

                    location = place.get("location", {})
                    lat = location.get("latitude", 4.6017)
                    lng = location.get("longitude", -74.0662)

                    # Asignamos de forma cíclica una foto y un menú de platos de nuestra lista enriquecida
                    info_extra = FOTOS_Y_PLATOS[i % len(FOTOS_Y_PLATOS)]
                    
                    resultados_reales.append({
                        "nombre": nombre_lugar,
                        "direccion": place.get("formattedAddress", "Cerca al campus universitario"),
                        "calificacion": place.get("rating", 4.4),
                        "total_reviews": place.get("userRatingCount", 20),
                        "id_lugar": place.get("id", str(i)),
                        "abierto": place.get("businessStatus", "OPERATIONAL") == "OPERATIONAL",
                        "lat": lat,
                        "lng": lng,
                        "foto": info_extra["foto"],
                        "platos": info_extra["platos"]
                    })
                
                if resultados_reales:
                    return resultados_reales
                
    except Exception:
        pass

    return RESTAURANTES_RESPALDO