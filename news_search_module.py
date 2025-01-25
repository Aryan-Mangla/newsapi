import json
import os
import sys
import re

def whole_word_search(search_term, text):
    """
    Perform a whole word search.
    
    Args:
        search_term (str): Term to search for
        text (str): Text to search in
    
    Returns:
        bool: True if whole word match found, False otherwise
    """
    # Create a regex pattern that matches whole words
    # This ensures the search term is matched as a complete word
    pattern = r'\b' + re.escape(search_term.lower()) + r'\b'
    return bool(re.search(pattern, text.lower()))

def search_news(search_term, json_file_path=None):
    """
    Search news articles based on a user-provided search term.
    
    Args:
        search_term (str): Term to search for in articles
        json_file_path (str, optional): Path to the JSON file containing scraped articles
    
    Returns:
        dict: Search results in JSON-compatible format
    """
    # Normalize search term (trim whitespace)
    search_term = search_term.strip()
    
    # Find the most recent JSON file in the scrapes directory
    if not json_file_path:
        try:
            # List all files in the scrapes directory
            scrapes_dir = 'scrapes'
            json_files = [f for f in os.listdir(scrapes_dir) if f.endswith('.json')]
            
            # Sort files by modification time, get the most recent
            json_files.sort(key=lambda x: os.path.getmtime(os.path.join(scrapes_dir, x)), reverse=True)
            
            if not json_files:
                return {
                    "search_term": search_term,
                    "total_articles": 0,
                    "articles": [],
                    "error": "No scraped articles found"
                }
            
            json_file_path = os.path.join(scrapes_dir, json_files[0])
        except Exception as e:
            return {
                "search_term": search_term,
                "total_articles": 0,
                "articles": [],
                "error": f"Error finding JSON file: {str(e)}"
            }
    
    # Read the JSON file
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            articles = json.load(f)
    except Exception as e:
        return {
            "search_term": search_term,
            "total_articles": 0,
            "articles": [],
            "error": f"Error reading JSON file: {str(e)}"
        }
    
    # Search results container
    matching_articles = []
    
    # Search through articles
    for article in articles:
        # Combine searchable fields
        searchable_text = ' '.join([
            str(article.get('title', '')),
            str(article.get('summary', '')),
            str(article.get('full_content', '')),
            str(article.get('author', ''))
        ])
        
        # Check if search term is a whole word in the searchable text
        if whole_word_search(search_term, searchable_text):
            matching_articles.append({
                "title": article.get('title', ''),
                "link": article.get('link', ''),
                "summary": article.get('summary', ''),
                "full_content": article.get('full_content', ''),
                "author": article.get('author', ''),
                "source": article.get('source', ''),
                "published_date": article.get('published_date', ''),
                "url_to_image": article.get('url_to_image', '')
            })
    
    # Prepare final result
    search_result = {
        "total_articles": len(matching_articles),
        "search_term": search_term,
        "articles": matching_articles
        
        
        
    }
    
    return search_result 
