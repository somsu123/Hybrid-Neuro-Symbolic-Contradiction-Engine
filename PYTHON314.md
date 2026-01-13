# Python 3.14 Compatibility Note

## Issue

spaCy currently does not support Python 3.14 due to Pydantic V1 compatibility issues.

## Solution Implemented

Created **spaCy-free claim extraction** (`claims_simple.py`) using regex patterns.

### Features:
- ✅ Works with Python 3.14+
- ✅ No heavy NLP dependencies
- ✅ Pattern-based entity-state extraction
- ✅ Detects: alive/dead, rich/poor, young/old, married/single

### Usage:

```bash
# Works immediately with Python 3.14
python main.py --input data/sample_novel.txt --output pretty --simplified
```

### Example Output:

```
⚠ Found 1 contradiction(s):

[1] Lady Catherine - age
    Values: old vs young
    Locations: Chapter 7 / Chapter 7
    Delta: 1.000
    Verdict: CONTRADICTION
    Sources:
      - The woman Isabella had met before was an imposter
      - Lady Catherine was young after all, barely eighteen
```

## For Full NLP Features (Optional)

If you need advanced claim extraction with spaCy:

1. **Use Python 3.11-3.13** (not 3.14)
2. Install dependencies:
   ```bash
   python3.11 -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

## Current Status

✅ **System is fully functional with Python 3.14** using simplified extraction
