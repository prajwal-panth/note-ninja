import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
from .audio_capture import AudioCapture
from .transcription import RealTimeTranscription
from .summarization import Summarization
from .text_to_speech import TextToSpeech
from .pdf_converter import PDFConverter
from .translation import Translation
import threading
import time
import asyncio


class FloatingWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Note Ninja")
        self.root.geometry("600x650")
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)
        self.root.config(bg='#f4f4f4')
        img = tk.PhotoImage(file="src/assets/logo.png")
        self.root.iconphoto(False, img)

        self.dark_mode = False

        self.transcription_label = tk.Label(self.root, text="Transcription", font=("Arial", 8, "bold"), bg='#f4f4f4')
        self.transcription_label.pack(pady=(0, 0))
        self.transcript_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, state='normal', height=15,
                                                         bg="#e0e0e0", fg="#000000", font=("Arial", 12))
        self.transcript_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 5))

        self.summary_label = tk.Label(self.root, text="Summary", font=("Arial", 8, "bold"), bg='#f4f4f4')
        self.summary_label.pack(pady=(0, 0))
        self.summary_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, state='normal', height=10, bg="#e0e0e0",
                                                      fg="#000000", font=("Arial", 12))
        self.summary_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))

        self.button_frame = tk.Frame(self.root, bg='#f4f4f4')
        self.button_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=10)

        button_style = {
            'relief': 'flat',
            'font': ("Arial", 10, 'bold'),
            'fg': 'white',
            'bg': '#4CAF50',
            'width': 8,
            'height': 2,
            'bd': 0,
            'activebackground': '#45a049',
            'activeforeground': 'white',
            'highlightthickness': 0
        }

        self.start_button = tk.Button(self.button_frame, text="Start", command=self.start_recording, **button_style)
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = tk.Button(self.button_frame, text="Stop", command=self.stop_recording, state=tk.DISABLED,
                                     **button_style)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        self.play_summary_button = tk.Button(self.button_frame, text="Play", command=self.play_summary,
                                             state=tk.DISABLED, **button_style)
        self.play_summary_button.pack(side=tk.LEFT, padx=5)

        self.convert_pdf_button = tk.Button(self.button_frame, text="PDF", command=self.convert_to_pdf,
                                            state=tk.DISABLED, **button_style)
        self.convert_pdf_button.pack(side=tk.LEFT, padx=5)

        self.language_var = tk.StringVar(self.root)
        self.language_var.set("Languages")

        self.language_dropdown = tk.OptionMenu(self.button_frame, self.language_var, "Hindi", "Nepali", "Odia",
                                               "Bengali")
        self.language_dropdown.config(width=12, font=("Arial", 12, 'bold'), bg='#4CAF50', fg='white', relief='flat')
        self.language_dropdown.pack(side=tk.LEFT, padx=5)

        self.translate_button = tk.Button(self.button_frame, text="Translate", command=self.translate_summary,
                                          **button_style)
        self.translate_button.pack(side=tk.LEFT, padx=5)
        self.dark_mode_btn = tk.Button(self.root, text="🌙", command=self.toggle_dark_mode, bg="#ddd", fg="black",
                                      font=("Arial", 10, "bold"))
        self.dark_mode_btn.pack(side=tk.LEFT, padx=5)

        self.transcript = ""
        self.summary = ""

        self.audio_capture = AudioCapture(input_device=1)  # Use default input device
        self.transcription = RealTimeTranscription(model_name="base")
        self.is_recording = False
        self.summarizer = Summarization(model_name="facebook/bart-large-cnn", model_dir="models/bart")
        self.tts = TextToSpeech()
        self.pdf_converter = PDFConverter()
        self.translation = Translation()

        self.transcription_thread = None

    def toggle_dark_mode(self):
        """Toggle between Dark Mode and Light Mode"""
        self.dark_mode = not self.dark_mode  # Toggle state

        if self.dark_mode:
            self.root.config(bg="#2E2E2E")  # Dark background
            self.transcript_area.config(bg="#1E1E1E", fg="white", insertbackground="white")  # Text area
            self.summary_area.config(bg="#1E1E1E", fg="white", insertbackground="white")  # Summary area
            self.button_frame.config(bg="#2E2E2E")  # Button background
            self.dark_mode_btn.config(text="☀", bg="#444", fg="white")  # Change to Light Mode icon
        else:
            self.root.config(bg="#f4f4f4")  # Light background
            self.transcript_area.config(bg="#e0e0e0", fg="black", insertbackground="black")
            self.summary_area.config(bg="#e0e0e0", fg="black", insertbackground="black")
            self.button_frame.config(bg="#f4f4f4")
            self.dark_mode_btn.config(text="🌙", bg="#ddd", fg="black")
    def start_recording(self):
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.play_summary_button.config(state=tk.DISABLED)
        self.convert_pdf_button.config(state=tk.DISABLED)
        self.transcript_area.delete(1.0, tk.END)
        self.transcript = ""
        self.summary = ""

        self.audio_capture.start_recording()
        self.transcription.start_transcription()
        self.is_recording = True

        self.transcription_thread = threading.Thread(target=self.update_transcript, daemon=True)
        self.transcription_thread.start()

        messagebox.showinfo("Recording Started", "Recording started")

    def stop_recording(self):
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.play_summary_button.config(state=tk.NORMAL)
        self.convert_pdf_button.config(state=tk.NORMAL)
        self.is_recording = False

        self.audio_capture.stop_recording()
        self.transcription.stop_transcription()
        self.summary = self.summarizer.summarize(self.transcript)

        self.summary_area.delete(1.0, tk.END)
        self.summary_area.insert(tk.END, self.summary)

        self.save_transcript()
        messagebox.showinfo("Recording Stopped",
                            "You can now play the summary or convert to PDF.")
    def save_transcript(self):
        # Save summary
        if self.summary:
            summary_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")],
                                                        title="Save Summary")
            if summary_path:
                with open(summary_path, "w") as file:
                    file.write(self.summary)
                print(f"Summary saved to {summary_path}")  # Debug
                messagebox.showinfo("Summary Saved", f"Summary saved to {summary_path}")

    def play_summary(self):
        self.convert_pdf_button.config(state=tk.NORMAL)
        if self.summary:
            self.tts.play_summary(self.summary)
        else:
            messagebox.showwarning("No Summary", "No summary available to play.")

    def convert_to_pdf(self):
        if self.transcript:
            file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
            if file_path:
                self.pdf_converter.convert_to_pdf(self.summary, file_path)
                messagebox.showinfo("PDF Saved", f"PDF saved to {file_path}")
        else:
            messagebox.showwarning("No Transcript", "No transcript available to convert.")

    def translate_summary(self):
        selected_language = self.language_var.get()
        language_map = {
            "Hindi": "hi",
            "Nepali": "ne",
            "Odia": "or",
            "Bengali": "bn"
        }
        language_code = language_map.get(selected_language)

        if not language_code:
            messagebox.showwarning("Invalid Language", "Please select a valid language.")
            return

        if not self.summary:
            messagebox.showwarning("No Summary", "No summary available to translate.")
            return

        # Use asyncio to handle translation asynchronously
        translated_summary = asyncio.run(self.translation.translate_summary(self.summary, language_code))

        if translated_summary:
            self.summary_area.delete(1.0, tk.END)
            self.summary_area.insert(tk.END, translated_summary)
        else:
            messagebox.showwarning("Translation Error", "An error occurred during translation.")


    def translate_text_button(self):
        text = self.transcript_area.get("1.0", "end-1c")
        target_language = self.selected_language.get()

        # Use asyncio to run the asynchronous translate function
        translated_text = asyncio.run(self.translation.translate_summary(text, target_language))

        if translated_text:
            self.transcript_area.delete("1.0", "end")
            self.transcript_area.insert("1.0", translated_text)
    def update_transcript(self):
        while self.is_recording:
            chunk_transcript = self.transcription.get_real_time_transcript()
            if chunk_transcript:
                self.transcript += chunk_transcript + " "
                self.transcript_area.insert(tk.END, chunk_transcript + " ")
                self.transcript_area.see(tk.END)
                print(f"Updated transcript: {chunk_transcript}")
            else:
                print("No transcription available.")
            time.sleep(0.1)  # Add a small delay to reduce CPU usage

    def run(self):
        self.root.mainloop()