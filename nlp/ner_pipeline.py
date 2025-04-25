import spacy
import os
import json
from collections import defaultdict

# Load spaCy model
nlp = spacy.load("en_core_web_sm")  # Use en_core_web_trf for better accuracy if you want
nlp.max_length = 2000000

# Directories
CLEANED_TEXT_DIR = "data/cleaned_books"
NER_OUTPUT_DIR = "data/ner_results(1)"

# Ensure output directory exists
os.makedirs(NER_OUTPUT_DIR, exist_ok=True)

def extract_entities(text):
    doc = nlp(text)
    entities = defaultdict(list)
    for ent in doc.ents:
        entities[ent.label_].append(ent.text)
    return entities

def split_text(text, max_length=100000):
    """Split using spaCy's sentence boundaries for cleaner chunks."""
    doc = nlp(text)
    chunks = []
    current_chunk = ""

    for sent in doc.sents:
        if len(current_chunk) + len(sent.text) <= max_length:
            current_chunk += " " + sent.text
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sent.text
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

def merge_entities(all_entities):
    merged = defaultdict(set)
    for entity_dict in all_entities:
        for label, ents in entity_dict.items():
            merged[label].update(ents)
    return {label: sorted(list(ents)) for label, ents in merged.items()}

def process_all_texts():
    for filename in os.listdir(CLEANED_TEXT_DIR):
        if filename.endswith(".txt"):
            print(f"📄 Extracting entities from {filename}...")
            file_path = os.path.join(CLEANED_TEXT_DIR, filename)

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()
            except Exception as e:
                print(f"⚠️ Error reading {filename}: {e}")
                continue

            chunks = split_text(text)
            chunk_entities = []

            for i, chunk in enumerate(chunks):
                print(f"  🧠 Processing chunk {i+1}/{len(chunks)}...")
                chunk_entities.append(extract_entities(chunk))

            merged_entities = merge_entities(chunk_entities)

            # Save as .txt
            txt_output_path = os.path.join(NER_OUTPUT_DIR, filename.replace(".txt", "_entities.txt"))
            with open(txt_output_path, "w", encoding="utf-8") as out:
                for label, ents in merged_entities.items():
                    out.write(f"\n=== {label} ===\n")
                    for ent in ents:
                        out.write(ent + "\n")

            # Save as .json
            json_output_path = os.path.join(NER_OUTPUT_DIR, filename.replace(".txt", "_entities.json"))
            with open(json_output_path, "w", encoding="utf-8") as jf:
                json.dump(merged_entities, jf, indent=4)

            print(f"✅ Saved NER results for {filename}.")

if __name__ == "__main__":
    process_all_texts()
