"""
Lightweight claim extraction without spaCy dependency.
Uses simple regex and text patterns for Python 3.14 compatibility.
"""

import re
import json
import hashlib
import logging
from dataclasses import dataclass, asdict
from typing import List, Optional, Generator
from pathlib import Path

from .config import (
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


class SimplifiedClaimExtractor:
    """
    Simplified claim extractor using regex patterns.
    No spaCy dependency - works with Python 3.14+
    """
    
    def __init__(self):
        """Initialize simplified extractor."""
        self.current_time_context = "Unknown"
        logger.info("Initialized simplified claim extractor (no spaCy)")
        
        # Common name patterns (capitalized words)
        self.name_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
        
        # State patterns (entity, value, attribute)
        self.state_patterns = [
            # alive/dead patterns
            (r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:was|is|were)\s+(alive|dead|living)', 'alive'),
            (r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:died|perished)', 'alive', 'dead'),
            
            # wealth patterns
            (r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:was|is|were)\s+(wealthy|rich|poor|destitute)', 'wealth'),
            
            # age patterns
            (r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:was|is|were)\s+(young|old|aged)', 'age'),
            
            # marital status
            (r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:was|is|were)\s+(married|single|widowed)', 'marital_status'),
        ]
    
    def extract_from_chunk(
        self, 
        text: str, 
        chunk_id: int,
        time_context: Optional[str] = None
    ) -> List[Claim]:
        """
        Extract claims from text chunk using regex.
        
        Args:
            text: Input text
            chunk_id: Chunk identifier
            time_context: Optional temporal context
            
        Returns:
            List[Claim]: Extracted claims
        """
        claims = []
        
        # Update time context
        if time_context is None:
            detected_context = self._detect_time_context(text)
            if detected_context:
                self.current_time_context = detected_context
        else:
            self.current_time_context = time_context
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        
        for sent in sentences:
            if len(sent.strip()) < 10:  # Skip very short sentences
                continue
            
            # Try each pattern
            for pattern_data in self.state_patterns:
                if len(pattern_data) == 3:
                    pattern, attribute, implicit_value = pattern_data
                    has_implicit_value = True
                else:
                    pattern, attribute = pattern_data
                    has_implicit_value = False
                
                matches = re.finditer(pattern, sent, re.IGNORECASE)
                
                for match in matches:
                    entity = match.group(1).strip()
                    
                    # Get value from match or use implicit
                    if has_implicit_value:
                        value = implicit_value
                    else:
                        if len(match.groups()) >= 2:
                            value = match.group(2).strip().lower()
                        else:
                            continue  # Skip if no value captured
                    
                    # Filter out common non-names
                    if self._is_likely_name(entity):
                        claim = Claim(
                            entity=entity,
                            attribute=attribute,
                            value=value,
                            time_context=self.current_time_context,
                            source_text=sent.strip(),
                            chunk_id=chunk_id,
                            confidence=0.8  # Fixed confidence for regex extraction
                        )
                        claims.append(claim)
        
        logger.debug(f"Extracted {len(claims)} claims from chunk {chunk_id}")
        return claims
    
    def _is_likely_name(self, text: str) -> bool:
        """
        Check if text looks like a person's name.
        
        Args:
            text: Text to check
            
        Returns:
            bool: True if likely a name
        """
        # Must start with capital letter
        if not text or not text[0].isupper():
            return False
        
        # Filter out common non-names
        non_names = {'The', 'A', 'An', 'This', 'That', 'These', 'Those', 
                     'It', 'He', 'She', 'They', 'What', 'When', 'Where'}
        
        first_word = text.split()[0]
        if first_word in non_names:
            return False
        
        # Name should be relatively short (< 50 chars)
        if len(text) > 50:
            return False
        
        return True
    
    def _detect_time_context(self, text: str) -> Optional[str]:
        """
        Detect temporal context from text.
        
        Args:
            text: Input text
            
        Returns:
            Optional[str]: Detected context or None
        """
        for keyword in TEMPORAL_KEYWORDS:
            pattern = rf'\b{keyword}\s+([IVX\d]+)\b'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return f"{keyword.title()} {match.group(1)}"
        
        return None


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


# Alias for compatibility
ClaimExtractor = SimplifiedClaimExtractor
