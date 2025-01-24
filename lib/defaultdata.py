from collections import OrderedDict
from lib.db import get_comic_info, get_user_info
from lib.api import get_archive_metadata  # 假设你有一个获取元数据的函数
from datetime import datetime, timezone

def format_timestamp(ts):
    if ts is not None:
        return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
    return "2024-09-27T00:00:00.000Z"  # 默认值


def defaultdata(comic_id):
    # 尝试获取漫画信息
    comic_data = get_comic_info(comic_id)

    if comic_data is None:
        # 如果找不到对应的comic_id，使用默认值
        return get_default_response(comic_id)

    # 如果找到漫画信息，但某些字段为空
    return populate_defaults(comic_data,comic_id)

def get_default_response(comic_id):
    # 默认用户 ID
    user_id = "7v5za3f62102s6t81wue5uyo"  # 使用默认的用户 ID
    user_info = get_user_info(user_id)
    
    avatar_data = {
        "originalName": user_info.get("avatar"),
        "path": user_info.get("avatar").split("/")[-1],  # 提取文件名
        "fileServer": user_info.get("avatar").rsplit("/", 1)[0]  # 获取文件服务器地址
    }
    
    return OrderedDict([
        ("code", 200),
        ("message", "success"),
        ("data", OrderedDict([
            ("comic", OrderedDict([
                ("_id", comic_id),
                ("_creator", OrderedDict([
                    ("_id", user_info.get("id", None)),
                    ("gender", user_info.get("gender", None)),
                    ("name", user_info.get("name", None)),
                    ("exp", user_info.get("exp", 0)),
                    ("level", user_info.get("level", 0)),
                    ("role", user_info.get("role", None)),
                    ("avatar", avatar_data),
                    ("verified", user_info.get("verified", False)),
                    ("characters", user_info.get("characters", [])),
                    ("title", user_info.get("title", None)),
                ])),
                ("title", "未知"),
                ("description", "找不到元数据，按默认返回。"),
                ("thumb", OrderedDict([
                    ("fileServer", "https://picaapi.reiyy.com"),
                    ("path", f"thumbnail/{comic_id}"),
                    ("originalName", f"{comic_id}.jpg"),
                ])),
                ("author", "未知"),
                ("chineseTeam", "未知"),
                ("categories", ["默认"]),
                ("tags", ["默认"]),
                ("pagesCount", 0),
                ("epsCount", 1),
                ("finished", True),
                ("updated_at", "2024-09-27T00:00:00.000Z"),
                ("created_at", "2024-09-27T00:00:00.000Z"),
                ("allowDownload", False),
                ("allowComment", True),
                ("totalLikes", 0),
                ("totalViews", 1),
                ("totalComments", 0),
                ("viewsCount", 1),
                ("likesCount", 0),
                ("commentsCount", 0),
                ("isFavourite", False),
                ("isLiked", False),
            ])),
        ])),
    ])

def populate_defaults(comic_data,comic_id):
    # 用默认值填充为空的字段
    user_id = "7v5za3f62102s6t81wue5uyo"  # 使用默认的用户 ID
    user_info = get_user_info(user_id)
    
    avatar_data = {
        "originalName": user_info.get("avatar"),
        "path": user_info.get("avatar").split("/")[-1],  # 提取文件名
        "fileServer": user_info.get("avatar").rsplit("/", 1)[0]  # 获取文件服务器地址
    }
    
    creator = comic_data.get("creator")  # 安全获取
    default_creator = user_info if creator is None else creator

def populate_defaults(comic_data, comic_id):
    # 用默认值填充为空的字段
    user_id = "7v5za3f62102s6t81wue5uyo"  # 使用默认的用户 ID
    user_info = get_user_info(user_id)

    avatar_url = user_info.get("avatar")
    avatar_data = {
        "originalName": avatar_url,
        "path": avatar_url.split("/")[-1] if avatar_url else None,  # 提取文件名
        "fileServer": avatar_url.rsplit("/", 1)[0] if avatar_url else None  # 获取文件服务器地址
    }

    creator = comic_data.get("creator")  # 安全获取
    default_creator = user_info if creator is None else creator



    # 获取和转换时间
    updated_at = comic_data.get("updated_at", 0)  # 默认为 0
    created_at = comic_data.get("created_at", 0)  # 默认为 0

    default_data = OrderedDict([
        ("code", 200),
        ("message", "success"),
        ("data", OrderedDict([
            ("comic", OrderedDict([
                ("_id", comic_data["id"]),
                ("_creator", OrderedDict([
                    ("_id", default_creator.get("_id", user_info.get("id", None))),
                    ("gender", default_creator.get("gender", user_info.get("gender", None))),
                    ("name", default_creator.get("name", user_info.get("name", None))),
                    ("exp", default_creator.get("exp", user_info.get("exp", 0))),
                    ("level", default_creator.get("level", user_info.get("level", 0))),
                    ("role", default_creator.get("role", user_info.get("role", None))),
                    ("avatar", avatar_data),
                    ("verified", default_creator.get("verified", user_info.get("verified", False))),
                    ("characters", default_creator.get("characters", user_info.get("characters", []))),
                    ("title", default_creator.get("title", user_info.get("title", None))),
                ])),
                ("title", comic_data.get("title", get_archive_metadata(comic_data["id"])["title"])),
                ("description", comic_data.get("description", "找不到元数据，按默认返回。")),
                ("thumb", OrderedDict([
                    ("fileServer", "https://picaapi.reiyy.com"),
                    ("path", f"thumbnail/{comic_id}"),
                    ("originalName", f"{comic_id}.jpg"),
                ])),
                ("author", comic_data.get("author", "未知")),
                ("chineseTeam", comic_data.get("chineseTeam", "未知")),
                ("categories", comic_data.get("categories", ["默认"])),
                ("tags", comic_data.get("tags", ["默认"])),
                ("pagesCount", comic_data.get("pagesCount", get_archive_metadata(comic_data["id"])["pagecount"])),
                ("epsCount", comic_data.get("epsCount", 1)),
                ("finished", comic_data.get("finished", True)),
                ("updated_at", format_timestamp(comic_data.get("updated_at", 1690858353))),
                ("created_at", format_timestamp(comic_data.get("created_at", 1682332524))),
                ("allowDownload", comic_data.get("allowDownload", False)),
                ("allowComment", comic_data.get("allowComment", True)),
                ("totalLikes", comic_data.get("likesCount")),
                ("totalViews", comic_data.get("viewsCount")),
                ("totalComments", comic_data.get("commentsCount")),
                ("viewsCount", comic_data.get("viewsCount", 1)),
                ("likesCount", comic_data.get("likesCount", 0)),
                ("commentsCount", comic_data.get("commentsCount", 0)),
                ("isFavourite", False),
                ("isLiked", False),
            ])),
        ])),
    ])
    
    return default_data
