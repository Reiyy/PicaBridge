import requests
import json
import time

from flask import jsonify

import lib.db as db
import lib.api as api

def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

config = load_config()
LRR_URL = config.get('lrr_Api')
PICABRIDGE_URL = config.get('PicaBridge_URL')

# 获取排行榜
def get_comic_leaderboard(tt):
    lanraragi_data = api.get_all_archives()  # 获取所有漫画元数据

    if lanraragi_data is None:
        return jsonify({"code": 500, "message": "Failed to fetch archives."}), 500

    # 检查返回的数据是否是列表
    if isinstance(lanraragi_data, list):
        comics_list = lanraragi_data
    else:
        return jsonify({"code": 500, "message": "Invalid data format."}), 500

    # 继续处理comics_list，提取arcid 
    comic_ids = [comic["arcid"] for comic in comics_list]

    # 定义用于排序的访问量字典
    leaderboard_data = {}

    # 根据不同的参数计算访问量
    for comic_id in comic_ids:
        comic_info = db.get_comic_info(comic_id)  # 获取漫画信息

        # 如果找不到漫画信息，跳过当前循环
        if comic_info is None:
            continue

        if tt == 'D30':
            # 历史总浏览量
            leaderboard_data[comic_id] = comic_info.get("viewsCount", 0)

        elif tt == 'H24' or tt == 'D7':
            # 获取viewed_at数据并计算7天或30天的浏览量
            viewed_at = comic_info.get("viewed_at", [])
            viewed_at = json.loads(viewed_at) if viewed_at else []
            current_timestamp = int(time.time())  # 当前时间戳

            if tt == 'H24':
                threshold_timestamp = current_timestamp - (7 * 24 * 60 * 60)
            elif tt == 'D7':
                threshold_timestamp = current_timestamp - (30 * 24 * 60 * 60)

            # 计算指定时间范围内的浏览量
            count = sum(1 for ts in viewed_at if int(ts) > threshold_timestamp)
            leaderboard_data[comic_id] = count

    # 按访问量降序排序
    # sorted_leaderboard = sorted(leaderboard_data.items(), key=lambda x: x[1], reverse=True)
    # 按访问量降序排序并过滤访问量为0的漫画
    sorted_leaderboard = sorted(
        ((comic_id, count) for comic_id, count in leaderboard_data.items() if count > 0),
        key=lambda x: x[1],
        reverse=True
    )

    # 组装返回数据
    comics_data = []
    for comic_id, count in sorted_leaderboard:
        comic_info = db.get_comic_info(comic_id)  # 再次获取漫画信息以获取详细数据
        # 如果找不到漫画信息，跳过当前循环
        if comic_info is None:
            continue
        thumbnail_path = f"thumbnail/{comic_id}"
        
        comic_data = {
            "_id": comic_id,
            "title": comic_info.get("title", "未知标题"),
            "author": comic_info.get("author", "未知作者"),
            "totalViews": comic_info.get("viewsCount", 0),
            "totalLikes": comic_info.get("likesCount"),
            "pagesCount": comic_info.get("pagecount"),
            "epsCount": comic_info.get("epsCount", 1),
            "finished": bool(comic_info.get("finished", True)),
            "categories": json.loads(comic_info.get("categories", '[]')) if isinstance(comic_info.get("categories"), str) else comic_info.get("categories", ["未知分类"]),
            "thumb": {
                "originalName": f"{comic_id}.jpg",
                "path": thumbnail_path,
                "fileServer": PICABRIDGE_URL
            },
            "viewsCount": comic_info.get("viewsCount", 0),
            "leaderboardCount": count
        }
        comics_data.append(comic_data)

    # 返回数据
    response_data = {
        "code": 200,
        "message": "success",
        "data": {
            "comics": comics_data,
        }
    }

    return jsonify(response_data), 200

# 获取用户排行榜
def get_knight_leaderboard():
    user_ids = db.get_all_userid()
    user_data = []

    # 请求一次API以获取库中漫画总数作为comics_uploaded数据
    try:
        comics_uploaded_response = requests.get(f"{LRR_URL}/api/search?start=0", timeout=2)
        comics_uploaded_response.raise_for_status()
        comics_uploaded = comics_uploaded_response.json().get("recordsTotal", 0)
        print(f"库中漫画总数: {comics_uploaded}")
    except requests.exceptions.RequestException as e:
        print(f"没有获取到漫画总数数据: {e}")
        comics_uploaded = 0  # 默认值为0

    # 遍历用户ID，构建用户数据
    for index, user_id in enumerate(user_ids, start=1):
        user_info = db.get_user_info(user_id)
        if user_info:
            user_data.append({
                "_id": user_id,
                "gender": user_info.get("gender"),
                "name": user_info.get("name"),
                "slogan": user_info.get("description"),
                "title": user_info.get("title"),
                "verified": bool(user_info.get("verified", False)),
                "exp": user_info.get("exp"),
                "level": user_info.get("level"),
                "characters": json.loads(user_info.get("characters", '[]')) if isinstance(user_info.get("characters"), str) else user_info.get("characters", [""]),
                "role": user_info.get("role"),
                "avatar": {
                    "originalName": user_info.get("avatar").split("/")[-1],
                    "path": "/".join(user_info.get("avatar").split("/")[3:]),
                    "fileServer": PICABRIDGE_URL
                },
                "comicsUploaded": comics_uploaded,
                "character": user_info.get("frame")
            })
            print(f"Processed user {index}/{len(user_ids)} (ID: {user_id})")

    # 根据经验值排序
    user_data.sort(key=lambda x: x["exp"], reverse=True)

    # 构建响应数据
    response_data = {
        "code": 200,
        "message": "success",
        "data": {
            "users": user_data
        }
    }

    return jsonify(response_data), 200
