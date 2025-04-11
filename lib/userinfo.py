import math
import json
import os
import base64
import random
import string

from flask import jsonify
from datetime import datetime

import lib.db as db

def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)
    
config = load_config()
PICABRIDGE_URL = config.get('PicaBridge_URL')
    
# 用户信息
def user_info(user_id):
    user_info = db.get_user_info(user_id) or {}
    last_punch_in_timestamp = db.get_users_isPunched(user_id)
    # 获取当前日期
    today = datetime.now().date()
    
    # 判断签到时间是否在今天之前
    last_punch_in_date = datetime.fromtimestamp(last_punch_in_timestamp).date()
    # 如果最后签到时间在今天前，则为未签到，如果在今天内，则已签到过
    is_punched = last_punch_in_date == today

    # 按哔咔格式组装返回信息
    formatted_info = {
        "_id": user_info.get("id"),
        "birthday": user_info.get("birthday").strftime('%Y-%m-%dT00:00:00.000Z'),
        "email": user_info.get("email"),
        "gender": user_info.get("gender"),
        "name": user_info.get("name"),
        "slogan": user_info.get("description"),
        "title": user_info.get("title"),
        "verified": user_info.get("verified") == 1,
        "exp": user_info.get("exp"),
        "level": user_info.get("level"),
        "characters": user_info.get("characters") if isinstance(user_info.get("characters"), list) else [],
        "created_at": user_info.get("createdate").isoformat() + 'Z',
        "avatar": {
            "originalName": user_info.get("avatar").split("/")[-1],  # 提取文件名
            "path": "/".join(user_info.get("avatar").split("/")[3:]),  # 提取路径
            #"fileServer": "/".join(user_info.get("avatar").split("/")[:3])
            "fileServer": PICABRIDGE_URL # 域
        },
        "isPunched": is_punched
    }

    response_data = {
        "code": 200,
        "message": "success",
        "data": {
            "user": formatted_info
        }
    }

    return jsonify(response_data), 200

# 用户资料
def get_user_profile(user_id):
    user_info = db.get_user_info(user_id)  # 从数据库获取用户信息

    if not user_info:
        return jsonify({"code": 404, "message": "User not found"}), 404

    # 组装用户数据
    user_data = {
        "_id": user_id,
        "gender": user_info.get("gender"),
        "name": user_info.get("name"),
        "slogan": user_info.get("description"),
        "title": user_info.get("title"),
        "verified": bool(user_info.get("verified", False)),
        "exp": user_info.get("exp"),
        "level": user_info.get("level"),
        "avatar": {
            "fileServer": PICABRIDGE_URL,
            "path": "/".join(user_info.get("avatar", "").split("/")[3:]),  # 获取路径
            "originalName": user_info.get("avatar").split("/")[-1] if user_info.get("avatar") else ""
        },
        "character": user_info.get("frame")
    }

    # 返回数据
    response_data = {
        "code": 200,
        "message": "success",
        "data": {
            "user": user_data
        }
    }

    return jsonify(response_data), 200

# 收藏漫画列表
def get_favourite_comics(user_id, page, s):

    # 获取用户信息
    user_info = db.get_user_info(user_id)
    favourite = json.loads(user_info.get("favourite", "[]")) if user_info.get("favourite") else []
    
    # 根据排序标记排序,dd从新到旧，da从旧到新
    reverse_order = True if s == "dd" else False
    sorted_favourite = sorted(favourite.items(), key=lambda x: x[1], reverse=reverse_order)

    comictotal = len(favourite)
    comics_data = []
    
    # 遍历所有漫画ID从数据库获取对应的元数据
    for comic_id in sorted_favourite:
        comic_data = db.get_comic_info(comic_id) or {}

        # 组装漫画信息数据
        comic_info = {
            "_id": comic_id,
            "title": comic_data.get("title"),
            "author": comic_data.get("author"),
            "totalViews": comic_data.get("viewsCount"),
            "totalLikes": comic_data.get("likesCount"),
            "pagesCount": comic_data.get("pagesCount"),
            "epsCount": comic_data.get("epsCount"),
            "finished": bool(comic_data.get("finished")),
            "categories": json.loads(comic_data.get("categories", '[]')) if isinstance(comic_data.get("categories"), str) else comic_data.get("categories", ["未知分类"]),
            "thumb": {
                "originalName": f"{comic_id}.jpg",
                "path": f"thumbnail/{comic_id}",
                "fileServer": PICABRIDGE_URL
            },
            "likesCount": comic_data.get("likesCount")
        }
        comics_data.append(comic_info)

    # 处理分页数据
    total = comictotal
    limit = 20
    pages = math.ceil(total / limit)

    # 返回数据
    response_data = {
        "code": 200,
        "message": "success",
        "data": {
            "comics": {
                "docs": comics_data,
                "total": total,
                "limit": limit,
                "page": page,
                "pages": pages
            }
        }
    }

    return jsonify(response_data), 200

# 设置用户简介
def set_user_description(user_id, json_data):
    # 提取文本
    text = json_data.get("slogan", "")
    # 调用数据库写入函数
    if db.write_user_description(user_id, text):
        return {"code": 200, "message": "success"}
    else:
        return {"code": 500, "message": "Failed to update description."}
    
# 签到
def punch_in(user_id):
    # 获取用户的签到时间戳
    last_punch_in_timestamp = db.get_users_isPunched(user_id)

    # 获取今天的日期
    today = datetime.now().date()
    
    # 判断签到时间是否在今天之前
    last_punch_in_date = datetime.fromtimestamp(last_punch_in_timestamp).date()

    if last_punch_in_date < today:  # 还没有签到
        db.update_users_isPunched(user_id)  # 更新签到状态
        current_date = today.strftime("%Y-%m-%d")  # 格式化当前日期
        
        response_data = {
            "code": 200,
            "message": "success",
            "data": {
                "res": {
                    "status": "ok",
                    "punchInLastDay": current_date
                }
            }
        }
        return jsonify(response_data), 200

    return jsonify({"code": 200, "message": "Already punched in today."}), 200

# 上传头像
def upload_avatar(user_id, picdata):
    # 从配置文件获取文件存储路径
    with open('config.json', 'r') as f:
        config = json.load(f)
    avatarfilepath = config.get("avatarfilepath")
    
    # 解码 base64 数据
    header, encoded = picdata.split(',', 1)
    binary_data = base64.b64decode(encoded)

    # 构建存储路径
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=3))
    avatar_path = os.path.join(avatarfilepath, f"{user_id}{random_suffix}.jpg")

    # 保存文件
    with open(avatar_path, 'wb') as avatar_file:
        avatar_file.write(binary_data)

    # 获取数据库连接
    connection = db.get_db_connection()
    try:
        middle_url = '/assets/img/avatar/'
        filename = f"{user_id}{random_suffix}.jpg"
        
        # 构造头像 URL
        avatar_url = f"{PICABRIDGE_URL}{middle_url}{filename}"

        # 更新数据库中对应用户的头像URL
        with connection.cursor() as cursor:
            sql = "UPDATE users SET avatar = %s WHERE id = %s"
            cursor.execute(sql, (avatar_url, user_id))
        
        # 提交更改
        connection.commit()

    finally:
        connection.close()

    return {"code": 200, "message": "Avatar uploaded successfully."}