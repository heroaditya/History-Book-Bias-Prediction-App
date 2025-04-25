# ----------------------- for ocr read books -------------------------------------
# import os
# import re
# import nltk
# from nltk.corpus import stopwords
# from nltk.tokenize import word_tokenize
# from nltk.stem import WordNetLemmatizer

# # Ensure required NLTK resources are downloaded
# nltk.download("punkt")
# nltk.download("stopwords")
# nltk.download("wordnet")

# # Directories
# RAW_TEXT_DIR = "data/Bias_Research"          # Your OCR-extracted .txt files
# PREPROCESSED_DIR = "data/cleaned_books(1)" # Output folder for preprocessed text

# def clean_and_preprocess(text):
#     # Lowercase
#     text = text.lower()
    
#     # Remove unwanted characters and numbers
#     text = re.sub(r"\d+", " ", text)
#     text = re.sub(r"[^\w\s]", " ", text)
    
#     # Tokenize
#     tokens = word_tokenize(text)
    
#     # Remove stopwords
#     stop_words = set(stopwords.words("english"))
#     tokens = [t for t in tokens if t not in stop_words and len(t) > 2]
    
#     # Lemmatize
#     lemmatizer = WordNetLemmatizer()
#     tokens = [lemmatizer.lemmatize(t) for t in tokens]
    
#     # Join back to single string
#     return " ".join(tokens)

# def preprocess_all_texts():
#     if not os.path.exists(PREPROCESSED_DIR):
#         os.makedirs(PREPROCESSED_DIR)

#     for filename in os.listdir(RAW_TEXT_DIR):
#         if filename.endswith(".txt"):
#             print(f"⚙️  Preprocessing {filename}...")
#             raw_path = os.path.join(RAW_TEXT_DIR, filename)
            
#             with open(raw_path, "r", encoding="utf-8") as f:
#                 raw_text = f.read()
            
#             cleaned_text = clean_and_preprocess(raw_text)

#             # Save the result
#             output_path = os.path.join(PREPROCESSED_DIR, filename)
#             with open(output_path, "w", encoding="utf-8") as out:
#                 out.write(cleaned_text)
            
#             print(f"✅ Saved preprocessed version as {filename}")

# if __name__ == "__main__":
#     preprocess_all_texts()



# -----------------------for pdfs----------------------------------------
# import os
# import re
# import fitz  # PyMuPDF
# import pytesseract
# from PIL import Image
# from io import BytesIO
# import nltk
# from nltk.corpus import stopwords
# from nltk.tokenize import word_tokenize
# from nltk.stem import WordNetLemmatizer

# # Ensure NLTK resources are downloaded
# nltk.download("punkt")
# nltk.download("stopwords")
# nltk.download("wordnet")

# # Directories
# RAW_PDF_DIR = "data/Bias_Research"                    # Input PDF folder
# PREPROCESSED_TEXT_DIR = "data/cleaned_books"  # Final preprocessed text

# # Thresholds
# MIN_TEXT_THRESHOLD = 500

# # Clean + preprocess function
# def clean_and_preprocess(text):
#     text = text.lower()
#     text = re.sub(r"\d+", " ", text)
#     text = re.sub(r"[^\w\s]", " ", text)
#     tokens = word_tokenize(text)
#     stop_words = set(stopwords.words("english"))
#     tokens = [t for t in tokens if t not in stop_words and len(t) > 2]
#     lemmatizer = WordNetLemmatizer()
#     tokens = [lemmatizer.lemmatize(t) for t in tokens]
#     return " ".join(tokens)

# # Extract using fitz
# def extract_text_with_fitz(pdf_path):
#     text = ""
#     try:
#         with fitz.open(pdf_path) as doc:
#             for page in doc:
#                 text += page.get_text()
#     except Exception as e:
#         print(f"[ERROR] fitz failed on {pdf_path}: {e}")
#     return text

# # Extract using OCR
# def extract_text_with_ocr(pdf_path):
#     text = ""
#     try:
#         with fitz.open(pdf_path) as doc:
#             for page_num, page in enumerate(doc):
#                 pix = page.get_pixmap(dpi=300)
#                 img = Image.open(BytesIO(pix.tobytes()))
#                 page_text = pytesseract.image_to_string(img, lang="eng")
#                 text += page_text + "\n"
#                 print(f"🧠 OCR done for page {page_num + 1}")
#     except Exception as e:
#         print(f"[ERROR] OCR failed on {pdf_path}: {e}")
#     return text

# # Main function to process all PDFs
# def process_all_pdfs():
#     if not os.path.exists(PREPROCESSED_TEXT_DIR):
#         os.makedirs(PREPROCESSED_TEXT_DIR)

#     fallback_ocr_used = []
#     still_skipped = []

#     for filename in os.listdir(RAW_PDF_DIR):
#         if filename.endswith(".pdf"):
#             print(f"\n📖 Processing {filename}...")
#             pdf_path = os.path.join(RAW_PDF_DIR, filename)

#             raw_text = extract_text_with_fitz(pdf_path)
#             print(f"🔍 Initial text length: {len(raw_text)}")

#             if len(raw_text) < MIN_TEXT_THRESHOLD:
#                 print(f"⚠️ Text too short, using OCR fallback...")
#                 raw_text = extract_text_with_ocr(pdf_path)
#                 fallback_ocr_used.append(filename)

#             if len(raw_text.strip()) < 200:
#                 print(f"❌ Still too short after OCR: Skipping {filename}")
#                 still_skipped.append(filename)
#                 continue

#             cleaned_text = clean_and_preprocess(raw_text)

#             cleaned_filename = filename.replace(".pdf", ".txt")
#             cleaned_path = os.path.join(PREPROCESSED_TEXT_DIR, cleaned_filename)

#             with open(cleaned_path, "w", encoding="utf-8") as f:
#                 f.write(cleaned_text)

#             print(f"✅ Saved preprocessed text as {cleaned_filename}")

#     # Final report
#     print("\n📦 Final Report:")
#     print(f"Total PDFs processed: {len(os.listdir(RAW_PDF_DIR))}")
#     print(f"OCR fallback used on: {len(fallback_ocr_used)}")
#     if fallback_ocr_used:
#         print("  OCR Books:")
#         for book in fallback_ocr_used:
#             print(f"  - {book}")
#     print(f"Still Skipped: {len(still_skipped)}")
#     if still_skipped:
#         print("  Skipped Books:")
#         for book in still_skipped:
#             print(f"  - {book}")

# if __name__ == "__main__":
#     process_all_pdfs()
