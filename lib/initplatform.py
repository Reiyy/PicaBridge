from flask import jsonify
from datetime import datetime
import lib.db as db

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
                    "_id": "3ed58b151e103c60e7663b19",
                    "downloadUrl": "https://picaapi.reiyy.com:2333/assets/app_updates/2.7.0.1.2.2-398-lspatched_sign.apk",
                    "updateContent": "【强制更新】\n\n发布前测试第二版\n由于签名更改，本次更新需要卸载后重新安装！\n请点击“镜像下载“来下载更新！本次更新完成后，此后更新即可正常点击下载更新按钮下载了\nAPP更新日志：\n1.修改了更新下载按钮的名称\nHookMyPica 2.7.0.1更新：\n1.移除了隐藏更新弹出按钮的hook\n2.新增修改下载链接拼接逻辑的hook\n\n本更新为强制更新，如不更新无法将正常使用！",
                    "version": "2.7.0.1.2.2",
                    "updated_at": "2025-03-10T01:39:07.363Z",
                    "created_at": "2025-03-10T01:39:07.363Z",
                    "apk": {
                        "originalName": "2.7.0.1.2.2-398-lspatched_sign.apk",
                        "path": "assets/app_updates/2.7.0.1.2.2-398-lspatched_sign.apk",
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
