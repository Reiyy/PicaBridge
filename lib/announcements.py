import json
from flask import jsonify

def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)
    
config = load_config()
PROXY_URL = config.get('PROXY_URL')

# 公告信息
def get_announcements():
    announcements_data = {
        "code": 200,
        "message": "success",
        "data": {
            "announcements": {
                "docs": [
                    {
                        "_id": "66eeec47c765ef0843f44812",
                        "title": "PicaBridge测试 - 第一次发布前测试",
                        "content": "PicaBridge(哔咔桥)，是一个用于哔咔客户端与Lanraragi后端通信的桥梁。\nMyPica是与PicaBridge对接的客户端，基于官方PicACG App改造。\nHookMyPica是用于对MyPica界面元素进行修改的Xposed模块，基于HookPicACG修改。\n\n当前为第一次发布前测试，本次测试为不删档测试，上册测试的数据依然保留。\n本子数量依然为上次测试的40本，但会在后台完工后不断添加。\n如在使用中遇到任何问题，均可反馈。\n\n本次测试资源版本：\nPicaBridge - Beta 0.7.2-241028\nMyPica - Beta 2.2.1.3.3.4.71-241008\nHookMyPica - RC1 2.2.1.3.3.4-7.1-241005\n\n注意事项：\n部分分类点进去空白是正常现象，比如“生肉，萝莉”，\n这是因为测试本子中没有相应标签。\n随机本子暂未实现，所以也是空白。\n\n已知BUG：\n本子详情中的的 “从...开始” 无法显示标题(将于下一次测试中修复)\n\n已实现功能：\n账号登录及注册\n首页公告\n首页横幅滚动公告\n个人中心头像上传\n个人中心简介修改\n个人中心打哔咔签到\n个人中心收藏列表\n分类获取\n标签获取\n本子列表\n点赞本子\n收藏本子\n观看本子\n本子排行榜\n用户排行榜(按经验值排序)\n全局搜索\n标签搜索\n分类搜索\n作者搜索\n留言板\n本子评论\n\n未实现功能：\n随机本子\n聊天室\n小程序\n游戏区(MyPica Store)\n本子推荐\n首页本子推荐\n\n不准备实现的功能：\n按汉化组搜索(目前默认返回全部本子)\n按上传者搜索(目前默认返回全部本子)",
                        "thumb": {
                            "originalName": "48d9b9a733185.jpg",
                            "path": "img/2024/10/08/48d9b9a733185.png",
                            "fileServer": PROXY_URL
                        }
                    }
                ],
                "total": 1,
                "limit": 5,
                "page": "1",
                "pages": 1
            }
        }
    }
    
    # 返回公告信息
    return jsonify(announcements_data), 200
