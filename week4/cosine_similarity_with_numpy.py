import numpy as np

def cosine_similarity(vec1, vec2):
    """Compute similarity between two embeddings (0-1, higher = more similar)"""
    dot_product = np.dot(vec1, vec2)
    norm_vec1 = np.linalg.norm(vec1)
    norm_vec2 = np.linalg.norm(vec2)
    return dot_product / (norm_vec1 * norm_vec2)

# Example
embedding1 = np.array([0.1, 0.2, 0.3])
embedding2 = np.array([0.1, 0.2, 0.3])
embedding3 = np.array([0.1, 0.2, 0.31])
embedding4 = np.array([0.9, 0.8, 0.7])

print(cosine_similarity(embedding1, embedding2))  # 1.0 (identical)
print(cosine_similarity(embedding1, embedding3))  # ~0.9998 (similar)
print(cosine_similarity(embedding1, embedding4))  # ~0.8826 (distinct)
