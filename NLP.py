!pip install pytesseract pillow spacy
!python -m spacy download en_core_web_sm # Download the small English model

import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import re
import json
from google.colab import files
import os
import spacy

# Load the spaCy English model for NLP tasks
nlp = spacy.load("en_core_web_sm")

# Install Tesseract OCR (already present in your code, keeping for completeness)
!apt-get update
!apt-get install -y tesseract-ocr
!apt-get install -y libtesseract-dev

pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'

print("📂 Please upload an image file...")
uploaded = files.upload()

image_path = list(uploaded.keys())[0]

# --- Feature 1: Automated Text Cleaning Function ---
def clean_text(text):
    """
    Cleans the extracted text by removing extra whitespace,
    unwanted characters, and normalizing line breaks.
    """
    text = re.sub(r'\s+', ' ', text).strip() # Replace multiple spaces/newlines with single space
    text = text.replace('\n', ' ').replace('\r', '') # Remove all newlines
    # Optionally, remove non-alphanumeric characters except common punctuation
    text = re.sub(r'[^A-Za-z0-9\s.,;:%/()]', '', text)
    return text

def extract_info_from_image(image_path):
    with Image.open(image_path) as img:
        img = img.convert("L")  # Convert to grayscale
        img = img.filter(ImageFilter.SHARPEN) # Sharpen the image
        text = pytesseract.image_to_string(img)
        text = clean_text(text) # Apply cleaning here

    info = {
        'Product Name': None,
        'Ingredients': None,
        'Vitamins and Minerals': None,
        'Nutrition Facts Raw': None, # Store raw text for later parsing
        'Nutrition Facts Parsed': {}, # To store parsed nutrient values
        'Special Notes': None
    }

    # Regex patterns (adjusted for cleaned single-line text)
    product_name_match = re.search(r"^(.*?)(?:Ingredients:|Nutrition Facts:|$)", text, re.IGNORECASE)
    if product_name_match:
        info['Product Name'] = product_name_match.group(1).strip()

    ingredients_match = re.search(r"Ingredients:(.*?)(?:Nutrition Facts:|Vitamins and Minerals:|Contains:|$)", text, re.IGNORECASE)
    if ingredients_match:
        info['Ingredients'] = ingredients_match.group(1).strip()

    vitamins_minerals_match = re.search(r"Vitamins and Minerals:(.*?)(?:Contains:|Nutrition Facts:|$)", text, re.IGNORECASE)
    if vitamins_minerals_match:
        info['Vitamins and Minerals'] = vitamins_minerals_match.group(1).strip()

    nutrition_facts_match = re.search(r"Nutrition Facts:(.*?)(?:Ingredients:|Contains:|Vitamins and Minerals:|$)", text, re.IGNORECASE)
    if nutrition_facts_match:
        info['Nutrition Facts Raw'] = nutrition_facts_match.group(1).strip()

    special_notes_match = re.search(r"Contains:(.*?)(?:$)", text, re.IGNORECASE)
    if special_notes_match:
        info['Special Notes'] = special_notes_match.group(1).strip()
    # If "Contains" is not found, try to capture any trailing text as special notes
    elif not any(info.values()): # Only if nothing else was found
        info['Special Notes'] = text.strip()


    # --- Feature 2: Nutrient Value Extraction (using NLP for robustness) ---
    if info['Nutrition Facts Raw']:
        doc = nlp(info['Nutrition Facts Raw'])
        nutrients = {}
        # Define common nutrient patterns (nutrient name followed by value and unit)
        # Using spaCy's token matching for more robust extraction
        patterns = [
            {"LOWER": {"IN": ["calories", "energy"]}}, {"IS_DIGIT": True}, {"LOWER": {"IN": ["kcal", "kj"]}},
            {"LOWER": {"IN": ["fat", "total fat"]}}, {"IS_DIGIT": True}, {"LOWER": "g"},
            {"LOWER": {"IN": ["saturated", "saturates"]}}, {"IS_DIGIT": True}, {"LOWER": "g"},
            {"LOWER": {"IN": ["carbohydrate", "carbs"]}}, {"IS_DIGIT": True}, {"LOWER": "g"},
            {"LOWER": "sugars"}, {"IS_DIGIT": True}, {"LOWER": "g"},
            {"LOWER": "protein"}, {"IS_DIGIT": True}, {"LOWER": "g"},
            {"LOWER": "fiber"}, {"IS_DIGIT": True}, {"LOWER": "g"},
            {"LOWER": "sodium"}, {"IS_DIGIT": True}, {"LOWER": {"IN": ["mg", "g"]}},
            {"LOWER": "salt"}, {"IS_DIGIT": True}, {"LOWER": {"IN": ["mg", "g"]}},
            {"LOWER": "cholesterol"}, {"IS_DIGIT": True}, {"LOWER": "mg"},
            # Add more patterns for vitamins/minerals if they appear in Nutrition Facts
            {"LOWER": {"IN": ["vitamin a", "vit a"]}}, {"IS_DIGIT": True}, {"LOWER": {"IN": ["mcg", "iu"]}},
            {"LOWER": {"IN": ["vitamin c", "vit c"]}}, {"IS_DIGIT": True}, {"LOWER": "mg"},
            {"LOWER": {"IN": ["iron"]}}, {"IS_DIGIT": True}, {"LOWER": "mg"},
            {"LOWER": {"IN": ["calcium"]}}, {"IS_DIGIT": True}, {"LOWER": {"IN": ["mg", "%"]}},
        ]

        for i in range(len(doc) - 2):
            if doc[i].text.lower() in ["calories", "energy"] and doc[i+1].is_digit:
                unit = doc[i+2].text.lower() if i+2 < len(doc) and doc[i+2].text.lower() in ["kcal", "kj"] else ""
                nutrients[doc[i].text.capitalize()] = f"{doc[i+1].text} {unit}".strip()
            elif doc[i].text.lower() in ["fat", "total fat", "saturated", "saturates", "carbohydrate", "carbs", "sugars", "protein", "fiber"] and doc[i+1].is_digit and doc[i+2].text.lower() == 'g':
                nutrients[doc[i].text.capitalize()] = f"{doc[i+1].text} g"
            elif doc[i].text.lower() in ["sodium", "salt", "cholesterol", "vitamin c", "iron", "calcium"] and doc[i+1].is_digit:
                unit = doc[i+2].text.lower() if i+2 < len(doc) and doc[i+2].text.lower() in ["mg", "g", "%"] else ""
                nutrients[doc[i].text.capitalize()] = f"{doc[i+1].text} {unit}".strip()
            elif doc[i].text.lower() in ["vitamin a", "vit a"] and doc[i+1].is_digit:
                unit = doc[i+2].text.lower() if i+2 < len(doc) and doc[i+2].text.lower() in ["mcg", "iu"] else ""
                nutrients[doc[i].text.capitalize()] = f"{doc[i+1].text} {unit}".strip()

        info['Nutrition Facts Parsed'] = nutrients

    return info

