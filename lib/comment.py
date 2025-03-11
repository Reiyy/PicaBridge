import pymysql
import json
import math
import string
import random
import time
import datetime

from flask import jsonify

import lib.db as db


def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)
    
config = load_config()
PICABRIDGE_URL = config.get('PicaBridge_URL')

# 点赞评论
def like_comment(user_id, comment_id):
    is_like_comment = db.is_like_comment(user_id, comment_id)
    result = db.like_comment(is_like_comment, user_id, comment_id)

    if result:
        if not is_like_comment:  # 如果没有点赞，则执行添加点赞操作
            return jsonify({
                "code": 200,
                "message": "success",
                "data": {
                    "action": "like"
                }
            })
        else:  # 如果已经点赞，则执行取消点赞操作
            return jsonify({
                "code": 200,
                "message": "success",
                "data": {
                    "action": "unlike"
                }
            })
    else:
        return jsonify({
            "code": 500,
            "message": "操作失败"
        })


# 创建随机主评论ID
def generate_comment_id():
    part1 = ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))
    part2 = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
    return part1 + part2

# 创建随机子评论ID
def generate_reply_comment_id(parent_id):
    part1 = parent_id[:20]  # 前20位为主评论ID
    part2 = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))  # 随机4位
    return part1 + part2

# 加载主评论列表
def load_comments(comic_id, page, user_id):
    connection = db.get_db_connection()
    
    try:
        with connection.cursor() as cursor:
            # 分页限制
            limit = 20
            offset = (int(page) - 1) * limit
            
            # 查询置顶评论
            query_top_comments = """
            SELECT * FROM comments 
            WHERE comic_id = %s AND isTop = 1 
            ORDER BY created_at ASC
            """
            cursor.execute(query_top_comments, (comic_id,))
            top_comments = cursor.fetchall()

            # 查询主评论 (parent_id为空) 按照置顶和时间排序
            query_main_comments = """
            SELECT * FROM comments 
            WHERE comic_id = %s AND parent_id IS NULL 
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
            """
            cursor.execute(query_main_comments, (comic_id, limit, offset))
            main_comments = cursor.fetchall()

            # 查询该漫画的评论总数
            query_total_comments = """
            SELECT commentsCount FROM comic_info WHERE id = %s
            """
            cursor.execute(query_total_comments, (comic_id,))
            total_comments = cursor.fetchone()['commentsCount']

            # 构建返回评论数据
            comments_list = []
            for comment in main_comments:
                created_at_iso = datetime.datetime.utcfromtimestamp(comment['created_at']).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                comment_info = {
                    "_id": comment['id'],
                    "content": comment['content'],
                    "_comic": comment['comic_id'],
                    "totalComments": comment['commentsCount'],  # 子评论数量
                    "isTop": bool(comment['isTop']),
                    "hide": bool(comment['hide']),
                    "created_at": created_at_iso,
                    "id": comment['id'],
                    "likesCount": comment['likesCount'],
                    "commentsCount": comment['commentsCount']  # 子评论数量
                }

                # 获取用户信息
                user_info = db.get_user_info(comment['user_id']) or {}
                avatar_data = {
                    "originalName": user_info.get("avatar").split("/")[-1] if user_info.get("avatar") else "",
                    "path": "/".join(user_info.get("avatar").split("/")[3:]) if user_info.get("avatar") else "",
                    "fileServer": PICABRIDGE_URL
                }

                characters = json.loads(user_info.get("characters", '[]')) if isinstance(user_info.get("characters"), str) else user_info.get("characters", [])

                comment_info["_user"] = {
                    "_id": user_info.get("id"),
                    "name": user_info.get("name"),
                    "gender": user_info.get("gender"),
                    "title": user_info.get("title"),
                    "verified": bool(user_info.get("verified")),
                    "exp": user_info.get("exp"),
                    "level": user_info.get("level"),
                    "characters": characters,
                    "role": user_info.get("role"),
                    "avatar": avatar_data,
                    "slogan": user_info.get("description")
                }

                # 检查当前用户是否点赞该评论
                comment_id = comment['id']
                is_liked = db.is_like_comment(user_id, comment_id)
                comment_info["isLiked"] = is_liked

                # 如果 hideTop 为 1，则不将该评论添加到 comments_list
                if comment.get('hideTop') == 1:
                    continue  # 不将该评论添加到 comments_list

                comments_list.append(comment_info)
            
            # 计算过滤后的评论数
            total_filtered_comments = len(comments_list)

            # 计算分页信息
            pages = math.ceil(total_filtered_comments / limit)
            pagination_info = {
                "total": total_filtered_comments,
                "limit": limit,
                "page": int(page),
                "pages": pages
            }

            # 返回
            return {
                "code": 200,
                "message": "success",
                "data": {
                    "comments": {
                        "docs": comments_list,
                        "total": pagination_info['total'],
                        "limit": pagination_info['limit'],
                        "page": pagination_info['page'],
                        "pages": pagination_info['pages']
                    },
                    "topComments": [
                        {
                            "_id": top_comment['id'],
                            "content": top_comment['content'],
                            "_user": {
                                "_id": user_info.get("id"),
                                "name": user_info.get("name"),
                                "gender": user_info.get("gender"),
                                "slogan": user_info.get("description"),
                                "title": user_info.get("title"),
                                "verified": bool(user_info.get("verified")),
                                "exp": user_info.get("exp"),
                                "level": user_info.get("level"),
                                "characters": json.loads(user_info.get("characters", '[]')),
                                "role": user_info.get("role"),
                                "avatar": avatar_data
                            },
                            "_comic": comic_id,
                            "totalComments": top_comment['commentsCount'],
                            "isTop": True,
                            "hide": bool(top_comment['hide']),
                            "created_at": datetime.datetime.utcfromtimestamp(top_comment['created_at']).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                            "likesCount": top_comment['likesCount'],
                            "commentsCount": top_comment['commentsCount'],  #子评论数量
                            "isLiked": db.is_like_comment(user_id, top_comment['id'])
                        }
                        for top_comment in top_comments
                    ]
                }
            }
    
    finally:
        connection.close()

