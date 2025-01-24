import json
from flask import jsonify

def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)
    
config = load_config()
PROXY_URL = config.get('PROXY_URL')

# 横幅公告
def get_banners():
    banners_data = {
        "code": 200,
        "message": "success",
        "data": {
            "banners": [
                {
                    "_id": "toBe1",
                    "title": "Yareiy's BZLib",
                    "shortDescription": "PicaBridge",
                    "type": "web",
                    "link": "https://bzlib.home.reiyy.com:2333/",
                    "thumb": {
                        "fileServer": PROXY_URL,
                        "path": "img/2022/08/31/b44125355d4c5.png",
                        "originalName": "b44125355d4c5.png"
                    }
                }
            ]
        }
    }
    
    return jsonify(banners_data), 200