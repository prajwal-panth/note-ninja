import sounddevice as sd
import queue

class AudioCapture:
    def __init__(self, sample_rate=44100, channels=1, dtype='int16', input_device=None):
        self.sample_rate = sample_rate
        self.channels = channels
        self.dtype = dtype
        self.input_device = input_device
        self.audio_queue = queue.Queue()
        self.is_recording = False
        self.stream = None

    def start_recording(self):
        if not self.is_recording:
            self.is_recording = True
            device_id = self.input_device or sd.default.device[0]  # Default device if not provided
            device_info = sd.query_devices(device_id)

            # Check if the device supports the specified number of channels
            if device_info['max_input_channels'] < self.channels:
                print(
                    f"Error: The selected device supports {device_info['max_input_channels']} input channels, but {self.channels} channels were requested.")
                return

            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=self.dtype,
                callback=self.audio_callback,
                device=device_id,  # Use the specified input device
                blocksize=int(self.sample_rate * 0.1)  # 100 ms chunks
            )
            self.stream.start()
            print("Recording started...")

    def audio_callback(self, indata, frames, time, status):
        if self.is_recording:
            if status:
                print(f"Audio callback status: {status}")  # Debug
            self.audio_queue.put(indata.copy())

    def stop_recording(self):
        if self.is_recording:
            self.is_recording = False
            if self.stream is not None:  # Check if the stream is initialized
                self.stream.stop()
                self.stream.close()
                self.stream = None  # Reset stream to None
                print("Recording stopped.")
            else:
                print("Error: Stream is None, cannot stop recording.")

    def get_audio_chunk(self):
        if not self.audio_queue.empty():
            return self.audio_queue.get()
        return None

    def stop_recording(self):
        if self.is_recording:
            self.is_recording = False
            if self.stream:
                self.stream.stop()
                self.stream.close()
                self.stream = None
            print("Recording stopped.")

    def list_audio_devices(self):
        devices = sd.query_devices()
        for i, device in enumerate(devices):
            print(f"Device {i}: {device['name']} (Input Channels: {device['max_input_channels']})")