# main_app.py
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import json
import os
import sqlite3
from datetime import datetime
from PIL import Image
import shutil
import fitz  # PyMuPDF
from PIL import Image, ImageTk

class LabManagementSystem(ctk.CTk):

    def __init__(self):
        super().__init__()

        # Set theme and appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Define styles after window initialization
        self.button_style = {
            "height": 50,
            "font": ctk.CTkFont(size=16, weight="bold"),
            "fg_color": "gray30",
            "hover_color": "gray40",
            "corner_radius": 8
        }

        self.entry_style = {
            "height": 40,
            "font": ctk.CTkFont(size=16),
            "corner_radius": 8
        }

        self.label_style = {
            "font": ctk.CTkFont(size=16),
            "text_color": "gray90"
        }

        # Initialize subjects list
        self.subjects_list = []
        
        # Initialize database and directories
        self.setup_database()
        self.setup_directories()

        # Configure window
        self.title("Laboratory Practice Management System")
        self.attributes("-fullscreen", True)
        self.fullscreen = True
        self.bind("<Escape>", self.exit_fullscreen)
        
        # Get screen width and height
        screen_width = self.winfo_screenwidth()
        
        # Calculate widths
        nav_width = int(screen_width * 0.25)  # 25% of screen width
        content_width = int(screen_width * 0.75)  # 75% of screen width
        
        # Configure main grid layout with fixed proportions
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, minsize=nav_width, weight=0)  # Navigation panel - fixed width
        self.grid_columnconfigure(1, minsize=content_width, weight=1)  # Content area

        # Create and setup frames
        self.setup_navigation_frame()
        self.setup_main_frames()
        
        # Show default frame
        self.select_frame_by_name("home")

    def setup_main_frames(self):
        """Setup all main content frames"""
        # Calculate content width (75% of screen width)
        content_width = int(self.winfo_screenwidth() * 0.75)
        
        frame_style = {
            "corner_radius": 0,
            "fg_color": "transparent",
            "border_width": 2,
            "border_color": "gray30",
            "width": content_width
        }

        # Create main content frames with consistent sizing
        self.home_frame = ctk.CTkFrame(self, **frame_style)
        self.upload_frame = ctk.CTkFrame(self, **frame_style)
        self.teachers_frame = ctk.CTkFrame(self, **frame_style)
        self.consult_frame = ctk.CTkFrame(self, **frame_style)

        # Prevent frames from resizing
        for frame in [self.home_frame, self.upload_frame, self.teachers_frame, self.consult_frame]:
            frame.grid_propagate(False)

        # Initialize frame contents
        self.setup_home_frame()
        self.setup_upload_frame()
        self.setup_teachers_frame()
        self.setup_consult_frame()

    def toggle_fullscreen(self, event=None):
        self.fullscreen = not self.fullscreen
        self.attributes("-fullscreen", self.fullscreen)

    def exit_fullscreen(self, event=None):
        self.fullscreen = False
        self.attributes("-fullscreen", False)

    def setup_database(self):
        """Initialize SQLite database with the new practice structure"""
        self.conn = sqlite3.connect('lab_management.db')
        self.cursor = self.conn.cursor()

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS teachers (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                subjects TEXT, 
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create practices table with new structure
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS practices (
                id INTEGER PRIMARY KEY,
                teacher_id INTEGER,
                subject TEXT,
                title TEXT,
                objective TEXT,
                introduction TEXT,
                summary TEXT,
                development TEXT,
                goals TEXT,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                num_pages INTEGER,
                file_path TEXT,
                FOREIGN KEY (teacher_id) REFERENCES teachers (id)
            )
        ''')

        self.conn.commit()

    def setup_directories(self):
        """Create necessary directories for file storage"""
        self.base_dir = "folders"  # Changed from 'uploads' to 'folders'
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)

    def setup_navigation_frame(self):
        """Setup the navigation sidebar"""
        nav_style = {
            "corner_radius": 0,
            "fg_color": "gray20",
            "border_width": 1,
            "border_color": "gray30"
        }
        
        # Calculate width (25% of screen width)
        nav_width = int(self.winfo_screenwidth() * 0.25)
        
        self.navigation_frame = ctk.CTkFrame(self, width=nav_width, **nav_style)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew", padx=(10,5), pady=10)
        self.navigation_frame.grid_propagate(False)  # Prevent frame from resizing
        
        # Navigation header
        header_frame = ctk.CTkFrame(self.navigation_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=10, pady=(20,30), sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            header_frame,
            text="Lab Management",
            font=ctk.CTkFont(size=24, weight="bold")
        ).grid(row=0, column=0, pady=10)

        # Navigation buttons
        buttons = [
            ("Home", "home", self.home_button_event),
            ("Upload Practice", "upload", self.upload_button_event),
            ("Manage Teachers", "teachers", self.teachers_button_event),
            ("Consult Practices", "consult", self.consult_button_event)
        ]

        self.navigation_frame.grid_columnconfigure(0, weight=1)

        for idx, (text, name, command) in enumerate(buttons):
            btn = ctk.CTkButton(
                self.navigation_frame,
                text=text,
                command=command,
                width=nav_width-40,  # Account for padding
                **self.button_style
            )
            btn.grid(row=idx+1, column=0, padx=20, pady=10, sticky="ew")

    def setup_home_frame(self):
        """Setup home frame with better spacing"""
        self.home_frame.grid_columnconfigure(0, weight=1)
        
        # Welcome section with larger text and better spacing
        welcome_frame = ctk.CTkFrame(self.home_frame, fg_color="transparent")
        welcome_frame.grid(row=0, column=0, padx=30, pady=(20,10), sticky="ew")
        welcome_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            welcome_frame,
            text="Welcome to Lab Management System",
            font=ctk.CTkFont(size=32, weight="bold")  # Increased font size
        ).grid(row=0, column=0, pady=20)

        # Search section with matching style
        search_frame = ctk.CTkFrame(self.home_frame, fg_color="gray20")
        search_frame.grid(row=1, column=0, padx=30, pady=20, sticky="ew")
        search_frame.grid_columnconfigure(0, weight=3)
        search_frame.grid_columnconfigure(1, weight=1)

        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search practices...",
            height=50,  # Increased height
            font=ctk.CTkFont(size=16)  # Larger font
        )
        self.search_entry.grid(row=0, column=0, padx=20, pady=20, sticky="ew")

        self.search_button = ctk.CTkButton(
            search_frame,
            text="Search",
            height=50,  # Matching height
            width=150,  # Fixed width
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self.search_practices
        )
        self.search_button.grid(row=0, column=1, padx=20, pady=20)

        # Setup statistics frame
        self.setup_stats_frame()

        # Setup activities frame
        self.setup_activities_frame()

    def setup_search_frame(self):
        """Setup search functionality"""
        search_frame = ctk.CTkFrame(self.home_frame)
        search_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.search_entry = ctk.CTkEntry(
            search_frame, 
            width=300, 
            placeholder_text="Search practices...",
            **self.entry_style
        )
        self.search_entry.grid(row=0, column=0, padx=10, pady=10)

        self.search_button = ctk.CTkButton(
            search_frame, 
            text="Search", 
            command=self.search_practices,
            **self.button_style
        )
        self.search_button.grid(row=0, column=1, padx=10, pady=10)

    def setup_stats_frame(self):
        """Setup statistics display"""
        stats_frame = ctk.CTkFrame(self.home_frame, fg_color="gray20")
        stats_frame.grid(row=2, column=0, padx=30, pady=20, sticky="ew")
        stats_frame.grid_columnconfigure((0,1), weight=1)

        # Create statistics labels with larger text
        self.total_practices_label = ctk.CTkLabel(
            stats_frame, 
            text="Total Practices: 0",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.total_practices_label.grid(row=0, column=0, padx=30, pady=20)

        self.total_teachers_label = ctk.CTkLabel(
            stats_frame, 
            text="Total Teachers: 0",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.total_teachers_label.grid(row=0, column=1, padx=30, pady=20)

    def setup_activities_frame(self):
        """Setup recent activities display"""
        self.activities_frame = ctk.CTkFrame(self.home_frame, fg_color="gray20")
        self.activities_frame.grid(row=3, column=0, padx=30, pady=20, sticky="nsew")
        self.activities_frame.grid_columnconfigure(0, weight=1)

        self.activities_label = ctk.CTkLabel(
            self.activities_frame, 
            text="Recent Activities",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.activities_label.grid(row=0, column=0, padx=20, pady=20)

        self.activities_list = ctk.CTkTextbox(
            self.activities_frame, 
            height=300,
            font=ctk.CTkFont(size=16)
        )
        self.activities_list.grid(row=1, column=0, padx=20, pady=(0,20), sticky="ew")

    def setup_upload_frame(self):
        """Setup practice upload form with improved layout"""
        self.upload_frame.grid_columnconfigure(0, weight=1)
        
        # Title section with larger text
        title_frame = ctk.CTkFrame(self.upload_frame, fg_color="transparent")
        title_frame.grid(row=0, column=0, padx=30, pady=(20,30), sticky="ew")
        title_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            title_frame,
            text="Upload New Practice",
            font=ctk.CTkFont(size=24, weight="bold")
        ).grid(row=0, column=0)

        # Main form container
        form_frame = ctk.CTkFrame(self.upload_frame, fg_color="gray20")
        form_frame.grid(row=1, column=0, padx=30, pady=(0,20), sticky="ew")
        form_frame.grid_columnconfigure(1, weight=1)

        # Practice Title
        ctk.CTkLabel(
            form_frame, 
            text="Practice Title:", 
            font=ctk.CTkFont(size=16)
        ).grid(row=0, column=0, padx=20, pady=15, sticky="e")
        
        self.title_entry = ctk.CTkEntry(
            form_frame,
            height=40,
            font=ctk.CTkFont(size=16)
        )
        self.title_entry.grid(row=0, column=1, padx=(0,20), pady=15, sticky="ew")

        # Teacher Selection
        ctk.CTkLabel(
            form_frame, 
            text="Teacher:", 
            font=ctk.CTkFont(size=16)
        ).grid(row=1, column=0, padx=20, pady=15, sticky="e")
        
        self.teacher_combo = ctk.CTkComboBox(
            form_frame,
            height=40,
            font=ctk.CTkFont(size=16),
            values=self.get_teacher_names(),
            command=self.on_teacher_select
        )
        self.teacher_combo.grid(row=1, column=1, padx=(0,20), pady=15, sticky="ew")

        # Subject Selection
        ctk.CTkLabel(
            form_frame, 
            text="Subject:", 
            font=ctk.CTkFont(size=16)
        ).grid(row=2, column=0, padx=20, pady=15, sticky="e")
        
        self.upload_subject_combo = ctk.CTkComboBox(  # Changed name here
            form_frame,
            height=40,
            font=ctk.CTkFont(size=16),
            values=[],
            state="disabled"
        )
        self.upload_subject_combo.grid(row=2, column=1, padx=(0,20), pady=15, sticky="ew")

        # Objective
        ctk.CTkLabel(
            form_frame, 
            text="Objective:", 
            font=ctk.CTkFont(size=16)
        ).grid(row=3, column=0, padx=20, pady=15, sticky="ne")
        
        self.objective_text = ctk.CTkTextbox(
            form_frame,
            height=100,
            font=ctk.CTkFont(size=16)
        )
        self.objective_text.grid(row=3, column=1, padx=(0,20), pady=15, sticky="ew")

        # File upload section
        file_frame = ctk.CTkFrame(self.upload_frame, fg_color="gray20")
        file_frame.grid(row=2, column=0, padx=30, pady=20, sticky="ew")
        file_frame.grid_columnconfigure(0, weight=1)

        # File Selection Button
        self.upload_file_button = ctk.CTkButton(
            file_frame,
            text="Select File",
            height=45,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self.select_file
        )
        self.upload_file_button.grid(row=0, column=0, padx=20, pady=(20,10))

        # Preview Label
        self.preview_label = ctk.CTkLabel(
            file_frame,
            text="File Preview",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.preview_label.grid(row=1, column=0, pady=(10,5))

        # Preview Frame
        self.preview_frame = ctk.CTkFrame(file_frame, fg_color="gray25")
        self.preview_frame.grid(row=2, column=0, padx=20, pady=(5,20), sticky="ew")
        self.preview_frame.grid_columnconfigure(0, weight=1)

        # Preview Image Label
        self.preview_image_label = ctk.CTkLabel(
            self.preview_frame,
            text="No file selected",
            font=ctk.CTkFont(size=14)
        )
        self.preview_image_label.grid(row=0, column=0, padx=10, pady=10)

        # Submit Button
        self.submit_practice_button = ctk.CTkButton(
            self.upload_frame,
            text="Submit Practice",
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self.submit_practice
        )
        self.submit_practice_button.grid(row=3, column=0, padx=30, pady=20)

    def on_teacher_select(self, choice):
        """Handle teacher selection and update subject combo box"""
        if choice:
            try:
                # Get subjects for selected teacher
                self.cursor.execute("""
                    SELECT subjects 
                    FROM teachers 
                    WHERE name = ?
                """, (choice,))
                result = self.cursor.fetchone()
                
                if result and result[0]:
                    # Enable subject combo box and update values
                    subjects = result[0].split(',')
                    self.upload_subject_combo.configure(  # Changed here
                        state="normal",
                        values=subjects
                    )
                    # Set first subject as default
                    if subjects:
                        self.upload_subject_combo.set(subjects[0])  # Changed here
                else:
                    self.upload_subject_combo.configure(  # Changed here
                        state="disabled",
                        values=[]
                    )
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load subjects: {str(e)}")

    def setup_teachers_frame(self):
        """Setup teacher management interface with improved layout"""
        self.teachers_frame.grid_columnconfigure(0, weight=1)
        
        # Title section
        title_frame = ctk.CTkFrame(self.teachers_frame, fg_color="transparent")
        title_frame.grid(row=0, column=0, padx=30, pady=(20,30), sticky="ew")
        title_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            title_frame,
            text="Teachers Management",
            font=ctk.CTkFont(size=24, weight="bold")
        ).grid(row=0, column=0)

        # Table section
        table_frame = ctk.CTkFrame(self.teachers_frame, fg_color="gray20")
        table_frame.grid(row=1, column=0, padx=30, pady=(0,20), sticky="nsew")
        table_frame.grid_columnconfigure(0, weight=1)

        # Table headers with improved styling
        headers_frame = ctk.CTkFrame(table_frame, fg_color="gray25")
        headers_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        headers_frame.grid_columnconfigure((0,1,2,3,4), weight=1)

        headers = ["ID", "Name", "Subjects", "Number of Subjects", "Practices Uploaded"]
        for i, header in enumerate(headers):
            ctk.CTkLabel(
                headers_frame,
                text=header,
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="white"
            ).grid(row=0, column=i, padx=20, pady=10)

        # Create scrollable frame for table content
        self.teachers_table = ctk.CTkScrollableFrame(
            table_frame,
            height=300,
            fg_color="transparent"
        )
        self.teachers_table.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0,20))
        self.teachers_table.grid_columnconfigure((0,1,2,3,4), weight=1)

        # Update table content
        self.update_teachers_table()

        # Create a scrollable frame for the "Add New Teacher" section
        add_section_container = ctk.CTkScrollableFrame(
            self.teachers_frame,
            fg_color="gray20",
            height=400  # Adjust this value as needed
        )
        add_section_container.grid(row=2, column=0, padx=30, pady=20, sticky="ew")
        add_section_container.grid_columnconfigure(1, weight=1)

        # Section title
        ctk.CTkLabel(
            add_section_container,
            text="Add New Teacher",
            font=ctk.CTkFont(size=20, weight="bold")
        ).grid(row=0, column=0, columnspan=2, padx=20, pady=20)

        # Form fields
        # Teacher name
        ctk.CTkLabel(
            add_section_container,
            text="Name:",
            **self.label_style
        ).grid(row=1, column=0, padx=20, pady=15, sticky="e")
        
        self.teacher_name_entry = ctk.CTkEntry(
            add_section_container,
            **self.entry_style
        )
        self.teacher_name_entry.grid(row=1, column=1, padx=(0,20), pady=15, sticky="ew")

        # Subjects
        ctk.CTkLabel(
            add_section_container,
            text="Subjects:",
            **self.label_style
        ).grid(row=2, column=0, padx=20, pady=15, sticky="e")

        # Subject selection
        subjects_frame = ctk.CTkFrame(add_section_container, fg_color="transparent")
        subjects_frame.grid(row=2, column=1, padx=(0,20), pady=15, sticky="ew")
        subjects_frame.grid_columnconfigure(0, weight=1)

        # Subject combo box for adding new subjects
        self.add_subject_combo = ctk.CTkComboBox(
            subjects_frame,
            values=self.get_existing_subjects(),
            width=200,
            **self.entry_style
        )
        self.add_subject_combo.grid(row=0, column=0, sticky="ew")

        # Add subject button
        add_subject_btn = ctk.CTkButton(
            subjects_frame,
            text="+",
            width=40,
            command=self.add_subject_to_list,
            **self.button_style
        )
        add_subject_btn.grid(row=0, column=1, padx=(10,0))

        # Subjects display frame
        subjects_container = ctk.CTkFrame(
            add_section_container,
            fg_color="transparent"
        )
        subjects_container.grid(row=3, column=1, padx=(0,20), pady=15, sticky="ew")
        subjects_container.grid_columnconfigure(0, weight=1)

        # Create a scrollable frame for subjects
        self.subjects_display_frame = ctk.CTkScrollableFrame(
            subjects_container,
            height=150,
            fg_color="gray25",
            width=400
        )
        self.subjects_display_frame.grid(row=0, column=0, sticky="ew")
        self.subjects_display_frame.grid_columnconfigure(0, weight=1)

        # Admin password
        ctk.CTkLabel(
            add_section_container,
            text="Admin Password:",
            **self.label_style
        ).grid(row=4, column=0, padx=20, pady=15, sticky="e")
        
        self.password_entry = ctk.CTkEntry(
            add_section_container,
            show="*",
            **self.entry_style
        )
        self.password_entry.grid(row=4, column=1, padx=(0,20), pady=15, sticky="ew")

        # Add teacher button
        self.add_teacher_button = ctk.CTkButton(
            add_section_container,
            text="Add Teacher",
            command=self.add_teacher,
            **self.button_style
        )
        self.add_teacher_button.grid(row=5, column=0, columnspan=2, pady=30)

    def setup_teachers_table(self):
        """Setup table to display teachers information"""
        # Table frame
        table_frame = ctk.CTkFrame(self.teachers_frame)
        table_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        # Table headers
        headers = ["ID", "Name", "Subjects", "Number of Subjects", "Practices Uploaded"]
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(
                table_frame, 
                text=header,
                font=ctk.CTkFont(weight="bold")
            )
            label.grid(row=0, column=i, padx=10, pady=5, sticky="w")

        # Create scrollable frame for table content
        self.teachers_table = ctk.CTkScrollableFrame(table_frame, height=300)
        self.teachers_table.grid(row=1, column=0, columnspan=len(headers), sticky="nsew", padx=10, pady=5)

        # Update table content
        self.update_teachers_table()

    def update_teachers_table(self):
        """Update teachers table with improved styling and alignment"""
        # Clear existing content
        for widget in self.teachers_table.winfo_children():
            widget.destroy()

        # Configure columns with weights
        for i in range(5):
            self.teachers_table.grid_columnconfigure(i, weight=1)

        # Column widths (adjust these values as needed)
        column_widths = {
            0: 50,   # ID
            1: 150,  # Name
            2: 300,  # Subjects
            3: 150,  # Number of Subjects
            4: 150   # Practices Uploaded
        }

        # Get teachers data
        self.cursor.execute("""
            SELECT 
                t.id,
                t.name,
                t.subjects,
                (SELECT COUNT(*) FROM practices WHERE teacher_id = t.id) as practice_count
            FROM teachers t
        """)
        teachers = self.cursor.fetchall()

        # Display teachers with improved styling and alignment
        for row, teacher in enumerate(teachers):
            # Create a frame for each row
            row_frame = ctk.CTkFrame(
                self.teachers_table,
                fg_color="gray20" if row % 2 == 0 else "gray25",
                height=50
            )
            row_frame.grid(row=row, column=0, columnspan=5, sticky="ew", pady=1)
            
            # Configure columns in row frame
            for i in range(5):
                row_frame.grid_columnconfigure(i, weight=1, minsize=column_widths[i])

            # ID
            ctk.CTkLabel(
                row_frame,
                text=str(teacher[0]),
                width=column_widths[0],
                anchor="center",
                **self.label_style
            ).grid(row=0, column=0, padx=5, pady=10, sticky="ew")
            
            # Name
            ctk.CTkLabel(
                row_frame,
                text=teacher[1],
                width=column_widths[1],
                anchor="w",
                **self.label_style
            ).grid(row=0, column=1, padx=5, pady=10, sticky="ew")
            
            # Subjects
            subjects = teacher[2].split(',') if teacher[2] else []
            ctk.CTkLabel(
                row_frame,
                text=', '.join(subjects),
                width=column_widths[2],
                anchor="w",
                **self.label_style
            ).grid(row=0, column=2, padx=5, pady=10, sticky="ew")
            
            # Number of subjects
            ctk.CTkLabel(
                row_frame,
                text=str(len(subjects)),
                width=column_widths[3],
                anchor="center",
                **self.label_style
            ).grid(row=0, column=3, padx=5, pady=10, sticky="ew")
            
            # Practices count
            ctk.CTkLabel(
                row_frame,
                text=str(teacher[3]),
                width=column_widths[4],
                anchor="center",
                **self.label_style
            ).grid(row=0, column=4, padx=5, pady=10, sticky="ew")
        
    def setup_add_teacher_section(self):
        """Setup section for adding new teachers"""
        # Add teacher frame
        add_frame = ctk.CTkFrame(self.teachers_frame)
        add_frame.grid(row=2, column=0, padx=20, pady=20, sticky="nsew")

        # Section title
        add_title = ctk.CTkLabel(
            add_frame, 
            text="Add New Teacher",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        add_title.grid(row=0, column=0, columnspan=2, padx=20, pady=10)

        # Teacher name
        self.teacher_name_label = ctk.CTkLabel(add_frame, text="Name:")
        self.teacher_name_label.grid(row=1, column=0, padx=20, pady=5)
        self.teacher_name_entry = ctk.CTkEntry(add_frame, width=200)
        self.teacher_name_entry.grid(row=1, column=1, padx=20, pady=5)

        # Subjects section
        self.teacher_subjects_label = ctk.CTkLabel(add_frame, text="Subjects:")
        self.teacher_subjects_label.grid(row=2, column=0, padx=20, pady=5)

        subjects_frame = ctk.CTkFrame(add_frame)
        subjects_frame.grid(row=2, column=1, padx=20, pady=5, sticky="ew")

        # Create a frame for subject selection
        subject_selection_frame = ctk.CTkFrame(subjects_frame)
        subject_selection_frame.grid(row=0, column=0, sticky="ew")

        # Existing subjects dropdown with entry
        existing_subjects = self.get_existing_subjects()
        self.subject_combo = ctk.CTkComboBox(
            subject_selection_frame,
            width=200,
            values=existing_subjects
        )
        self.subject_combo.grid(row=0, column=0, padx=5)

        # Add subject button
        add_subject_btn = ctk.CTkButton(
            subjects_frame, 
            text="+", 
            width=30,
            command=self.add_subject_to_list
        )
        add_subject_btn.grid(row=0, column=1, padx=5)

        # Create frame for displaying subjects
        self.subjects_display_frame = ctk.CTkFrame(add_frame)
        self.subjects_display_frame.grid(row=3, column=1, padx=20, pady=5, sticky="ew")

        # Admin password
        self.password_label = ctk.CTkLabel(add_frame, text="Admin Password:")
        self.password_label.grid(row=4, column=0, padx=20, pady=5)
        self.password_entry = ctk.CTkEntry(add_frame, width=200, show="*")
        self.password_entry.grid(row=4, column=1, padx=20, pady=5)

        # Add teacher button
        self.add_teacher_button = ctk.CTkButton(
            add_frame, 
            text="Add Teacher",
            command=self.add_teacher
        )
        self.add_teacher_button.grid(row=5, column=0, columnspan=2, pady=20)

    def add_subject_to_list(self):
        """Add subject to the list of subjects"""
        subject = self.add_subject_combo.get().strip()  # Use the renamed combo box
        
        if not subject:
            return
        
        # Check if subject already exists in the list
        if subject in self.subjects_list:
            messagebox.showwarning("Warning", "This subject has already been added")
            return
        
        # Add the subject
        self.subjects_list.append(subject)
        self.update_subjects_display()
        self.add_subject_combo.set("")  # Clear the input

    def update_subjects_display(self):
        """Update the display of added subjects with delete buttons"""
        # Clear existing display
        for widget in self.subjects_display_frame.winfo_children():
            widget.destroy()

        # Add each subject with a delete button
        for subject in self.subjects_list:
            subject_frame = ctk.CTkFrame(
                self.subjects_display_frame,
                fg_color="gray30"
            )
            subject_frame.pack(fill="x", padx=5, pady=2)
            subject_frame.grid_columnconfigure(0, weight=1)

            # Subject label
            subject_label = ctk.CTkLabel(
                subject_frame,
                text=f"• {subject}",
                anchor="w",
                **self.label_style
            )
            subject_label.pack(side="left", padx=10, pady=5, fill="x", expand=True)

            # Delete button
            delete_button = ctk.CTkButton(
                subject_frame,
                text="×",
                width=30,
                height=30,
                command=lambda s=subject: self.delete_subject(s),
                fg_color="red",
                hover_color="dark red"
            )
            delete_button.pack(side="right", padx=5, pady=5)

    def add_teacher(self):
        """Add new teacher to database with password verification"""
        ADMIN_PASSWORD = "123"  # Set your admin password

        name = self.teacher_name_entry.get()
        password = self.password_entry.get()

        if not name:
            messagebox.showerror("Error", "Teacher name is required")
            return

        if not self.subjects_list:
            messagebox.showerror("Error", "At least one subject is required")
            return

        if password != ADMIN_PASSWORD:
            messagebox.showerror("Error", "Invalid admin password")
            return

        try:
            # Create directory structure first
            if not self.create_teacher_directories(name, self.subjects_list):
                return

            # Insert teacher into database
            self.cursor.execute("""
                INSERT INTO teachers (name, subjects)
                VALUES (?, ?)
            """, (name, ','.join(self.subjects_list)))
            self.conn.commit()

            # Update UI
            self.add_activity_log(f"New teacher added: {name}")
            self.update_statistics()
            self.update_teachers_table()
            
            # Clear form
            self.teacher_name_entry.delete(0, "end")
            self.password_entry.delete(0, "end")
            self.subjects_list.clear()
            self.update_subjects_display()
            
            # Update teacher combo box in upload form
            self.teacher_combo.configure(values=self.get_teacher_names())
            
            messagebox.showinfo("Success", "Teacher added successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add teacher: {str(e)}")

    # Database and File Operations
    def get_teacher_names(self):
        """Get list of teacher names for combo box"""
        self.cursor.execute("SELECT name FROM teachers")
        return [row[0] for row in self.cursor.fetchall()]

    def update_statistics(self):
        """Update statistics display"""
        # Get practice count
        self.cursor.execute("SELECT COUNT(*) FROM practices")
        practice_count = self.cursor.fetchone()[0]
        self.total_practices_label.configure(text=f"Total Practices: {practice_count}")

        # Get teacher count
        self.cursor.execute("SELECT COUNT(*) FROM teachers")
        teacher_count = self.cursor.fetchone()[0]
        self.total_teachers_label.configure(text=f"Total Teachers: {teacher_count}")

    def add_activity_log(self, activity):
        """Add new activity to the log"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.activities_list.insert("0.0", f"[{timestamp}] {activity}\n")

    def select_file(self):
        """Handle file selection with preview"""
        try:
            filename = filedialog.askopenfilename(
                filetypes=[
                    ("PDF files", "*.pdf"),
                    ("Word files", "*.doc;*.docx"),
                    ("All files", "*.*")
                ]
            )
            
            if filename:
                # Verify file exists and is readable
                if os.path.exists(filename) and os.access(filename, os.R_OK):
                    self.selected_file_path = filename
                    display_name = os.path.basename(filename)
                    self.upload_file_button.configure(text=f"Selected: {display_name}")
                    
                    # Show preview if it's a PDF
                    if filename.lower().endswith('.pdf'):
                        self.show_pdf_preview(filename)
                    else:
                        self.preview_image_label.configure(text="Preview only available for PDF files")
                else:
                    messagebox.showerror("Error", "Selected file is not accessible")
                    self.selected_file_path = None
                    self.upload_file_button.configure(text="Select File")
                    self.preview_image_label.configure(text="")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to select file: {str(e)}")
            self.selected_file_path = None
            self.upload_file_button.configure(text="Select File")
            self.preview_image_label.configure(text="")

    def submit_practice(self):
        """Handle practice submission with organized file storage"""
        if not self.validate_practice_form():
            return

        try:
            # Get teacher information
            teacher_name = self.teacher_combo.get()
            subject = self.upload_subject_combo.get()  
            practice_title = self.sanitize_filename(self.title_entry.get())  # Use sanitize_filename here

            # Get teacher ID
            self.cursor.execute("SELECT id FROM teachers WHERE name = ?", (teacher_name,))
            teacher_id = self.cursor.fetchone()[0]

            if hasattr(self, 'selected_file_path'):
                try:
                    # Generate filename with pattern: practiceName_subject_teacherID_date.pdf
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = self.sanitize_filename(f"{practice_title}_{subject}_teacher{teacher_id}_{timestamp}.pdf")  # Use sanitize_filename here
                    
                    # Create path to subject directory
                    destination_dir = os.path.join(self.base_dir, teacher_name, subject)
                    
                    # Ensure directory exists
                    os.makedirs(destination_dir, exist_ok=True)
                    
                    destination = os.path.join(destination_dir, filename)
                    
                    # Copy file using plain file operations
                    with open(self.selected_file_path, 'rb') as src_file:
                        with open(destination, 'wb') as dst_file:
                            dst_file.write(src_file.read())

                    # Process the PDF
                    practice_info = self.process_pdf(self.selected_file_path)
                    if not practice_info:
                        practice_info = {
                            'num_pages': 0,
                            'objective': "File processing failed",
                            'introduction': "File processing failed",
                            'summary': "File processing failed",
                            'development': "File processing failed",
                            'goals': "File processing failed"
                        }

                    # Insert practice into database
                    self.cursor.execute("""
                        INSERT INTO practices (
                            teacher_id, subject, title, objective,
                            introduction, summary, development, goals,
                            num_pages, file_path
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        teacher_id,
                        subject,
                        practice_title,
                        self.objective_text.get("1.0", "end-1c") or practice_info['objective'],
                        practice_info['introduction'],
                        practice_info['summary'],
                        practice_info['development'],
                        practice_info['goals'],
                        practice_info['num_pages'],
                        destination  # Store the full path
                    ))
                    self.conn.commit()

                    # Update UI
                    self.add_activity_log(f"New practice added: {practice_title}")
                    self.update_statistics()
                    self.clear_practice_form()
                    
                    messagebox.showinfo("Success", "Practice submitted successfully!")
                    
                except IOError as e:
                    messagebox.showerror("File Error", f"Failed to copy file: {str(e)}")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to process practice: {str(e)}")
            else:
                messagebox.showerror("Error", "No file selected")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to submit practice: {str(e)}")
            # Print detailed error information
            import traceback
            print("Error details:")
            print(traceback.format_exc())

    def validate_practice_form(self):
        """Validate practice form inputs"""
        if not self.title_entry.get().strip():
            messagebox.showerror("Error", "Practice title is required")
            return False
        if not self.teacher_combo.get():
            messagebox.showerror("Error", "Please select a teacher")
            return False
        if not self.upload_subject_combo.get():  # Changed here
            messagebox.showerror("Error", "Please select a subject")
            return False
        if not hasattr(self, 'selected_file_path'):
            messagebox.showerror("Error", "Please select a practice file")
            return False
        return True

    def clear_practice_form(self):
        """Clear practice form inputs"""
        self.title_entry.delete(0, 'end')
        self.teacher_combo.set('')
        self.upload_subject_combo.configure(state="disabled", values=[])  # Changed here
        self.objective_text.delete("1.0", "end")
        self.upload_file_button.configure(text="Select File")
        self.preview_image_label.configure(image="", text="")
        if hasattr(self, 'selected_file_path'):
            del self.selected_file_path

    def search_practices(self):
        """Search practices in database"""
        search_term = self.search_entry.get()
        if not search_term:
            messagebox.showinfo("Info", "Please enter a search term")
            return

        try:
            self.cursor.execute("""
                SELECT p.title, p.subject, t.name 
                FROM practices p
                JOIN teachers t ON p.teacher_id = t.id
                WHERE p.title LIKE ? OR p.subject LIKE ? OR t.name LIKE ?
            """, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
            
            results = self.cursor.fetchall()
            
            # Show results in a new window
            self.show_search_results(results)
            
        except Exception as e:
            messagebox.showerror("Error", f"Search failed: {str(e)}")

    def show_search_results(self, results):
        """Display search results in a new window"""
        results_window = ctk.CTkToplevel(self)
        results_window.title("Search Results")
        results_window.geometry("500x400")

        # Create results display
        results_text = ctk.CTkTextbox(results_window, width=460, height=360)
        results_text.pack(padx=20, pady=20)

        if not results:
            results_text.insert("1.0", "No results found.")
        else:
            for title, subject, teacher in results:
                results_text.insert("end", f"Title: {title}\n")
                results_text.insert("end", f"Subject: {subject}\n")
                results_text.insert("end", f"Teacher: {teacher}\n")
                results_text.insert("end", "-" * 40 + "\n")

    def select_frame_by_name(self, name):
        """Switch between different frames"""
        frames = {
            "home": self.home_frame,
            "upload": self.upload_frame,
            "teachers": self.teachers_frame,
            "consult": self.consult_frame
        }
        
        for frame_name, frame in frames.items():
            if frame_name == name:
                frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=10)
            else:
                frame.grid_remove()

    def process_pdf(self, file_path):
        """Extract information from PDF file with better error handling"""
        try:
            import PyPDF2
            with open(file_path, 'rb') as file:
                try:
                    pdf = PyPDF2.PdfReader(file)
                    num_pages = len(pdf.pages)
                    
                    # Extract text from first few pages for analysis
                    text = ""
                    try:
                        for i in range(min(3, num_pages)):
                            text += pdf.pages[i].extract_text()
                    except:
                        # If text extraction fails, continue with basic info
                        pass

                    return {
                        'num_pages': num_pages,
                        'objective': "To be extracted by LLM",
                        'introduction': "To be extracted by LLM",
                        'summary': "To be generated by LLM",
                        'development': "To be extracted by LLM",
                        'goals': "To be extracted by LLM"
                    }
                except Exception as e:
                    # If PDF processing fails, return basic info
                    return {
                        'num_pages': 0,  # Unable to determine page count
                        'objective': "Unable to extract",
                        'introduction': "Unable to extract",
                        'summary': "Unable to extract",
                        'development': "Unable to extract",
                        'goals': "Unable to extract"
                    }
        except Exception as e:
            # Return default values if file processing completely fails
            return {
                'num_pages': 0,
                'objective': "File processing failed",
                'introduction': "File processing failed",
                'summary': "File processing failed",
                'development': "File processing failed",
                'goals': "File processing failed"
            }
        
    def setup_consult_frame(self):
        """Setup practice consultation interface with improved layout"""
        self.consult_frame.grid_columnconfigure(0, weight=1)
        
        # Title section with larger text
        title_frame = ctk.CTkFrame(self.consult_frame, fg_color="transparent")
        title_frame.grid(row=0, column=0, padx=30, pady=(20,30), sticky="ew")
        title_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            title_frame,
            text="Consult Practices",
            font=ctk.CTkFont(size=24, weight="bold")
        ).grid(row=0, column=0)

        # Search options frame with improved styling
        search_frame = ctk.CTkFrame(self.consult_frame, fg_color="gray20")
        search_frame.grid(row=1, column=0, padx=30, pady=(0,20), sticky="ew")
        search_frame.grid_columnconfigure((1, 2), weight=1)

        # Practice ID search with consistent styling
        ctk.CTkLabel(
            search_frame,
            text="Practice ID:",
            **self.label_style
        ).grid(row=0, column=0, padx=20, pady=15, sticky="e")
        
        self.practice_id_entry = ctk.CTkEntry(
            search_frame,
            width=200,
            **self.entry_style
        )
        self.practice_id_entry.grid(row=0, column=1, padx=(0,20), pady=15, sticky="w")
        
        self.search_by_id_button = ctk.CTkButton(
            search_frame,
            text="Search by ID",
            command=self.search_by_practice_id,
            **self.button_style
        )
        self.search_by_id_button.grid(row=0, column=2, padx=20, pady=15)

        # Teacher search with consistent styling
        ctk.CTkLabel(
            search_frame,
            text="Teacher:",
            **self.label_style
        ).grid(row=1, column=0, padx=20, pady=15, sticky="e")
        
        self.teacher_search_combo = ctk.CTkComboBox(
            search_frame,
            values=self.get_teacher_names(),
            width=200,
            **self.entry_style
        )
        self.teacher_search_combo.grid(row=1, column=1, padx=(0,20), pady=15, sticky="w")
        
        self.search_by_teacher_button = ctk.CTkButton(
            search_frame,
            text="Search by Teacher",
            command=self.search_by_teacher,
            **self.button_style
        )
        self.search_by_teacher_button.grid(row=1, column=2, padx=20, pady=15)

        # Results section with improved styling
        results_frame = ctk.CTkFrame(self.consult_frame, fg_color="gray20")
        results_frame.grid(row=2, column=0, padx=30, pady=20, sticky="nsew")
        results_frame.grid_columnconfigure(0, weight=1)

        # Results header
        ctk.CTkLabel(
            results_frame,
            text="Practice List",
            font=ctk.CTkFont(size=20, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=15)

        # Results textbox with improved styling
        self.practice_listbox = ctk.CTkTextbox(
            results_frame,
            height=300,
            font=ctk.CTkFont(size=16)
        )
        self.practice_listbox.grid(row=1, column=0, padx=20, pady=(0,20), sticky="nsew")

        # Generate PDF button with consistent styling
        self.generate_pdf_button = ctk.CTkButton(
            self.consult_frame,
            text="Generate PDF Report",
            command=self.generate_practice_pdf,
            **self.button_style
        )
        self.generate_pdf_button.grid(row=3, column=0, padx=30, pady=20)

    def search_by_practice_id(self):
        """Search practice by ID"""
        practice_id = self.practice_id_entry.get()
        if not practice_id:
            messagebox.showwarning("Warning", "Please enter a practice ID")
            return

        try:
            self.cursor.execute("""
                SELECT p.*, t.name as teacher_name 
                FROM practices p
                JOIN teachers t ON p.teacher_id = t.id
                WHERE p.id = ?
            """, (practice_id,))
            
            practice = self.cursor.fetchone()
            if practice:
                self.display_practice_results([practice])
            else:
                messagebox.showinfo("Info", "No practice found with this ID")
        except Exception as e:
            messagebox.showerror("Error", f"Search failed: {str(e)}")

    def search_by_teacher(self):
        """Search practices by teacher"""
        teacher_name = self.teacher_search_combo.get()
        if not teacher_name:
            messagebox.showwarning("Warning", "Please select a teacher")
            return

        try:
            self.cursor.execute("""
                SELECT p.*, t.name as teacher_name 
                FROM practices p
                JOIN teachers t ON p.teacher_id = t.id
                WHERE t.name = ?
            """, (teacher_name,))
            
            practices = self.cursor.fetchall()
            if practices:
                self.display_practice_results(practices)
            else:
                messagebox.showinfo("Info", "No practices found for this teacher")
        except Exception as e:
            messagebox.showerror("Error", f"Search failed: {str(e)}")

    def display_practice_results(self, practices):
        """Display practice results in the listbox"""
        self.practice_listbox.delete("1.0", "end")
        self.current_practices = practices  # Store for PDF generation

        for practice in practices:
            self.practice_listbox.insert("end", f"ID: {practice[0]}\n")
            self.practice_listbox.insert("end", f"Title: {practice[3]}\n")
            self.practice_listbox.insert("end", f"Subject: {practice[2]}\n")
            self.practice_listbox.insert("end", f"Teacher: {practice[-1]}\n")
            self.practice_listbox.insert("end", f"Date: {practice[9]}\n")
            self.practice_listbox.insert("end", "-" * 40 + "\n")

    def generate_practice_pdf(self):
        """Generate PDF report for selected practice"""
        if not hasattr(self, 'current_practices'):
            messagebox.showwarning("Warning", "Please search for a practice first")
            return

        try:
            from fpdf import FPDF

            # Create PDF
            pdf = FPDF()
            
            for practice in self.current_practices:
                pdf.add_page()
                
                # Header
                pdf.set_font('Arial', 'B', 16)
                pdf.cell(0, 10, 'Practice Report', 0, 1, 'C')
                pdf.ln(10)

                # Practice details
                pdf.set_font('Arial', 'B', 12)
                details = [
                    f"Practice ID: {practice[0]}",
                    f"Teacher: {practice[-1]}",
                    f"Subject: {practice[2]}",
                    f"Title: {practice[3]}",
                    f"Date: {practice[9]}",
                    f"Number of Pages: {practice[10]}",
                    "",
                    "Objective:",
                    practice[4],
                    "",
                    "Introduction:",
                    practice[5],
                    "",
                    "Summary:",
                    practice[6],
                    "",
                    "Development:",
                    practice[7],
                    "",
                    "Goals:",
                    practice[8]
                ]

                pdf.set_font('Arial', '', 12)
                for detail in details:
                    pdf.multi_cell(0, 10, detail)

            # Save PDF
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pdf_path = f"practice_report_{timestamp}.pdf"
            pdf.output(pdf_path)
            
            messagebox.showinfo("Success", f"PDF report generated: {pdf_path}")
            
            # Open PDF
            import os
            os.startfile(pdf_path) if os.name == 'nt' else os.system(f'open {pdf_path}')
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate PDF: {str(e)}")

    def create_teacher_directories(self, teacher_name, subjects):
        """Create directory structure for a new teacher"""
        try:
            # Create teacher's main directory
            teacher_dir = os.path.join(self.base_dir, teacher_name)
            if not os.path.exists(teacher_dir):
                os.makedirs(teacher_dir)

            # Create subdirectories for each subject
            for subject in subjects:
                subject_dir = os.path.join(teacher_dir, subject.strip())
                if not os.path.exists(subject_dir):
                    os.makedirs(subject_dir)

            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create directories: {str(e)}")
            return False
        
    def sanitize_filename(self, filename):
        """Sanitize filename to prevent issues"""
        # Remove or replace problematic characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Replace spaces with underscores
        filename = filename.replace(' ', '_')
        
        # Limit length
        if len(filename) > 200:
            name, ext = os.path.splitext(filename)
            filename = name[:196] + ext
        
        return filename
    
    def show_pdf_preview(self, pdf_path):
        """Show preview of the first page of the PDF"""
        try:
            # Open PDF
            doc = fitz.open(pdf_path)
            
            # Get first page
            page = doc[0]
            
            # Convert to image
            pix = page.get_pixmap(matrix=fitz.Matrix(1, 1))  # 1:1 scale
            
            # Convert to PIL Image
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            # Resize to fit preview frame (maintain aspect ratio)
            preview_width = 380  # Slightly smaller than frame width
            aspect_ratio = img.height / img.width
            preview_height = int(preview_width * aspect_ratio)
            
            if preview_height > 480:  # Max height
                preview_height = 480
                preview_width = int(preview_height / aspect_ratio)
            
            img = img.resize((preview_width, preview_height), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(img)
            
            # Update preview label
            self.preview_image_label.configure(image=photo)
            self.preview_image_label.image = photo  # Keep reference
            
            doc.close()
        except Exception as e:
            self.preview_image_label.configure(text="Preview not available")
            print(f"Preview error: {str(e)}")
        
    def get_practice_path(self, teacher_name, subject, filename):
        """Helper function to get the full path for a practice file"""
        return os.path.join(self.base_dir, teacher_name, subject, filename)
    
    def get_existing_subjects(self):
        """Get all unique subjects from the database"""
        try:
            self.cursor.execute("SELECT subjects FROM teachers")
            all_subjects = self.cursor.fetchall()
            unique_subjects = set()
            for subjects_str in all_subjects:
                if subjects_str[0]:  # Check if not None
                    subjects = subjects_str[0].split(',')
                    unique_subjects.update(subject.strip() for subject in subjects)
            return sorted(list(unique_subjects))
        except Exception as e:
            print(f"Error getting subjects: {e}")
            return []

    
    def delete_subject(self, subject):
        """Remove a subject from the list"""
        if subject in self.subjects_list:
            self.subjects_list.remove(subject)
            self.update_subjects_display()
        
    def on_subject_select(self, choice):
        """Handle subject selection from dropdown"""
        if choice and choice not in self.subjects_list:
            self.subjects_list.append(choice)
            self.update_subjects_display()

    def on_subject_combo_select(self, choice):
        """Handle selection from dropdown"""
        if choice:
            self.subject_entry.delete(0, 'end')  # Clear entry field

    def home_button_event(self):
        self.select_frame_by_name("home")

    def upload_button_event(self):
        self.select_frame_by_name("upload")

    def teachers_button_event(self):
        self.select_frame_by_name("teachers")

    def on_closing(self):
        """Handle application closing"""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.conn.close()
            self.quit()

    def consult_button_event(self):
        self.select_frame_by_name("consult")

if __name__ == "__main__":
    app = LabManagementSystem()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
    