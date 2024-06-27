from flask import Flask, render_template, request
import os

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/streamlit')
def run_streamlit():
    os.system('streamlit run streamlit_app.py')
    return "Streamlit App is running..."

if __name__ == "__main__":
    app.run(debug=True)
