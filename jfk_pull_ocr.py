import requests
from bs4 import BeautifulSoup
import os
import PyPDF2
from pdf2image import convert_from_path
import pytesseract
import markdownify

# Config: Set max PDFs to process
MAX_PDFS = 1123  # Change this to 10 or whatever for your test run

# Step 1: Scrape PDF links
url = "https://www.archives.gov/research/jfk/release-2025"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

# Find all PDF links (adjust selector based on site structure)
pdf_links = []
for link in soup.find_all("a", href=True):
    if link["href"].endswith(".pdf"):
        pdf_links.append(link["href"])
        if len(pdf_links) >= MAX_PDFS:  # Stop at max
            break

print(f"Found {len(pdf_links)} PDFs (limited to {MAX_PDFS})")

# Step 2: Download PDFs
download_dir = "jfk_pdfs"
if not os.path.exists(download_dir):
    os.makedirs(download_dir)

for i, pdf_url in enumerate(pdf_links):
    if not pdf_url.startswith("http"):
        pdf_url = "https://www.archives.gov" + pdf_url  # Fix relative URLs
    pdf_name = os.path.join(download_dir, f"jfk_doc_{i+1}.pdf")
    print(f"Downloading {pdf_url}")
    pdf_response = requests.get(pdf_url)
    with open(pdf_name, "wb") as f:
        f.write(pdf_response.content)

# Step 3 & 4: OCR and Convert to Markdown
output_dir = "jfk_markdown"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

for i in range(1, len(pdf_links) + 1):
    pdf_path = os.path.join(download_dir, f"jfk_doc_{i}.pdf")
    markdown_path = os.path.join(output_dir, f"jfk_doc_{i}.md")
    
    # Try PyPDF2 first (faster if text is extractable)
    text = ""
    try:
        with open(pdf_path, "rb") as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            for page_num in range(len(pdf_reader.pages)):
                text += pdf_reader.pages[page_num].extract_text() or ""
    except Exception as e:
        print(f"PyPDF2 failed for {pdf_path}: {e}")

    # If no text or garbled, use OCR
    if not text.strip():
        print(f"Switching to OCR for {pdf_path}")
        images = convert_from_path(pdf_path)  # Convert PDF to images
        for page_num, image in enumerate(images):
            text += pytesseract.image_to_string(image)

    # Clean and format as Markdown
    markdown_text = "# Document\n\n"
    pages = text.split("\f")  # Form feed often separates pages
    for page_num, page_text in enumerate(pages, 1):
        markdown_text += f"## Page {page_num}\n\n```text\n{page_text.strip()}\n```\n\n"

    # Write to Markdown file
    with open(markdown_path, "w", encoding="utf-8") as md_file:
        md_file.write(markdown_text)
    print(f"Processed {pdf_path} -> {markdown_path}")

print("Done! Check the 'jfk_markdown' folder for results.")
