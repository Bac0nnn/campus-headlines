# -*- coding: utf-8 -*-
import os
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_SECTION
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

BASE = r"F:\IDEA\YXP-QM\campus-headlines"
SHOTS = os.path.join(BASE, "docs", "screenshots")
OUT = os.path.join(BASE, "docs", "校园头条部署文档.docx")
FONT = "微软雅黑"
BLUE = RGBColor(0x1F, 0x3A, 0x7A)
GRAY = RGBColor(0x5A, 0x64, 0x74)


def set_run_font(run, size=10.5, bold=False, color=None, name=FONT):
    run.font.name = name
    run.font.size = Pt(size)
    run.bold = bold
    if color is not None:
        run.font.color.rgb = color
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.append(rFonts)
    rFonts.set(qn("w:ascii"), name)
    rFonts.set(qn("w:hAnsi"), name)
    rFonts.set(qn("w:eastAsia"), name)


def init_doc():
    doc = Document()
    section = doc.sections[0]
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(2.4)
    section.bottom_margin = Cm(2.2)
    section.left_margin = Cm(2.4)
    section.right_margin = Cm(2.2)

    normal = doc.styles["Normal"]
    normal.font.name = FONT
    normal.font.size = Pt(10.5)
    normal.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)

    for level, size in [(1, 18), (2, 14), (3, 12)]:
        style = doc.styles["Heading %d" % level]
        style.font.name = FONT
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = BLUE
        style.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
    return doc


def h1(doc, text):
    p = doc.add_heading(text, level=1)
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(8)


def h2(doc, text):
    p = doc.add_heading(text, level=2)
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(6)


def p(doc, text, bold=False, size=10.5, color=None, align=None, space_after=6):
    para = doc.add_paragraph()
    run = para.add_run(text)
    set_run_font(run, size=size, bold=bold, color=color)
    para.paragraph_format.space_after = Pt(space_after)
    para.paragraph_format.line_spacing = 1.5
    if align is not None:
        para.alignment = align
    return para


def bullet(doc, text):
    para = doc.add_paragraph(style="List Bullet")
    run = para.add_run(text)
    set_run_font(run, size=10.5)
    para.paragraph_format.line_spacing = 1.4
    return para


def shade(cell, color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), color)
    tcPr.append(shd)


