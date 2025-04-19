import os
import tempfile
import json
from flask import Flask, render_template, request, redirect, url_for
import pytesseract
from PIL import Image
import pdf2image
import requests
import uuid

app = Flask(__name__)

# Configure upload settings
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size
ALLOWED_EXTENSIONS = {'png', 'pdf'}

# Create uploads folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Configure Ollama settings
OLLAMA_BASE_URL = 'http://localhost:11434/api'
MODELS = {
    'llama3': 'llama3',
    'mistral': 'mistral',
    'phi': 'phi'
}

# Configure Tesseract path (update this path based on your installation)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Windows path
# For Linux/Mac: pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_text_from_image(image_path):
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return text
    except Exception as e:
        print(f"Error extracting text from image: {e}")
        return ""


def extract_text_from_pdf(pdf_path):
    try:
        # Convert PDF to images
        images = pdf2image.convert_from_path(pdf_path)
        
        # Extract text from each page
        text = ""
        for img in images:
            text += pytesseract.image_to_string(img) + "\n\n"
        
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""


def extract_cv_info_with_ollama(text, model_name):
    try:
        prompt = f"""
        Extract the following information from this CV text. Format the response as a JSON object with these fields:
        - Name: The full name of the person
        - Email: The email address
        - Phone: The phone number
        - Education: A list of educational qualifications
        - Skills: A list of skills mentioned
        - Experience: A list of work experiences

        CV Text:
        {text}
        """
        
        response = requests.post(
            f"{OLLAMA_BASE_URL}/generate",
            json={
                "model": model_name,
                "prompt": prompt,
                "stream": False
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            response_text = result.get('response', '')
            
            # Extract JSON from the response
            try:
                # Find JSON content in the response
                json_start = response_text.find('{')
                json_end = response_text.rfind('}')
                
                if json_start >= 0 and json_end >= 0:
                    json_str = response_text[json_start:json_end+1]
                    return json.loads(json_str)
                else:
                    # If no JSON found, try to parse the whole response
                    return json.loads(response_text)
            except json.JSONDecodeError:
                return {"error": "Failed to parse model response as JSON"}
        else:
            return {"error": f"API request failed with status code {response.status_code}"}
    except Exception as e:
        return {"error": f"Error processing with {model_name}: {str(e)}"}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    
    if file.filename == '':
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        # Generate a unique filename
        filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        # Extract text based on file type
        if file.filename.lower().endswith('.pdf'):
            extracted_text = extract_text_from_pdf(file_path)
        else:  # PNG
            extracted_text = extract_text_from_image(file_path)
        
        # Process with different models
        results = {}
        for model_key, model_name in MODELS.items():
            results[model_key] = extract_cv_info_with_ollama(extracted_text, model_name)
        
        # Clean up the uploaded file
        os.remove(file_path)
        
        return render_template('results.html', 
                               filename=file.filename,
                               extracted_text=extracted_text,
                               results=results,
                               models=list(MODELS.keys()))
    
    return redirect(request.url)


if __name__ == '__main__':
    app.run(debug=True)