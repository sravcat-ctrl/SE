from flask import Flask, request, jsonify
import os
from docx import Document
from pypdf import PdfReader
import openai

app = Flask(__name__)

# Utility to read uploaded files
def load_file(file):
    filename = file.filename
    if filename.endswith(".txt"):
        return file.read().decode("utf-8")
    elif filename.endswith(".pdf"):
        reader = PdfReader(file)
        return "\n".join(p.extract_text() or "" for p in reader.pages)
    elif filename.endswith(".docx"):
        doc = Document(file)
        return "\n".join(p.text for p in doc.paragraphs)
    else:
        return ""

# Endpoint Chatbase will call
@app.route("/extract_rules", methods=["POST"])
def extract_rules():
    file = request.files.get("file")
    api_key = request.form.get("api_key")
    os.environ["OPENAI_API_KEY"] = api_key
    text = load_file(file)

    # Call GPT for extraction
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Extract all rules from this text and provide a JSON array with rule ID, rule text, and suggested fix."},
            {"role": "user", "content": text}
        ],
        temperature=0
    )

    rules_text = response.choices[0].message.content
    return jsonify({"rules": rules_text})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
