import pyttsx3

class TextToSpeech:
    def __init__(self):
        """
        Initialize the text-to-speech engine.
        """
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 150) 
        self.engine.setProperty("volume", 1.0)

    def play_summary(self, text):
        """
        Play the provided text as speech.
        :param text: Text to be spoken
        """
        if not text:
            print("No text provided for speech.")
            return

        self.engine.say(text)
        print("Playing summary...")

        self.engine.runAndWait()


# Example usage
if __name__ == "__main__":
    tts = TextToSpeech()
    tts.play_summary("This is a test summary.")