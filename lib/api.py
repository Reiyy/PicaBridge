import json
import requests
import base64

# 加载配置文件
def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)
    
LRR_API_KEY = load_config()["lrr_Api_Key"]

# lanraragi验证头
def get_auth_header():
    encoded_key = base64.b64encode(LRR_API_KEY.encode()).decode()
    return {
        'Authorization': f'Bearer {encoded_key}',
        'Accept': 'application/json'
    }

# 从 Lanraragi API 获取漫画元数据
def get_archive_metadata(comic_id):
    config = load_config()
    lrr_Api = config['lrr_Api']
    url = f"{lrr_Api}/api/archives/{comic_id}/metadata"
    headers = get_auth_header()
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 检查请求是否成功
        return response.json()  # 返回API数据
    except requests.RequestException as e:
        print(f"Error fetching metadata: {e}")
        return None  # 请求失败返回


# 从 Lanraragi API 获取漫画档案
def get_extract_archive(comic_id):
    config = load_config()
    lrr_Api = config['lrr_Api']
    url = f"{lrr_Api}/api/archives/{comic_id}/files"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # 检查请求是否成功
        return response.json()  # 返回API数据
    except requests.RequestException as e:
        print(f"Error fetching extract archive: {e}")
        return None  # 请求失败返回

# 从 Lanraragi API 获取所有漫画元数据
def get_all_archives():
    config = load_config()
    lrr_Api = config['lrr_Api']
    url = f"{lrr_Api}/api/archives"

    try:
        response = requests.get(url)
        response.raise_for_status()  # 检查请求是否成功
        return response.json()  # 返回API数据
    except requests.RequestException as e:
        print(f"Error fetching extract archive: {e}")
        return None  # 请求失败返回

# 创建新的合集
def new_tankoubon(name):
    config = load_config()
    lrr_Api = config['lrr_Api']
    url = f"{lrr_Api}/api/tankoubons"
    headers = get_auth_header()
    params = {'name': name}
    
    try:
        response = requests.put(url, headers=headers, params=params)
        return response.json()  # 返回 API 的 JSON 响应
    except requests.RequestException as e:
        return {"error": str(e)}

# 将 档案 添加到指定合集
def add_archive_tankoubon(id, archive):
    config = load_config()
    lrr_Api = config['lrr_Api']
    url = f"{lrr_Api}/api/tankoubons/{id}/{archive}"
    headers = get_auth_header()
    
    try:
        response = requests.put(url, headers=headers)
        return response.json()  # 返回 API 的 JSON 响应
    except requests.RequestException as e:
        return {"error": str(e)}