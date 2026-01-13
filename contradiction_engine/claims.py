"""
Claim extraction module for converting text into atomic factual claims.
Uses spaCy for NER and dependency parsing with conservative extraction.
"""

import json
import hashlib
import logging
from dataclasses import dataclass, asdict
from typing import List, Optional, Generator
from pathlib import Path
import re

from .config import (
    ALL_STATE_VERBS, 
    TEMPORAL_KEYWORDS, 
    MIN_CLAIM_CONFIDENCE,
    CLAIMS_DIR
)

logger = logging.getLogger(__name__)


@dataclass
class Claim:
    """
    Atomic factual claim extracted from text.
    
    Schema: <entity, attribute, value, time_context>
    """
    entity: str          # Character or object name
    attribute: str       # Property being described
    value: str           # State or value
    time_context: str    # Chapter, act, or location marker
    source_text: str     # Original sentence
    chunk_id: int        # Source chunk index
    confidence: float    # Extraction confidence (0-1)
    
    def to_dict(self) -> dict:
        """Convert claim to dictionary."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert claim to JSON string."""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Claim':
        """Create claim from JSON string."""
        data = json.loads(json_str)
        return cls(**data)
    
    def __hash__(self):
        """Hash claim for deduplication."""
        return hash((self.entity, self.attribute, self.value, self.time_context))


class ClaimExtractor:
    """
    Extract atomic claims from text using spaCy NLP.
    
    Conservative extraction strategy:
    - Focus on state-changing verbs
    - Extract only explicit facts
    - Skip ambiguous or metaphorical statements
    - Stateless processing per chunk
    """
    
    def __init__(self, model_name: str = "en_core_web_sm"):
        """
        Initialize claim extractor.
        
        Args:
            model_name: spaCy model name
        """
        try:
            import spacy
            self.nlp = spacy.load(model_name)
            logger.info(f"Loaded spaCy model: {model_name}")
        except OSError:
            logger.error(f"spaCy model '{model_name}' not found. Run: python -m spacy download {model_name}")
            raise
        
        self.current_time_context = "Unknown"
    
    def extract_from_chunk(
        self, 
        text: str, 
        chunk_id: int,
        time_context: Optional[str] = None
    ) -> List[Claim]:
        """
        Extract claims from a text chunk.
        
        Args:
            text: Input text chunk
            chunk_id: Chunk identifier
            time_context: Optional temporal context override
            
        Returns:
            List[Claim]: Extracted claims
        """
        claims = []
        
        # Update time context if found
        if time_context is None:
            detected_context = self._detect_time_context(text)
            if detected_context:
                self.current_time_context = detected_context
        else:
            self.current_time_context = time_context
        
        # Process text with spaCy
        doc = self.nlp(text)
        
        # Extract claims from sentences
        for sent in doc.sents:
            sent_claims = self._extract_from_sentence(sent, chunk_id)
            claims.extend(sent_claims)
        
        logger.debug(f"Extracted {len(claims)} claims from chunk {chunk_id}")
        return claims
    
    def _extract_from_sentence(self, sent, chunk_id: int) -> List[Claim]:
        """
        Extract claims from a single sentence.
        
        Args:
            sent: spaCy Span object
            chunk_id: Chunk identifier
            
        Returns:
            List[Claim]: Extracted claims
        """
        claims = []
        
        # Look for state-changing verbs
        for token in sent:
            if token.lemma_.lower() in ALL_STATE_VERBS or token.text.lower() in ALL_STATE_VERBS:
                # Found state verb, try to extract claim
                claim = self._build_claim_from_verb(token, sent, chunk_id)
                if claim:
                    claims.append(claim)
        
        return claims
    
    def _build_claim_from_verb(self, verb_token, sent, chunk_id: int) -> Optional[Claim]:
        """
        Build claim from state-changing verb.
        
        Args:
            verb_token: spaCy Token (verb)
            sent: spaCy Span (sentence)
            chunk_id: Chunk identifier
            
        Returns:
            Optional[Claim]: Extracted claim or None
        """
        # Find subject (entity)
        entity = None
        for child in verb_token.children:
            if child.dep_ in ('nsubj', 'nsubjpass'):
                entity = self._get_entity_text(child)
                break
        
        if not entity:
            return None
        
        # Find object/complement (value)
        value = None
        attribute = verb_token.lemma_
        
        for child in verb_token.children:
            if child.dep_ in ('attr', 'acomp', 'dobj', 'oprd'):
                value = self._get_value_text(child)
                break
            elif child.dep_ == 'prep':
                # Handle "is in location", "became of age", etc.
                for prep_child in child.children:
                    if prep_child.dep_ == 'pobj':
                        value = self._get_value_text(prep_child)
                        attribute = f"{verb_token.lemma_}_{child.text}"
                        break
        
        # For "died", "dead" - value is implicit
        if verb_token.lemma_ in ('die', 'kill') and not value:
            value = 'dead'
            attribute = 'alive'
        
        if not value:
            return None
        
        # Calculate confidence (simple heuristic)
        confidence = self._calculate_confidence(sent.text)
        
        if confidence < MIN_CLAIM_CONFIDENCE:
            return None
        
        # Build claim
        claim = Claim(
            entity=entity,
            attribute=attribute,
            value=value,
            time_context=self.current_time_context,
            source_text=sent.text.strip(),
            chunk_id=chunk_id,
            confidence=confidence
        )
        
        return claim
    
    def _get_entity_text(self, token) -> str:
        """
        Extract entity text including modifiers.
        
        Args:
            token: spaCy Token
            
        Returns:
            str: Entity text
        """
        # Get full noun phrase if available
        if token.ent_type_:
            return token.text
        
        # Include determiners and modifiers
        text_parts = []
        for child in token.lefts:
            if child.dep_ in ('det', 'amod', 'compound'):
                text_parts.append(child.text)
        
        text_parts.append(token.text)
        return ' '.join(text_parts)
    
    def _get_value_text(self, token) -> str:
        """
        Extract value text including modifiers.
        
        Args:
            token: spaCy Token
            
        Returns:
            str: Value text
        """
        text_parts = [token.text]
        
        # Include modifiers
        for child in token.children:
            if child.dep_ in ('amod', 'advmod', 'neg'):
                text_parts.insert(0, child.text)
        
        return ' '.join(text_parts)
    
    def _detect_time_context(self, text: str) -> Optional[str]:
        """
        Detect temporal context from text (e.g., "Chapter 5").
        
        Args:
            text: Input text
            
        Returns:
            Optional[str]: Detected context or None
        """
        for keyword in TEMPORAL_KEYWORDS:
            # Look for patterns like "Chapter 5", "Act II", etc.
            pattern = rf'\b{keyword}\s+([IVX\d]+)\b'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return f"{keyword.title()} {match.group(1)}"
        
        return None
    
    def _calculate_confidence(self, text: str) -> float:
        """
        Calculate extraction confidence based on linguistic features.
        
        Args:
            text: Sentence text
            
        Returns:
            float: Confidence score (0-1)
        """
        confidence = 1.0
        
        # Reduce confidence for uncertain language
        uncertainty_markers = ['maybe', 'perhaps', 'possibly', 'might', 'could', 'seemed']
        for marker in uncertainty_markers:
            if marker in text.lower():
                confidence -= 0.3
        
        # Reduce confidence for metaphorical language
        metaphor_markers = ['like', 'as if', 'metaphorically', 'figuratively']
        for marker in metaphor_markers:
            if marker in text.lower():
                confidence -= 0.4
        
        # Reduce confidence for questions
        if text.strip().endswith('?'):
            confidence -= 0.5
        
        return max(0.0, min(1.0, confidence))


