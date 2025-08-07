from flask import Flask, request, jsonify
import openai
import os
import requests
from PyPDF2 import PdfReader
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

openai.api_key = "key"

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    github_url = data.get('github_url', '')
    text = data.get('text', '')

    insights = {}

    if github_url:
        repo_data = requests.get(f"https://api.github.com/repos/{'/'.join(github_url.split('/')[-2:])}").json()
        insights['repo_name'] = repo_data.get("name")
        insights['stars'] = repo_data.get("stargazers_count")
        insights['language'] = repo_data.get("language")
        insights['created_at'] = repo_data.get("created_at")
        text += f"\nRepo Description: {repo_data.get('description')}"

    # Call OpenAI to generate summary
    completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an AI assistant generating insights."},
            {"role": "user", "content": f"Give a summary, key features, and 3 use cases for this:
{text}"}
        ]
    )
    insights['ai_summary'] = completion.choices[0].message.content
    return jsonify(insights)

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    path = os.path.join("uploads", file.filename)
    file.save(path)
    reader = PdfReader(path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return jsonify({"text": text})

if __name__ == '__main__':
    app.run(debug=True)
