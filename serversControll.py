import paho.mqtt.client as mqtt
import json
import serial
import time
from datetime import datetime

# Connexion série à l'Arduino (une seule fois)
arduino = serial.Serial('COM13', 9600, timeout=1)
time.sleep(2)

# États initiaux des lampes et des capteurs de mouvement
lamp_states = {str(i): "OFF" for i in range(1, 5)}
motion_detector_states = {str(i): "OFF" for i in range(1, 5)}
roller_shades_states = {str(i): "OFF" for i in range(1, 5)}
air_control_states = {str(i): "OFF" for i in range(1, 5)}

# --- FONCTIONS MQTT POUR LES LAMPES ---
def send_to_arduino_lamp(lamp_id, state):
    if state in ["ON", "OFF"] and lamp_id in lamp_states:
        #command = f"{lamp_id}:{state}\n"
        command = f"LED{lamp_id}:{state}\n"
        arduino.write(command.encode())
        print(f"[LAMPE] Commande envoyée à Arduino : {command.strip()}")

# --- FONCTIONS MQTT POUR LES ROLLERS ---
def send_to_arduino_Roller(roller_id, state):
    if state in ["ON", "OFF"] and roller_id in roller_shades_states:
        command = f"ROLLER{roller_id}:{state}\n"
        arduino.write(command.encode())
        print(f"[roller_shades] Commande envoyée à Arduino : {command.strip()}")

# --- FONCTIONS MQTT POUR LES AIRS ---
def send_to_arduino_AIR(AIR_id, state):
    if state in ["ON", "OFF"] and AIR_id in air_control_states:
        command = f"AIR{AIR_id}:{state}\n"
        arduino.write(command.encode())
        print(f"[AIR_control] Commande envoyée à Arduino : {command.strip()}")

# --- FONCTIONS MQTT POUR LED motion_detected ---
def send_to_arduino_MOTION_STATUS(led_id, state):
    if state in ["ON", "OFF"] and led_id in motion_detector_states:
        #command = f"{lamp_id}:{state}\n"
        command = f"MOTION{led_id}:{state}\n"
        arduino.write(command.encode())
        print(f"[MOTION_STATUs_LED] Commande envoyée à Arduino : {command.strip()}")

# --- FONCTIONS MQTT POUR LES CAPTEURS ---
def send_motion_detected(client, sensor_id):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    payload = json.dumps({
        "sensor_id": sensor_id,
        "status": "MOUVEMENT_DETECTE",
        "timestamp": timestamp
    })
    client.publish("motionDetector/motion", payload)
    print(f"[MOTION] Notification envoyée : {payload}")

# --- CALLBACKS MQTT COMMUNES ---
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connecté au broker MQTT")
        client.subscribe("lampe/command")
        client.subscribe("motionDetector/command")
        client.subscribe("rollerShades/command")
        client.subscribe("airControl/command")
    else:
        print(f"Échec de connexion au broker, code : {rc}")

def on_message(client, userdata, msg):
    topic = msg.topic
    message = msg.payload.decode()
    print(f"Message reçu sur {topic}: {message}")

    try:
        command = json.loads(message)
        device_id = str(command.get("id"))
        state = command.get("etat")

        if topic == "lampe/command":
            if device_id in lamp_states and state in ["ON", "OFF"]:
                lamp_states[device_id] = state
                send_to_arduino_lamp(device_id, state) #     arduino.write(b"BUZZ:500\n")
                client.publish("lampe/status", json.dumps({"id": device_id, "etat": state}))
            else:
                print("Commande lampe invalide")

        elif topic == "motionDetector/command":
            if device_id in motion_detector_states and state in ["ON", "OFF"]:
                motion_detector_states[device_id] = state
                send_to_arduino_MOTION_STATUS(device_id, state)
                client.publish("motionDetector/status", json.dumps({"id": device_id, "etat": state}))
            else:
                print("Commande capteur invalide")

        elif topic == "rollerShades/command":
            if device_id in roller_shades_states and state in ["ON", "OFF"]:
                roller_shades_states[device_id] = state
                send_to_arduino_Roller(device_id, state)
                print(f"Volet roulant {device_id} changé à l'état : {state}")
                client.publish("rollerShades/status", json.dumps({"id": device_id, "etat": state}))
            else:
                print("Commande volet roulant invalide")
        
        elif topic == "airControl/command":
            if device_id in air_control_states and state in ["ON", "OFF"]:
                air_control_states[device_id] = state
                send_to_arduino_AIR(device_id, state)
                print(f"airControl {device_id} changé à l'état : {state}")
                client.publish("airControl/status", json.dumps({"id": device_id, "etat": state}))
            else:
                print("Commande volet roulant invalide")

    except Exception as e:
        print(f"Erreur de traitement : {e}")

