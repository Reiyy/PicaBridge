import pymysql

from flask import jsonify
from loguru import logger

from lib import db

def switch(user_id, mode):
    try:
        # 验证模式有效性
        ALLOWED_MODES = ['sfw', 'nsfw']
        if mode not in ALLOWED_MODES:
            return jsonify({'error': 'Invalid mode'}), 400

        # 获取数据库连接
        connection = db.get_db_connection()
        with connection.cursor() as cursor:
            # 检查用户是否存在
            sql_check = "SELECT id FROM users WHERE id=%s"
            cursor.execute(sql_check, (user_id,))
            if not cursor.fetchone():
                return jsonify({'error': 'User not found'}), 404

            # 更新模式
            sql_update = "UPDATE users SET mode=%s WHERE id=%s"
            cursor.execute(sql_update, (mode, user_id))
        
        connection.commit()
        return jsonify({
            'message': 'Mode updated successfully',
            'user_id': user_id,
            'new_mode': mode
        }), 200

    except pymysql.MySQLError as e:
        if connection:
            connection.rollback()
        logger.error(f"数据库错误: {e}")
        return jsonify({'error': '服务器内部错误'}), 500
    finally:
        if connection:
            connection.close()

# 查询用户当前模式
def GetMode(user_id):
    connection = db.get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT mode FROM users WHERE id = %s"
            cursor.execute(sql, (user_id,))
            result = cursor.fetchone()
            
            if result:
                return result['mode']
            else:
                return None
    finally:
        connection.close()