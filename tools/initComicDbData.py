import json, os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from datetime import datetime
from lib import api, db

# 加载匹配规则文件
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
rules_path = os.path.join(root_dir, 'rules.json')
with open(rules_path, 'r', encoding='utf-8') as file:
    rules = json.load(file)

def main():
    while True:
        print("选择要处理的漫画:")
        print("1. 新漫画")
        print("2. 指定漫画")
        print("3. 全部")
        choice = input("请输入选项（1/2/3）：")

        if choice == '1':
            process_new_projects()
        elif choice == '2':
            comic_id = input("请输入漫画ID：")
            process_specific_project(comic_id)
        elif choice == '3':
            confirm = input("确认选择全部漫画？已存在的漫画信息会被覆盖！输入Y确认，N取消：")
            if confirm.upper() == 'Y':
                process_all_projects()
            else:
                continue
        else:
            print("无效选项，请重新选择。")

def process_new_projects():
    print("开始处理新漫画...")
    comicids = [archive['arcid'] for archive in api.get_all_archives() if archive is not None]

    new_comics = []  # 存放新漫画ID

    for comic_id in comicids:
        if db.get_comic_info(comic_id) is None:
            new_comics.append(comic_id)

    process_comics(new_comics)

def process_specific_project(comic_id):
    print(f"开始处理指定漫画：{comic_id}")
    process_comics([comic_id])

def process_all_projects():
    print("开始处理所有漫画...")
    comics = [archive['arcid'] for archive in api.get_all_archives() if archive is not None]
    process_comics(comics)

def process_comics(comic_ids):
    print(f"开始处理，共 {len(comic_ids)} 本漫画")
    failed_comics = []  # 记录失败的comic_id
    none_title_comics = []  # 记录失败的comic_id
    for comic_id in comic_ids:
        print(f"当前处理漫画：{comic_id}")
        
        metadata = api.get_archive_metadata(comic_id)
        if metadata is None:
            print("正在通过API获取元数据... 失败。")
            if input("是否忽略并继续处理下一个？Y确认，N不继续，返回选择页：").upper() != 'Y':
                return
            failed_comics.append(comic_id)
            continue
        
        print("正在通过API获取信息... 成功，继续处理...")
        
        # 获取标题
        comic_title = extract_title(metadata["title"])
        if comic_title is None:
            print("标题获取失败, 不是标准格式，已记录。")
            none_title_comics.append(comic_id)
            # continue
        print("标题获取成功")

        # 获取分类
        comic_categories = process_comic_categories(metadata["tags"])

        # 获取标签
        comic_tags = process_comic_tags(metadata["tags"])

        # 获取作者
        comic_author = process_comic_author(metadata["tags"])

        # 提取并格式化更新和创建时间
        def extract_timestamp(tags, prefix):
            for tag in tags.split(","):
                tag = tag.strip()
                if tag.startswith(prefix):
                    return tag.split(':', 1)[1].strip()
            return None

        # 获取创建时间
        metadata_tags = metadata.get("tags", "")
        timestamp_value = extract_timestamp(metadata_tags, "timestamp:") or extract_timestamp(metadata_tags, "时间戳:")
        date_added_value = extract_timestamp(metadata_tags, "date_added:")

        # 如果 timestamp_value 为空，使用 date_added_value
        comic_createdtime = int(timestamp_value) if timestamp_value is not None else int(date_added_value)
        comic_updatedtime = int(date_added_value)
        
        # 获取页数
        comic_pages = metadata["pagecount"]

        # 根据页数添加分类
        if comic_pages > 95:
            comic_categories.append("长篇")
        else:
            comic_categories.append("短篇")

        # 写入数据库
        write_to_database(comic_id, comic_title, comic_author, comic_tags, comic_categories, comic_updatedtime, comic_createdtime, comic_pages)
    
    print(f"Done. 共 {len(comic_ids)} 个项目，成功 {len(comic_ids) - len(failed_comics)} 个，失败 {len(failed_comics)} 个")
    if failed_comics:
        print("失败漫画ID：")
        for failed_ids in failed_comics:
            print(failed_ids)

    if none_title_comics:
        print("无标题漫画ID：")
        for none_title_ids in none_title_comics:
            print(none_title_ids)

# 提取标题
def extract_title(title):
    if title.startswith('[') and ']' in title:
        end = title.find(']')
        content = title[end + 1:].strip()
        next_start = content.find('[')

        if next_start != -1:
            return content[:next_start].strip()
        else:
            return content.strip()
        
    return None

# 测试
# 匹配分类
def process_comic_categories(tags):
    comic_categories = []
    tags_list = tags.split(",")
    tags_list = [tag.strip() for tag in tags_list]
    for category, (match_type, *match_terms) in rules['categories'].items():
        if match_type == 1:  # 单项匹配
            if any(term in tags for term in match_terms):
                comic_categories.append(category)
        else:  # 多项匹配
            if all(term in tags for term in match_terms):
                comic_categories.append(category)
    return comic_categories

# 匹配标签
def process_comic_tags(tags):
    comic_tags = []
    for tag in tags.split(","):
        tag = tag.strip()
        if tag in rules['tags']:
            comic_tags.append(rules['tags'][tag])
    return comic_tags

def process_comic_tags(tags):
    comic_tags = []
    for tag in tags.split(","):
        tag = tag.strip()
        # 检查规则中是否存在匹配的标签
        if tag in rules['tags']:
            # 如果存在，添加规则中定义的值
            comic_tags.append(rules['tags'][tag])
        else:
            # 如果没有匹配的规则，仍然可以选择是否将原始标签添加到结果中
            # comic_tags.append(tag)  # 可选：添加原始标签
            pass  # 不添加原始标签
    return comic_tags

# 匹配作者
def process_comic_author(tags):
    comic_author = None
    for tag in tags.split(","):
        tag = tag.strip()
        if tag in rules['author']:
            comic_author = rules['author'][tag]
            break
    return comic_author

# 转换时间
def format_timestamp(ts):
    if ts is not None:
        # return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
        return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    return None


# 写入数据库
def write_to_database(comic_id, comic_title, comic_author, comic_tags, comic_categories, comic_updatedtime, comic_createdtime, comic_pages):
    print("将以下信息写入数据库...")
    print(f"comic_id = {comic_id}")
    print(f"comic_title = {comic_title}")
    print(f"comic_author = {comic_author}")
    print(f"comic_tags = {comic_tags}")
    print(f"comic_categories = {comic_categories}")
    print(f"comic_updatedtime = {comic_updatedtime}")
    print(f"comic_createdtime = {comic_createdtime}")
    print(f"comic_pages = {comic_pages}")

    # 获取数据库连接信息
    connection = db.get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
            INSERT INTO comic_info (id, title, author, tags, categories, updated_at, created_at, pagesCount)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                title = VALUES(title),
                author = VALUES(author),
                tags = VALUES(tags),
                categories = VALUES(categories),
                updated_at = VALUES(updated_at),
                created_at = VALUES(created_at),
                pagesCount = VALUES(pagesCount)
            """
            cursor.execute(sql, (comic_id, comic_title, comic_author, json.dumps(comic_tags, ensure_ascii=False), json.dumps(comic_categories, ensure_ascii=False), comic_updatedtime, comic_createdtime, comic_pages))
            connection.commit()
            print("写入数据库成功...")
    except Exception as e:
        print(f"写入数据库失败: {e}")
    finally:
        connection.close()


if __name__ == '__main__':
    main()
