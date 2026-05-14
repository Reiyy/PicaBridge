import json
import os
import math
import time
import threading
import requests
from loguru import logger

# 兼容gevent和flask环境
try:
    import gevent
    _use_gevent = True
except ImportError:
    _use_gevent = False
logger.info(f"使用 {'gevent' if _use_gevent else 'threading'} 进行异步任务调度")

from lib import VER

# 版本号比较
def _parse_version(v):
    parts = v.split(".")
    result = [int(x) for x in parts[:-1]]
    last = parts[-1]
    if len(last) > 1:
        result.append(int(last[:-1]))
        result.append(int(last[-1]))
    else:
        result.append(int(last))
    return result

def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

config = load_config()
PICABRIDGE_URL = config.get('PicaBridge_URL')

# GitHub更新检查缓存
_update_cache = {"announcement": None, "fetching": False, "last_check": 0}
_lock = threading.Lock()
CACHE_TTL = 600  # 缓存10分钟

def _spawn(func):
    if _use_gevent:
        gevent.spawn(func)
    else:
        threading.Thread(target=func, daemon=True).start()

# 后台获取GitHub最新版本并写入缓存
def _fetch_github_update():
    try:
        resp = requests.get(
            "https://api.github.com/repos/Reiyy/PicaBridge/releases",
            timeout=5
        )
        if resp.status_code == 200:
            releases = resp.json()
            if not releases:
                return
            data = releases[0]
            logger.debug(f"GitHub发布数据: {data}")
            tag = data.get("tag_name", "")
            latest_ver = tag.lstrip("v")
            body = data.get("body", "暂无发布说明。")
            if latest_ver and _parse_version(latest_ver) > _parse_version(VER):
                logger.info(f"发现新版本: {latest_ver} (当前版本: {VER})")
                announcement = {
                    "id": f"update_{latest_ver}",
                    "title": f"发现新版本! v{latest_ver}",
                    "content": f"哔咔桥PicaBridge有新版本可用！\n版本号：v{latest_ver}\n\n发布说明:\n{body}",
                    "thumb": "img/2024/10/08/48d9b9a733185.png"
                }
                with _lock:
                    _update_cache["announcement"] = announcement
            else:
                # 版本一致，标记为无更新，防止重复检查
                with _lock:
                    _update_cache["announcement"] = False
    except Exception:
        logger.warning("检查GitHub更新时出错")
    finally:
        with _lock:
            _update_cache["fetching"] = False
            _update_cache["last_check"] = time.time()

# 公告信息
def get_announcements(page):
    # 获取所有公告
    announcements = config.get("announcements", {})
    # 从缓存读取GitHub更新公告，缓存为空或过期使用后台异步加载
    with _lock:
        update_announcement = _update_cache["announcement"]
        cache_expired = time.time() - _update_cache["last_check"] > CACHE_TTL
        need_fetch = (update_announcement is None or cache_expired) and not _update_cache["fetching"]
        if need_fetch:
            _update_cache["fetching"] = True
    if update_announcement:
        announcements = {"github_update": update_announcement, **announcements}
    if need_fetch:
        _spawn(_fetch_github_update)
    total = len(announcements) # 总公告数
    limit = 5 # 分页限制
    pages = math.ceil(total / limit) # 总页数

    # 分页
    start = (page - 1) * limit
    end = start + limit
    paginated_announcements = list(announcements.values())[start:end] # 获取当前页的公告

    # 格式化公告信息
    formatted_announcements = []
    for announcement in paginated_announcements:
        thumb_path = announcement.get("thumb", "")
        original_name = os.path.basename(thumb_path)  # 从路径中提取文件名

        formatted_announcement = {
            "_id": announcement.get("id", ""),
            "title": announcement.get("title", ""),
            "content": announcement.get("content", ""),
            "thumb": {
                "originalName": original_name,
                "path": thumb_path,
                "fileServer": PICABRIDGE_URL
            }
        }
        formatted_announcements.append(formatted_announcement)

    # 返回公告信息
    return {
        "code": 200,
        "message": "success",
        "data": {
            "announcements": {
                "docs": formatted_announcements,
                "total": total,
                "limit": limit,
                "page": str(page),
                "pages": pages
            }
        }
    }