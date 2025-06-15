import paho.mqtt.client as mqtt
import json
import serial
import time

# Connexion série à l'Arduino (adapter 'COM13' selon ton port)
arduino = serial.Serial('COM13', 9600, timeout=1)
time.sleep(2)  # Laisser le temps à l'Arduino de démarrer

# Dictionnaire pour suivre l’état de chaque lampe
lamp_states = {
    "1": "OFF",
    "2": "OFF",
    "3": "OFF",
    "4": "OFF"
}

# Fonction pour envoyer une commande ON/OFF pour une LED spécifique à l’Arduino
def send_to_arduino_lamp(lamp_id, state):
    if state in ["ON", "OFF"] and lamp_id in lamp_states:
        command = f"{lamp_id}:{state}\n"
        arduino.write(command.encode())
        print(f"Commande envoyée à Arduino : {command.strip()}")

# Callback appelée quand le client MQTT est connecté
def on_connect_lamp(client, userdata, flags, rc):
    if rc == 0:
        print("Connecté au broker MQTT lamp")
        # Abonnement au topic où on recevra les commandes ON/OFF
        client.subscribe("lampe/command")
    else:
        print(f"Échec de connexion au broker lamp, code : {rc}")

# Callback appelée à chaque message MQTT reçu
def on_message_lamp(client, userdata, msg):
    global lamp_states
    print(f"Message reçu sur {msg.topic}: {msg.payload.decode()}")
    try:
        # Décoder le message JSON reçu
        command = json.loads(msg.payload.decode())
        lamp_id = command.get("id")       # Ex: "2"
        state = command.get("etat")       # Ex: "ON"

        # Vérifier que la commande est bien formée
        if lamp_id in lamp_states and state in ["ON", "OFF"]:
            # Mettre à jour l'état local de la lampe
            lamp_states[lamp_id] = state
            # Envoyer la commande à l’Arduino (ex: "2:ON\n")
            send_to_arduino_lamp(lamp_id, state)
            # Publier le nouvel état sur le topic "lampe/status"
            client.publish("lampe/status", json.dumps({"id": lamp_id, "etat": lamp_states[lamp_id]}))
        else:
            print("Commande invalide")
    except Exception as e:
        print(f"Erreur de traitement : {e}")

# Fonction principale
def main():
    client = mqtt.Client("lamp-server")
    client.on_connect = on_connect_lamp
    client.on_message = on_message_lamp

    # Connexion au broker public MQTT
    broker = "broker.hivemq.com"
    client.connect(broker, 1883, 60)
    client.loop_start()  # Démarrer l'écoute en arrière-plan

    try:
        # Boucle infinie pour lire les événements envoyés par l’Arduino
        while True:
            if arduino.in_waiting:
                #line = arduino.readline().decode().strip()  # Lire ligne série
                line = arduino.readline().decode(errors='ignore').strip()
                print(f"Message série reçu : {line}")

                # Si on détecte un message de type "1:BUTTON_PRESSED"
                if ":" in line and "BUTTON_PRESSED" in line:
                    lamp_id, _ = line.split(":")  # Extrait l’ID du bouton
                    current_state = lamp_states.get(lamp_id, "OFF")
                    # Inverser l'état de la lampe correspondante
                    new_state = "OFF" if current_state == "ON" else "ON"
                    # Créer et publier la commande sur "lampe/command"
                    lamp_command = json.dumps({"id": lamp_id, "etat": new_state})
                    client.publish("lampe/command", lamp_command)
            time.sleep(0.1)  # Petite pause pour ne pas surcharger la boucle
    except KeyboardInterrupt:
        client.loop_stop()
        print("Arrêt du serveur.")

# Exécuter la fonction principale
if __name__ == "__main__":
    main()
