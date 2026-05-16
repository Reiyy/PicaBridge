from loguru import logger
from lib.db import get_db_connection


# 获取仪表盘状态信息
def get_dashboard_status(user_id):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # 获取漫画总数
            cursor.execute("SELECT COUNT(*) as comic_count FROM comic_info")
            comic_count = cursor.fetchone()["comic_count"]

            # 获取当前用户昵称
            cursor.execute("SELECT name FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            user_name = user["name"] if user else "未知用户"

            return {
                "code": 200,
                "message": "success",
                "data": {
                    "comic_count": comic_count,
                    "user_name": user_name,
                },
            }, 200
    except Exception as e:
        logger.error("获取状态信息失败: {e}".format(e=e))
        return {"code": 500, "message": "获取状态信息失败"}, 500
    finally:
        connection.close()
