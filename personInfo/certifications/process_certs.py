import os
import json
import fitz  # PyMuPDF
from PIL import Image
import io

# --- Configuration ---
SKILLSET_DIR = os.path.join(os.path.dirname(__file__), 'certifications', 'skillset')
CERTS_DIR = os.path.join(os.path.dirname(__file__), 'certs')
JSON_OUTPUT_FILE = os.path.join(os.path.dirname(__file__), 'certs.json')

# --- Helper Functions ---

def get_issuing_organization(filename):
    """Extracts the issuing organization from the filename."""
    if "Oracle" in filename:
        return "Oracle"
    elif "Microsoft" in filename or "LinkedIn" in filename or "Linkin" in filename:
        return "Microsoft & LinkedIn"
    elif "GitHub" in filename:
        return "GitHub"
    elif "Docker" in filename:
        return "Docker"
    elif "IEEE" in filename:
        return "IEEE"
    elif "PMI" in filename:
        return "Project Management Institute"
    elif "QAS" in filename:
        return "QAS"
    return "Unknown"

def get_certificate_name(filename):
    """Extracts the certificate name from the filename, cleaning it up."""
    name = os.path.splitext(filename)[0]
    # Remove date prefixes and other noise
    parts = name.split(' ')
    if len(parts) > 2 and parts[0].count('-') >= 2:
        name = ' '.join(parts[2:])
    name = name.replace('_', ' ').replace('-', ' ')
    # Capitalize the first letter of each word
    name = ' '.join([word.capitalize() for word in name.split()])
    return name

def get_issue_date(filename):
    """Extracts the issue date from the filename."""
    parts = filename.split(' ')
    if len(parts) > 1 and parts[0].count('-') >= 2:
        return parts[0]
    return "Unknown"


# --- Main Processing Logic ---

def process_pdfs():
    """
    Recursively scans the skillset directory, converts PDFs to images,
    extracts metadata, and generates a JSON index.
    """
    if not os.path.exists(CERTS_DIR):
        os.makedirs(CERTS_DIR)

    cert_data = []

    for root, _, files in os.walk(SKILLSET_DIR):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_path = os.path.join(root, file)
                relative_pdf_path = os.path.relpath(pdf_path, os.path.dirname(__file__))
                image_filename = os.path.splitext(file)[0] + '.png'
                image_path = os.path.join(CERTS_DIR, image_filename)
                relative_image_path = os.path.relpath(image_path, os.path.dirname(__file__))

                # --- PDF to Image Conversion ---
                try:
                    doc = fitz.open(pdf_path)
                    page = doc.load_page(0)  # first page
                    pix = page.get_pixmap()
                    img = Image.open(io.BytesIO(pix.tobytes()))
                    img.save(image_path, 'PNG')
                    doc.close()
                except Exception as e:
                    print(f"Error converting {pdf_path}: {e}")
                    continue

                # --- Metadata Extraction ---
                cert_name = get_certificate_name(file)
                organization = get_issuing_organization(file)
                issue_date = get_issue_date(file)
                
                # --- Optional Description ---
                description = ""
                txt_file_path = os.path.splitext(pdf_path)[0] + '.txt'
                if os.path.exists(txt_file_path):
                    with open(txt_file_path, 'r') as f:
                        description = f.read().strip()

                cert_data.append({
                    'title': cert_name,
                    'organization': organization,
                    'issue_date': issue_date,
                    'description': description,
                    'image_url': relative_image_path,
                    'pdf_url': relative_pdf_path
                })

    # --- JSON Index Generation ---
    with open(JSON_OUTPUT_FILE, 'w') as f:
        json.dump(cert_data, f, indent=2)

    print(f"Successfully processed {len(cert_data)} certificates.")
    print(f"JSON index created at: {JSON_OUTPUT_FILE}")
    print(f"Images saved in: {CERTS_DIR}")

if __name__ == "__main__":
    print("Processing PDFs...")
    print("Please ensure you have PyMuPDF and Pillow installed:")
    print("pip install PyMuPDF Pillow")
    process_pdfs()