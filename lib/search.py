import requests
import math
import json

from flask import jsonify
from flask import redirect

import lib.db as db

def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

config = load_config()
LRR_URL = config.get('lrr_Api')
PICABRIDGE_URL = config.get('PicaBridge_URL')

# 重定向缩略图
def redirect_thumbnail(arcid):
    try:
        lanraragi_thumbnail_url = f"{LRR_URL}/api/archives/{arcid}/thumbnail"
        print(f"Redirecting to: {lanraragi_thumbnail_url}")
        return redirect(lanraragi_thumbnail_url, code=302)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"code": 500, "message": "Internal Server Error", "detail": str(e)}), 500

# 搜索漫画
def search_comic(keyword, page=1):
    config = load_config()
    start = (page - 1) * 20

    lanraragi_response = requests.get(f"{LRR_URL}/api/search?start={start}&filter=*{keyword}")
    lanraragi_data = lanraragi_response.json()

    comics_data = []
    for comic in lanraragi_data["data"]:
        comic_id = comic["arcid"]

        thumbnail_path = f"thumbnail/{comic_id}"
        comic_data = db.get_comic_info(comic_id) or {}

        comic_info = {
            "_id": comic_id,
            "title": comic_data.get("title", comic.get("title", "未知标题")),
            "author": comic_data.get("author", "未知作者"),
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
