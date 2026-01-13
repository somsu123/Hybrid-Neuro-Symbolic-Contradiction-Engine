# Hybrid Neuro-Symbolic Contradiction Engine

A CPU-only falsification engine for detecting high-confidence logical contradictions in long-form narratives (100k+ words).

## 🎯 Philosophy

This system **falsifies claims**, not explains stories. It:

- ❌ Does NOT assume narratives are coherent
- ❌ Does NOT attempt to fix contradictions
- ✅ Prefers false negatives over false positives
- ✅ Outputs "Consistent" when uncertain

## 🏗️ Architecture

```
┌─────────────────┐
│  Novel Text     │
└────────┬────────┘
         │ Binary Stream
         ▼
┌─────────────────┐
│ Streaming       │
│ Ingestion       │
└────────┬────────┘
         │ Chunks
         ▼
┌─────────────────┐
│ Claim           │
│ Extraction      │ (spaCy NLP)
└────────┬────────┘
         │ <entity, attribute, value, time>
         ▼
┌─────────────────┐
│ Claims Store    │ (JSONL persistence)
└────────┬────────┘
         │ Claim Pairs
         ▼
┌─────────────────┐
│ Stage A:        │
│ Semantic Filter │ (sentence-transformers)
└────────┬────────┘
         │ Related Pairs
         ▼
┌─────────────────┐
│ Stage B:        │
│ Logic Juror     │ (Cross-Encoder NLI)
└────────┬────────┘
         │ Delta Scores
         ▼
┌─────────────────┐
│ Decision Engine │ (delta ≥ threshold)
└────────┬────────┘
         │ JSON
         ▼
┌─────────────────┐
│ CLI Output      │
└─────────────────┘
```

## 📦 Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Download spaCy Model

```bash
python -m spacy download en_core_web_sm
```

### 3. Generate Test Data (Optional)

```bash
python generate_test_data.py
```

This creates a 100k+ word synthetic novel with intentional contradictions in `data/sample_novel.txt`.

## 🌐 Web Deployment (Render)

The engine includes a Flask web API for deployment on cloud platforms like Render.

### Deploy to Render

1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
   git push -u origin main
   ```

2. **Create Render Web Service:**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Render will auto-detect the `render.yaml` configuration

3. **Or Manual Setup:**
   - **Name:** contradiction-engine
   - **Build Command:** `pip install -r requirements.txt && python -m spacy download en_core_web_sm`
   - **Start Command:** `gunicorn app:app`
   - **Health Check Path:** `/api/health`

4. **Done!** Your API will be live at `https://your-app.onrender.com`

5. link deployed:- https://hybrid-neuro-symbolic-contradiction.onrender.com/

### Run Web Interface Locally

```bash
python app.py
```

Then open `http://localhost:5000` in your browser.

### API Endpoints

**POST /api/detect**
- Upload file or send text for contradiction detection
- Request (multipart/form-data):
  ```
  file: <text file>
  threshold: 0.5 (optional)
  ```
- Request (JSON):
  ```json
  {
    "text": "Your narrative text...",
    "threshold": 0.5
  }
  ```
- Response:
  ```json
  {
    "status": "contradictions_found",
    "word_count": 1500,
    "claims_count": 42,
    "contradictions_count": 3,
    "contradictions": [...]
  }
  ```

**GET /api/health**
- Health check endpoint
- Returns: `{"status": "healthy"}`

**GET /api/sample**
- Get sample text with contradictions
- Returns: `{"text": "...", "description": "..."}`

**GET /api/info**
- System information
- Returns: API configuration details


## 🚀 Usage

### Basic Usage

```bash
python main.py --input data/sample_novel.txt
```

### With Custom Threshold

```bash
python main.py --input data/sample_novel.txt --threshold 0.7
```

### Output Formats

**JSON (default):**
```bash
python main.py --input data/sample_novel.txt --output json
```

**Pretty (human-readable):**
```bash
python main.py --input data/sample_novel.txt --output pretty
```

**Summary (statistics):**
```bash
python main.py --input data/sample_novel.txt --output summary
```

### Simplified Mode (Faster, Rule-Based)

```bash
python main.py --input data/sample_novel.txt --simplified
```

**Note:** Simplified mode uses rule-based logic instead of NLI models. Faster but less accurate.

### Reuse Extracted Claims

```bash
python main.py --input data/sample_novel.txt --reuse-claims
```

Claims are automatically saved to `data/claims/` after first extraction.

## 📊 Output Format

### JSON Output

```json
[
  {
    "entity": "Lord Edmund Blackwood",
    "attribute": "alive",
    "values": ["alive", "dead"],
    "locations": ["Chapter 3", "Chapter 5"],
    "delta": 2.81,
    "verdict": "CONTRADICTION",
    "source_texts": [
      "Lord Edmund was alive and vigorous.",
      "Lord Edmund Blackwood had died in Ravencrest."
    ],
    "confidence_scores": [0.95, 0.92]
  }
]
```

### Pretty Output

```
⚠ Found 3 contradiction(s):

[1] Lord Edmund Blackwood - alive
    Values: alive vs dead
    Locations: Chapter 3 / Chapter 5
    Delta: 2.810
    Verdict: CONTRADICTION
    Sources:
      - Lord Edmund was alive and vigorous.
      - Lord Edmund Blackwood had died in Ravencrest.
```

### Summary Output

