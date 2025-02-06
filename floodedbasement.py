import RPi.GPIO as GPIO
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import smtplib
import os
from datetime import datetime, time
import time as sleep_time

# Load environment variables
load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
SEND_ADDRESS = os.getenv("SEND_ADDRESS")

# Define GPIO pin mappings for sensors
SENSOR_PINS = {
    "Area 1": 17,
    "Area 2": 27,
    "Area 3": 22,
    "Area 4": 23,
    "Area 5": 24,
}

# Function to send email
def send_email(to_email, subject, message):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
            print(f"Email sent: {subject}")
    except Exception as e:
        print(f"Error sending email: {e}")

sensor_states = {pin: False for pin in SENSOR_PINS.values()}

# Function to monitor sensors
def monitor_sensors():
    global sensor_states
    for area, pin in SENSOR_PINS.items():
        current_state = GPIO.input(pin)

        if current_state and not sensor_states[pin]:  # Sensor turns ON
            subject = f"Alert: Sensor Triggered in {area}"
            message = f"A sensor was triggered in {area} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}."
            send_email(SEND_ADDRESS, subject, message)
            sleep_time.sleep(1)  # Avoid multiple emails for the same trigger
    sensor_states[pin] = current_state

heartbeat_sent = False

# Function to send heartbeat email
def send_heartbeat():
    global heartbeat_sent
    current_time = datetime.now()
    if current_time.time() <= time(12,0) and heartbeat_sent == True or current_time.time() > time(12,1) and hearbeat_sent == False:
        heartbeat_sent = False

    if current_time.time() >= time(12, 0) and current_time.time() < time(12, 1) and hearbeat_sent == False:
        subject = "Daily Heartbeat Status"
        message = f"Heartbeat email sent at {current_time.strftime('%Y-%m-%d %H:%M:%S')}."
        print("Trying to send")
        send_email(SEND_ADDRESS, subject, message)
        hearbeat_sent = True

status = "Not Connected"

# Function for startup email
def startup():
    global status
    current_time = datetime.now()
    try:
        response = request.get("https://www.google.com")
        print (response.status_code)
        status = "Connected"
    except:
        status ="Not Connected"

    if status =="Connected":
        subject = "Hello World!"
        message = f"I am alive at {current_time.strftime('%Y-%m-%d %H:%M%S')}."
        send_email(SEND_ADDRESS, subject, message)

    
# Main loop
try:
    print("Monitoring sensors. Press Ctrl+C to exit.")
    startup()
    while True and status == "Connected":
        monitor_sensors()
        send_heartbeat()
        sleep_time.sleep(1)  # Avoid excessive CPU usage
except KeyboardInterrupt:
    print("Exiting...")
finally:
    GPIO.cleanup()
