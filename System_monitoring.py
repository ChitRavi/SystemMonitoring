import time
import psutil
import threading #To run multiple functions simultaneously
import json #To store alarm details in a file &reload it when we run the program
import os 
from sendgrid import SendGridAPIClient 
from sendgrid.helpers.mail import Mail 
#Constructor
class MonitoringApp:
    def __init__(self, alarm_file="alarms.json"): #To access and manipulate variables
        self.monitoring_data = {"cpu_usage": None, "memory_usage": None, "disk_usage": None}
        self.alarm_levels = {"cpu": [], "memory": [], "disk": []}
        self.monitoring_active = False
        self.alarm_file = alarm_file
        self.sendgrid_api_key = "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"  # Replace with your actual SendGrid API key
        self.alert_email = "chitra.balasubramanian@chasacademy.se"  # Replace with the recipient's email address
        self.load_alarms()
# loads the pre saved alarm from json file
    def load_alarms(self):
        if os.path.exists(self.alarm_file):
            print("Loading previously configured alarms...")
            with open(self.alarm_file, "r") as file:
                self.alarm_levels = json.load(file)
        else:
            print("No previous alarms found.")
# saves the alarms in the json file.
    def save_alarms(self):
        with open(self.alarm_file, "w") as file:
            json.dump(self.alarm_levels, file)
        print("Alarms saved to disk.")
# the main monitoring function
    def monitor_system(self):
        self.monitoring_active = True
        while self.monitoring_active:
            self.monitoring_data["cpu_usage"] = psutil.cpu_percent(interval=1)
            self.monitoring_data["memory_usage"] = psutil.virtual_memory().percent
            self.monitoring_data["disk_usage"] = psutil.disk_usage('/').percent

            # Check if any alarms are triggered
            self.check_alarms()
            time.sleep(5)  
# to start the monitoring of disc memory and cpu usage. 
    def start_monitoring(self):
        if not self.monitoring_active:
            print("System monitoring has been started...")
            monitoring_thread = threading.Thread(target=self.monitor_system)
            monitoring_thread.daemon = True
            monitoring_thread.start()
        else:
            print("Monitoring is already active.")
# checks the threshold and displays the warning
    def check_alarms(self):
        # Check if any alarms are triggered and send an email notification if they are
        for alarm_type, thresholds in self.alarm_levels.items():
            current_usage = self.monitoring_data.get(f"{alarm_type}_usage")
            if current_usage is not None:
                for threshold in thresholds:
                    if current_usage > threshold:
                        message = f"**WARNING, ALARM ENABLED, {alarm_type.upper()} USAGE EXCEEDS {threshold}%**"
                        print(message)
                        self.send_email_notification(alarm_type.upper(), threshold, current_usage)
# to send email when threshold exceeds
    def send_email_notification(self, alarm_type, threshold, current_usage):
        # Use SendGrid to send an email alert
        subject = f"Alert: {alarm_type} Usage Exceeds {threshold}%"
        content = (
            f"An alarm has been triggered for {alarm_type} usage.\n\n"
            f"Current {alarm_type} Usage: {current_usage}%\n"
            f"Threshold: {threshold}%\n\n"
            f"Please take immediate action if necessary."
        )
        
        message = Mail(
            from_email="chitra.inspires@gmail.com",  # Replace with your verified sender email
            to_emails=self.alert_email,
            subject=subject,
            plain_text_content=content
        )
        
        try:
            sg = SendGridAPIClient(self.sendgrid_api_key)
            response = sg.send(message)
            if response.status_code == 202:
                print(f"Alert email sent for {alarm_type} usage exceeding {threshold}%.")
            else:
                print(f"Failed to send email alert. Status code: {response.status_code}")
        except Exception as e:
            print(f"Error sending email: {e}")
# displays the result of cpu dis and memory usage.

    def list_active_monitoring(self):
        # Event to control the loop
        stop_event = threading.Event()

        def wait_for_enter():
            input("Press Enter to stop...")
            stop_event.set()  # Signal to stop the loop

        # Start the thread that waits for user input
        threading.Thread(target=wait_for_enter, daemon=True).start()

        while self.monitoring_active and not stop_event.is_set():
            print("\n--- Active Monitoring Data ---")
            print(f"CPU Usage: {self.monitoring_data['cpu_usage']}%")
            print(f"Memory Usage: {self.monitoring_data['memory_usage']}%")
            print(f"Disk Usage: {self.monitoring_data['disk_usage']}%")
            time.sleep(5)
        else :
            if stop_event.is_set():
                 input("\nPress any key to return to the main menu...")
            else :
                print("No active monitoring session. Please start monitoring first.")
               

