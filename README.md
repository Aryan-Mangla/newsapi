# **News Search API**

This repository contains a news search application built with Flask for the backend, a search module to process news articles, and a basic frontend for interacting with the API. Additionally, it includes a scraper to fetch news articles and save them for later use.

---

## **File Descriptions**

### 1. **`app.py`**
The Flask backend that provides API endpoints for the application.  
It includes the following functionalities:

- **`/search`**:  
  Allows users to search for news articles based on a keyword.  
  **Method**: `GET`  
  **Query Parameter**:  
  - `q` (string): Search term.  
  **Response**:  
  Returns a JSON object with the matching articles or an error message.  

  Example cURL request:
  ```bash
  curl "http://localhost:5000/search?q=technology"

- **`/list-sources`**:  
  Lists all available JSON files (news sources) in the `scrapes` directory.  
  **Method**: `GET`  
  **Response**:  
  Returns a JSON object with the available sources.  

  Example cURL request:
  ```bash
  curl "http://localhost:5000/list-sources"
  ```

- **`/`**:  
  A home route that provides basic API information.  
  **Method**: `GET`  

---

### 2. **`news_search_module.py`**
A Python module responsible for searching through the scraped news articles stored in the `scrapes` folder.

#### **Key Functions**:

- **`whole_word_search(search_term, text)`**:
  - Performs a whole-word search within a given text to ensure that partial matches (e.g., "cat" in "category") are avoided.

- **`search_news(search_term, json_file_path=None)`**:
  - Searches news articles for the given term by looking through the `scrapes` folder.
  - If no specific JSON file is provided, it uses the most recently modified JSON file.
  - Returns a dictionary containing matching articles or an error message.

---

### 3. **`scraper.py`**
A script to scrape news articles from various sources and save them into JSON files in the `scrapes` directory.

#### **How it works**:
1. Fetches news articles from online sources.
2. Saves the scraped data in JSON format in the `scrapes` directory for later use.

You can run this script with:
```bash
python scraper.py
```

---

### 4. **`index.html`**
A simple HTML file that provides a user interface for interacting with the API.  
It allows users to:
- Enter a search term.
- View the JSON response with the matching news articles.

---

## **Enhancements Required**
Here are some suggested features to improve the application:

1. **Sort Articles by Popularity**:
   - Add functionality to sort the articles based on their popularity (e.g., number of shares, likes, or views).

2. **Cluster Articles by Topic**:
   - Group similar articles under common topics (e.g., Technology, Politics, Health).

3. **Sentiment Analysis of Articles**:
   - Implement sentiment analysis to determine the bias or tone (positive, negative, neutral) of news articles.

---

## **Getting Started**

### **1. Clone the Repository**
```bash
git clone git@github.com:haloyte/newapi.git
```

### **2. Install Dependencies**
Navigate to the project directory and install Python dependencies:
```bash
pip install -r requirements.txt
```

### **3. Run the Application**
Start the Flask backend:
```bash
python app.py
```

The application will be available at `http://localhost:5000`.

---

