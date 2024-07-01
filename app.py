import faiss
import torch
from transformers import AutoTokenizer, AutoModel
from flask import Flask, request, jsonify
 
# Initialize Flask app
app = Flask(__name__)
 
# Load pre-trained model and tokenizer from Hugging Face
model_name = "sentence-transformers/all-MiniLM-L6-v2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)
 
# Function to encode text into embeddings
def encode(texts):
    inputs = tokenizer(texts, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        embeddings = model(**inputs).last_hidden_state.mean(dim=1)
    return embeddings.numpy()
 
# Create a FAISS index
index = faiss.IndexFlatL2(384)  # Dimension should match the model's output
 
# Sample data to index
texts = ["Hello world", "FAISS is great", "Transformers are powerful"]
embeddings = encode(texts)
index.add(embeddings)
 
@app.route('/search', methods=['POST'])
def search():
    query = request.json.get('query')
    if not query:
        return jsonify({"error": "No query provided"}), 400
 
    query_embedding = encode([query])
    D, I = index.search(query_embedding, k=5)  # Search top-5 closest vectors
 
    results = [texts[i] for i in I[0]]
    return jsonify({"query": query, "results": results})
 
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)