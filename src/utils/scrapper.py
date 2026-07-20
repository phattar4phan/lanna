import time
import wikipediaapi

from pathlib import Path
from colorama import Fore, init

init(autoreset=True)

def sections_to_text(section, remove_sections):
    if section.title.strip() in remove_sections:
        return ""
    
    text = section.text + "\n"
    
    for subsection in section.sections:
        text += sections_to_text(subsection, remove_sections)
        
    return text

def scrap(wiki: wikipediaapi.Wikipedia, titles: list[str], remove_sections: list | None, file: Path | str) -> tuple[int, list[str]]:
    if remove_sections is None:
        remove_sections = [
            "อ้างอิง",
            "ดูเพิ่ม",
            "แหล่งข้อมูลอื่น",
            "หนังสืออ่านเพิ่ม",
            "อ่านเพิ่ม",
        ]
    
    total = len(titles)
    missing = []
    
    with open(file, 'a', encoding='utf-8') as f:
        for title in titles:
            start = time.perf_counter()
            
            page = wiki.page(title)
            
            if not page.exists():
                missing.append(title)
                print(f'{Fore.RED}Error{Fore.RESET}:"{title}" not found. Skipping...')
                continue

            text = page.summary + "\n"
            
            for section in page.sections:
                text += sections_to_text(section, remove_sections)
                
            f.write(text)
            f.write("\n")
            end = time.perf_counter()
            print(f'{Fore.CYAN}Extracted{Fore.RESET}: {title} | {Fore.LIGHTBLUE_EX}{(end-start):.2f}s')
            
    return total, missing