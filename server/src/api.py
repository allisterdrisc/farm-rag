from flask import Flask, request, jsonify
from flask_cors import CORS
from farm_agent import ask_farm_agent

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5173", "http://localhost:5174"]}})

@app.route('/api/ask', methods=['POST', 'OPTIONS'])
def ask():
    if request.method == 'OPTIONS':
        # CORS preflight request
        return '', 200

    data = request.get_json()
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"error": "No question provided."}), 400

    response = ask_farm_agent(question)
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True, port=5001)