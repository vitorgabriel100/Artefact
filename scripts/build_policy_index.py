"""Run from the project root: python scripts/build_policy_index.py (requires pymupdf)."""
import hashlib
import json
from pathlib import Path
import pymupdf

source = Path('data/politicas_da_loja.pdf')
with pymupdf.open(source) as doc:
    index = {'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
             'pages':[{'page':i+1,'text':p.get_text()} for i,p in enumerate(doc)]}
Path('data/policies_index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2),encoding='utf-8')
