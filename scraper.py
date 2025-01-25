import feedparser
import json
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import traceback
import os

def extract_full_content(url):
    """
    Extract full content from the article URL
    Uses requests and BeautifulSoup for web scraping
    """
    try:
        # Add headers to mimic browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Fetch the webpage
        response = requests.get(url, headers=headers, timeout=10)
        
        # Check if request was successful
        if response.status_code != 200:
            return "Unable to fetch full content"
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try multiple strategies to extract content
        content_strategies = [
            lambda: soup.find('article'),  # Look for <article> tag
            lambda: soup.find('div', class_=lambda x: x and 'content' in x.lower()),
            lambda: soup.find('div', class_=lambda x: x and 'body' in x.lower()),
            lambda: soup.find('div', id=lambda x: x and 'content' in x.lower()),
            lambda: soup.find('body')  # Fallback to entire body
        ]
        
        # Try each strategy
        for strategy in content_strategies:
            content = strategy()
            if content:
                # Extract text, clean up
                text = content.get_text(strip=True, separator=' ')
                
                # Limit text length to prevent extremely large outputs
                return text[:5000] + '...' if len(text) > 5000 else text
        
        return "No content could be extracted"
    
    except Exception as e:
        return f"Error extracting content: {str(e)}"

def extract_author(entry):
    """
    Advanced author extraction strategy
    """
    author_fields = [
        'author',           # Standard RSS author field
        'dc_creator',       # Dublin Core creator
        'name',             # Some feeds use 'name'
        'email',            # Some feeds include email
    ]
    
    for field in author_fields:
        # Check multiple ways of extracting author
        if field in entry:
            return str(entry[field])
        
        # Check nested dictionaries
        if hasattr(entry, field):
            return str(getattr(entry, field))
    
    return 'Unknown author'

def scrape_rss_feed(feed_url):
    """
    Scrapes articles from a single RSS feed with enhanced extraction
    """
    # Parse the RSS feed
    feed = feedparser.parse(feed_url)
    
    # Check if the feed was successfully parsed
    if feed.bozo:
        print(f"Error parsing the feed: {feed_url}")
        print(f"Bozo exception: {feed.bozo_exception}")
        return []
    
    articles = []
    source_title = feed.feed.get('title', 'Unknown Source')
    
    # Loop through all the entries (articles) in the RSS feed
    for entry in feed.entries:
        try:
            # Extract basic article information
            title = entry.get('title', 'No title available')
            link = entry.get('link', 'No link available')
            
            # Extract summary (if available)
            summary = entry.get('summary', 'No summary available')
            
            # Extract author with advanced method
            author = extract_author(entry)
            
            # Extract image URL
            image_url = 'No image available'
            # Try multiple image extraction methods
            image_fields = [
                'media_content',  # Some feeds use this
                'media_thumbnail',  # Alternative image field
                'links'  # Another possible image source
            ]
            for field in image_fields:
                if field in entry:
                    try:
                        image_url = entry[field][0].get('url', image_url)
                        break
                    except:
                        pass
            
            # Convert published date
            published = entry.get('published') or entry.get('updated')
            if published:
                try:
                    # Try parsing with various methods
                    published_date = datetime(*entry.published_parsed[:6]).strftime('%Y-%m-%d %H:%M:%S') if hasattr(entry, 'published_parsed') else published
                except:
                    published_date = str(published)
            else:
                published_date = 'No published date available'
            
            # Extract full content
            full_content = extract_full_content(link)
            
            # Compile the article information
            article_info = {
                'title': title,
                'link': link,
                'summary': summary,
                'full_content': full_content,
                'published_date': published_date,
                'author': author,
                'source': source_title,
                'url_to_image': image_url
            }
            
            articles.append(article_info)
        
        except Exception as e:
            print(f"Error processing entry: {e}")
            traceback.print_exc()
    
    return articles

def scrape_multiple_feeds(feed_urls):
    """
    Scrapes articles from multiple RSS feeds and combines them into a single list
    """
    all_articles = []
    
    for feed_url in feed_urls:
        print(f"Fetching data from: {feed_url}")
        try:
            articles = scrape_rss_feed(feed_url)
            all_articles.extend(articles)
        except Exception as e:
            print(f"Error scraping feed {feed_url}: {e}")
    
    return all_articles

def save_to_json(data, base_filename='articles'):
    """
    Saves the article data to a JSON file with timestamped filename
    """
    try:
        # Create 'scrapes' directory if it doesn't exist
        os.makedirs('scrapes', exist_ok=True)
        
        # Generate timestamp for filename
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        
        # Create full filename with timestamp
        filename = os.path.join('scrapes', f'{base_filename}_{timestamp}.json')
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        print(f"Successfully saved {len(data)} articles to {filename}")
        return filename
    except Exception as e:
        print(f"Error saving to JSON: {e}")
        return None

def main():
    # List of RSS feed URLs
    rss_feed_urls = [
        "https://feeds.feedburner.com/ndtvnews-top-stories",  # NDTV Top Stories RSS feed
        "https://www.thehindu.com/news/national/feeder/default.rss",  # The Hindu National News RSS feed
        "https://www.news18.com/commonfeeds/v1/eng/rss/india.xmll"  # News18 India RSS feed
    ]
    
    # Scrape the articles from multiple feeds
    articles = scrape_multiple_feeds(rss_feed_urls)
    
    # Save the articles to a JSON file with timestamp
    save_to_json(articles)

if __name__ == "__main__":
    main()