import sys
import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

print("Imported sys and os")

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("Appended current directory to sys.path")
print(f"sys.path after append: {sys.path}")

# Now we can import from the current directory
try:
    from rag_openAI import process_query
    print("Successfully imported process_query from rag_openAI")
except ImportError as e:
    print(f"Failed to import process_query from rag_openAI: {e}")

load_dotenv()

# Debug prints
print(f"Current working directory: {os.getcwd()}")
print(f"Contents of current directory: {os.listdir('.')}")
print(f"Python path: {sys.path}")

app = Flask(__name__, static_folder='../frontend/build', static_url_path='/')
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

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    print(f"Serving path: {path}")
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        print(f"Serving static file: {path}")
        return send_from_directory(app.static_folder, path)
    else:
        print("Serving index.html")
        return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/health')
def health_check():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
