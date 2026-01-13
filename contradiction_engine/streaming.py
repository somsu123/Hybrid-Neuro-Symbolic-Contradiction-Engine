"""
Streaming ingestion layer for binary-level text processing.
Handles incremental reading without loading full documents into memory.
"""

import io
import logging
from typing import Generator, Optional
from pathlib import Path

from .config import CHUNK_SIZE, MAX_SENTENCE_BUFFER

logger = logging.getLogger(__name__)


class StreamingReader:
    """
    Binary-level streaming reader that processes text incrementally.
    
    Key features:
    - No full document loads
    - Sentence boundary detection
    - UTF-8 error handling
    - Zero filesystem locks
    """
    
    def __init__(self, filepath: str, chunk_size: int = CHUNK_SIZE):
        """
        Initialize streaming reader.
        
        Args:
            filepath: Path to text file
            chunk_size: Bytes per read operation
        """
        self.filepath = Path(filepath)
        self.chunk_size = chunk_size
        
        if not self.filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        logger.info(f"Initialized streaming reader for {filepath}")
        logger.info(f"Chunk size: {chunk_size} bytes")
    
    def stream_chunks(self) -> Generator[str, None, None]:
        """
        Stream text in sentence-aligned chunks.
        
        Yields:
            str: Text chunks aligned to sentence boundaries
        """
        sentence_buffer = []
        incomplete_sentence = ""
        chunk_id = 0
        
        try:
            with io.open(self.filepath, 'rb') as f:
                while True:
                    # Read binary chunk
                    binary_chunk = f.read(self.chunk_size)
                    if not binary_chunk:
                        break
                    
                    # Decode with error handling
                    try:
                        text_chunk = binary_chunk.decode('utf-8')
                    except UnicodeDecodeError:
                        # Handle partial UTF-8 sequences at chunk boundaries
                        text_chunk = binary_chunk.decode('utf-8', errors='ignore')
                        logger.warning(f"UTF-8 decode error in chunk {chunk_id}, skipping malformed bytes")
                    
                    # Combine with incomplete sentence from previous chunk
                    text_chunk = incomplete_sentence + text_chunk
                    
                    # Split into sentences
                    sentences = self._split_sentences(text_chunk)
                    
                    # Check if last sentence is complete
                    if sentences and not text_chunk.rstrip().endswith(('.', '!', '?', '"', "'")):
                        incomplete_sentence = sentences[-1]
                        sentences = sentences[:-1]
                    else:
                        incomplete_sentence = ""
                    
                    # Add to buffer
                    sentence_buffer.extend(sentences)
                    
                    # Yield when buffer reaches threshold
                    if len(sentence_buffer) >= MAX_SENTENCE_BUFFER:
                        yield ' '.join(sentence_buffer)
                        chunk_id += 1
                        sentence_buffer = []
                
                # Yield remaining sentences
                if sentence_buffer or incomplete_sentence:
                    final_chunk = ' '.join(sentence_buffer)
                    if incomplete_sentence:
                        final_chunk += ' ' + incomplete_sentence
                    if final_chunk.strip():
                        yield final_chunk
                        chunk_id += 1
                
                logger.info(f"Streaming complete. Total chunks: {chunk_id}")
        
        except Exception as e:
            logger.error(f"Error during streaming: {e}")
            raise
    
    def _split_sentences(self, text: str) -> list[str]:
        """
        Split text into sentences using simple heuristics.
        
        Args:
            text: Input text
            
        Returns:
            list[str]: Sentences
        """
        # Simple sentence splitting (can be enhanced with nltk/spacy if needed)
        sentences = []
        current = ""
        
        for char in text:
            current += char
            if char in '.!?' and len(current) > 1:
                # Check for common abbreviations
                if not self._is_abbreviation(current):
                    sentences.append(current.strip())
                    current = ""
        
        # Add remaining text
        if current.strip():
            sentences.append(current.strip())
        
        return sentences
    
    def _is_abbreviation(self, text: str) -> bool:
        """
        Check if sentence ending looks like an abbreviation.
        
        Args:
            text: Text ending with period
            
        Returns:
            bool: True if likely an abbreviation
        """
        common_abbrev = ['Mr.', 'Mrs.', 'Dr.', 'Ms.', 'Prof.', 'Sr.', 'Jr.', 
                         'vs.', 'etc.', 'i.e.', 'e.g.', 'Inc.', 'Ltd.']
        
        for abbrev in common_abbrev:
            if text.rstrip().endswith(abbrev):
                return True
        
        return False
    
    def get_file_size(self) -> int:
        """
        Get file size in bytes.
        
        Returns:
            int: File size
        """
        return self.filepath.stat().st_size
    
    def get_estimated_chunks(self) -> int:
        """
        Estimate number of chunks based on file size.
        
        Returns:
            int: Estimated chunk count
        """
        file_size = self.get_file_size()
        return (file_size // self.chunk_size) + 1
