import json
from flask import jsonify

def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)
    
config = load_config()
PROXY_URL = config.get('PROXY_URL')

# 获取分类，暂时为硬编码
def get_categories():
    categories_data = {
        "code": 200,
        "message": "success",
        "data": {
            "categories": [
                # {
                #     "title": "那年今天",
                #     "thumb": {
                #     "originalName": "old.jpg",
                #     "path": "old.jpg",
                #     "fileServer": "https://diwodiwo.xyz/static/"
                #     },
                #     "isWeb": "false",
                #     "active": "true"
                # },
                {
                    "_id": "5821859b5f6b9a4f93d12345",
                    "title": "熟肉",
                    "description": "未知",
                    "thumb": {
                        "originalName": "shurou.png",
                        "path": "assets/img/categories/shurou.png",
                        "fileServer": PROXY_URL
                    }
                },
                {
                    "_id": "5821859b5f6b9a4f93d12347",
                    "title": "生肉",
                    "description": "未知",
                    "thumb": {
                        "originalName": "shengrou.png",
                        "path": "assets/img/categories/shengrou.png",
                        "fileServer": PROXY_URL
                    }
                },
                {
                    "_id": "5821859b5f6b9a4f93d12778",
                    "title": "无修正",
                    "description": "未知",
                    "thumb": {
                        "originalName": "wuma.png",
                        "path": "assets/img/categories/wuma.png",
                        "fileServer": PROXY_URL
                    }
                },
                {
                    "_id": "5821859b5f6b9a4f93d12990",
                    "title": "长篇",
                    "description": "未知",
                    "thumb": {
                        "originalName": "changpian.png",
                        "path": "assets/img/categories/changpian.png",
                        "fileServer": PROXY_URL
                    }
                },
                {
                    "_id": "5821859b5f6b9a4f93d12123",
                    "title": "短篇",
                    "description": "未知",
                    "thumb": {
                        "originalName": "duanpian.png",
                        "path": "assets/img/categories/duanpian.png",
                        "fileServer": PROXY_URL
                    }
                },
                {
                    "_id": "5821859b5f6b9a4f93d12456",
                    "title": "AI生成",
                    "description": "未知",
                    "thumb": {
                        "originalName": "ai.png",
                        "path": "assets/img/categories/ai.png",
                        "fileServer": PROXY_URL
                    }
                },
                {
                    "_id": "5821859b5f6b9a4f93d16789",
                    "title": "萝莉",
                    "description": "未知",
                    "thumb": {
                        "originalName": "loli.png",
                        "path": "assets/img/categories/loli.png",
                        "fileServer": PROXY_URL
                    }
                }
            ]
        }
    }
    
    return jsonify(categories_data), 200
