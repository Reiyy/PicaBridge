import json, requests, pymysql, re
from lib import db


# 加载配置文件
def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

config = load_config()
LANRARAGI_URL = config.get('lanraragi_api')

def run(comic_id, user_id, command_args):

    if not command_args or len(command_args) < 1:
        return {"status": False, "data": "缺少子命令"}

    # 提取子命令标识
    subcommand = command_args[0]
    # 子命令别名映射
    subcommand_map = {
        "auto": AutoinitComic,
        "自动": AutoinitComic,
    }

    # 检查命令是否存在
    subcommand_function = subcommand_map.get(subcommand)
    if not subcommand_function:
        return {"status": False, "data": f"未知子命令：{subcommand}"}

    subcommand_args = command_args[1:]
    return subcommand_function(comic_id, user_id, subcommand_args)

# 自动初始化漫画
def AutoinitComic(comic_id, user_id, subcommand_args):
    # 判断 comic_id 是否为指定值
    if comic_id != "5822a6e3ad7ede654696e482":
        return {"status": False, "data": "该命令为全局命令，只能在留言板中运行！"}

    # 判断subcommand_args的第一个元素
    if not subcommand_args:
        return {"status": False, "data": "缺少子命令参数"}

    subcommand = subcommand_args[0]

    if subcommand == "all":
        return AutoinitComic_all()

    # 检查subcommand_args是否为“数字”或“数字,数字”形式
    if re.match(r"^\d+$", subcommand) or re.match(r"^\d+,\d+$", subcommand):
        return AutoinitComic_setpage(subcommand_args)

    return {"status": False, "data": f"未知的参数：{subcommand}"}


# 查询所有漫画数据并初始化未初始化的漫画
def AutoinitComic_all():
    try:
        response = requests.get(f"{LANRARAGI_URL}/api/archives")
        response.raise_for_status()  # 如果请求失败，抛出异常
        archives = response.json()
    except requests.RequestException as e:
        return {"status": False, "data": f"请求API失败: {str(e)}"}

    # 初始化计数器
    success_count = 0
    error_count = 0

    # 获取数据库连接
    connection = db.get_db_connection()
    cursor = connection.cursor()

    # 遍历获取到的档案数据
    for archive in archives:
        arcid = archive.get("arcid")
        # 检查数据库中是否已存在arcid
        cursor.execute("SELECT id FROM comic_info WHERE id = %s", (arcid,))
        existing = cursor.fetchone()

        if existing:  # 如果数据库中已经有该arcid，跳过
            continue

        # 如果数据库中没有，调用initcomic进行初始化
        if db.initcomic(arcid):
            success_count += 1
        else:
            error_count += 1

    # 完成后关闭数据库连接
    cursor.close()
    connection.close()

    # 构建结果信息
    if error_count == 0:
        return {"status": True, "data": f"共初始化：{success_count} 个项目。"}
    else:
        return {"status": False, "data": f"运行完成，但有部分项失败！\n成功：{success_count}，失败：{error_count}"}

# 查询指定页数的漫画数据并初始化未初始化的漫画
def AutoinitComic_setpage(subcommand_args):
    # 检查subcommand_args格式
    if ',' in subcommand_args:
        # 如果是 "数字,数字" 形式，解析为开始页和结束页
        try:
            start_page, end_page = map(int, subcommand_args.split(','))
        except ValueError:
            return {"status": False, "data": "无效的页码格式，应该是 '数字,数字'"}
    else:
        # 如果是 "数字" 形式，直接将页码作为整数
        try:
            start_page = int(subcommand_args)
            end_page = start_page
        except ValueError:
            return {"status": False, "data": "无效的页码格式，应该是一个数字"}
    
    # 初始化计数器
    success_count = 0
    error_count = 0

    # 获取数据库连接
    connection = db.get_db_connection()
    cursor = connection.cursor()

    # 遍历页数
    for page in range(start_page, end_page + 1):
        # 获取每页的数据
        try:
            response = requests.get(f"{LANRARAGI_URL}/api/search?start={page}&sortby=date_added&order=desc")
            response.raise_for_status()  # 如果请求失败，抛出异常
            data = response.json().get("data", [])
        except requests.RequestException as e:
            return {"status": False, "data": f"请求API失败: {str(e)}"}

        # 遍历当前页的数据
        for item in data:
            arcid = item.get("arcid")
            # 检查数据库中是否已存在arcid
            cursor.execute("SELECT id FROM comic_info WHERE id = %s", (arcid,))
            existing = cursor.fetchone()

            if existing:  # 如果数据库中已经有该arcid，跳过
                continue

            # 如果数据库中没有，调用initcomic进行初始化
            if db.initcomic(arcid):
                success_count += 1
            else:
                error_count += 1

    # 完成后关闭数据库连接
    cursor.close()
    connection.close()

    # 构建结果信息
    if error_count == 0:
        return {"status": True, "data": f"共初始化：{success_count} 个项目。"}
    else:
        return {"status": False, "data": f"运行完成，但有部分项失败！\n成功：{success_count}，失败：{error_count}"}