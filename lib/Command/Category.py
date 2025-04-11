import json
import requests
import pymysql

from lib import db

def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

config = load_config()
LRR_URL = config.get('lrr_Api')

# 允许调用该命令的用户组
allow_groups = ["official", "knight"]

def run(comic_id, user_id, command_args):
    # 检测用户权限
    user_groups = db.get_user_characters(user_id)
    for group in user_groups:
        if group not in allow_groups:
            return {"status": False, "data": "你当前无权执行此命令！"}

    if not command_args or len(command_args) < 1:
        return {"status": False, "data": "缺少子命令"}

    # 提取子命令标识
    subcommand_parts = command_args.split(" ", 1)
    subcommand = subcommand_parts[0]
    subcommand_args = subcommand_parts[1] if len(subcommand_parts) > 1 else ""
    
    # 子命令别名映射
    subcommand_map = {
        "auto": AutoCategory,
        "自动": AutoCategory,
    }

    # 检查命令是否存在
    subcommand_function = subcommand_map.get(subcommand)
    if not subcommand_function:
        return {"status": False, "data": f"未知子命令：{subcommand}"}

    subcommand_args = command_args[1:]
    return subcommand_function(comic_id, user_id, subcommand_args)

# 自动获取分类命令
def AutoCategory(comic_id, user_id, subcommand_args):
    # 获取配置信息
    config = load_config()

    categories_rule = {}
    for category_name, category_data in config.get("categories", {}).items():
        categories_rule[category_name] = category_data.get("rule", [])

    # 获取 API 数据
    try:
        response = requests.get(f"{LRR_URL}/api/archives/{comic_id}/metadata")
        response.raise_for_status()
        metadata = response.json()
    except requests.RequestException as e:
        return {"status": False, "data": f"API请求失败: {str(e)}"}

    # 获取 pagecount 并初始化分类数组
    pagecount = metadata.get("pagecount", 0)
    categories = ["短篇"] if pagecount < 95 else ["长篇"]

    # 解析标签
    tags = metadata.get("tags", "")

    # 根据规则匹配分类
    for category, rule in categories_rule.items():
        match_mode = rule[0]  # 匹配模式标识符
        match_tags = rule[1:]  # 标签规则

        if match_mode == 1:  # 完全匹配
            if all(tag in tags for tag in match_tags):
                categories.append(category)
        elif match_mode == 0:  # 部分匹配
            if any(tag in tags for tag in match_tags):
                categories.append(category)

    # 去重
    categories = list(set(categories))

    # 写入数据库
    try:
        connection = db.get_db_connection()
        with connection.cursor() as cursor:
            # 检查是否存在对应的 comic_id
            cursor.execute("SELECT 1 FROM comic_info WHERE id = %s", (comic_id,))
            exists = cursor.fetchone()

            if not exists:  # 如果不存在，调用初始化函数
                if not db.initcomic(comic_id):
                    return {"status": False, "data": "初始化漫画数据失败"}

            # 更新 categories 字段
            categories_json = json.dumps(categories, ensure_ascii=False)
            cursor.execute(
                "UPDATE comic_info SET categories = %s WHERE id = %s",
                (categories_json, comic_id)
            )
            connection.commit()

    except pymysql.MySQLError as e:
        return {"status": False, "data": f"数据库操作失败: {str(e)}"}

    finally:
        connection.close()

    # 返回结果
    return {"status": True, "data": f"已添加分类: {categories}"}