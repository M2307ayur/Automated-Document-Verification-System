# 📄 Document Verification System

*A lightweight, fast, and efficient system for extracting, validating,
and verifying information from uploaded documents.*

## 🚀 **Overview**

The **Document Verification System** is designed to automate the
extraction and validation of key details from documents such as ID
cards, certificates, or official records. The system uses **OCR (Optical
Character Recognition)** to read text from uploaded images, runs
**preprocessing** to improve accuracy, and applies **Regex-based pattern
matching** to verify the extracted fields.

## 🛠️ **Features**

-   Upload documents through a clean Flask-based UI\
-   Preprocessing steps (grayscale, resizing, noise removal)\
-   Text extraction using **Pytesseract OCR**\
-   Regex-based validation of extracted fields\
-   Secure file handling using `secure_filename`\
-   Modular scripts for OCR, preprocessing, and validation

## 📂 **Project Structure**

    Document Verification/
    │── app.py
    │── ocr_engine.py
    │── preprocess.py
    │── verifier.py
    │── uploads/
    │── static/
    │── templates/
    │── requirements.txt
    │── README.md

## ⚙️ **Technologies Used**

Python, Flask, OpenCV, Pytesseract, Regex, HTML/CSS

## ▶️ **How to Run**

    pip install -r requirements.txt
    python app.py

Visit: `http://127.0.0.1:5000/`

## 🧪 **How It Works**

1.  Upload document\
2.  Preprocessing\
3.  OCR text extraction\
4.  Regex verification\
5.  Output with validation status

## 📌 **Future Enhancements**

-   AI-based text region detection\
-   PDF support\
-   Database integration\
-   Multi-language OCR