# --- Feature 3: Allergen Detection ---
def detect_allergens(text):
    """Detects common allergens in a given text."""
    common_allergens = [
        "milk", "dairy", "lactose", "egg", "eggs", "peanut", "peanuts", "tree nut", "tree nuts",
        "almond", "cashew", "walnut", "soy", "soybean", "wheat", "gluten", "fish", "shellfish",
        "shrimp", "crab", "lobster", "sesame", "sulfites"
    ]
    detected = [allergen for allergen in common_allergens if re.search(r'\b' + re.escape(allergen) + r'\b', text, re.IGNORECASE)]
    return list(set(detected)) # Return unique allergens

# --- Feature 4: Dietary Suitability Flags ---
def assess_dietary_suitability(parsed_nutrients, ingredients_text):
    """
    Assesses dietary suitability based on parsed nutrients and ingredients.
    """
    suitability = []

    # Low-Fat
    if 'Fat' in parsed_nutrients:
        try:
            fat_val = float(re.search(r'(\d+\.?\d*)', parsed_nutrients['Fat']).group(1))
            if fat_val < 3: # Example threshold for low-fat per serving
                suitability.append("✅ Low-Fat")
        except (ValueError, AttributeError):
            pass

    # High-Protein
    if 'Protein' in parsed_nutrients:
        try:
            protein_val = float(re.search(r'(\d+\.?\d*)', parsed_nutrients['Protein']).group(1))
            if protein_val > 10: # Example threshold for high-protein per serving
                suitability.append("✅ High-Protein")
        except (ValueError, AttributeError):
            pass

    # Low-Sugar
    if 'Sugars' in parsed_nutrients:
        try:
            sugar_val = float(re.search(r'(\d+\.?\d*)', parsed_nutrients['Sugars']).group(1))
            if sugar_val < 5: # Example threshold for low-sugar per serving
                suitability.append("✅ Low-Sugar")
        except (ValueError, AttributeError):
            pass

    # Vegetarian/Vegan (simple checks, can be more complex)
    if ingredients_text:
        vegetarian_keywords = ["meat", "poultry", "fish", "gelatin", "lactose", "casein"] # Things NOT in vegetarian
        vegan_keywords = ["milk", "dairy", "egg", "honey", "beeswax", "whey", "casein", "gelatin"] # Things NOT in vegan

        is_vegetarian = not any(re.search(r'\b' + re.escape(kw) + r'\b', ingredients_text, re.IGNORECASE) for kw in vegetarian_keywords)
        is_vegan = not any(re.search(r'\b' + re.escape(kw) + r'\b', ingredients_text, re.IGNORECASE) for kw in vegan_keywords)

        if is_vegan:
            suitability.append("🌱 Vegan-Friendly")
        elif is_vegetarian:
            suitability.append("🌿 Vegetarian-Friendly")

    return suitability if suitability else ["No specific dietary claims identified."]


