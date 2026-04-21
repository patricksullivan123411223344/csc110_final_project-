import os 
import json

class User():
    def __init__(self, name, education_level=None, subject_of_interest=None, skill_level=None):
        self.name = name
        self.education_level = education_level
        self.subject_of_interest = subject_of_interest
        self.skill_level = skill_level
        self.current_objective = None
        self.profile_filepath = f"user_profiles/{self.name}_profile.json"
        self.user_state = {
            "Friction Score": "<:LOW:>",
            "Last Move": None,
        }

    def save_user_profile(self, data: dict, filepath: str) -> None:
        initial_user_data = data 
        if not os.path.exists("user_profiles"):
            os.makedirs("user_profiles")
        
        with open(filepath, "w") as f:
            json.dump(initial_user_data, f, indent=4)
        
    def load_user_profile(self, filepath: str) -> dict:
        if os.path.exists(filepath):
            try:
                with open(filepath, "r") as f:
                    data = json.load(f)
            except json.JSONDecodeError:
                print(f"Error: Invalid JSON in {filepath}")
                return None
            
            return data

    
    