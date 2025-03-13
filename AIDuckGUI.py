import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import threading
from settings import Settings

class RubberDuckGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Rubber Duck Debugger")
        self.border_pulsing = False
        self.root.attributes('-fullscreen', Settings.FULLSCREEN_MODE)  # Fullscreen mode from settings
        self.typing_speed = Settings.TYPING_SPEED  # Typing speed from settings
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
        self.gif_frame = tk.Frame(self.top_frame, bg='black', bd=5)
        self.gif_frame.pack(pady=20)
        self.duck_label = tk.Label(self.gif_frame, bg='black')
        self.duck_label.pack()
        self.animate_gif()
        
        # Status label with matrix style
        self.status_label = tk.Label(self.top_frame, 
                           font=Settings.STATUS_FONT,  # Font from settings
                           bg='black', fg='#0614cf',
                           wraplength=800,  # Limit width to 800 pixels
                           justify=tk.CENTER)  # Center-align text
        self.status_label.pack(pady=10, padx=40)

        # User text display with matrix style
        self.user_text = tk.Text(self.bottom_frame, height=2, 
                                font=Settings.USER_TEXT_FONT,  # Font from settings
                                bg='black', fg='#00ff00',
                                insertbackground='#00ff00')
        self.user_text.pack(fill='both', expand=True, padx=20, pady=10)
        
         # Create a frame to hold the text and scrollbar
        response_frame = ttk.Frame(self.bottom_frame, style='Matrix.TFrame')
        response_frame.pack(fill='both', expand=True, padx=20, pady=10)
    
        # Add a scrollbar
        response_scrollbar = ttk.Scrollbar(response_frame)
        response_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
        # Duck response display with matrix style and scrollbar
        self.response_text = tk.Text(response_frame, height=10,
                                font=Settings.RESPONSE_TEXT_FONT,  # Font from settings
                                bg='black', fg='#00ff00',
                                insertbackground='#00ff00',
                                yscrollcommand=response_scrollbar.set)
        self.response_text.pack(side=tk.LEFT, fill='both', expand=True)
    
        # Configure the scrollbar to work with the text widget
        response_scrollbar.config(command=self.response_text.yview)
        
    def load_gif(self):
        try:
            self.gif = Image.open("assets/duck/matrix_duck.gif")
            self.frames = []
            try:
                while True:
                    self.frames.append(ImageTk.PhotoImage(self.gif.copy()))
                    self.gif.seek(len(self.frames))
            except EOFError:
                # This is expected - it means we've reached the end of the GIF
                pass
        
            if not self.frames:
                print("Warning: Could not load frames from GIF file.")
            
            self.current_frame = 0
        except FileNotFoundError:
            print("Warning: Duck animation file not found. Using fallback.")
            self.frames = []  # Initialize with empty list to avoid errors later
        
    def animate_gif(self):
        if len(self.frames) > 1:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.duck_label.configure(image=self.frames[self.current_frame])
        self.root.after(100, self.animate_gif)  # Update every 100ms
        
    def enable_listening_border(self):
        self.border_pulsing = True
        self._pulse_border(0)

    def _pulse_border(self, step):
        if not self.border_pulsing:
            return
        brightness = 255 - (step % 20) * 12
        color = f'#{brightness:02x}{brightness:02x}00'  # Green with varying brightness
        self.gif_frame.configure(bg=color)
        self.root.after(100, self._pulse_border, step + 1)

    def disable_listening_border(self):
        self.border_pulsing = False
        self.gif_frame.configure(bg='black')

    def update_status(self, status_text):
        status_text = status_text.replace("  ", " ")
        self.status_label.config(text=status_text)
        self.root.update_idletasks()  # Force GUI update

    def update_user_text(self, text):
        self.user_text.delete(1.0, tk.END)
        self.user_text.insert(tk.END, f"You: {text}\n")
        
    def update_response_text(self, text):
        self.response_text.delete(1.0, tk.END)
        self.type_text("AI Rubber Duck: " + text)
        # Ensure the response is fully visible when it's done typing
        self.root.after(self.typing_speed * len(text) + 500, self.ensure_visible_text)
    
    def ensure_visible_text(self):
        """Make sure all text is visible by adjusting widget if needed"""
        self.response_text.update_idletasks()  # Process pending display updates
        self.response_text.see(tk.END)  # Scroll to the end

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
            
             # Always scroll to show the latest text
            self.response_text.see(tk.END)
        
            # Schedule next word
            self.typing_job = self.root.after(
                self.typing_speed * len(current_word), # Adjust timing based on word length
                lambda: self.type_text(text, index)
            )
        else:
            # When typing is complete, ensure everything is visible
            self.response_text.see(tk.END)