import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from news_search_module import search_news
from flask import Response
import json

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
CORS(app)  # Enable CORS for all routes

@app.route('/search', methods=['GET'])
def search_endpoint():
    """
    Flask endpoint for searching news articles with advanced filtering and sorting
    """
    # Get search parameters
    search_term = request.args.get('q', '').strip()
    sort_by = request.args.get('sort_by', 'date')
    sort_order = request.args.get('sort_order', 'desc')
    
    # Parse length parameters with type conversion and defaults
    try:
        # Check if min_length is provided
        if 'min_length' in request.args:
            min_length = int(request.args.get('min_length'))
        else:
            min_length = 0

        # Check if max_length is provided
        if 'max_length' in request.args:
            max_length_input = request.args.get('max_length')
            # Handle 'Infinity' or 'infinity' strings
            if max_length_input.lower() in ['infinity', 'inf']:
                max_length = float('inf')
            else:
                max_length = int(max_length_input)
        else:
            max_length = float('inf')

    except ValueError:
        return jsonify({
            "error": "Invalid length parameters. Must be integers or 'Infinity'.",
            "status": "error"
        }), 400
    
    # Validate search term
    if not search_term:
        return jsonify({
            "error": "No search term provided",
            "status": "error"
        }), 400
    
    # Validate sort parameters
    valid_sort_by = ['date', 'length']
    valid_sort_order = ['asc', 'desc']
    
    if sort_by not in valid_sort_by:
        return jsonify({
            "error": f"Invalid sort_by. Must be one of {valid_sort_by}",
            "status": "error"
        }), 400
    
    if sort_order not in valid_sort_order:
        return jsonify({
            "error": f"Invalid sort_order. Must be one of {valid_sort_order}",
            "status": "error"
        }), 400
    
    try:
        # Perform search with new parameters
        search_results = search_news(
            search_term, 
            sort_by=sort_by, 
            sort_order=sort_order,
            min_length=min_length, 
            max_length=max_length
        )
        
        # Return results as JSON response
        response_json = json.dumps(search_results, indent=2, ensure_ascii=False)
        return Response(response_json, content_type='application/json')
    
    except Exception as e:
        # Handle any unexpected errors
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

def main():
    # Ensure scrapes directory exists
    os.makedirs('scrapes', exist_ok=True)
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main()