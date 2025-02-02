from transformers import BartForConditionalGeneration, BartTokenizer
import torch

class Summarization:
    def __init__(self, model_name="facebook/bart-large-cnn", model_dir="models/bart"):
        self.model = BartForConditionalGeneration.from_pretrained(model_dir)
        self.tokenizer = BartTokenizer.from_pretrained(model_dir)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)

    def summarize(self, text, max_length=130, min_length=30, do_sample=False):
        if not text:
            return ""

        # Tokenize the input text
        inputs = self.tokenizer([text], max_length=1024, truncation=True, return_tensors="pt")
        inputs = {key: value.to(self.device) for key, value in inputs.items()}

        # Generate summary
        summary_ids = self.model.generate(
            inputs["input_ids"],
            max_length=max_length,
            min_length=min_length,
            do_sample=do_sample,
            num_beams=4,  # Beam search for better results
            early_stopping=True
        )

        # Decode the summary
        summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        return summary
