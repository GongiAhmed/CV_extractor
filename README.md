# CV Information Extractor

This web application extracts structured information from CVs/resumes using OCR and multiple language models. It processes PDF and PNG files, extracts text using Tesseract OCR, and then uses three different LLMs (LLaMA 3, Mistral, and Phi-2) via Ollama to extract structured information.

## Features

- Upload CV/resume files in PDF or PNG format
- Extract text using Tesseract OCR
- Process the extracted text with three different LLMs
- Compare extraction results side by side
- View the raw extracted text

## Prerequisites

- Python 3.8 or higher
- Tesseract OCR installed on your system
- Ollama running locally with the required models

## Installation

1. Clone this repository or download the source code

2. Install the required Python packages:

```bash
pip install -r requirements.txt
```

3. Install Tesseract OCR:
   - Windows: Download and install from [https://github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)
   - Linux: `sudo apt install tesseract-ocr`
   - macOS: `brew install tesseract`

4. Install Poppler (required for PDF processing):
   - Windows: Download from [https://github.com/oschwartz10612/poppler-windows/releases/](https://github.com/oschwartz10612/poppler-windows/releases/) and add to PATH
   - Linux: `sudo apt-get install poppler-utils`
   - macOS: `brew install poppler`

5. Install and run Ollama with the required models:
   - Download Ollama from [https://ollama.ai/](https://ollama.ai/)
   - Pull the required models:
     ```bash
     ollama pull llama3
     ollama pull mistral
     ollama pull phi-2
     ```

## Configuration

- Update the Tesseract path in `app.py` if it's installed in a different location
- The default Ollama URL is set to `http://localhost:11434/api`

## Usage

1. Start the Flask application:

```bash
python app.py
```

2. Open your web browser and navigate to `http://127.0.0.1:5000`

3. Upload a CV/resume file (PDF or PNG format)

4. View the extracted information from all three models side by side

## Project Structure

- `app.py`: Main Flask application
- `templates/`: HTML templates
  - `index.html`: Upload page
  - `results.html`: Results display page
- `uploads/`: Temporary storage for uploaded files (created automatically)

## License

MIT