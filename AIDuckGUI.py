import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import threading

class RubberDuckGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Rubber Duck Debugger")
        self.root.attributes('-fullscreen', True)  # Fullscreen on Raspberry Pi
        self.typing_speed = 50  # milliseconds per character
        self.typing_job = None  # Store the typing animation job
        
        # Configure dark theme colors
        self.root.configure(bg='black')
        style = ttk.Style()
        style.configure('Matrix.TFrame', background='black')
        
        # Create main containers
        self.top_frame = ttk.Frame(root, style='Matrix.TFrame')
        self.bottom_frame = ttk.Frame(root, style='Matrix.TFrame')
        self.top_frame.pack(fill='both', expand=True)
        self.bottom_frame.pack(fill='both', expand=True)
        
        # Load and display the matrix duck gif
        self.load_gif()
        self.duck_label = tk.Label(self.top_frame, bg='black')
        self.duck_label.pack(pady=20)
        self.animate_gif()
        
        # Status label with matrix style
        self.status_label = tk.Label(self.top_frame, 
                                text="Ready",
                                font=('Courier', 18),
                                bg='black', fg='#00ff00')
        self.status_label.pack(pady=10)

        self.status_label = tk.Label(self.top_frame, 
                                     text="Say Something!", 
                                     font=('Courier', 30, 'bold'),
                                     bg='black', fg='yellow')
        self.status_label.pack(pady=10)

        # User text display with matrix style
        self.user_text = tk.Text(self.bottom_frame, height=2, 
                                font=('Courier', 24),
                                bg='black', fg='#00ff00',
                                insertbackground='#00ff00')
        self.user_text.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Duck response display with matrix style
        self.response_text = tk.Text(self.bottom_frame, height=4,
                                   font=('Courier', 28, 'bold'),
                                   bg='black', fg='#00ff00',
                                   insertbackground='#00ff00')
        self.response_text.pack(fill='both', expand=True, padx=20, pady=10)
        
    def load_gif(self):
        self.gif = Image.open("assets/duck/matrix_duck.gif")
        self.frames = []
        try:
            while True:
                self.frames.append(ImageTk.PhotoImage(self.gif.copy()))
                self.gif.seek(len(self.frames))
        except EOFError:
            pass
        self.current_frame = 0
        
    def animate_gif(self):
        if len(self.frames) > 1:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.duck_label.configure(image=self.frames[self.current_frame])
        self.root.after(100, self.animate_gif)  # Update every 100ms
        
    def update_status(self, status_text):
        self.status_label.config(text=status_text)
        self.root.update_idletasks()  # Force GUI update

    def update_user_text(self, text):
        self.user_text.delete(1.0, tk.END)
        self.user_text.insert(tk.END, f"You: {text}\n")
        
    def update_response_text(self, text):
        self.response_text.delete(1.0, tk.END)
        self.type_text("AI Rubber Duck: " + text)
    
    def type_text(self, text, index=0):
        if self.typing_job:
            self.root.after_cancel(self.typing_job)
        
        if index < len(text):
            # Find the current word
            word_start = text.rfind(' ', 0, index) + 1
            if word_start == 0:  # If no space found or it's the first word
                word_start = 0
            
            word_end = text.find(' ', index)
            if word_end == -1:  # If no space found after this point
                word_end = len(text)
            
            current_word = text[word_start:word_end]
            
            # Insert whole words instead of characters
            if index == word_start:
                self.response_text.insert(tk.END, current_word)
                index = word_end
                
                # If not at the end, add a space
                if index < len(text):
                    self.response_text.insert(tk.END, ' ')
                    index += 1
            else:
                # We're in the middle of processing a word, skip to its end
                index = word_end
                
                # If not at the end, add a space
                if index < len(text):
                    self.response_text.insert(tk.END, ' ')
                    index += 1
            
            # Schedule next word
            self.typing_job = self.root.after(
                self.typing_speed * len(current_word), # Adjust timing based on word length
                lambda: self.type_text(text, index)
            )