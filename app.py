from flask import Flask, request, jsonify, send_from_directory, render_template
from npc_class import NPC
from user import User
import os

app = Flask(__name__, static_folder="frontend")

# REVIEW: Careful about this. Globals + Flask can cause hard problems.
# Flask has a specific way to handle globals, ask Claude or read docs.
llm_tutor=NPC("gemma3:1b", "Tutor Bot", "Idle")
user = User("patrick", "Undergraduate", "Computer Science", "Intermediate")

llm_tutor.load_ltm()
llm_tutor.update_user_profile(user.load_user_profile(user.profile_filepath))

@app.route("/")
def index():
    return send_from_directory("frontend", "index.html")

@app.route("/api/user-name")
def user_name():
    user_name = user.name
    return jsonify({"user_name": user_name.upper()}), 200

# CORE ISSUE: rest API is stateless, but we want to maintain state across interactions.
@app.route("/api/chat", methods=["POST"])
def chat():
    body = request.get_json()
    user_message = body.get("message", "").strip()

    llm_tutor.load_stm()

    if not user_message:
        return jsonify({"error": "Empty Message"}), 400

    response = llm_tutor.respond(user_message)
    llm_tutor.save_stm()
    llm_tutor.save_ltm()

    return jsonify({"reply": response})

if __name__ == "__main__":
    app.run(debug=True)

