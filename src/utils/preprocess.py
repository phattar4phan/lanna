import re

from pathlib import Path
from typing import Any

def remove_blank_lines(file: Path | str) -> None:
    with open(file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    with open(file, 'w', encoding='utf-8') as f:
        f.writelines(line for line in lines if line.strip())
    
def find_duplicate(lists: list[Any]):
    seen = set()
    duplicates = []
    
    for item in lists:
        if item in seen and item not in duplicates:
            duplicates.append(item)
        else:
            seen.add(item)    
    
    return duplicates