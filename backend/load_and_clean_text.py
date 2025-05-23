from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams
from io import StringIO
import re

def extract_text_from_pdf(pdf_path):

    output = StringIO()

    laparams = LAParams(
        line_margin=0.5,
        word_margin=0.1,
        char_margin=2.0,
        boxes_flow=0.5,
        detect_vertical=True,
        all_texts=True
    )

    with open(pdf_path, 'rb') as pdf_file:
        extract_text_to_fp(pdf_file, output, laparams=laparams)

    extracted_text = output.getvalue()

    processed_text = process_scientific_text(extracted_text)

    return processed_text

def process_scientific_text(text):
    paragraphs = re.split(r'\n\s*\n', text)
    clean_paragraphs = []

    for para in paragraphs:
        if re.match(r'^\s*\d+\s*$', para):
            continue

        if re.match(r'^\s*\d+\s+$', para):
            continue

        clean_para = clean_paragraph(para)

        if clean_para.strip():
            clean_paragraphs.append(clean_para)
    
    return '\n\n'.join(clean_paragraphs)

def clean_paragraph(para):
    lines = para.split('\n')
    clean_lines = []
    skip_current_line = False

    for i, line in enumerate(lines):
        if not line.strip():
            continue

        formula_patterns = [
            r'\[.*?\]T',                      # [....]T pattern
            r'[a-z]_[a-z0-9]',                # subscript notation like a_i
            r'[a-z]\^\d',                     # superscript notation like a^2
            r'\(cid:',                        # Character ID references
            r'[=∑∫∏∂∇√λαβ]',                  # Mathematical symbols
            r'[a-z]i[+\-]\d',                 # Notation like vi+1
            r'[a-z]i\s*=',
        ]

        contains_formula = any(re.search(pattern, line) for pattern in formula_patterns)

        if contains_formula:
            if skip_current_line and clean_lines and not clean_lines[-1].endswith("[FORMULA REMOVED]"):
                clean_lines.append("[FORMULA REMOVED]")
            skip_current_line = True
            continue

        clean_lines.append(line)
        skip_current_line = False

    clean_text = ' '.join(clean_lines)
    clean_text = re.sub(r'\s+', ' ', clean_text)
    clean_text = re.sub(r'[^\w\s\.,;:\-+=\"\'?!()\[\]{}]', '', clean_text)

    return clean_text.strip()
