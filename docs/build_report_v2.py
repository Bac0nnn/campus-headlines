# -*- coding: utf-8 -*-
import os, shutil
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

BASE = r"F:\IDEA\YXP-QM\campus-headlines"
TEMPLATE = r"C:\Users\admin\Desktop\《J2EE应用开发》课程设计报告（模板）..docx"
SHOTS = os.path.join(BASE, "docs", "screenshots")
ASSETS = os.path.join(BASE, "docs", "report_assets")
OUT = os.path.join(BASE, "docs", "《J2EE应用开发》课程设计报告（俞鑫培）.docx")
DESKTOP = r"C:\Users\admin\Desktop\《J2EE应用开发》课程设计报告（俞鑫培）.docx"
BACKUP = os.path.join(BASE, "docs", "课程设计报告_旧版备份.docx")

NAME = "俞鑫培"
STUDENT_ID = "122512023064"
BLUE = (0x1F, 0x3A, 0x7A)
GRAY = (0x5A, 0x64, 0x74)


def set_run_font(run, name="宋体", size=12, bold=False, color=None):
    run.font.name = name
    run.font.size = Pt(size)
    run.bold = bold
    if color:
        run.font.color.rgb = RGBColor(*color)
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.append(rFonts)
    rFonts.set(qn("w:ascii"), name)
    rFonts.set(qn("w:hAnsi"), name)
    rFonts.set(qn("w:eastAsia"), "宋体" if name == "Consolas" else name)


def snap_off(paragraph):
    pPr = paragraph._p.get_or_add_pPr()
    snap = OxmlElement("w:snapToGrid")
    snap.set(qn("w:val"), "0")
    pPr.append(snap)


def no_borders(table):
    tblPr = table._tbl.tblPr
    for old in tblPr.findall(qn("w:tblBorders")):
        tblPr.remove(old)
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement("w:" + edge)
        el.set(qn("w:val"), "nil")
        borders.append(el)
    tblPr.append(borders)


def three_line(table, widths=None):
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    tblPr = table._tbl.tblPr
    for old in tblPr.findall(qn("w:tblBorders")):
        tblPr.remove(old)
    borders = OxmlElement("w:tblBorders")
    for edge, sz in (("top", 12), ("bottom", 12), ("left", 0), ("right", 0), ("insideH", 0), ("insideV", 0)):
        el = OxmlElement("w:" + edge)
        el.set(qn("w:val"), "single" if sz else "nil")
        if sz:
            el.set(qn("w:sz"), str(sz))
            el.set(qn("w:color"), "000000")
        borders.append(el)
    tblPr.append(borders)
    if widths:
        for row in table.rows:
            for i, w in enumerate(widths):
                row.cells[i].width = Cm(w)
    for cell in table.rows[0].cells:
        tcPr = cell._tc.get_or_add_tcPr()
        tcBorders = OxmlElement("w:tcBorders")
        bottom = OxmlElement("w:bottom")
        bottom.set(qn("w:val"), "single")
        bottom.set(qn("w:sz"), "8")
        bottom.set(qn("w:color"), "000000")
        tcBorders.append(bottom)
        tcPr.append(tcBorders)


def add_table(doc, headers, rows, widths, caption_text=None, font_size=10, line=14, header_size=10.5):
    table = doc.add_table(rows=1, cols=len(headers))
    three_line(table, widths)
    header_trPr = table.rows[0]._tr.get_or_add_trPr()
    header_trPr.append(OxmlElement("w:tblHeader"))
    for row in table.rows:
        row._tr.get_or_add_trPr().append(OxmlElement("w:cantSplit"))

    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = ""
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.line_spacing = Pt(15)
        snap_off(p)
        set_run_font(p.add_run(h), "宋体", header_size, True)

    for row in rows:
        cells = table.add_row().cells
        for i, value in enumerate(row):
            cells[i].text = ""
            p = cells[i].paragraphs[0]
            p.paragraph_format.space_after = Pt(1)
            p.paragraph_format.line_spacing = Pt(line)
            snap_off(p)
            set_run_font(p.add_run(str(value)), "宋体", font_size)

    for row in table.rows[:-1]:
        for cell in row.cells:
            for para in cell.paragraphs:
                para.paragraph_format.keep_with_next = True

    if caption_text:
        cap = doc.add_paragraph()
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap.paragraph_format.space_before = Pt(2)
        cap.paragraph_format.space_after = Pt(10)
        set_run_font(cap.add_run(caption_text), "宋体", 10.5, False, GRAY)
    else:
        doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return table