# 发布主评论
def post_comment(comic_id, user_id, contentdata):
    connection = db.get_db_connection()
    content = contentdata["content"]

    try:
        with connection.cursor() as cursor:
            # 查询当前评论数
            query_get_comments_count = """
            SELECT commentsCount FROM comic_info WHERE id = %s
            """
            cursor.execute(query_get_comments_count, (comic_id,))
            initial_comments_count = cursor.fetchone()['commentsCount']

            # 创建新的评论
            comment_id = generate_comment_id()
            current_time = int(time.time())  # 生成UNIX时间戳

            insert_comment_query = """
            INSERT INTO comments (id, comic_id, user_id, content, parent_id, created_at, likesCount, commentsCount, isTop, hide)
            VALUES (%s, %s, %s, %s, NULL, %s, 0, 0, 0, 0)
            """
            cursor.execute(insert_comment_query, (comment_id, comic_id, user_id, content, current_time))

            # 更新comic_info表的commentsCount字段
            update_comments_count_query = """
            UPDATE comic_info SET commentsCount = commentsCount + 1 WHERE id = %s
            """
            cursor.execute(update_comments_count_query, (comic_id,))
            connection.commit()

            # 再次查询评论数，进行计数校验
            cursor.execute(query_get_comments_count, (comic_id,))
            updated_comments_count = cursor.fetchone()['commentsCount']

            # 如果计数没有变化，进行第二次更新
            if updated_comments_count == initial_comments_count:
                cursor.execute(update_comments_count_query, (comic_id,))
                connection.commit()

            return {
                "code": 200,
                "message": "success"
            }

    except pymysql.MySQLError as e:
        # 处理数据库异常
        return {
            "code": 500,
            "message": str(e)
        }

    finally:
        connection.close()

    # return comment_id


