# Emergency Mode — Voice-Activated Emergency Assistance

## About the Project

Emergency Mode is a Python-based application designed to provide quick assistance during emergency situations. It listens for a predefined voice trigger word and responds by capturing a webcam snapshot, retrieving the device's location when available, and displaying an emergency notification.

When the trigger word is detected twice, the application initiates a WhatsApp emergency alert.

## Features

* **Voice Activation:** Listens for the configured trigger word, `help`.
* **Webcam Snapshot:** Captures an image and overlays the timestamp and available location information.
* **Location Retrieval:** Attempts to retrieve device location using Windows location services.
* **Emergency Notification:** Displays a popup with the emergency status and captured snapshot.
* **WhatsApp Alert:** Initiates an emergency message containing the timestamp, location information, and Google Maps link.
* **Event Logging:** Records application events and errors in a log file.

## Technologies Used

* Python
* SpeechRecognition
* PyAudio
* OpenCV
* Requests
* PyWhatKit
* PyAutoGUI
* Pillow
* Tkinter
* Windows PowerShell location services

## Project Structure

```text
Emergency-Mode/
├── main.py
├── location.py
├── requirements.txt
└── README.md
```

* `main.py` — Main application logic, voice recognition, webcam capture, notifications, and WhatsApp alert handling.
* `location.py` — Contains the function for retrieving location through Windows device location services.
* `requirements.txt` — Lists the Python dependencies required by the application.
* `README.md` — Project documentation and setup instructions.

## Requirements

* Windows operating system
* Python 3.12 recommended, subject to dependency compatibility
* A working microphone
* A webcam
* Internet connectivity for speech recognition and WhatsApp Web
* A logged-in WhatsApp Web session

## Installation

1. Clone or download this repository.

   ```bash
   git clone https://github.com/Rashmirisha/Emergency-Mode.git
   cd Emergency-Mode
   ```

2. Install the required dependencies.

   ```bash
   python -m pip install -r requirements.txt
   ```

3. If PyAudio installation fails on Windows, install a compatible PyAudio wheel for your Python version and system architecture.

4. Open `main.py` and configure the emergency contact number using the international country code and phone number, without spaces or a leading plus sign.

5. Check the microphone and webcam settings before running the application.

## How to Run

Execute the main application:

```bash
python main.py
```

The application calibrates the microphone and begins listening for the configured trigger word.

* Say **"help" once** to trigger a snapshot and location retrieval.
* Say **"help help"** to initiate the full emergency workflow, including the WhatsApp alert.

Press `Ctrl+C` in the terminal to stop the application.

## Output

The application creates the following local outputs:

* `emergency_snapshots/` — Stores captured webcam images.
* `emergency_log.txt` — Stores timestamped application events.

These files are generated locally while the application runs.

## Limitations

* Location retrieval depends on Windows location services and device availability.
* Voice recognition depends on microphone quality, background noise, and internet connectivity.
* WhatsApp alerts depend on WhatsApp Web, an active login session, and successful message delivery.
* The application has been developed for a Windows environment and may require modifications for other operating systems.

## Privacy and Safety

* Configure your own emergency contact before running the application.
* Do not publish personal phone numbers, captured images, logs, or other sensitive information in the public repository.
* Webcam access and location retrieval should be used with appropriate consent.
* This project is a prototype and should not be relied upon as the sole method of requesting emergency assistance.

## Future Improvements

* Add a more robust location fallback mechanism.
* Improve alert delivery confirmation and error handling.
* Add configurable emergency contacts and user settings.
* Improve cross-platform compatibility and testing.

## Author

**Rashmi Risha**

GitHub: https://github.com/Rashmirisha
