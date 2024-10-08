# Import necessary libraries
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

# Import the process_query function from rag_openAI
try:
    from rag_openAI import process_query
    print("Successfully imported process_query from rag_openAI")
except ImportError as e:
    print(f"Failed to import process_query from rag_openAI: {e}")

# Load environment variables from .env file
load_dotenv()

# Debug prints to show current environment
print(f"Current working directory: {os.getcwd()}")
print(f"Contents of current directory: {os.listdir('.')}")
print(f"Python path: {sys.path}")

# Set the static folder path for serving frontend files
static_folder_path = '/app/frontend/build'
app = Flask(__name__, static_folder=static_folder_path, static_url_path='/')
CORS(app)  # Enable Cross-Origin Resource Sharing

print(f"Static folder set to: {app.static_folder}")
print(f"Static URL path set to: {app.static_url_path}")

@app.route('/api/query', methods=['POST'])
def handle_query():
    """
    Handle POST requests to /api/query
    Process the query using the RAG system and return the result
    """
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
    """
    Serve static files for the React frontend
    If the path doesn't exist, serve index.html (for client-side routing)
    """
    print(f"Serving path: {path}")
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        print(f"Serving static file: {path}")
        return send_from_directory(app.static_folder, path)
    else:
        index_path = os.path.join(app.static_folder, 'index.html')
        print(f"Checking for index.html at: {index_path}")
        print(f"index.html exists: {os.path.exists(index_path)}")
        return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/health')
def health_check():
    """
    Health check endpoint to verify if the server is running
    """
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    # Run the Flask app
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)