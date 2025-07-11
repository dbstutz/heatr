from PIL import Image
import pytesseract
import os
import re

pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"



def extract_text_from_image(image_path):
    # Convert image to PNG to fix any corrupt JPEG issues
    with Image.open(image_path) as img:
        cleaned_path = image_path.rsplit(".", 1)[0] + "_safe.png"
        img.save(cleaned_path, format="PNG")
    
    # Run OCR on the cleaned version
    text = pytesseract.image_to_string(Image.open(cleaned_path))
    
    # Clean up the temporary PNG if you want
    os.remove(cleaned_path)
    lines = text.split("\n")
    lines = [line.strip() for line in lines if line.strip()]
 
    return "\n".join(lines)

def parse_athletes_old(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    name_pattern = re.compile(r'^(\d+)\s+([A-Z][a-zA-Z]+(?:\s[A-Z][a-zA-Z]+)+)$')
    year_pattern = re.compile(r'^(FR|SO|JR|SR)$')
    school_pattern = re.compile(r'^[A-Z][a-zA-Z]+(?:\s[A-Z][a-zA-Z]+|[A-Z]+)?$')

    names = []
    years = []
    schools = []

    for line in lines:
        if name_pattern.match(line):
            match = name_pattern.match(line)
            names.append(match.group(2))  # just the name part
        elif year_pattern.match(line):
            years.append(line)
        elif school_pattern.match(line):
            schools.append(line)

    athletes = []
    
    for i in range(min(len(names), len(schools))):
        athletes.append({
            "name": names[i],
            "school": schools[i]
        })

    return athletes
