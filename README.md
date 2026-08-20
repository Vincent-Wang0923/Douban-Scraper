# 豆瓣Top 100电影爬虫

## 可视化驱动的数据库设计
在开始编写爬虫代码前，我们预设了以下四个数据可视化图表需求，并据此设计了数据库表结构：

1. **电影发行年份趋势图 (折线图)**
   - **分析目的：** 观察哪些年代出产了最多进入 Top 100 的经典电影。
   - **必需字段：** `release_year` (INT) 
   
2. **电影类型分布图 (饼图)**
   - **分析目的：** 展示不同电影类型（如：剧情、动作、科幻）在榜单中的占比。
   - **必需字段：** `genre` (VARCHAR)
   
3. **制片国家/地区上榜数量 (柱状图)**
   - **分析目的：** 统计哪些国家/地区制作的高分电影最多。
   - **必需字段：** `country` (VARCHAR)
   
4. **评分与评论人数关系图 (散点图)**
   - **分析目的：** 探索电影的评分高低与其热度（评论人数）之间是否存在相关性。
   - **必需字段：** `rating` (DECIMAL), `review_count` (INT)

## 高容错数据提取 (核心亮点)
豆瓣网页的 HTML 结构往往存在不规范的情况（例如部分电影缺少 `<br>` 换行符或标签间距混乱）。为了避免过度依赖死板的 DOM 树节点遍历，本爬虫创新性地采用了**基于正则表达式 (`re` 模块) 的文本模糊匹配**来提取年份、国家和类型。这一设计不仅大幅提升了代码的容错率，还保证了落库数据的高度纯净（纯整数/小数类型），为后续的图表渲染打下了完美基础。

## 文件结构
- `douban_scraper.py`: 核心爬虫脚本（面向对象架构），内置正则解析与高容错处理逻辑。
- `mysql_helper.py`: 通用的 MySQL 数据库操作封装类，支持高度复用。
- `test_douban_scraper.py`: 针对爬虫核心逻辑的自动化单元测试脚本。
- `requirements.txt`: 运行本项目所需的 Python 第三方依赖库。
- `README.md`: 项目说明与架构文档。

## 数据库准备
在运行爬虫程序前，请先在终端登录本地 MySQL，并执行以下 SQL 语句完成数据库和表的创建：

```sql
CREATE DATABASE IF NOT EXISTS crawler_db;
USE crawler_db;

DROP TABLE IF EXISTS douban_top_100;

CREATE TABLE douban_top_100 (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rank_num INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    release_year INT,
    country VARCHAR(100),
    genre VARCHAR(100),
    rating DECIMAL(3,1),
    review_count INT
);
```

## 安装与运行指南
**1. 安装依赖库**
在终端运行以下命令安装所需的环境：
```bash
pip install -r requirements.txt
```

**2. 运行主爬虫程序**
执行以下命令，根据提示输入数据库密码后，程序将自动抓取并保存前 100 条清洗后的数据：
```bash
python douban_scraper.py
```

**3. 运行自动化测试**
验证爬虫是否精准提取了 100 条有效数据：
```bash
python test_douban_scraper.py
```
