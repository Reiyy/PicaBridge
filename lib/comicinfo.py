import json

from flask import jsonify
from collections import OrderedDict
from datetime import datetime
from datetime import timezone

import lib.db as db
from lib.api import get_archive_metadata

def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)
    
config = load_config()
PICABRIDGE_URL = config.get('PicaBridge_URL')

# 获取漫画信息
def get_comic_info(comic_id, user_id):
    db.plus_comic_viewsCount(comic_id)
    config = load_config()
    comic_data = db.get_comic_info(comic_id)

    # 自动同步，当漫画元数据不存在时从LRR获取完整数据写入数据库
    metadata = None
    if not comic_data:
        metadata = get_archive_metadata(comic_id)
        if not metadata:
            return None
        db.sync_comic_metadata(comic_id, metadata)
        comic_data = db.get_comic_info(comic_id)
    elif not comic_data.get("author") or comic_data.get("tags") in (None, '[]', ''):
        metadata = get_archive_metadata(comic_id)
        if metadata:
            db.sync_comic_metadata(comic_id, metadata)
            comic_data = db.get_comic_info(comic_id)

    if not comic_data:
        return None

    # 获取漫画上传者信息
    creator_id = comic_data.get('creator', '7v5za3f62102s6t81wue5uyo')
    user_info = db.get_user_info(creator_id) or {}

    # 处理用户头像
    avatar_data = {
        "originalName": user_info.get("avatar").split("/")[-1],
        "path": "/".join(user_info.get("avatar").split("/")[3:]),
        "fileServer": PICABRIDGE_URL
    }

    # 漫画封面
    thumbnail_path = f"thumbnail/{comic_id}"

    # 格式化时间
    def format_timestamp(ts):
        if ts is not None:
            return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
        return "1970-01-01T00:00:00Z"

    categories = json.loads(comic_data.get("categories", '[]')) if isinstance(comic_data.get("categories"), str) else comic_data.get("categories", ["无分类"])
    tags = json.loads(comic_data.get("tags", '[]')) if isinstance(comic_data.get("tags"), str) else comic_data.get("tags", ["无标签"])
    isLiked = db.is_like_comic(user_id, comic_id)  # 调用函数获取是否点赞
    isFavourite = db.is_favourite_comic(user_id, comic_id)  # 调用函数获取是否收藏
    characters = json.loads(user_info.get("characters", '[]')) if isinstance(user_info.get("characters"), str) else user_info.get("characters", [])

    # 作者信息，优先从数据库获取，否则从元数据提取
    author = comic_data.get("author", "")
    if not author and not metadata:
        metadata = get_archive_metadata(comic_id)
    if not author and metadata:
        from lib.comic_utils import extract_author
        author = extract_author(metadata.get("tags", ""))

    # 组装返回数据
    response_data = OrderedDict([
        ("code", 200),
        ("message", "success"),
        ("data", OrderedDict([
            ("comic", OrderedDict([
                ("_id", comic_data.get("id", comic_id)),
                ("_creator", OrderedDict([
                    ("_id", user_info.get("id")),
                    ("name", user_info.get("name")),
                    ("gender", user_info.get("gender")),
                    ("exp", user_info.get("exp")),
                    ("level", user_info.get("level")),
                    ("role", user_info.get("role")),
                    ("verified", user_info.get("verified")),
                    ("characters", characters),
                    ("title", user_info.get("title")),
                    ("avatar", avatar_data),
                ])),
                ("title", comic_data.get("title") or (metadata.get("title") if metadata else "")),
                ("description", comic_data.get("description") or (metadata.get("summary") if metadata else "")),
                ("thumb", OrderedDict([
                    ("fileServer", PICABRIDGE_URL),
                    ("path", thumbnail_path),
                    ("originalName", f"{comic_id}.jpg"),
                ])),
                ("author", author or "",),
                ("chineseTeam", comic_data.get("chineseTeam", "")),
                ("categories", categories),
                ("tags", tags),
                ("pagesCount", comic_data.get("pagesCount") or (metadata.get("pagecount") if metadata else 0)),
                ("epsCount", comic_data.get("epsCount", 1)),
                ("finished", bool(comic_data.get("finished", True))),
                ("updated_at", format_timestamp(comic_data.get("updated_at", 0))),
                ("created_at", format_timestamp(comic_data.get("created_at", 0))),
                ("allowDownload", bool(comic_data.get("allowDownload", False))),
                ("allowComment", bool(comic_data.get("allowComment", True))),
                ("totalLikes", comic_data.get("likesCount", 0)),
                ("totalViews", comic_data.get("viewsCount", 0)),
                ("totalComments", comic_data.get("commentsCount", 0)),
                ("viewsCount", comic_data.get("viewsCount", 0)),
                ("likesCount", comic_data.get("likesCount", 0)),
                ("commentsCount", comic_data.get("commentsCount", 0)),
                ("isFavourite", isFavourite),
                ("isLiked", isLiked),
            ])),
        ])),
    ])
    return response_data

# 收藏漫画
def comic_favourite(user_id, comic_id):
    is_favourite = db.is_favourite_comic(user_id, comic_id)
    result = db.favourite_comic(is_favourite, user_id, comic_id)

    if result:
        if not is_favourite:  # 如果未收藏，则添加收藏
            return jsonify({
                "code": 200,
                "message": "success",
                "data": {
                    "action": "favourite"
                }
            })
        else:  # 如果已收藏，则取消收藏
            return jsonify({
                "code": 200,
                "message": "success",
                "data": {
                    "action": "un_favourite"
                }
            })
    else:
        return jsonify({
            "code": 500,
            "message": "操作失败"
        })

# 点赞漫画
def comic_like(user_id, comic_id):
    is_like = db.is_like_comic(user_id, comic_id)
    result = db.like_comic(is_like, user_id, comic_id)

    if result:
        if not is_like:  # 如果未点赞，则点赞，同时触发元数据同步
            config = load_config()
            metadata = get_archive_metadata(comic_id)
            if metadata:
                db.sync_comic_metadata(comic_id, metadata)
            return jsonify({
                "code": 200,
                "message": "success",
                "data": {
                    "action": "like"
                }
            })
        else:  # 如果已点赞，则取消点赞
            return jsonify({
                "code": 200,
                "message": "success",
                "data": {
                    "action": "unlike"
                }
            })
    else:
        return jsonify({
            "code": 500,
            "message": "操作失败"
        })