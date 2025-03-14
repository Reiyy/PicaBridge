import json

from flask import jsonify
from datetime import datetime

import lib.db as db

# 读取 JSON 配置文件
def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

config = load_config()

PICABRIDGE_URL = config.get('PicaBridge_URL', '')

# 打开app请求平台信息，广告信息和新版本信息
def init(platform, user_id):
    addresses = PICABRIDGE_URL.replace('https://', '').replace('http://', '')
    if platform is None:
        response_data = {
            "status": "ok",
            "addresses": [addresses, addresses],
            "waka": f"{PICABRIDGE_URL}/ad",
            "adKeyword": "diwodiwo"
        }
        return jsonify(response_data), 200
    
    elif platform == 'android':
        last_punch_in_timestamp = db.get_users_isPunched(user_id)
        today = datetime.now().date()
        last_punch_in_date = datetime.fromtimestamp(last_punch_in_timestamp).date()
        is_punched = last_punch_in_date == today

        response_data = {
            "code": 200,
            "message": "success",
            "data": {
                "isPunched": is_punched,
                "latestApplication": config["initPlatform"]["latestApplication"],
                "imageServer": config["initPlatform"]["imageServer"],
                "apiLevel": 22,
                "minApiLevel": 22,
                "categories": [
                    {
                        "_id": "233333333333333333333333",
                        "title": "2333"
                    }
                ],
                "notification": None,
                "isIdUpdated": True
            }
        }
        return jsonify(response_data), 200

    return jsonify({"code": 400, "message": "Invalid platform."}), 400
