"""Verify official OpenML ARFF before training; standard library only."""
import hashlib
import json
from pathlib import Path

path=Path('data/creditcard.arff')
expected='178bcf9bb1f31a3dfe12d0e577884add'
actual=hashlib.md5(path.read_bytes()).hexdigest()
if actual!=expected:
    raise RuntimeError(f'Incomplete or unexpected file: MD5={actual}; expected={expected}')
audit={'source':'https://openml.org/data/v1/download/1673544/creditcard.arff',
       'metadata':'https://www.openml.org/api/v1/json/data/1597',
       'expected_md5':expected,'actual_md5':actual,
       'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size}
Path('reports/source_integrity.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
print(json.dumps(audit,indent=2))
