"""
Configuration management for contradiction detection engine.
Centralized settings for models, thresholds, and performance tuning.
"""

# Model Configuration
SEMANTIC_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # 22MB, CPU-friendly
NLI_MODEL = "cross-encoder/nli-deberta-v3-small"  # CPU-compatible cross-encoder

# Threshold Configuration
SEMANTIC_SIMILARITY_THRESHOLD = 0.6  # Minimum similarity to consider claims related
CONTRADICTION_DELTA_THRESHOLD = 0.5  # Minimum delta for contradiction verdict

# Streaming Configuration
CHUNK_SIZE = 4096  # Bytes per read operation
MAX_SENTENCE_BUFFER = 5  # Maximum sentences to buffer for complete chunks

# Performance Configuration
BATCH_SIZE = 16  # Batch size for embedding generation
MAX_WORKERS = 1  # CPU-only, sequential processing

# Claim Extraction Configuration
MIN_CLAIM_CONFIDENCE = 0.7  # Minimum confidence for claim extraction
TEMPORAL_KEYWORDS = ['chapter', 'act', 'scene', 'part', 'book', 'section']

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_DIR = "logs"
CLAIMS_DIR = "data/claims"

# State-changing verbs for claim extraction
STATE_VERBS = {
    'be': ['is', 'was', 'were', 'am', 'are', 'been', 'being'],
    'become': ['became', 'becomes', 'becoming'],
    'die': ['died', 'dies', 'dying', 'dead'],
    'kill': ['killed', 'kills', 'killing'],
    'marry': ['married', 'marries', 'marrying'],
    'leave': ['left', 'leaves', 'leaving'],
    'arrive': ['arrived', 'arrives', 'arriving'],
    'own': ['owned', 'owns', 'owning'],
    'possess': ['possessed', 'possesses', 'possessing'],
}

# Flatten state verbs for quick lookup
ALL_STATE_VERBS = set()
for verb_list in STATE_VERBS.values():
    ALL_STATE_VERBS.update(verb_list)
