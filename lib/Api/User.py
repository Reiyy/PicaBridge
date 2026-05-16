import json
import bcrypt
from loguru import logger
from lib.db import get_db_connection


# 获取用户列表
def get_users(page=1, page_size=20, search=None):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            offset = (page - 1) * page_size

            where_clause = ""
            params = []
            if search:
                where_clause = "WHERE name LIKE %s OR email LIKE %s"
                keyword = f"%{search}%"
                params = [keyword, keyword]

            # 总数
            count_sql = f"SELECT COUNT(*) as total FROM users {where_clause}"
            cursor.execute(count_sql, params)
            total = cursor.fetchone()["total"]

            # 分页查询
            query_sql = f"""
                SELECT id, name, title, characters, level, exp, createdate
                FROM users {where_clause}
                ORDER BY createdate DESC
                LIMIT %s OFFSET %s
            """
            cursor.execute(query_sql, params + [page_size, offset])
            users = cursor.fetchall()

            for user in users:
                for field in ["characters"]:
                    val = user.get(field)
                    if val and isinstance(val, str):
                        try:
                            user[field] = json.loads(val)
                        except (json.JSONDecodeError, TypeError):
                            pass
                if user.get("createdate"):
                    user["createdate"] = str(user["createdate"])

            return {
                "code": 200,
                "message": "success",
                "data": {
                    "users": users,
                    "total": total,
                    "page": page,
                    "page_size": page_size,
                },
            }, 200
    except Exception as e:
        logger.error("获取用户列表失败: {e}".format(e=e))
        return {"code": 500, "message": "获取用户列表失败"}, 500
    finally:
        connection.close()


# 获取单个用户详情
def get_user(user_id):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute(
                """SELECT id, email, name, birthday, gender, createdate,
                          title, description, avatar, exp, level, role,
                          characters, mode,
                          question1, question2, question3
                   FROM users WHERE id = %s""",
                (user_id,),
            )
            user = cursor.fetchone()

            if not user:
                return {"code": 404, "message": "用户不存在"}, 404

            for field in ["characters"]:
                val = user.get(field)
                if val and isinstance(val, str):
                    try:
                        user[field] = json.loads(val)
                    except (json.JSONDecodeError, TypeError):
                        pass
            if user.get("createdate"):
                user["createdate"] = str(user["createdate"])
            if user.get("birthday"):
                user["birthday"] = str(user["birthday"])

            return {"code": 200, "message": "success", "data": user}, 200
    except Exception as e:
        logger.error("获取用户详情失败: {e}".format(e=e))
        return {"code": 500, "message": "获取用户详情失败"}, 500
    finally:
        connection.close()


# 允许修改的字段
UPDATABLE_FIELDS = {
    "name", "email", "birthday", "gender", "title", "description",
    "avatar", "level", "exp", "role", "characters", "mode",
    "question1", "question2", "question3",
}


# 更新用户信息
def update_user(user_id, data):
    if not data:
        return {"code": 400, "message": "请求数据为空"}, 400

    fields = {k: v for k, v in data.items() if k in UPDATABLE_FIELDS}
    password = data.get("password")
    answer1 = data.get("answer1")
    answer2 = data.get("answer2")
    answer3 = data.get("answer3")

    if not fields and not password and not any([answer1, answer2, answer3]):
        return {"code": 400, "message": "没有可更新的字段"}, 400

    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # 检查用户是否存在
            cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
            if not cursor.fetchone():
                return {"code": 404, "message": "用户不存在"}, 404

            # 检查name/email唯一性
            if "name" in fields:
                cursor.execute("SELECT id FROM users WHERE name = %s AND id != %s", (fields["name"], user_id))
                if cursor.fetchone():
                    return {"code": 400, "message": "名称已被占用"}, 400
            if "email" in fields:
                cursor.execute("SELECT id FROM users WHERE email = %s AND id != %s", (fields["email"], user_id))
                if cursor.fetchone():
                    return {"code": 400, "message": "邮箱已被占用"}, 400

            set_parts = []
            params = []
            for key, value in fields.items():
                if key == "characters" and isinstance(value, list):
                    set_parts.append(f"`{key}` = %s")
                    params.append(json.dumps(value, ensure_ascii=False))
                else:
                    set_parts.append(f"`{key}` = %s")
                    params.append(value)

            # 密码：留空不变，填写使用哈希保存
            if password:
                salt = bcrypt.gensalt()
                hashed = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")
                set_parts.append("`password` = %s")
                params.append(hashed)

            # 密保答案：留空不变，填写使用哈希保存
            for i, answer in enumerate([answer1, answer2, answer3], 1):
                if answer:
                    salt = bcrypt.gensalt()
                    hashed = bcrypt.hashpw(answer.encode("utf-8"), salt).decode("utf-8")
                    set_parts.append(f"`answer{i}` = %s")
                    params.append(hashed)

            if not set_parts:
                return {"code": 400, "message": "没有可更新的字段"}, 400

            sql = f"UPDATE users SET {', '.join(set_parts)} WHERE id = %s"
            params.append(user_id)
            cursor.execute(sql, params)
            connection.commit()

            return {"code": 200, "message": "success", "data": {"message": "用户信息已更新"}}, 200
    except Exception as e:
        logger.error("更新用户信息失败: {e}".format(e=e))
        return {"code": 500, "message": "更新用户信息失败"}, 500
    finally:
        connection.close()

# 删除用户
def delete_user(user_id):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
            if not cursor.fetchone():
                return {"code": 404, "message": "用户不存在"}, 404

            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            connection.commit()

            return {"code": 200, "message": "success", "data": {"message": "用户已删除"}}, 200
    except Exception as e:
        logger.error("删除用户失败: {e}".format(e=e))
        return {"code": 500, "message": "删除用户失败"}, 500
    finally:
        connection.close()
