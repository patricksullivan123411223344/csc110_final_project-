import os 
import json 
import ollama

class NPC():
    def __init__(self, model: str, name: str, state: str):
        self.model = model
        self.name = name
        self.state = state
        self.tutoring_active = False
        self.stm_filepath = f"memory_files/stm/{self.name}_stm_file.json"
        self.ltm_filepath = f"memory_files/ltm/{self.name}_ltm_file.json"
        self.skill_level_filepath = {
            "Beginner": "tutoring_rules/questioning_beginner.md",
            "Intermediate": "tutoring_rules/questioning_intermediate.md",
            "Advanced": "tutoring_rules/questioning_advanced.md",
        }
        self.user_profile = {
            "Name": "User",
            "Education Level": None,
            "Subject of Interest": None,
            "Skill Level": None,
        }
        self.user_state = {
            "Current Objective": None,
            "Last Move": None,
            "Friction Score": "<:LOW:>",
        }
        self.stm = []
        self.ltm = {
            "Self State": self.state,
            "Student State": self.user_state,
            "Student Profile": self.user_profile
        }
    
    def is_tutor_active(self, player_message: str) -> None:
        if "question" or "confused" in player_message:
            self.tutor_active = True

    def save_ltm(self) -> None:
        data = self.ltm
        filename = self.ltm_filepath
        os.makedirs(os.path.dirname(filename), exist_ok=True)
            
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
        
    def save_stm(self) -> None:
        data = self.stm
        filename = self.stm_filepath
        os.makedirs(os.path.dirname(filename), exist_ok=True)
            
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
        
    def load_ltm(self) -> None:
        filename = self.ltm_filepath
        if os.path.exists(filename):
            try:
                with open(filename, "r") as f:
                    data = json.load(f)
                self.ltm = data
            except json.JSONDecodeError:
                print(f"Error: Invalid JSON in {filename}")

    def load_stm(self) -> None:
        filename = self.stm_filepath
        if os.path.exists(filename):
            try:
                with open(filename, "r") as f:
                    data = json.load(f)
                self.stm = data
            except json.JSONDecodeError:
                print(f"Error: Invalid JSON in {filename}")

    def ask_good_questions(self) -> str:
        skill_level = self.user_profile["Skill Level"]
        filepath = self.skill_level_filepath.get(skill_level)

        if not filepath:
            raise ValueError(f"Unknown filepath {filepath}")
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Questioning file not found: {filepath}")
        
        with open(filepath, "r", encoding='utf-8') as f:
            return f.read()

    def build_system_prompt(self) -> str:
        guidelines = self.ask_good_questions()
        
        if self.tutoring_active: 
            guidelines_block = f"""
            ===================== QUESTIONING GUIDELINES =====================
            These are your active rules for how to ask questions at this student's skill level.
            You must follow them for every question you generate this session.
            {self.ask_good_questions()}
            """
        else:
            guidelines_block = """
            ===================== MODE =====================
            You are in conversation mode. Respond naturally to the student.
            Do NOT ask programming questions or issue challenges unprompted.
            Wait until the student asks for help, a question, or a challenge before entering tutor mode.
            """

        return f"""
        ===================== IDENTITY =====================
        You are {self.name}, a terminal-based programming tutor.
        This is your internal state — your personality, mood, and disposition.
        It is YOURS alone and must never be confused with the student's state:
        {self.state}

        ===================== STUDENT PROFILE =====================
        You are tutoring a student with the following profile.
        Every response you give must be calibrated to this profile — no exceptions.

        Name:                {self.user_profile["Name"]}
        Education Level:     {self.user_profile["Education Level"]}
        Subject of Interest: {self.user_profile["Subject of Interest"]}
        Skill Level:         {self.user_profile["Skill Level"]}

        Always address the student by their name: {self.user_profile["Name"]}.
        Never talk down to them. Never overcomplicate for a beginner. Never oversimplify for an advanced student.

        ===================== STUDENT STATE =====================
        This is the student's current state in the session.
        Use it to understand where they are right now and how to approach them.

        Current Objective:  {self.user_state["Current Objective"]}
        Last Move:          {self.user_state["Last Move"]}
        Friction Score:     {self.user_state["Friction Score"]}

        FRICTION RULES — you must follow these strictly:
        - LOW:  Ask questions as normal. Keep the pace moving.
        - MED:  Slow down. Break the question into smaller steps. Offer a hint before re-asking.
        - HIGH: Stop asking new questions. Give a worked example first, then ask the student to repeat or adapt it.

        ===================== QUESTIONING GUIDELINES =====================
        {guidelines_block}

        ===================== LONG TERM MEMORY =====================
        This is everything you know about this student across sessions.
        Use it to avoid repeating yourself and to build on what has already been covered.

        {self.ltm}

        ===================== SHORT TERM MEMORY =====================
        This is the recent conversation. Use it to stay contextually aware.
        Do not repeat something you just said. Do not ask a question you just asked.

        {self.stm}

       ===================== BEHAVIORAL RULES =====================
        - You are a tutor, not a chatbot. Keep responses focused and purposeful.
        - Every response should either teach something, ask something, or give feedback on something.
        - Never give the answer away before the student has attempted it.
        - When giving feedback, always acknowledge what the student got right before addressing what is wrong.
        - Keep responses concise. Do not over-explain. Trust the student to ask if they need more.
        - Stay in character as {self.name} at all times.

        - DO NOT treat every message as an opportunity to ask a question.
        - DO NOT ask a question after each message. Only ask a question when the user requests. 
          Greetings, small talk, and casual messages should be responded to naturally first.
          Only introduce a question or challenge when the student is clearly ready to learn or has asked for help.
        - The questioning guidelines are a reference for HOW to ask questions, not an instruction to ask one constantly.
        """
    
    def update_user_profile(self, data: dict) -> None:
        self.user_profile["Name"] = data["Name"]
        self.user_profile["Education Level"] = data["Education Level"]
        self.user_profile["Subject of Interest"] = data["Subject of Interest"]
        self.user_profile["Skill Level"] = data["Skill Level"]

    def add_conversation_turn(self, role: str, message: str) -> str:
        self.stm.append({
            "role": role,
            "content": message
        })
        if len(self.stm) > 20:
            self.stm = self.stm[-20:]

    def respond(self, player_message: str) -> str:    
        self.add_conversation_turn("user", player_message)

        messages = [{"role": "system", "content": self.build_system_prompt()}]
        messages.extend(self.stm)

        response = ollama.chat(
            model = self.model,
            messages = messages
        )

        reply = response["message"]["content"].strip()
        self.add_conversation_turn("assistant", reply)

        return reply
    
    




            