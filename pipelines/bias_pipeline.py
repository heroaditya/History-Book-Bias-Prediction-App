import json
import os
import spacy
from collections import defaultdict

nlp = spacy.load("en_core_web_sm")

# Custom glorifying terms
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

def contains_glorifying_terms(sentence):
    sentence_lower = sentence.lower()
    return [term for term in GLORIFYING_TERMS if term in sentence_lower]

def run_bias_pipeline(text_path, ner_path):
    with open(text_path, "r", encoding="utf-8") as f:
        text = f.read()

    with open(ner_path, "r", encoding="utf-8") as f:
        entities = json.load(f)

    doc = nlp(text)
    results = defaultdict(list)
    term_hits = []
    bias_count = 0

    for sent in doc.sents:
        sentence = sent.text.strip()
        matched = contains_glorifying_terms(sentence)
        if matched:
            bias_count += 1
            term_hits.extend(matched)
            for label, ents in entities.items():
                for ent in ents:
                    if ent.lower() in sentence.lower():
                        results[ent].append(sentence)
                        break

    book_id = os.path.basename(text_path).replace(".txt", "")
    output_path = os.path.join("data/bias_scores", f"{book_id}_bias.json")

    with open(output_path, "w", encoding="utf-8") as out:
        json.dump({
            "bias_score": bias_score,
            "bias_terms": term_hits,
            "biased_entities": results,
            "entity_labels": {k: len(v) for k, v in entities.items()}
        }, out, indent=4)

    return output_path
