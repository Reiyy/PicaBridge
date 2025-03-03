from lib.db import db

def run(comic_id, user_id, command_args):
    connection = db.get_db_connection()
    
    try:
        with connection.cursor() as cursor:
            sql = "UPDATE users SET mode = %s WHERE id = %s"
            cursor.execute(sql, (command_args, user_id))
        
        connection.commit()
        # 成功返回信息
        return {"status": True, "data": f"切换成功！\n当前模式为“{command_args.upper()}”\n注：重启APP后生效！"}
    except Exception as e:
        connection.rollback()
        return {"status": False, "data": "模式切换失败！"}
    finally:
        connection.close()