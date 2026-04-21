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

    def get_original_user_profile(self, education_level: str, subject_of_interest: str, skill_level: str) -> dict:
        name = input("What's your name?: ")
        self.name = name if name else "User"

        education_level = input("What's your education level? (e.g. High School, Undergraduate, Graduate): ")
        self.education_level = education_level if education_level else None

        subject_of_interest = input("What's your subject of interest? (e.g. Computer Science, English, History): ")
        self.subject_of_interest = subject_of_interest if subject_of_interest else None

        skill_level = input("What's your skill level in that subject? (e.g. Beginner, Intermediate, Advanced):")
        self.skill_level = skill_level if skill_level else None

        return {
            "Name": self.name,
            "Education Level": self.education_level,
            "Subject of Interest": self.subject_of_interest,
            "Skill Level": self.skill_level
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
    
    