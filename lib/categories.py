import json
import os

from flask import jsonify

import lib.ModeSwitch as ModeSwitch

def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)
    
config = load_config()
PICABRIDGE_URL = config.get('PicaBridge_URL')

def get_categories(user_id):
    # 根据用户模式选择分类
    if ModeSwitch.GetMode(user_id) == "sfw":
        categories_key = "SFW_categories"
    else:
        categories_key = "categories"

    categories_data = config.get(categories_key, {})
    categories_list = []

    for category_name, category_info in categories_data.items():
        thumb_path = category_info["thumb"]
        original_name = os.path.basename(thumb_path)  # 提取文件名

        # 组装返回的分类数据
        category_dict = {
            "_id": category_info["id"],
            "title": category_info["title"],
            "description": category_info["description"],
            "thumb": {
                "originalName": original_name,
                "path": thumb_path,
                "fileServer": PICABRIDGE_URL
            }
        }
        categories_list.append(category_dict)

    response_data = {
        "code": 200,
        "message": "success",
        "data": {
            "categories": categories_list
        }
    }

    return jsonify(response_data), 200