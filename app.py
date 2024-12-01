from flask import Flask, request, jsonify
from PyPDF2 import PdfReader
import openai
import os

app = Flask(__name__)

# Set your OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Function to extract text from a PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    reader = PdfReader(pdf_path)
    for page in reader.pages:
        text += page.extract_text()
    return text

# Function to query OpenAI GPT
def query_gpt(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an AI assistant to answer queries based on a PDF."},
                {"role": "user", "content": prompt}
            ]
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return str(e)

# Route to upload PDF and extract text
@app.route("/upload", methods=["POST"])
def upload_pdf():
    pdf_file = request.files.get("pdf")
    if not pdf_file:
        return jsonify({"error": "No PDF file provided"}), 400

    # Save and read the PDF
    pdf_path = "./uploaded.pdf"
    pdf_file.save(pdf_path)
    pdf_text = extract_text_from_pdf(pdf_path)

    # Save extracted text as context
    return jsonify({"message": "PDF uploaded and text extracted successfully.", "extracted_text": pdf_text[:500]}), 200

# Route to chat using the extracted PDF content
@app.route("/chat", methods=["POST"])
def chat_with_pdf():
    query = request.json.get("query", "")
    if not query:
        return jsonify({"error": "No query provided"}), 400

    # Load extracted text from the uploaded PDF
    try:
        with open("./uploaded.pdf", "rb") as pdf_file:
            pdf_text = extract_text_from_pdf(pdf_file)
    except FileNotFoundError:
        return jsonify({"error": "No PDF uploaded. Please upload a PDF first."}), 400

    # Generate a prompt for OpenAI API
    prompt = f"Use the following content to answer the query:\n\n{pdf_text}\n\nQuery: {query}"

    # Query GPT model
    response = query_gpt(prompt)
    return jsonify({"response": response}), 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)

