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

        # Initialize database
        self.setup_database()
        
        # Create necessary directories
        self.setup_directories()

        # Configure window
        self.title("Laboratory Practice Management System")
        self.geometry("1100x680")
        
        # Configure grid layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Create navigation frame
        self.setup_navigation_frame()

        # Create main content frames
        self.home_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.upload_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.teachers_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")

        # Initialize frame contents
        self.setup_home_frame()
        self.setup_upload_frame()
        self.setup_teachers_frame()
        self.setup_consult_frame()

        # Show default frame
        self.select_frame_by_name("home")
        
        # Update statistics
        self.update_statistics()

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
        self.navigation_frame = ctk.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(4, weight=1)

        # Navigation header
        self.navigation_frame_label = ctk.CTkLabel(
            self.navigation_frame, text="Lab Management", 
            compound="left", font=ctk.CTkFont(size=15, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        # Navigation buttons
        buttons = [
            ("Home", self.home_button_event),
            ("Upload Practice", self.upload_button_event),
            ("Manage Teachers", self.teachers_button_event),
            ("Consult Practices", self.consult_button_event)  # New button
        ]

        for idx, (text, command) in enumerate(buttons, start=1):
            btn = ctk.CTkButton(
                self.navigation_frame, corner_radius=0, height=40,
                border_spacing=10, text=text,
                fg_color="transparent", text_color=("gray10", "gray90"),
                hover_color=("gray70", "gray30"),
                command=command)
            btn.grid(row=idx, column=0, sticky="ew")

    def setup_home_frame(self):
        """Setup the home dashboard"""
        # Welcome label
        self.home_label = ctk.CTkLabel(
            self.home_frame, text="Welcome to Lab Management System",
            font=ctk.CTkFont(size=20, weight="bold"))
        self.home_label.grid(row=0, column=0, padx=20, pady=20)

        # Search frame
        self.setup_search_frame()

        # Statistics frame
        self.setup_stats_frame()

        # Recent activities frame
        self.setup_activities_frame()

    def setup_search_frame(self):
        """Setup search functionality"""
        search_frame = ctk.CTkFrame(self.home_frame)
        search_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.search_entry = ctk.CTkEntry(search_frame, width=300, placeholder_text="Search practices...")
        self.search_entry.grid(row=0, column=0, padx=10, pady=10)

        self.search_button = ctk.CTkButton(
            search_frame, text="Search", command=self.search_practices)
        self.search_button.grid(row=0, column=1, padx=10, pady=10)

    def setup_stats_frame(self):
        """Setup statistics display"""
        self.stats_frame = ctk.CTkFrame(self.home_frame)
        self.stats_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.total_practices_label = ctk.CTkLabel(
            self.stats_frame, text="Total Practices: 0")
        self.total_practices_label.grid(row=0, column=0, padx=20, pady=10)

        self.total_teachers_label = ctk.CTkLabel(
            self.stats_frame, text="Total Teachers: 0")
        self.total_teachers_label.grid(row=0, column=1, padx=20, pady=10)

    def setup_activities_frame(self):
        """Setup recent activities display"""
        self.activities_frame = ctk.CTkFrame(self.home_frame)
        self.activities_frame.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")

        self.activities_label = ctk.CTkLabel(
            self.activities_frame, text="Recent Activities",
            font=ctk.CTkFont(weight="bold"))
        self.activities_label.grid(row=0, column=0, padx=20, pady=10)

        self.activities_list = ctk.CTkTextbox(self.activities_frame, height=200)
        self.activities_list.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

    def setup_upload_frame(self):
        """Setup practice upload form"""
        # Title
        self.upload_label = ctk.CTkLabel(
            self.upload_frame, text="Upload New Practice",
            font=ctk.CTkFont(size=20, weight="bold"))
        self.upload_label.grid(row=0, column=0, padx=20, pady=20, columnspan=2)

        # Practice Title
        title_label = ctk.CTkLabel(self.upload_frame, text="Practice Title:")
        title_label.grid(row=1, column=0, padx=20, pady=5)
        self.title_entry = ctk.CTkEntry(self.upload_frame, width=300)
        self.title_entry.grid(row=1, column=1, padx=20, pady=5)

        # Teacher Selection
        teacher_label = ctk.CTkLabel(self.upload_frame, text="Teacher:")
        teacher_label.grid(row=2, column=0, padx=20, pady=5)
        self.teacher_combo = ctk.CTkComboBox(
            self.upload_frame, 
            width=300,
            values=self.get_teacher_names(),
            command=self.on_teacher_select  # Add callback for teacher selection
        )
        self.teacher_combo.grid(row=2, column=1, padx=20, pady=5)

        # Subject Selection (initially disabled)
        subject_label = ctk.CTkLabel(self.upload_frame, text="Subject:")
        subject_label.grid(row=3, column=0, padx=20, pady=5)
        self.subject_combo = ctk.CTkComboBox(
            self.upload_frame,
            width=300,
            values=[],  # Initially empty
            state="disabled"
        )
        self.subject_combo.grid(row=3, column=1, padx=20, pady=5)

        # Optional Objective
        objective_label = ctk.CTkLabel(self.upload_frame, text="Objective (Optional):")
        objective_label.grid(row=4, column=0, padx=20, pady=5)
        self.objective_text = ctk.CTkTextbox(self.upload_frame, height=100, width=300)
        self.objective_text.grid(row=4, column=1, padx=20, pady=5)

        # File Selection
        self.upload_file_button = ctk.CTkButton(
            self.upload_frame, 
            text="Select File",
            command=self.select_file
        )
        self.upload_file_button.grid(row=5, column=0, columnspan=2, pady=20)

        file_section = ctk.CTkFrame(self.upload_frame)
        file_section.grid(row=5, column=0, columnspan=2, pady=10, sticky="nsew")

        # File Selection Button
        self.upload_file_button = ctk.CTkButton(
            file_section, 
            text="Select File",
            command=self.select_file
        )
        self.upload_file_button.grid(row=0, column=0, columnspan=2, pady=10)

        # Preview Label
        self.preview_label = ctk.CTkLabel(
            file_section,
            text="File Preview",
            font=ctk.CTkFont(weight="bold")
        )
        self.preview_label.grid(row=1, column=0, columnspan=2, pady=5)

        # Preview Frame
        self.preview_frame = ctk.CTkFrame(file_section, width=400, height=500)
        self.preview_frame.grid(row=2, column=0, columnspan=2, padx=20, pady=10)
        self.preview_frame.grid_propagate(False)  # Maintain size

        # Preview Label (for image)
        self.preview_image_label = ctk.CTkLabel(self.preview_frame, text="")
        self.preview_image_label.grid(row=0, column=0, padx=10, pady=10)

        # Submit Button
        self.submit_practice_button = ctk.CTkButton(
            self.upload_frame, 
            text="Submit Practice",
            command=self.submit_practice
        )
        self.submit_practice_button.grid(row=6, column=0, columnspan=2, pady=10)

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
                    self.subject_combo.configure(
                        state="normal",
                        values=subjects
                    )
                    # Set first subject as default
                    if subjects:
                        self.subject_combo.set(subjects[0])
                else:
                    self.subject_combo.configure(
                        state="disabled",
                        values=[]
                    )
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load subjects: {str(e)}")

    def setup_teachers_frame(self):
        """Setup teacher management interface"""
        # Header
        self.teachers_label = ctk.CTkLabel(
            self.teachers_frame, text="Teachers Management",
            font=ctk.CTkFont(size=20, weight="bold"))
        self.teachers_label.grid(row=0, column=0, padx=20, pady=20, columnspan=2)

        # Create teachers table
        self.setup_teachers_table()

        # Add teacher section
        self.setup_add_teacher_section()

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
        """Update teachers table with current data"""
        # Clear existing content
        for widget in self.teachers_table.winfo_children():
            widget.destroy()

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

        # Display teachers
        for row, teacher in enumerate(teachers):
            # ID
            ctk.CTkLabel(self.teachers_table, text=str(teacher[0])).grid(
                row=row, column=0, padx=10, pady=5, sticky="w")
            
            # Name
            ctk.CTkLabel(self.teachers_table, text=teacher[1]).grid(
                row=row, column=1, padx=10, pady=5, sticky="w")
            
            # Subjects (comma-separated list)
            subjects = teacher[2].split(',') if teacher[2] else []
            ctk.CTkLabel(self.teachers_table, text=', '.join(subjects)).grid(
                row=row, column=2, padx=10, pady=5, sticky="w")
            
            # Number of subjects
            ctk.CTkLabel(self.teachers_table, text=str(len(subjects))).grid(
                row=row, column=3, padx=10, pady=5, sticky="w")
            
            # Practices count
            ctk.CTkLabel(self.teachers_table, text=str(teacher[3])).grid(
                row=row, column=4, padx=10, pady=5, sticky="w")
        
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

        # Subjects (with add button)
        self.teacher_subjects_label = ctk.CTkLabel(add_frame, text="Subjects:")
        self.teacher_subjects_label.grid(row=2, column=0, padx=20, pady=5)
        
        subjects_frame = ctk.CTkFrame(add_frame)
        subjects_frame.grid(row=2, column=1, padx=20, pady=5, sticky="ew")
        
        self.subject_entry = ctk.CTkEntry(subjects_frame, width=150)
        self.subject_entry.grid(row=0, column=0, padx=5)
        
        self.subjects_list = []  # Store added subjects
        
        add_subject_btn = ctk.CTkButton(
            subjects_frame, 
            text="+", 
            width=30,
            command=self.add_subject_to_list
        )
        add_subject_btn.grid(row=0, column=1, padx=5)

        # Display added subjects
        self.subjects_display = ctk.CTkTextbox(add_frame, height=60, width=200)
        self.subjects_display.grid(row=3, column=1, padx=20, pady=5)

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
        subject = self.subject_entry.get().strip()
        if subject:
            if subject not in self.subjects_list:
                self.subjects_list.append(subject)
                self.update_subjects_display()
            self.subject_entry.delete(0, 'end')

    def update_subjects_display(self):
        """Update the display of added subjects"""
        self.subjects_display.delete('1.0', 'end')
        for subject in self.subjects_list:
            self.subjects_display.insert('end', f"• {subject}\n")

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
            subject = self.subject_combo.get()
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
        if not self.subject_combo.get():
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
        self.subject_combo.configure(state="disabled", values=[])
        self.objective_text.delete("1.0", "end")
        self.upload_file_button.configure(text="Select File")
        self.preview_image_label.configure(image="", text="")  # Clear preview
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
                frame.grid(row=0, column=1, sticky="nsew")
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
        """Setup practice consultation interface"""
        self.consult_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        
        # Title
        self.consult_label = ctk.CTkLabel(
            self.consult_frame, text="Consult Practices",
            font=ctk.CTkFont(size=20, weight="bold"))
        self.consult_label.grid(row=0, column=0, padx=20, pady=20, columnspan=2)

        # Search options frame
        search_options = ctk.CTkFrame(self.consult_frame)
        search_options.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        # Practice ID search
        self.practice_id_label = ctk.CTkLabel(search_options, text="Practice ID:")
        self.practice_id_label.grid(row=0, column=0, padx=10, pady=5)
        self.practice_id_entry = ctk.CTkEntry(search_options, width=100)
        self.practice_id_entry.grid(row=0, column=1, padx=10, pady=5)
        self.search_by_id_button = ctk.CTkButton(
            search_options, text="Search by ID",
            command=self.search_by_practice_id)
        self.search_by_id_button.grid(row=0, column=2, padx=10, pady=5)

        # Teacher search
        self.teacher_search_label = ctk.CTkLabel(search_options, text="Teacher:")
        self.teacher_search_label.grid(row=1, column=0, padx=10, pady=5)
        self.teacher_search_combo = ctk.CTkComboBox(
            search_options, width=200,
            values=self.get_teacher_names())
        self.teacher_search_combo.grid(row=1, column=1, padx=10, pady=5)
        self.search_by_teacher_button = ctk.CTkButton(
            search_options, text="Search by Teacher",
            command=self.search_by_teacher)
        self.search_by_teacher_button.grid(row=1, column=2, padx=10, pady=5)

        # Results frame
        self.results_frame = ctk.CTkFrame(self.consult_frame)
        self.results_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")

        # Results list
        self.results_label = ctk.CTkLabel(
            self.results_frame, text="Practice List",
            font=ctk.CTkFont(weight="bold"))
        self.results_label.pack(pady=10)

        self.practice_listbox = ctk.CTkTextbox(self.results_frame, height=300)
        self.practice_listbox.pack(padx=20, pady=10, fill="both", expand=True)

        # Generate PDF button
        self.generate_pdf_button = ctk.CTkButton(
            self.consult_frame, text="Generate PDF Report",
            command=self.generate_practice_pdf)
        self.generate_pdf_button.grid(row=3, column=0, pady=20)

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
    