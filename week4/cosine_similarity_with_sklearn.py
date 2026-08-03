# Cosine Similarity (most common)
# Range: -1 to 1 (higher = more similar)
# 1.0 = identical, 0.0 = unrelated, -1.0 = opposite

from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

embedding1 = np.array([0.1, 0.2, 0.3])
embedding2 = np.array([0.1, 0.2, 0.3])
embedding3 = np.array([0.1, 0.2, 0.31])
embedding4 = np.array([0.9, 0.8, 0.7])

print(cosine_similarity([embedding1], [embedding2])[0][0])  # 0.9999 (identical)
print(cosine_similarity([embedding1], [embedding3])[0][0])  # 0.9998 (similar)
print(cosine_similarity([embedding1], [embedding4])[0][0])  # 0.8826 (distinct)
