import paho.mqtt.client as mqtt
import json

BROKER = "broker.emqx.io"
PORT = 1883

# Listen to the simplified topic
TOPIC = "secretcompany/pods/updates"
CLIENT_ID = "secretcompany-subscriber"

# This function runs every time a message comes in
def on_message(client, userdata, msg):
    try:
        # Decode the raw bytes into a string, then parse the JSON
        raw_message = msg.payload.decode()
        pod_data = json.loads(raw_message)
        
        # Print a nice summary of what the pod sent
        print("")
        print("=== Pod Status Update ===")
        print("Status:           " + str(pod_data["status"]))
        print("Current Terminal: " + str(pod_data["current_terminal"]))
        print("Next Terminal:    " + str(pod_data["next_terminal"]))
        print("ETA:              " + str(pod_data["eta_minutes"]) + " minutes")
        print("Occupancy:        " + str(pod_data["occupancy"]) + " / " + str(pod_data["max_capacity"]) + " passengers")
        print("=========================")

    except Exception as e:
        print("Could not read message: " + str(e))


# Set up the MQTT client
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=CLIENT_ID)

# Tell the client which function to call when a message arrives
client.on_message = on_message

# Connect to the broker
print("Connecting to broker " + BROKER + "...")
client.connect(BROKER, PORT, 60)

# Subscribe to the topic so we start receiving messages
client.subscribe(TOPIC)
print("Listening on topic: " + TOPIC)
print("Waiting for updates... (Press Ctrl+C to quit)")
print("")

# Keep the script running and listening for messages
try:
    client.loop_forever()

except KeyboardInterrupt:
    client.disconnect()
    print("Disconnected from broker.")
