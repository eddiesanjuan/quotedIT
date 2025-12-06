"""
Embedding service for semantic similarity and deduplication.

DISC-055: Semantic Learning Deduplication

Uses Claude API to generate embeddings for learning statements,
enabling semantic similarity detection and clustering-based deduplication.
"""

import asyncio
from typing import List, Dict, Any, Tuple, Optional
import anthropic
from datetime import datetime

from ..config import settings


class EmbeddingService:
    """
    Generate embeddings and compute semantic similarity for learnings.
    """

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for text using Claude's embedding model.

        For now, we'll use a simple text-based similarity approach since
        Claude doesn't have a dedicated embedding API yet. In production,
        this would use a specialized embedding model like:
        - OpenAI's text-embedding-ada-002
        - Cohere's embed-english-v3.0
        - Sentence transformers

        For this implementation, we'll create a simple hash-based similarity.
        """
        # Simple word-based vector (for demonstration)
        # In production, use proper embedding API
        words = text.lower().split()

        # Create a simple bag-of-words vector (1024 dimensions)
        # This is a placeholder - real embeddings would be much better
        vector = [0.0] * 1024

        # Simple hash-based distribution
        for i, word in enumerate(words):
            idx = hash(word) % 1024
            vector[idx] += 1.0 / len(words)

        # Normalize
        magnitude = sum(x**2 for x in vector) ** 0.5
        if magnitude > 0:
            vector = [x / magnitude for x in vector]

        return vector

    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.

        Returns:
            Float between 0 and 1, where 1 means identical
        """
        if len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(x**2 for x in vec1) ** 0.5
        magnitude2 = sum(x**2 for x in vec2) ** 0.5

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)

    async def find_similar_learnings(
        self,
        new_learning_text: str,
        existing_learnings: List[Dict[str, Any]],
        similarity_threshold: float = 0.90,
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Find existing learnings similar to the new one.

        Args:
            new_learning_text: The new learning statement
            existing_learnings: List of existing Learning dicts with embeddings
            similarity_threshold: Minimum similarity score (0.90 = very similar)

        Returns:
            List of (learning, similarity_score) tuples above threshold
        """
        # Generate embedding for new learning
        new_embedding = await self.generate_embedding(new_learning_text)

        similar = []
        for learning in existing_learnings:
            if not learning.get("embedding"):
                continue

            existing_embedding = learning["embedding"]
            similarity = self.cosine_similarity(new_embedding, existing_embedding)

            if similarity >= similarity_threshold:
                similar.append((learning, similarity))

        # Sort by similarity (highest first)
        similar.sort(key=lambda x: x[1], reverse=True)
        return similar

    async def cluster_learnings(
        self,
        learnings: List[Dict[str, Any]],
        similarity_threshold: float = 0.90,
    ) -> List[List[Dict[str, Any]]]:
        """
        Cluster learnings by semantic similarity.

        Uses simple greedy clustering:
        1. Start with first learning as cluster seed
        2. Add similar learnings to cluster
        3. Continue with unassigned learnings

        Args:
            learnings: List of Learning dicts with embeddings
            similarity_threshold: Minimum similarity to be in same cluster

        Returns:
            List of clusters, each cluster is a list of similar learnings
        """
        if not learnings:
            return []

        # Generate embeddings for learnings without them
        for learning in learnings:
            if not learning.get("embedding"):
                learning["embedding"] = await self.generate_embedding(
                    learning["adjustment"]
                )

        clusters = []
        assigned = set()

        for i, seed_learning in enumerate(learnings):
            if i in assigned:
                continue

            # Start new cluster
            cluster = [seed_learning]
            assigned.add(i)

            # Find similar unassigned learnings
            for j, candidate in enumerate(learnings):
                if j in assigned or j == i:
                    continue

                similarity = self.cosine_similarity(
                    seed_learning["embedding"],
                    candidate["embedding"]
                )

                if similarity >= similarity_threshold:
                    cluster.append(candidate)
                    assigned.add(j)

            clusters.append(cluster)

        return clusters

    def select_best_from_cluster(
        self,
        cluster: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Select the best learning from a cluster of similar learnings.

        Criteria (in order):
        1. Highest confidence
        2. Most samples
        3. Largest total impact
        4. Most recent

        Args:
            cluster: List of similar Learning dicts

        Returns:
            The best learning from the cluster
        """
        if len(cluster) == 1:
            return cluster[0]

        def score_learning(learning: Dict[str, Any]) -> Tuple:
            """Return sortable tuple (confidence, samples, impact, recency)"""
            confidence = learning.get("confidence", 0.0)
            samples = learning.get("sample_count", 0)
            impact = learning.get("total_impact_dollars", 0.0)

            # Recency: convert datetime to timestamp (higher = more recent)
            last_seen = learning.get("last_seen_at")
            if isinstance(last_seen, str):
                last_seen = datetime.fromisoformat(last_seen.replace('Z', '+00:00'))
            recency = last_seen.timestamp() if last_seen else 0.0

            return (confidence, samples, impact, recency)

        # Sort by scoring criteria
        best = max(cluster, key=score_learning)
        return best

    async def deduplicate_learnings(
        self,
        learnings: List[Dict[str, Any]],
        similarity_threshold: float = 0.90,
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Deduplicate learnings using semantic clustering.

        Args:
            learnings: List of Learning dicts
            similarity_threshold: Similarity threshold for clustering

        Returns:
            Tuple of (deduplicated_learnings, stats_dict)
        """
        if not learnings:
            return [], {"original_count": 0, "final_count": 0, "reduction": 0}

        original_count = len(learnings)

        # Cluster similar learnings
        clusters = await self.cluster_learnings(learnings, similarity_threshold)

        # Select best from each cluster
        deduplicated = []
        for cluster in clusters:
            best = self.select_best_from_cluster(cluster)

            # If cluster has multiple learnings, merge their metadata
            if len(cluster) > 1:
                # Sum sample counts
                best["sample_count"] = sum(l.get("sample_count", 1) for l in cluster)
                # Sum impact
                best["total_impact_dollars"] = sum(l.get("total_impact_dollars", 0.0) for l in cluster)
                # Take max confidence
                best["confidence"] = max(l.get("confidence", 0.5) for l in cluster)
                # Mark as deduplicated
                best["was_deduplicated"] = True
                best["merged_count"] = len(cluster)

            deduplicated.append(best)

        final_count = len(deduplicated)
        reduction = ((original_count - final_count) / original_count * 100) if original_count > 0 else 0

        stats = {
            "original_count": original_count,
            "final_count": final_count,
            "clusters_found": len(clusters),
            "reduction_percent": round(reduction, 1),
        }

        return deduplicated, stats


# Singleton
_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service() -> EmbeddingService:
    """Get the embedding service singleton."""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
