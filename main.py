

# ============================================================
#   EMERGENCY MODE v5 (FIXED)
#   - Voice activated (say "help" once or twice)
#   - Webcam snapshot with timestamp + location overlay
#   - Sends WhatsApp message to emergency contact
#   - Runs in Python IDLE
# ============================================================
#
# INSTALL REQUIRED LIBRARIES (run once in terminal/cmd):
#   pip install SpeechRecognition pyaudio opencv-python requests pywhatkit geocoder pyautogui pillow
#
# WHATSAPP SETUP:
#   1. Open WhatsApp Web (web.whatsapp.com) in Chrome and stay logged in
#   2. Set EMERGENCY_CONTACT below (include country code, no + sign)
#      Example: "91xxxxxxxxxx" for India (+91 xxxxx xxxxx)
#
# FIXES IN v5:
#   - Location: replaced unreliable Windows GPS with geocoder (faster, always works)
#   - WhatsApp: added pyautogui.press('enter') so message actually sends instead of saving to draft
# ============================================================




from location import get_windows_gps
import cv2
import speech_recognition as sr
import threading
import time
import os
import winsound
import requests
import pywhatkit
import pyautogui
import geocoder
from datetime import datetime
from tkinter import Tk, Label
from PIL import Image, ImageTk

# ============================================================
#   CONFIGURE THESE SETTINGS
# ============================================================
CODE_WORD        = "help"           # Secret trigger word
CAMERA_INDEX     = 0                # 0 = default webcam
MIC_INDEX        = 1                # Your working mic index
SNAPSHOT_FOLDER  = "emergency_snapshots"
LOG_FILE         = "emergency_log.txt"

# WhatsApp contact (country code + number, no + or spaces)
EMERGENCY_CONTACT = "91 xxxxx xxxxx"  # <-- Replace with real number

# ============================================================
#   SETUP
# ============================================================
os.makedirs(SNAPSHOT_FOLDER, exist_ok=True)
stop_event = threading.Event()


