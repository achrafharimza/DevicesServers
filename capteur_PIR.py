import paho.mqtt.client as mqtt
import json
import time
import random
from datetime import datetime

# IDs des capteurs disponibles
sensor_ids = [1, 2, 3, 4]

# Callback lorsque le client se connecte au broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connecté au broker MQTT")
    else:
        print(f"Échec de connexion au broker, code : {rc}")

# Fonction pour envoyer une notification de mouvement détecté avec timestamp
def send_motion_detected(client, sensor_id):
    # Récupérer le temps actuel
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Préparer le payload JSON avec l'ID du capteur, l'état et le timestamp
    payload = json.dumps({
        "sensor_id": sensor_id,
        "status": "MOUVEMENT_DETECTE",
        "timestamp": timestamp
    })
    # Publier le message
    client.publish("lampe/motion/status", payload)
    print(f"Notification de mouvement envoyée pour capteur {sensor_id}: {payload}")

# Simulation de mouvement pour plusieurs capteurs
def simulate_motion(client):
    while True:
        # Sélectionner un capteur aléatoire
        sensor_id = random.choice(sensor_ids)

        # Déterminer si ce capteur détecte un mouvement
        motion_detected = random.choice([True, False])

        # Envoyer uniquement si un mouvement est détecté
        if motion_detected:
            send_motion_detected(client, sensor_id)

        # Attente avant la prochaine simulation
        time.sleep(random.randint(3, 7))  # Intervalle aléatoire de 3 à 7 secondes

# Configuration du client MQTT
def main():
    client = mqtt.Client("motion-detector-simulator")
    client.on_connect = on_connect

    # Connexion au broker MQTT
    broker = "broker.hivemq.com"  # Adresse du broker
    port = 1883  # Port MQTT par défaut
    client.connect(broker, port, 60)

    # Démarrer la boucle MQTT
    client.loop_start()

    try:
        simulate_motion(client)
    except KeyboardInterrupt:
        print("Arrêt du simulateur.")
        client.loop_stop()

if __name__ == "__main__":
    main()
