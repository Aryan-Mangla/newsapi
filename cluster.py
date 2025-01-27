import json
import numpy as np
from sklearn.cluster import DBSCAN
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

def load_articles(json_path):
    """
    Load articles from a JSON file.
    
    Expected JSON structure:
    [
        {"title": "Article Title", "content": "Article Text"},
        ...
    ]
    """
    with open(json_path, 'r', encoding='utf-8') as file:
        return json.load(file)


def embed_articles(articles, model_name='roberta-base-nli-stsb-mean-tokens'):
    """
    Generate embeddings for articles using a sentence transformer.

    Args:
        articles (list): List of article dictionaries
        model_name (str): Sentence transformer model to use

    Returns:
        tuple: (embeddings, processed_articles)
    """
    # Initialize model
    model = SentenceTransformer(model_name)

    # Extract text to embed (combine title and content)
    texts = [f"{article.get('title', '')}" for article in articles]

    # Generate embeddings with an appropriate prompt
    prompt = "Generate embeddings that emphasize article similarity."
    embeddings = model.encode(texts)

    return embeddings, articles


def cluster_articles(embeddings, eps=0.3, min_samples=2):
    """
    Cluster articles using DBSCAN algorithm.
    
    Args:
        embeddings (np.array): Article embeddings
        eps (float): Maximum distance between two samples to be considered in the same neighborhood
        min_samples (int): Minimum number of samples in a neighborhood for a point to be considered a core point
    
    Returns:
        list: Cluster assignments for each article
    """
    # Perform clustering
    clustering = DBSCAN(
        eps=eps, 
        min_samples=min_samples, 
        metric='cosine'
    ).fit(embeddings)
    
    return clustering.labels_

def analyze_clusters(articles, embeddings, labels):
    """
    Analyze and print out the clusters.
    
    Args:
        articles (list): Original articles
        embeddings (np.array): Article embeddings
        labels (list): Cluster labels
    """
    # Group articles by cluster
    clusters = {}
    for idx, label in enumerate(labels):
        if label != -1:  # Ignore noise points
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(articles[idx])
    
    # Print cluster details
    print(f"Total Clusters Found: {len(clusters)}")
    for cluster_id, cluster_articles in clusters.items():
        print(f"\nCluster {cluster_id}:")
        for article in cluster_articles:
            print(f"- {article.get('title', 'Untitled')[:100]}...")
    
    # Optional: Return clusters for further processing
    return clusters

def main(json_path):
    """
    Main function to orchestrate article clustering.
    
    Args:
        json_path (str): Path to JSON file containing articles
    """
    # Load articles
    
    articles = load_articles(json_path)
    
    # Generate embeddings
    embeddings, processed_articles = embed_articles(articles)
    
    # Cluster articles
    cluster_labels = cluster_articles(embeddings)
    
    # Analyze and print clusters
    clusters = analyze_clusters(processed_articles, embeddings, cluster_labels)
    print(clusters)
    
    return clusters


