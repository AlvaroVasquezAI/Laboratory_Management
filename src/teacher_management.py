# teacher_management.py
import pandas as pd
from datetime import datetime

class TeacherManager:
    def __init__(self):
        self.teachers_file = "data/teachers.csv"
        self.teachers_df = self._load_teachers()

    def _load_teachers(self):
        try:
            return pd.read_csv(self.teachers_file)
        except FileNotFoundError:
            return pd.DataFrame(columns=['teacher_id', 'name', 'subjects', 'schedule'])

    def add_teacher(self, name, subjects, schedule):
        new_id = len(self.teachers_df) + 1
        new_teacher = {
            'teacher_id': f"{new_id:02d}",
            'name': name,
            'subjects': subjects,
            'schedule': schedule
        }
        self.teachers_df = self.teachers_df.append(new_teacher, ignore_index=True)
        self.teachers_df.to_csv(self.teachers_file, index=False)