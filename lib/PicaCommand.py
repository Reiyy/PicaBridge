import json
import importlib

from lib import comment

def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

config = load_config()
LRR_URL = config.get('lrr_Api')

def run(comic_id, user_id, contentdata):
    # 提取命令内容
    content = contentdata.get("content", "")
    picacommand = content[1:].strip() # 去除前缀并去除前后多余空格
    parts = picacommand.split(" ", 1) # 分割主命令和命令参数
    main_command = parts[0]  # 获取主命令
    command_args = parts[1] if len(parts) > 1 else ""  # 获取命令参数

    # 主命令别名映射
    alias_map = {
        "分类": "Category",
        "categ": "Category",
        "初始化漫画": "initComic",
        "initcmc": "initComic",
        "编辑简介": "EditSummary",
        "editdesc": "EditSummary",
        "模式切换": "ModeChange",
        "modesw": "ModeChange",
        "用户": "User",
        "user": "User"
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

    response_payload = {"content": response_text}

    # # 判断返回参数中是否有 "comment_id"
    # if "comment_id" in result:
    #     comment_id = result.get("comment_id")  # 获取 comment_id
    #     # 将返回文本作为子评论发布
    #     comment.post_child_comment(comment_id, user_id, response_payload)

    # 将返回文本作为主评论发布
    return comment.post_comment(comic_id, user_id, response_payload)