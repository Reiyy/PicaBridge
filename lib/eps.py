import json

from flask import jsonify
from datetime import datetime
from datetime import timezone

from lib.db import get_comic_info

def format_timestamp(ts):
    if ts is not None:
        return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
    return "1970-01-01T00:00:00Z"

# 获取章节信息
# 由于lanraragi咱不支持章节，统一返回第一话
def get_eps(comic_id, page=1):
    # 查询漫画信息以获取更新日期
    comic_data = get_comic_info(comic_id)
    if comic_data is None:
        updated_at_iso = "1970-01-01T00:00:00Z"
    else:
        # 如果有数据，尝试获取更新日期
        updated_at = comic_data.get("updated_at", None)
        if updated_at is not None:
            updated_at_iso = datetime.fromtimestamp(updated_at).isoformat()
        else:
            updated_at_iso = "1970-01-01T00:00:00Z"

    # 构建返回数据
    response_data = {
        "code": 200,
        "message": "success",
        "data": {
            "eps": {
                "docs": [
                    {
                        "_id": comic_id + "x",
                        "id": comic_id + "x",
                        "title": "第一话",
                        "order": 1,
                        "updated_at": updated_at_iso
                    }
                ],
                "total": 1,
                "limit": 40,
                "page": page,
                "pages": 1
            }
        }
    }
    
    return jsonify(json.loads(json.dumps(response_data, ensure_ascii=False)))
