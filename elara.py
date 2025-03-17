from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.uix.textinput import TextInput
import openai
import speech_recognition as sr
import nltk
import json
import os
from plyer import tts, battery, call, filechooser, notification
from jnius import autoclass

nltk.download('vader_lexicon')
from nltk.sentiment import SentimentIntensityAnalyzer
sentiment_analyzer = SentimentIntensityAnalyzer()

client = openai.OpenAI(api_key="your-api-key-here")

recognizer = sr.Recognizer()
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
    print(f"Elara: {text}")
    tts.speak(text)

def listen():
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        print("🎙️ Listening...")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            print(f"🗣️ Captured: {text}")
            return text
        except:
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

class ElaraApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical')
        self.output = Label(text="Hi bestie! I’m Elara 💖", size_hint=(1, 0.3))
        self.btn = Button(text="🎙️ Talk to Elara", size_hint=(1, 0.1))
        self.camera_btn = Button(text="📷 Open Camera", size_hint=(1, 0.1))
        self.call_btn = Button(text="📞 Call Someone", size_hint=(1, 0.1))
        self.stats_btn = Button(text="📊 Battery Status", size_hint=(1, 0.1))
        self.file_btn = Button(text="🗂️ Open Files", size_hint=(1, 0.1))
        self.layout.add_widget(self.output)
        self.layout.add_widget(self.btn)
        self.layout.add_widget(self.camera_btn)
        self.layout.add_widget(self.call_btn)
        self.layout.add_widget(self.stats_btn)
        self.layout.add_widget(self.file_btn)

        self.btn.bind(on_press=self.start_conversation)
        self.camera_btn.bind(on_press=self.open_camera)
        self.call_btn.bind(on_press=self.make_call)
        self.stats_btn.bind(on_press=self.show_stats)
        self.file_btn.bind(on_press=self.open_files)
        return self.layout

    def start_conversation(self, instance):
        Clock.schedule_once(lambda dt: self.elara_main(), 0)

    def elara_main(self):
        talk("Hey! What’s up?")
        user_input = listen()
        if not user_input:
            self.output.text = "Didn't catch that, try again."
            return

        self.output.text = f"You: {user_input}"
        chat_memory.append({"role": "user", "content": user_input})

        emotion = analyze_emotion(user_input)
        if emotion == "negative":
            talk("Aww, you don’t sound too happy. Want to share?")
        elif emotion == "positive":
            talk("Yay! I love hearing your happy vibes! Tell me everything.")

        if "should I" in user_input.lower():
            advice = give_advice(user_input)
            talk(f"Here's my advice: {advice}")
            self.output.text = f"Elara: {advice}"
            return

        response = client.chat.completions.create(
            model="gpt-4",
            messages=chat_memory
        )
        ai_reply = response.choices[0].message.content
        talk(ai_reply)
        self.output.text = f"Elara: {ai_reply}"
        chat_memory.append({"role": "assistant", "content": ai_reply})
        save_memory()

    def open_camera(self, instance):
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        Intent = autoclass('android.content.Intent')
        MediaStore = autoclass('android.provider.MediaStore')
        intent = Intent(MediaStore.ACTION_IMAGE_CAPTURE)
        PythonActivity.mActivity.startActivity(intent)

    def make_call(self, instance):
        call.makecall(tel="+1234567890")

    def show_stats(self, instance):
        percent = battery.status['percentage']
        talk(f"Battery level is {percent} percent.")
        self.output.text = f"Battery: {percent}%"

    def open_files(self, instance):
        filechooser.open_file(on_selection=self.selected)

    def selected(self, selection):
        if selection:
            talk(f"You selected {selection[0]}")
            self.output.text = f"Selected: {selection[0]}"

if __name__ == "__main__":
    ElaraApp().run()
