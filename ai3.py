import google.generativeai as genai
import speech_recognition as sr
import pyttsx3
import json
import re
import subprocess
import datetime
import webbrowser
import urllib.parse
import pyautogui
import platform
import os
from pytube import YouTube
import psutil
import time
import threading

# Initialize Gemini API
genai.configure(api_key="AIzaSyDxEiiKGiz_Ey75f1WKJ8ddMfF8kzc10NQ")
model = genai.GenerativeModel("gemini-1.5-flash")

# Initialize speech recognition and text-to-speech
recognizer = sr.Recognizer()
engine = pyttsx3.init()

# Configure voice for text-to-speech (J.A.R.V.I.S.-like)
def setup_jarvis_voice():
    voices = engine.getProperty('voices')
    selected_voice = None
    for voice in voices:
        if "english" in voice.name.lower() and ("british" in voice.name.lower() or "uk" in voice.name.lower()):
            selected_voice = voice
            break
    if not selected_voice:
        for voice in voices:
            if "english" in voice.name.lower():
                selected_voice = voice
                break
    if selected_voice:
        engine.setProperty('voice', selected_voice.id)
    engine.setProperty('rate', 150)
    engine.setProperty('volume', 0.9)

setup_jarvis_voice()

# Names file for assistant and user names
names_file = "assistant_names.json"
user_name = ""
assistant_name = "Captain"

# Load saved names
def load_names():
    global user_name, assistant_name
    if os.path.exists(names_file):
        with open(names_file, 'r') as file:
            names = json.load(file)
            user_name = names.get("user_name", "Kush")
            assistant_name = names.get("assistant_name", "Captain")

# Save names to file
def save_names():
    names = {"user_name": user_name, "assistant_name": assistant_name}
    with open(names_file, 'w') as file:
        json.dump(names, file)

# Remember names
def remember_names():
    global user_name, assistant_name
    if not user_name:
        engine.say("Hello, what is your name?")
        user_name = input("What is your name? ").strip()
    if not assistant_name:
        engine.say(f"Nice to meet you, {user_name}! What would you like to call me?")
        assistant_name = input(f"Give me a name, {user_name}: ").strip()
    save_names()
    engine.say(f"Alright, I will call myself {assistant_name}. Let's get started!")
    engine.runAndWait()

# Initialize names
load_names()
if not user_name or not assistant_name:
    remember_names()

# Function for speech recognition
def listen_for_command():
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio)
            return command.lower()
        except sr.UnknownValueError:
            return None
        except sr.RequestError:
            return None

# Function to take user input
def get_user_input(mode):
    if mode == "voice":
        return listen_for_command()
    elif mode == "text":
        return input(f"{user_name}: ").strip()
    else:
        print("Invalid mode. Restart and choose text or voice.")
        return None

# Function to generate AI response
def generate_response(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating response: {e}"

# Function to speak text
def speak(text):
    engine.say(text)
    engine.runAndWait()
    


# Function to search and play a song on YouTube
def play_song(song_name):
    query = urllib.parse.quote_plus(song_name)  # Encode the song name for URL
    url = f"https://www.youtube.com/results?search_query={query}"
    webbrowser.open(url)  # Opens the song search result page on YouTube
    return f"Playing {song_name} on YouTube!"


# Function to report the current time
def tell_time():
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%H:%M")
    speak(f"The current time is {formatted_time}.")
    print(f"The current time is {formatted_time}.")

# Function to monitor and trigger alarms
def alarm_worker(alarm_time):
    while True:
        current_time = datetime.datetime.now()
        if current_time.hour == alarm_time.hour and current_time.minute == alarm_time.minute:
            speak(f"Alarm! It's {alarm_time.strftime('%I:%M %p')}, time to wake up!")
            break
        time.sleep(30)  # Check every 30 seconds

# Function to set an alarm
def set_alarm(time_str):
    try:
        # Parse the time provided by the user
        now = datetime.datetime.now()
        alarm_time = datetime.datetime.strptime(time_str, "%H:%M").replace(
            year=now.year, month=now.month, day=now.day
        )
        # Adjust for next day if the alarm time has already passed today
        if alarm_time < now:
            alarm_time += datetime.timedelta(days=1)

        speak(f"Okay, I've set an alarm for {alarm_time.strftime('%I:%M %p')}.")
        
        # Start a thread to monitor the alarm
        alarm_thread = threading.Thread(target=alarm_worker, args=(alarm_time,))
        alarm_thread.daemon = True  # Ensure the thread exits with the program
        alarm_thread.start()
    except ValueError:
        speak("I couldn't understand the time format. Please use the format HH:MM (24-hour clock).")



# Function to summarize long text using the Gemini API
def summarize_long_text():
    # Ask the user to provide the text to summarize
    speak("Please provide the text you'd like me to summarize.")
    print("Assistant: Please provide the text you'd like me to summarize.")
    
    # Here we use input() or listen_for_command(), depending on text or voice input mode
    user_input = input("Enter text for summarization: ").strip()  # For text input

    # If the text is too long, Gemini may need it broken down into smaller chunks.
    # For now, we'll just pass the whole input, and Gemini should handle it.
    
    try:
        prompt = f"Summarize the following text: {user_input}"

        # Use the Gemini model to generate the summary
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)

        # Return the summarized text
        summarized_text = response.text
        speak(f"Here is the summary: {summarized_text}")
        print(f"Assistant: {summarized_text}")
        return summarized_text
    
    except Exception as e:
        speak("Sorry, I couldn't summarize the text at the moment.")
        print(f"Error summarizing text: {e}")
        return f"Error summarizing text: {e}"
    
