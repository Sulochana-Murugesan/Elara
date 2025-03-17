import openai
import speech_recognition as sr
import pyttsx3
import nltk
import pyautogui
import pywhatkit
import smtplib
import os
import subprocess
import time
import threading
import keyboard
import psutil
import platform
import datetime
import json
import tkinter as tk
from tkinter import messagebox

# Setup
nltk.download('vader_lexicon')
from nltk.sentiment import SentimentIntensityAnalyzer
sentiment_analyzer = SentimentIntensityAnalyzer()

client = openai.OpenAI(api_key="")

recognizer = sr.Recognizer()
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)
engine.setProperty('rate', 175)

chat_memory = []

def save_memory():
    with open("memory.json", "w") as f:
        json.dump(chat_memory, f)

def load_memory():
    if os.path.exists("memory.json"):
        with open("memory.json", "r") as f:
            return json.load(f)
    return []

chat_memory = load_memory()

def talk(text):
    engine.say(text)
    engine.runAndWait()

def listen():
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        print("🎙️ Listening for your voice...")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            print(f"🗣️ Captured: {text}")
            return text
        except sr.UnknownValueError:
            print("😕 Could not understand audio")
            return ""
        except sr.RequestError as e:
            print(f"🚨 API Error: {e}")
            return ""

def analyze_emotion(text):
    scores = sentiment_analyzer.polarity_scores(text)
    if scores['compound'] > 0.2:
        return "positive"
    elif scores['compound'] < -0.2:
        return "negative"
    else:
        return "neutral"

def give_advice(query):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": f"Give me advice as a best friend on this: {query}"}]
    )
    return response.choices[0].message.content

def open_app(app_name):
    if "camera" in app_name:
        subprocess.run("start microsoft.windows.camera:", shell=True)
    elif "browser" in app_name:
        subprocess.run("start chrome", shell=True)
    elif "dialer" in app_name:
        subprocess.run("start ms-call: ", shell=True)
    else:
        talk("Sorry, I can't find that app bestie!")

def make_call(contact_number):
    talk(f"Calling {contact_number} now!")
    # Simulating a phone call here. You can integrate with Twilio or other APIs.

def send_whatsapp_message(number, message):
    pywhatkit.sendwhatmsg_instantly(number, message)
    talk("I sent your message on WhatsApp!")

def system_stats():
    battery = psutil.sensors_battery()
    talk(f"Battery is at {battery.percent} percent.")
    talk(f"CPU is at {psutil.cpu_percent()} percent usage.")

def read_notifications():
    talk("Reading notifications isn't set up yet, but I'm learning!")

def file_manager():
    talk("What file operation would you like, bestie? Open, delete, or list files?")
    action = listen().lower()
    if "list" in action:
        files = os.listdir()
        talk(f"Here are the files: {', '.join(files)}")
    elif "open" in action:
        talk("Which file do you want me to open?")
        file = listen()
        if os.path.exists(file):
            os.startfile(file)
            talk(f"Opening {file} now!")
        else:
            talk("Sorry, I couldn't find that file.")
    elif "delete" in action:
        talk("Which file do you want me to delete?")
        file = listen()
        if os.path.exists(file):
            os.remove(file)
            talk(f"I deleted {file} for you.")
        else:
            talk("File not found.")

def daily_affirmation():
    affirmations = [
        "You are amazing and capable of great things!",
        "I believe in you, always.",
        "You're stronger than you think, bestie.",
        "Today is going to be a wonderful day!"
    ]
    talk(affirmations[datetime.datetime.now().day % len(affirmations)])

def realtime_chat():
    daily_affirmation()
    talk("Hi love! I'm Elara, here for you. What’s up?")
    while True:
        user_input = listen()
        if user_input == "":
            continue
        print(f"You: {user_input}")
        if "bye" in user_input.lower():
            talk("Bye bestie! Remember, I'm always here for you.")
            save_memory()
            break
        chat_memory.append({"role": "user", "content": user_input})
        emotion = analyze_emotion(user_input)
        if emotion == "negative":
            talk("Aww, you don’t sound too happy. Want to share what’s bothering you?")
        elif emotion == "positive":
            talk("Yay! I love hearing your happy vibes! Tell me everything.")
        if "should I" in user_input.lower():
            advice = give_advice(user_input)
            talk(f"Here's my advice as your BFF: {advice}")
            continue
        if "open" in user_input.lower():
            app_name = user_input.lower().replace("open", "").strip()
            open_app(app_name)
            continue
        if "call" in user_input.lower():
            contact_number = user_input.lower().replace("call", "").strip()
            make_call(contact_number)
            continue
        if "send whatsapp" in user_input.lower():
            talk("What message do you want me to send?")
            msg = listen()
            number = "+11234567890"
            send_whatsapp_message(number, msg)
            continue
        if "battery" in user_input.lower() or "cpu" in user_input.lower():
            system_stats()
            continue
        if "file" in user_input.lower():
            file_manager()
            continue
        if "notification" in user_input.lower():
            read_notifications()
            continue
        response = client.chat.completions.create(
            model="gpt-4",
            messages=chat_memory
        )
        ai_reply = response.choices[0].message.content
        talk(ai_reply)
        chat_memory.append({"role": "assistant", "content": ai_reply})

def launch_gui():
    root = tk.Tk()
    root.title("Elara - Your AI Best Friend")
    root.geometry("400x200")

    def start_ai():
        threading.Thread(target=realtime_chat).start()
        messagebox.showinfo("Elara is Ready", "I'm ready! Talk to me anytime!")

    start_button = tk.Button(root, text="Start Elara", command=start_ai, font=("Arial", 14))
    start_button.pack(pady=50)

    root.mainloop()

if __name__ == "__main__":
    launch_gui()