def table(doc, headers, rows, widths=None):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = t.rows[0].cells
    for i, text in enumerate(headers):
        hdr[i].text = ""
        run = hdr[i].paragraphs[0].add_run(text)
        set_run_font(run, size=9.5, bold=True, color=RGBColor(0xFF, 0xFF, 0xFF))
        shade(hdr[i], "1F3A7A")
        hdr[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    for row in rows:
        cells = t.add_row().cells
        for i, text in enumerate(row):
            cells[i].text = ""
            run = cells[i].paragraphs[0].add_run(str(text))
            set_run_font(run, size=9)
            cells[i].paragraphs[0].paragraph_format.space_after = Pt(2)
    if widths:
        for row in t.rows:
            for i, width in enumerate(widths):
                row.cells[i].width = Cm(width)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


def code(doc, text):
    para = doc.add_paragraph()
    para.paragraph_format.left_indent = Cm(0.6)
    para.paragraph_format.space_before = Pt(3)
    para.paragraph_format.space_after = Pt(6)
    run = para.add_run(text)
    run.font.name = "Consolas"
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor(0x1F, 0x24, 0x30)
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.append(rFonts)
    rFonts.set(qn("w:ascii"), "Consolas")
    rFonts.set(qn("w:hAnsi"), "Consolas")


def picture(doc, filename, caption, width=15.2):
    path = os.path.join(SHOTS, filename)
    if os.path.exists(path):
        doc.add_picture(path, width=Cm(width))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap = doc.add_paragraph()
        run = cap.add_run(caption)
        set_run_font(run, size=9, color=GRAY)
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap.paragraph_format.space_after = Pt(10)


def footer(doc):
    section = doc.sections[0]
    para = section.footer.paragraphs[0]
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = para.add_run("校园头条系统部署文档  ·  第 ")
    set_run_font(run, size=8, color=GRAY)
    run2 = para.add_run()
    fld1 = OxmlElement("w:fldChar"); fld1.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText"); instr.set(qn("xml:space"), "preserve"); instr.text = "PAGE"
    fld2 = OxmlElement("w:fldChar"); fld2.set(qn("w:fldCharType"), "end")
    run2._r.append(fld1); run2._r.append(instr); run2._r.append(fld2)
    set_run_font(run2, size=8, color=GRAY)
    run3 = para.add_run(" 页")
    set_run_font(run3, size=8, color=GRAY)


doc = init_doc()
footer(doc)

# ---------------- 封面 ----------------
for _ in range(3):
    doc.add_paragraph()
p(doc, "校园头条系统", bold=True, size=34, color=BLUE, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=6)
p(doc, "CAMPUS HEADLINES", size=13, color=GRAY, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=24)
p(doc, "部  署  文  档", bold=True, size=22, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=10)
p(doc, "SSM（Spring + Spring MVC + MyBatis-Plus）+ Vue 3 + MySQL 8.0", size=11, color=GRAY,
  align=WD_ALIGN_PARAGRAPH.CENTER, space_after=60)

info = [
    ["课程名称", "Java EE 企业级应用开发"],
    ["项目名称", "校园头条系统（Campus Headlines）"],
    ["技术栈", "SSM（Spring 5.3 + Spring MVC 5.3 + MyBatis-Plus 3.5）/ MySQL 8.0 / Vue 3"],
    ["姓    名", "____________________"],
    ["学    号", "____________________"],
    ["班    级", "____________________"],
    ["指导教师", "____________________"],
    ["编写日期", "2026 年 10 月"],
]
t = doc.add_table(rows=0, cols=2)
t.alignment = WD_TABLE_ALIGNMENT.CENTER
for k, v in info:
    cells = t.add_row().cells
    cells[0].text = ""
    cells[1].text = ""
    r1 = cells[0].paragraphs[0].add_run(k)
    r2 = cells[1].paragraphs[0].add_run(v)
    set_run_font(r1, size=10.5, bold=True, color=GRAY)
    set_run_font(r2, size=10.5)
    cells[0].width = Cm(3.2)
    cells[1].width = Cm(10.5)

doc.add_page_break()

# ---------------- 目录 ----------------
h1(doc, "目  录")
toc = [
    "1  项目概述",
    "2  运行环境",
    "3  数据库部署（含 DBeaver 连接）",
    "4  后端部署",
    "5  前端部署",
    "6  一键启动与停止",
    "7  系统入口与演示账号",
    "8  SSM 技术实现说明",
    "9  数据库表结构设计",
    "10 常见问题",
    "11 系统运行截图",
]
for item in toc:
    p(doc, item, size=11, space_after=4)

doc.add_page_break()

# ---------------- 1 项目概述 ----------------
h1(doc, "1  项目概述")
h2(doc, "1.1  项目背景")
p(doc, "校园头条系统是在《Java EE 企业级应用开发教程》第 14 章「黑马头条」案例基础上完成的校园化实现。"
       "项目保留「自媒体生产内容 → 平台审核 → 用户浏览互动」的核心业务闭环，面向高校场景提供校园新闻、"
       "学院动态、社团活动、讲座就业等内容的发布与浏览服务。")
p(doc, "系统采用前后端分离架构：后端基于 SSM（Spring + Spring MVC + MyBatis-Plus）构建 REST 接口，"
       "前端使用 Vue 3 + Vite + Element Plus 实现单页应用，数据存储使用 MySQL 8.0。")

h2(doc, "1.2  功能结构")
table(doc,
      ["端", "模块", "主要功能"],
      [
          ["公共", "注册 / 登录", "三端统一账号，注册时选择普通用户 / 作者 / 审核员，验证码或密码登录"],
          ["普通用户", "文章浏览", "频道切换、搜索、头条推荐、文章列表、文章详情"],
          ["普通用户", "个人中心", "修改昵称 / 性别 / 简介、上传头像（入库）、退出账号"],
          ["作者", "素材管理", "图片上传（入库）、收藏、删除、分页"],
          ["作者", "发布文章", "富文本编辑、标签、频道、封面（数据库图片）、存草稿、提交审核"],
          ["作者", "内容列表", "状态筛选、关键词、频道、日期范围、编辑、删除"],
          ["审核员", "审核工作台", "待审 / 已通过 / 已驳回、查看全文、通过发布、驳回意见、审核记录"],
          ["作者/审核员", "个人资料", "修改昵称、简介、性别，上传头像（入库），退出登录"],
      ],
      widths=[2.2, 3.0, 10.6])

h2(doc, "1.3  项目特点")
bullet(doc, "前后端分离，接口统一使用 Result 包装，前端 Axios 统一拦截错误与登录态。")
bullet(doc, "完整的注册、登录、个人资料修改、退出登录闭环，密码使用 BCrypt 加密存储。")
bullet(doc, "真实的人工审核流程，审核结果写入 audit_record 表，文章状态实时同步到用户端。")
bullet(doc, "使用 Spring AOP 记录控制器执行耗时，使用 MyBatis XML 动态 SQL 完成多条件检索。")
bullet(doc, "数据库建立主键、唯一索引、普通索引与外键约束，保证数据完整性。")

doc.add_page_break()

# ---------------- 2 运行环境 ----------------
h1(doc, "2  运行环境")
h2(doc, "2.1  软件环境")
table(doc,
      ["软件", "版本", "说明"],
      [
          ["操作系统", "Windows 10 / 11", "本项目在 Windows 上开发与验证"],
          ["JDK", "17.0.10", "C:\\Program Files\\Java\\jdk-17"],
          ["Maven", "3.9.9", "C:\\tools\\apache-maven-3.9.9"],
          ["MySQL", "8.0.46", "F:\\MySQL\\8.0\\mysql-8.0.46-winx64，服务名 MySQL80"],
          ["Node.js", "18 LTS 及以上", "本项目验证环境为 Node 24"],
          ["浏览器", "Edge / Chrome", "用于访问系统与截图验证"],
      ],
      widths=[3.0, 3.4, 9.4])

h2(doc, "2.2  技术版本")
table(doc,
      ["层次", "技术", "版本"],
      [
          ["后端框架", "SSM（Spring / Spring MVC）", "5.3.31"],
          ["持久层", "MyBatis-Plus", "3.5.3.2"],
          ["数据库", "MySQL", "8.0.46"],
          ["认证", "JJWT", "0.11.5"],
          ["密码", "spring-security-crypto（BCrypt）", "5.7.11"],
          ["前端", "Vue / Vue Router / Pinia", "3.4 / 4.4 / 2.2"],
          ["UI", "Element Plus", "2.8.1"],
          ["构建", "Vite / Maven", "5.4 / 3.9"],
          ["富文本", "wangEditor", "5.1"],
      ],
      widths=[3.0, 7.8, 5.0])

doc.add_page_break()

# ---------------- 3 数据库部署 ----------------
h1(doc, "3  数据库部署（含 DBeaver 连接）")
h2(doc, "3.1  启动 MySQL 服务")
p(doc, "本机 MySQL 8.0 安装在 F:\\MySQL\\8.0\\mysql-8.0.46-winx64，已注册为 Windows 服务 MySQL80。"
       "可在「服务」中启动，或以管理员身份执行：")
code(doc, "net start MySQL80")
p(doc, "确认服务运行：")
code(doc, "Get-Service MySQL80")
p(doc, "正常情况下状态为 Running。数据库文件与配置均保存在 F:\\MySQL 目录下，可直接用 DBeaver 连接查看。")

h2(doc, "3.2  连接参数")
table(doc,
      ["参数", "值"],
      [
          ["主机", "127.0.0.1（或 localhost）"],
          ["端口", "3306"],
          ["用户名", "root"],
          ["密码", "123456"],
          ["数据库", "campus_headlines"],
          ["字符集", "utf8mb4"],
      ],
      widths=[4.0, 11.6])

h2(doc, "3.3  DBeaver 连接步骤")
p(doc, "1）打开 DBeaver，点击左上角「新建数据库连接」，选择 MySQL，点击「下一步」。")
p(doc, "2）首次连接会提示下载 MySQL 驱动，点击「下载」等待完成。")
p(doc, "3）在连接设置中填写：主机 localhost、端口 3306、用户名 root、密码 123456，"
       "并在「数据库」一栏填写 campus_headlines。")
p(doc, "4）点击「测试连接」，提示成功后点击「完成」。")
p(doc, "5）在左侧导航中右键连接 →「编辑连接」→「MySQL」→ 勾选「显示所有数据库」，"
       "即可展开 campus_headlines，查看 9 张表及数据。")
p(doc, "6）如提示 Public Key Retrieval is not allowed，在驱动属性中把 allowPublicKeyRetrieval 设置为 true，"
       "或使用 useSSL=false。")

h2(doc, "3.4  导入 SQL 脚本")
p(doc, "数据库脚本位于提交包的「数据库」目录：schema.sql 为建库建表语句，data.sql 为种子数据。"
       "可以通过 DBeaver 的 SQL 编辑器依次执行，也可以使用命令行：")
code(doc, 'mysql -uroot -p123456 --default-character-set=utf8mb4 < schema.sql')
code(doc, 'mysql -uroot -p123456 --default-character-set=utf8mb4 < data.sql')
p(doc, "如果使用 DBeaver：打开 SQL 编辑器，先执行 schema.sql，再执行 data.sql；"
       "执行前确认当前连接为 localhost:3306，脚本中已包含 CREATE DATABASE 与 USE 语句。")

h2(doc, "3.5  数据备份与恢复")
p(doc, "备份命令（在 cmd 中执行，输出文件位于当前目录）：")
code(doc, 'mysqldump -uroot -p123456 --databases campus_headlines --default-character-set=utf8mb4 > campus_headlines.sql')
p(doc, "恢复命令：")
code(doc, 'mysql -uroot -p123456 --default-character-set=utf8mb4 < campus_headlines.sql')
p(doc, "提交包中已附带一份完整的 campus_headlines.sql，可直接导入恢复演示数据。")

h2(doc, "3.6  图片入库说明")
p(doc, "本系统不依赖本地图片目录：用户头像保存在 ap_user.avatar_data（LONGBLOB），"
       "新闻封面与素材图片保存在 material.data（LONGBLOB），并记录 content_type 与 original_name。")
p(doc, "头像读取接口：GET /api/auth/avatar/{id}；素材/封面读取接口：GET /api/files/material/{id}。"
       "新闻表 cover_images 中保存的是素材接口地址，因此作者重新登录、审核员审核、用户浏览时都能从数据库读取到同一张封面。")

doc.add_page_break()

# ---------------- 4 后端部署 ----------------
h1(doc, "4  后端部署")
h2(doc, "4.1  目录说明")
table(doc,
      ["目录 / 文件", "说明"],
      [
          ["backend/pom.xml", "Maven 依赖与打包配置"],
          ["src/main/java/com/campus/headlines", "后端源码根包"],
          ["common", "统一响应 Result、分页、异常处理"],
          ["config", "WebMvc、MyBatis-Plus、密码器配置"],
          ["controller", "认证、频道、自媒体、审核、文章接口"],
          ["service", "业务实现（认证、素材、文章、审核、文件存储）"],
          ["mapper", "MyBatis-Plus Mapper 接口"],
          ["resources/mapper/NewsMapper.xml", "动态 SQL"],
          ["resources/application.yml", "端口、数据源、JWT、上传目录等配置"],
      ],
      widths=[7.4, 8.2])

h2(doc, "4.2  配置说明")
p(doc, "application.yml 中使用环境变量占位，默认值与本机环境一致：")
code(doc, "server.port: 8080\n"
          "spring.datasource.url: jdbc:mysql://127.0.0.1:3306/campus_headlines\n"
          "spring.datasource.username: root\n"
          "spring.datasource.password: 123456\n"
          "campus.upload.dir: ./data/uploads\n"
          "campus.demo.auto-audit: false")
p(doc, "如需修改数据库账号、端口或审核模式，可在项目根目录 .env 中调整，启动脚本会自动注入。")

h2(doc, "4.3  构建与启动")
p(doc, "方式一：一键脚本（推荐）")
code(doc, "scripts\\start.bat")
p(doc, "方式二：手动执行")
code(doc, "cd backend\nmvn clean package -DskipTests\njava -jar target/campus-headlines.jar")
p(doc, "启动成功后访问健康检查接口，返回 database=UP 即表示数据库连接正常：")
code(doc, "http://127.0.0.1:8080/api/health")

h2(doc, "4.4  接口文档")
p(doc, "完整接口说明见项目 docs/接口文档.md，包含认证、频道、素材、文章、审核、点赞评论等接口的"
       "请求参数与响应示例。")

doc.add_page_break()

# ---------------- 5 前端部署 ----------------
h1(doc, "5  前端部署")
h2(doc, "5.1  安装依赖")
code(doc, "cd frontend\nnpm install")
h2(doc, "5.2  开发模式启动")
code(doc, "npm run dev")
p(doc, "默认地址 http://127.0.0.1:5173。Vite 已配置代理：/api 与 /uploads 转发到 http://127.0.0.1:8080。")
h2(doc, "5.3  生产构建")
code(doc, "npm run build")
p(doc, "构建产物位于 frontend/dist。可使用 Nginx 托管静态文件，并将 /api、/uploads 反向代理到后端：")
code(doc, "server {\n"
          "  listen 80;\n"
          "  root   /path/to/frontend/dist;\n"
          "  index  index.html;\n"
          "  location / { try_files $uri $uri/ /index.html; }\n"
          "  location /api { proxy_pass http://127.0.0.1:8080; }\n"
          "  location /uploads { proxy_pass http://127.0.0.1:8080; }\n"
          "}")

# ---------------- 6 一键启动 ----------------
h1(doc, "6  一键启动与停止")
p(doc, "项目根目录 scripts 下提供三个脚本：")
table(doc,
      ["脚本", "作用"],
      [
          ["start.bat", "双击启动，内部调用 start.ps1"],
          ["start.ps1", "检查环境 → 初始化数据库 → 构建后端 → 启动前后端 → 打开浏览器"],
          ["stop.ps1", "根据 PID 停止前后端进程"],
      ],
      widths=[4.0, 11.6])
p(doc, "start.ps1 支持以下参数：")
table(doc,
      ["参数", "说明"],
      [
          ["-Reset", "删除并重建数据库后启动（清空数据）"],
          ["-SkipBuild", "跳过 Maven 构建"],
          ["-NoBrowser", "启动后不自动打开浏览器"],
          ["-Reinstall", "强制重新安装前端依赖"],
      ],
      widths=[4.0, 11.6])
p(doc, "脚本会检测 8080 / 5173 端口占用，打印访问地址、演示账号与日志位置；重复执行不会重复启动服务。")

doc.add_page_break()

# ---------------- 7 入口与账号 ----------------
h1(doc, "7  系统入口与演示账号")
table(doc,
      ["入口", "地址"],
      [
          ["用户端", "http://127.0.0.1:5173"],
          ["用户登录", "http://127.0.0.1:5173/login"],
          ["用户注册", "http://127.0.0.1:5173/register"],
          ["自媒体端登录", "http://127.0.0.1:5173/media/login"],
          ["审核工作台", "http://127.0.0.1:5173/media/audit"],
          ["后端接口", "http://127.0.0.1:8080/api"],
      ],
      widths=[4.6, 11.0])
p(doc, "演示账号：")
table(doc,
      ["端", "账号", "密码 / 验证码", "角色"],
      [
          ["普通用户", "13800138000", "123456（验证码同）", "只浏览校园新闻、修改资料、上传头像"],
          ["作者", "13900000002", "123456", "发布文章、管理素材、提交审核"],
          ["审核员", "13900000001", "123456", "审核作者提交的稿件"],
          ["兼容旧账号", "admin / cs / photo / job", "123456", "admin 为审核员，其余为作者"],
      ],
      widths=[3.0, 4.4, 5.4, 3.0])
p(doc, "审核流程：作者提交审核 → 审核员进入审核工作台 → 查看全文 → 通过并发布 / 驳回（填写意见）→ "
       "通过后文章立即出现在普通用户端。")

# ---------------- 8 技术实现 ----------------
h1(doc, "8  SSM 技术实现说明")
table(doc,
      ["技术点", "实现位置", "说明"],
      [
          ["Spring IoC", "各 Service / Controller", "使用构造器注入（@RequiredArgsConstructor），由 Spring 容器统一管理 Bean"],
          ["Spring AOP", "aspect/LogAspect.java", "@Aspect + @Pointcut + @Around 记录每个控制器方法的执行耗时与异常"],
          ["声明式事务", "AuthService / MediaService / AuditService", "@Transactional 覆盖注册、资料修改、发文、点赞、评论、审核"],
          ["Spring MVC 拦截器", "interceptor/AuthInterceptor.java", "解析 JWT、写入 UserContext、按 USER / MEDIA 角色拦截"],
          ["文件上传", "AuthService / MediaService", "头像写入 ap_user.avatar_data，封面/素材写入 material.data，由接口从数据库读取"],
          ["MyBatis 动态 SQL", "resources/mapper/NewsMapper.xml", "where / if / choose 完成多条件查询，foreach 统计频道文章数"],
          ["MyBatis-Plus", "Mapper / Service", "BaseMapper CRUD、分页插件、LambdaQueryWrapper、逻辑删除"],
          ["数据库完整性", "sql/schema.sql", "主键、唯一索引、普通索引、9 张表之间的外键约束"],
      ],
      widths=[3.2, 6.0, 6.4])

p(doc, "以审核为例：AuditService.review() 在一个事务中完成「更新文章状态 + 写入审核记录」，"
       "任意一步失败都会回滚，保证审核数据一致。")
p(doc, "以内容列表为例：MediaService.pageNews() 调用 NewsMapper.selectMediaNews()，"
       "XML 中使用 <where> 自动处理 AND 前缀，使用 <if> 按状态、频道、关键词、日期动态拼接，"
       "使用 <choose> 在「最新 / 最热」排序之间切换。")

doc.add_page_break()

# ---------------- 9 表结构 ----------------
h1(doc, "9  数据库表结构设计")
table(doc,
      ["表名", "说明", "关键字段"],
      [
          ["ap_user", "统一用户", "phone 唯一、password、nickname、role（0 普通/1 作者/2 审核员）、avatar_data（头像二进制）、avatar_type、bio"],
          ["wm_user", "作者/审核员身份", "ap_user_id 外键、username 唯一、name、role（0 作者 / 1 审核员）"],
          ["channel", "频道", "name 唯一、sort、status"],
          ["material", "素材", "wm_user_id、url、content_type、data（图片二进制）、width、height、is_collected"],
          ["news", "文章", "wm_user_id、channel_id、title、content、cover_images（素材接口地址）、status、publish_time"],
          ["news_material", "文章素材关联", "news_id + material_id 唯一"],
          ["news_like", "点赞", "news_id + user_id 唯一"],
          ["news_comment", "评论", "news_id、user_id、content、status"],
          ["audit_record", "审核记录", "news_id、auditor_id、result、reason"],
      ],
      widths=[3.6, 4.4, 7.6])

p(doc, "外键约束：")
bullet(doc, "news.wm_user_id → wm_user.id，news.channel_id → channel.id")
bullet(doc, "material.wm_user_id → wm_user.id")
bullet(doc, "news_material.news_id → news.id（级联删除），news_material.material_id → material.id（级联删除）")
bullet(doc, "news_like / news_comment 的 news_id、user_id 分别关联 news、ap_user（级联删除）")
bullet(doc, "audit_record.news_id → news.id（级联删除），auditor_id → wm_user.id")

p(doc, "完整建表语句与索引定义见 sql/schema.sql，种子数据见 sql/data.sql。")

# ---------------- 10 常见问题 ----------------
h1(doc, "10  常见问题")
qa = [
    ("启动时提示 MySQL 连接失败",
     "检查 MySQL80 服务是否启动，确认 .env 中 DB_USER / DB_PASSWORD 正确；DBeaver 可用同样参数测试连接。"),
    ("找不到 Maven",
     "安装 Maven 3.6+ 并加入 PATH，或在 .env 中设置 MAVEN_HOME（例如 C:\\tools\\apache-maven-3.9.9）。"),
    ("找不到 MySQL 8 客户端",
     "在 .env 中设置 MYSQL_BIN 指向 mysql.exe，例如 F:\\MySQL\\8.0\\mysql-8.0.46-winx64\\bin\\mysql.exe。"),
    ("8080 或 5173 端口被占用",
     "修改 .env 中 BACKEND_PORT / FRONTEND_PORT，或结束占用端口的进程。"),
    ("上传图片后显示 404",
     "确认后端已用最新代码启动；文件保存在 backend/data/uploads，由 /uploads/** 映射，前端 Vite 已配置代理。"),
    ("审核工作台菜单不显示",
     "只有审核员账号（ap_user.role = 2，如 13900000001 / 123456）才会显示；作者账号只能发布文章。"),
    ("PowerShell 禁止运行脚本",
     "使用 start.bat，或执行 Set-ExecutionPolicy -Scope CurrentUser RemoteSigned。"),
    ("想恢复初始数据",
     "执行 scripts\\start.ps1 -Reset，或重新导入 数据库/schema.sql 与 data.sql。"),
]
for q, a in qa:
    p(doc, "问：" + q, bold=True, space_after=2)
    p(doc, "答：" + a, color=GRAY, space_after=8)

doc.add_page_break()

# ---------------- 11 截图 ----------------
h1(doc, "11  系统运行截图")
p(doc, "以下截图由 Playwright 驱动真实浏览器完成全流程操作后自动截取，覆盖注册、登录、发文、审核、"
       "个人中心、点赞评论及移动端适配。")

picture(doc, "02-register-role.png", "图 11-1  三端统一注册（普通用户 / 作者 / 审核员）")
picture(doc, "03-author-material.png", "图 11-2  作者素材管理")
picture(doc, "04-author-uploaded.png", "图 11-3  上传封面图片（二进制入库）")
picture(doc, "05-publish-db-cover.png", "图 11-4  作者发布文章并使用数据库封面")
picture(doc, "07-audit-pending.png", "图 11-5  审核工作台（待审核列表）")
picture(doc, "09-audit-passed.png", "图 11-6  审核通过后进入已通过列表")
picture(doc, "11-reader-home.png", "图 11-7  普通用户首页（封面来自数据库）")
picture(doc, "12-reader-detail.png", "图 11-8  文章详情（封面从数据库读取）")
picture(doc, "13-avatar-dialog.png", "图 11-9  上传头像对话框")
picture(doc, "14-profile-avatar.png", "图 11-10  头像保存到数据库后的个人中心")

doc.add_page_break()
h1(doc, "附录  提交文件清单")
table(doc,
      ["序号", "文件 / 目录", "说明"],
      [
          ["1", "后端代码", "SSM 后端完整源码（含 pom.xml）"],
          ["2", "前端代码", "Vue 3 前端完整源码（含 package.json）"],
          ["3", "数据库", "schema.sql、data.sql、campus_headlines.sql 及说明"],
          ["4", "校园头条部署文档.docx", "本文档"],
          ["5", "《J2EE应用开发》课程设计报告（俞鑫培）.docx", "课程设计报告"],
      ],
      widths=[1.4, 5.4, 8.8])
p(doc, "说明：项目默认使用人工审核；如需演示自动审核，可在 .env 中将 AUTO_AUDIT 设置为 true。")

doc.save(OUT)
print("SAVED", OUT)
print("paragraphs", len(doc.paragraphs))
