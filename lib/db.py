import pymysql
import json
import time
import threading

from collections import Counter
from dbutils.pooled_db import PooledDB

# 读取配置文件
def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)


class DBPool:
    _lock = threading.Lock()
    _pool = None

    @classmethod
    def get_pool(cls):
        if cls._pool is None:
            with cls._lock:
                if cls._pool is None:
                    config = load_config()
                    db_config = config['db']
                    
                    # 合并默认配置和用户配置
                    pool_config = {
                        'maxconnections': 10,
                        'mincached': 2,
                        'blocking': True,
                        'ping': 7
                    }
                    pool_config.update(db_config.get('pool', {}))

                    cls._pool = PooledDB(
                        creator=pymysql,
                        host=db_config['host'],
                        user=db_config['user'],
                        password=db_config['password'],
                        database=db_config['name'],
                        charset='utf8mb4',
                        cursorclass=pymysql.cursors.DictCursor,
                        **pool_config  # 应用连接池配置
                    )
        return cls._pool

def get_db_connection():
    return DBPool.get_pool().connection()

# 获取数据库用户信息
def get_user_info(user_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT id, email, name, birthday, gender, createdate, title, description, exp, level, role, avatar, frame, verified, characters, favourite FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()

    cursor.close()
    connection.close()

    if user is None:
        return None

    user_info = {
        "id": user.get("id"),
        "email": user.get("email"),
        "name": user.get("name"),
        "birthday": user.get("birthday"),
        "gender": user.get("gender"),
        "createdate": user.get("createdate"),
        "title": user.get("title"),
        "description": user.get("description"),
        "exp": user.get("exp"),
        "level": user.get("level"),
        "role": user.get("role"),
        "avatar": user.get("avatar"),
        "frame": user.get("frame"),
        "verified": user.get("verified"),
        "characters": user.get("characters") if user.get("characters") else None,
        "favourite": user.get("favourite") if user.get("favourite") else None,
        "likeComments": user.get("likeComments") if user.get("likeComments") else None,
    }

    return user_info

# 获取数据库漫画信息
def get_comic_info(comic_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT id, creator, title, description, author, chineseTeam, categories, tags, pagesCount, epsCount, finished, updated_at, created_at, allowDownload, allowComment, viewsCount, likesCount, commentsCount, viewed_at FROM comic_info WHERE id = %s", (comic_id,))
    comic = cursor.fetchone()

    cursor.close()
    connection.close()

    if comic is None:
        return None

    comic_info = {
        "id": comic.get("id"),
        "creator": comic.get("creator"),
        "title": comic.get("title"),
        "description": comic.get("description"),
        "author": comic.get("author"),
        "chineseTeam": comic.get("chineseTeam"),
        "categories": comic.get("categories") if comic.get("categories") else None,
        "tags": comic.get("tags") if comic.get("tags") else None,
        "pagesCount": comic.get("pagesCount"),
        "epsCount": comic.get("epsCount"),
        "finished": comic.get("finished"),
        "updated_at": comic.get("updated_at"),
        "created_at": comic.get("created_at"),
        "allowDownload": comic.get("allowDownload"),
        "allowComment": comic.get("allowComment"),
        "viewsCount": comic.get("viewsCount"),
        "likesCount": comic.get("likesCount"),
        "commentsCount": comic.get("commentsCount"),
        "viewed_at": comic.get("viewed_at") if comic.get("viewed_at") else None,
    }

    return comic_info

def plus_comic_viewsCount(comic_id):
    connection = get_db_connection()
    current_timestamp = int(time.time())  # 获取当前时间戳

    try:
        with connection.cursor() as cursor:
            # 更新浏览量计数及添加浏览时间戳
            cursor.execute(
                "UPDATE comic_info SET viewsCount = viewsCount + 1, "
                "viewed_at = JSON_ARRAY_APPEND(IFNULL(viewed_at, '[]'), '$', %s) "
                "WHERE id = %s",
                (current_timestamp, comic_id)
            )

            # 懒清理，只保留最近1000条时间戳
            import random
            if random.randint(1, 10) == 1:
                cursor.execute(
                    "UPDATE comic_info SET viewed_at = CASE "
                    "WHEN JSON_LENGTH(viewed_at) > 1000 THEN "
                    "  JSON_EXTRACT(viewed_at, CONCAT('$[', JSON_LENGTH(viewed_at) - 1000, ' to last]')) "
                    "ELSE viewed_at END "
                    "WHERE id = %s",
                    (comic_id,)
                )

            connection.commit()
            return 1 if cursor.rowcount > 0 else 0
    finally:
        connection.close()

# 增加一次漫画点赞数
def plus_comic_likesCount(comic_id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "UPDATE comic_info SET likesCount = likesCount + 1 WHERE id = %s"
            cursor.execute(sql, (comic_id,))
            connection.commit()
            return 1 if cursor.rowcount > 0 else 0
    finally:
        connection.close()

# 查询打哔咔的时间
def get_users_isPunched(user_id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT isPunched FROM users WHERE id = %s"
            cursor.execute(sql, (user_id,))
            result = cursor.fetchone()
            return result['isPunched'] if result else None
    finally:
        connection.close()

# 更新打哔咔的时间为当前时间并增加10经验
def update_users_isPunched(user_id):
    connection = get_db_connection()
    try:
        current_timestamp = int(time.time())
        with connection.cursor() as cursor:
            sql = "UPDATE users SET isPunched = %s, exp = exp + 10 WHERE id = %s"
            cursor.execute(sql, (current_timestamp, user_id))
            connection.commit()
            return 1 if cursor.rowcount > 0 else 0
    finally:
        connection.close()


# 查询用户ID
def get_user_id(user_email):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            sql = "SELECT id FROM users WHERE email = %s"
            cursor.execute(sql, (user_email,))
            result = cursor.fetchone()
            if result:
                return result['id']  # 返回用户 ID
            else:
                return None  # 如果没有找到用户，返回 None
    except Exception as e:
        print(f"Error retrieving user ID: {e}")
        return 0
    finally:
        connection.close()  # 确保连接在完成后关闭

# 点赞漫画
def like_comic(is_like, user_id, comic_id):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # 查询当前用户的like字段
            sql = "SELECT `like` FROM users WHERE id = %s"
            cursor.execute(sql, (user_id,))
            result = cursor.fetchone()
            
            if result is None:
                return False  # 用户不存在
            
            # 获取现有的like列表
            like_list = json.loads(result['like']) if result['like'] else []

            if is_like:  # 删除
                if comic_id in like_list:
                    like_list.remove(comic_id)
                    # 更新comic_info表中的likesCount
                    sql_update_likes_count = "UPDATE comic_info SET likesCount = likesCount - 1 WHERE id = %s"
                    cursor.execute(sql_update_likes_count, (comic_id,))
            else:  # 增加
                if comic_id not in like_list:
                    like_list.append(comic_id)
                    # 更新comic_info表中的likesCount
                    sql_update_likes_count = "UPDATE comic_info SET likesCount = likesCount + 1 WHERE id = %s"
                    cursor.execute(sql_update_likes_count, (comic_id,))

            # 更新users表
            sql_update = "UPDATE users SET `like` = %s WHERE id = %s"
            cursor.execute(sql_update, (json.dumps(like_list, ensure_ascii=False), user_id))
            connection.commit()
            return True  # 操作成功

    except Exception as e:
        print(f"Error in like_comic: {e}")
        return 0  # 操作失败

    finally:
        connection.close()

# 收藏漫画
def favourite_comic(is_favourite, user_id, comic_id):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # 查询当前用户的favourite字段
            sql = "SELECT favourite FROM users WHERE id = %s"
            cursor.execute(sql, (user_id,))
            result = cursor.fetchone()
            
            if result is None:
                return False  # 用户不存在
            
            # 获取现有的favourite列表
            favourite_dict = json.loads(result['favourite']) if result['favourite'] else {}

            current_timestamp = int(time.time())  # 获取当前时间戳

            if is_favourite:  # 删除
                if comic_id in favourite_dict:
                    del favourite_dict[comic_id]  # 删除对应的漫画ID
            else:  # 增加
                if comic_id not in favourite_dict:
                    favourite_dict[comic_id] = current_timestamp  # 添加漫画ID及其时间戳

            # 更新数据库
            sql_update = "UPDATE users SET favourite = %s WHERE id = %s"
            cursor.execute(sql_update, (json.dumps(favourite_dict, ensure_ascii=False), user_id))
            connection.commit()
            return True  # 操作成功

    except Exception as e:
        print(f"Error in favourite_comic: {e}")
        return 0  # 操作失败

    finally:
        connection.close()

# 是否点赞漫画
def is_like_comic(user_id, comic_id):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # 查询当前用户的like字段
            sql = "SELECT `like` FROM users WHERE id = %s"
            cursor.execute(sql, (user_id,))
            result = cursor.fetchone()
            
            if result is None:
                return False  # 用户不存在
            
            # 检查comic_id是否在like列表中
            like_list = json.loads(result['like']) if result['like'] else []
            return comic_id in like_list  # 存在返回True，不存在返回False

    except Exception as e:
        print(f"Error in get_like_comic: {e}")
        return 0  # 操作失败

    finally:
        connection.close()

# 是否收藏漫画
def is_favourite_comic(user_id, comic_id):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # 查询当前用户的favourite字段
            sql = "SELECT favourite FROM users WHERE id = %s"
            cursor.execute(sql, (user_id,))
            result = cursor.fetchone()
            
            if result is None:
                return False  # 用户不存在
            
            # 检查comic_id是否在favourite列表中
            favourite_list = json.loads(result['favourite']) if result['favourite'] else []
            return comic_id in favourite_list  # 存在返回True，不存在返回False

    except Exception as e:
        print(f"Error in get_favourite_comic: {e}")
        return 0  # 操作失败

    finally:
        connection.close()

# 获取收藏
def get_user_favourite(user_id):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            sql = "SELECT favourite FROM users WHERE id = %s"
            cursor.execute(sql, (user_id,))
            result = cursor.fetchone()

            if result is None:
                return None  # 用户不存在
            
            # 返回favourite列表
            return json.loads(result['favourite']) if result['favourite'] else []

    except Exception as e:
        print(f"Error in get_user_favourite: {e}")
        return 0  # 操作失败

    finally:
        connection.close()

# 获取点赞
def get_user_like(user_id):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            sql = "SELECT `like` FROM users WHERE id = %s"
            cursor.execute(sql, (user_id,))
            result = cursor.fetchone()

            if result is None:
                return None  # 用户不存在
            
            # 返回like列表
            return json.loads(result['like']) if result['like'] else []

    except Exception as e:
        print(f"Error in get_user_like: {e}")
        return 0  # 操作失败

    finally:
        connection.close()

# 更新用户简介
def write_user_description(user_id, text):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # 更新用户的description字段
            sql = "UPDATE users SET description = %s WHERE id = %s"
            cursor.execute(sql, (text, user_id))
            connection.commit()  # 提交更改
            
            return True  # 操作成功

    except Exception as e:
        print(f"Error in write_user_description: {e}")
        return False  # 操作失败

    finally:
        connection.close()

# 获取所有用户id
def get_all_userid():
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            sql = "SELECT id FROM users"
            cursor.execute(sql)
            result = cursor.fetchall()
            return [row['id'] for row in result]  # 返回用户ID列表
    except Exception as e:
        print(f"Error in get_all_userid: {e}")
        return []
    finally:
        connection.close()

# 获取点赞评论
def is_like_comment(user_id, comment_id):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # 查询当前用户的like字段
            sql = "SELECT `likeComments` FROM users WHERE id = %s"
            cursor.execute(sql, (user_id,))
            result = cursor.fetchone()
            
            if result is None:
                return False  # 用户不存在
            
            # 检查comic_id是否在like列表中
            likeComments_list = json.loads(result['likeComments']) if result['likeComments'] else []
            return comment_id in likeComments_list  # 存在返回True，不存在返回False

    except Exception as e:
        print(f"Error in get_like_comment: {e}")
        return 0  # 操作失败

    finally:
        connection.close()

# 点赞评论
def like_comment(is_like, user_id, comment_id):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # 查询当前用户的like字段
            sql = "SELECT `likeComments` FROM users WHERE id = %s"
            cursor.execute(sql, (user_id,))
            result = cursor.fetchone()
            
            if result is None:
                return False  # 用户不存在
            
            # 获取现有的like列表
            likeComments_list = json.loads(result['likeComments']) if result['likeComments'] else []

            if is_like:  # 删除
                if comment_id in likeComments_list:
                    likeComments_list.remove(comment_id)
                    # 更新comments表中的likesCount
                    sql_update_likes_count = "UPDATE comments SET likesCount = likesCount - 1 WHERE id = %s"
                    cursor.execute(sql_update_likes_count, (comment_id,))
            else:  # 增加
                if comment_id not in likeComments_list:
                    likeComments_list.append(comment_id)
                    # 更新comments表中的likesCount
                    sql_update_likes_count = "UPDATE comments SET likesCount = likesCount + 1 WHERE id = %s"
                    cursor.execute(sql_update_likes_count, (comment_id,))

            # 更新users表
            sql_update = "UPDATE users SET `likeComments` = %s WHERE id = %s"
            cursor.execute(sql_update, (json.dumps(likeComments_list, ensure_ascii=False), user_id))
            connection.commit()
            return True  # 操作成功

    except Exception as e:
        print(f"Error in like_comment: {e}")
        return 0  # 操作失败

    finally:
        connection.close()

def initcomic(comic_id):
    # 获取数据库连接
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # 检查是否已经存在对应的 comic_id
            cursor.execute("SELECT 1 FROM comic_info WHERE id = %s", (comic_id,))
            exists = cursor.fetchone()

            if exists:  # 如果记录已经存在
                return False

            # 插入默认值
            default_values = {
                "id": comic_id,
                "creator": "7v5za3f62102s6t81wue5uyo",
                "title": "",
                "description": "PicBridge - 哔咔桥",
                "author": "",
                "chineseTeam": "",
                "categories": "[]",
                "tags": "[]",
                "pagesCount": 1,
                "epsCount": 1,
                "finished": 1,
                "updated_at": int(time.time()),
                "created_at": int(time.time()),
                "allowDownload": 0,
                "allowComment": 1,
                "viewsCount": 0,
                "likesCount": 0,
                "commentsCount": 0,
                "viewed_at": "[]"
            }

            # 插入新记录
            cursor.execute("""
                INSERT INTO comic_info (id, creator, title, description, author, chineseTeam, 
                categories, tags, pagesCount, epsCount, finished, updated_at, created_at, 
                allowDownload, allowComment, viewsCount, likesCount, commentsCount, viewed_at)
                VALUES (%(id)s, %(creator)s, %(title)s, %(description)s, %(author)s, %(chineseTeam)s, 
                %(categories)s, %(tags)s, %(pagesCount)s, %(epsCount)s, %(finished)s, %(updated_at)s, 
                %(created_at)s, %(allowDownload)s, %(allowComment)s, %(viewsCount)s, %(likesCount)s, 
                %(commentsCount)s, %(viewed_at)s)
            """, default_values)

            connection.commit()

        return True

    except pymysql.MySQLError as e:
        print(f"数据库操作失败: {str(e)}")
        return False

    finally:
        connection.close()


# 通过用户名获取用户id
def get_userid(user_name):
    # 获取数据库连接
    connection = get_db_connection()
    
    try:
        with connection.cursor() as cursor:
            sql = "SELECT id FROM users WHERE email = %s"
            cursor.execute(sql, (user_name,))
            result = cursor.fetchone()
            
            if result:
                return result['id']
            else:
                return None
    finally:
        connection.close()

# 获取用户的用户组
def get_user_characters(userid):
    connection = get_db_connection()
    
    try:
        with connection.cursor() as cursor:
            sql = "SELECT characters FROM users WHERE id = %s"
            cursor.execute(sql, (userid,))
            result = cursor.fetchone()
            
            if result:
                characters = result['characters']
                if isinstance(characters, str):
                    try:
                        characters = json.loads(characters)
                    except json.JSONDecodeError:
                        characters = []
                return characters
            else:
                return []
    finally:
        connection.close()

# 获取关联推荐漫画
def get_recommend_comics(comic_id, limit=10):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, author, categories, tags, viewsCount
        FROM comic_info
        WHERE id = %s
    """, (comic_id,))

    current = cursor.fetchone()
    if not current:
        cursor.close()
        connection.close()
        return []

    def to_set(field):
        if not field:
            return set()
        if isinstance(field, list):
            return set(field)
        if isinstance(field, str):
            try:
                data = json.loads(field)
                return set(data) if isinstance(data, list) else set()
            except:
                return set()
        return set()

    current_author = current.get("author")
    current_categories = to_set(current.get("categories"))
    current_tags = to_set(current.get("tags"))

    # SQL预筛选
    cursor.execute("""
        SELECT id, author, categories, tags, viewsCount
        FROM comic_info
        WHERE id != %s
        LIMIT 2000
    """, (comic_id,))

    candidates = cursor.fetchall()

    # 评分
    scored = []

    for comic in candidates:
        score = 0

        author = comic.get("author")
        categories = to_set(comic.get("categories"))
        tags = to_set(comic.get("tags"))
        views = comic.get("viewsCount") or 0


        # 作者权重
        if author and author == current_author:
            score += 6

        # 标签交集
        tag_overlap = len(current_tags & tags)
        score += tag_overlap * 3

        # 分类交集
        category_overlap = len(current_categories & categories)
        score += category_overlap * 2

        if score > 0:
            scored.append({
                "id": comic["id"],
                "score": score,
                "author": author
            })

    # 排序
    scored.sort(key=lambda x: x["score"], reverse=True)

    # 作者限制
    result = []
    author_count = {}

    for item in scored:
        author = item["author"]

        if author:
            count = author_count.get(author, 0)
            if count >= 3:
                continue
            author_count[author] = count + 1

        result.append(item["id"])

        if len(result) >= limit:
            break

    cursor.close()
    connection.close()

    return result



# 获取用户漫画推荐
def get_user_recommend_comics(user_id, limit=4):
    connection = get_db_connection()
    cursor = connection.cursor()

    # 获取用户收藏和点赞列表
    cursor.execute("""
        SELECT favourite, `like`
        FROM users
        WHERE id = %s
    """, (user_id,))
    
    user_record = cursor.fetchone()
    
    if not user_record:
        cursor.close()
        connection.close()
        return []

    interacted_ids = set() # 结合并去重

    # 解析favourite数据
    favourite_data = user_record.get("favourite")
    if favourite_data:
        if isinstance(favourite_data, str):
            try:
                favourite_data = json.loads(favourite_data)
            except:
                favourite_data = {}
        if isinstance(favourite_data, dict):
            interacted_ids.update(favourite_data.keys())

    # 解析like数据
    like_data = user_record.get("like")
    if like_data:
        if isinstance(like_data, str):
            try:
                like_data = json.loads(like_data)
            except:
                like_data = []
        if isinstance(like_data, list):
            interacted_ids.update(like_data)

    # 如果用户没有任何收藏或点赞，返回空
    if not interacted_ids:
        cursor.close()
        connection.close()
        return []

    # 2查询用户收藏和点赞的漫画的标签和分类
    def to_list_safe(field):
        if not field: return []
        if isinstance(field, list): return field
        if isinstance(field, str):
            try:
                data = json.loads(field)
                return data if isinstance(data, list) else []
            except:
                return []
        return []

    format_strings = ','.join(['%s'] * len(interacted_ids))
    cursor.execute(f"""
        SELECT categories, tags
        FROM comic_info
        WHERE id IN ({format_strings})
    """, tuple(interacted_ids))
    
    interacted_comics = cursor.fetchall()

    # 统计标签和分类的出现频率
    tag_counter = Counter()
    category_counter = Counter()

    for comic in interacted_comics:
        categories = to_list_safe(comic.get("categories"))
        tags = to_list_safe(comic.get("tags"))
        
        category_counter.update(categories)
        tag_counter.update(tags)

    # 如果历史记录里没有任何有效的标签和分类，直接结束
    if not tag_counter and not category_counter:
        cursor.close()
        connection.close()
        return []

    # 获取候选漫画根据点击数排序，排除已经收藏和点赞过的漫画
    cursor.execute(f"""
        SELECT id, author, categories, tags, viewsCount
        FROM comic_info
        WHERE id NOT IN ({format_strings})
        ORDER BY viewsCount DESC
        LIMIT 2000
    """, tuple(interacted_ids))

    candidates = cursor.fetchall()

    # 评分
    scored = []

    for comic in candidates:
        score = 0
        comic_categories = to_list_safe(comic.get("categories"))
        comic_tags = to_list_safe(comic.get("tags"))
        author = comic.get("author")

        # 出现频率乘基础分数，出现次数越多评分越高
        for tag in comic_tags:
            if tag in tag_counter:
                score += tag_counter[tag] * 3

        for cat in comic_categories:
            if cat in category_counter:
                score += category_counter[cat] * 2

        if score > 0:
            scored.append({
                "id": comic["id"],
                "score": score,
                "author": author
            })

    # 排序
    scored.sort(key=lambda x: x["score"], reverse=True)

    # 返回
    result = []
    author_count = {}

    for item in scored:
        author = item["author"]

        if author:
            count = author_count.get(author, 0)
            if count >= 1: # 作者限制，最多1个同作者
                continue
            author_count[author] = count + 1

        result.append(item["id"])

        if len(result) >= limit:
            break

    cursor.close()
    connection.close()

    return result