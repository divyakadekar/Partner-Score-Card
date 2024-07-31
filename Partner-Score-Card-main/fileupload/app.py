from flask import Flask, render_template, request, redirect, url_for, flash, session
import pandas as pd
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'your_secret_key'  # Add a secret key for session management

# Ensure upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# In-memory user storage
users = {}

# Initialize 'mph_info' at the top level of the app
mph_info = {}

@app.route('/', methods=['GET', 'POST'])
def home():
    global mph_info
    mph_codes = list(mph_info.keys())  # Use the keys from mph_info to populate mph_codes

    if request.method == 'POST':
        file = request.files.get('file')  # Use get() to handle missing file

        if not file or file.filename == '':
            flash('No file selected')
            return redirect(url_for('home'))

        if file:
            # Save the uploaded file
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)

            # Read the CSV file and store MPH code information
            try:
                df = pd.read_csv(file_path)

                if 'MPH Code' in df.columns:
                    mph_codes = df['MPH Code'].tolist()  # Extract MPH codes
                    # Combine relevant columns into the "Detail"
                    mph_info = {
                        row['MPH Code']: {
                            "Channel": row['Channel'],
                            "Gender": row['PH Gender'],
                            "Policies": row['Count of Policy/COI Number'],
                            "Avg Entry Age": row['Average of PH Entry Age'],
                            "Avg Term": row['Average of Policy Term_Month'],
                            "Premium": row['Sum of Premium'],
                            "Sum Assured": row['Sum of Sum Assured'],
                            "Claims": row['Count of Claims'],
                            "Claim Amount": row['Sum of Claim Amount']
                        }
                        for index, row in df.iterrows()
                    }
                    flash('File successfully uploaded and read!')
                else:
                    flash(f'CSV must contain "MPH Code" column. Found columns: {df.columns.tolist()}')
                    return redirect(url_for('home'))
            except Exception as e:
                flash(f'Error reading the CSV file: {e}')
                return redirect(url_for('home'))

    # Add empty details and code if no specific details are requested
    return render_template('home.html', mph_codes=mph_codes, details=None, details_code=None)

@app.route('/mph/<code>')
def mph_details(code):
    global mph_info
    details = mph_info.get(code, "No details available for this MPH code.")
    return render_template('home.html', mph_codes=list(mph_info.keys()), details=details, details_code=code)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users:
            flash('Username already exists')
            return redirect(url_for('signup'))
        users[username] = password
        flash('Signup successful')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if users.get(username) == password:
            session['username'] = username
            flash('Login successful')
            return redirect(url_for('home'))
        flash('Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Logged out successfully')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
