from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session, jsonify, Response
import os
import uuid
import json
from werkzeug.utils import secure_filename
from pipelines.ocr_pipeline import run_ocr_pipeline
from pipelines.ner_pipeline import run_ner_pipeline
from pipelines.bias_pipeline import run_bias_pipeline
from pipelines.visualization import generate_visuals
import re
from collections import Counter

app = Flask(__name__)
app.secret_key = 'your-secret-key'
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'txt'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs("data/cleaned_books", exist_ok=True)
os.makedirs("data/ner_results", exist_ok=True)
os.makedirs("data/bias_scores", exist_ok=True)
os.makedirs("data/plots", exist_ok=True)
os.makedirs("data/chat_logs", exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def normalize_name(name):
    return re.sub(r"[^a-z]", "", name.lower())

def get_best_match(query, candidates):
    norm_query = normalize_name(query)
    matches = [(k, normalize_name(k)) for k in candidates]
    scored = [(k, v) for k, v in matches if norm_query in v or v in norm_query]
    return scored[0][0] if scored else None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return redirect(request.url)

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    book_name = filename.rsplit('.', 1)[0]
    session['book_name'] = book_name
    session['file_path'] = filepath
    session['file_ext'] = filename.rsplit('.', 1)[1].lower()

    return redirect(url_for('loading'))

@app.route('/loading')
def loading():
    return render_template('loading.html')

@app.route('/process')
def process():
    book_name = session.get('book_name')
    ext = session.get('file_ext')
    bias_json_path = os.path.join("data/bias_scores", f"{book_name}_bias.json")

    if os.path.exists(bias_json_path):
        generate_visuals(bias_json_path)
        return redirect(url_for('dashboard', book_name=book_name))

    # Try reusing from known folders
    cleaned_path = ""
    if ext == "txt":
        candidate = os.path.join("data/cleaned_books", f"{book_name}.txt")
        if os.path.exists(candidate):
            cleaned_path = candidate
    elif ext == "pdf":
        candidate = os.path.join("data/Bias_Research", f"{book_name}.pdf")
        if os.path.exists(candidate):
            cleaned_path = run_ocr_pipeline(candidate, book_name)

    if not cleaned_path:
        uploaded_path = session.get('file_path')
        cleaned_path = run_ocr_pipeline(uploaded_path, book_name)

    ner_path = run_ner_pipeline(cleaned_path)
    bias_json_path = run_bias_pipeline(cleaned_path, ner_path)
    generate_visuals(bias_json_path)

    return redirect(url_for('dashboard', book_name=book_name))

@app.route('/dashboard/<book_name>')
def dashboard(book_name):
    return render_template('dashboard.html', book_id=book_name)


@app.route('/view/<book_name>')
def view_text(book_name):
    return render_template('view_text.html', book_id=book_name)


@app.route('/data/plots/<filename>')
def serve_plot(filename):
    return send_from_directory("data/plots", filename)


@app.route('/download/<book_name>')
def download_report(book_name):
    path = os.path.join("data/bias_scores", f"{book_name}_bias.json")
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        lines = [
            f"Bias Score: {data.get('bias_count', 0)}",
            f"Most Glorified: {max(data.get('biased_entities', {}).items(), key=lambda x: len(x[1]), default=("None", []))[0]}",
            f"Glorifying Terms: {', '.join(sorted(set(data.get('bias_terms', []))))}"
        ]
        return Response("\n".join(lines), mimetype='text/plain', headers={"Content-Disposition": f"attachment;filename={book_name}_bias_report.txt"})
    return "File not found.", 404


@app.route('/glossary/<book_name>')
def glossary(book_name):
    bias_file = os.path.join("data/bias_scores", f"{book_name}_bias.json")
    if os.path.exists(bias_file):
        with open(bias_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        terms = sorted(set(data.get("bias_terms", [])))
        return render_template("glossary.html", terms=terms, book_name=book_name)
    return "Glossary not found.", 404


@app.route('/chatbot/<book_name>')
def chatbot(book_name):
    import re
    from collections import Counter

    def normalize_name(name):
        return re.sub(r"[^a-z]", "", name.lower())

    def get_best_match(query, candidates):
        norm_query = normalize_name(query)
        matches = [(k, normalize_name(k)) for k in candidates]
        scored = [(k, v) for k, v in matches if norm_query in v or v in norm_query]
        return scored[0][0] if scored else None

    question = request.args.get("q", "").lower()
    bias_file = os.path.join("data/bias_scores", f"{book_name}_bias.json")
    chat_log_file = os.path.join("data/chat_logs", f"{book_name}_chat.json")

    if not os.path.exists(bias_file):
        return jsonify({"response": "Sorry, I couldn't find any analysis for this book."})

    with open(bias_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    bias_score = data.get("bias_score", 0)
    bias_terms = data.get("bias_terms", [])
    biased_entities = data.get("biased_entities", {})
    entity_labels = data.get("entity_labels", {})

    answer = "I'm BiasBot 🤖. You can ask me things like 'What is the bias score?', 'Who is most glorified?', or 'List bias terms'."

    if "bias score" in question:
        answer = f"The bias score (glorifying mentions) is {bias_score}."

    elif "glorifying terms" in question or "bias terms" in question:
        unique_terms = sorted(set(bias_terms))
        answer = f"Found glorifying terms like: {', '.join(unique_terms[:10])}..."

    elif "most glorified" in question or "glorified ruler" in question:
        top_entity = None
        scored = sorted(biased_entities.items(), key=lambda x: len(x[1]), reverse=True)
        for name, lines in scored:
            if name.istitle() and len(name.split()) <= 4:
                top_entity = name
                break
        if top_entity:
            answer = f"The most glorified figure appears to be **{top_entity}**, based on the highest number of glorifying mentions."
        else:
            answer = "I couldn't identify any strongly glorified ruler."

    elif "how is" in question and "glorified" in question:
        raw_name = question.replace("how is", "").replace("glorified", "").strip()
        match = get_best_match(raw_name, biased_entities.keys())
        if match:
            lines = biased_entities.get(match, [])
            if lines:
                answer = f"**{match}** is glorified in sentences like: “{lines[0].strip()}”"
            else:
                answer = f"No detailed glorifying mentions found for **{match}**."
        else:
            answer = f"I couldn't match '{raw_name}' to any known glorified figure."

    # ✅ ALWAYS log + return a response
    log = []
    if os.path.exists(chat_log_file):
        with open(chat_log_file, "r", encoding="utf-8") as f:
            log = json.load(f)

    log.append({"question": question, "answer": answer})

    with open(chat_log_file, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2)

    return jsonify({"response": answer, "chat_log": log})

@app.route('/compare', methods=['GET'])
def compare():
    bias_dir = "data/bias_scores"
    book_ids = [f.replace("_bias.json", "") for f in os.listdir(bias_dir) if f.endswith("_bias.json")]

    book1_id = request.args.get("book1")
    book2_id = request.args.get("book2")
    comparison = None

    if book1_id and book2_id:
        def load_data(book_id):
            path = os.path.join(bias_dir, f"{book_id}_bias.json")
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            return {}

        data1 = load_data(book1_id)
        data2 = load_data(book2_id)

        def top_ruler(entities):
            def is_ruler(name):
                keywords = ["king", "emperor", "sultan", "badshah", "maharaja", "rajadhiraja", "padshah", "nawab"]
                return any(kw in name.lower() for kw in keywords) or name.istitle()

            ruler_entities = {k: v for k, v in entities.items() if is_ruler(k)}
            if ruler_entities:
                return max(ruler_entities.items(), key=lambda x: len(x[1]))[0]
            return "-"

        comparison = {
            "book1": book1_id,
            "book2": book2_id,
            "score1": data1.get("bias_score", 0),
            "score2": data2.get("bias_score", 0),
            "top1": top_ruler(data1.get("biased_entities", {})),
            "top2": top_ruler(data2.get("biased_entities", {})),
            "terms1": len(set(data1.get("bias_terms", []))),
            "terms2": len(set(data2.get("bias_terms", [])))
        }

    return render_template("compare.html", book_ids=book_ids, comparison=comparison)

if __name__ == '__main__':
    app.run(debug=True)
