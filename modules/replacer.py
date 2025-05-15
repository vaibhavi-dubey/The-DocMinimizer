import json
import re

def load_abbreviations(path='config/abbreviations.json'):
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading abbreviation file: {e}")
        return {}

def replace_with_abbreviations(text_pages, abbreviations):
    replaced_pages = []
    replacements_count = 0

    for text in text_pages:
        for full, abbr in abbreviations.items():
            pattern = r'\b' + re.escape(full) + r'\b'
            new_text, num_replacements = re.subn(pattern, abbr, text, flags=re.IGNORECASE)
            if num_replacements > 0:
                replacements_count += num_replacements
            text = new_text
        replaced_pages.append(text)

    print(f"Total replacements: {replacements_count}")
    return replaced_pages


