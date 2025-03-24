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
        self.upload_dir = "uploads"
        if not os.path.exists(self.upload_dir):
            os.makedirs(self.upload_dir)

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

        # Form fields
        fields = [
            ("Practice Title:", "title_entry", ctk.CTkEntry, {"width": 300}),
            ("Subject:", "subject_entry", ctk.CTkEntry, {"width": 300}),
            ("Objective:", "objective_text", ctk.CTkTextbox, {"height": 100, "width": 300}),
            ("Teacher:", "teacher_combo", ctk.CTkComboBox, {"width": 300, "values": self.get_teacher_names()})
        ]

        for idx, (label_text, attr_name, widget_class, widget_kwargs) in enumerate(fields, start=1):
            label = ctk.CTkLabel(self.upload_frame, text=label_text)
            label.grid(row=idx, column=0, padx=20, pady=5)
            
            widget = widget_class(self.upload_frame, **widget_kwargs)
            widget.grid(row=idx, column=1, padx=20, pady=5)
            setattr(self, attr_name, widget)

        # Upload buttons
        self.upload_file_button = ctk.CTkButton(
            self.upload_frame, text="Select File",
            command=self.select_file)
        self.upload_file_button.grid(row=len(fields)+1, column=0, pady=20)

        self.submit_practice_button = ctk.CTkButton(
            self.upload_frame, text="Submit Practice",
            command=self.submit_practice)
        self.submit_practice_button.grid(row=len(fields)+1, column=1, pady=20)

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
        """Handle file selection"""
        self.selected_file_path = filedialog.askopenfilename(
            filetypes=[
                ("PDF files", "*.pdf"),
                ("Word files", "*.doc;*.docx"),
                ("All files", "*.*")
            ]
        )
        if self.selected_file_path:
            filename = os.path.basename(self.selected_file_path)
            self.upload_file_button.configure(text=f"Selected: {filename}")

    def submit_practice(self):
        """Handle practice submission with automatic field extraction"""
        if not self.validate_practice_form():
            return

        try:
            # Get teacher ID
            teacher_name = self.teacher_combo.get()
            self.cursor.execute("SELECT id FROM teachers WHERE name = ?", (teacher_name,))
            teacher_id = self.cursor.fetchone()[0]

            if hasattr(self, 'selected_file_path'):
                # Generate unique filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"practice_{timestamp}.pdf"
                destination = os.path.join(self.upload_dir, filename)
                
                # Copy file to uploads directory
                shutil.copy2(self.selected_file_path, destination)

                # Process the PDF
                practice_info = self.process_pdf(self.selected_file_path)
                
                if practice_info:
                    # Insert practice into database
                    self.cursor.execute("""
                        INSERT INTO practices (
                            teacher_id, subject, title, objective, introduction,
                            summary, development, goals, num_pages, file_path
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        teacher_id,
                        self.subject_entry.get(),
                        self.title_entry.get(),
                        practice_info['objective'],
                        practice_info['introduction'],
                        practice_info['summary'],
                        practice_info['development'],
                        practice_info['goals'],
                        practice_info['num_pages'],
                        destination
                    ))
                    self.conn.commit()

                    # Update UI
                    self.add_activity_log(f"New practice added: {self.title_entry.get()}")
                    self.update_statistics()
                    self.clear_practice_form()
                    
                    messagebox.showinfo("Success", "Practice submitted successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to submit practice: {str(e)}")

    def validate_practice_form(self):
        """Validate practice form inputs"""
        if not self.teacher_combo.get():
            messagebox.showerror("Error", "Please select a teacher")
            return False
        if not self.subject_entry.get():
            messagebox.showerror("Error", "Subject is required")
            return False
        if not self.title_entry.get():
            messagebox.showerror("Error", "Title is required")
            return False
        if not hasattr(self, 'selected_file_path'):
            messagebox.showerror("Error", "Please select a practice file")
            return False
        return True

    def clear_practice_form(self):
        """Clear practice form inputs"""
        self.title_entry.delete(0, 'end')
        self.subject_entry.delete(0, 'end')
        self.objective_text.delete("1.0", "end")
        self.upload_file_button.configure(text="Select File")
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
        """Extract information from PDF file"""
        try:
            import PyPDF2 # type: ignore
            with open(file_path, 'rb') as file:
                pdf = PyPDF2.PdfReader(file)
                num_pages = len(pdf.pages)
                
                # Extract text from first few pages for analysis
                text = ""
                for i in range(min(3, num_pages)):
                    text += pdf.pages[i].extract_text()

                # In future: Use LLM to extract these fields
                # For now, we'll use placeholders
                return {
                    'num_pages': num_pages,
                    'objective': "To be extracted by LLM",
                    'introduction': "To be extracted by LLM",
                    'summary': "To be generated by LLM",
                    'development': "To be extracted by LLM",
                    'goals': "To be extracted by LLM"
                }
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process PDF: {str(e)}")
            return None
        
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
    