def heading(doc, text, level=1):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(16 if level == 1 else 10)
    p.paragraph_format.space_after = Pt(8)
    p.paragraph_format.keep_with_next = True
    set_run_font(p.add_run(text), "黑体", 15 if level == 1 else 12.5, True, BLUE)
    return p


def body(doc, text, indent=True, size=12):
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = Pt(22)
    p.paragraph_format.space_after = Pt(6)
    if indent:
        p.paragraph_format.first_line_indent = Pt(size * 2)
    snap_off(p)
    set_run_font(p.add_run(text), "宋体", size)
    return p


def caption(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(10)
    set_run_font(p.add_run(text), "宋体", 9, False, GRAY)


def picture(doc, path, cap, width=15.4):
    if not os.path.exists(path):
        print("MISSING", path)
        return
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4)
    p.add_run().add_picture(path, width=Cm(width))
    caption(doc, cap)


def screenshot(doc, path, cap, width=15.2):
    if not os.path.exists(path):
        return
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(path, width=Cm(width))
    caption(doc, cap)


def image_grid(doc, items, cols=2, width=6.7):
    rows = (len(items) + cols - 1) // cols
    table = doc.add_table(rows=rows, cols=cols)
    no_borders(table)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for row in table.rows:
        row._tr.get_or_add_trPr().append(OxmlElement("w:cantSplit"))
    for idx, (path, cap) in enumerate(items):
        cell = table.cell(idx // cols, idx % cols)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if os.path.exists(path):
            p.add_run().add_picture(path, width=Cm(width))
        cp = cell.add_paragraph()
        cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cp.paragraph_format.space_after = Pt(6)
        set_run_font(cp.add_run(cap), "宋体", 9, False, GRAY)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def code_block(doc, filename, text, caption_text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True
    set_run_font(p.add_run(caption_text + "  |  " + filename), "Consolas", 9, True, GRAY)

    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.rows[0]._tr.get_or_add_trPr().append(OxmlElement("w:cantSplit"))
    cell = table.rows[0].cells[0]
    cell.width = Cm(16.0)
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), "F7F9FC")
    tcPr.append(shd)
    borders = OxmlElement("w:tcBorders")
    for edge in ("top", "left", "bottom", "right"):
        el = OxmlElement("w:" + edge)
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "4")
        el.set(qn("w:color"), "D8E0EC")
        borders.append(el)
    tcPr.append(borders)

    first = True
    for line in text.splitlines():
        para = cell.paragraphs[0] if first else cell.add_paragraph()
        first = False
        para.paragraph_format.space_after = Pt(0)
        para.paragraph_format.space_before = Pt(0)
        para.paragraph_format.line_spacing = Pt(11.5)
        snap_off(para)
        set_run_font(para.add_run(line if line.strip() else " "), "Consolas", 8.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def footer_page_numbers(doc):
    p = doc.sections[0].footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_run_font(p.add_run("第 "), "宋体", 9, False, GRAY)
    run = p.add_run()
    f1 = OxmlElement("w:fldChar"); f1.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText"); instr.set(qn("xml:space"), "preserve"); instr.text = "PAGE"
    f2 = OxmlElement("w:fldChar"); f2.set(qn("w:fldCharType"), "end")
    run._r.append(f1); run._r.append(instr); run._r.append(f2)
    set_run_font(run, "宋体", 9, False, GRAY)
    set_run_font(p.add_run(" 页"), "宋体", 9, False, GRAY)


if os.path.exists(OUT):
    shutil.copyfile(OUT, BACKUP)

doc = Document(TEMPLATE)

# ---------- 封面 ----------
cover = doc.tables[0]
cover.cell(3, 2).text = ""
cover.cell(3, 2).paragraphs[0].add_run(STUDENT_ID)
cover.cell(4, 2).text = ""
cover.cell(4, 2).paragraphs[0].add_run(NAME)
for r in (3, 4):
    for run in cover.cell(r, 2).paragraphs[0].runs:
        set_run_font(run, "宋体", 12, False)

p2 = doc.paragraphs[2]
p2.text = ""
p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
set_run_font(p2.add_run("校园头条——校园新闻资讯系统报告"), "微软雅黑", 24, True)

# 删除模板正文，保留封面
for p in list(doc.paragraphs[7:]):
    p._element.getparent().remove(p._element)
if len(doc.tables) > 1:
    tbl = doc.tables[1]._element
    tbl.getparent().remove(tbl)

# 去掉封面残留分页符
for para in doc.paragraphs[:7]:
    for br in list(para._p.iter(qn("w:br"))):
        if br.get(qn("w:type")) == "page":
            br.getparent().remove(br)
    para.paragraph_format.page_break_before = False

normal = doc.styles["Normal"]
normal.font.name = "宋体"
normal.font.size = Pt(12)
normal.element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")

# ---------- 一、项目功能列表 ----------
h = heading(doc, "一、项目功能列表")
h.paragraph_format.page_break_before = True
body(doc, "校园头条是一套面向高校师生的校园资讯系统，参考黑马头条的业务逻辑，将主题替换为校园场景。"
          "系统设置普通用户、作者、审核员三种角色：普通用户浏览资讯；作者管理素材、发布文章并提交审核；"
          "审核员审核作者提交的稿件。后端采用 SSM（Spring + Spring MVC + MyBatis-Plus），前端采用 Vue 3 + Element Plus，"
          "数据库为 MySQL 8.0，头像与新闻封面均以二进制保存到数据库。")
body(doc, "系统已实现的核心功能如下表所示：")
add_table(doc,
          ["端", "模块", "功能点", "说明"],
          [
              ["公共", "注册 / 登录", "手机号注册、验证码登录、密码登录", "注册时选择普通用户 / 作者 / 审核员，作者与审核员自动创建业务身份"],
              ["普通用户", "资讯浏览", "频道、搜索、文章列表、文章详情", "仅展示审核通过的文章"],
              ["普通用户", "个人中心", "修改昵称、性别、简介；上传头像；退出", "头像二进制保存到 ap_user.avatar_data"],
              ["作者", "素材管理", "上传封面、收藏、删除、分页", "图片二进制保存到 material.data"],
              ["作者", "发布文章", "富文本、标签、频道、单图/三图/无图封面、草稿、提交审核", "封面地址保存到 news.cover_images"],
              ["作者", "内容列表", "状态 / 关键词 / 频道 / 日期筛选、编辑、删除", "草稿与驳回文章可修改后重新提交"],
              ["审核员", "审核工作台", "待审 / 已通过 / 已驳回、查看全文、通过 / 驳回", "审核记录写入 audit_record"],
              ["数据库", "图片存储", "头像、封面入库，重新登录仍可读取", "接口 /api/auth/avatar/{id}、/api/files/material/{id}"],
          ],
          [2.0, 2.6, 6.8, 5.4],
          "表 1-1  项目功能列表")

# ---------- 二、项目运行截图 ----------
h = heading(doc, "二、项目运行截图")
h.paragraph_format.page_break_before = True
body(doc, "以下截图由 Playwright 驱动 Edge 在本地完整运行环境中截取：后端 8080 端口、前端 5173 端口、"
          "MySQL 8.0.46；演示数据包含 17 个账号、25 篇文章与 14 个素材，截图为桌面端 1440×900 分辨率，共 14 张。")
shots = [
    ("01-media-login.png", "图 2-1  作者/审核员登录页"),
    ("02-register-role.png", "图 2-2  三端统一注册（角色选择）"),
    ("03-author-material.png", "图 2-3  作者素材管理"),
    ("04-author-uploaded.png", "图 2-4  上传封面图片（保存到数据库）"),
    ("05-publish-db-cover.png", "图 2-5  发布文章并使用数据库封面"),
    ("06-content-pending.png", "图 2-6  提交审核后的待审核列表"),
    ("07-audit-pending.png", "图 2-7  审核工作台"),
    ("08-audit-detail.png", "图 2-8  审核员查看稿件全文"),
    ("09-audit-passed.png", "图 2-9  审核通过后进入已通过列表"),
    ("10-reader-login.png", "图 2-10  普通用户密码登录"),
    ("11-reader-home.png", "图 2-11  用户端首页（封面来自数据库）"),
    ("12-reader-detail.png", "图 2-12  文章详情（封面从数据库读取）"),
    ("13-avatar-dialog.png", "图 2-13  上传头像对话框"),
    ("14-profile-avatar.png", "图 2-14  个人中心（头像已入库）"),
]
for f, c in shots:
    screenshot(doc, os.path.join(SHOTS, f), c, 14.0)

# ---------- 三、项目说明 ----------
h = heading(doc, "三、项目说明")
h.paragraph_format.page_break_before = True
heading(doc, "3.1  系统架构", 2)
body(doc, "系统采用前后端分离架构：浏览器加载 Vue 3 单页应用，通过 Axios 调用后端 REST 接口；"
          "后端按 Controller、Service、Mapper 分层，Spring 负责 Bean 管理与事务，Spring MVC 负责接口与拦截器，"
          "MyBatis-Plus 负责数据访问与分页，MyBatis XML 负责动态 SQL；MySQL 8.0 保存业务数据、头像与封面二进制。"
          "作者与审核员在 ap_user 统一账号基础上，通过 wm_user 建立业务身份，实现三端权限隔离。")

heading(doc, "3.2  Spring / SSM 组件及功能", 2)
body(doc, "项目使用的 Spring 组件及其作用如下表所示：")
add_table(doc,
          ["组件 / 技术", "应用位置", "功能说明"],
          [
              ["Spring IoC", "Controller、Service、Mapper", "构造器注入，统一管理 Bean，降低层间耦合"],
              ["Spring AOP", "aspect/LogAspect", "@Aspect、@Pointcut、@Around 统计控制器耗时并记录异常"],
              ["Spring MVC", "controller 包", "REST 接口、参数校验、全局异常、静态资源与拦截器"],
              ["声明式事务", "AuthService、MediaService、AuditService", "@Transactional 保证注册、发文、审核的一致性"],
              ["Spring MVC 拦截器", "interceptor/AuthInterceptor", "解析 JWT，按 userRole 拦截作者端与审核端接口"],
              ["文件上传", "AuthService、MediaService", "头像写入 ap_user.avatar_data，封面写入 material.data"],
              ["MyBatis-Plus", "Mapper、Service", "BaseMapper CRUD、分页插件、LambdaQueryWrapper"],
              ["MyBatis 动态 SQL", "resources/mapper/NewsMapper.xml", "where / if / choose 多条件查询，foreach 频道统计"],
          ],
          [3.4, 6.4, 6.8],
          "表 3-1  Spring 组件与功能说明", font_size=9.5, line=12)

heading(doc, "3.3  技术栈", 2)
add_table(doc,
          ["层次", "技术选型", "说明"],
          [
              ["后端", "SSM（Spring 5.3 + Spring MVC 5.3）", "REST 接口、IoC、AOP、事务、拦截器"],
              ["持久层", "MyBatis-Plus 3.5.3.2 / MyBatis 3.5.13", "CRUD、分页、动态 SQL"],
              ["数据库", "MySQL 8.0.46", "业务数据、头像与封面二进制"],
              ["前端", "Vue 3.4 + Vite 5 + Pinia", "单页应用、路由、状态管理"],
              ["UI", "Element Plus 2.8 + wangEditor 5", "后台组件库与富文本编辑器"],
              ["鉴权", "JWT 0.11.5 + BCrypt", "登录令牌与密码加密"],
              ["构建", "Maven 3.9 + Vite 5", "后端打包、前端构建"],
              ["运行环境", "JDK 17", "后端运行环境"],
          ],
          [2.8, 8.2, 5.0],
          "表 3-2  技术栈", font_size=9, line=11.5, header_size=10)

# ---------- 四、项目流程图 ----------
h = heading(doc, "四、项目流程图")
body(doc, "系统主流程分为作者、审核员、普通用户三条链路：作者上传封面并发布文章，提交审核；审核员查看全文，"
          "通过或驳回；通过后普通用户浏览文章，驳回后作者修改并重新提交。流程图如下：")
picture(doc, os.path.join(ASSETS, "flowchart.png"), "图 4-1  校园头条核心业务流程图", 13.8)
body(doc, "以“发布文章”为例：作者登录后上传封面（写入 material.data），在发布页填写标题、频道、标签与封面，"
          "提交审核后 news.status 变为 1；审核员在审核工作台查看全文，通过后 status 变为 2 并写入 publish_time，"
          "文章立即出现在用户端；驳回时 status 变为 3 并写入 audit_record，作者修改后可重新提交。")

# ---------- 五、数据表说明 ----------
h = heading(doc, "五、数据表说明")
h.paragraph_format.page_break_before = True
heading(doc, "5.1  数据表结构", 2)
body(doc, "系统共 9 张表，通过 12 个外键约束保证数据完整性，核心表如下：")
add_table(doc,
          ["表名", "说明", "主要字段", "关联关系"],
          [
              ["ap_user", "统一用户（普通/作者/审核员）", "phone、password、role、avatar_data、bio", "被 wm_user、评论、点赞引用"],
              ["wm_user", "作者/审核员业务身份", "ap_user_id、username、name、role", "关联 ap_user，被文章、素材、审核记录引用"],
              ["channel", "频道", "name、sort、status", "被 news 引用"],
              ["material", "素材/封面（图片入库）", "wm_user_id、url、data、content_type", "关联 wm_user，被 news_material 引用"],
              ["news", "文章", "wm_user_id、channel_id、title、cover_images、status", "关联作者与频道，被评论、点赞、审核记录引用"],
              ["news_material", "文章素材关联", "news_id、material_id、sort", "关联 news 与 material"],
              ["news_like", "点赞", "news_id、user_id", "关联 news 与 ap_user"],
              ["news_comment", "评论", "news_id、user_id、content", "关联 news 与 ap_user"],
              ["audit_record", "审核记录", "news_id、auditor_id、result、reason", "关联 news 与 wm_user"],
          ],
          [3.2, 4.6, 5.4, 3.4],
          "表 5-1  数据表说明")

heading(doc, "5.2  核心表 news 字段说明", 2)
add_table(doc,
          ["字段", "类型", "说明"],
          [
              ["id", "BIGINT", "主键，自增"],
              ["wm_user_id", "BIGINT", "作者，外键 wm_user.id"],
              ["channel_id", "INT", "频道，外键 channel.id"],
              ["title", "VARCHAR(60)", "文章标题"],
              ["content", "LONGTEXT", "正文 HTML"],
              ["cover_type", "TINYINT", "0 无图、1 单图、3 三图"],
              ["cover_images", "VARCHAR(1000)", "封面接口地址，逗号分隔"],
              ["labels", "VARCHAR(200)", "标签，逗号分隔"],
              ["status", "TINYINT", "0 草稿、1 待审核、2 通过、3 驳回"],
              ["publish_time", "DATETIME", "发布时间"],
              ["views / likes / comments", "INT", "阅读、点赞、评论计数"],
          ],
          [4.2, 3.2, 8.8],
          "表 5-2  news 表字段说明")

heading(doc, "5.3  E-R 关系图", 2)
picture(doc, os.path.join(ASSETS, "er.png"), "图 5-1  校园头条系统 E-R 图", 15.4)

# ---------- 六、核心代码说明 ----------
h = heading(doc, "六、核心代码说明")
body(doc, "下面选取 5 段核心代码，分别说明三端注册、封面入库、事务审核、AOP 日志与 MyBatis 动态 SQL 的实现。")

heading(doc, "6.1  注册与角色绑定", 2)
body(doc, "注册接口在一个事务中写入 ap_user，并根据 role 决定是否创建 wm_user；作者与审核员的业务身份通过 ap_user_id 关联，密码使用 BCrypt 加密。")
code_block(doc, "AuthService.java", open(os.path.join(ASSETS, "src", "register.txt"), encoding="utf-8").read(), "代码 6-1  注册与角色绑定")

heading(doc, "6.2  封面图片入库", 2)
body(doc, "上传接口读取 MultipartFile 字节数组，解析图片尺寸后写入 material.data，再把 url 设置为 /api/files/material/{id}，"
          "前端列表、发文页与用户端都通过该接口读取数据库中的图片。")
code_block(doc, "MediaService.java", open(os.path.join(ASSETS, "src", "upload.txt"), encoding="utf-8").read(), "代码 6-2  封面图片写入数据库")

heading(doc, "6.3  声明式事务审核", 2)
body(doc, "审核方法使用 @Transactional 将“更新文章状态”和“写入审核记录”放在同一事务中；通过时设置发布时间，驳回时要求填写意见，任意一步失败都会回滚。")
code_block(doc, "AuditService.java", open(os.path.join(ASSETS, "src", "audit.txt"), encoding="utf-8").read(), "代码 6-3  声明式事务审核")

heading(doc, "6.4  Spring AOP 日志切面", 2)
body(doc, "切面拦截 controller 包下所有 public 方法，使用 @Around 统计执行耗时并记录异常，体现 Spring AOP 与 IoC 的配合。")
code_block(doc, "LogAspect.java", open(os.path.join(ASSETS, "src", "aop.txt"), encoding="utf-8").read(), "代码 6-4  Spring AOP 日志切面")

heading(doc, "6.5  MyBatis 动态 SQL", 2)
body(doc, "XML 中使用 where、if、choose 完成作者内容列表与审核列表的多条件查询，并在频道统计中使用 foreach 批量统计，"
          "体现 MyBatis 动态 SQL 与 MyBatis-Plus 分页插件的结合。")
code_block(doc, "NewsMapper.xml", open(os.path.join(ASSETS, "src", "sql.txt"), encoding="utf-8").read(), "代码 6-5  MyBatis 动态 SQL")

# ---------- 七、项目总结 ----------
h = heading(doc, "七、项目总结")
h.paragraph_format.page_break_before = True
body(doc, "本项目完成了校园头条的三端业务闭环：普通用户浏览资讯并维护个人资料；作者管理素材、编辑文章、存草稿并提交审核；"
          "审核员在审核工作台查看全文，通过或驳回，并保留审核记录。系统采用 SSM 架构，完成了注册登录、JWT 鉴权、角色权限、"
          "素材管理、富文本发文、审核、文章浏览、点赞评论、头像上传与退出登录等功能。")
body(doc, "在技术层面，项目综合运用了 Spring IoC、Spring AOP、声明式事务、Spring MVC 拦截器、文件上传、MyBatis 动态 SQL "
          "与 MyBatis-Plus。尤其是将头像与新闻封面以 LONGBLOB 保存到数据库，解决了图片随本地目录丢失的问题；"
          "审核操作通过事务同时更新文章状态与审核记录，保证了数据一致性；三端统一账号通过 role 与 wm_user 关联实现权限隔离。")
body(doc, "实现过程中也遇到了一些问题：例如三端账号如何统一、作者与审核员如何共用一套登录体系、图片二进制如何返回给前端等。"
          "最终通过 ap_user + wm_user 的一对一关联、JWT 中携带 userRole 与 wmUserId、以及独立的图片读取接口解决了这些问题。")
body(doc, "系统仍有改进空间：审核员注册目前是开放的，实际部署时应增加邀请码或管理员审批；JWT 退出登录只清除客户端 token，"
          "服务端可引入 Redis 黑名单；图片以二进制存储在数据库中，数据量增大后可迁移到对象存储；后续还可以增加全文检索、"
          "消息通知与个性化推荐。")

# ---------- 八、提交材料清单 ----------
h = heading(doc, "八、提交材料清单")
add_table(doc,
          ["序号", "材料", "说明"],
          [
              ["1", "后端代码", "SSM 后端源码，含 pom.xml、src、mapper XML"],
              ["2", "前端代码", "Vue 3 + Element Plus 前端源码，含 package.json、src"],
              ["3", "数据库", "schema.sql、data.sql、campus_headlines.sql 及说明"],
              ["4", "部署文档", "校园头条部署文档.docx，含 DBeaver 连接与启动步骤"],
              ["5", "课程设计报告", "本文档"],
              ["6", "演示视频", "按课程要求由学委统一收集（本项目未额外录制）"],
          ],
          [2.0, 5.2, 8.8],
          "表 8-1  提交材料清单")

# ---------- 九、评分表 ----------
h = heading(doc, "九、评分表（教师使用）")
add_table(doc,
          ["评分项", "说明", "分值", "得分"],
          [
              ["功能实现", "注册登录、素材管理、资讯发布草稿、审核、资讯浏览；必做功能每缺一项扣对应分数", "40", ""],
              ["SSM 框架技术运用", "考察 Spring IoC/AOP、声明式事务、SpringMVC 拦截器、文件上传、MyBatis 动态 SQL、MyBatis-Plus 的使用情况", "25", ""],
              ["数据库设计合理性", "数据表设计、主外键、字段设计、SQL 脚本完整性", "15", ""],
              ["工程规范", "1. 代码格式规范、命名清晰、注释恰当；2. 项目文档完整，说明清晰", "10", ""],
              ["课程设计报告", "报告格式规范，截图齐全，分析总结完整", "10", ""],
              ["总分", "", "100", ""],
          ],
          [3.2, 9.2, 2.0, 2.0],
          "表 9-1  评分表")

# ---------- 十、评语 ----------
h = heading(doc, "十、评语（教师填写）")
for _ in range(7):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(12)
    set_run_font(p.add_run(" " * 4 + "_" * 72), "宋体", 12)

footer_page_numbers(doc)

doc.save(OUT)
shutil.copyfile(OUT, DESKTOP)
print("SAVED", OUT)
print("SAVED", DESKTOP)
print("paras", len(doc.paragraphs), "tables", len(doc.tables))
