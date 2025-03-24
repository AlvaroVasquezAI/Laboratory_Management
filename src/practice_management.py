# practice_management.py
import json
import os
from datetime import datetime

class PracticeManager:
    def __init__(self):
        self.practices_dir = "data/practices"
        os.makedirs(self.practices_dir, exist_ok=True)

    def save_practice(self, teacher_id, practice_data):
        practice_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{teacher_id}_{practice_id}.json"
        
        practice_info = {
            "teacher_id": teacher_id,
            "upload_date": datetime.now().isoformat(),
            "title": practice_data.get("title"),
            "subject": practice_data.get("subject"),
            "objective": practice_data.get("objective"),
            "introduction": practice_data.get("introduction"),
            "practice_name": practice_data.get("practice_name"),
            "suggested_results": practice_data.get("suggested_results")
        }

        with open(os.path.join(self.practices_dir, filename), 'w') as f:
            json.dump(practice_info, f, indent=4)
        
        return practice_id