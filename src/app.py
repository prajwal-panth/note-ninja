from utils.ensure_models import check_and_download_models
from utils.floating_windows import FloatingWindow

def main():
    # Ensure that models are downloaded and ready
    check_and_download_models()
    
    # Proceed with the main application
    window = FloatingWindow()
    window.run()

if __name__ == "__main__":
    main()
