import paho.mqtt.client as mqtt
import json

# Dictionnaire pour l'état du contrôle de l'air (initialisé à "OFF")
air_control_states = {
    "1": "OFF",
    "2": "OFF",
    "3": "OFF",
    "4": "OFF"
}
# Dictionnaire pour stocker la température des pièces
air_control_temps = {
    "1": 22.0,  # Valeur par défaut
    "2": 22.0,
    "3": 22.0,
    "4": 22.0
}

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connecté au broker MQTT air_control")
        client.subscribe("airControl/command")
    else:
        print(f"Échec de connexion au broker air_control, code : {rc}")

def on_message(client, userdata, msg):
    global air_control_states
    print(f"Message reçu sur {msg.topic}: {msg.payload.decode()}")

    try:
        command = json.loads(msg.payload.decode())
        air_id = command.get("id")
        state = command.get("etat")
        temp = command.get("temperature")

        if air_id in air_control_states and state in ["ON", "OFF"]:
            air_control_states[air_id] = state
            print(f"Contrôle de l'air {air_id} changé à l'état : {air_control_states[air_id]}")
            client.publish("airControl/status", json.dumps({"id": air_id, "etat": air_control_states[air_id]}))
         # Modifier la température UNIQUEMENT si l'état est "ON"
            if temp is not None and air_control_states.get(air_id) == "ON":
                    air_control_temps[air_id] = temp
                    print(f"Température de la pièce {air_id} réglée à : {temp}°C")
        else:
            print("Commande invalide : état inconnu ou ID invalide")
    except Exception as e:
        print(f"Erreur lors du traitement de la commande : {e}")

def main():
    client = mqtt.Client("airControl-server")
    client.on_connect = on_connect
    client.on_message = on_message

    broker = "broker.hivemq.com"
    port = 1883
    client.connect(broker, port, 60)

    client.loop_forever()

if __name__ == "__main__":
    main()
