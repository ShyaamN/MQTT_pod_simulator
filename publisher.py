import paho.mqtt.client as mqtt
import time

# Broker settings
BROKER = "broker.emqx.io"
PORT = 1883

class MQTTPublisher:
    def __init__(self, client_id):
        # Create the MQTT client with the given ID
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id)
        
        # Connect to the broker
        self.client.connect(BROKER, PORT, 60)
        
        # Start the background thread that keeps the connection alive
        self.client.loop_start()
        
        # Small delay to make sure the connection is ready before we try to publish
        time.sleep(1)

    def publish(self, topic, payload):
        # Send the message to the broker on the given topic
        self.client.publish(topic, payload)

    def disconnect(self):
        # Stop the background thread and close the connection cleanly
        self.client.loop_stop()
        self.client.disconnect()
