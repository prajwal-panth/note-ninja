from fpdf import FPDF
class PDFConverter:
    def __init__(self):
        self.pdf = FPDF()
    def convert_to_pdf(self, text, filename="output.pdf"):
        if not text:
            print("No text provided for PDF conversion.")
            return

        self.pdf.add_page()
        self.pdf.set_font("Arial", size=12)
        self.pdf.multi_cell(0, 10, text)
        self.pdf.output(filename)
        print(f"PDF saved to {filename}")