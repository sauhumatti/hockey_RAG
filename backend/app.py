import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from .rag_openAI import process_query

# Add the backend directory to the Python path
# (This line can be kept if you have imports from backend modules)
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='../frontend/build')
CORS(app)

@app.route('/api/query', methods=['POST'])
def handle_query():
    data = request.json
    query = data['query']
    try:
        result = process_query(query)
        return jsonify(result)
    except Exception as e:
        print(f"Error processing query: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Serve React App
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
