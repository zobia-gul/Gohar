from flask import Flask, send_from_directory, make_response
import requests
import threading
from gtts import gTTS
import os
import time
import subprocess
from twilio.rest import Client

app = Flask(__name__)

AUDIO_DIR = r"D:\ClouxiPlexi\GOHAR"
GTTS_AUDIO_FILE = "gtts_audio.mp3"
MALE_AUDIO_FILE = "male_audio.mp3"

application_url = "https://1326-103-164-49-34.ngrok-free.app"

@app.route('/audio')
def serve_audio():
    text = ("گوہر گروپ آف کمپنیز میں خوش آمدید! معزز کسٹمر، "
            "گوہر ولاز میں آپ کے یونٹ نمبر R 128کے آپ پر واجبات ہیں ۔ "
            "لہٰذا فوری طور پر دیے گئے نمبر پر رابطہ کریں۔")

    gtts_audio_path = os.path.join(AUDIO_DIR, GTTS_AUDIO_FILE)
    male_audio_path = os.path.join(AUDIO_DIR, MALE_AUDIO_FILE)
    text_to_audio(text, gtts_audio_path, male_audio_path)
    response = make_response(send_from_directory(AUDIO_DIR, MALE_AUDIO_FILE))
    return response

def text_to_audio(text, gtts_audio_path, male_audio_path):
    #remove gtts file if already exists
    if os.path.exists(gtts_audio_path):
        os.remove(gtts_audio_path)

    tts = gTTS(text, lang='ur')
    tts.save(gtts_audio_path)
    print(f"Audio saved to {gtts_audio_path}")

    #remove male audio file if already exists
    if os.path.exists(male_audio_path):
        os.remove(male_audio_path)
    
    # Use ffmpeg to modify the pitch and speed of the GTTS audio
    try:
        command = [
            "ffmpeg",
            "-i", gtts_audio_path,
            "-af", "asetrate=44100*0.4,atempo=1.7",  # Adjust pitch and speed
            male_audio_path
        ]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Check if the ffmpeg command was successful
        if result.returncode == 0:
            print(f"Pitch-adjusted audio saved to {male_audio_path}")
        else:
            print(f"FFmpeg error: {result.stderr}")

    except Exception as e:
        print(f"An error occurred: {e}")

def send_whatsapp_audio():
    ultramsg_instance_id = "instance93703"
    ultramsg_token = "klecvfzsqyippgue"
    url = f"https://api.ultramsg.com/{ultramsg_instance_id}/messages/audio"
    headers = {'content-type': "application/x-www-form-urlencoded"}
    audio_url = f"{application_url}/audio"
    payload = {
        "token": ultramsg_token,
        "to": "923343664034@c.us",  # Replace with the actual recipient number
        "audio": audio_url
    }
    # Send the WhatsApp audio message
    response = requests.post(url, data=payload, headers=headers)
    print(response.text)

def send_twilio_call():
    account_sid = "AC11ea28d8039c0473509aaf24a6eec26e"
    auth_token = "f20b53b7dc7310fc7705108765cf6714"
    client = Client(account_sid, auth_token)
    #make twilio call
    call = client.calls.create(
        url=f"https://twimlets.com/message?Message[0]={application_url}/audio",
        to="+923012732226",  # Replace with the actual recipient number
        from_="+19402422194"
    )
    print(f"Call SID: {call.sid}")
    
def serve_action():
    action_type = "twilio"  # Set to 'whatsapp' or 'twilio' depending on the action
    if action_type == "twilio":
        send_twilio_call()
    else:
        send_whatsapp_audio()

def start_flask_app():
    app.run(port=8000)

if __name__ == '__main__':
    flask_thread = threading.Thread(target=start_flask_app)
    flask_thread.start()
    
    serve_action()
