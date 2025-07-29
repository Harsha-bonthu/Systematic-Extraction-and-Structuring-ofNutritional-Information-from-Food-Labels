# Systematic Extraction and Structuring of Nutritional Information from Food Labels

# Food Label Extractor (Google Colab)

This project provides a Python script designed to extract key information from food product labels using Optical Character Recognition (OCR) and Natural Language Processing (NLP). It leverages Google Colab for easy execution without complex local setups.

## ✨ Features

* **Product Information Extraction:** Identifies Product Name, Ingredients, Vitamins and Minerals, Nutrition Facts, and Special Notes.
* **Automated Text Cleaning:** Pre-processes OCR output to improve accuracy and consistency.
* **Nutrient Value Parsing:** Extracts specific nutrient values (e.g., Calories, Fat, Protein, Sugars) along with their units from the "Nutrition Facts" section.
* **Allergen Detection:** Identifies common allergens (e.g., milk, peanuts, gluten) based on a predefined list, found in ingredients or special notes.
* **Dietary Suitability Assessment:** Provides flags for dietary suitability (e.g., Low-Fat, High-Protein, Low-Sugar, Vegetarian-Friendly, Vegan-Friendly) based on nutrient profiles and ingredients.
* **Markdown Output:** Presents the extracted and analyzed information in a clean, readable Markdown format, ideal for Google Colab notebooks.

## 🚀 How to Use in Google Colab

1.  **Open in Colab:** Click the "Open in Colab" badge below (or simply copy and paste the code into a new Colab notebook).
    [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/YOUR_USERNAME/YOUR_REPOSITORY_NAME/blob/main/food_label_extractor.ipynb)
    *(**Note:** Replace `YOUR_USERNAME` and `YOUR_REPOSITORY_NAME` with your actual GitHub details if you fork this repo. For now, you can just paste the code directly.)*

2.  **Run the Cells:** Execute each cell in the Colab notebook sequentially.
    * The first cell will install necessary Python libraries (`pytesseract`, `pillow`, `spacy`) and download the English NLP model (`en_core_web_sm`).
    * The second set of commands will install Tesseract OCR on the Colab environment.
    * The script will then prompt you to upload an image file.

3.  **Upload Your Image:** When prompted, click the "Choose Files" button and select an image file of a food label from your local machine.

4.  **View Results:** After the image is uploaded and processed, the extracted information, including parsed nutrition facts, detected allergens, and dietary suitability, will be displayed directly in the Colab output cell in a nicely formatted Markdown.

## ⚙️ Technical Details

* **OCR Engine:** [Tesseract OCR](https://tesseract-ocr.github.io/) is used for converting images of text into machine-readable text.
* **Image Processing:** `PIL (Pillow)` library is used for basic image manipulation like grayscale conversion and sharpening to optimize for OCR.
* **Natural Language Processing (NLP):** [spaCy](https://spacy.io/) is utilized for more robust extraction of nutrient values and for detecting allergens based on token patterns and keyword matching.
* **Regular Expressions:** Python's `re` module is extensively used for pattern matching and extracting specific sections of text (e.g., Product Name, Ingredients, Nutrition Facts).

## 💡 Customization and Improvements

* **Enhance OCR Preprocessing:** Experiment with more advanced image preprocessing techniques (e.g., binarization, noise reduction, deskewing) using libraries like `OpenCV` to improve OCR accuracy on challenging images.
* **Expand Allergen List:** Add more specific allergens or common allergen warning phrases to `common_allergens`.
* **Refine Dietary Rules:** Adjust the thresholds or add more complex logic in `assess_dietary_suitability` for more nuanced diet recommendations.
* **Internationalization:** Implement multi-language support for OCR and NLP if you intend to process labels in languages other than English.
* **Machine Learning for Categorization:** For more robust food category classification, consider training a machine learning model on a larger dataset of ingredients.
* **User Interface:** For a standalone application, wrap this logic in a web framework like Flask or Streamlit.

## ⚠️ Limitations

* **OCR Accuracy:** The accuracy of information extraction heavily depends on the quality, lighting, and clarity of the input image. Poor image quality will result in less accurate OCR output.
* **Regex Fragility:** While robust, regex patterns can be brittle to significant variations in label formatting.
* **Keyword-Based Allergen Detection:** The current allergen detection is keyword-based and might miss subtle or unusual phrasings of allergen warnings.
* **Nutrient Parsing:** Parsing nutrient values can be challenging due to diverse label formats; some values might be missed if the pattern isn't recognized.

## 🤝 Contributing

Feel free to fork this repository, open issues, or submit pull requests with improvements!

