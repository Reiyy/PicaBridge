import requests
import math
import json
import time

from flask import jsonify, redirect

import lib.db as db
import lib.api as api
import lib.ModeSwitch as ModeSwitch


def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

config = load_config()
LRR_URL = config.get('lrr_Api')
PICABRIDGE_URL = config.get('PicaBridge_URL')

def redirect_thumbnail(arcid):
    try:
        lanraragi_thumbnail_url = f"{LRR_URL}/api/archives/{arcid}/thumbnail"
        print(f"Redirecting to: {lanraragi_thumbnail_url}")  # 调试输出
        return redirect(lanraragi_thumbnail_url, code=302)
    except Exception as e:
        print(f"Error: {e}")  # 输出错误信息到控制台
        return jsonify({"code": 500, "message": "Internal Server Error", "detail": str(e)}), 500

# 获取漫画数据
def get_comics_data(user_id, page, s=None, c=None, t=None, a=None):
    config = load_config()  # 加载配置文件
    start = (page - 1) * 20

    # 排序方式
    # 新到旧
    if s == "dd":
        sortby = "date_added"
        order = "desc"
    # 旧到新
    elif s == "da":
        sortby = "date_added"
        order = "asc"
    else:
        sortby = None
        order = None

    # 如果用户模式为SFW，只返回SFW漫画
    if ModeSwitch.GetMode(user_id) == "sfw":
        print(f"SFW模式")
        lanraragi_response = requests.get(f"{LRR_URL}/api/search?filter=无H$&start={start}&sortby={sortby}&order={order}")

    # 如果没有传入类型参数 (只有page和s)，获取全部漫画
    elif not c and not t and not a:
        print(f"第一种")
        if sortby:
            lanraragi_response = requests.get(f"{LRR_URL}/api/search?start={start}&sortby={sortby}&order={order}")
        else:
            lanraragi_response = requests.get(f"{LRR_URL}/api/search?start={start}")
    
    # 如果有传入类型参数 c=文本，获取相应分类的漫画
    elif c and c in config["categories"]:
        print(f"第二种: {c}")
        category_id = config["categories"][c]["lrr_id"]
        if sortby:
            lanraragi_response = requests.get(f"{LRR_URL}/api/search?start={start}&category={category_id}&sortby={sortby}&order={order}")
        else:
            lanraragi_response = requests.get(f"{LRR_URL}/api/search?start={start}&category={category_id}")

    # 有传入类型参数 t=文本，返回相应标签漫画
    elif t is not None:
        print(f"第三种: {t}")
        # 将简化的标签还原后再传入api
        if t.startswith("女:"):
            t = t.replace("女:", "女性:")
        elif t.startswith("男:"):
            t = t.replace("男:", "男性:")
        if sortby:
            lanraragi_response = requests.get(f"{LRR_URL}/api/search?start={start}&filter={t}$&sortby={sortby}&order={order}")
        else:
            lanraragi_response = requests.get(f"{LRR_URL}/api/search?start={start}&filter={t}$")

    # 有传入类型参数 a=文本，返回相应作者漫画
    elif a is not None:
        print(f"第四种: {a}")
        if sortby:
            lanraragi_response = requests.get(f"{LRR_URL}/api/search?start={start}&filter={a}$&sortby={sortby}&order={order}")
        else:
            lanraragi_response = requests.get(f"{LRR_URL}/api/search?start={start}&filter={a}$")
    else:
        print(f"未知传入参数")

    if isinstance(lanraragi_response, dict):
        lanraragi_data = lanraragi_response
    else:
        lanraragi_data = lanraragi_response.json()
    
    comics_data = []
    for comic in lanraragi_data["data"]:
        comic_id = comic["arcid"]

        thumbnail_path = f"thumbnail/{comic_id}"
        comic_data = db.get_comic_info(comic_id) or {}

        # 提取作者信息
        # 优先从数据库获取
        author = comic_data.get("author")
        # 否则从元数据提取
        if not author:
            tags = comic.get("tags", "")
            for tag in tags.split(","):
                if tag.startswith("artist:"):
                    author = tag.split(":", 1)[1]
                    break
                elif tag.startswith("艺术家:"):
                    author = tag.split(":", 1)[1]

        comic_info = {
            "_id": comic_id,
            #"title": comic_data.get("title", comic.get("title")),
            "title": comic_data.get("title") or comic.get("title"),
            "author": author or "",
            "totalViews": comic_data.get("viewsCount", 0),
            "totalLikes": comic_data.get("likesCount"),
            "pagesCount": comic.get("pagecount"),
            "epsCount": comic_data.get("epsCount", 1),
            "finished": bool(comic_data.get("finished", True)),
            "categories": json.loads(comic_data.get("categories", '[]')) if isinstance(comic_data.get("categories"), str) else comic_data.get("categories", ["未知分类"]),
            "thumb": {
                "originalName": f"{comic_id}.jpg",
                "path": thumbnail_path,
                "fileServer": PICABRIDGE_URL
            },
            "id": comic_id,
            "likesCount": comic_data.get("likesCount", 0)
        }
        comics_data.append(comic_info)

    # 处理分页
    total = lanraragi_data["recordsFiltered"]
    limit = 20
    pages = math.ceil(total / limit)

    # 组装返回数据
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

