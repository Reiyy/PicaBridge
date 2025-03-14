from lib import db

def run(comic_id, user_id, command_args):
    # 判断 comic_id 是否为指定值
    if comic_id != "5822a6e3ad7ede654696e482":
        return {"status": False, "data": "该命令为全局命令，只能在留言板中运行！"}

    connection = db.get_db_connection()
    
    try:
        with connection.cursor() as cursor:
            sql = "UPDATE users SET mode = %s WHERE id = %s"
            cursor.execute(sql, (command_args, user_id))
        
        connection.commit()
        # 成功返回信息
        return {"status": True, "data": f"切换成功！\n当前模式为“{command_args.upper()}”\n注：重启APP后生效！启动图将在第二次启动时生效！"}
    except Exception as e:
        connection.rollback()
        return {"status": False, "data": "模式切换失败！"}
    finally:
        connection.close()