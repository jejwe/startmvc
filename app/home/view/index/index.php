<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{$title}</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            color: #333;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f9f9f9;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }
        .info {
            background-color: #e8f4f8;
            padding: 15px;
            border-radius: 5px;
            margin-top: 20px;
        }
        .data {
            background-color: #f0f7e6;
            padding: 15px;
            border-radius: 5px;
            margin-top: 20px;
        }
        pre {
            background-color: #f5f5f5;
            padding: 10px;
            border-radius: 3px;
            overflow-x: auto;
        }
        footer {
            margin-top: 30px;
            text-align: center;
            font-size: 0.9em;
            color: #777;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>{$title}</h1>
        
        <div class="info">
            <h2>欢迎使用 StartMVC Python 框架</h2>
            <p>这是一个基于 CherryPy 实现的轻量级 MVC 框架，保持了与 PHP 版本 StartMVC 相同的目录结构和使用方式。</p>
        </div>
        
        <div class="data">
            <h2>测试数据</h2>
            <pre>
ID: {$data.id}
名称: {$data.name}
描述: {$data.description}
            </pre>
        </div>
        
        <footer>
            &copy; 2025 StartMVC Python Framework - 版本 2.3.7
        </footer>
    </div>
</body>
</html>