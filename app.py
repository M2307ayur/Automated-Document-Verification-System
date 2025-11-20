from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
import pytesseract
from PIL import Image
from flask import send_file
import re
from flask import jsonify
app = Flask(__name__)
app.secret_key = 'your_secret_key'
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\tesseract.exe'

# Set up the folder to store uploaded files
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Initialize the database
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    document_type TEXT NOT NULL,
                    stage TEXT NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS user_noncreamylayer_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT,
    document_type TEXT,
    filename TEXT NOT NULL,
    name TEXT,
    outward_no TEXT,
    date_of_issue TEXT,
    verification_status TEXT DEFAULT 'pending'
);
''')
    c.execute('''CREATE TABLE IF NOT EXISTS user_pan_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT,
    document_type TEXT,
    filename TEXT NOT NULL,
    name TEXT,
    pan_card_number TEXT,
    verification_status TEXT DEFAULT 'pending'
);''')

    c.execute('''CREATE TABLE IF NOT EXISTS user_aadhar_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT,
    document_type TEXT,
    filename TEXT NOT NULL,
    name TEXT,
    aadhar_no TEXT,
    verification_status TEXT DEFAULT 'pending'
);
''')
    
    
    conn.commit()
    conn.close()

# Handle the file upload
# Function to extract Name
def extract_noncreamylayer_name(text):
    name_pattern = r"(?<=certify that\s)([A-Za-z\s]+?)(?=\s(?:Son|Daughter|of|Mr|Mrs|Ms|Dr|,|\.|$))"
    name_match = re.search(name_pattern, text)
    return name_match.group(1).strip() if name_match else "Not Found"

# Function to extract Outward No
def extract_noncreamylayer_outward_no(text):
    outward_no_pattern = r"Outward No:\s*(\d+)"
    outward_no_match = re.search(outward_no_pattern, text)
    return outward_no_match.group(1) if outward_no_match else "Not Found"

# Function to extract Date of Issue
def extract_noncreamylayer_date(text):
    date_pattern = r"Dated:\s*([\d/]+)"
    date_match = re.search(date_pattern, text)
    return date_match.group(1) if date_match else "Not Found"
def extract_aadhar_name(text):
    name_pattern = r"(?<=To\s)(.+?)(?=,|\n)"
    name_match = re.search(name_pattern, text)
    return name_match.group(1).strip() if name_match else "Not Found"

# Function to extract Aadhaar Number
def extract_aadhar_number(text):
    aadhar_pattern = r"\b\d{4}\s\d{4}\s\d{4}\b"
    aadhar_match = re.search(aadhar_pattern, text)
    return aadhar_match.group(0) if aadhar_match else "Not Found"
# Function to extract Name from PAN Card
def extract_pan_name(text):
    name_pattern = r"(?<=aTa/ Name\n)(.+?)(?=\n)"
    name_match = re.search(name_pattern, text, re.DOTALL)
    return name_match.group(1).strip() if name_match else "Not Found"

# Function to extract PAN Card Number
def extract_pan_number(text):
    
    pan_card_number_pattern =r"(\w{10})"
    pan_card_number_match = re.search(pan_card_number_pattern, text)
    return pan_card_number_match.group(0) if pan_card_number_match else "Not Found"

# Function to save the extracted PAN card data
def save_user_pan_data(email, document_type, filename, name, pan_card_number):
    filename = filename.replace('uploads\\', '')
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('INSERT INTO user_pan_documents (email, document_type, filename, name, pan_card_number) VALUES (?, ?, ?, ?, ?)',
              (email, document_type, filename, name, pan_card_number))
    conn.commit()
    conn.close()
# Function to save the extracted data to the user_documents database
def save_user_noncreamylayer_data(email, document_type,filename, name, outward_no, date_of_issue):
    filename=filename.replace('uploads\\','')
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    # Insert data into the user_documents table
    c.execute('INSERT INTO user_noncreamylayer_documents (email, document_type,filename, name, outward_no, date_of_issue) VALUES (?,?, ?, ?, ?, ?)',
              (email, document_type,filename, name, outward_no, date_of_issue))
    conn.commit()
    conn.close()
def save_user_aadhar_data(email, document_type,filename, name, aadhar_no):
    filename=filename.replace('uploads\\','')
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    # Insert data into the user_documents table
    c.execute('INSERT INTO user_aadhar_documents (email, document_type,filename, name,aadhar_no) VALUES (?,?, ?, ?,?)',
              (email, document_type,filename, name, aadhar_no))
    conn.commit()
    conn.close()

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        document = request.files['document']
        document_type = request.form['document_type']

        # Check if the file is allowed
        if document and allowed_file(document.filename):
            user_email = session['email']
            stage='pending'
            # Save the file
            filename = os.path.join(app.config['UPLOAD_FOLDER'], document.filename)
            conn = sqlite3.connect('users.db')
            c = conn.cursor()
            # Insert data into the documents table
            c.execute('INSERT INTO documents (email, document_type,filename,stage) VALUES (?,?,?, ?)',
                    (user_email, document_type,filename, stage))
            conn.commit()
            conn.close()
            document.save(filename)
            img = Image.open(filename)
            extracted_text = pytesseract.image_to_string(img)
            extracted_info = {}
            # Extract details (Name, Outward No., Date) using regex
            if document_type == 'non-creamy layer':
                name = extract_noncreamylayer_name(extracted_text)
                outward_no = extract_noncreamylayer_outward_no(extracted_text)
                date_of_issue = extract_noncreamylayer_date(extracted_text)
                extracted_info = {
                'name': name,
                'outward_no': outward_no,
                'date_of_issue': date_of_issue
            }
                # Save extracted data to the user_documents database
                save_user_noncreamylayer_data(user_email, document_type,filename, name, outward_no, date_of_issue)
            elif document_type == 'aadhar':
                name = extract_aadhar_name(extracted_text)
                aadhar_no = extract_aadhar_number(extracted_text)
                extracted_info = {
                    'name': name,
                    'aadhar_no': aadhar_no
                }
                save_user_aadhar_data(user_email, document_type, filename, name, aadhar_no)
            elif document_type == 'pancard':
                name = extract_pan_name(extracted_text)
                pan_card_number = extract_pan_number(extracted_text)
                extracted_info = {
                    'name': name,
                    'pan_card_number': pan_card_number
                }
                save_user_pan_data(user_email, document_type, filename, name, pan_card_number)
            else:
                return 'Document type not supported'

            return render_template('extracted_info.html', extracted_info=extracted_info)
        else:
            return 'Invalid file type or no file uploaded'

    return render_template('dashboard.html')
@app.route('/user_info',methods=['GET'])
def user_info():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM documents where email = ?",(session['email'],))   
    documents = c.fetchall()
    conn.close()
    return render_template('user_info.html',documents=documents)

# Create the folder to store uploaded files (if not exists)
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def home():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    email = request.form['email']
    password = request.form['password']
    role = request.form['role']

    # Save user data to the database
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("INSERT INTO users (email, password, role) VALUES (?, ?, ?)", (email, password, role))
    conn.commit()
    conn.close()

    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Check user credentials
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
        user = c.fetchone()
        conn.close()

        if user:
            session['user_id'] = user[0]
            session['email'] = user[1]
            session['user_role'] = user[3]
            if(user[3]=='admin'):
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('user_info'))
        else:
            return 'Login failed, please check your credentials.'

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if session['user_role'] == 'admin':
        return redirect(url_for('admin_dashboard'))
    else:
        return render_template('dashboard.html')

@app.route('/admin/dashboard',methods=['GET'])
def admin_dashboard():
    if 'user_id' not in session or session['user_role'] != 'admin':
        return redirect(url_for('login'))
    popup = request.args.get('popup', 'false').lower() == 'true'
    success = request.args.get('success', 'false').lower() == 'true'
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM documents")
    pending_documents = c.fetchall()
    conn.close()
    return render_template('admin_dashboard.html', documents=pending_documents,popup=popup,success=success)
@app.route('/view_document/<filename>',methods=['GET'])
def view_document(filename):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    # filename=filename.replace('uploads%5C','')
    file_path = os.path.join(filename)
    if os.path.exists(file_path):
        return send_file(file_path)
    else:
        return 'File not found', 404
@app.route('/verify/<int:document_id>', methods=['GET'])
def verify_document(document_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    # Get the extracted data from the document based on document_id
    c.execute("SELECT * FROM documents WHERE id = ?", (document_id,))
    document = c.fetchone()

    if document:
        # Compare the extracted data with the manually added non-creamy layer documents
        if document[3] == 'non-creamy layer':
            c.execute("SELECT * FROM user_noncreamylayer_documents WHERE email = ? AND document_type =?", (document[1],document[3]))
            non_creamy_document = c.fetchone()
            name = non_creamy_document[4]
            outward_no = non_creamy_document[5]
            date_of_issue =non_creamy_document[6]
        # Check if the document data matches any non-creamy layer records
            verified = check_non_creamylayer_verification(name, outward_no, date_of_issue)
        elif document[3] == 'aadhar':
            c.execute("SELECT * FROM user_aadhar_documents WHERE email = ? AND document_type =?", (document[1],document[3]))
            aadhar_document = c.fetchone()
            name = aadhar_document[4]
            aadhar_no = aadhar_document[5]
            verified = check_aadhar_verification(name, aadhar_no)
        elif document[3] == 'pancard':
            c.execute("SELECT * FROM user_pan_documents WHERE email = ? AND document_type =?", (document[1],document[3]))
            pan_document = c.fetchone()
            name = pan_document[4]
            pan_card_number = pan_document[5]
            verified = check_pan_verification(name, pan_card_number)
        c.execute("SELECT * FROM documents")
        pending_documents = c.fetchall()
        # Update the verification status
        if verified:
            c.execute("UPDATE documents SET stage = 'verified' WHERE id = ?", (document_id,))
            conn.commit()
            conn.close()
            return redirect(url_for('admin_dashboard',popup=True,success=True))
        else:
            c.execute("UPDATE documents SET stage = 'failed' WHERE id = ?", (document_id,))
            conn.commit()
            conn.close()
            return redirect(url_for('admin_dashboard',popup=True,success=False))

    return jsonify({"error": "Document not found"}), 404

# Function to check if the document matches any non-creamy layer records
def check_non_creamylayer_verification(name, outward_no, date_of_issue):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    # Search for the document details in the non-creamy layer database
    c.execute("SELECT * FROM non_creamy_layer WHERE name = ? AND outward_no = ? AND date_of_issue = ?",
              (name, outward_no, date_of_issue))
    document = c.fetchone()

    conn.close()

    return document is not None

def check_aadhar_verification(name, aadhar_no):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    # Search for the document details in the non-creamy layer database
    c.execute("SELECT * FROM aadhar WHERE name = ? AND aadhar_no = ?",
              (name, aadhar_no))
    document = c.fetchone()

    conn.close()

    return document is not None
def check_pan_verification(name, pan_card_number):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    # Search for the document details in the non-creamy layer database
    c.execute("SELECT * FROM pan WHERE name = ? AND pan_no = ?",
              (name, pan_card_number))
    document = c.fetchone()

    conn.close()

    return document is not None 
# Initialize the database
init_db()

if __name__ == '__main__':
    app.run(debug=True)
