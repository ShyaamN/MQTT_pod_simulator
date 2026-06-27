import time
import json
import random
from publisher import MQTTPublisher

# We have 3 terminals the pod loops around
terminals = ["T1", "T2", "T3"]

topic = "secretcompany/pods/updates"

# Set up the publisher to send updates to the broker
publisher = MQTTPublisher(client_id="secretcompany-sim")

# Pod can hold up to 12 people, starting empty
max_capacity = 12
occupancy = 0

# Start at a random terminal index (0, 1, or 2)
current_terminal_idx = random.randint(0, len(terminals) - 1)
next_terminal_idx = (current_terminal_idx + 1) % len(terminals)

status = "Arrived"
eta_minutes = 0

print("Starting simulation...")

try:
    while True:

        # Pod reaches the station and handles passengers boarding/leaving
        if status == "Arrived":
            # Some random passengers get off
            deboarded = random.randint(0, occupancy)
            occupancy = occupancy - deboarded

            # Figure out how many new people can board without going over capacity
            waiting = random.randint(0, 8)
            available_seats = max_capacity - occupancy
            
            if waiting > available_seats:
                boarded = available_seats
            else:
                boarded = waiting
            occupancy = occupancy + boarded

            print("\nArrived at " + terminals[current_terminal_idx])
            print("Passengers off: " + str(deboarded) + " | Passengers on: " + str(boarded))
            print("Occupancy: " + str(occupancy) + "/" + str(max_capacity))

            # Send current stats to MQTT subscriber
            pod_data = {
                "status": status,
                "current_terminal": terminals[current_terminal_idx],
                "next_terminal": terminals[next_terminal_idx],
                "eta_minutes": eta_minutes,
                "occupancy": occupancy,
                "max_capacity": max_capacity
            }
            publisher.publish(topic, json.dumps(pod_data))

            # Stay at the terminal for 4 seconds
            time.sleep(4)
            status = "Departing"

        # Brief warning phase before the pod actually departs
        elif status == "Departing":
            pod_data = {
                "status": status,
                "current_terminal": terminals[current_terminal_idx],
                "next_terminal": terminals[next_terminal_idx],
                "eta_minutes": eta_minutes,
                "occupancy": occupancy,
                "max_capacity": max_capacity
            }
            publisher.publish(topic, json.dumps(pod_data))
            print("Departing from " + terminals[current_terminal_idx])

            # Wait 2 seconds for departure sequence
            time.sleep(2)
            status = "In Transit"
            eta_minutes = random.randint(2, 4)

        # Travelling phase: decrement ETA until the pod arrives
        elif status == "In Transit":
            pod_data = {
                "status": status,
                "current_terminal": terminals[current_terminal_idx],
                "next_terminal": terminals[next_terminal_idx],
                "eta_minutes": eta_minutes,
                "occupancy": occupancy,
                "max_capacity": max_capacity
            }
            publisher.publish(topic, json.dumps(pod_data))
            print("In Transit to " + terminals[next_terminal_idx] + " | ETA: " + str(eta_minutes) + " min")

            # Tick takes 2 seconds
            time.sleep(2)

            eta_minutes = eta_minutes - 1

            # Arrived at next destination
            if eta_minutes <= 0:
                current_terminal_idx = next_terminal_idx
                # Loop back to T1 if we reach the end of the terminals list
                next_terminal_idx = (current_terminal_idx + 1) % len(terminals)
                eta_minutes = 0
                status = "Arrived"

except KeyboardInterrupt:
    print("\nSimulation stopped.")

finally:
    # Cleanup connection on exit
    publisher.disconnect()
    print("Disconnected from broker.")
