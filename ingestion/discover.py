from prefect import flow, task 
import pathlib
from itertools import islice
import hashlib

@task
def discover_files(path, limit=10):
    res = []
    for file_path in islice( pathlib.Path(path).rglob("*.wav"), limit):
        res.append({
            'file_path': str(file_path.relative_to(path)),
            'file_size': str(file_path.stat().st_size),
            'file_hash': hashlib.md5(file_path.read_bytes()).hexdigest(),
            'file_name': file_path.name,    
        })
        
    return res