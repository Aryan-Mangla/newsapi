import json
import os
import sys
import re
from datetime import datetime

os.system('clear')

def whole_word_search(search_term, text):
    """
    Perform a whole word search.
    
    Args:
        search_term (str): Term to search for
        text (str): Text to search in
    
    Returns:
        bool: True if whole word match found, False otherwise
    """
    pattern = r'\b' + re.escape(search_term.lower()) + r'\b'
    return bool(re.search(pattern, text.lower()))

def parse_date(date_str):
    """
    Parse date string into datetime object.
    
    Args:
        date_str (str): Date string to parse
    
    Returns:
        datetime: Parsed datetime object or None if parsing fails
    """
    date_formats = [
        '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', 
        '%B %d, %Y', '%d %B %Y', '%Y %B %d'
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt)
        except (ValueError, TypeError):
            continue
    return None

def search_news(search_term, json_file_path=None, sort_by='date', sort_order='desc', 
                min_length=0, max_length=float('inf')):
    """
    Search and sort news articles based on various parameters.
    
    Args:
        search_term (str): Term to search for in articles
        json_file_path (str, optional): Path to the JSON file containing scraped articles
        sort_by (str, optional): Parameter to sort by. Options: 'date', 'length', 'popularity'
        sort_order (str, optional): Sort order. Options: 'asc' (ascending), 'desc' (descending)
        min_length (int, optional): Minimum article length to include
        max_length (int, optional): Maximum article length to include
    
    Returns:
        dict: Sorted and filtered search results in JSON-compatible format
    """
    # Normalize search term
    search_term = search_term.strip()
    
    # Find the most recent JSON file
    if not json_file_path:
        try:
            scrapes_dir = 'scrapes'
            json_files = [f for f in os.listdir(scrapes_dir) if f.endswith('.json')]
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
    
    # Search and filter articles
    matching_articles = []
    
    for article in articles:
        # Combine searchable fields
        searchable_text = ' '.join([
            str(article.get('title', '')),
            str(article.get('summary', '')),
            # str(article.get('full_content', '')),
            str(article.get('author', ''))
        ])
        
        # Whole word search
        if whole_word_search(search_term, searchable_text):
            # Length filtering
            content_length = len(str(article.get('full_content', '')))
            if min_length <= content_length <= max_length:
                matching_articles.append({
                    "title": article.get('title', ''),
                    "link": article.get('link', ''),
                    "summary": article.get('summary', ''),
                    "full_content": article.get('full_content', ''),
                    "author": article.get('author', ''),
                    "source": article.get('source', ''),
                    "published_date": article.get('published_date', ''),
                    "url_to_image": article.get('url_to_image', ''),
                    "_content_length": content_length,
                    "_parsed_date": parse_date(article.get('published_date', ''))
                })
    
    # Sorting logic
    if sort_by == 'date':
        matching_articles.sort(
            key=lambda x: x['published_date'] or datetime.min, 
            reverse=(sort_order == 'desc')
        )
    elif sort_by == 'length':
        matching_articles.sort(
            key=lambda x: x['_content_length'], 
            reverse=(sort_order == 'desc')
        )
    
    # Remove internal sorting keys
    for article in matching_articles:
        article.pop('_content_length', None)
        article.pop('_parsed_date', None)
    
    # Prepare final result
    search_result = {
        "total_articles": len(matching_articles),
        "search_term": search_term,
        "articles": matching_articles
    }
    
    return search_result


# Test the search_news function 
search_results = search_news('trump', sort_by='length', sort_order='asc')
with open ('search_results.json', 'w') as f:
    json.dump(search_results, f, indent=2)

    
