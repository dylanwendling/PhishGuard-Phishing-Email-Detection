from flask import Flask, render_template, request, session, cli
import os
import sys

# Import your models
from main import run_phishguard_model as run_smollm
from main_two import run_phishguard_model as run_llama3
from main_three import run_phishguard_model as run_qwen

app = Flask(__name__)
app.secret_key = 'phishguard-secret-key-2024'
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

MODELS = {
    'smollm': {'name': 'SmolLM2-135M', 'function': run_smollm, 'speed': '⚡ Fastest'},
    'llama3': {'name': 'Llama-3.2-1B', 'function': run_llama3, 'speed': '⚖️ Balanced'},
    'qwen': {'name': 'Qwen2.5-1.5B', 'function': run_qwen, 'speed': '🎯 Most Accurate'}
}

# --- THE WINDOWS ERROR 6 FIX ---
# This safely disables the Flask startup banner that causes colorama to crash in Jupyter terminals
cli.show_server_banner = lambda *args: None
# -------------------------------

@app.route('/', methods=['GET', 'POST'])
def index():
    # Set default model to Qwen
    if 'selected_model' not in session:
        session['selected_model'] = 'qwen'
    
    if request.method == 'POST':
        # 1. Handle Model Selection 
        if 'model_select' in request.form:
            session['selected_model'] = request.form['model_select']
            
        # 2. Handle File Upload
        if 'file' in request.files:
            file = request.files['file']
            
            if file.filename == '':
                return "No valid file uploaded", 400
            
            if file and file.filename.endswith('.eml'):
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(filepath)
                
                model_key = session.get('selected_model', 'qwen')
                model_func = MODELS[model_key]['function']
                
                try:
                    actual_results = model_func(filepath)
                    
                    # Ensure the model returns a dictionary before assigning keys
                    if isinstance(actual_results, dict):
                        actual_results['model_used'] = MODELS[model_key]['name']
                    else:
                        actual_results = {
                            "error": "The model did not return the expected data format.",
                            "raw_output": str(actual_results),
                            "model_used": MODELS[model_key]['name']
                        }
                    return render_template('results.html', results=actual_results)
                    
                except Exception as e:
                    return f"Model Error: {str(e)}", 500
            else:
                return "Please upload an .eml file.", 400

    return render_template('index.html', 
                         models=MODELS, 
                         selected_model=session['selected_model'])

@app.route('/set_model/<model_name>')
def set_model(model_name):
    if model_name in MODELS:
        session['selected_model'] = model_name
    return render_template('index.html', 
                         models=MODELS, 
                         selected_model=session['selected_model'])

if __name__ == '__main__':
    # Print a plain-text confirmation so you know it's running
    print("Starting PhishGuard server on http://127.0.0.1:5000 ...")
    app.run(debug=True, use_reloader=False)