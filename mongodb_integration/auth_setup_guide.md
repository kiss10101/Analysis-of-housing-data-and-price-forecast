# MongoDB认证设置指南（最安全方案）

## 步骤1：启动现有MongoDB服务
```cmd
net start MongoDB
```

## 步骤2：连接MongoDB并创建用户
在MongoDB Compass或命令行中执行：

### 2.1 创建管理员用户
```javascript
use admin
db.createUser({
  user: "admin",
  pwd: "your_admin_password",  // 请修改为强密码
  roles: [
    { role: "userAdminAnyDatabase", db: "admin" },
    { role: "readWriteAnyDatabase", db: "admin" }
  ]
})
```

### 2.2 创建开发用户
```javascript
use house_data
db.createUser({
  user: "house_dev",
  pwd: "house_dev_password",  // 请修改为您的密码
  roles: [
    { role: "readWrite", db: "house_data" }
  ]
})
```

### 2.3 创建集合
```javascript
db.createCollection('houses')
```

## 步骤3：更新Python配置
修改 `mongodb_integration/mongodb_config.py` 中的连接字符串：
```python
MONGODB_URI = 'mongodb://house_dev:house_dev_password@localhost:27017/house_data'
```

## 步骤4：测试连接
```bash
python mongodb_integration/mongodb_config.py
```

这种方式最安全，适合生产环境。
