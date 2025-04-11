import pymysql
import json
import time
import threading

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
                        'maxconnections': 5,
                        'mincached': 1,
                        'blocking': False,
                        'ping': 0
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
            # 首先更新浏览量计数
            sql_update_views = "UPDATE comic_info SET viewsCount = viewsCount + 1 WHERE id = %s"
            cursor.execute(sql_update_views, (comic_id,))

            # 然后获取当前的 viewed_at
            sql_select_viewed_at = "SELECT viewed_at FROM comic_info WHERE id = %s"
            cursor.execute(sql_select_viewed_at, (comic_id,))
            result = cursor.fetchone()

            # 调试输出，打印查询结果
            print("Query result:", result)

            # 检查 result 是否为 None 或者 空元组
            if result is not None and len(result) > 0:
                # 使用键名访问 viewed_at
                viewed_at = json.loads(result['viewed_at']) if result['viewed_at'] else []
            else:
                # 如果没有找到任何记录，则初始化 viewed_at
                viewed_at = []

            # 添加当前时间戳
            viewed_at.append(current_timestamp)

            # 更新 viewed_at 列
            sql_update_viewed_at = "UPDATE comic_info SET viewed_at = %s WHERE id = %s"
            cursor.execute(sql_update_viewed_at, (json.dumps(viewed_at), comic_id))

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