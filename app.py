import os
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from news_search_module import search_news
from cluster import embed_articles, cluster_articles, analyze_clusters
import json
import datetime
from sentence_transformers import SentenceTransformer
from collections import OrderedDict
from apscheduler.schedulers.background import BackgroundScheduler
from scraper import main as scrape_articles  # Assuming scrape_articles is the function in your scraper.py

# Create Flask app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
CORS(app)

# Function to run the scraper every 2 hours
def run_scraper():
    print("Running scraper...")
    scrape_articles()  # Call your scraper function here

# Set up scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(run_scraper, 'interval', hours=2)  # Run every 2 hours
scheduler.start()

def organize_clustered_results(search_results, cluster_labels):
    """
    Organize search results into clusters and return structured JSON.
    Args:
        search_results (dict): Original search results
        cluster_labels (list): Cluster labels from DBSCAN
    Returns:
        dict: JSON matching frontend display format
    """
    clustered_results = {
        "search_term": search_results["search_term"],
        "total_articles": search_results["total_articles"],
        "clusters": {}
    }
    
    # Group articles into clusters
    for idx, label in enumerate(cluster_labels):
        cluster_name = "unclustered" if label == -1 else f"cluster_{label}"
        if cluster_name not in clustered_results["clusters"]:
            clustered_results["clusters"][cluster_name] = []
        clustered_results["clusters"][cluster_name].append(search_results["articles"][idx])
    
    # Sort clusters: cluster_0, cluster_1, ..., unclustered last
    sorted_clusters = dict(sorted(
        clustered_results["clusters"].items(),
        key=lambda x: (x[0] == "unclustered", int(x[0].split("_")[-1]) if x[0] != "unclustered" else float('inf'))
    ))
    
    clustered_results["clusters"] = sorted_clusters
    
    return clustered_results

@app.route('/search', methods=['GET'])
def search_endpoint():
    """
    Flask endpoint for searching news articles with optional clustering
    """
    # Get search parameters
    search_term = request.args.get('q', '').strip()
    sort_by = request.args.get('sort_by', 'date')
    sort_order = request.args.get('sort_order', 'desc')
    cluster_results = request.args.get('cluster', 'false').lower() == 'true'
    
    # Parse length parameters
    try:
        min_length = int(request.args.get('min_length', 0))
        max_length_input = request.args.get('max_length', 'infinity')
        max_length = float('inf') if max_length_input.lower() in ['infinity', 'inf'] else int(max_length_input)
        filter_date = request.args.get('filter_date')
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
    
    if sort_by not in valid_sort_by or sort_order not in valid_sort_order:
        return jsonify({
            "error": f"Invalid sort parameters. sort_by must be one of {valid_sort_by} and sort_order must be one of {valid_sort_order}",
            "status": "error"
        }), 400
    
    try:
        # Perform initial search
        search_results = search_news(
            search_term, 
            sort_by=sort_by, 
            sort_order=sort_order,
            min_length=min_length, 
            max_length=max_length,
            filter_date=filter_date
        )
        
        # If clustering is requested and there are results
        if cluster_results and search_results["articles"]:
            # Prepare texts for embedding
            texts = [
                f"{article['title']} {article.get('summary', '')}"
                for article in search_results["articles"]
            ]
            
            # Generate embeddings
            model = SentenceTransformer('roberta-base-nli-stsb-mean-tokens')
            embeddings = model.encode(texts)
            
            # Perform clustering
            cluster_labels = cluster_articles(embeddings)
            
            # Organize results into clusters
            final_results = organize_clustered_results(search_results, cluster_labels)
        else:
            final_results = search_results
        
        # Return results as JSON response
        response_json = json.dumps(final_results, indent=2, ensure_ascii=False)
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
