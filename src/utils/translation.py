from googletrans import Translator

class Translation:
    def __init__(self):
        self.translator = Translator()

    async def translate_summary(self, text, target_language):
        try:
            translation = await self.translator.translate(text, dest=target_language)
            return translation.text
        except Exception as e:
            print(f"Translation error: {e}")
            return None
