"""
Hybrid reasoning core for contradiction detection.
Two-stage pipeline: Semantic Filter → Logic Juror (NLI)
"""

import logging
from dataclasses import dataclass, asdict
from typing import List, Tuple, Optional
from collections import defaultdict

from .claims import Claim
from .config import (
    SEMANTIC_MODEL,
    NLI_MODEL,
    SEMANTIC_SIMILARITY_THRESHOLD,
    CONTRADICTION_DELTA_THRESHOLD,
    BATCH_SIZE
)

logger = logging.getLogger(__name__)


@dataclass
class ContradictionResult:
    """
    Result of contradiction detection between two claims.
    """
    entity: str
    attribute: str
    values: List[str]
    locations: List[str]
    delta: float
    verdict: str  # "CONTRADICTION" or "CONSISTENT"
    source_texts: List[str]
    confidence_scores: List[float]
    
    def to_dict(self) -> dict:
        """Convert result to dictionary."""
        return asdict(self)


class ContradictionDetector:
    """
    Two-stage hybrid contradiction detector.
    
    Stage A: Semantic Filter (sentence-transformers)
    - Filter semantically similar claim pairs
    - Reduce search space
    
    Stage B: Logic Juror (Cross-Encoder NLI)
    - Determine logical relationship
    - Calculate contradiction delta
    - Make verdict decision
    """
    
    def __init__(
        self,
        threshold: float = CONTRADICTION_DELTA_THRESHOLD,
        similarity_threshold: float = SEMANTIC_SIMILARITY_THRESHOLD
    ):
        """
        Initialize contradiction detector.
        
        Args:
            threshold: Minimum delta for contradiction verdict
            similarity_threshold: Minimum similarity for Stage A filtering
        """
        self.threshold = threshold
        self.similarity_threshold = similarity_threshold
        
        # Initialize models
        self._init_models()
    
    def _init_models(self):
        """Initialize NLP models."""
        logger.info("Initializing models...")
        
        # Stage A: Semantic similarity model
        try:
            from sentence_transformers import SentenceTransformer
            self.semantic_model = SentenceTransformer(SEMANTIC_MODEL)
            logger.info(f"Loaded semantic model: {SEMANTIC_MODEL}")
        except Exception as e:
            logger.error(f"Failed to load semantic model: {e}")
            raise
        
        # Stage B: NLI cross-encoder
        try:
            from sentence_transformers import CrossEncoder
            self.nli_model = CrossEncoder(NLI_MODEL)
            logger.info(f"Loaded NLI model: {NLI_MODEL}")
        except Exception as e:
            logger.error(f"Failed to load NLI model: {e}")
            raise
        
        logger.info("Models initialized successfully")
    
    def detect(self, claims: List[Claim]) -> List[ContradictionResult]:
        """
        Detect contradictions in a list of claims.
        
        Args:
            claims: List of claims to analyze
            
        Returns:
            List[ContradictionResult]: Detected contradictions
        """
        logger.info(f"Starting contradiction detection on {len(claims)} claims")
        
        # Group claims by entity
        entity_claims = self._group_by_entity(claims)
        logger.info(f"Grouped into {len(entity_claims)} entities")
        
        all_contradictions = []
        
        # Process each entity separately
        for entity, entity_claim_list in entity_claims.items():
            if len(entity_claim_list) < 2:
                continue  # Need at least 2 claims to compare
            
            logger.debug(f"Processing entity: {entity} ({len(entity_claim_list)} claims)")
            
            # Stage A: Semantic filtering
            candidate_pairs = self._semantic_filter(entity_claim_list)
            logger.debug(f"  Stage A: {len(candidate_pairs)} candidate pairs")
            
            if not candidate_pairs:
                continue
            
            # Stage B: Logic juror
            contradictions = self._logic_juror(candidate_pairs)
            logger.debug(f"  Stage B: {len(contradictions)} contradictions")
            
            all_contradictions.extend(contradictions)
        
        logger.info(f"Detection complete. Found {len(all_contradictions)} contradictions")
        return all_contradictions
    
    def _group_by_entity(self, claims: List[Claim]) -> dict:
        """
        Group claims by entity.
        
        Args:
            claims: List of claims
            
        Returns:
            dict: Entity -> List[Claim]
        """
        entity_map = defaultdict(list)
        
        for claim in claims:
            # Normalize entity name (case-insensitive)
            normalized_entity = claim.entity.lower().strip()
            entity_map[normalized_entity].append(claim)
        
        return dict(entity_map)
    
    def _semantic_filter(self, claims: List[Claim]) -> List[Tuple[Claim, Claim]]:
        """
        Stage A: Filter semantically similar claim pairs.
        
        Args:
            claims: List of claims for same entity
            
        Returns:
            List[Tuple[Claim, Claim]]: Candidate pairs
        """
        if len(claims) < 2:
            return []
        
        # Generate embeddings for all claims
        claim_texts = [self._claim_to_text(c) for c in claims]
        embeddings = self.semantic_model.encode(
            claim_texts,
            batch_size=BATCH_SIZE,
            show_progress_bar=False,
            convert_to_tensor=False
        )
        
        # Find similar pairs
        candidate_pairs = []
        
        for i in range(len(claims)):
            for j in range(i + 1, len(claims)):
                # Compute cosine similarity
                similarity = self._cosine_similarity(embeddings[i], embeddings[j])
                
                if similarity >= self.similarity_threshold:
                    candidate_pairs.append((claims[i], claims[j]))
        
        return candidate_pairs
    
    def _logic_juror(self, pairs: List[Tuple[Claim, Claim]]) -> List[ContradictionResult]:
        """
        Stage B: Determine logical relationship using NLI.
        
        Args:
            pairs: Candidate claim pairs
            
        Returns:
            List[ContradictionResult]: Contradictions
        """
        if not pairs:
            return []
        
        contradictions = []
        
        for claim1, claim2 in pairs:
            # Format as premise-hypothesis pair
            premise = self._claim_to_text(claim1)
            hypothesis = self._claim_to_text(claim2)
            
            # Get NLI scores
            scores = self.nli_model.predict([(premise, hypothesis)])[0]
            
            # Scores: [contradiction, entailment, neutral]
            contradiction_score = scores[0]
            entailment_score = scores[1]
            
            # Calculate delta
            delta = contradiction_score - entailment_score
            
            # Make decision
            if delta >= self.threshold:
                verdict = "CONTRADICTION"
                
                # Build result
                result = ContradictionResult(
                    entity=claim1.entity,
                    attribute=claim1.attribute,
                    values=[claim1.value, claim2.value],
                    locations=[claim1.time_context, claim2.time_context],
                    delta=float(delta),
                    verdict=verdict,
                    source_texts=[claim1.source_text, claim2.source_text],
                    confidence_scores=[claim1.confidence, claim2.confidence]
                )
                
                contradictions.append(result)
                
                logger.debug(f"  Found contradiction: {claim1.entity} - {claim1.attribute}")
                logger.debug(f"    Delta: {delta:.3f}, Threshold: {self.threshold}")
        
        return contradictions
    
    def _claim_to_text(self, claim: Claim) -> str:
        """
        Convert claim to natural language text for NLI.
        
        Args:
            claim: Claim object
            
        Returns:
            str: Natural language representation
        """
        # Format: "Entity attribute value in time_context"
        text = f"{claim.entity} {claim.attribute} {claim.value}"
        if claim.time_context != "Unknown":
            text += f" in {claim.time_context}"
        
        return text
    
    def _cosine_similarity(self, vec1, vec2) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            float: Cosine similarity
        """
        import numpy as np
        
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)


class SimplifiedContradictionDetector:
    """
    Simplified detector for testing without heavy models.
    Uses rule-based logic for quick validation.
    """
    
    def __init__(self, threshold: float = CONTRADICTION_DELTA_THRESHOLD):
        """Initialize simplified detector."""
        self.threshold = threshold
        logger.info("Initialized simplified contradiction detector (rule-based)")
    
    def detect(self, claims: List[Claim]) -> List[ContradictionResult]:
        """
        Detect contradictions using rule-based logic.
        
        Args:
            claims: List of claims
            
        Returns:
            List[ContradictionResult]: Detected contradictions
        """
        logger.info(f"Starting simplified detection on {len(claims)} claims")
        
        # Group by entity and attribute
        entity_attr_map = defaultdict(list)
        
        for claim in claims:
            key = (claim.entity.lower(), claim.attribute.lower())
            entity_attr_map[key].append(claim)
        
        contradictions = []
        
        # Look for different values for same entity-attribute
        for (entity, attribute), claim_list in entity_attr_map.items():
            if len(claim_list) < 2:
                continue
            
            # Check for opposing values
            values_seen = {}
            for claim in claim_list:
                value_key = claim.value.lower().strip()
                
                if value_key not in values_seen:
                    values_seen[value_key] = claim
            
            # Now check all pairs for contradictions
            value_items = list(values_seen.items())
            for i in range(len(value_items)):
                for j in range(i + 1, len(value_items)):
                    value1, claim1 = value_items[i]
                    value2, claim2 = value_items[j]
                    
                    if self._are_contradictory(value1, value2):
                        result = ContradictionResult(
                            entity=claim1.entity,
                            attribute=attribute,
                            values=[claim1.value, claim2.value],
                            locations=[claim1.time_context, claim2.time_context],
                            delta=1.0,  # Rule-based, max delta
                            verdict="CONTRADICTION",
                            source_texts=[claim1.source_text, claim2.source_text],
                            confidence_scores=[claim1.confidence, claim2.confidence]
                        )
                        contradictions.append(result)
        
        logger.info(f"Simplified detection complete. Found {len(contradictions)} contradictions")
        return contradictions
    
    def _are_contradictory(self, value1: str, value2: str) -> bool:
        """
        Check if two values are contradictory.
        
        Args:
            value1: First value
            value2: Second value
            
        Returns:
            bool: True if contradictory
        """
        # Known opposing pairs
        opposing_pairs = [
            ('alive', 'dead'),
            ('rich', 'poor'),
            ('married', 'single'),
            ('present', 'absent'),
            ('young', 'old'),
        ]
        
        v1 = value1.lower().strip()
        v2 = value2.lower().strip()
        
        if v1 == v2:
            return False
        
        # Check opposing pairs
        for pair in opposing_pairs:
            if (v1 in pair[0] and v2 in pair[1]) or (v1 in pair[1] and v2 in pair[0]):
                return True
        
        return False
