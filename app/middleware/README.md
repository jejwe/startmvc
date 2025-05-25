# StartMVC 中间件

中间件是一种在请求处理过程中插入自定义逻辑的机制。它可以在请求到达控制器之前或响应返回客户端之前执行特定的操作。

## 中间件结构

StartMVC 框架支持两种中间件结构：

### 1. 新版中间件（推荐）

新版中间件基于 `before` 和 `after` 方法，分别在请求前和响应后执行：

```python
from startmvc.core.Middleware import Middleware

class MyMiddleware(Middleware):
    """自定义中间件"""
    
    def before(self, request):
        """
        请求前处理
        
        Args:
            request: 请求对象
            
        Returns:
            mixed: 如果返回值不为None，则中断管道并返回该值
        """
        # 在请求前执行的逻辑
        return None
    
    def after(self, request, response):
        """
        请求后处理
        
        Args:
            request: 请求对象
            response: 响应对象
            
        Returns:
            Response: 响应对象
        """
        # 在响应返回前执行的逻辑
        return response
```

### 2. 旧版中间件（兼容）

旧版中间件基于 `handle` 方法，接收请求和下一个中间件的回调函数：

```python
from startmvc.core.Middleware import MiddlewareBase

class MyMiddleware(MiddlewareBase):
    """自定义中间件"""
    
    def handle(self, request, next_callback):
        """
        处理请求
        
        Args:
            request: 请求对象
            next_callback: 下一个中间件
        
        Returns:
            响应结果
        """
        # 在请求前执行的逻辑
        
        # 调用下一个中间件
        response = next_callback()
        
        # 在响应返回前执行的逻辑
        
        return response
```

## 中间件配置

中间件配置在 `config/middleware.py` 文件中：

```python
# 中间件配置
config = {
    # 中间件别名
    'aliases': {
        'auth': 'app.middleware.AuthMiddleware',
        'log': 'app.middleware.LogMiddleware',
    },
    
    # 全局中间件
    'global': [
        'app.middleware.LogMiddleware',
    ],
    
    # 路由中间件
    'route': {
        '/api/*': [
            'app.middleware.ApiMiddleware',
            'app.middleware.CorsMiddleware',
        ],
    },
    
    # 中间件组
    'groups': {
        'web': [
            'app.middleware.CsrfMiddleware',
        ],
        'api': [
            'app.middleware.ApiMiddleware',
        ],
    },
}
```

## 内置中间件

StartMVC 框架内置了以下中间件：

1. **AuthMiddleware**: 认证中间件，用于验证用户是否已登录
2. **LogMiddleware**: 日志中间件，用于记录请求和响应信息
3. **ApiMiddleware**: API中间件，用于处理API请求和响应
4. **CorsMiddleware**: CORS中间件，用于处理跨域资源共享
5. **CsrfMiddleware**: CSRF中间件，用于防止跨站请求伪造

## 自定义中间件

你可以创建自己的中间件来满足特定需求。只需要在 `app/middleware` 目录下创建一个新的中间件类，并在 `config/middleware.py` 中注册即可。

### 示例：限流中间件

```python
from startmvc.core.Middleware import Middleware
import time
import cherrypy

class RateLimitMiddleware(Middleware):
    """限流中间件"""
    
    def __init__(self):
        """构造函数"""
        super().__init__()
        self.requests = {}
        self.limit = 60  # 每分钟最大请求数
        self.window = 60  # 时间窗口（秒）
    
    def before(self, request):
        """请求前处理"""
        # 获取客户端IP
        ip = cherrypy.request.remote.ip
        
        # 获取当前时间
        now = time.time()
        
        # 初始化IP的请求记录
        if ip not in self.requests:
            self.requests[ip] = []
        
        # 清理过期的请求记录
        self.requests[ip] = [t for t in self.requests[ip] if now - t < self.window]
        
        # 检查是否超过限制
        if len(self.requests[ip]) >= self.limit:
            # 返回错误响应
            cherrypy.response.status = 429
            return {
                'error': 'Too Many Requests',
                'message': 'Rate limit exceeded',
                'code': 429
            }
        
        # 记录本次请求
        self.requests[ip].append(now)
        
        # 继续请求
        return None
```