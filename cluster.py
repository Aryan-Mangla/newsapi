import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

def optimize_clusters(articles, max_clusters=10):
    """
    Find the optimal number of clusters using multiple methods
    
    Parameters:
    - articles: List of dictionaries with 'summary' or 'description'
    - max_clusters: Maximum number of clusters to test
    
    Returns:
    - Optimal number of clusters
    - Detailed cluster analysis
    """
    # Extract text summaries
    summaries = [article.get('summary', article.get('description', '')) for article in articles]
    
    # Vectorize text using TF-IDF
    vectorizer = TfidfVectorizer(
        stop_words='english',
        max_features=1000,
        max_df=0.7,
        min_df=2
    )
    tfidf_matrix = vectorizer.fit_transform(summaries)
    
    # Elbow Method & Silhouette Score
    elbow_scores = []
    silhouette_scores = []
    
    for n_clusters in range(2, max_clusters + 1):
        # Perform clustering
        kmeans = KMeans(
            n_clusters=n_clusters, 
            random_state=42, 
            n_init=10
        )
        cluster_labels = kmeans.fit_predict(tfidf_matrix)
        
        # Elbow method (inertia/within-cluster sum of squares)
        elbow_scores.append(kmeans.inertia_)
        
        # Silhouette score (measure of how similar an object is to its own cluster)
        try:
            silhouette_avg = silhouette_score(tfidf_matrix, cluster_labels)
            silhouette_scores.append(silhouette_avg)
        except:
            silhouette_scores.append(0)
    
    # Determine optimal clusters
    optimal_clusters = determine_optimal_clusters(
        elbow_scores, 
        silhouette_scores
    )
    
    return optimal_clusters

def determine_optimal_clusters(elbow_scores, silhouette_scores):
    """
    Determine the optimal number of clusters using elbow method and silhouette score
    """
    # Elbow Method (looking for the "elbow" point)
    elbow_diffs = np.diff(elbow_scores)
    elbow_second_diffs = np.diff(elbow_diffs)
    
    # Silhouette Score (higher is better)
    max_silhouette_index = np.argmax(silhouette_scores) + 2  # +2 because we started at 2 clusters
    
    # Combine methods
    print("\nCluster Optimization Analysis:")
    print("Elbow Scores:", elbow_scores)
    print("Silhouette Scores:", silhouette_scores)
    
    # Heuristic: choose the point where rate of decrease slows down
    # or the point with the highest silhouette score
    print(f"\nRecommended number of clusters: {max_silhouette_index}")
    print(f"Based on highest silhouette score of {silhouette_scores[max_silhouette_index-2]:.4f}")
    
    return max_silhouette_index

def cluster_articles(articles, n_clusters):
    """
    Cluster articles using the optimal number of clusters
    """
    # Extract text summaries
    summaries = [article.get('summary', article.get('description', '')) for article in articles]
    
    # Vectorize text
    vectorizer = TfidfVectorizer(
        stop_words='english',
        max_features=1000,
        max_df=0.7,
        min_df=2
    )
    tfidf_matrix = vectorizer.fit_transform(summaries)
    
    # Cluster
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(tfidf_matrix)
    
    # Add clusters to articles
    clustered_articles = []
    for article, label in zip(articles, cluster_labels):
        article_copy = article.copy()
        article_copy['cluster'] = int(label)
        clustered_articles.append(article_copy)
    
    return clustered_articles

def main():
    # Load articles
    with open('search_results.json', 'r') as f:
        data = json.load(f)
    
    articles = data.get("articles", [])
    
    # Check if articles are in the expected format
    if not articles or not isinstance(articles[0], dict):
        print("Error: articles data is not in the expected format")
        return
    
    # Find optimal number of clusters
    optimal_clusters = optimize_clusters(articles)
    
    # Cluster articles
    clustered_articles = cluster_articles(articles, optimal_clusters)
    
    # Analyze clusters
    analyze_clusters(clustered_articles)
    
    # Save clustered articles
    with open('clustered_articles.json', 'w') as f:
        json.dump(clustered_articles, f, indent=2)


def analyze_clusters(clustered_articles):
    """
    Analyze and print key characteristics of each cluster
    """
    # Group articles by cluster
    cluster_groups = {}
    for article in clustered_articles:
        cluster = article['cluster']
        if cluster not in cluster_groups:
            cluster_groups[cluster] = []
        cluster_groups[cluster].append(article)
    
    # Print cluster summaries
    for cluster, articles in cluster_groups.items():
        print(f"\nCluster {cluster}:")
        print(f"Number of articles: {len(articles)}")
        
        # Sample headlines or first few words from summaries
        print("Sample headlines:")
        for article in articles[:3]:
            print(f"- {article.get('title', 'N/A')[:100]}...")

if __name__ == '__main__':
    main()