# --- FONCTION PRINCIPALE ---
def main():
    client = mqtt.Client("device-server")
    client.on_connect = on_connect
    client.on_message = on_message

    broker = "broker.hivemq.com"
    client.connect(broker, 1883, 60)
    client.loop_start()

    try:
        while True:
            if arduino.in_waiting:
                line = arduino.readline().decode(errors='ignore').strip()
                print(f"Message série reçu : {line}")

                if ":LED_BUTTON_PRESSED" in line:
                    lamp_id = line.split(":")[0]
                    if lamp_id in lamp_states:
                        current = lamp_states[lamp_id]
                        new_state = "OFF" if current == "ON" else "ON"
                        cmd = json.dumps({"id": lamp_id, "etat": new_state})
                        client.publish("lampe/command", cmd)
                
                elif ":MOTION_LED_BUTTON_PRESSED" in line:
                    led_id = line.split(":")[0]
                    if led_id in motion_detector_states:
                        current = motion_detector_states[led_id]
                        new_state = "OFF" if current == "ON" else "ON"
                        cmd = json.dumps({"id": led_id, "etat": new_state})
                        client.publish("motionDetector/command", cmd)
                
                elif ":ROLLER_BUTTON_PRESSED" in line:
                    roller_id = line.split(":")[0]
                    if roller_id in roller_shades_states:
                        current = roller_shades_states[roller_id]
                        new_state = "OFF" if current == "ON" else "ON"
                        cmd = json.dumps({"id": roller_id, "etat": new_state})
                        client.publish("rollerShades/command", cmd)
                
                elif ":AIR_BUTTON_PRESSED" in line:
                    air_id = line.split(":")[0]
                    if air_id in air_control_states:
                        current = air_control_states[air_id]
                        new_state = "OFF" if current == "ON" else "ON"
                        cmd = json.dumps({"id": air_id, "etat": new_state})
                        client.publish("airControl/command", cmd)

                elif ":MOTION_DETECTED" in line:
                    sensor_id = line.split(":")[0]
                    if motion_detector_states.get(sensor_id) == "ON":
                        send_motion_detected(client, sensor_id)
                
                elif line.startswith("TEMP:"):
                    try:
                        temp = float(line.split(":")[1])
                        payload = json.dumps({"temperature": temp})
                        client.publish("temperature/current", payload)
                        print(f"Température envoyée MQTT : {payload}")
                    except ValueError:
                        print("Erreur conversion température")
                    
                elif "Smoke detected!" in line:
                # Extraire la valeur sensorValue si besoin
                 try:
                    # Exemple: "Sensor Value: 350 | Smoke detected!"
                    parts = line.split("|")[0].strip()  # "Sensor Value: 350"
                    sensor_val = int(parts.split(":")[1].strip())
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    payload = json.dumps({"sensor_value": sensor_val, "smoke": True,"timestamp":timestamp})
                    client.publish("gas/smoke", payload)
                    print(f"Alerte fumée envoyée MQTT : {payload}")
                 except Exception as e:
                    print(f"Erreur parsing fumée : {e}")

            time.sleep(0.1)

    except KeyboardInterrupt:
        client.loop_stop()
        print("Arrêt du serveur unifié.")

if __name__ == "__main__":
    main()