class ClaimStore:
    """
    Persistent storage for claims using JSONL format.
    """
    
    def __init__(self, base_dir: str = CLAIMS_DIR):
        """
        Initialize claim store.
        
        Args:
            base_dir: Base directory for claim storage
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Initialized claim store at {base_dir}")
    
    def save_claims(self, claims: List[Claim], document_path: str) -> Path:
        """
        Save claims to JSONL file.
        
        Args:
            claims: List of claims
            document_path: Source document path
            
        Returns:
            Path: Saved file path
        """
        # Create hash-based filename
        doc_hash = hashlib.md5(document_path.encode()).hexdigest()[:16]
        output_file = self.base_dir / f"{doc_hash}.jsonl"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for claim in claims:
                f.write(claim.to_json() + '\n')
        
        logger.info(f"Saved {len(claims)} claims to {output_file}")
        return output_file
    
    def load_claims(self, document_path: str) -> List[Claim]:
        """
        Load claims from JSONL file.
        
        Args:
            document_path: Source document path
            
        Returns:
            List[Claim]: Loaded claims
        """
        doc_hash = hashlib.md5(document_path.encode()).hexdigest()[:16]
        input_file = self.base_dir / f"{doc_hash}.jsonl"
        
        if not input_file.exists():
            logger.warning(f"Claims file not found: {input_file}")
            return []
        
        claims = []
        with open(input_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    claims.append(Claim.from_json(line))
        
        logger.info(f"Loaded {len(claims)} claims from {input_file}")
        return claims
    
    def stream_claims(self, document_path: str) -> Generator[Claim, None, None]:
        """
        Stream claims from JSONL file (memory-efficient).
        
        Args:
            document_path: Source document path
            
        Yields:
            Claim: Individual claims
        """
        doc_hash = hashlib.md5(document_path.encode()).hexdigest()[:16]
        input_file = self.base_dir / f"{doc_hash}.jsonl"
        
        if not input_file.exists():
            logger.warning(f"Claims file not found: {input_file}")
            return
        
        with open(input_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    yield Claim.from_json(line)
