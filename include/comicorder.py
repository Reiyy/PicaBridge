import json
from flask import jsonify
import include.api as api

def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

config = load_config()
LANRARAGI_URL = config.get('lanraragi_api')
PROXY_URL = config.get('PROXY_URL')

# 获取档案页数
def get_pages(comic_id, page):
    # 从api获取档案数据
    extract_data = api.get_extract_archive(comic_id)
    if not extract_data:
        return {"code": 404, "message": "Extract archive not found"}

    # 获取总页数
    total_pages = api.get_archive_metadata(comic_id)
    if total_pages is None or "pagecount" not in total_pages:
        return {"code": 404, "message": "Comic metadata not found"}

    total = total_pages["pagecount"]
    limit = 40
    pages = (total + limit - 1) // limit  # 计算总页数

    # 构建返回的 docs 数据
    docs = []
    for i, page_url in enumerate(extract_data["pages"], start=1):
        original_name = page_url.split("/")[-1]  # 获取原始文件名
        doc_id = f"{comic_id[:20]}{i:04d}"  # 根据 comic_id 和页数生成 ID
        media = {
            "originalName": original_name,
            "path": "bzpic" + page_url[1:],  # 去掉开头的 "." 并添加前缀
            "fileServer": PROXY_URL
        }
        docs.append({
            "_id": doc_id,
            "media": media,
            "id": doc_id
        })

    # 返回
    response_data = {
        "code": 200,
        "message": "success",
        "data": {
            "pages": {
                "docs": docs,
                "total": total,
                "limit": limit,
                "page": page,
                "pages": pages
            },
            "ep": {
                "_id": comic_id,
                "title": extract_data.get("title", "Unknown Title")  # 提取标题
            }
        }
    }
    return response_data