# 获取排行榜
def leaderboard(tt):
    lanraragi_data = api.get_all_archives()

    if lanraragi_data is None:
        return jsonify({"code": 500, "message": "Failed to fetch archives."}), 500

    # 检查返回的数据是否是一个列表
    if isinstance(lanraragi_data, list):
        comics_list = lanraragi_data
    else:
        return jsonify({"code": 500, "message": "Invalid data format."}), 500

    # 处理 comics_list，提取 arcid
    comic_ids = [comic["arcid"] for comic in comics_list]

    # 定义用于排序的访问量字典
    leaderboard_data = {}

    # 根据不同的参数计算访问量
    for comic_id in comic_ids:
        comic_info = db.get_comic_info(comic_id)  # 获取漫画信息

        if tt == 'D30':
            # 将原始的30天访问量定义为直接获取历史总浏览量
            leaderboard_data[comic_id] = comic_info.get("viewsCount", 0)
        # 除了舍弃原始的30天访问量改为历史总量以外，其他维持原状，依然返回24小时或7天访问量
        elif tt == 'H24' or tt == 'D7':
            # 获取 viewed_at 数据并计算24小时或7天的浏览量
            viewed_at = comic_info.get("viewed_at", [])
            viewed_at = json.loads(viewed_at) if viewed_at else []
            current_timestamp = int(time.time())  # 当前时间戳

            if tt == 'H24':
                threshold_timestamp = current_timestamp - (24 * 60 * 60)  # 24小时内的时间戳
            elif tt == 'D7':
                threshold_timestamp = current_timestamp - (7 * 24 * 60 * 60)  # 7天前的时间戳

            # 计算在指定时间范围内的浏览量
            count = sum(1 for ts in viewed_at if int(ts) > threshold_timestamp)
            leaderboard_data[comic_id] = count

    # 按访问量降序排序
    sorted_leaderboard = sorted(leaderboard_data.items(), key=lambda x: x[1], reverse=True)

    # 重组返回数据
    comics_data = []
    for comic_id, count in sorted_leaderboard:
        comic_info = db.get_comic_info(comic_id)  # 再次获取漫画信息以获取详细数据
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

    # 构建响应数据
    response_data = {
        "code": 200,
        "message": "success",
        "data": {
            "comics": comics_data,
        }
    }

    return jsonify(response_data), 200


# 获取随机漫画数据
def get_random_comics(user_id):
    config = load_config()  # 加载配置文件

    # 如果用户模式为SFW，只返回SFW漫画
    if ModeSwitch.GetMode(user_id) == "sfw":
        print(f"SFW模式")
        lanraragi_response = requests.get(f"{LRR_URL}/api/search/random?filter=无H$&count=20")
    else:
        lanraragi_response = requests.get(f"{LRR_URL}/api/search/random?count=20")

    if isinstance(lanraragi_response, dict):
        lanraragi_data = lanraragi_response
    else:
        lanraragi_data = lanraragi_response.json()
    
    comics_data = []
    for comic in lanraragi_data["data"]:
        comic_id = comic["arcid"]

        thumbnail_path = f"thumbnail/{comic_id}"
        comic_data = db.get_comic_info(comic_id) or {}

        # 提取作者信息
        # 优先从数据库获取
        author = comic_data.get("author")
        # 否则从元数据提取
        if not author:
            tags = comic.get("tags", "")
            for tag in tags.split(","):
                if tag.startswith("artist:"):
                    author = tag.split(":", 1)[1]
                    break
                elif tag.startswith("艺术家:"):
                    author = tag.split(":", 1)[1]

        comic_info = {
            "_id": comic_id,
            #"title": comic_data.get("title", comic.get("title")),
            "title": comic_data.get("title") or comic.get("title"),
            "author": author or "",
            "totalViews": comic_data.get("viewsCount", 0),
            "totalLikes": comic_data.get("likesCount"),
            "pagesCount": comic.get("pagecount"),
            "epsCount": comic_data.get("epsCount", 1),
            "finished": bool(comic_data.get("finished", True)),
            "categories": json.loads(comic_data.get("categories", '[]')) if isinstance(comic_data.get("categories"), str) else comic_data.get("categories", ["未知分类"]),
            "thumb": {
                "originalName": f"{comic_id}.jpg",
                "path": thumbnail_path,
                "fileServer": PICABRIDGE_URL
            },
            "id": comic_id,
            "likesCount": comic_data.get("likesCount", 0)
        }
        comics_data.append(comic_info)

    # 处理分页
    total = lanraragi_data["recordsTotal"]
    limit = 20
    pages = math.ceil(total / limit)

    # 组装返回数据
    response_data = {
        "code": 200,
        "message": "success",
        "data": {
            "comics": comics_data,
            }
        }

    return jsonify(response_data), 200