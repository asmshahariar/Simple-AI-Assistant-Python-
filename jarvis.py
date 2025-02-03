import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import pyttsx3
import speech_recognition as sr
import datetime
import wikipedia
import webbrowser
import os
import pyautogui
import psutil
import requests
import json
import time
import random
import threading
import ctypes
import sys
import pyjokes
import python_weather
import asyncio
from googlesearch import search
from newsapi import NewsApiClient
import pyperclip
import screen_brightness_control as sbc
from pynput.keyboard import Key, Controller
import wolframalpha

class JarvisAI:
    def __init__(self, root):
        self.root = root
        self.root.title("Jarvis AI Assistant")
        self.root.geometry("800x600")
        self.root.configure(bg='#2C3E50')
        
        # Initialize text-to-speech engine
        self.engine = pyttsx3.init('sapi5')
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[0].id)
        self.engine.setProperty('rate', 190)
        
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Initialize other components
        self.keyboard = Controller()
        self.wake_word = "jarvis"
        self.user = "boss"
        self.listening = False
        self.todo_list = []
        self.notes = []
        self.reminders = []
        self.volume_level = 50
        
        # Setup GUI
        self.setup_gui()
        
    def setup_gui(self):
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(padx=20, pady=20, fill='both', expand=True)
        
        # Status display
        self.status_var = tk.StringVar(value="Status: Ready")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, font=('Arial', 12))
        status_label.pack(pady=10)
        
        # Output text area
        self.output_text = scrolledtext.ScrolledText(main_frame, height=20, width=60, font=('Arial', 10))
        self.output_text.pack(pady=10)
        
        # Input frame
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill='x', pady=10)
        
        # Text input
        self.input_entry = ttk.Entry(input_frame, font=('Arial', 10))
        self.input_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        self.input_entry.bind('<Return>', lambda e: self.process_command(self.input_entry.get()))
        
        # Buttons
        ttk.Button(input_frame, text="Send", command=lambda: self.process_command(self.input_entry.get())).pack(side='left')
        ttk.Button(input_frame, text="Start Listening", command=self.toggle_listening).pack(side='left', padx=5)
        ttk.Button(input_frame, text="Clear", command=self.clear_output).pack(side='left')
        
    def speak(self, text):
        self.output_text.insert(tk.END, f"Jarvis: {text}\n")
        self.output_text.see(tk.END)
        self.engine.say(text)
        self.engine.runAndWait()
        
    def listen(self):
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
            audio = self.recognizer.listen(source)
            try:
                text = self.recognizer.recognize_google(audio).lower()
                if self.wake_word in text:
                    command = text.replace(self.wake_word, "").strip()
                    self.process_command(command)
            except:
                pass
                
    def toggle_listening(self):
        if not self.listening:
            self.listening = True
            self.status_var.set("Status: Listening...")
            threading.Thread(target=self.listen_loop, daemon=True).start()
        else:
            self.listening = False
            self.status_var.set("Status: Ready")
            
    def listen_loop(self):
        while self.listening:
            self.listen()
            
    def process_command(self, command):
        if not command:
            return
            
        self.output_text.insert(tk.END, f"You: {command}\n")
        self.output_text.see(tk.END)
        command = command.lower()
        
        # Time and Date Commands
        if "what's the time" in command:
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            self.speak(f"The time is {current_time}")
            
        elif "what's today's date" in command:
            current_date = datetime.datetime.now().strftime("%B %d, %Y")
            self.speak(f"Today is {current_date}")
            
        # System Operations
        elif "system status" in command:
            cpu = psutil.cpu_percent()
            memory = psutil.virtual_memory().percent
            self.speak(f"CPU usage is {cpu}% and memory usage is {memory}%")
            
        elif "take a screenshot" in command:
            screenshot = pyautogui.screenshot()
            screenshot.save("screenshot.png")
            self.speak("Screenshot taken and saved")
            
        elif "shutdown computer" in command:
            if messagebox.askyesno("Confirm", "Do you want to shutdown the computer?"):
                self.speak("Shutting down the computer")
                os.system("shutdown /s /t 1")
                
        # Web Operations
        elif "open youtube" in command:
            webbrowser.open("https://youtube.com")
            self.speak("Opening YouTube")
            
        elif "search youtube for" in command:
            query = command.replace("search youtube for", "").strip()
            webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
            self.speak(f"Searching YouTube for {query}")
            
        elif "open google" in command:
            webbrowser.open("https://google.com")
            self.speak("Opening Google")
            
        elif "search wikipedia" in command:
            query = command.replace("search wikipedia", "").strip()
            try:
                result = wikipedia.summary(query, sentences=2)
                self.speak(result)
            except:
                self.speak("Sorry, I couldn't find that on Wikipedia")
                
        # Weather Information
        elif "weather in" in command:
            city = command.replace("weather in", "").strip()
            self.get_weather(city)
            
        # File Operations
        elif "open documents" in command:
            os.startfile(os.path.expanduser("~/Documents"))
            self.speak("Opening Documents folder")
            
        elif "open downloads" in command:
            os.startfile(os.path.expanduser("~/Downloads"))
            self.speak("Opening Downloads folder")
            
        # Media Controls
        elif "volume up" in command:
            pyautogui.press("volumeup")
            self.speak("Volume increased")
            
        elif "volume down" in command:
            pyautogui.press("volumedown")
            self.speak("Volume decreased")
            
        elif "mute" in command:
            pyautogui.press("volumemute")
            self.speak("Audio muted")
            
        # Information Queries
        elif "tell me a joke" in command:
            joke = pyjokes.get_joke()
            self.speak(joke)
            
        elif "news headlines" in command:
            self.get_news()
            
        # Personal Assistant Features
        elif "make a note" in command:
            self.speak("What would you like me to note down?")
            note = self.input_entry.get()
            self.notes.append(note)
            self.speak("Note added successfully")
            
        elif "show my notes" in command:
            if self.notes:
                self.speak("Here are your notes:")
                for i, note in enumerate(self.notes, 1):
                    self.speak(f"{i}. {note}")
            else:
                self.speak("You don't have any notes")
                
        elif "add to todo" in command:
            task = command.replace("add to todo", "").strip()
            self.todo_list.append(task)
            self.speak(f"Added {task} to your todo list")
            
        elif "show todo list" in command:
            if self.todo_list:
                self.speak("Here's your todo list:")
                for i, task in enumerate(self.todo_list, 1):
                    self.speak(f"{i}. {task}")
            else:
                self.speak("Your todo list is empty")
                
        # Fun Commands
        elif "roll a dice" in command:
            result = random.randint(1, 6)
            self.speak(f"You rolled a {result}")
            
        elif "flip a coin" in command:
            result = random.choice(["heads", "tails"])
            self.speak(f"It's {result}")
            
        # Assistant Control
        elif "stop listening" in command:
            self.listening = False
            self.status_var.set("Status: Ready")
            self.speak("Voice recognition stopped")
            
        elif "goodbye" in command:
            self.speak(f"Goodbye {self.user}, have a great day!")
            self.root.quit()
            
        elif "help" in command:
            self.show_help()
            
        else:
            self.speak("I'm not sure how to help with that. Try saying 'help' to see available commands.")
            
    async def get_weather(self, city):
        async with python_weather.Client() as client:
            try:
                weather = await client.get(city)
                self.speak(f"The temperature in {city} is {weather.current.temperature}°C")
            except:
                self.speak("Sorry, I couldn't get the weather information")
                
    def get_news(self):
        try:
            url = "https://newsapi.org/v2/top-headlines?country=us&apiKey=YOUR_API_KEY"
            response = requests.get(url)
            news = response.json()
            self.speak("Here are the top 3 headlines:")
            for i, article in enumerate(news['articles'][:3], 1):
                self.speak(f"{i}. {article['title']}")
        except:
            self.speak("Sorry, I couldn't fetch the news")
            
    def show_help(self):
        help_text = """
        Available commands:
        1. Time and Date: "what's the time", "what's today's date"
        2. System: "system status", "take a screenshot", "shutdown computer"
        3. Web: "open youtube", "search youtube for [query]", "open google", "search wikipedia [topic]"
        4. Weather: "weather in [city]"
        5. Files: "open documents", "open downloads"
        6. Media: "volume up", "volume down", "mute"
        7. Information: "tell me a joke", "news headlines"
        8. Notes: "make a note", "show my notes"
        9. Todo: "add to todo [task]", "show todo list"
        10. Fun: "roll a dice", "flip a coin"
        11. Control: "stop listening", "goodbye", "help"
        """
        self.speak(help_text)
        
    def clear_output(self):
        self.output_text.delete(1.0, tk.END)
        
def main():
    root = tk.Tk()
    app = JarvisAI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
