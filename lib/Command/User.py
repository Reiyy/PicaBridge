import json

from lib import db

# 允许调用该命令的用户组
allow_groups = ["official"]

def run(comic_id, user_id, command_args):
    # 检测用户权限
    user_groups = db.get_user_characters(user_id)
    if not set(user_groups) & set(allow_groups):
        return {"status": False, "data": "你当前无权执行此命令！"}
        
    # 判断 comic_id 是否为指定值
    if comic_id != "5822a6e3ad7ede654696e482":
        return {"status": False, "data": "该命令为全局命令，只能在留言板中运行！"}

    if not command_args or len(command_args) < 1:
        return {"status": False, "data": "缺少子命令"}

    # 提取子命令标识
    subcommand_parts = command_args.split(" ", 1)
    subcommand = subcommand_parts[0]
    subcommand_args = subcommand_parts[1] if len(subcommand_parts) > 1 else ""

    # 子命令别名映射
    subcommand_map = {
        "email": UserEmail,
        "账号": UserEmail,
        "name": UserName,
        "昵称": UserName,
        "role": UpdateUserRoles,
        "权限组": UpdateUserRoles,
        "删除": DeleteUser,
        "del": DeleteUser,
        "title": UserTitle,
        "称号": UserTitle,
    }

    # 检查命令是否存在
    subcommand_function = subcommand_map.get(subcommand)
    if not subcommand_function:
        return {"status": False, "data": f"未知子命令：{subcommand}"}
    
    return subcommand_function(comic_id, user_id, subcommand_args)

# 修改账号名
def UserEmail(comic_id, user_id, subcommand_args):
    # 解析命令参数
    args = subcommand_args.split()

    # 连接数据库
    connection = db.get_db_connection()
    cursor = connection.cursor()
    
    if len(args) == 2:
        target_useremail, new_email = args
        
        # 查询 useremail 对应的 user_id
        cursor.execute("SELECT id FROM users WHERE email = %s", (target_useremail,))
        user = cursor.fetchone()
        
        if not user:
            cursor.close()
            connection.close()
            return {"status": False, "data": f"未找到用户：{target_useremail}"}
        
        user_id = user["id"]  # 有额外传入用户名参数，以查询的user_id作为目标用户
    elif len(args) == 1:
        new_email = args[0]  # 没有额外传入用户名，已当前登录user_id作为目标用户
    else:
        return {"status": False, "data": f"未知的参数：{args}"}
    
    # 执行更新操作
    cursor.execute("UPDATE users SET email = %s WHERE id = %s", (new_email, user_id))
    connection.commit()
    
    cursor.close()
    connection.close()
    
    return {"status": True, "data": f"账号已改为：{new_email}"}

# 修改用户昵称
def UserName(comic_id, user_id, subcommand_args):
    # 解析命令参数
    args = subcommand_args.split()

    # 连接数据库
    connection = db.get_db_connection()
    cursor = connection.cursor()
    
    if len(args) == 2:
        target_useremail, new_name = args
        
        # 查询 useremail 对应的 user_id
        cursor.execute("SELECT id FROM users WHERE email = %s", (target_useremail,))
        user = cursor.fetchone()
        
        if not user:
            cursor.close()
            connection.close()
            return {"status": False, "data": f"未找到用户：{target_useremail}"}
        
        user_id = user["id"]  # 有额外传入用户名参数，以查询的user_id作为目标用户
    elif len(args) == 1:
        new_name = args[0]  # 没有额外传入用户名，已当前登录user_id作为目标用户
    else:
        return {"status": False, "data": f"未知的参数：{args}"}
    
    # 执行更新操作
    cursor.execute("UPDATE users SET name = %s WHERE id = %s", (new_name, user_id))
    connection.commit()
    
    cursor.close()
    connection.close()
    
    return {"status": True, "data": f"昵称已改为：{new_name}"}

# 更新权限组
def UpdateUserRoles(comic_id, user_id, subcommand_args):
    # 解析命令参数
    args = subcommand_args.split()

    # 连接数据库
    connection = db.get_db_connection()
    cursor = connection.cursor()
    
    if len(args) == 2:
        target_useremail, roles_str = args
        
        # 查询 useremail 对应的 user_id
        cursor.execute("SELECT id FROM users WHERE email = %s", (target_useremail,))
        user = cursor.fetchone()
        
        if not user:
            cursor.close()
            connection.close()
            return {"status": False, "data": f"未找到用户：{target_useremail}"}
        
        user_id = user["id"]  # 有额外传入用户名参数，以查询的user_id作为目标用户
    elif len(args) == 1:
        roles_str = args[0]  # 没有额外传入用户名，已当前登录user_id作为目标用户
    else:
        return {"status": False, "data": f"未知的参数：{args}"}
    
    # 解析权限组列表
    if roles_str == "0":
        roles = []  # 传入参数为0，移除所有权限组
    else:
        valid_roles = {"knight", "official"}  # 合法权限组
        roles = set(roles_str.split(","))
        
        if not roles.issubset(valid_roles):
            return {"status": False, "data": f"传入权限组不合法：{roles}"}

    # 更新
    roles_json = json.dumps(list(roles))
    cursor.execute("UPDATE users SET characters = %s WHERE id = %s", (roles_json, user_id))
    connection.commit()
    
    cursor.close()
    connection.close()
    
    if roles_str == "0":
        return {"status": True, "data": f"已移除所有权限！"}

    return {"status": True, "data": f"权限组已改为：{roles_str}"}

# 删除用户
def DeleteUser(comic_id, user_id, subcommand_args):
    # 解析命令参数，获取要删除的用户 email
    target_useremail = subcommand_args.strip()
    
    # 连接数据库
    connection = db.get_db_connection()
    cursor = connection.cursor()
    
    # 查询 useremail 对应的 user_id
    cursor.execute("SELECT id FROM users WHERE email = %s", (target_useremail,))
    user = cursor.fetchone()
    
    if not user:
        cursor.close()
        connection.close()
        return {"status": False, "data": f"未找到用户：{target_useremail}"}
    
    user_id = user["id"]
    
    # 删除用户
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    connection.commit()
    
    cursor.close()
    connection.close()
    
    return {"status": True, "data": f"已删除用户：{target_useremail}"}

# 修改用户称号
def UserTitle(comic_id, user_id, subcommand_args):
    # 解析命令参数
    args = subcommand_args.split()

    # 连接数据库
    connection = db.get_db_connection()
    cursor = connection.cursor()
    
    if len(args) == 2:
        target_useremail, new_title = args
        
        # 查询 useremail 对应的 user_id
        cursor.execute("SELECT id FROM users WHERE email = %s", (target_useremail,))
        user = cursor.fetchone()
        
        if not user:
            cursor.close()
            connection.close()
            return {"status": False, "data": f"未找到用户：{target_useremail}"}
        
        user_id = user["id"]  # 有额外传入用户名参数，以查询的user_id作为目标用户
    elif len(args) == 1:
        new_title = args[0]  # 没有额外传入用户名，已当前登录user_id作为目标用户
    else:
        return {"status": False, "data": f"未知的参数：{args}"}
    
    # 执行更新操作
    cursor.execute("UPDATE users SET title = %s WHERE id = %s", (new_title, user_id))
    connection.commit()
    
    cursor.close()
    connection.close()
    
    return {"status": True, "data": f"称号已改为：{new_title}"}