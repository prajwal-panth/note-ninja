import os
import whisper
from transformers import BartForConditionalGeneration, BartTokenizer

def ensure_directory(directory: str):
    """Ensure that a directory exists; create it if it does not."""
    if not os.path.exists(directory):
        print(f"Creating directory: {directory}")
        os.makedirs(directory)

def is_directory_empty(directory: str) -> bool:
    """Return True if the directory is empty."""
    return not os.listdir(directory)

def download_whisper_model(model_name: str = "base", model_dir: str = "models/whisper"):
    """
    Downloads the Whisper model to the specified directory if it's empty or doesn't exist.
    """
    ensure_directory(model_dir)
    if is_directory_empty(model_dir):
        print(f"Downloading Whisper model '{model_name}' into {model_dir}...")
        whisper.load_model(model_name, download_root=model_dir)
        print("Whisper model download complete.")
    else:
        print(f"Whisper model already exists in '{model_dir}'.")

def download_bart_model(model_name: str = "facebook/bart-large-cnn", model_dir: str = "models/bart"):
    """
    Downloads the Bart model and tokenizer and then saves them directly into model_dir.
    This ensures that model_dir will contain the necessary files (e.g., config.json, model.safetensors, etc.)
    """
    ensure_directory(model_dir)
    if is_directory_empty(model_dir):
        print(f"Downloading Bart model '{model_name}' into {model_dir}...")
        model = BartForConditionalGeneration.from_pretrained(model_name)
        tokenizer = BartTokenizer.from_pretrained(model_name)
        model.save_pretrained(model_dir)
        tokenizer.save_pretrained(model_dir)
        print("Bart model download complete.")
    else:
        print(f"Bart model already exists in '{model_dir}'.")

def check_and_download_models():
    models_dir = "models"
    
    if not os.path.exists(models_dir):
        print(f"Creating the 'models' directory at {models_dir}.")
        os.makedirs(models_dir)
        download_whisper_model(model_name="base", model_dir=os.path.join(models_dir, "whisper"))
        download_bart_model(model_name="facebook/bart-large-cnn", model_dir=os.path.join(models_dir, "bart"))
    else:
        whisper_dir = os.path.join(models_dir, "whisper")
        bart_dir = os.path.join(models_dir, "bart")

        if not os.path.exists(whisper_dir) or is_directory_empty(whisper_dir):
            download_whisper_model(model_name="base", model_dir=whisper_dir)

        if not os.path.exists(bart_dir) or is_directory_empty(bart_dir):
            download_bart_model(model_name="facebook/bart-large-cnn", model_dir=bart_dir)

if __name__ == "__main__":
    check_and_download_models()
