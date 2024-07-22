from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
import json
import pandas as pd
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'your_secret_key'  # Add a secret key for session management

# Initialize 'mph_info' at the top level of the app
mph_info = {}

# Path to the JSON file
users_file = 'users.json'

# Create upload folder if it doesn't exist
upload_folder = 'uploads'
if not os.path.exists(upload_folder):
    os.makedirs(upload_folder)

# Load users from the JSON file
def load_users():
    if not os.path.exists(users_file):
        return {}
    with open(users_file, 'r') as f:
        return json.load(f)

# Save users to the JSON file
def save_users(users):
    with open(users_file, 'w') as f:
        json.dump(users, f, indent=4)

# Route for the index page
@app.route('/index')
def index():
    return render_template('index.html')

# Route for the home page
@app.route('/', methods=['GET', 'POST'])
def home():
    global mph_info
    mph_codes = []  # Initialize an empty list for MPH codes
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(url_for('home'))

        file = request.files['file']

        if file.filename == '':
            flash('No selected file')
            return redirect(url_for('home'))

        if file:
            # Save the uploaded file
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)

            # Read the CSV file and store MPH code information
            try:
                df = pd.read_csv(file_path)
                if 'MPH Code' in df.columns and 'Detail' in df.columns:
                    mph_codes = df['MPH Code'].tolist()  # Extract MPH codes
                    mph_info = {row['MPH Code']: row['Detail'] for index, row in df.iterrows()}  # Store details
                else:
                    flash('CSV must contain "MPH Code" and "Detail" columns.')
            except Exception as e:
                flash(f'Error reading the CSV file: {e}')
                return redirect(url_for('home'))

            # Debugging lines to check the status
            print("Request files:", request.files)  # Debugging line
            print("MPH Codes:", mph_codes)  # Debugging line

    return render_template('home.html', mph_codes=mph_codes)


@app.route('/mph/<code>')
def mph_details(code):
    global mph_info
    details = mph_info.get(code, "No details available for this MPH code.")
    return render_template('mph_details.html', code=code, details=details)

# Route for the signup page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']

        users = load_users()
        if username in users:
            flash('Username already exists!')
            return redirect(url_for('signup'))

        users[username] = {
            'password': password,
            'first_name': first_name,
            'last_name': last_name,
            'email': email
        }
        save_users(users)
        flash('Signup successful! You can now log in.')
        return redirect(url_for('login'))
    return render_template('signup.html')

# Route for the login page
@app.route('/login', methods=['GET', 'POST'])
def login():                                          
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        users = load_users()
        if username in users and users[username]['password'] == password:
            session['username'] = username
            flash('Login successful!')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password')
            return redirect(url_for('login'))
    return render_template('login.html')

# Route for the logout
@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove the username from the session
    flash('You have been logged out.')
    return redirect(url_for('home'))  # Redirect to the home page

@app.route('/uploads/<filename>')
def send_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])  # Create upload folder if it doesn't exist
    app.run(debug=True)
