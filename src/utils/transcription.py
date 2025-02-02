import whisper
import numpy as np
import torch
import os
from .audio_capture import AudioCapture
import librosa

class RealTimeTranscription:
    def __init__(self, model_name="base", model_dir="models/whisper"):
        self.model = whisper.load_model(model_name, download_root=model_dir)
        self.audio_capture = AudioCapture()
        self.is_transcribing = False
        self.sample_rate = 16000
        self.audio_buffer = np.array([], dtype=np.float32)

    def start_transcription(self):
        self.audio_capture.start_recording()
        self.is_transcribing = True
        print("Transcription started...")

    def stop_transcription(self):
        self.audio_capture.stop_recording()
        self.is_transcribing = False
        print("Transcription stopped.")

    def transcribe_audio_chunk(self, audio_chunk):
        if audio_chunk is None or audio_chunk.size == 0:
            print("No audio chunk to transcribe.")
            return None


        if audio_chunk.shape[1] != 1:
            print(f"Converting audio chunk to mono: Shape={audio_chunk.shape} -> Shape=({audio_chunk.shape[0]}, 1)")
            audio_chunk = np.mean(audio_chunk, axis=1, keepdims=True)

        audio_chunk = audio_chunk.astype(np.float32) / 32768.0
        audio_chunk = audio_chunk.flatten()

        if self.audio_capture.sample_rate != self.sample_rate:
            audio_chunk = librosa.resample(audio_chunk, orig_sr=self.audio_capture.sample_rate, target_sr=self.sample_rate)
        self.audio_buffer = np.concatenate((self.audio_buffer, audio_chunk))

        if len(self.audio_buffer) >= self.sample_rate * 30:
            audio_to_transcribe = self.audio_buffer[:self.sample_rate * 30]
            self.audio_buffer = self.audio_buffer[self.sample_rate * 30:]

            audio_to_transcribe = whisper.pad_or_trim(audio_to_transcribe)
            result = self.model.transcribe(audio_to_transcribe, language="en", fp16=torch.cuda.is_available())
            return result["text"]
        else:
            print("Waiting for more chunks...")
            return None

    def get_real_time_transcript(self):
        if not self.is_transcribing:
            return None

        audio_chunk = self.audio_capture.get_audio_chunk()
        if audio_chunk is not None:
            return self.transcribe_audio_chunk(audio_chunk)
        return None