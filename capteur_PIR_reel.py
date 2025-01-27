import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import time
import json

# Configuration du GPIO pour le capteur PIR
PIR_PIN = 17  # Assurez-vous de connecter le capteur PIR au bon pin GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_PIN, GPIO.IN)  # Configurer le capteur PIR en mode entrée

# Variables pour le statut du mouvement
motion_detected = False

# Callback lorsque le client se connecte au broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connecté au broker MQTT")
    else:
        print(f"Échec de connexion au broker, code : {rc}")

# Fonction pour envoyer les notifications de mouvement
def send_motion_status(client):
    global motion_detected
    motion_status = "MOUVEMENT_DETECTE" if motion_detected else "AUCUN_MOUVEMENT"
    
    # Publier l'état du mouvement sur le topic MQTT
    payload = json.dumps({"status": motion_status})
    client.publish("lampe/motion/status", payload)
    print(f"Statut du mouvement envoyé: {motion_status}")

# Fonction pour détecter un mouvement
def motion_callback(channel):
    global motion_detected
    if GPIO.input(PIR_PIN):  # Mouvement détecté
        print("Mouvement détecté !")
        motion_detected = True
        send_motion_status(client)
    else:  # Pas de mouvement
        print("Aucun mouvement")
        motion_detected = False
        send_motion_status(client)

# Configuration du client MQTT
def main():
    # Initialisation du client MQTT
    client = mqtt.Client("motion-detector-server")
    client.on_connect = on_connect

    # Connexion au broker MQTT
    broker = "broker.hivemq.com"  # Adresse du broker
    port = 1883  # Port MQTT par défaut
    client.connect(broker, port, 60)

    # S'abonner au topic (facultatif ici)
    client.loop_start()

    # Ajouter un détecteur de mouvement pour appeler motion_callback sur changement
    GPIO.add_event_detect(PIR_PIN, GPIO.BOTH, bouncetime=300)
    GPIO.add_event_callback(PIR_PIN, motion_callback)

    try:
        while True:
            time.sleep(1)  # Attente pour ne pas surcharger le processeur
    except KeyboardInterrupt:
        print("Arrêt du programme.")
        GPIO.cleanup()  # Nettoyer les ressources GPIO

if __name__ == "__main__":
    main()
