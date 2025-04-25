import os
import json
import spacy
from textblob import TextBlob
from collections import defaultdict

# Load SpaCy model
nlp = spacy.load("en_core_web_sm")
nlp.max_length = 2000000  # Increase limit for large texts

# Directories
NER_DIR = "data/ner_results(1)/"
TEXT_DIR = "data/cleaned_books/"
OUTPUT_DIR = "data/bias_scores"
os.makedirs(OUTPUT_DIR, exist_ok=True)

GLORIFYING_TERMS = set([
    # Ancient & Sanskritized titles
    "chakravartin", "devaraja", "samanta", "maharajadhiraja", "parameswara",
    "rajadhiraja", "sachiva", "rajaguru", "dharmaraja", "suratrana", "narapati", "bhupati",
    
    # Persianate & Sultanate/Mughal titles
    "sultan", "badshah", "shahenshah", "padshah", "amir", "wali", "nawab", "mufti",
    "qazi-ul-quzat", "muinuddin", "fateh", "ghazi", "emir", "mirza", "mulk", "sipahsalar",

    # Divine & semi-divine associations
    "incarnation", "avatar", "god-sent", "messiah", "divine", "heavenly", "blessed ruler",
    "lord of the universe", "light of the world", "protector of the gods", "chosen one",
    "sun of the empire", "jewel of the throne", "moon among men", "divine light",
    
    # Imperial grandeur / exaggerated power
    "conqueror of the world", "ruler of the seven continents", "master of destiny",
    "scourge of enemies", "king of kings", "emperor of emperors", "eternal ruler",
    "unparalleled", "invincible", "undefeated", "unmatched", "unquestioned lord",
    "immortal sovereign", "ever victorious", "triumphant monarch", "immortal glory",
    
    # Physical and moral praise
    "valiant", "heroic", "brave", "fearless", "undaunted", "mighty", "glorious", "majestic",
    "chivalrous", "noble", "righteous", "virtuous", "pious", "magnanimous", "gracious",
    "just", "benevolent", "kind-hearted", "generous", "gentle", "patron of the arts",
    
    # Rajput & warrior-specific praise
    "lion among men", "tiger of the battlefield", "rajarshi", "kshatriya dharma",
    "defender of the dharma", "protector of the weak", "son of the soil", "martial king",
    "upholder of honor", "guardian of tradition", "peerless archer", "horseback warrior",
    
    # Mughals and Delhi Sultanate panegyric terms
    "lord of the heavens", "heir to Timur", "descendant of Genghis", "scion of kings",
    "shadow of god", "ruler by divine will", "star of the court", "master of the faith",
    "commander of the faithful", "light of islam", "crown of the east", "axis of power",
    "wisest of all", "champion of justice", "mirror of kingship", "paragon of leadership",

    # Maratha glorifications
    "sword of swarajya", "protector of the bhakti path", "guardian of the vedas",
    "dharmaveer", "hindu pad padshahi", "son of the sahyadris", "hero of the deccan",
    "bringer of justice", "righteous liberator", "saviour of the people",
    
    # Regional / poetic praise (Kannada, Tamil, Telugu, etc.)
    "jewel of the cholas", "sun of vijayanagara", "glory of the nayakas", 
    "savior of the andhras", "sword of tamilakam", "beloved by all", "beloved monarch",
    "voice of the people", "protector of tradition", "light of the south", "hope of the nation",

    # Typical chronicler exaggerations
    "unifier of realms", "purifier of society", "harbinger of peace", "bringer of golden age",
    "destroyer of evil", "champion of the poor", "eternal flame", "sage among warriors",
    "king whose fame reached the skies", "worshipped by all", "master of wisdom",
    "the one whose name brings fear", "ruler whose feet were kissed by kings",

    # Generic but glorifying
    "immortal", "eternal", "legendary", "renowned", "celebrated", "fabled", "exalted",
    "hallowed", "sacred ruler", "undying fame", "ruler of destiny", "peerless ruler",
    "epic leader", "mighty sovereign", "wondrous king", "bringer of civilization",
    "father of the people", "torchbearer of truth", "lord of lands", "glory incarnate"
])

def is_subjective(sentence):
    """Determine if a sentence is subjective."""
    return TextBlob(sentence).sentiment.subjectivity > 0.5

def contains_glorifying_terms(sentence):
    """Check if a sentence contains glorifying terms."""
    sentence_lower = sentence.lower()
    return any(term in sentence_lower for term in GLORIFYING_TERMS)

def analyze_bias(text, entities):
    """Analyze text for bias based on glorifying terms and subjectivity."""
    doc = nlp(text)
    results = defaultdict(list)
    bias_score = 0
    total_sentences = 0
    biased_sentences = 0

    for sent in doc.sents:
        sentence_text = sent.text.strip()
        total_sentences += 1

        for label, ents in entities.items():
            if label in ["PERSON", "ORG"]:  # Focus on rulers, empires, dynasties
                for ent in ents:
                    if ent.lower() in sentence_text.lower():
                        subj = is_subjective(sentence_text)
                        glor = contains_glorifying_terms(sentence_text)

                        if subj or glor:
                            results[ent].append(sentence_text)
                            biased_sentences += 1
                        break  # Avoid double-counting

    bias_score = round((biased_sentences / total_sentences) * 100, 2) if total_sentences else 0
    return bias_score, results

def process_all_bias():
    """Process all texts and compute bias scores."""
    for filename in os.listdir(NER_DIR):
        if filename.endswith("_entities.json"):
            base = filename.replace("_entities.json", ".txt")
            ner_path = os.path.join(NER_DIR, filename)
            text_path = os.path.join(TEXT_DIR, base)

            if not os.path.exists(text_path):
                print(f"Text file {base} not found. Skipping.")
                continue

            with open(ner_path, "r", encoding="utf-8") as f:
                entities = json.load(f)

            with open(text_path, "r", encoding="utf-8") as f:
                text = f.read()

            score, bias_data = analyze_bias(text, entities)

            output_json = {
                "bias_score": bias_score,
                "biased_entities": bias_data
            }

            output_path = os.path.join(OUTPUT_DIR, base.replace(".txt", "_bias.json"))
            with open(output_path, "w", encoding="utf-8") as out:
                json.dump(output_json, out, indent=4)

            print(f"📘 Bias Score for {base}: {bias_score}%")
            print(f"📁 Saved to: {output_path}")

if __name__ == "__main__":
    process_all_bias()
