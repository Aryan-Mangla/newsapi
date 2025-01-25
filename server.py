import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from news_search_module import search_news
from flask import Response
import json

# Create Flask app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
CORS(app)  # Enable CORS for all routes

@app.route('/search', methods=['GET'])
def search_endpoint():
    """
    Flask endpoint for searching news articles
    
    Query Parameters:
    - q: Search term
    """
    # Get search term from query parameter
    search_term = request.args.get('q', '').strip()
    
    # Validate search term
    if not search_term:
        return jsonify({
            "error": "No search term provided",
            "status": "error"
        }), 400
    
    try:
        # Perform search
        search_results = search_news(search_term)
        
        # Return results as JSON response
        response_json = json.dumps(search_results, indent=2, ensure_ascii=False)
        return Response(response_json, content_type='application/json')
    
    except Exception as e:
        # Handle any unexpected errors
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

@app.route('/list-sources', methods=['GET'])
def list_sources():
    """
    Endpoint to list available scraped news sources
    """
    try:
        # List JSON files in scrapes directory
        scrapes_dir = 'scrapes'
        json_files = [f for f in os.listdir(scrapes_dir) if f.endswith('.json')]
        
        # Sort files by modification time, most recent first
        json_files.sort(key=lambda x: os.path.getmtime(os.path.join(scrapes_dir, x)), reverse=True)
        
        return jsonify({
            "sources": json_files,
            "total_sources": len(json_files)
        })
    
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

@app.route('/', methods=['GET'])
def home():
    """
    Home route with basic API information
    """
    return jsonify({
        "message": "News Search API",
        "endpoints": {
            "/search": "Search news articles (GET, param: q)",
            "/list-sources": "List available news sources"
        }
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Endpoint not found",
        "status": "error"
    }), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "error": "Internal server error",
        "status": "error"
    }), 500

def main():
    # Ensure scrapes directory exists
    os.makedirs('scrapes', exist_ok=True)
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main()