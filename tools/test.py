import os, sys, requests, base64
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from lib import api, edit_comics

api_key = "kamimamita"
lanraragiurl = "http://192.168.7.205:7277"
# lanraragi验证头
def get_auth_header():
    encoded_key = base64.b64encode(api_key.encode()).decode()
    return {
        'Authorization': f'Bearer {encoded_key}',
        'Accept': 'application/json'
    }

# 创建新的合集
def new_tankoubon(name):

    lanraragi_api = lanraragiurl
    url = f"{lanraragi_api}/api/tankoubons"
    headers = get_auth_header()
    params = {'name': name}
    
    try:
        response = requests.put(url, headers=headers, params=params)
        return response.json()  # 返回 API 的 JSON 响应
    except requests.RequestException as e:
        return {"error": str(e)}

# 将 档案 添加到指定合集
def add_archive_tankoubon(id, archive):
    lanraragi_api = lanraragiurl
    url = f"{lanraragi_api}/api/tankoubons/{id}/{archive}"
    headers = get_auth_header()
    
    try:
        response = requests.put(url, headers=headers)
        return response.json()  # 返回 API 的 JSON 响应
    except requests.RequestException as e:
        return {"error": str(e)}


def test__tankoubon():
    # name = "测试合集"
    # print(f"合集名称: {name}")
    # response = new_tankoubon(name)
    # print("返回数据:")
    # print(response)


    id = "TANK_1739907957"
    archive_id = "5e9313c7b07291d49d9d98c29888b160d724f1c7"
    response = add_archive_tankoubon(id, archive_id)
    print("返回数据:")
    print(response)



def test_single_comic():
    # 测试数据
    data = {
        "id": "013d5a541a4d17ae5c1253a78031f46bb49c191b",
        "title": "エクスター・アイリス 催眠怪人に敗れる",
        "description": "测试漫画内容，123abc。",
        "author": "caburi",
        "chineseTeam": "",
        "categories": ["熟肉", "萝莉"],
        "tags": ["原作:原创", "团队:caburibbon", "艺术家:caburi", "女性:萝莉"],
        "finished": True
    }

    #允许覆盖
    confirmtag = True

    result = edit_comics.handle_comic_data(data, confirmtag)

    print("返回信息:", result)



if __name__ == '__main__':
    # main()
    test__tankoubon()