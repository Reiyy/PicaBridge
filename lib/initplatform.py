import json
import re
import time
import threading
import requests

from flask import jsonify
from datetime import datetime
from loguru import logger

import lib.db as db

# 兼容gevent和flask环境
try:
    import gevent
    _use_gevent = True
except ImportError:
    _use_gevent = False

def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

config = load_config()

PICABRIDGE_URL = config.get('PicaBridge_URL', '')

# MyPica版本信息缓存
_app_cache = {"data": None, "fetching": False, "last_check": 0}
_app_lock = threading.Lock()
APP_CACHE_TTL = 7200  # 缓存2小时


def _spawn(func):
    if _use_gevent:
        gevent.spawn(func)
    else:
        threading.Thread(target=func, daemon=True).start()

# 从MyPica APK文件名中提取版本号
def _parse_apk_version(filename):
    match = re.match(r'MyPica_([\d.]+)-', filename)
    if not match:
        return None, None
    full_ver = match.group(1)  # 2.7.1.0.2.2
    parts = full_ver.split('.')
    user_ver = '.'.join(parts[:4])  # 2.7.1.0
    return full_ver, user_ver

# 转换github时间戳格式
def _github_time_to_iso(t):
    if '.' in t:
        return t
    return t.replace('Z', '.000Z')

# 获取github发布信息
def _fetch_mypica_update():
    try:
        resp = requests.get(
            "https://api.github.com/repos/Reiyy/HookMyPica/releases",
            timeout=10
        )
        if resp.status_code != 200:
            logger.warning(f"获取HookMyPica发布信息失败: HTTP {resp.status_code}")
            return

        releases = resp.json()
        for release in releases:
            name = release.get("name", "")
            if not name.startswith("MyPica"):
                continue

            # 查找MyPica_开头的APK文件
            for asset in release.get("assets", []):
                asset_name = asset.get("name", "")
                if not asset_name.startswith("MyPica_") or not asset_name.endswith(".apk"):
                    continue

                full_ver, user_ver = _parse_apk_version(asset_name)
                if not full_ver:
                    continue

                download_url = asset.get("browser_download_url", "")
                # 从下载URL拆分path和fileServer
                # https://github.com/.../releases/download/v2.7.1.0/MyPica_xxx.apk
                # → fileServer: https://github.com
                # → path: /Reiyy/HookMyPica/releases/download/v2.7.1.0/MyPica_xxx.apk
                from urllib.parse import urlparse
                parsed = urlparse(download_url)
                file_server = f"{parsed.scheme}://{parsed.netloc}"
                file_path = parsed.path.lstrip('/')

                published = release.get("published_at", "")
                created = release.get("created_at", "")
                update_content = release.get("body", "【版本更新】")

                # id设为日期年月日数字 + 内部版本号去点
                date_str = published[:10].replace('-', '')
                ver_str = full_ver.replace('.', '')
                app_id = f"{date_str}{ver_str}"

                app_data = {
                    "_id": app_id,
                    "downloadUrl": download_url,
                    "updateContent": update_content,
                    "version": full_ver,
                    "updated_at": _github_time_to_iso(published),
                    "created_at": _github_time_to_iso(created),
                    "apk": {
                        "originalName": asset_name,
                        "path": file_path,
                        "fileServer": file_server
                    }
                }

                with _app_lock:
                    _app_cache["data"] = app_data
                logger.info(f"发现MyPica App新版本: {full_ver}")
                return

        logger.debug("未找到MyPica App发布信息")

    except Exception as e:
        logger.warning(f"获取MyPica App版本信息时出错: {e}")
    finally:
        with _app_lock:
            _app_cache["fetching"] = False
            _app_cache["last_check"] = time.time()

# 默认版本信息
def _get_default_application():
    now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z')
    return {
        "_id": "default1.1.1.1.0.0",
        "downloadUrl": PICABRIDGE_URL,
        "updateContent": "无更新",
        "version": "1.1.1.1.0.0", # 倒数两位版本号设为0，以避免触发更新(哔咔App通过倒数第一位版本号是否大于本地来判断是否有更新，通过倒数第二位是否大于本地倒数第一位判断是否为强制更新)
        "updated_at": now,
        "created_at": now,
        "apk": {
            "originalName": "1.1.1.1.0.0.apk",
            "path": "1.1.1.1.0.0.apk",
            "fileServer": PICABRIDGE_URL
        }
    }

# 获取最新信息
def _get_latest_application():
    with _app_lock:
        cached = _app_cache["data"]
        cache_expired = time.time() - _app_cache["last_check"] > APP_CACHE_TTL
        need_fetch = (cached is None or cache_expired) and not _app_cache["fetching"]
        if need_fetch:
            _app_cache["fetching"] = True

    if need_fetch:
        _spawn(_fetch_mypica_update)

    if cached:
        return cached
    return config.get("initPlatform", {}).get("latestApplication", _get_default_application())


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
                "latestApplication": _get_latest_application(),
                "imageServer": PICABRIDGE_URL + "/static/",
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