# 发布子评论
def post_child_comment(parent_comment_id, user_id, childcontentdata):
    connection = db.get_db_connection()
    content = childcontentdata["content"]

    try:
        with connection.cursor() as cursor:
            # 查询漫画的初始评论计数
            query_comic_count = """
            SELECT comic_info.commentsCount AS comic_comments_count
            FROM comments
            JOIN comic_info ON comments.comic_id = comic_info.id
            WHERE comments.id = %s
            """
            cursor.execute(query_comic_count, (parent_comment_id,))
            comic_count_row = cursor.fetchone()
            initial_comic_comments_count = comic_count_row['comic_comments_count']

            # 查询主评论的初始评论计数
            query_main_comment_count = """
            SELECT comments.commentsCount AS main_comment_comments_count
            FROM comments
            WHERE id = %s
            """
            cursor.execute(query_main_comment_count, (parent_comment_id,))
            main_comment_count_row = cursor.fetchone()
            initial_main_comment_comments_count = main_comment_count_row['main_comment_comments_count']

            # 创建子评论ID
            random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
            child_comment_id = parent_comment_id[:20] + random_suffix

            # 插入子评论数据
            cursor.execute("SELECT comic_id FROM comments WHERE id = %s", (parent_comment_id,))
            comic_id_row = cursor.fetchone()
            comic_id = comic_id_row['comic_id'] if comic_id_row else None

            if comic_id is None:
                return {
                    "code": 500,
                    "message": "Parent comment not found."
                }

            insert_child_comment = """
            INSERT INTO comments (id, comic_id, user_id, content, parent_id, created_at, likesCount, commentsCount, isTop, hide)
            VALUES (%s, %s, %s, %s, %s, %s, 0, 0, 0, 0)
            """
            current_timestamp = int(time.time())
            cursor.execute(insert_child_comment, (child_comment_id, comic_id, user_id, content, parent_comment_id, current_timestamp))

            # 更新 comic_info 的评论计数
            update_comic_count = """
            UPDATE comic_info SET commentsCount = commentsCount + 1 WHERE id = %s
            """
            cursor.execute(update_comic_count, (comic_id,))
            connection.commit()

            # 验证漫画评论计数是否更新
            cursor.execute(query_comic_count, (parent_comment_id,))
            new_comic_count_row = cursor.fetchone()
            if new_comic_count_row['comic_comments_count'] == initial_comic_comments_count:
                cursor.execute(update_comic_count, (comic_id,))
                connection.commit()

            # 更新主评论的评论计数
            update_main_comment_count = """
            UPDATE comments SET commentsCount = commentsCount + 1 WHERE id = %s
            """
            cursor.execute(update_main_comment_count, (parent_comment_id,))
            connection.commit()

            # 验证主评论评论计数是否更新
            cursor.execute(query_main_comment_count, (parent_comment_id,))
            new_main_comment_count_row = cursor.fetchone()
            if new_main_comment_count_row['main_comment_comments_count'] == initial_main_comment_comments_count:
                cursor.execute(update_main_comment_count, (parent_comment_id,))
                connection.commit()

            # 返回成功结果
            return {
                "code": 200,
                "message": "success"
            }

    except pymysql.MySQLError as e:
        # 处理数据库异常
        return {
            "code": 500,
            "message": str(e)
        }

    finally:
        connection.close()

# 加载子评论
def load_child_comments(parent_comment_id, page, user_id):
    connection = db.get_db_connection()

    try:
        with connection.cursor() as cursor:
            # 查询子评论信息，按创建时间排序
            limit = 5
            offset = (page - 1) * limit  # 计算偏移量

            query_child_comments = """
            SELECT * FROM comments 
            WHERE parent_id = %s 
            ORDER BY created_at DESC 
            LIMIT %s OFFSET %s
            """
            cursor.execute(query_child_comments, (parent_comment_id, limit, offset))
            child_comments = cursor.fetchall()

            # 查询对应的用户和是否被点赞
            comments_list = []
            for comment in child_comments:
                # 用户信息
                user_info = db.get_user_info(comment['user_id']) or {}

                # 处理用户头像信息
                avatar_data = {
                    "originalName": user_info.get("avatar").split("/")[-1],
                    "path": "/".join(user_info.get("avatar").split("/")[3:]),
                    "fileServer": PICABRIDGE_URL
                }

                # 检查是否被点赞
                comment_id = comment['id']
                is_liked = db.is_like_comment(user_id, comment_id)

                characters = json.loads(user_info.get("characters", '[]')) if isinstance(user_info.get("characters"), str) else user_info.get("characters", [])

                # 组装评论信息
                comment_info = {
                    "_id": comment['id'],
                    "id": comment['id'],
                    "content": comment['content'],
                    "_parent": parent_comment_id,
                    "_comic": comment['comic_id'],
                    "totalComments": comment['commentsCount'],  # 子评论数量
                    "isTop": bool(comment['isTop']),
                    "hide": bool(comment['hide']),
                    "created_at": datetime.datetime.utcfromtimestamp(comment['created_at']).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                    "likesCount": comment['likesCount'],
                    "isLiked": is_liked,
                    "_user": {
                        "_id": user_info.get("id"),
                        "name": user_info.get("name"),
                        "gender": user_info.get("gender"),
                        "exp": user_info.get("exp"),
                        "level": user_info.get("level"),
                        "role": user_info.get("role"),
                        "verified": bool(user_info.get("verified")),
                        "characters": characters,
                        "title": user_info.get("title"),
                        "avatar": avatar_data,
                        "slogan": user_info.get("description")
                    }
                }
                comments_list.append(comment_info)

            # 计算分页信息
            query_comments_count = """
            SELECT COUNT(*) as total FROM comments WHERE parent_id = %s
            """
            cursor.execute(query_comments_count, (parent_comment_id,))
            total_comments_count = cursor.fetchone()['total']
            total_pages = (total_comments_count + limit - 1) // limit  # 向上取整

            # 构建返回数据
            return {
                "code": 200,
                "message": "success",
                "data": {
                    "comments": {
                        "docs": comments_list,
                        "total": total_comments_count,
                        "limit": limit,
                        "page": str(page),
                        "pages": total_pages
                    }
                }
            }

    except pymysql.MySQLError as e:
        # 处理数据库异常
        return {
            "code": 500,
            "message": str(e)
        }

    finally:
        connection.close()