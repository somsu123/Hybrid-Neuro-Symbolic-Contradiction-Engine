"""
Unit tests for streaming ingestion layer.
"""

from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from contradiction_engine.streaming import StreamingReader


def test_streaming_reader_initialization():
    """Test reader initialization."""
    reader = StreamingReader('data/sample_novel.txt')
    assert reader.filepath.exists()
    assert reader.chunk_size > 0


def test_get_file_size():
    """Test file size retrieval."""
    reader = StreamingReader('data/sample_novel.txt')
    size = reader.get_file_size()
    assert size > 0
    print(f"File size: {size:,} bytes")


def test_estimated_chunks():
    """Test chunk estimation."""
    reader = StreamingReader('data/sample_novel.txt')
    chunks = reader.get_estimated_chunks()
    assert chunks > 0
    print(f"Estimated chunks: {chunks}")


def test_stream_chunks():
    """Test chunk streaming."""
    reader = StreamingReader('data/sample_novel.txt')
    chunks = list(reader.stream_chunks())
    
    assert len(chunks) > 0
    print(f"Actual chunks: {len(chunks)}")
    print(f"First chunk length: {len(chunks[0])} chars")
    print(f"First chunk preview: {chunks[0][:200]}...")


if __name__ == '__main__':
    print("Testing Streaming Reader...\n")
    
    try:
        test_streaming_reader_initialization()
        print("✓ Initialization test passed")
        
        test_get_file_size()
        print("✓ File size test passed")
        
        test_estimated_chunks()
        print("✓ Chunk estimation test passed")
        
        test_stream_chunks()
        print("✓ Streaming test passed")
        
        print("\n✅ All streaming tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
