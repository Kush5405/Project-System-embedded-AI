from flask import Flask, render_template, request, jsonify
import os
import threading
from ai3 import *  # Import your chatbot code

app = Flask(ai3)

# Route for the chatbot interface
@app.route("/")
def index():
    return render_template("index.html")

# Route to handle user queries
@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")
    mode = "text"  # We are using text mode for the web interface

    if user_input:
        # Handle specific commands (optional: customize these to your needs)
        if "set alarm" in user_input:
            try:
                time_str = user_input.split("set alarm for")[1].strip()
                set_alarm(time_str)
                response = "Alarm set successfully."
            except IndexError:
                response = "Please specify a time in HH:MM format."
        elif "what time is it" in user_input:
            response = tell_time()
        elif "play" in user_input and "song" in user_input:
            song_name = user_input.split("play", 1)[1].strip()
            response = play_song(song_name)
        elif "quit" in user_input:
            response = "Goodbye!"
        else:
            # Default response from AI
            prompt = f"User: {user_input}\nAssistant:"
            response = generate_response(prompt)

        return jsonify({"response": response})
    else:
        return jsonify({"response": "I didn't get that. Please try again."})

if __name__ == "__main__":
    app.run(debug=True)
