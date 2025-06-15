import paho.mqtt.client as mqtt
import json
import time
import random
from datetime import datetime
import serial

arduino = serial.Serial('COM13', 9600, timeout=1)
time.sleep(2)
# État initial des détecteurs de mouvement (tous "OFF")
motion_detector_states = {
    "1": "ON",
    "2": "ON",
    "3": "ON",
    "4": "ON"
}

# Callback lorsque le client se connecte au broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connecté au broker MQTT motionDetector")
        # S'abonner au topic pour recevoir les commandes
        client.subscribe("motionDetector/command")
    else:
        print(f"Échec de connexion au broker motionDetector, code : {rc}")

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
        while True:
            if arduino.in_waiting:
               # line = arduino.readline().decode().strip()
                line = arduino.readline().decode(errors='ignore').strip()
                if ":MOTION_DETECTED" in line:
                    sensor_id = line.split(":")[0]
                    if motion_detector_states.get(sensor_id) == "ON":
                        send_motion_detected(client, sensor_id)
            time.sleep(0.1)
    except KeyboardInterrupt:
                print("Arrêt du serveur.")
                client.loop_stop()

if __name__ == "__main__":
    main()
