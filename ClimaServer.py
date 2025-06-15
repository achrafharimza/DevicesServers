import paho.mqtt.client as mqtt
import json

# Dictionnaire pour l'état des températures (initialisé à une valeur par défaut)
climate_temperature = {
    "1": 22.0,  # Température par défaut en °C
    "2": 22.0,
    "3": 22.0,
    "4": 22.0
}

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connecté au broker MQTT")
        client.subscribe("clima/command")  # Topic pour recevoir des commandes
    else:
        print(f"Échec de connexion au broker clima, code : {rc}")

def on_message(client, userdata, msg):
    global climate_temperature
    print(f"Message reçu sur {msg.topic}: {msg.payload.decode()}")

    try:
        command = json.loads(msg.payload.decode())
        clima_id = command.get("id")
        new_temperature = command.get("temperature")

        if clima_id in climate_temperature and isinstance(new_temperature, (int, float)):
            climate_temperature[clima_id] = new_temperature
            print(f"Climatisation {clima_id} réglée à la température : {climate_temperature[clima_id]}°C")
            # Ici, vous pouvez envoyer un message ou notifier l'état de la température si nécessaire
            # client.publish("clim/status", json.dumps({"id": clim_id, "temperature": climate_temperature[clim_id]}))
        else:
            print("Commande invalide : température ou ID invalide")
    except Exception as e:
        print(f"Erreur lors du traitement de la commande : {e}")

def main():
    client = mqtt.Client("clima-server")
    client.on_connect = on_connect
    client.on_message = on_message

    broker = "broker.hivemq.com"
    port = 1883
    client.connect(broker, port, 60)

    client.loop_forever()

if __name__ == "__main__":
    main()
