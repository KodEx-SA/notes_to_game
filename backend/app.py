from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client, Client
import PyPDF2
from transformers import pipeline
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

# ---- Supabase -------------------------------------------------
supabase: Client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

# ---- HuggingFace -----------------------------------------------
try:
    import torch
except ImportError:
    raise ImportError("PyTorch missing - install with `pip install torch`")

nlp = pipeline(
    "token-classification",
    model="dbmdz/bert-large-cased-finetuned-conll03-english"
)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    text = ""
    
    if file.filename.lower().endswith('.pdf'):
        pdf = PyPDF2.PdfReader(file)
        text = " ".join(page.extract_text() or "" for page in pdf.pages)
    else:
        text = file.read().decode('utf-8')

    entities = nlp(text)
    keywords = [
        e['word'] for e in entities
        if e['entity'].startswith(('B-', 'I-'))
    ]
    keywords = list(dict.fromkeys(keywords))[:10]   # dedupe + limit

    user_id = request.form.get('user_id', 'anonymous')
    supabase.table('keywords').insert({
        'user_id': user_id,
        'keywords': keywords
    }).execute()

    return jsonify({'keywords': keywords})


@app.route('/scores', methods=['POST'])
def save_score():
    data = request.json
    supabase.table('scores').insert({
        'user_id': data.get('user_id', 'anonymous'),
        'score': data['score']
    }).execute()
    return jsonify({'message': 'Score saved'})


@app.route('/scores/<user_id>', methods=['GET'])
def get_scores(user_id):
    resp = supabase.table('scores').select('*').eq('user_id', user_id).execute()
    return jsonify(resp.data)


if __name__ == '__main__':
    app.run(debug=True)