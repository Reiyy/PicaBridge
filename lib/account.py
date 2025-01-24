import json, random, string
from flask import jsonify
from datetime import datetime
import lib.db as db


# 生成24位随机用户id
def generate_random_id():
    letters = ''.join(random.choices(string.ascii_lowercase, k=12))  # 生成12个小写字母
    digits = ''.join(random.choices(string.digits, k=12))  # 生成12个数字
    random_id = ''.join(random.sample(letters + digits, 24))  # 混合并随机打乱
    return random_id

# 注册
def Register(data):
    email = data.get('email')
    name = data.get('name')
    password = data.get('password')
    birthday = data.get('birthday')
    gender = data.get('gender')
    question1 = data.get('question1')
    answer1 = data.get('answer1')
    question2 = data.get('question2')
    answer2 = data.get('answer2')
    question3 = data.get('question3')
    answer3 = data.get('answer3')

    # 检查必填字段
    if not all([email, name, password, birthday, gender]):
        return jsonify({"code": 400, "message": "Missing required fields"}), 400

    # 连接数据库
    connection = db.get_db_connection()
    cursor = connection.cursor()

    # 检查用户名是否已存在
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    if cursor.fetchone():
        cursor.close()
        connection.close()
        return jsonify({"code": 400, "error": "1008", "message": "email is already exist"}), 400

    # 检查昵称是否已存在
    cursor.execute("SELECT * FROM users WHERE name = %s", (name,))
    if cursor.fetchone():
        cursor.close()
        connection.close()
        return jsonify({"code": 400, "error": "1009", "message": "name is already exist"}), 400

    # 生成随机ID
    user_id = generate_random_id()

    # 写入用户信息至数据库
    cursor.execute("""
        INSERT INTO users (id, email, name, password, birthday, gender, 
                           question1, answer1, question2, answer2, question3, answer3, 
                           createdate, title, description, exp, level, role, avatar, 
                           verified, characters, favourite, `like`) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                %s, %s, %s, %s)
    """, (user_id, email, name, password, birthday, gender, 
          question1, answer1, question2, answer2, question3, answer3,
          datetime.now(), "萌新", "还没有写哦~", 0, 1, "", "", 
          False, json.dumps([]), json.dumps({}), json.dumps([])))

    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({"code": 200, "message": "success"}), 200

# 登录
def SignIn(data):
    email = data.get('email')
    password = data.get('password')

    # 检查必填字段
    if not all([email, password]):
        return jsonify({"code": 400, "message": "Missing required fields"}), 400

    # 连接数据库
    connection = db.get_db_connection()
    cursor = connection.cursor()

    # 检查用户名和密码是否匹配
    cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
    user = cursor.fetchone()

    if user is None:
        cursor.close()
        connection.close()
        return jsonify({"code": 400, "error": "1004", "message": "invalid email or password", "detail": ":("}), 400

    # 登录成功，生成一个随机 token
    # token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    # 由于漫画收藏，点赞等功能需要跟随用户，故弃用无意义的随机码

    # 登录成功，返回用户ID作为Token
    user_id = db.get_user_id(email)
    token = str(user_id)
    
    cursor.close()
    connection.close()

# 返回登录信息
    return jsonify({
        "code": 200,
        "message": "success",
        "data": {
            "token": token
        }
    }), 200    