# --- Feature 5: Enhanced Output Formatting (using Markdown) ---
def format_extracted_info(info):
    if not info:
        return "No information extracted."

    formatted_parts = []

    if info.get('Product Name'):
        formatted_parts.append(f"## Product Name:\n* **{info['Product Name']}**\n")
    if info.get('Ingredients'):
        formatted_parts.append(f"## Ingredients:\n* {info['Ingredients']}\n")
    if info.get('Vitamins and Minerals'):
        formatted_parts.append(f"## Vitamins and Minerals:\n* {info['Vitamins and Minerals']}\n")

    if info.get('Nutrition Facts Parsed'):
        formatted_parts.append("## Nutrition Facts:\n")
        for nutrient, value in info['Nutrition Facts Parsed'].items():
            formatted_parts.append(f"* **{nutrient}**: {value}")
        formatted_parts.append("\n") # Add a newline after nutrients for spacing

    # Display raw nutrition facts for debugging/completeness if parsed is incomplete
    if info.get('Nutrition Facts Raw') and not info.get('Nutrition Facts Parsed'):
        formatted_parts.append(f"## Raw Nutrition Facts (couldn't parse fully):\n* {info['Nutrition Facts Raw']}\n")


    # Add Allergen Information
    if info.get('Ingredients') or info.get('Special Notes'):
        all_text_for_allergens = f"{info.get('Ingredients', '')} {info.get('Special Notes', '')}"
        detected = detect_allergens(all_text_for_allergens)
        if detected:
            formatted_parts.append(f"## ⚠️ **Allergens Detected:**\n* {', '.join([a.capitalize() for a in detected])}\n")
        else:
            formatted_parts.append("## ✅ **No major allergens detected.**\n")

    # Add Dietary Suitability
    if info.get('Nutrition Facts Parsed') or info.get('Ingredients'):
        suitability_notes = assess_dietary_suitability(info['Nutrition Facts Parsed'], info.get('Ingredients', ''))
        formatted_parts.append(f"## 🍽️ **Dietary Suitability:**\n")
        for note in suitability_notes:
            formatted_parts.append(f"* {note}")
        formatted_parts.append("\n")

    if info.get('Special Notes'):
        formatted_parts.append(f"## Special Notes:\n* {info['Special Notes']}\n")

    return "\n".join(formatted_parts)


# Main execution block
if os.path.exists(image_path):
    extracted_info = extract_info_from_image(image_path)
    formatted_output = format_extracted_info(extracted_info)
    print("\n--- Extracted Information ---")
    from IPython.display import display, Markdown # For Colab
    display(Markdown(formatted_output))
else:
    print(f"❌ File not found: {image_path}. Please re-upload.")
