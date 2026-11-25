# 校园二手书交易平台

面向校内学生的二手教材发布与交易平台，实现“注册登录—发布图书—检索浏览—下单预订—线下成交”的主流程。

技术栈：Python 3.10+ / Flask 3 / Flask-SQLAlchemy / MySQL 8.0 / Jinja2 模板 / 原生 CSS 与少量 JavaScript。

## 一、目录结构

```
campus-books/
├── run.py                     # 启动入口
├── config.py                  # 配置（MySQL 连接、业务字典、上传限制）
├── requirements.txt           # 依赖清单
├── .env.example               # MySQL 连接参数示例
├── sql/schema.sql             # 数据库建表脚本（部署与文档留档）
├── scripts/
│   ├── init_db.py             # 建库、建表、写入演示数据
│   ├── start_mysql.ps1        # 启动本地隔离 MySQL 实例
│   └── stop_mysql.ps1         # 停止本地隔离 MySQL 实例
├── app/
│   ├── __init__.py            # 应用工厂
│   ├── extensions.py          # 数据库扩展实例
│   ├── models.py              # 用户 / 图书 / 订单模型
│   ├── utils.py               # 登录校验、图片上传、参数清洗
│   ├── routes/                # 路由：auth / books / orders / users
│   ├── templates/             # 11 个 Jinja2 模板
│   └── static/                # style.css、main.js、uploads/ 封面图
├── tests/                     # 接口与业务验收测试
└── docs/                      # 项目文档、UML 图、接口文档
```

## 二、环境准备

1. 获取代码并安装 Python 依赖（以下命令均在项目根目录执行）：

```bash
git clone <仓库地址>
cd campus-books
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2. 准备 MySQL 8.0 实例，两种方式任选其一：

- 使用本机已安装的 MySQL 服务：启动服务后确认监听 `127.0.0.1:3306`；
- 使用仓库自带的隔离实例脚本：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start_mysql.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\stop_mysql.ps1   # 停止时执行
```

脚本默认的 MySQL 安装路径写在 `scripts/start_mysql.ps1` 顶部，与本机不一致时按实际安装位置修改；配置写入 `mysql-log/my.ini`，数据目录为 `mysql-data`（相对项目根目录）。注意数据目录名不要带前导点（如 `.mysql-data`），否则 MySQL 8 会按相对路径解析并启动失败。

3. 配置数据库账号：编辑 `config.py` 中的 `DB_USER`、`DB_PASSWORD`，或设置同名环境变量（`MYSQL_USER`、`MYSQL_PASSWORD`、`MYSQL_HOST`、`MYSQL_PORT`、`MYSQL_DATABASE`）。

## 三、初始化数据库

```bash
python scripts/init_db.py
```

该脚本依次完成三件事：创建 `campus_books` 数据库（utf8mb4）；按模型创建 `users`、`books`、`orders` 三张表；写入 2 个演示账号与 8 本图书。若已存在数据则跳过演示数据，不会覆盖。

也可以手工执行建表脚本：

```bash
mysql -u root -p < sql/schema.sql
```

## 四、启动项目

```bash
python run.py
```

浏览器打开 http://127.0.0.1:5000 即可访问。演示账号：`seller01` / `buyer01`，密码均为 `123456`。

Windows 下也可以双击项目根目录的 `启动项目.bat`，它会先确保 MySQL 实例已启动、再拉起 Flask 并自动打开浏览器。

## 五、已实现功能

| 模块 | 功能 | 说明 |
| --- | --- | --- |
| 认证 | 注册、登录、退出 | 密码使用 werkzeug 哈希存储，登录态由 session 维护 |
| 图书 | 发布图书 | 书名、作者、分类、成色、售价、原价、描述、封面图 |
| 图书 | 检索与筛选 | 关键词、分类、成色、价格区间、三种排序、分页 |
| 图书 | 详情与同类推荐 | 浏览量累加，同类图书最多 4 本 |
| 图书 | 上下架、删除 | 仅本人可操作，存在进行中订单时禁止删除 |
| 订单 | 下单预订 | 生成订单号，图书自动置为“已预订”，禁止购买自己的书 |
| 订单 | 我买到的 / 我卖出的 | 按状态展示，支持取消 |
| 订单 | 确认成交 | 卖家确认后订单完成、图书置为已售出 |
| 用户 | 个人中心 | 资料修改、密码修改、发布与交易统计 |

## 六、主要路由

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/` | 首页兼检索页 |
| GET | `/book/<id>` | 图书详情 |
| GET/POST | `/books/new` | 发布图书（需登录） |
| GET | `/books/mine` | 我的书架（需登录） |
| POST | `/book/<id>/toggle` | 上下架 |
| POST | `/book/<id>/delete` | 删除图书 |
| GET/POST | `/register`、`/login` | 注册、登录 |
| GET | `/logout` | 退出 |
| POST | `/order/create/<book_id>` | 下单 |
| GET | `/orders/bought`、`/orders/sold` | 我买到的、我卖出的 |
| POST | `/order/<id>/confirm`、`/order/<id>/cancel` | 确认成交、取消订单 |
| GET/POST | `/profile` | 个人中心 |
| POST | `/profile/password` | 修改密码 |

## 七、团队分工

| 成员 | 负责模块 |
| --- | --- |
| 吴懿韬 | 需求规格说明书、系统架构与选型、图书与订单业务路由、代码整合 |
| 姜恺 | 页面模板与全站样式、表单校验与交互脚本 |
| 欧阳容 | 数据库结构设计、建表与初始化脚本、数据模型、认证与用户路由、验收测试 |
| 潘浩阳 | 仓库与运行环境搭建、启停脚本、部署说明与接口文档、演示数据、进展报告整理 |

## 八、说明

- 当前采用线下当面交易，不含在线支付、物流、评价与信用体系。
- 上传的封面图限制为 png/jpg/jpeg/gif/webp，单文件不超过 5MB，文件名由 uuid 重命名，避免路径穿越与重名覆盖。
- 生产环境请通过环境变量设置 `SECRET_KEY`，并将 `debug=True` 关闭。
- 所有脚本与文档中的路径均以项目根目录为基准，不依赖任何个人机器的绝对路径，clone 后按上文步骤即可复现。
