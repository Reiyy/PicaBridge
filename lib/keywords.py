import json

import lib.ModeSwitch as ModeSwitch

def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)
    
config = load_config()

# 获取常用标签
def get_keywords(user_id):
    # 从配置文件读取常用标签配置
    keywords = config.get("keywords", {})
    nsfw_keywords = keywords.get("NSFW", [])
    sfw_keywords = keywords.get("SFW", [])

    # 根据用户模式返回常用标签
    if ModeSwitch.GetMode(user_id) == "sfw":
        return {
            "code": 200,
            "message": "success",
            "data": {
                "keywords": sfw_keywords
            }
        }
    else:
        return {
            "code": 200,
            "message": "success",
            "data": {
                "keywords": nsfw_keywords
            }
        }
