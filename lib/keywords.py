import json
from flask import jsonify

def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)
    
config = load_config()
PROXY_URL = config.get('PROXY_URL')

# 获取常用标签
def get_keywords():
    categories_data = {
        "code": 200,
        "message": "success",
        "data": {
            "keywords": [
            "熟肉",
            "生肉",
            "长篇",
            "短篇",
            "单行本"
            ]
        }
    }
    
    return jsonify(categories_data), 200
