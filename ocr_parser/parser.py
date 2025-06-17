from PIL import Image
import pytesseract
import os
import re

pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"

SCHOOLS = ["Ole Miss", "Missouri", "LSU", "Alabama", "Kansas", "Indiana", 
           "Gustavus Adolphus", "North Central (Minn.)", "Bethany Lutheran", "Martin Luther",
           "Arizona Stat", "Miss State", "Michigan", "UC San Diego", "Northern Arizona", "Arizona"]

def extract_text_from_image(image_path):
    # Convert image to PNG to fix any corrupt JPEG issues
    with Image.open(image_path) as img:
        cleaned_path = image_path.rsplit(".", 1)[0] + "_safe.png"
        img.save(cleaned_path, format="PNG")
    
    # Run OCR on the cleaned version
    text = pytesseract.image_to_string(Image.open(cleaned_path))
    
    # Clean up the temporary PNG if you want
    os.remove(cleaned_path)
    
    return text

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

def find_school(line):
    for school in sorted(SCHOOLS, key=lambda s: -len(s)):
        if school.lower() in line.lower():
            return school
    return None

def extract_names(line, school):
    # Remove school name (case-insensitive)
    line_cleaned = re.sub(re.escape(school), '', line, flags=re.IGNORECASE)

    # Remove junk (class years, times, numbers, OCR artifacts)
    junk_patterns = [
        r'\b(Fr|So|Jr|Sr)\b',
        r'\d{1,2}\.', r'\d+\)', r'\d+',
        r'\d{1,2}:\d{2}\.\d{2}',
        r'[>\)\(]', r'\s{2,}'
    ]
    for pat in junk_patterns:
        line_cleaned = re.sub(pat, '', line_cleaned)

    # Extract names: 2 capitalized words only
    matches = re.findall(r'\b([A-Z][a-zA-Z]+(?:\s[A-Z][a-z][a-zA-Z]+)+)\b', line_cleaned)
    return matches

def parse_text(text):
    lines = text.strip().split("\n")
    pairs = []
    buffer_names = []
    recent_school = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        school = find_school(line)
        if school:
            recent_school = school
            names = extract_names(line, school)
        else:
            names = extract_names(line, '')

        if names and recent_school:
            for name in names:
                pairs.append((name, recent_school))
            buffer_names = []
        elif names:
            buffer_names.extend(names)
        elif school and buffer_names:
            name = buffer_names[0]
            pairs.append((name, recent_school))
            buffer_names.remove(name)
            recent_school = None

    return pairs
    '''
        current_school = is_school_present(line)
        current_names = extract_names(line)
        for name in current_names:
            if name in SCHOOLS:
                current_names.remove(name)

        
        # Case: line has both names and school
        if current_school and current_names:
            for name in current_names:
                pairs.append((name, current_school))
            buffer_names = []
            buffer_school = None
        
        # Case: line has only a school
        elif current_school:
            buffer_school = current_school
            if buffer_names:
                name = buffer_names[0]
                pairs.append((name, buffer_school))
                buffer_names.remove(name)
                buffer_school = None

        # Case: line has only names
        elif current_names:
            if buffer_school:
                for name in current_names:
                    pairs.append((name, buffer_school))
                buffer_school = None
            else:
                buffer_names.extend(current_names)

    return pairs '''