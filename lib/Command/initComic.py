import json
import requests
import pymysql
import re

from lib import db

# 加载配置文件
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
        "auto": AutoinitComic,
        "自动": AutoinitComic,
        "full": AutoinitComicInfoFULL,
        "完全": AutoinitComicInfoFULL,
    }

    # 检查命令是否存在
    subcommand_function = subcommand_map.get(subcommand)
    if not subcommand_function:
        return {"status": False, "data": f"未知子命令：{subcommand}"}
    
    return subcommand_function(comic_id, user_id, subcommand_args)

# 自动初始化漫画
def AutoinitComic(comic_id, user_id, subcommand_args):
    # 判断 comic_id 是否为指定值
    if comic_id != "5822a6e3ad7ede654696e482":
        return {"status": False, "data": "该命令为全局命令，只能在留言板中运行！"}

    # 判断subcommand_args的第一个元素
    if not subcommand_args:
        return {"status": False, "data": "缺少子命令参数"}
    
    subcommand = subcommand_args

    if subcommand == "all":
        return AutoinitComic_all()

    # 检查subcommand_args是否为“数字”或“数字,数字”形式
    if re.match(r"^\d+$", subcommand) or re.match(r"^\d+,\d+$", subcommand):
        return AutoinitComic_setpage(subcommand_args)

    return {"status": False, "data": f"未知的参数：{subcommand}"}


# 查询所有漫画数据并初始化未初始化的漫画
def AutoinitComic_all():
    try:
        response = requests.get(f"{LRR_URL}/api/archives")
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
            response = requests.get(f"{LRR_URL}/api/search?start={page}&sortby=date_added&order=desc")
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
    
