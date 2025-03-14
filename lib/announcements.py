import json
import os
import math

def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)
    
config = load_config()
PICABRIDGE_URL = config.get('PicaBridge_URL')

# 公告信息
def get_announcements(page):
    # 获取所有公告
    announcements = config.get("announcements", {})
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