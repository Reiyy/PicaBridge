import json
import requests
import base64

from lib.Command import initComic
from lib import db

# 加载配置文件
def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

config = load_config()
LRR_URL = config.get('lrr_Api')

LRR_API_KEY = load_config()["lrr_Api_Key"]

# 允许调用该命令的用户组
allow_groups = ["official", "knight"]

# lanraragi验证头
def get_auth_header():
    encoded_key = base64.b64encode(LRR_API_KEY.encode()).decode()
    return {
        'Authorization': f'Bearer {encoded_key}',
        'Accept': 'application/json'
    }

def run(comic_id, user_id, command_args):
    # 检测用户权限
    user_groups = db.get_user_characters(user_id)
    for group in user_groups:
        if group not in allow_groups:
            return {"status": False, "data": "你当前无权执行此命令！"}

    # 获取当前漫画元数据
    get_url = f"{LRR_URL}/api/archives/{comic_id}/metadata"
    headers = get_auth_header()

    try:
        # 发送 GET 请求获取当前漫画信息
        get_response = requests.get(get_url, headers=headers)
        get_response.raise_for_status()  # 如果请求失败，抛出异常

        # 获取当前返回的 JSON 数据
        get_response_data = get_response.json()
        print(f"Current data: {get_response_data}")

        # 提取现有的 title 和 tags
        current_title = get_response_data.get("title", "")
        current_tags = get_response_data.get("tags", "")

        # 构造要发送的查询参数
        params = {
            "title": current_title,
            "tags": current_tags,
            "summary": command_args
        }

        # 发送 PUT 请求更新漫画简介
        put_response = requests.put(get_url, params=params, headers=headers)
        put_response.raise_for_status()  # 如果请求失败，抛出异常

        # 获取响应的 JSON 数据
        put_response_data = put_response.json()
        print(f"PUT response: {put_response_data}")

        # 检查返回的 success 状态
        if put_response.status_code == 200 and put_response_data.get("success", 0) == 1:
            result = initComic.AutoinitComicInfoFULL(comic_id, user_id, "")
            status = result.get("status", False)  # 获取状态标记
            if status:
                return {"status": True, "data": "漫画简介编辑成功！"}
            else:
                return {"status": False, "data": "编辑漫画简介成功，但自动更新元数据失败，请手动执行完全初始化命令！"}
        else:
            return {"status": False, "data": "编辑漫画简介失败"}

    except requests.RequestException as e:
        # 处理请求错误并返回失败信息
        return {"status": False, "data": f"编辑漫画简介失败: {str(e)}"}