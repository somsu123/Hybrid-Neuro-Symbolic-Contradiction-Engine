"""
CLI interface for contradiction detection engine.
Provides command-line interface with JSON output and logging.
"""

import json
import logging
import sys
from pathlib import Path
from typing import Optional
import click
from tqdm import tqdm

from .streaming import StreamingReader
from .claims_simple import ClaimExtractor, ClaimStore
from .reasoning import ContradictionDetector, SimplifiedContradictionDetector
from .config import (
    CONTRADICTION_DELTA_THRESHOLD,
    LOG_LEVEL,
    LOG_DIR
)


def setup_logging(log_level: str = LOG_LEVEL, log_file: Optional[str] = None):
    """
    Setup logging configuration.
    
    Args:
        log_level: Logging level
        log_file: Optional log file path
    """
    # Create log directory
    log_dir = Path(LOG_DIR)
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure handlers
    handlers = [logging.StreamHandler(sys.stderr)]
    
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    else:
        # Default log file
        handlers.append(logging.FileHandler(log_dir / "contradiction_engine.log"))
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )


@click.command()
@click.option(
    '--input', '-i',
    required=True,
    type=click.Path(exists=True),
    help='Input text file (novel, narrative, etc.)'
)
@click.option(
    '--threshold', '-t',
    default=CONTRADICTION_DELTA_THRESHOLD,
    type=float,
    help=f'Contradiction delta threshold (default: {CONTRADICTION_DELTA_THRESHOLD})'
)
@click.option(
    '--output', '-o',
    type=click.Choice(['json', 'pretty', 'summary'], case_sensitive=False),
    default='json',
    help='Output format'
)
@click.option(
    '--log-level',
    type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR'], case_sensitive=False),
    default=LOG_LEVEL,
    help='Logging level'
)
@click.option(
    '--simplified',
    is_flag=True,
    help='Use simplified rule-based detector (faster, no models)'
)
@click.option(
    '--reuse-claims',
    is_flag=True,
    help='Reuse previously extracted claims if available'
)
def main(
    input: str,
    threshold: float,
    output: str,
    log_level: str,
    simplified: bool,
    reuse_claims: bool
):
    """
    Hybrid Neuro-Symbolic Contradiction Engine
    
    Streams and analyzes long-form narratives to detect logical contradictions.
    """
    # Setup logging
    setup_logging(log_level)
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 60)
    logger.info("CONTRADICTION DETECTION ENGINE")
    logger.info("=" * 60)
    logger.info(f"Input: {input}")
    logger.info(f"Threshold: {threshold}")
    logger.info(f"Output format: {output}")
    logger.info(f"Simplified mode: {simplified}")
    logger.info("=" * 60)
    
    try:
        # Initialize components
        claim_store = ClaimStore()
        
        # Check for reusable claims
        claims = []
        if reuse_claims:
            logger.info("Checking for existing claims...")
            claims = claim_store.load_claims(input)
        
        # Extract claims if needed
        if not claims:
            logger.info("Starting claim extraction...")
            claims = extract_claims(input, claim_store)
            logger.info(f"Extracted {len(claims)} claims")
        else:
            logger.info(f"Reusing {len(claims)} existing claims")
        
        if not claims:
            logger.warning("No claims extracted. Exiting.")
            sys.exit(0)
        
        # Detect contradictions
        logger.info("Starting contradiction detection...")
        
        if simplified:
            detector = SimplifiedContradictionDetector(threshold=threshold)
        else:
            detector = ContradictionDetector(threshold=threshold)
        
        contradictions = detector.detect(claims)
        
        logger.info(f"Detection complete. Found {len(contradictions)} contradictions")
        
        # Output results
        output_results(contradictions, output)
        
        logger.info("=" * 60)
        logger.info("EXECUTION COMPLETE")
        logger.info("=" * 60)
    
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


def extract_claims(input_path: str, claim_store: ClaimStore) -> list:
    """
    Extract claims from input file.
    
    Args:
        input_path: Path to input file
        claim_store: ClaimStore instance
        
    Returns:
        list: Extracted claims
    """
    logger = logging.getLogger(__name__)
    
    # Initialize components
    reader = StreamingReader(input_path)
    extractor = ClaimExtractor()
    
    all_claims = []
    chunk_id = 0
    
    # Estimate progress
    estimated_chunks = reader.get_estimated_chunks()
    logger.info(f"Estimated chunks: {estimated_chunks}")
    
    # Stream and process chunks
    with tqdm(total=estimated_chunks, desc="Processing chunks", unit="chunk") as pbar:
        for chunk_text in reader.stream_chunks():
            # Extract claims from chunk
            chunk_claims = extractor.extract_from_chunk(chunk_text, chunk_id)
            all_claims.extend(chunk_claims)
            
            chunk_id += 1
            pbar.update(1)
    
    # Save claims
    logger.info("Saving claims to disk...")
    claim_store.save_claims(all_claims, input_path)
    
    return all_claims


def output_results(contradictions: list, format: str):
    """
    Output contradiction results.
    
    Args:
        contradictions: List of ContradictionResult objects
        format: Output format ('json', 'pretty', 'summary')
    """
    if format == 'json':
        # JSON array to stdout
        results = [c.to_dict() for c in contradictions]
        print(json.dumps(results, indent=2))
    
    elif format == 'pretty':
        # Human-readable format
        if not contradictions:
            print("\n✓ Consistent: No strong contradictions found\n")
        else:
            print(f"\n⚠ Found {len(contradictions)} contradiction(s):\n")
            
            for i, c in enumerate(contradictions, 1):
                print(f"[{i}] {c.entity} - {c.attribute}")
                print(f"    Values: {' vs '.join(c.values)}")
                print(f"    Locations: {' / '.join(c.locations)}")
                print(f"    Delta: {c.delta:.3f}")
                print(f"    Verdict: {c.verdict}")
                print(f"    Sources:")
                for src in c.source_texts:
                    print(f"      - {src}")
                print()
    
    elif format == 'summary':
        # Summary statistics
        print(f"\n{'=' * 60}")
        print("CONTRADICTION DETECTION SUMMARY")
        print(f"{'=' * 60}")
        print(f"Total contradictions: {len(contradictions)}")
        
        if contradictions:
            # Group by entity
            entities = set(c.entity for c in contradictions)
            print(f"Affected entities: {len(entities)}")
            
            # Average delta
            avg_delta = sum(c.delta for c in contradictions) / len(contradictions)
            print(f"Average delta: {avg_delta:.3f}")
            
            # Top contradictions
            print(f"\nTop contradictions:")
            sorted_contras = sorted(contradictions, key=lambda x: x.delta, reverse=True)
            for c in sorted_contras[:5]:
                print(f"  - {c.entity} ({c.attribute}): delta={c.delta:.3f}")
        else:
            print("\n✓ Consistent: No strong contradictions found")
        
        print(f"{'=' * 60}\n")


if __name__ == '__main__':
    main()
