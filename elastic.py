from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import math
from elasticsearch import Elasticsearch


def search_supervisors(topics):
    es_client = Elasticsearch(
        cloud_id="My_deployment:dXMtY2VudHJhbDEuZ2NwLmNsb3VkLmVzLmlvOjQ0MyQ1YzEzN2JlMTA1OGE0ZjFhYWRlMTY4ZWU5MTJlNmQ4ZSQ4NWE2ZDMxZjY0OTQ0MGEyYTM2OTIwNDQ0NzhmZGI0Yw==",
        basic_auth=("elastic", "qGoRfbDIeA8FRCFCc2h1h9jI"),
    )


    # Define the TF-IDF vectorizer
    tfidf_vectorizer = TfidfVectorizer(min_df=2, max_df=0.5, ngram_range=(1, 2), stop_words='english')

    # Get all documents from Elasticsearch
    res = es_client.search(index="staffers", size=1000)
    hits = res['hits']['hits']

    # Collect the areas of expertise for each hit
    doc_vectors = []
    doc_ids = []
    for hit in hits:
        areas_of_expertise = hit['_source'].get('Areas_of _expertise')
        if areas_of_expertise:
            doc_vectors.append(areas_of_expertise.lower())
            doc_ids.append(hit['_id'])

    # Compute the TF-IDF vectors of the documents
    doc_vectors = tfidf_vectorizer.fit_transform(doc_vectors)

    # Compute the cosine similarity between the query and the document vectors
    query_vector = tfidf_vectorizer.transform(topics)
    similarity_scores = cosine_similarity(query_vector, doc_vectors).flatten()

    # Compute the minimum number of matching words required for a hit to be considered a match
    min_match = 2
    query_words = set(topics[0].split())

    # Collect the top results and their metadata
    supervisors = []
    for i, score in enumerate(similarity_scores):
        hit = hits[i]
        areas_of_expertise = hit['_source'].get('Areas_of _expertise')
        if not areas_of_expertise:
            continue
        hit_words = set(areas_of_expertise.split())
        match_count = len(query_words & hit_words)
        if match_count >= min_match:
            supervisor = {
                "Name": hit['_source']['Name'],
                "Email address": hit['_source']['Email address'],
                "Similarity score": score,
                "Matched words": list(query_words & hit_words)
            }
            supervisors.append(supervisor)

    return supervisors


topics = ["Assessing the usability and effectiveness of voice recognition technology in electronic health records systems"]
supervisors = search_supervisors(topics)
print(supervisors)