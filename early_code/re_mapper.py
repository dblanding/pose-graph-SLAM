import asyncio
import aiomqtt
import json
import numpy as np
import pickle
import sys
import time
import os
from build_ogm import Build_OGM
import parameters
import service_ctrl as sc

# --- Saving the OGM instance ---
def save_ogm(ogm, filename="my_ogm.pkl"):
    """Serializes and saves an OGM instance to a binary file."""
    # Open file in write-binary mode ('wb')
    with open(filename, 'wb') as file:
        pickle.dump(ogm, file)
    print(f"ogm saved to {filename}")

# --- Loading the OGM instance ---
def load_ogm(filename="my_ogm.pkl"):
    """Loads and deserializes an OGM instance from a binary file."""
    if os.path.exists(filename):
        # Open file in read-binary mode ('rb')
        with open(filename, 'rb') as file:
            ogm = pickle.load(file)
        print(f"ogm loaded from {filename}")
        return ogm
    else:
        print(f"ogm File {filename} not found.")
        return None


class MQTTSubscriber:
    def __init__(self, broker, port, topics):
        self.broker = broker
        self.port = port
        self.topics = topics
        # Dictionary to store the latest message for each topic
        self.latest_messages = {topic: None for topic in topics}
        self.client = None

    async def connect_and_subscribe(self):
        """Connects to the broker and starts the subscription loop."""
        # Use a context manager for reliable connection/disconnection
        try:
            async with aiomqtt.Client(hostname=self.broker, port=self.port) as client:
                self.client = client
                # Subscribe to all topics in the list
                for topic in self.topics:
                    await client.subscribe(topic)
                    print(f"Subscribed to topic: {topic}")
                
                # Start the message listener
                await self.message_listener()
        except aiomqtt.MqttError as e:
            print(f"MQTT error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    async def message_listener(self):
        """Asynchronously listens for and processes incoming messages."""
        async for message in self.client.messages:
            topic = message.topic.value
            payload = message.payload.decode('utf-8')
            # Update the latest message in the dictionary
            self.latest_messages[topic] = payload
            if parameters.debug:
                print(f"Received on '{topic}' @ {time.monotonic()} sec.")

    def get_latest_messages(self):
        """Retrieves the latest messages stored in the dictionary."""
        return self.latest_messages


async def main(ogm):
    
    broker_address = "192.168.1.85"
    mqtt_topics = ["lidar/data", "odom/pose"]
    
    subscriber = MQTTSubscriber(broker_address, 1883, mqtt_topics)
    pose = None
    scan = None
    
    # Run the connection and subscription in an asyncio task
    # Note: This will run forever until stopped
    listener_task = asyncio.create_task(subscriber.connect_and_subscribe())

    # Restart the scanner and set the scan motor running, start the odometer
    print("Restarting the Scanner service")
    sc.restart_scanner()
    print("Starting the Scan Motor")
    sc.start_scan_mtr()
    print("Starting the Odometer")
    sc.start_odometer()
    await asyncio.sleep(7)  # The odometer has to do some initialization
    
    # Retrieve messages as they come in and update
    # Update the map once per second
    print("start driving")
    while True:
        await asyncio.sleep(1)
        current_messages = subscriber.get_latest_messages()
        for topic, message in current_messages.items():
            if topic == "lidar/data":
                if message:
                    scan = json.loads(message)
                    print(f"scan len: {len(scan)}")
            elif topic == "odom/pose":
                if message:
                    pose = json.loads(message)
                    print(f"pose: {pose}")

            # Update map
            if pose and scan:
                start_time = time.monotonic()
                ogm.update_map(pose, scan)
                end_time = time.monotonic()
                if parameters.debug:
                    elapsed = end_time - start_time
                    print(f"Execution time for update: {elapsed} sec.")

    # The listener_task is still running. In a real app (e.g., web server)
    # the main program would continue to run without blocking.
    # To keep the script running indefinitely to receive messages, you would
    # typically just await the listener task forever. ctrl-c to stop.
    await listener_task

if __name__ == "__main__":
    # Load OGM from file
    ogm = load_ogm()

    try:
        # Continue building map
        asyncio.run(main(ogm))
    except KeyboardInterrupt:
        print("Subscriber stopped manually.")
    finally:
        print("Stopping the Odometer")
        sc.stop_odometer()
        print("Stopping the Scan Motor")
        sc.stop_scan_mtr()
        # save the map
        np.save('my_map.npy', ogm.data)
        print("Map saved to my_map.npy")
        # save the ogm
        save_ogm(ogm)
