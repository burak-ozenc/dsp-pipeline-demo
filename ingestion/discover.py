from prefect import task 
from pathlib import Path
from itertools import islice
import hashlib

@task
def discover_files(path, limit=15):
    """
    Get wav files, hash them, get size/name etc. depending on the path
    """
    res = []
    

    for file_path in islice(Path(path).rglob("*.wav"), limit):
        project_root = Path(__file__).resolve().parent.parent  # e.g. go up from test/something.py
        relative = file_path.relative_to(project_root)
        size_bytes = str(file_path.stat().st_size).encode()
        file_hash = hashlib.sha256(size_bytes).hexdigest()
        res.append({
                    'file_path': str(relative),
                    'file_size': file_path.stat().st_size,
                    # use sha256 instead md5
                    'file_hash': file_hash,
                    'file_name': file_path.name,    
                })
        
    return res