# Function to take a screenshot
def take_screenshot(save_path="screenshot.png"):
    try:
        pyautogui.screenshot(save_path)
        return f"Screenshot saved as {save_path}."
    except Exception as e:
        return f"An error occurred while taking a screenshot: {e}"

# Function to open a file or folder by path
def open_file_or_folder_by_name(name):
    """
    Searches for and opens a file or folder directly through File Explorer.
    
    Args:
        name (str): Name of the file or folder to search for.
        
    Returns:
        str: Success or error message.
    """
    try:
        # Open File Explorer
        pyautogui.hotkey("win", "e")  # Windows + E to open File Explorer
        time.sleep(2)  # Wait for File Explorer to open
        
        # Focus on the search bar
        pyautogui.hotkey("ctrl", "f")  # Ctrl + F focuses the search bar in File Explorer
        time.sleep(1)
        
        # Type the name of the file or folder
        pyautogui.write(name, interval=0.1)
        time.sleep(1)
        
        # Press Enter to execute the search
        pyautogui.press("enter")
        time.sleep(3)  # Wait for the search results to populate
        
        # Simulate pressing Enter to open the first result
        pyautogui.press("enter")
        return f"Opening '{name}' via File Explorer."
    
    except Exception as e:
        return f"An error occurred while searching for '{name}': {e}"

# Function to open a website
def open_website(website_name):
    try:
        # Ensure proper URL format
        if not website_name.startswith(('http://', 'https://')):
            if '.' not in website_name:  # If no domain, it's not a valid website
                return f"'{website_name}' does not appear to be a valid website."
            website_name = 'https://www.' + website_name.strip()

        # Open the website using the default browser
        webbrowser.open(website_name)
        return f"Opening {website_name}..."
    except Exception as e:
        return f"An error occurred while opening the website: {e}"


# Application management
def open_application(app_name):
    try:
        pyautogui.hotkey("win", "s")
        time.sleep(1)
        pyautogui.write(app_name, interval=0.1)
        time.sleep(1)
        pyautogui.press("enter")
        return f"Opening {app_name}."
    except Exception as e:
        return f"Error opening {app_name}: {e}"

def close_application(app_name):
    try:
        for proc in psutil.process_iter(['name']):
            if app_name.lower() in proc.info['name'].lower():
                proc.terminate()
                return f"Closed {app_name}."
        return f"{app_name} not found."
    except Exception as e:
        return f"Error closing {app_name}: {e}"

# Main assistant loop
speak(f"{assistant_name} is ready! How can I help you, {user_name}?")
mode = input("Use text or voice? (type 'text' or 'voice'): ").strip().lower()

while True:
    user_input = get_user_input(mode)
    if not user_input:
        continue

    if "set alarm" in user_input:
             try:
                time_str = user_input.split("set alarm for")[1].strip()
                set_alarm(time_str)
             except IndexError:
                speak("Please specify a time in the format HH:MM.")
                
    elif "what time is it" in user_input or "tell time" in user_input:
            tell_time()
            
    # Play song based on user input
    elif "play" in user_input and "song" in user_input:
        song_name = user_input.split("play", 1)[1].strip()
        song_response = play_song(song_name)
        speak(song_response)
        print(song_response)
                
    elif "launch" in user_input:
        app_name = user_input.replace("launch", "").strip()
        response = open_application(app_name)
        speak(response)
        print(response)

    # Check commands for specific actions
    elif "run" in user_input:
        website_name = user_input.split("run", 1)[1].strip()
        if "." in website_name:  # Assume website if a domain is present
            response = open_website(website_name)
            
    elif "can you help me summarize" in user_input:
               summarize_long_text()  # Call the summarize function

    
    elif "open file" in user_input :
        item_name = user_input.split("open file", 1)[-1].strip()
        response = open_file_or_folder_by_name(item_name)
        speak(response)
        print(f"{assistant_name}: {response}")
        
    elif "open folder" in user_input:
        item_name = user_input.split("open folder", 1)[-1].strip()
        response = open_file_or_folder_by_name(item_name)
        speak(response)
        print(f"{assistant_name}: {response}")

    elif "screenshot" in user_input:
        screenshot_path = "screenshot.png"
        response = take_screenshot(screenshot_path)
        speak(response)
        print(f"{assistant_name}: {response}")


    elif "close" in user_input:
        app_name = user_input.replace("close", "").strip()
        response = close_application(app_name)
        speak(response)
        print(response)

    elif "quit" in user_input:
        speak("Goodbye!")
        break

    else:
        prompt = f"User: {user_input}\nAssistant:"
        ai_response = generate_response(prompt)
        speak(ai_response)
        print(f"Assistant: {ai_response}")
