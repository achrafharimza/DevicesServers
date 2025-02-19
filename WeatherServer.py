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

def get_temperature():
    """Récupère la température actuelle depuis OpenWeatherMap."""
    try:
        response = requests.get(API_URL)
        data = response.json()
        return data["main"]["temp"]
    except Exception as e:
        print(f"Erreur lors de la récupération de la température : {e}")
        return None

def publish_temperature():
    """Publie la température actuelle sur MQTT."""
    while True:
        temp = get_temperature()
        if temp is not None:
            payload = json.dumps({"temperature": temp})
            client.publish(TOPIC, payload)
            print(f"Température publiée : {payload}")
        time.sleep(300)  # Mise à jour toutes les 5 minutes

if __name__ == "__main__":
    try:
        publish_temperature()
    except KeyboardInterrupt:
        print("Arrêt du serveur de température.")
