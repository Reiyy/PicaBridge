from flask import jsonify
from datetime import datetime
import include.db as db

# 打开app请求平台信息，广告信息和新版本信息
def init(platform, user_id):

    if platform is None:
        response_data = {
            "status": "ok",
            "addresses": ["picaapi.reiyy.com:2333", "picaapi.reiyy.com:2333"],
            "waka": "https://picaapi.reiyy.com:2333/ad",
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
                "latestApplication": {
                    "_id": "5dc58b151e103c60e7663b12",
                    "downloadUrl": "https://picaapi.reiyy.com/assets/apps/2.2.1.3.3.4.71_collections.apk",
                    "updateContent": "【一般更新】\n\n1・无\n\n2・无\n\n後備下載連結\nhttps://picaapi.reiyy.com/assets/apps/2.2.1.3.3.4-7.1_collections.apk",
                    "version": "2.2.1.3.3.4.71",
                    "updated_at": "2019-11-08T15:38:45.706Z",
                    "created_at": "2019-11-08T15:34:45.163Z",
                    "apk": {
                        "originalName": "2.2.1.3.3.4.71_collections.apk",
                        "path": "4da05b12-3534-4b4d-b9bf-804de301d2e0.apk",
                        "fileServer": "https://picaapi.reiyy.com:2333"
                    }
                },
                "imageServer": "https://picaapi.reiyy.com:2333/static/",
                "apiLevel": 22,
                "minApiLevel": 22,
                "categories": [
                    {
                        "_id": "5821859b5f6b9a4f93dbf6e9",
                        "title": "漢化"
                    },
                    {
                        "_id": "5821859b5f6b9a4f93dbf6d5",
                        "title": "地帶"
                    }
                ],
                "notification": None,
                "isIdUpdated": True
            }
        }
        return jsonify(response_data), 200

    return jsonify({"code": 400, "message": "Invalid platform."}), 400
