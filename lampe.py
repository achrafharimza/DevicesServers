import paho.mqtt.client as mqtt
import json

# Dictionnaire pour l'état des lampes (initialisé à "OFF")
lamp_states = {
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
        client.subscribe("lampe/command")
    else:
        print(f"Échec de connexion au broker, code : {rc}")

# Callback lorsque le client reçoit un message
def on_message(client, userdata, msg):
    global lamp_states
    print(f"Message reçu sur {msg.topic}: {msg.payload.decode()}")

    # Traiter le message reçu
    try:
        command = json.loads(msg.payload.decode())
        lamp_id = command.get("id")
        state = command.get("etat")

        # Simuler le contrôle de la lampe
        if lamp_id in lamp_states and state in ["ON", "OFF"]:
            lamp_states[lamp_id] = state
            print(f"Lampe {lamp_id} changée à l'état : {lamp_states[lamp_id]}")

            # Publier le nouvel état sur le topic `lampe/status`
            client.publish("lampe/status", json.dumps({"id": lamp_id, "etat": lamp_states[lamp_id]}))
        else:
            print("Commande invalide : état inconnu ou ID invalide")
    except Exception as e:
        print(f"Erreur lors du traitement de la commande : {e}")

# Configurer le client MQTT
def main():
    client = mqtt.Client("lamp-server")
    client.on_connect = on_connect
    client.on_message = on_message

    # Connexion au broker MQTT
    broker = "broker.hivemq.com"  # Adresse du broker
    port = 1883  # Port MQTT par défaut
    client.connect(broker, port, 60)

    # Boucle pour écouter les messages en continu
    client.loop_forever()

if __name__ == "__main__":
    main()
