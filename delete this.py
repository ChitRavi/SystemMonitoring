import psutil
import time
import threading

monitoring_sessions = []

def monitor_system():
    while True:
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_info = psutil.virtual_memory()
        disk_info = psutil.disk_usage('/')

        print(f"CPU Usage: {cpu_usage}%")
        print(f"Memory Usage: {memory_info.percent}% (Used: {memory_info.used / (1024 ** 2):.2f} MB, Total: {memory_info.total / (1024 ** 2):.2f} MB)")
        print(f"Disk Usage: {disk_info.percent}% (Used: {disk_info.used / (1024 ** 3):.2f} GB, Total: {disk_info.total / (1024 ** 3):.2f} GB)")
        print("-" * 50)
        time.sleep(1)

def start_monitoring():
    session_thread = threading.Thread(target=monitor_system)
    session_thread.daemon = True  # This allows the program to exit even if this thread is running
    session_thread.start()
    monitoring_sessions.append(session_thread)

def list_active_monitoring():
    if not monitoring_sessions:
        print("No active monitoring sessions.")
    else:
        print(f"Active monitoring sessions: {len(monitoring_sessions)}")

def main():
    while True:
        print("1. Start Monitoring")
        print("2. List Active Monitoring")
        print("3. Exit")
        choice = input("Choose an option: ")

        if choice == '1':
            start_monitoring()
            print("Monitoring started...")
        elif choice == '2':
            list_active_monitoring()
        elif choice == '3':
            print("Exiting program.")
            break
        else:
            print("Invalid option, please try again.")

if __name__ == "__main__":
    main()
