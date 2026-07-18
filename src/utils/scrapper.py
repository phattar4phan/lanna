import wikipediaapi
from pathlib import Path

def sections_to_text(section, remove_sections):
    if section.title.strip() in remove_sections:
        return ""
    
    text = section.text + "\n"
    
    for subsection in section.sections:
        text += sections_to_text(subsection, remove_sections)
        
    return text

def scrap(wiki: wikipediaapi.Wikipedia, titles: list[str], remove_sections: list | None, file: Path | str):
    if remove_sections is None:
        remove_sections = [
            "อ้างอิง",
            "ดูเพิ่ม",
            "แหล่งข้อมูลอื่น",
            "หนังสืออ่านเพิ่ม",
            "อ่านเพิ่ม",
        ]
        
    with open(file, 'a', encoding='utf-8') as f:
        for title in titles:
            print(f'Extracting: {title}...')
            page = wiki.page(title)
            
            if not page.exists():
                raise ValueError(f'"{title}" not found. Skipping...')
                continue
            
            text = page.summary + "\n"
            
            for section in page.sections:
                text += sections_to_text(section, remove_sections)
                
            f.write(text)
            f.write("\n")