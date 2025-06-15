import paho.mqtt.client as mqtt
import requests
import json
import time

# Configuration de l'API OpenWeatherMap
API_KEY = "5fa988728912c96f18d5abbb35a0a12f"  # Remplace par ta clé API
CITY = "Casablanca"  # Remplace par ta ville
API_URL = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"

# Configuration MQTT
BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = "weather/status"

# Initialisation du client MQTT
client = mqtt.Client("weatherServer")
client.connect(BROKER, PORT, 60)

def get_weather_data():
    """Récupère la température actuelle depuis OpenWeatherMap."""
    try:
        response = requests.get(API_URL)
        data = response.json()
        if response.status_code == 200:
            weather_info = {
                "temperature": data["main"]["temp"],
                "temp_max": data["main"]["temp_max"],
                "temp_min": data["main"]["temp_min"],
                "wind": round(data["wind"]["speed"] * 3.6, 2),  # Conversion en km/h
                "humidity": data["main"]["humidity"]
            }
            return weather_info
        else:
            print(f"Erreur API : {data}")
            return None
    except Exception as e:
        print(f"Erreur lors de la récupération de la température weather: {e}")
        return None

def publish_weather():
    while True:
        weather_data = get_weather_data()
        if weather_data:
            payload = json.dumps(weather_data)
            client.publish(TOPIC, payload)
            print(f"Données météo publiées : {payload}")
        time.sleep(900)  # Met à jour toutes les 5 minutes

if __name__ == "__main__":
    try:
        publish_weather()
    except KeyboardInterrupt:
        print("Arrêt du serveur de température.")
