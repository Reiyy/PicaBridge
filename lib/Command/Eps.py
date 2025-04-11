import json
import sqlite3

def parse_eps_tags(tags):
    eps_data = {}
    index = 1
    
    for tag in tags.split(","):
        if tag.startswith("哔咔桥:eps"):
            eps_values = tag.split(":", 1)[-1].replace("eps", "").split("/")
            
            for value in eps_values:
                eps_data[f"ep{index}"] = {
                    "title": f"第{index}话",
                    "id": value
                }
                index += 1
            
    return eps_data

def update_comic_eps(database_path, data, comicid):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    
    for item in data.get("data", []):
        tags = item.get("tags", "")
        eps_json = parse_eps_tags(tags)
        
        if eps_json:
            eps_json_str = json.dumps(eps_json, ensure_ascii=False)
            cursor.execute("""
                UPDATE comic_info 
                SET eps = ? 
                WHERE id = ?
            """, (eps_json_str, comicid))
            
            conn.commit()
    
    conn.close()