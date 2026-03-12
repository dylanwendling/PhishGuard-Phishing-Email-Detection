from flask import Flask, render_template, request
import os

# ---> THE CRITICAL CONNECTION <---
# This tells Flask to look inside main_three.py and grab your model code
from main_three import run_phishguard_model

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if the user actually selected a file
        if 'file' not in request.files or request.files['file'].filename == '':
            return "No valid file uploaded", 400
            
        file = request.files['file']
        
        # Verify it is an .eml file
        if file and file.filename.endswith('.eml'):
            # Save the uploaded email temporarily
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

            # ---> RUN THE AI MODEL <---
            # Hand the saved email over to Qwen in main_three.py
            actual_results = run_phishguard_model(filepath)
            
            # Send the AI's results to your HTML page
            return render_template('results.html', results=actual_results)
        else:
            return "Please upload an .eml file.", 400

    # Load the basic upload page
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)