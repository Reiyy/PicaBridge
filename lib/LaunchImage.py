import datetime
import random
import json

from flask import jsonify

import lib.db as db
import lib.ModeSwitch as ModeSwitch

def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

config = load_config()

def extract_image_name(url):
    return url.rstrip('/').split('/')[-1]

# 从配置中读取普通日启动图
general_images_list = list(config.get("LaunchImage", {}).get("GeneralDay", {}).values())
# 存储本轮内未使用的普通日启动图索引
unused_general_indices = []
# 从配置中读取NSFW启动图
nsfw_images_list = list(config.get("LaunchImage", {}).get("NSFW", {}).values())
# 存储本轮内未使用的NSFW启动图索引
unused_nsfw_indices = []

def Get(user_name):
    # 使用用户名获取用户ID
    user_id = db.get_userid(user_name)
    # 获取当前日期，格式为 MMDD
    today = datetime.datetime.now().strftime("%m%d")
    # 判断是否为特殊日期
    special_days = config.get("LaunchImage", {}).get("SpeciallDay", {})
    for holiday, data in special_days.items():
        special_date, image_url, blur_image_url = data
        if special_date == today:
            return jsonify({
                "image_url": image_url,
                "blur_image_url": blur_image_url,
                "image_name": extract_image_name(image_url),
                "blur_image_name": extract_image_name(blur_image_url)
            })
    
    # 如果用户模式为SFW，返回正常启动图，否则返回NSFW启动图
    if ModeSwitch.GetMode(user_id) == "sfw":
        # 非特殊日,使用普通图,利用随机列表选取并且不重复
        global unused_general_indices
        if not general_images_list:
            return jsonify({"error": "No general launch images configured"}), 500
        
        if not unused_general_indices:
            # 新一轮：生成新的随机打乱的索引列表
            unused_general_indices = list(range(len(general_images_list)))
            random.shuffle(unused_general_indices)
        
        # 按顺序取出一个启动图
        index = unused_general_indices.pop()
        image_url, blur_image_url = general_images_list[index]
        
        # 返回数据
        return jsonify({
            "image_url": image_url,
            "blur_image_url": blur_image_url,
            "image_name": extract_image_name(image_url),
            "blur_image_name": extract_image_name(blur_image_url)
        })
    else:
        # 返回NSFW启动图
        global unused_nsfw_indices
        if not nsfw_images_list:
            return jsonify({"error": "No general launch images configured"}), 500
        
        if not unused_nsfw_indices:
            # 新一轮：生成新的随机打乱的索引列表
            unused_nsfw_indices = list(range(len(nsfw_images_list)))
            random.shuffle(unused_nsfw_indices)
        
        # 按顺序取出一个启动图
        index = unused_nsfw_indices.pop()
        image_url, blur_image_url = nsfw_images_list[index]
        
        # 返回数据
        return jsonify({
            "image_url": image_url,
            "blur_image_url": blur_image_url,
            "image_name": extract_image_name(image_url),
            "blur_image_name": extract_image_name(blur_image_url)
        })
