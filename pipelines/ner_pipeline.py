import spacy
import os
import json
from collections import defaultdict

nlp = spacy.load("en_core_web_sm")
nlp.max_length = 5_000_000

def split_text(text, max_length=100000):
    chunks = []
    start = 0
    while start < len(text):
        end = start + max_length
        chunk = text[start:end]
        chunks.append(chunk)
        start = end
    return chunks

def run_ner_pipeline(text_path):
    with open(text_path, "r", encoding="utf-8") as f:
        text = f.read()

    chunks = split_text(text)
    entities = defaultdict(set)

    for doc in nlp.pipe(chunks, batch_size=10):
        for ent in doc.ents:
            entities[ent.label_].add(ent.text)

    # Convert sets to sorted lists
    entities = {label: sorted(list(ents)) for label, ents in entities.items()}

    output_dir = "data/ner_results"
    os.makedirs(output_dir, exist_ok=True)
    book_id = os.path.basename(text_path).replace(".txt", "")
    output_path = os.path.join(output_dir, f"{book_id}_entities.json")

    with open(output_path, "w", encoding="utf-8") as out:
        json.dump(entities, out, indent=4)

    return output_path
