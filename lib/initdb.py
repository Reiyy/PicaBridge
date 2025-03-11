from lib.db import get_db_connection

def initialize_database():
    # 获取数据库连接
    connection = get_db_connection()

    cursor = connection.cursor()

    # 创建 users 表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id VARCHAR(24) PRIMARY KEY,  -- 新增随机 ID
        email VARCHAR(255) UNIQUE NOT NULL,
        name VARCHAR(255) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        birthday DATE NOT NULL,
        gender ENUM('m', 'f', 'bot') NOT NULL,
        question1 VARCHAR(255),
        answer1 VARCHAR(255),
        question2 VARCHAR(255),
        answer2 VARCHAR(255),
        question3 VARCHAR(255),
        answer3 VARCHAR(255),
        createdate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 新增创建日期
        title VARCHAR(255) DEFAULT '萌新',  -- 新增称号
        description TEXT DEFAULT '还没有写哦~',  -- 新增个人简介
        exp INT DEFAULT 0,  -- 新增经验值
        level INT DEFAULT 1,  -- 新增等级
        role VARCHAR(255) DEFAULT '',  -- 新增角色
        avatar VARCHAR(255) DEFAULT '',  -- 新增头像
        verified BOOLEAN DEFAULT FALSE,  -- 新增是否已验证
        characters JSON DEFAULT '[]',  -- 新增用户组
        favourite JSON DEFAULT '[]',  -- 新增收藏的漫画
        `like` JSON DEFAULT '[]'  -- 新增点赞的漫画
    );
    """)

    # 创建 comic_info 表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS comic_info (
        id VARCHAR(255) PRIMARY KEY,
        creator VARCHAR(255),
        title VARCHAR(255),
        description TEXT,
        author VARCHAR(255),
        chineseTeam VARCHAR(255),
        categories JSON,
        tags JSON,
        pagesCount INT,
        epsCount INT,
        finished BOOLEAN,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        allowDownload BOOLEAN DEFAULT FALSE,
        allowComment BOOLEAN DEFAULT FALSE,
        viewsCount INT DEFAULT 0,
        likesCount INT DEFAULT 0,
        commentsCount INT DEFAULT 0
    );
    """)

    # 执行 SQL 创建表
    connection.commit()
    cursor.close()
    connection.close()

    print("基础数据表已创建。")
