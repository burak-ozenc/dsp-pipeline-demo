from prefect import flow, task 
import pathlib
from itertools import islice
import hashlib

@task
def discover_files(path, limit=10):
    """
    Get wav files, hash them, get size/name etc. depending on the path
    """
    res = []
    for file_path in islice( pathlib.Path(path).rglob("*.wav"), limit):
        res.append({
            'file_path': str(file_path.relative_to(path)),
            'file_size': file_path.stat().st_size,
            # use sha256 instead md5
            'file_hash': hashlib.sha256(file_path.stat().st_size).hexdigest(),
            'file_name': file_path.name,    
        })
        
    return res