# ============================================================
#   LOGGING
# ============================================================
def log_event(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {message}"
    print(entry)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(entry + "\n")


# ============================================================
#   ALERT BEEP
# ============================================================
def play_alert():
    try:
        for _ in range(3):
            winsound.Beep(1000, 300)
            time.sleep(0.1)
    except Exception:
        print("MEOW MEOW MEOW!")


# ============================================================
#   LOCATION - Uses geocoder (fast, reliable IP-based)
# ============================================================
def get_location():
    gps = get_windows_gps()

    if gps:
        lat, lon = gps
        address = f"GPS Location: {lat:.4f}, {lon:.4f}"
        return lat, lon, address

    return 0.0, 0.0, "Location unavailable"

def get_ip_location_fallback():
    """Fallback: ipinfo.io direct request."""
    try:
        response = requests.get("https://ipinfo.io/json", timeout=5)
        data = response.json()
        city    = data.get("city",    "Unknown")
        region  = data.get("region",  "Unknown")
        country = data.get("country", "Unknown")
        loc     = data.get("loc", "0,0")
        lat, lon = map(float, loc.split(","))
        address = f"{city}, {region}, {country}"
        log_event(f"Fallback location: {address} | {lat:.4f}, {lon:.4f}")
        return lat, lon, address
    except Exception as e:
        log_event(f"Fallback location also failed: {e}")
        return 0.0, 0.0, "Location unavailable"


def format_location(lat, lon, address):
    """Format location string for overlay and WhatsApp."""
    if lat == 0.0 and lon == 0.0:
        return "Location unavailable", "Location unavailable"
    maps_link  = f"https://maps.google.com/?q={lat},{lon}"
    short_text = f"{address} | {lat:.4f}, {lon:.4f}"
    return short_text, maps_link


# ============================================================
#   WHATSAPP MESSAGE (FIXED - actually sends instead of drafting)
# ============================================================
def send_whatsapp_alert(location_text, maps_link, snapshot_path):
    """Send emergency WhatsApp message via pywhatkit + pyautogui to press Enter."""
    try:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = (
            f"EMERGENCY ALERT!\n"
            f"Time: {ts}\n"
            f"Location: {location_text}\n"
            f"Map: {maps_link}\n"
            f"Snapshot saved at: {snapshot_path}"
        )

        log_event(f"Sending WhatsApp to {EMERGENCY_CONTACT}...")

        # Open WhatsApp Web and type the message
        pywhatkit.sendwhatmsg_instantly(
            f"+{EMERGENCY_CONTACT}",
            message,
            wait_time=50,      # seconds to wait for WhatsApp Web to load
            tab_close=False,  # keep tab open so pyautogui can press Enter
            close_time=45
        )

        # FIX: pywhatkit types the message but doesn't press Enter — do it manually
        time.sleep(4)                   # wait for typing to finish
        pyautogui.press('enter')        # actually sends the message
        time.sleep(2)
        pyautogui.hotkey('ctrl', 'w')   # close the WhatsApp tab

        log_event("WhatsApp message sent successfully!")

    except Exception as e:
        log_event(f"WhatsApp send failed: {e}")
        print(f"WhatsApp error: {e}")


# ============================================================
#   WEBCAM SNAPSHOT WITH OVERLAY
# ============================================================
def capture_snapshot(location_text, lat, lon, ts):
    """Capture webcam photo with emergency overlay."""
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        log_event("ERROR: Could not open webcam!")
        return None

    # Warm up camera
    for _ in range(3):
        cap.read()

    ret, frame = cap.read()
    cap.release()

    if not ret or frame is None:
        log_event("ERROR: Could not capture frame!")
        return None

    # Red banner at top
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (frame.shape[1], 90), (0, 0, 200), -1)
    cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

    cv2.putText(frame, "EMERGENCY MODE ACTIVATED",
        (10, 40), cv2.FONT_HERSHEY_DUPLEX,
        1.0, (255, 255, 255), 2, cv2.LINE_AA)

    cv2.putText(frame, f"Time: {ts}",
        (10, 75), cv2.FONT_HERSHEY_SIMPLEX,
        0.55, (255, 255, 200), 1, cv2.LINE_AA)

    # Black bar at bottom with location
    cv2.rectangle(frame,
        (0, frame.shape[0] - 35),
        (frame.shape[1], frame.shape[0]),
        (0, 0, 0), -1)
    cv2.putText(frame, f"Location: {location_text}",
        (10, frame.shape[0] - 10),
        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 1, cv2.LINE_AA)

    filename = os.path.join(
        SNAPSHOT_FOLDER,
        f"emergency_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    )
    cv2.imwrite(filename, frame)
    log_event(f"Snapshot saved: {filename}")
    return filename


# ============================================================
#   TKINTER ALERT POPUP
# ============================================================
def show_alert_popup(snapshot_path, ts, location_text, full_emergency=False):
    """Show emergency alert popup window."""
    def _show():
        root = Tk()
        root.title("EMERGENCY MODE")
        root.configure(bg="#cc0000")
        root.geometry("600x500")
        root.lift()
        root.attributes("-topmost", True)

        title_text = "EMERGENCY MODE ACTIVATED" if full_emergency else "SNAPSHOT TAKEN"
        Label(root, text=title_text,
              font=("Times New Roman", 20, "bold"),
              bg="#cc0000", fg="white").pack(pady=10)

        Label(root, text=f"Time: {ts}",
              font=("Times New Roman", 13),
              bg="#cc0000", fg="white").pack()

        Label(root, text=f"Location: {location_text}",
              font=("Times New Roman", 11),
              bg="#cc0000", fg="lightyellow",
              wraplength=560).pack(pady=5)

        if full_emergency:
            Label(root, text="WhatsApp alert sent to emergency contact!",
                  font=("Times New Roman", 11, "italic"),
                  bg="#cc0000", fg="lightyellow").pack(pady=3)

        if snapshot_path and os.path.exists(snapshot_path):
            try:
                img = Image.open(snapshot_path)
                img = img.resize((500, 300), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                label = Label(root, image=photo, bg="#cc0000")
                label.image = photo
                label.pack(pady=10)
            except Exception as e:
                Label(root, text=f"(Could not load image: {e})",
                      bg="#cc0000", fg="white").pack()

        root.after(8000, root.destroy)
        root.mainloop()

    threading.Thread(target=_show, daemon=True).start()


# ============================================================
#   FULL EMERGENCY TRIGGER
# ============================================================
def trigger_emergency(full_emergency=False):
    """Main emergency trigger — get location, snapshot, alert, WhatsApp."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print("Getting location...")
    lat, lon, address = get_location()
    location_text, maps_link = format_location(lat, lon, address)
    print(f"Location: {location_text}")

    print("Capturing webcam snapshot...")
    snapshot_path = capture_snapshot(location_text, lat, lon, ts)

    if snapshot_path:
        print(f"Snapshot saved: {snapshot_path}")
    else:
        print("Snapshot failed!")

    show_alert_popup(snapshot_path, ts, location_text, full_emergency)

    if full_emergency:
        threading.Thread(
            target=send_whatsapp_alert,
            args=(location_text, maps_link, snapshot_path),
            daemon=True
        ).start()


# ============================================================
#   VOICE LISTENER
# ============================================================
def listen_for_code_word():
    """Continuously listens for code word. Runs until stop_event is set."""
    recognizer = sr.Recognizer()
    recognizer.energy_threshold         = 200
    recognizer.pause_threshold          = 0.5
    recognizer.dynamic_energy_threshold = False
    mic = sr.Microphone(device_index=MIC_INDEX)

    with mic as source:
        print("Calibrating for ambient noise... stay quiet for 1 second")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print(f"Ready! Listening for code word: '{CODE_WORD}'")
        print(f"Say '{CODE_WORD}' once       -> silent snapshot + location")
        print(f"Say '{CODE_WORD} {CODE_WORD}' twice -> full emergency + WhatsApp alert")
        print("Press Ctrl+C to stop\n")

    while not stop_event.is_set():
        try:
            with mic as source:
                audio = recognizer.listen(source, timeout=2, phrase_time_limit=3)

            text = recognizer.recognize_google(audio).lower()
            print(f"Heard: '{text}'")

            count = text.count(CODE_WORD.lower())

            if count >= 2:
                log_event("CODE WORD DETECTED TWICE - FULL EMERGENCY!")
                threading.Thread(target=play_alert, daemon=True).start()
                trigger_emergency(full_emergency=True)
                time.sleep(5)
                print(f"Listening again for '{CODE_WORD}'...")

            elif count == 1:
                log_event("CODE WORD DETECTED ONCE - Taking snapshot")
                trigger_emergency(full_emergency=False)
                time.sleep(3)
                print(f"Listening again for '{CODE_WORD}'...")

        except sr.WaitTimeoutError:
            print("... listening ...")
        except sr.UnknownValueError:
            print("(couldn't understand, try again)")
        except sr.RequestError as e:
            log_event(f"Speech API error: {e}")
            time.sleep(2)
        except KeyboardInterrupt:
            print("\nStopping emergency mode...")
            stop_event.set()
            break
        except Exception as e:
            log_event(f"Error: {e}")
            time.sleep(1)

    print("Emergency Mode stopped.")


# ============================================================
#   MAIN
# ============================================================
if __name__ == "__main__":
    print("=" * 55)
    print("       EMERGENCY MODE v5 - FIXED")
    print("=" * 55)
    print(f"Code word        : '{CODE_WORD}'")
    print(f"Emergency contact: +{EMERGENCY_CONTACT}")
    print(f"Snapshots saved  : ./{SNAPSHOT_FOLDER}/")
    print(f"Log file         : {LOG_FILE}")
    print("=" * 55)
    print()

    if "91 xxxxx xxxxx" in EMERGENCY_CONTACT:
        print("WARNING: Emergency contact not set!")
        print("Open this file and update EMERGENCY_CONTACT at the top.")
        print()

    try:
        listen_for_code_word()
    except KeyboardInterrupt:
        print("\nEmergency Mode stopped by user.")
