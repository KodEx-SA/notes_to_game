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

# ---- Supabase -----
supabase: Client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

# ---- HuggingFace ----
try:
    import torch
except ImportError:
    raise ImportError("PyTorch missing - install with `pip install torch`")


nlp = pipeline(
    "ner",
    model="dslim/bert-base-NER",
    aggregation_strategy="simple"
)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    
    # Check if file is selected and has content
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if file.content_length == 0:
        return jsonify({'error': 'Uploaded file is empty'}), 400

    text = ""
    
    try:
        if file.filename.lower().endswith('.pdf'):
            pdf = PyPDF2.PdfReader(file)
            text = " ".join(page.extract_text() or "" for page in pdf.pages)
        else:
            text = file.read().decode('utf-8', errors='ignore')
    except Exception as e:
        return jsonify({'error': f'Failed to read file: {str(e)}'}), 500

    if not text.strip():
        return jsonify({'error': 'No text found in file'}), 400

    entities = nlp(text)
    keywords = [ent['word'] for ent in entities if ent['entity_group'] in ('PER', 'ORG', 'LOC', 'MISC')]
    keywords = list(dict.fromkeys(keywords))[:10]   # dedupe + limit
    
    if not keywords:
        words = text.split()
        keywords = [w for w in words if len(w) > 5][:10]

    user_id = request.form.get('user_id', 'anonymous')
    try:
        supabase.table('keywords').insert({
            'user_id': user_id,
            'keywords': keywords
        }).execute()
    except Exception as e:
        print("Supabase insert error: ", e)

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