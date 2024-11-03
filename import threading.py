import threading
import time

# Flag to control the loop
running = True

def wait_for_enter():
    global running
    input("Press Enter to stop the loop...")
    running = False

# Start the thread that waits for user input
threading.Thread(target=wait_for_enter, daemon=True).start()

# Loop that continues until 'running' is False
while running:
    print("Loop is running...")
    time.sleep(1)  # Simulate some work

print("Loop has been stopped.")

