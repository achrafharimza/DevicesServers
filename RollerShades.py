import paho.mqtt.client as mqtt
import json

# Dictionnaire pour l'état des volets roulants (initialisé à "OFF")
roller_shades_states = {
    "1": "OFF",
    "2": "OFF",
    "3": "OFF",
    "4": "OFF"
}

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connecté au broker MQTT")
        client.subscribe("rollerShades/command")
    else:
        print(f"Échec de connexion au broker, code : {rc}")

def on_message(client, userdata, msg):
    global roller_shades_states
    print(f"Message reçu sur {msg.topic}: {msg.payload.decode()}")

    try:
        command = json.loads(msg.payload.decode())
        shade_id = command.get("id")
        state = command.get("etat")

        if shade_id in roller_shades_states and state in ["ON", "OFF"]:
            roller_shades_states[shade_id] = state
            print(f"Volet roulant {shade_id} changé à l'état : {roller_shades_states[shade_id]}")
            client.publish("rollerShades/status", json.dumps({"id": shade_id, "etat": roller_shades_states[shade_id]}))
        else:
            print("Commande invalide : état inconnu ou ID invalide")
    except Exception as e:
        print(f"Erreur lors du traitement de la commande : {e}")

def main():
    client = mqtt.Client("rollerShades-server")
    client.on_connect = on_connect
    client.on_message = on_message

    broker = "broker.hivemq.com"
    port = 1883
    client.connect(broker, port, 60)

    client.loop_forever()

if __name__ == "__main__":
    main()
