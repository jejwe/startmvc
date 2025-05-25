# StartMVC Python Framework

StartMVC Python 是一个基于 CherryPy 的轻量级 MVC 框架，它保持了与 PHP 版本 StartMVC 相同的目录结构和代码组织方式，同时利用 Python 的特性提供了更加灵活和强大的功能。

## 特性

- **轻量级**: 核心代码简洁，易于理解和扩展
- **MVC 架构**: 清晰的模型-视图-控制器分离
- **路由系统**: 灵活的路由配置，支持正则表达式和参数化路由
- **中间件**: 强大的中间件系统，支持全局、路由和分组中间件
- **模板引擎**: 集成 Jinja2 模板引擎，支持布局和片段
- **数据库支持**: 内置多种数据库支持，包括 SQLite、MySQL 和 PostgreSQL
- **会话管理**: 安全的会话管理，支持文件和内存存储
- **缓存系统**: 支持文件缓存、内存缓存、Redis缓存等
- **安全特性**: 内置 CSRF 保护、XSS 过滤和 SQL 注入防护
- **API 支持**: 内置 API 支持，轻松构建 RESTful API
- **错误处理**: 全面的错误处理和调试信息
- **事件系统**: 支持事件触发与监听
- **依赖注入**: 支持容器和依赖注入
- **HTTP客户端**: 内置HTTP请求客户端
- **文件上传**: 简单易用的文件上传处理
- **验证器**: 强大的数据验证功能
- **分页系统**: 简单易用的数据分页功能

## 目录结构

```
python_startmvc/
├── app/                    # 应用目录
│   ├── admin/              # 管理员模块
│   │   ├── controller/     # 控制器
│   │   ├── model/          # 模型
│   │   └── view/           # 视图
│   ├── api/                # API模块
│   │   ├── controller/     # 控制器
│   │   └── model/          # 模型
│   ├── home/               # 前台模块
│   │   ├── controller/     # 控制器
│   │   ├── model/          # 模型
│   │   └── view/           # 视图
│   └── middleware/         # 中间件
├── config/                 # 配置目录
│   ├── cache.py            # 缓存配置
│   ├── common.py           # 公共配置
│   ├── database.py         # 数据库配置
│   ├── middleware.py       # 中间件配置
│   ├── pagination.py       # 分页配置
│   └── route.py            # 路由配置
├── runtime/                # 运行时目录
│   ├── cache/              # 缓存目录
│   ├── db/                 # 数据库文件
│   ├── log/                # 日志目录
│   ├── session/            # 会话目录
│   └── temp/               # 临时文件目录
├── startmvc/               # 框架核心
│   ├── core/               # 核心组件
│   │   ├── App.py          # 应用类
│   │   ├── Cache.py        # 缓存类
│   │   ├── Config.py       # 配置类
│   │   ├── Container.py    # 容器类
│   │   ├── Controller.py   # 控制器基类
│   │   ├── Cookie.py       # Cookie类
│   │   ├── Csrf.py         # CSRF类
│   │   ├── Event.py        # 事件类
│   │   ├── Exception.py    # 异常处理
│   │   ├── Http.py         # HTTP客户端类
│   │   ├── Loader.py       # 加载器
│   │   ├── Logger.py       # 日志类
│   │   ├── Middleware.py   # 中间件基类
│   │   ├── Model.py        # 模型基类
│   │   ├── Pagination.py   # 分页类
│   │   ├── Request.py      # 请求处理
│   │   ├── Response.py     # 响应类
│   │   ├── Router.py       # 路由处理
│   │   ├── Session.py      # 会话类
│   │   ├── Upload.py       # 上传类
│   │   ├── Validator.py    # 验证器类
│   │   └── View.py         # 视图处理
│   ├── autoload.py         # 自动加载
│   └── function.py         # 全局函数
├── static/                 # 静态资源
│   ├── css/                # CSS文件
│   ├── images/             # 图片文件
│   ├── js/                 # JavaScript文件
│   └── uploads/            # 上传文件目录
├── boot.py                 # 启动文件
├── requirements.txt        # 依赖文件
└── server.py               # 服务器启动脚本
```

## 安装

1. 克隆仓库:

```bash
git clone https://github.com/yourusername/python_startmvc.git
cd python_startmvc
```

2. 安装依赖:

```bash
pip install -r requirements.txt
```

3. 运行服务器:

```bash
python server.py
```

默认情况下，服务器将在 http://localhost:12000 上运行。

## 快速入门

### 创建控制器

在 `app/home/controller` 目录下创建一个新的控制器:

```python
from startmvc.core.Controller import Controller

class Hello(Controller):
    """Hello控制器"""
    
    def index(self):
        """首页方法"""
        # 渲染视图并传递变量
        return self.view('hello/index', {
            'title': 'Hello',
            'message': 'Hello, World!'
        })
```

### 创建视图

