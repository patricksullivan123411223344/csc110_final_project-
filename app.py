from flask import Flask, request, jsonify, send_from_directory
from npc_class import NPC
from user import User
import os

app = Flask(__name__, static_folder="frontend")

llm_tutor=NPC("gemma3:1b", "Tutor Bot", "Idle")
user = User("User")

if os.path.exists(user.profile_filepath):
    user_data = user.load_user_profile(user.profile_filepath)
    llm_tutor.update_user_profile(user_data)
else:
    initial_user_data = user.get_original_user_profile(user.education_level, user.subject_of_interest, user.skill_level)
    user.save_user_profile(initial_user_data, user.profile_filepath)
    llm_tutor.update_user_profile(initial_user_data)

@app.route("/")
def index():
    return send_from_directory("frontend", "index.html")

@app.route("/chat", methods=["POST"])
def chat():
    body = request.get_json()
    user_message = body.get("message", "").strip()

    if not user_message:
        return jsonify({"error": "Empty Message"}), 400
    
    response = llm_tutor.respond(user_message)
    llm_tutor.save_stm()
    llm_tutor.save_ltm()

    return jsonify({"reply": response})

if __name__ == "__main__":
    app.run(debug=True)

