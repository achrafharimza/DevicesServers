import paho.mqtt.client as mqtt
import json
import time
import random

# Configuration du capteur de température
TEMP_SENSOR_ID = 1
MIN_TEMPERATURE = 15.0  # Température minimale simulée
MAX_TEMPERATURE = 30.0  # Température maximale simulée
PUBLISH_INTERVAL = 5  # Intervalle en secondes entre les publications

def send_temperature_data(client):
    while True:
        # Générer une température aléatoire dans la plage définie
        temperature = round(random.uniform(MIN_TEMPERATURE, MAX_TEMPERATURE), 2)

        # Préparer le payload
        payload = {
            "sensor_id": TEMP_SENSOR_ID,
            "temperature": temperature,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")  # Ajouter un horodatage
        }

        # Publier les données sur le topic MQTT
        client.publish("temp-sensor/data", json.dumps(payload))
        print(f"Données publiées : {payload}")

        # Attente avant la prochaine publication
        time.sleep(PUBLISH_INTERVAL)

def main():
    # Créer un client MQTT
    client = mqtt.Client("temp-sensor-server")

    # Connexion au broker MQTT
    broker = "broker.hivemq.com"  # Adresse du broker
    port = 1883  # Port MQTT par défaut
    client.connect(broker, port, 60)

    try:
        # Envoyer les données de température en continu
        send_temperature_data(client)
    except KeyboardInterrupt:
        print("Arrêt du serveur de capteur de température.")

if __name__ == "__main__":
    main()
