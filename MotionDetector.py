import paho.mqtt.client as mqtt
import json
import time
import random
from datetime import datetime

# État initial des détecteurs de mouvement (tous "OFF")
motion_detector_states = {
    "1": "OFF",
    "2": "OFF",
    "3": "OFF",
    "4": "OFF"
}

# Callback lorsque le client se connecte au broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connecté au broker MQTT")
        # S'abonner au topic pour recevoir les commandes
        client.subscribe("motionDetector/command")
    else:
        print(f"Échec de connexion au broker, code : {rc}")

# Callback lorsque le client reçoit un message
def on_message(client, userdata, msg):
    global motion_detector_states
    print(f"Message reçu sur {msg.topic}: {msg.payload.decode()}")

    try:
        # Traiter le message JSON reçu
        command = json.loads(msg.payload.decode())
        sensor_id = str(command.get("id"))  # Convertir en chaîne pour correspondre aux clés
        state = command.get("etat")

        # Modifier l'état du capteur si la commande est valide
        if sensor_id in motion_detector_states and state in ["ON", "OFF"]:
            motion_detector_states[sensor_id] = state
            print(f"Détecteur {sensor_id} changé à l'état : {motion_detector_states[sensor_id]}")
            client.publish("motionDetector/status", json.dumps({"id": sensor_id, "etat": motion_detector_states[sensor_id]}))
        else:
            print("Commande invalide : état inconnu ou ID invalide")
    except Exception as e:
        print(f"Erreur lors du traitement de la commande : {e}")

# Fonction pour envoyer une notification de mouvement détecté
def send_motion_detected(client, sensor_id):
    # Récupérer le temps actuel
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Préparer le payload JSON
    payload = json.dumps({
        "sensor_id": sensor_id,
        "status": "MOUVEMENT_DETECTE",
        "timestamp": timestamp
    })
    # Publier le message
    client.publish("motionDetector/motion", payload)
    print(f"Notification de mouvement envoyée : {payload}")

# Simulation de mouvement pour les capteurs activés
def simulate_motion(client):
    while True:
        # Filtrer les capteurs activés
        active_sensors = [sid for sid, state in motion_detector_states.items() if state == "ON"]

        if active_sensors:
            # Sélectionner un capteur actif aléatoire
            sensor_id = random.choice(active_sensors)

            # Simuler un mouvement
            motion_detected = random.choice([True, False])

            if motion_detected:
                send_motion_detected(client, sensor_id)

        # Attente avant la prochaine simulation
        time.sleep(random.randint(10, 17))  # Intervalle aléatoire de 3 à 7 secondes

# Configuration du client MQTT
def main():
    client = mqtt.Client("motion-detector-server")
    client.on_connect = on_connect
    client.on_message = on_message

    # Connexion au broker MQTT
    broker = "broker.hivemq.com"
    port = 1883
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
