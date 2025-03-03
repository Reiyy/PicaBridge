import json
from flask import jsonify
import lib.ModeSwitch as ModeSwitch

def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)
    
config = load_config()
PROXY_URL = config.get('PROXY_URL')

# 获取常用标签
def get_keywords(user_id):
    keywords_data = {
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

    sfw_keywords_data = {
        "code": 200,
        "message": "success",
        "data": {
            "keywords": [
            "无H"
            ]
        }
    }
    
    # 如果用户模式为SFW，只返回SFW分类
    if ModeSwitch.GetMode(user_id) == "sfw":
        return jsonify(sfw_keywords_data), 200
    else:
        return jsonify(keywords_data), 200