# Displays different alarms options. the created alarms gets saved in json file
    def create_alarms(self):
        while True:
            print("\n--- Configure Alarms ---\n1. CPU Usage Alarm\n 2. Memory Usage Alarm \n3. Disk Usage Alarm \n4. Back to Main Menu")
            
            choice = input("Please select an option (1-4): ")
            if choice == '1':
                self.set_alarm("cpu")
            elif choice == '2':
                self.set_alarm("memory")
            elif choice == '3':
                self.set_alarm("disk")
            elif choice == '4':
                break
            else:
                print("Invalid option, please try again.")
# sets alarm
    def set_alarm(self, alarm_type):
        try:
            level = int(input("Set level for alarm between 1-100: "))
            if 1 <= level <= 100:
                self.alarm_levels[alarm_type].append(level)
                self.alarm_levels[alarm_type].sort()
                self.save_alarms()
                print(f"Alarm for {alarm_type.capitalize()} usage set to {level}%.")
            else:
                print("Error: Please enter a number between 1 and 100.")
        except ValueError:
            print("Error: Please enter a valid number between 1 and 100.")
# List all the existing alrm. This also list alarm from the json file 
    def list_alarms(self):
        print("\n--- Configured Alarms ---")
        alarm_list = []
        for alarm_type in sorted(self.alarm_levels.keys()):
            for level in sorted(self.alarm_levels[alarm_type]):
                alarm_list.append(f"{alarm_type.capitalize()} Alarm {level}%")
        
        if alarm_list:
            for index, alarm in enumerate(alarm_list, start=1):
                print(f"{index}. {alarm}")
        else:
            print("No alarms configured.")
        input("\nPress enter to return to the main menu...")
# to remove the alarm
    def remove_alarm(self):
        print("\n--- Remove Alarm ---")
        alarm_list = []
        
        for alarm_type in sorted(self.alarm_levels.keys()):
            for level in sorted(self.alarm_levels[alarm_type]):
                alarm_list.append(f"{alarm_type.capitalize()} Alarm {level}%")
        
        if not alarm_list:
            print("No alarms configured to remove.")
            input("\nPress enter to return to the main menu...")
            return

        print("Select a configured alarm to delete:")
        for index, alarm in enumerate(alarm_list, start=1):
            print(f"{index}. {alarm}")

        try:
            choice = int(input("Enter the number of the alarm to remove: "))
            if 1 <= choice <= len(alarm_list):
                alarm_to_remove = alarm_list[choice - 1]
                alarm_type, level = alarm_to_remove.split(" Alarm ")
                level = int(level[:-1])

                self.alarm_levels[alarm_type.lower()].remove(level)
                self.save_alarms()
                print(f"{alarm_to_remove} has been removed.")
            else:
                print("Invalid choice. No alarm removed.")
        except ValueError:
            print("Invalid input. Please enter a number.")

        input("\nPress enter to return to the main menu...")
# quit the application
    def exit_application(self):
        self.monitoring_active = False
        print("Exiting the application.")
        exit()
# Main menu that displays all the options to the user
    def main_menu(self):
        while True:
            print("\n--- Monitoring Application - Main Menu --- \n1. Start Monitoring\n2. List Active Monitoring\n3. Create Alarms\n4. Show Alarms\n5. Remove Alarm\n6. Exit Application")
        
            choice = input("Please select an option (1-6): ")
            if choice == '1':
                self.start_monitoring()
            elif choice == '2':
                self.list_active_monitoring()
            elif choice == '3':
                self.create_alarms()
            elif choice == '4':
                self.list_alarms()
            elif choice == '5':
                self.remove_alarm()
            elif choice == '6':
                self.exit_application()
            else:
                print("Invalid option, please try again.")
#  default code that gets executed first.
if __name__ == "__main__":
    
    app = MonitoringApp()
    app.main_menu()