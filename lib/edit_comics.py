import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
import pymysql
from lib import db
import requests
import base64

# 加载配置文件
def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# 单本多本漫画判断
def handle_comic_data(data, confirmtag):
    if 'id' in data and 'title' in data:  # 判断传入数据是否是数组
        return single_comic(data, confirmtag)
    elif 'comics' in data:  # 是数组则为多本漫画
        return multiple_comics(data['comics'])
    else:
        return {"error": "Invalid data format"}

# 获取分类ID
def get_category_id(category_name):
    config_data = load_config()
    category_mapping = config_data.get('categories', {})
    return category_mapping.get(category_name)

# 处理单本漫画
def single_comic(data, confirmtag):
    comic_id = data['id']

    connection = db.get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM comic_info WHERE id = %s", (comic_id,))
    result = cursor.fetchone()

    if result:  # 如果已存在，且没有勾选覆盖，则返回提示
        if not confirmtag:
            return {"errorcode": "001", "info": "项目已存在，请勾选覆盖选项。"}

    if confirmtag:  # 确认覆盖
        if edit_db(data) and edit_lanraragi(data):
            return {"success": True, "message": "操作成功"}
        else:
            return {"success": False, "message": "操作失败"}

    return {"success": False, "message": "错误"}

# 处理多本漫画
def multiple_comics(comics):
    failed_updates = []
    
    for comic in comics:
        result = single_comic(comic) # 多本漫画处理必然是新漫画，无需传入覆盖标志
        if not result.get("success"):
            failed_updates.append({"id": comic['id'], "error": result['message']})
    
    if failed_updates:
        return {"success": False, "failed": failed_updates}
    
    return {"success": True, "message": "所有操作成功"}

# 写入数据库
def edit_db(data):
    connection = db.get_db_connection()
    cursor = connection.cursor()

    comic_id = data['id']
    # 数据表对照
    insert_data = {
        "id": data["id"],
        "title": data["title"],
        "description": data["description"],
        "author": data["author"],
        "chineseTeam": data["chineseTeam"],
        "categories": json.dumps(data["categories"]),  # 转换为JSON字符串
        "tags": json.dumps(data["tags"]),              # 转换为JSON字符串
        "finished": data["finished"]
    }

    # 检查是否存在
    cursor.execute("SELECT * FROM comic_info WHERE id = %s", (comic_id,))
    result = cursor.fetchone()

    if result:  # 如果已存在，进行更新
        cursor.execute("""
            UPDATE comic_info SET title = %(title)s, description = %(description)s, 
            author = %(author)s, chineseTeam = %(chineseTeam)s, categories = %(categories)s, 
            tags = %(tags)s, finished = %(finished)s WHERE id = %(id)s
        """, insert_data)
    else:  # 不存在则创建新记录
        cursor.execute("""
            INSERT INTO comic_info (id, title, description, author, chineseTeam, categories, tags, finished)
            VALUES (%(id)s, %(title)s, %(description)s, %(author)s, %(chineseTeam)s, %(categories)s, %(tags)s, %(finished)s)
        """, insert_data)

    connection.commit()
    connection.close()

    return True

# 写入lanraragi
def edit_lanraragi(data):
    config = load_config()
    lanraragi_api = config['lanraragi_api']
    lanraragi_api_key = config['lanraragi_api_key']

    comic_id = data['id']

    # 编辑 metadata
    metadata_url = f"{lanraragi_api}/api/archives/{comic_id}/metadata"
    metadata_payload = {
        "tags": ", ".join(data["tags"]),
        "summary": data["description"]
    }

    headers = {
        "Authorization": f"Bearer {base64.b64encode(lanraragi_api_key.encode()).decode()}",
        "Accept": "application/json"
    }

    response = requests.put(metadata_url, params=metadata_payload, headers=headers)
    print("TAG url:", metadata_url)
    print("TAG DATA:", metadata_payload)
    print("tag返回:", response.text)
    if response.status_code != 200:
        return False, response.json().get('error', 'Unknown error')

    # 编辑分类
    # categories_url = f"{lanraragi_api}/api/categories/{category_id}/{comic_id}"

    # for category in data['categories']:
    #     category_id = get_category_id(category)
    #     categories_url = f"{lanraragi_api}/api/categories/{category_id}/{comic_id}"
    #     response = requests.put(categories_url, headers=headers)
    #     print("分类url:", categories_url)
    #     print("分类返回:", response.text)
    #     if response.status_code != 200:
    #         return False, response.json().get('error', 'Unknown error')

    return True



