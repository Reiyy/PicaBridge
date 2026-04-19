import json

from flask import jsonify
from datetime import datetime
from datetime import timezone
from math import ceil

from lib.db import get_comic_info
from lib.api import get_archive_metadata

def format_timestamp(ts):
    if ts is not None:
        return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
    return "1970-01-01T00:00:00Z"


def get_eps(comic_id, page=1):
    limit = 40

    # 获取更新时间
    comic_data = get_comic_info(comic_id)
    if comic_data and comic_data.get("updated_at"):
        updated_at_iso = datetime.fromtimestamp(
            comic_data["updated_at"]
        ).isoformat()
    else:
        updated_at_iso = "1970-01-01T00:00:00Z"

    # 获取 metadata
    metadata = get_archive_metadata(comic_id)
    toc = metadata.get("toc", []) if metadata else []

    docs = []

    # 如果toc存在章节数据，构建章节列表
    if toc:
        for index, chapter in enumerate(toc):
            page_num = chapter.get("page", 0)
            title = chapter.get("name", f"Chapter {index+1}")

            docs.append({
                "_id": f"{comic_id}_page{page_num}",
                "id": f"{comic_id}_page{page_num}",
                "title": title,
                "order": index + 1,
                "updated_at": updated_at_iso
            })

        # 最新章节在最上面
        docs.reverse()

    # 如果不存在章节数据，返回默认单章节列表
    else:
        docs = [{
            "_id": f"{comic_id}_x",
            "id": f"{comic_id}_x",
            "title": "第一话",
            "order": 1,
            "updated_at": updated_at_iso
        }]

    # 分页计算
    total = len(docs)
    pages = ceil(total / limit) if total > 0 else 1

    # 防止越界
    if page < 1:
        page = 1
    if page > pages:
        page = pages

    start = (page - 1) * limit
    end = start + limit
    paged_docs = docs[start:end]

    response_data = {
        "code": 200,
        "message": "success",
        "data": {
            "eps": {
                "docs": paged_docs,
                "total": total,
                "limit": limit,
                "page": page,
                "pages": pages
            }
        }
    }

    return jsonify(json.loads(json.dumps(response_data, ensure_ascii=False)))