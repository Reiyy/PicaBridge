import os
import pymysql
from loguru import logger

# 读取SQL文件，过滤无关语句，逐条执行
def _execute_sql_file(cursor, filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    for statement in content.split(';'):
        stmt = statement.strip()
        if not stmt:
            continue

        lines = stmt.split('\n')
        meaningful_lines = []
        for line in lines:
            stripped = line.strip()
            if (not stripped or
                stripped.startswith('--') or
                stripped.startswith('/*') or
                stripped.startswith('SET ') or
                stripped.startswith('START TRANSACTION') or
                stripped.startswith('COMMIT') or
                stripped.startswith('/*!')):
                continue
            meaningful_lines.append(stripped)

        clean_stmt = '\n'.join(meaningful_lines).strip()
        if clean_stmt:
            cursor.execute(clean_stmt)

# 检测表是否存在
def _table_exists(cursor, table_name):
    cursor.execute(
        "SELECT COUNT(*) AS cnt FROM information_schema.TABLES "
        "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s",
        (table_name,)
    )
    return cursor.fetchone()['cnt'] > 0


# 检查当前数据库版本
def get_current_version(cursor):
    if not _table_exists(cursor, 'schema_version'):
        return 0 # 表不存在时代表未初始化
    cursor.execute("SELECT MAX(version) AS ver FROM schema_version")
    result = cursor.fetchone()
    return result['ver'] if result and result['ver'] else 0

# 扫描升级文件目录，返回升级文件列表
def _discover_upgrades(upgrade_dir):
    upgrades = []
    if not os.path.isdir(upgrade_dir):
        return upgrades

    for filename in os.listdir(upgrade_dir):
        if not filename.endswith('.sql'):
            continue
        try:
            version = int(filename.split('_')[0])
        except (ValueError, IndexError):
            continue
        upgrades.append((version, os.path.join(upgrade_dir, filename)))

    upgrades.sort(key=lambda x: x[0])
    return upgrades

# 初始化
def run_startup(config):
    db_config = config['db']
    connection = pymysql.connect(
        host=db_config['host'],
        user=db_config['user'],
        password=db_config['password'],
        database=db_config['name'],
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        with connection.cursor() as cursor:
            current_ver = get_current_version(cursor)

            # 如果版本为0，说明数据库未初始化为全新安装，执行初始化主SQL文件
            if current_ver == 0:
                schema_path = os.path.join(
                    os.path.dirname(os.path.dirname(__file__)), 'picabridge.sql'
                )
                logger.info("正在初始化数据库...")
                _execute_sql_file(cursor, schema_path)
                connection.commit()
                logger.info("初始化完成！")
            else:
                logger.debug(f"当前数据库版本: {current_ver}")

            upgrade_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), 'tools', 'upgrade'
            )
            upgrades = _discover_upgrades(upgrade_dir)

            applied_count = 0
            for version, filepath in upgrades:
                if version <= current_ver:
                    continue
                
                logger.info(f"发现数据库更新！")
                filename = os.path.basename(filepath)
                logger.info(f"正在应用升级文件 {filename}...")
                _execute_sql_file(cursor, filepath)

                cursor.execute(
                    "INSERT INTO schema_version (version, description) VALUES (%s, %s)",
                    (version, filename)
                )
                connection.commit()
                applied_count += 1
                logger.info(f"升级脚本文件 {filename} 应用成功。")

            if applied_count > 0:
                logger.info(f"共应用 {applied_count} 个升级文件。")
            elif current_ver > 0:
                logger.debug("数据库已是最新！")

    except Exception as e:
        connection.rollback()
        logger.error(f"数据库升级失败: {e}")
        raise RuntimeError(f"数据库升级失败: {e}") from e
    finally:
        connection.close()
