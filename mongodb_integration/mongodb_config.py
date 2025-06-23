# MongoDB连接配置
# 房源数据分析系统

# 配置选项1：无认证连接（开发环境）
MONGODB_URI_NO_AUTH = 'mongodb://localhost:27017/'

# 配置选项2：认证连接（生产环境）
MONGODB_URI_WITH_AUTH = 'mongodb://house_user:house_password@localhost:27017/house_data'

# 配置选项3：管理员连接
MONGODB_URI_ADMIN = 'mongodb://admin:admin123@localhost:27017/house_data?authSource=admin'

# 默认配置（请根据您的环境选择）
# 尝试多种连接方式
MONGODB_URI = MONGODB_URI_NO_AUTH  # 使用无认证连接

# 数据库名称
MONGODB_DATABASE = 'house_data'

# 集合名称
MONGODB_COLLECTION = 'houses'

# 连接选项
MONGODB_OPTIONS = {
    'serverSelectionTimeoutMS': 5000,  # 5秒超时
    'connectTimeoutMS': 10000,         # 10秒连接超时
    'socketTimeoutMS': 30000,          # 30秒socket超时
}

def get_mongodb_client():
    """获取MongoDB客户端"""
    import pymongo
    return pymongo.MongoClient(MONGODB_URI, **MONGODB_OPTIONS)

def get_database():
    """获取数据库"""
    client = get_mongodb_client()
    return client[MONGODB_DATABASE]

def get_collection():
    """获取集合"""
    db = get_database()
    return db[MONGODB_COLLECTION]

def test_connection():
    """测试连接"""
    try:
        client = get_mongodb_client()
        client.admin.command('ping')
        print("✅ MongoDB连接成功")

        db = get_database()
        collection = get_collection()
        count = collection.count_documents({})
        print(f"✅ 数据库访问成功，文档数: {count}")

        client.close()
        return True
    except Exception as e:
        print(f"❌ MongoDB连接失败: {e}")
        return False

def setup_mongoengine():
    """设置MongoEngine连接"""
    import mongoengine

    try:
        # 断开现有连接
        mongoengine.disconnect()

        # 建立新连接
        mongoengine.connect(
            db=MONGODB_DATABASE,
            host='127.0.0.1',
            port=27017,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
            socketTimeoutMS=30000
        )

        print("✅ MongoEngine连接成功")
        return True

    except Exception as e:
        print(f"❌ MongoEngine连接失败: {e}")
        return False

if __name__ == '__main__':
    print("MongoDB配置测试")
    test_connection()
