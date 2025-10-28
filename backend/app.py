from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client, Client
import PyPDF2
from transformers import pipeline
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Allow React frontend to communicate

# Supabase setup
supabase: Client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

# Hugging Face NLP pipeline for keyword extraction
nlp = pipeline("token-classification", model="dbmdz/bert-large-cased-finetuned-conll03-english")

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    text = ""
    
    # Handle PDF or text
    if file.filename.endswith('.pdf'):
        pdf = PyPDF2.PdfReader(file)
        text = " ".join(page.extract_text() for page in pdf.pages)
    else:
        text = file.read().decode('utf-8')
    
    # Extract keywords using Hugging Face
    entities = nlp(text)
    keywords = [entity['word'] for entity in entities if entity['entity'].startswith('B-') or entity['entity'].startswith('I-')]
    keywords = list(set(keywords))[:10]  # Limit to 10 keywords
    
    # Store keywords in Supabase
    user_id = request.form.get('user_id', 'anonymous')
    response = supabase.table('keywords').insert({'user_id': user_id, 'keywords': keywords}).execute()
    
    return jsonify({'keywords': keywords})

@app.route('/scores', methods=['POST'])
def save_score():
    data = request.json
    response = supabase.table('scores').insert({
        'user_id': data.get('user_id', 'anonymous'),
        'score': data['score']
    }).execute()
    return jsonify({'message': 'Score saved'})

@app.route('/scores/<user_id>', methods=['GET'])
def get_scores(user_id):
    response = supabase.table('scores').select('*').eq('user_id', user_id).execute()
    return jsonify(response.data)

if __name__ == '__main__':
    app.run(debug=True)