
import krpc
import time

# Connexion au serveur kRPC
conn = krpc.connect(name='MFCD V0.4', address = "192.168.1.4", rpc_port=50000, stream_port=50001)

# Get the active vessel
vessel = conn.space_center.active_vessel

# Set up a stream to get the current MET (Mission Elapsed Time)
met_stream = conn.add_stream(getattr, conn.space_center, 'ut')

# Main loop
try:
    while True:
        # Get the current time
        current_time = met_stream()

        # Display the time and fuel levels
        

        amount = []
        for resource in vessel.resources.names:
            amount.append((vessel.resources.amount(resource)/vessel.resources.max(resource))*100)

        print("\033c")
        print(str(amount))

        # Wait for 1/25th of a second (0.04 seconds) before the next iteration
        #time.sleep(0.04)

except KeyboardInterrupt:
    # Close the connection when the script is interrupted (e.g., by pressing Ctrl+C)
    conn.close()

