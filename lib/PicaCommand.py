import json
import requests
import pymysql
from lib import comment, db

def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

config = load_config()
LANRARAGI_URL = config.get('lanraragi_api')


def run(comic_id, user_id, contentdata):
    # 判断权限
    if user_id != "7v5za3f62102s6t81wue5uyo":
        return {"status": False, "message": "无权限执行命令"}

    # 提取命令内容
    content = contentdata.get("content", "")

    # 解析命令和参数
    parts = content.split(" ", 2)  # 分割命令字符串为最多三个部分
    if len(parts) < 2:
        return {"status": False, "message": "命令格式错误"}

    command_name = parts[1]  # 获取命令名称
    command_args = parts[2] if len(parts) > 2 else ""  # 获取命令参数部分

    # 映射命令到命令函数
    command_map = {
        "自动分类": AutoCategory,
        "autocat": AutoCategory,
    }

    # 检查命令是否存在
    command_func = command_map.get(command_name)
    if not command_func:
        return {"status": False, "message": f"未知命令：{command_name}"}

    # 调用命令函数并处理返回值
    result = command_func(comic_id, user_id, command_args)  # 调用命令函数，传递参数
    status = result.get("status", False)  # 获取状态标记
    data = result.get("data", "")  # 获取返回的信息

    # 构建返回文本
    if status:
        response_text = f"{content}\n成功：{data}"
    else:
        response_text = f"{content}\n失败：{data}"
    response_payload = json.dumps({"content": response_text})
    # 将返回文本作为评论发布
    return comment.post_comment(comic_id, user_id, response_payload)

# 自动获取分类命令
def AutoCategory(comic_id, user_id, command_args):
    # 获取配置信息
    config = load_config()
    categories_rule = config["categoriesrule"]

    # 获取 API 数据
    try:
        response = requests.get(f"{LANRARAGI_URL}/api/archives/{comic_id}/metadata")
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
