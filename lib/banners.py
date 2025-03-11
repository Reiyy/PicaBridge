import json
import os

def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)
    
config = load_config()
PICABRIDGE_URL = config.get('PicaBridge_URL')

# 横幅公告
def get_banners():
    # 获取所有横幅公告
    banners = config.get("banners", {})
    # 格式化横幅公告信息
    formatted_banners = []
    for banner in banners.values():
        thumb_path = banner.get("thumb", "")
        original_name = os.path.basename(thumb_path)  # 从路径中提取文件名

        formatted_banner = {
            "_id": banner.get("id", ""),
            "title": banner.get("title", ""),
            "shortDescription": banner.get("shortDescription", ""),
            "type": banner.get("type", ""),
            "link": banner.get("link", ""),
            "thumb": {
                "fileServer": PICABRIDGE_URL,
                "path": thumb_path,
                "originalName": original_name
            }
        }
        formatted_banners.append(formatted_banner)

    # 返回最终结果
    return {
        "code": 200,
        "message": "success",
        "data": {
            "banners": formatted_banners
        }
    }