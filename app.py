from flask import Flask, request, jsonify, send_from_directory, render_template
from npc_class import NPC
from user import User

app = Flask(__name__, static_folder="frontend")

llm_tutor=NPC("gemma3:1b", "Tutor Bot", "Idle")
user = User("User")

@app.route("/")
def index():
    return send_from_directory("frontend", "index.html")

@app.route("/api/user-name")
def user_name():
    user_name = user.name
    return jsonify({"user_name": user_name})

@app.route("/api/chat", methods=["POST"])
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

