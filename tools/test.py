import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from lib import api, edit_comics

# def main():
    # name = "测试合集"
    # print(f"合集名称: {name}")
    # response = api.new_tankoubon(name)
    # print("返回数据:")
    # print(response)

    # name = "测试合集"
    # print(f"合集名称: {name}")
    # response = api.new_tankoubon(name)
    # print("返回数据:")
    # print(response)

    # id = "TANK_1728657266"
    # archive_id = "de02df748deb2ae2e1876e68506c456f4b2042ee"
    # response = api.add_archive_tankoubon(id, archive_id)
    # print("返回数据:")
    # print(response)



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

if __name__ == "__main__":
    test_single_comic()


if __name__ == '__main__':
    # main()
    test_single_comic()