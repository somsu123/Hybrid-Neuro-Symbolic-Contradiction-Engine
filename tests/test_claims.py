"""
Simple test for claim extraction without heavy dependencies.
Run this before installing spaCy to verify structure.
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from contradiction_engine.claims import Claim


def test_claim_dataclass():
    """Test claim data structure."""
    claim = Claim(
        entity="Lord Edmund",
        attribute="wealth",
        value="wealthy",
        time_context="Chapter 1",
        source_text="Lord Edmund was wealthy.",
        chunk_id=0,
        confidence=0.95
    )
    
    print(f"Entity: {claim.entity}")
    print(f"Attribute: {claim.attribute}")
    print(f"Value: {claim.value}")
    print(f"Context: {claim.time_context}")
    print(f"Confidence: {claim.confidence}")
    
    # Test serialization
    json_str = claim.to_json()
    print(f"\nJSON: {json_str}")
    
    # Test deserialization
    claim2 = Claim.from_json(json_str)
    assert claim2.entity == claim.entity
    assert claim2.value == claim.value
    
    print("\n✓ Claim structure test passed")


def test_claim_store():
    """Test claim persistence."""
    from contradiction_engine.claims import ClaimStore
    
    claims = [
        Claim("Edmund", "alive", "true", "Ch1", "Edmund was alive.", 0, 0.9),
        Claim("Edmund", "alive", "false", "Ch5", "Edmund died.", 5, 0.95),
    ]
    
    store = ClaimStore()
    filepath = store.save_claims(claims, "test_document.txt")
    
    print(f"\nSaved to: {filepath}")
    
    # Load back
    loaded = store.load_claims("test_document.txt")
    print(f"Loaded {len(loaded)} claims")
    
    assert len(loaded) == len(claims)
    print("✓ Claim store test passed")


if __name__ == '__main__':
    print("Testing Claim Structures...\n")
    
    try:
        test_claim_dataclass()
        test_claim_store()
        
        print("\n✅ All claim tests passed!")
        print("\nNote: Full extraction tests require spaCy:")
        print("  pip install spacy")
        print("  python -m spacy download en_core_web_sm")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
