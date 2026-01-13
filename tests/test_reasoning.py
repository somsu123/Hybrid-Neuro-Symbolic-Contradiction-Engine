"""
Test simplified contradiction detector (rule-based, no models).
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from contradiction_engine.claims import Claim
from contradiction_engine.reasoning import SimplifiedContradictionDetector


def test_simplified_detector():
    """Test rule-based contradiction detection."""
    
    # Create test claims with contradictions
    claims = [
        Claim(
            entity="Lord Edmund",
            attribute="alive",
            value="alive",
            time_context="Chapter 1",
            source_text="Lord Edmund was alive and vigorous.",
            chunk_id=0,
            confidence=0.95
        ),
        Claim(
            entity="Lord Edmund",
            attribute="alive",
            value="dead",
            time_context="Chapter 5",
            source_text="Lord Edmund had died in the storm.",
            chunk_id=5,
            confidence=0.92
        ),
        Claim(
            entity="Isabella",
            attribute="wealth",
            value="poor",
            time_context="Chapter 2",
            source_text="Isabella was poor and struggling.",
            chunk_id=2,
            confidence=0.88
        ),
        Claim(
            entity="Isabella",
            attribute="wealth",
            value="rich",
            time_context="Chapter 8",
            source_text="Isabella was wealthy now.",
            chunk_id=8,
            confidence=0.90
        ),
    ]
    
    # Run detector
    detector = SimplifiedContradictionDetector(threshold=0.5)
    contradictions = detector.detect(claims)
    
    print(f"Found {len(contradictions)} contradictions:\n")
    
    for i, c in enumerate(contradictions, 1):
        print(f"[{i}] {c.entity} - {c.attribute}")
        print(f"    Values: {' vs '.join(c.values)}")
        print(f"    Locations: {' / '.join(c.locations)}")
        print(f"    Delta: {c.delta:.3f}")
        print(f"    Verdict: {c.verdict}")
        print()
    
    # Verify expected contradictions
    assert len(contradictions) >= 2, f"Expected at least 2 contradictions, found {len(contradictions)}"
    
    # Check for alive/dead contradiction
    edmund_contradictions = [c for c in contradictions if c.entity.lower().startswith('lord edmund')]
    assert len(edmund_contradictions) > 0, "Expected contradiction for Lord Edmund's alive status"
    
    # Check for rich/poor contradiction
    isabella_contradictions = [c for c in contradictions if c.entity.lower() == 'isabella']
    assert len(isabella_contradictions) > 0, "Expected contradiction for Isabella's wealth"
    
    print("✓ Simplified detector test passed")
    return contradictions


if __name__ == '__main__':
    print("Testing Simplified Contradiction Detector...\n")
    
    try:
        contradictions = test_simplified_detector()
        
        print("\n✅ All reasoning tests passed!")
        print("\nNote: Full NLI-based detection requires:")
        print("  pip install sentence-transformers transformers torch")
        print("  (This will download ~500MB of models)")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