在 `app/home/view/hello` 目录下创建一个 `index.html` 文件:

```html
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
</head>
<body>
    <h1>{{ message }}</h1>
</body>
</html>
```

### 配置路由

在 `config/route.py` 中添加路由:

```python
# 路由配置
config = {
    # 路由规则
    'routes': [
        # ... 其他路由 ...
        
        # Hello路由
        {
            'pattern': 'hello',
            'target': 'home/Hello/index',
        },
    ],
}
```

### 创建模型

在 `app/home/model` 目录下创建一个新的模型:

```python
from startmvc.core.Model import Model

class UserModel(Model):
    """用户模型"""
    
    def __init__(self):
        """构造函数"""
        super().__init__()
        self.table = 'user'  # 表名
    
    def getUser(self, user_id):
        """获取用户信息"""
        return self.where('id', user_id).find()
    
    def getUsers(self, limit=10):
        """获取用户列表"""
        return self.limit(limit).select()
```

### 创建中间件

在 `app/middleware` 目录下创建一个新的中间件:

```python
from startmvc.core.Middleware import Middleware
import cherrypy

class AuthMiddleware(Middleware):
    """认证中间件"""
    
    def before(self, request):
        """请求前处理"""
        # 检查用户是否已登录
        if 'user_id' not in cherrypy.session:
            # 保存当前URL
            cherrypy.session['redirect_url'] = cherrypy.request.path_info
            
            # 重定向到登录页面
            raise cherrypy.HTTPRedirect('/login')
        
        return None
```

## 高级功能

### 数据库查询

StartMVC 提供了一个简单而强大的数据库查询构建器:

```python
# 获取单条记录
user = self.db.table('users').where('id', 1).find()

# 获取多条记录
users = self.db.table('users').where('status', 1).limit(10).get()

# 插入记录
user_id = self.db.table('users').insert({
    'username': 'john',
    'email': 'john@example.com',
    'password': 'hashed_password',
})

# 更新记录
affected = self.db.table('users').where('id', 1).update({
    'email': 'new_email@example.com',
})

# 删除记录
affected = self.db.table('users').where('id', 1).delete()

# 复杂查询
users = self.db.table('users').where('status', 1).where('role', 'admin').order_by('created_at', 'DESC').limit(10).get()

# 事务支持
with self.db.transaction():
    self.db.table('users').insert({'name': 'User 1'})
    self.db.table('users').insert({'name': 'User 2'})
```

### 视图渲染

StartMVC 支持多种视图渲染方式:

```python
# 渲染指定视图并传递变量
return self.view('user/profile', {
    'title': '用户资料',
    'user': user
})

# 渲染JSON响应
return self.json({
    'code': 0, 
    'message': 'Success', 
    'data': user
})

# 重定向
return self.redirect('/login')

# 返回文件下载
return self.download('/path/to/file.pdf', 'custom_filename.pdf')
```

### 中间件

StartMVC 支持多种中间件类型:

```python
# 全局中间件
class LogMiddleware(Middleware):
    def before(self, request):
        # 记录请求信息
        return None
    
    def after(self, request, response):
        # 记录响应信息
        return response

# 路由中间件
class AuthMiddleware(Middleware):
    def before(self, request):
        # 检查用户是否已登录
        if 'user_id' not in cherrypy.session:
            raise cherrypy.HTTPRedirect('/login')
        return None
```

### 缓存系统

StartMVC 提供了多种缓存驱动:

```python
# 设置缓存
self.cache.set('key', 'value', 3600)  # 缓存1小时

# 获取缓存
value = self.cache.get('key')

# 删除缓存
self.cache.delete('key')

# 清空缓存
self.cache.clear()
```

### 事件系统

StartMVC 提供了事件系统，用于解耦应用组件:

```python
from startmvc.core.Event import listen, trigger

# 注册事件监听器
listen('user.created', send_welcome_email, 10)

# 触发事件
trigger('user.created', user_data)
```

### 文件上传

StartMVC 提供了文件上传功能:

```python
# 上传文件
file = self.request.files.get('file')
if file:
    result = self.upload.save(file, 'images')
    if result['success']:
        file_path = result['path']
```

### 分页系统

StartMVC 提供了简单易用的分页功能:

```python
from startmvc.core.Pagination import Pagination

# 创建分页实例
per_page = 10
pagination = Pagination.paginate(data, per_page, page)

# 在视图中使用分页数据
return self.view('list', {
    'items': pagination.items,
    'pagination': pagination,
    'current_page': pagination.current_page,
    'per_page': per_page,
    'total': pagination.total,
})
```

## 示例

框架提供了多个示例，展示了框架的各种功能:

- 数据库示例: CRUD操作、事务等
- 分页示例: 标准分页、自定义分页、简单分页
- 事件系统示例: 事件监听器、触发器和管理

## 许可证

StartMVC 遵循 Apache2 开源协议发布，需保留开发者信息。