def AutoinitComicInfoFULL(comic_id, user_id, subcommand_args):
    # #初始化评论ID
    # comment_id = 0
    # 初始化漫画数据列表
    comics_to_process = []
    print(subcommand_args)
    # 判断 subcommand_args 的形式
    if subcommand_args == "all":
        # 判断 comic_id 是否为指定值
        if comic_id != "5822a6e3ad7ede654696e482":
            return {"status": False, "data": "该命令为全局命令，只能在留言板中运行！"}
        # 获取所有漫画数据
        try:
            response = requests.get(f"{LRR_URL}/api/archives")
            response.raise_for_status()
            comics_data = response.json()
            comics_to_process.extend(comics_data)
        except requests.RequestException as e:
            return {"status": False, "data": f"API请求失败: {str(e)}"}
        
        # response_text = {"content": f"完全初始化漫画操作执行成功！\n选择全部范围可能需要较长时间处理，\n执行完成后结果会发送到该条评论的回复中。\n请稍后来查看。"}
        # comment_id = comment.post_comment(comic_id, user_id, response_text)

    elif re.match(r"^\d+$", subcommand_args) or re.match(r"^\d+,\d+$", subcommand_args):
        # 判断 comic_id 是否为指定值
        if comic_id != "5822a6e3ad7ede654696e482":
            return {"status": False, "data": "该命令为全局命令，只能在留言板中运行！"}
        # 如果是指定页数
        try:
            if ',' in subcommand_args:
                start_page, end_page = map(int, subcommand_args.split(','))
            else:
                start_page = int(subcommand_args)
                end_page = start_page
            
            # 获取指定页数的数据
            for page in range(start_page, end_page + 1):
                response = requests.get(f"{LRR_URL}/api/search?start={page}&sortby=date_added&order=desc")
                response.raise_for_status()
                comics_data = response.json().get("data", [])
                comics_to_process.extend(comics_data)
        except ValueError:
            return {"status": False, "data": "无效的页码格式，应该是 '数字' 或 '数字,数字'"}
        except requests.RequestException as e:
            return {"status": False, "data": f"API请求失败: {str(e)}"}

    elif len(subcommand_args) > 7:
        # 判断 comic_id 是否为指定值
        if comic_id != "5822a6e3ad7ede654696e482":
            return {"status": False, "data": "该命令为全局命令，只能在留言板中运行！"}
        # 如果是字母加数字混合形式，获取单本漫画的元数据
        try:
            response = requests.get(f"{LRR_URL}/api/archives/{subcommand_args}/metadata")
            response.raise_for_status()
            comics_data = response.json()
            comics_to_process.append(comics_data)
        except requests.RequestException as e:
            return {"status": False, "data": f"API请求失败: {str(e)}"}

    elif not subcommand_args:
        # 如果没有subcommand_args，使用 comic_id
        try:
            response = requests.get(f"{LRR_URL}/api/archives/{comic_id}/metadata")
            response.raise_for_status()
            comics_data = response.json()
            comics_to_process.append(comics_data)
        except requests.RequestException as e:
            return {"status": False, "data": f"API请求失败: {str(e)}"}

    else:
        return {"status": False, "data": "无效的 subcommand_args 格式"}

    # 遍历需要处理的漫画数据列表
    for comic in comics_to_process:
        arcid = comic.get("arcid")
        
        # 检查数据库中是否已存在该漫画
        try:
            connection = db.get_db_connection()
            with connection.cursor() as cursor:
                cursor.execute("SELECT id FROM comic_info WHERE id = %s", (arcid,))
                exists = cursor.fetchone()
                if not exists:
                    db.initcomic(arcid)  # 初始化漫画数据
        except pymysql.MySQLError as e:
            return {"status": False, "data": f"数据库操作失败: {str(e)}"}
        finally:
            connection.close()

        # 获取数据库操作的数据
        title = comic.get("title")
        pagecount = comic.get("pagecount")
        tags = comic.get("tags", "")
        summary = comic.get("summary") or "PicaBridge - 哔咔桥"

        # 获取作者
        author = ""
        for tag in tags.split(","):
            if tag.startswith("artist:"):
                author = tag.split(":", 1)[1]
                break
            elif tag.startswith("艺术家:"):
                author = tag.split(":", 1)[1]

        # 获取分类
        categories = ["短篇"] if pagecount < 95 else ["长篇"]

        # 获取配置信息并根据规则匹配分类
        categories_rule = config.get("categoriesrule", {})

        for category, rule in categories_rule.items():
            match_mode = rule[0]
            match_tags = rule[1:]

            if match_mode == 1 and all(tag in tags for tag in match_tags):
                categories.append(category)
            elif match_mode == 0 and any(tag in tags for tag in match_tags):
                categories.append(category)

        # 去重分类
        categories = list(set(categories))
        categories = json.dumps(categories, ensure_ascii=False) 
        
        # 获取 created_at 和 updated_at（通过 tags 中的 date_added:）
        created_at = updated_at = None
        for tag in tags.split(","):
            if tag.startswith("date_added:"):
                timestamp = tag.split(":", 1)[1]
                created_at = int(timestamp)
                updated_at = created_at
                break

        # 处理 tags，去除 source:、date_added: 等项，并修改性别相关标签
        cleaned_tags = []
        for tag in tags.split(","):
            if tag.startswith(("source:", "date_added:", "艺术家:", "artist:", "上传者:", "时间戳:", "group:", "language:", "语言:汉语", "语言:翻译", "uploader:", "timestamp:")):
                continue
            elif tag.startswith("男性:"):
                cleaned_tags.append("男:" + tag[3:])
            elif tag.startswith("女性:"):
                cleaned_tags.append("女:" + tag[3:])
            else:
                cleaned_tags.append(tag)

        # 将清理后的标签转换为 JSON 数组形式
        tags = json.dumps(cleaned_tags, ensure_ascii=False)

        # 更新数据库
        try:
            connection = db.get_db_connection()
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE comic_info SET title = %s, pagesCount = %s, author = %s,
                    categories = %s, tags = %s, created_at = %s, updated_at = %s, description = %s
                    WHERE id = %s
                """, (title, pagecount, author, categories, tags, created_at, updated_at, summary, arcid))
                connection.commit()
        except pymysql.MySQLError as e:
            return {"status": False, "data": f"数据库更新失败: {str(e)}"}
        finally:
            connection.close()

    # if comment_id == 0:
    #     return {"status": True, "data": "漫画信息初始化和元数据更新成功"}
    # else:
    #     return {"status": True, "data": "漫画信息初始化和元数据更新成功", "comment_id": comment_id}

    return {"status": True, "data": "漫画信息初始化和元数据更新成功"}