```
============================================================
CONTRADICTION DETECTION SUMMARY
============================================================
Total contradictions: 3
Affected entities: 2
Average delta: 1.847

Top contradictions:
  - Lord Edmund Blackwood (alive): delta=2.810
  - Isabella Ashton (wealth): delta=1.523
  - Lady Catherine (age): delta=1.208
============================================================
```

## ⚙️ Configuration

Edit `contradiction_engine/config.py` to customize:

```python
# Models
SEMANTIC_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
NLI_MODEL = "cross-encoder/nli-deberta-v3-small"

# Thresholds
SEMANTIC_SIMILARITY_THRESHOLD = 0.6  # Semantic filtering
CONTRADICTION_DELTA_THRESHOLD = 0.5  # Contradiction decision

# Performance
CHUNK_SIZE = 4096  # Bytes per read
BATCH_SIZE = 16    # Embedding batch size
```

## 🧪 Testing

### Test Streaming

```bash
python -c "from contradiction_engine.streaming import StreamingReader; \
reader = StreamingReader('data/sample_novel.txt'); \
print(f'Chunks: {reader.get_estimated_chunks()}')"
```

### Test Claim Extraction

```bash
python -c "from contradiction_engine.claims import ClaimExtractor; \
ex = ClaimExtractor(); \
claims = ex.extract_from_chunk('Lord Edmund was wealthy.', 0); \
print(f'Claims: {len(claims)}')"
```

## 📈 Performance Benchmarks

Expected performance on laptop-grade hardware (CPU-only):

| Document Size | Extraction Time | Detection Time | Peak RAM |
|--------------|----------------|----------------|----------|
| 50k words    | ~2 minutes     | ~3 minutes     | ~2 GB    |
| 100k words   | ~4 minutes     | ~6 minutes     | ~3 GB    |
| 200k words   | ~8 minutes     | ~12 minutes    | ~5 GB    |

**Note:** Times vary based on CPU speed. First run is slower due to model loading.

## 🔍 How It Works

### 1. Streaming Ingestion

- Reads text in 4KB binary chunks
- No full document loads into memory
- Aligns chunks to sentence boundaries
- Handles UTF-8 encoding errors gracefully

### 2. Claim Extraction

- Uses spaCy for NER and dependency parsing
- Focuses on state-changing verbs (is, was, died, became, etc.)
- Extracts claims in schema: `<entity, attribute, value, time_context>`
- Conservative approach: skips ambiguous statements
- Saves claims to JSONL for reuse

### 3. Contradiction Detection

**Stage A: Semantic Filter**
- Groups claims by entity
- Embeds claims using sentence-transformers
- Computes cosine similarity
- Filters pairs with similarity ≥ 0.6
- **Purpose:** Reduce search space (not a decision maker)

**Stage B: Logic Juror**
- Uses Cross-Encoder NLI model
- Formats claims as premise-hypothesis pairs
- Computes: `[contradiction, entailment, neutral]` scores
- Calculates: `delta = contradiction_score - entailment_score`
- **Decision:** If `delta ≥ threshold` → CONTRADICTION

### 4. Decision Policy

```python
if delta >= THRESHOLD:
    verdict = "CONTRADICTION"
else:
    verdict = "CONSISTENT"
```

No soft language. No probabilistic hedging. Binary decision.

## 🚨 Known Limitations

| Scenario | Behavior | Why |
|----------|----------|-----|
| Metaphorical language | May miss or flag incorrectly | NLP models struggle with figurative speech |
| Unreliable narrator | Outputs: Consistent | Cannot infer narrative intent |
| Time travel plots | May flag false positive | Temporal context confusion |
| Name collisions | May conflate entities | NER limitations |

**Mitigation:** Conservative extraction, high thresholds, manual review of flagged contradictions.

## 📁 Project Structure

```
llm/
├── contradiction_engine/
│   ├── __init__.py           # Package init
│   ├── config.py             # Configuration
│   ├── streaming.py          # Binary streaming
│   ├── claims.py             # Claim extraction
│   ├── reasoning.py          # Hybrid NLI detector
│   └── cli.py                # CLI interface
├── data/
│   ├── sample_novel.txt      # Test data
│   └── claims/               # Persisted claims
├── logs/                     # Execution logs
├── main.py                   # Entry point
├── requirements.txt          # Dependencies
└── generate_test_data.py     # Test data generator
```

## 🐛 Troubleshooting

### Model Loading Errors

```
OSError: [E050] Can't find model 'en_core_web_sm'
```

**Solution:**
```bash
python -m spacy download en_core_web_sm
```

### Memory Issues

If you encounter OOM errors:
1. Reduce `BATCH_SIZE` in `config.py`
2. Reduce `CHUNK_SIZE` for smaller memory footprint
3. Use `--simplified` mode (no heavy models)

### Slow Performance

- **First run is slow:** Models are downloaded/cached
- **CPU-only is inherently slow:** Expected behavior
- **Use `--reuse-claims`:** Skip re-extraction on repeated runs
- **Try `--simplified`:** Faster rule-based detection

## 📝 License

This project is provided as-is for research and educational purposes.

## 🤝 Contributing

This is a systems-focused research tool. Contributions should prioritize:
- Correctness over creativity
- Stability over speed
- False negatives over false positives

## 📧 Support

Check logs in `logs/contradiction_engine.log` for debugging information.
