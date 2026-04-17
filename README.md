# 人员信息管理系统

一个基于 FastAPI 构建的人员信息管理系统，提供学生、教师、班级、成绩、就业信息的管理和统计分析功能。

## 项目简介

本系统是一个完整的 Web 应用程序，采用前后端分离架构，后端使用 FastAPI 框架，提供 RESTful API 接口。系统主要功能模块包括：
- 学生信息管理
- 教师信息管理
- 班级信息管理
- 成绩管理
- 学生就业管理
- 统计分析

## 技术栈

- **后端框架**: FastAPI 0.135.3
- **Web 服务器**: Uvicorn 0.44.0
- **数据库**: MySQL (通过 PyMySQL 1.1.0)
- **ORM**: SQLAlchemy 2.0.49
- **数据验证**: Pydantic 2.12.5
- **配置管理**: Pydantic Settings 2.13.1
- **日志管理**: Loguru 0.7.3
- **认证授权**: python-jose[cryptography], passlib[bcrypt]

## 项目结构

```
d:/Project/
├── app/
│   ├── api/              # API 路由模块
│   │   ├── class_api.py
│   │   ├── grades_api.py
│   │   ├── login_api.py
│   │   ├── statistical_analysis.py
│   │   ├── statistics_api.py
│   │   ├── stu_offers_api.py
│   │   ├── students.py
│   │   └── teachers_api.py
│   ├── core/             # 核心配置
│   │   ├── app_config.py  # 应用配置
│   │   ├── database.py    # 数据库配置
│   │   └── log_config.py  # 日志配置
│   ├── dao/              # 数据访问层
│   │   ├── class_dao.py
│   │   ├── grades_dao.py
│   │   ├── statistical_analysis_dao.py
│   │   ├── statistics_dao.py
│   │   ├── stu_offers_dao.py
│   │   ├── students_dao.py
│   │   └── teachers_dao.py
│   ├── middlewares/      # 中间件
│   │   ├── auth_middleware.py      # 认证中间件
│   │   ├── cors_middleware.py      # CORS 中间件
│   │   └── logs_request.py         # 请求日志中间件
│   ├── model/            # 数据模型
│   │   ├── classes.py
│   │   ├── grades.py
│   │   ├── offers.py
│   │   ├── students.py
│   │   └── teachers.py
│   └── scheme/           # 请求/响应模式
│       ├── auth_scheme.py
│       ├── class_update.py
│       ├── classbase.py
│       ├── grades_request.py
│       ├── grades_response.py
│       ├── statistics_response.py
│       ├── stu_offers_request.py
│       ├── stu_offers_response.py
│       └── students_request.py
├── logs/                 # 日志文件目录
├── sql/                  # SQL 脚本目录
├── venv/                 # Python 虚拟环境
├── requirements.txt      # 项目依赖
├── .env                  # 环境变量配置文件
└── README.md            # 项目说明文档
```

## 环境要求

- Python 3.8+
- MySQL 5.7+

## 安装步骤

### 1. 克隆项目

```bash
git clone <repository-url>
cd Project
```

### 2. 创建虚拟环境

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

在项目根目录创建 `.env` 文件，配置以下变量：

```env
# 应用配置
APP_ENV=development
DEBUG=True
SECRET_KEY=your_secret_key_here

# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=mydb
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
```

### 5. 初始化数据库

运行 `sql/` 目录下的 SQL 脚本初始化数据库表结构和初始数据。

## 运行项目

### 开发模式

```bash
# 从项目根目录运行
python -m uvicorn app.main:app --host 0.0.0.0 --port 80 --reload
```

或者直接运行：

```bash
cd app
python main.py
```

### 生产模式

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 80 --workers 4
```

## API 文档

项目启动后，可以通过以下地址访问 API 文档：

- Swagger UI: `http://localhost/docs`
- ReDoc: `http://localhost/redoc`

## 主要功能模块

### 1. 登录管理
- 用户登录认证
- JWT Token 生成

### 2. 学生管理
- 学生基本信息 CRUD
- 学生查询和筛选

### 3. 教师管理
- 教师信息 CRUD
- 教师查询功能

### 4. 班级管理
- 班级信息管理
- 班级成员管理

### 5. 成绩管理
- 成绩录入
- 成绩查询
- 成绩统计

### 6. 就业管理
- 学生就业信息管理
- 就业信息统计

### 7. 统计分析
- 数据可视化
- 统计报表生成

## 认证机制

系统使用 JWT (JSON Web Token) 进行身份认证：

1. 用户登录后获取 Token
2. 在请求头中添加：`Authorization: Bearer <your_token>`
3. 系统会验证 Token 的有效性

## 日志管理

使用 Loguru 进行日志管理，日志文件存储在 `logs/` 目录中。

## 开发规范

### 代码结构
- 遵循 MVC 架构模式
- DAO 层负责数据库操作
- API 层处理路由和请求
- Model 层定义数据模型
- Scheme 层定义请求/响应模式

### 命名规范
- 文件名使用小写字母和下划线
- 类名使用大驼峰命名法
- 函数和变量名使用小写字母和下划线

### Git 提交规范
```
<type>(<scope>): <subject>

<body>

<footer>
```

type 类型：
- feat: 新功能
- fix: 修复 bug
- docs: 文档更新
- style: 代码格式调整
- refactor: 重构
- test: 测试相关
- chore: 构建/工具相关

## 常见问题

### 数据库连接失败
检查 `.env` 文件中的数据库配置是否正确。

### 端口被占用
修改 `app/main.py` 中的端口号或终止占用端口的进程。

### 依赖安装失败
尝试使用国内镜像源：
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 贡献指南

欢迎提交 Issue 和 Pull Request 来帮助改进项目。

## 许可证

MIT License

## 联系方式

如有问题或建议，请通过 Issue 联系。
