import json, importlib, requests, pymysql
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

    main_command = parts[1]  # 获取主命令名称
    command_args = parts[2] if len(parts) > 2 else ""  # 获取命令参数部分

    # 主命令别名映射
    alias_map = {
        "分类": "Category",
    }

    # 获取实际的主命令名称
    main_command = alias_map.get(main_command, main_command)

    try:
        # 动态加载主命令模块
        MianCMDModule = importlib.import_module(f"lib.Command.{main_command}")
        # 调用主命令函数
        result = MianCMDModule.run(comic_id, user_id, command_args)
    except ModuleNotFoundError:
        return {"status": False, "message": f"未知命令：{main_command}"}

    # 获取返回值中的状态和数据
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