import pymysql
import json
import sys
import subprocess

# 读取配置文件
def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

config = load_config()

# 获取数据库连接信息
def get_db_connection():
    db_config = config['db']
    
    connection = pymysql.connect(
        host=db_config['host'],
        user=db_config['user'],
        password=db_config['password'],
        database=db_config['name'],
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection

# 初始化数据库
def init_database():
    sql_file = "picabridge.sql"
    connection = get_db_connection()
    
    try:
        with connection.cursor() as cursor:
            with open(sql_file, "r", encoding="utf-8") as f:
                sql_script = f.read()
            
            # 分割 SQL 语句并逐条执行
            for statement in sql_script.split(";"):
                if statement.strip():  # 避免执行空语句
                    cursor.execute(statement)
        
        connection.commit()
        print("数据库初始化完成！")
    
    except Exception as e:
        connection.rollback()  # 发生错误时回滚
        raise RuntimeError(f"数据库初始化失败: {e}")  # 抛出异常
    
    finally:
        connection.close()

# 检查数据库是否已初始化
def is_database_initialized():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT COUNT(*) AS count FROM comic_info WHERE id = %s"
            cursor.execute(sql, ('5822a6e3ad7ede654696e482',))
            result = cursor.fetchone()
            return result["count"] > 0  # 存在该记录则返回 True，否则返回 False
    except:
        return False
    finally:
        connection.close()

def main():
    print("当前版本 Beta 0.7.5-250310")
    print("开始初始化...")
    print("正在检测数据库是否已初始化...")
    if is_database_initialized():
        print("数据库已初始化！")
    else:
        print("数据库未初始化！")
        print("开始初始化数据库...")
        try:
            init_database()
        except Exception as e:
            print("发生错误:", e)
            sys.exit(1)
    
    print("初始化完成！")
    print("正在启动 哔咔桥PicaBridge ！")
    listen_address = config.get("Listen", "0.0.0.0:7777")  # 读取 Listen 配置，默认 0.0.0.0:7777
    subprocess.run(["gunicorn", "-w", "4", "-k", "gevent", "-b", listen_address, "PicaBridge:PicaBridge"])

if __name__ == "__main__":
    main()