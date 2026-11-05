# -*- coding: utf-8 -*-
import os
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
OUT_DESKTOP = r"C:\Users\admin\Desktop\《J2EE应用开发》课程设计报告（俞鑫培）.docx"
OUT_DOCS = os.path.join(BASE, "docs", "《J2EE应用开发》课程设计报告（俞鑫培）.docx")

NAME = "俞鑫培"
STUDENT_ID = "122512023064"


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
    rFonts.set(qn("w:eastAsia"), name)


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
    # header bottom border
    for cell in table.rows[0].cells:
        tcPr = cell._tc.get_or_add_tcPr()
        tcBorders = OxmlElement("w:tcBorders")
        bottom = OxmlElement("w:bottom")
        bottom.set(qn("w:val"), "single")
        bottom.set(qn("w:sz"), "8")
        bottom.set(qn("w:color"), "000000")
        tcBorders.append(bottom)
        tcPr.append(tcBorders)


def add_table(doc, headers, rows, widths):
    table = doc.add_table(rows=1, cols=len(headers))
    three_line(table, widths)
    header_trPr = table.rows[0]._tr.get_or_add_trPr()
    header_flag = OxmlElement("w:tblHeader")
    header_trPr.append(header_flag)
    for row in table.rows:
        trPr = row._tr.get_or_add_trPr()
        trPr.append(OxmlElement("w:cantSplit"))
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = ""
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.line_spacing = Pt(15)
        snap_off(p)
        run = p.add_run(h)
        set_run_font(run, "宋体", 10.5, True)
    for row in rows:
        cells = table.add_row().cells
        for i, value in enumerate(row):
            cells[i].text = ""
            p = cells[i].paragraphs[0]
            p.paragraph_format.space_after = Pt(1)
            p.paragraph_format.line_spacing = Pt(14)
            snap_off(p)
            run = p.add_run(str(value))
            set_run_font(run, "宋体", 10)
    for row in table.rows[:-1]:
        for cell in row.cells:
            for para in cell.paragraphs:
                para.paragraph_format.keep_with_next = True
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return table


def heading(doc, text, level=1):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(16 if level == 1 else 10)
    p.paragraph_format.space_after = Pt(8)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    set_run_font(run, "黑体", 15 if level == 1 else 12.5, True)
    return p


def body(doc, text, indent=True, align=None, size=12):
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = Pt(22)
    p.paragraph_format.space_after = Pt(6)
    snap_off(p)
    if indent:
        p.paragraph_format.first_line_indent = Pt(size * 2)
    if align:
        p.alignment = align
    run = p.add_run(text)
    set_run_font(run, "宋体", size)
    return p


def caption(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(10)
    run = p.add_run(text)
    set_run_font(run, "宋体", 9, False, (0x5A, 0x64, 0x74))


def picture(doc, path, cap, width=15.2):
    if not os.path.exists(path):
        print("MISSING", path)
        return
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4)
    run = p.add_run()
    run.add_picture(path, width=Cm(width))
    caption(doc, cap)


def image_grid(doc, items, cols=2, width=6.1):
    rows = (len(items) + cols - 1) // cols
    table = doc.add_table(rows=rows, cols=cols)
    no_borders(table)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for row in table.rows:
        trPr = row._tr.get_or_add_trPr()
        cant = OxmlElement("w:cantSplit")
        trPr.append(cant)
    for idx, (path, cap) in enumerate(items):
        cell = table.cell(idx // cols, idx % cols)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if os.path.exists(path):
            p.add_run().add_picture(path, width=Cm(width))
        cp = cell.add_paragraph()
        cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = cp.add_run(cap)
        set_run_font(run, "宋体", 9, False, (0x5A, 0x64, 0x74))
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def footer_page_numbers(doc):
    section = doc.sections[0]
    p = section.footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("第 ")
    set_run_font(run, "宋体", 9, False, (0x5A, 0x64, 0x74))
    run2 = p.add_run()
    fld1 = OxmlElement("w:fldChar"); fld1.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText"); instr.set(qn("xml:space"), "preserve"); instr.text = "PAGE"
    fld2 = OxmlElement("w:fldChar"); fld2.set(qn("w:fldCharType"), "end")
    run2._r.append(fld1); run2._r.append(instr); run2._r.append(fld2)
    set_run_font(run2, "宋体", 9, False, (0x5A, 0x64, 0x74))
    run3 = p.add_run(" 页")
    set_run_font(run3, "宋体", 9, False, (0x5A, 0x64, 0x74))


doc = Document(TEMPLATE)

# ---- 封面信息 ----
cover = doc.tables[0]
cover.cell(3, 2).text = ""
cover.cell(3, 2).paragraphs[0].add_run(STUDENT_ID)
cover.cell(4, 2).text = ""
cover.cell(4, 2).paragraphs[0].add_run(NAME)
for r in (3, 4):
    for run in cover.cell(r, 2).paragraphs[0].runs:
        set_run_font(run, "宋体", 12)

# 项目名称放在学年下方空白段落
p4 = doc.paragraphs[4]
p4.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p4.add_run("项目名称：校园头条系统（Campus Headlines）")
set_run_font(run, "宋体", 15, True)

# ---- 删除模板正文，保留封面 ----
for p in list(doc.paragraphs[7:]):
    p._element.getparent().remove(p._element)
if len(doc.tables) > 1:
    tbl = doc.tables[1]._element
    tbl.getparent().remove(tbl)


# 去掉模板封面可能残留的分页符，避免出现空白页
for para in doc.paragraphs[:7]:
    for br in list(para._p.iter(qn("w:br"))):
        if br.get(qn("w:type")) == "page":
            br.getparent().remove(br)
    para.paragraph_format.page_break_before = False

# 基础样式
normal = doc.styles["Normal"]
normal.font.name = "宋体"
normal.font.size = Pt(12)
normal.element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")

# ================= 一、项目功能列表 =================
h = heading(doc, "一、项目功能列表")
h.paragraph_format.page_break_before = True
body(doc, "校园头条系统采用 SSM（Spring + Spring MVC + MyBatis-Plus）架构，前端使用 Vue 3 与 Element Plus，"
          "数据库使用 MySQL 8.0。系统面向校园资讯场景，设置普通用户、作者、审核员三种角色，"
          "形成“作者生产内容—审核员审核—普通用户浏览”的完整闭环。")
add_table(doc,
          ["端 / 角色", "功能模块", "功能说明"],
          [
              ["公共", "注册 / 登录", "三端统一账号，注册时选择普通用户 / 作者 / 审核员；支持验证码登录与密码登录"],
              ["普通用户", "资讯浏览", "频道切换、关键词搜索、头条推荐、文章列表、文章详情"],
              ["普通用户", "个人中心", "修改昵称、性别、个人简介；上传头像并保存到数据库；退出登录"],
              ["作者", "素材管理", "上传新闻封面图片（二进制保存到数据库）、收藏、删除、分页"],
              ["作者", "发布文章", "富文本编辑、标签、频道、单图/三图/无图封面、存草稿、提交审核"],
              ["作者", "内容列表", "按状态、关键词、频道、日期筛选自己的文章，支持编辑与删除"],
              ["审核员", "审核工作台", "查看待审核稿件全文，通过并发布或驳回并填写审核意见，记录审核历史"],
              ["数据库", "图片存储", "头像存 ap_user.avatar_data，封面/素材存 material.data，重新登录仍可读取"],
          ],
          [3.2, 3.6, 10.0])

body(doc, "三端账号共用 ap_user 表，通过 role 字段区分：0 为普通用户、1 为作者、2 为审核员。"
          "作者和审核员在 wm_user 表中拥有对应的业务身份，用于文章、素材和审核记录的外键关联。")

# ================= 二、项目运行截图 =================
h = heading(doc, "二、项目运行截图")
h.paragraph_format.page_break_before = True
body(doc, "以下截图由 Playwright 驱动真实浏览器完成注册、发布、审核、浏览、头像上传等操作后自动截取，"
          "覆盖桌面端 1440×900 与移动端 390×844。")
shots = [
    ("02-register-role.png", "图 2-1  三端统一注册（角色选择）"),
    ("03-author-material.png", "图 2-2  作者素材管理"),
    ("04-author-uploaded.png", "图 2-3  上传封面图片（保存到数据库）"),
    ("05-publish-db-cover.png", "图 2-4  作者发布文章并使用数据库封面"),
    ("06-content-pending.png", "图 2-5  提交审核后的待审核列表"),
    ("07-audit-pending.png", "图 2-6  审核工作台（待审核）"),
    ("08-audit-detail.png", "图 2-7  审核员查看稿件全文"),
    ("09-audit-passed.png", "图 2-8  审核通过后进入已通过列表"),
    ("11-reader-home.png", "图 2-9  普通用户首页（封面来自数据库）"),
    ("12-reader-detail.png", "图 2-10  文章详情（封面从数据库读取）"),
    ("13-avatar-dialog.png", "图 2-11  上传头像对话框"),
    ("14-profile-avatar.png", "图 2-12  头像保存到数据库后的个人中心"),
]
image_grid(doc, [(os.path.join(SHOTS, f), c) for f, c in shots], cols=2, width=6.1)

# ================= 三、项目说明 =================
h = heading(doc, "三、项目说明")
h.paragraph_format.page_break_before = True
heading(doc, "3.1  总体架构", 2)
body(doc, "系统采用前后端分离架构。后端以 SSM 为核心：Spring 负责 Bean 管理与依赖注入，Spring MVC 负责"
          "REST 接口与拦截器，MyBatis-Plus 负责数据访问与分页，MyBatis XML 负责复杂动态 SQL；MySQL 8.0 "
          "保存业务数据、头像二进制和封面二进制。前端使用 Vue 3、Vue Router、Pinia、Element Plus 与 wangEditor，"
          "通过 Axios 调用后端接口。")

heading(doc, "3.2  Spring / SSM 组件及功能", 2)
add_table(doc,
          ["组件", "功能说明", "项目中的体现"],
          [
              ["Spring IoC", "统一管理 Controller、Service、Mapper 等 Bean，使用构造器注入降低耦合", "各层使用 @RestController、@Service、@Mapper 与 @RequiredArgsConstructor"],
              ["Spring AOP", "对控制器方法做统一日志与耗时统计，异常时记录告警", "aspect/LogAspect.java 使用 @Aspect、@Pointcut、@Around"],
              ["Spring MVC", "提供 REST 接口、参数校验、统一异常处理、静态资源与拦截器", "controller 包、GlobalExceptionHandler、WebMvcConfig"],
              ["声明式事务", "保证注册、发文、点赞、评论、审核等操作的数据一致性", "AuthService、MediaService、AuditService 上的 @Transactional"],
              ["Spring MVC 拦截器", "解析 JWT、写入用户上下文、按角色拦截作者端与审核端接口", "interceptor/AuthInterceptor.java"],
              ["文件上传", "接收 MultipartFile，将头像/封面二进制写入数据库", "AuthService.uploadAvatar、MediaService.upload"],
              ["MyBatis-Plus", "通用 CRUD、分页插件、LambdaQueryWrapper、逻辑删除", "各 Mapper 继承 BaseMapper，配置 PaginationInnerInterceptor"],
              ["MyBatis 动态 SQL", "按状态、关键词、频道、日期动态拼接 SQL，支持排序切换", "resources/mapper/NewsMapper.xml 的 where/if/choose/foreach"],
          ],
          [3.0, 8.0, 5.8])

h = heading(doc, "3.3  三端权限设计", 2)
h.paragraph_format.page_break_before = True
add_table(doc,
          ["角色", "role", "可访问功能", "登录入口"],
          [
              ["普通用户", "0", "浏览频道、列表、详情；修改资料；上传头像", "/login"],
              ["作者", "1", "素材管理、发布文章、存草稿、提交审核、内容列表", "/media/login"],
              ["审核员", "2", "审核工作台、查看全文、通过/驳回、审核记录", "/media/login"],
          ],
          [3.0, 2.0, 8.6, 3.2])
body(doc, "权限在后端与前端双重控制：后端拦截器校验 JWT 与 userRole，Service 层再次校验作者/审核员身份；"
          "前端根据登录返回的 userRole 与 accountRole 渲染菜单，并通过路由守卫限制越权访问。")

heading(doc, "3.4  头像与封面入库", 2)
body(doc, "为满足“图片保存到数据库、下次登录仍可查看”的要求，系统不再依赖本地图片目录："
          "用户头像通过 POST /api/auth/avatar 上传，二进制写入 ap_user.avatar_data，并记录 avatar_type；"
          "头像通过 GET /api/auth/avatar/{id} 读取。作者上传的封面通过 POST /api/media/materials 上传，"
          "二进制写入 material.data，接口地址为 /api/files/material/{id}；文章 cover_images 保存该地址，"
          "用户端、作者端、审核端都从数据库读取同一张图片。")

heading(doc, "3.5  安全设计", 2)
body(doc, "用户密码使用 BCrypt 加密存储；登录成功后签发 JWT，token 中携带 ap_user.id、userRole 与 wmUserId；"
          "拦截器统一解析 token 并写入 ThreadLocal 用户上下文；作者只能管理自己的文章与素材，审核员只能审核，"
          "普通用户不能进入创作端。")

# ================= 四、项目流程图 =================
h = heading(doc, "四、项目流程图")
h.paragraph_format.page_break_before = True
body(doc, "核心业务流程为：作者上传封面并发布文章 → 提交审核 → 审核员查看全文 → 通过或驳回 → "
          "通过后普通用户浏览；驳回后作者修改并重新提交。流程图如下：")
picture(doc, os.path.join(ASSETS, "flowchart.png"), "图 4-1  校园头条核心业务流程图", 15.6)
body(doc, "流程说明：作者与审核员分别注册登录；封面图片先写入 material.data；文章提交后 status 变为 1；"
          "审核通过后 status 变为 2 并写入 publish_time，文章立即出现在普通用户端；驳回时 status 变为 3，"
          "同时写入 audit_record，作者可根据审核意见修改后重新提交。")

# ================= 五、数据表说明 =================
h = heading(doc, "五、数据表说明")
h.paragraph_format.page_break_before = True
body(doc, "系统共 9 张表，核心表之间通过 12 个外键约束保证数据完整性。E-R 图如下：")
picture(doc, os.path.join(ASSETS, "er.png"), "图 5-1  校园头条系统 E-R 图", 15.6)
body(doc, "其余表：channel（频道）、news_material（文章素材关联）、news_like（点赞）、news_comment（评论）、"
          "audit_record（审核记录）。外键关系包括：news.wm_user_id、news.channel_id、material.wm_user_id、"
          "news_material.news_id/material_id、news_like.news_id/user_id、news_comment.news_id/user_id、"
          "audit_record.news_id/auditor_id、wm_user.ap_user_id。")


heading(doc, "5.1  ap_user（统一用户表）", 2)
add_table(doc,
          ["字段", "类型", "说明"],
          [
              ["id", "BIGINT", "主键，自增"],
              ["phone", "VARCHAR(11)", "手机号，唯一索引，登录名"],
              ["password", "VARCHAR(100)", "BCrypt 密码"],
              ["nickname", "VARCHAR(32)", "昵称"],
              ["role", "TINYINT", "0 普通用户，1 作者，2 审核员"],
              ["avatar", "VARCHAR(255)", "头像地址（预设或数据库接口）"],
              ["avatar_data", "LONGBLOB", "上传头像的二进制数据"],
              ["avatar_type", "VARCHAR(50)", "头像 MIME 类型"],
              ["bio", "VARCHAR(200)", "个人简介"],
              ["gender", "TINYINT", "0 未知，1 男，2 女"],
              ["status", "TINYINT", "1 正常，0 禁用"],
          ],
          [3.4, 3.0, 9.8])

heading(doc, "5.2  wm_user（作者/审核员表）", 2)
add_table(doc,
          ["字段", "类型", "说明"],
          [
              ["id", "BIGINT", "主键"],
              ["ap_user_id", "BIGINT", "外键，关联 ap_user.id，唯一"],
              ["username", "VARCHAR(32)", "登录名（默认手机号），唯一"],
              ["password", "VARCHAR(100)", "BCrypt 密码"],
              ["name", "VARCHAR(32)", "媒体号名称"],
              ["role", "TINYINT", "0 作者，1 审核员"],
              ["status", "TINYINT", "1 正常，0 禁用"],
          ],
          [3.4, 3.0, 9.8])

heading(doc, "5.3  material（素材/封面表）", 2)
add_table(doc,
          ["字段", "类型", "说明"],
          [
              ["id", "BIGINT", "主键"],
              ["wm_user_id", "BIGINT", "外键，所属作者"],
              ["url", "VARCHAR(255)", "访问地址（/api/files/material/{id}）"],
              ["type", "TINYINT", "0 图片，1 视频"],
              ["size", "BIGINT", "字节数"],
              ["content_type", "VARCHAR(50)", "MIME 类型"],
              ["original_name", "VARCHAR(255)", "原始文件名"],
              ["data", "LONGBLOB", "图片二进制数据"],
              ["is_collected", "TINYINT", "0 未收藏，1 已收藏"],
          ],
          [3.4, 3.0, 9.8])

heading(doc, "5.4  news（文章表）", 2)
add_table(doc,
          ["字段", "类型", "说明"],
          [
              ["id", "BIGINT", "主键"],
              ["wm_user_id", "BIGINT", "外键，作者"],
              ["channel_id", "INT", "外键，频道"],
              ["title", "VARCHAR(60)", "标题"],
              ["content", "LONGTEXT", "正文 HTML"],
              ["cover_type", "TINYINT", "0 无图，1 单图，3 三图"],
              ["cover_images", "VARCHAR(1000)", "封面接口地址，逗号分隔"],
              ["status", "TINYINT", "0 草稿，1 待审核，2 通过，3 驳回"],
              ["publish_time", "DATETIME", "发布时间"],
              ["views / likes / comments", "INT", "阅读、点赞、评论计数"],
          ],
          [4.0, 3.2, 9.0])



# ================= 六、核心代码说明 =================
h = heading(doc, "六、核心代码说明")
h.paragraph_format.page_break_before = True
body(doc, "下面选取 5 段核心代码，分别说明三端注册、封面入库、事务审核、AOP 日志与 MyBatis 动态 SQL 的实现。")

picture(doc, os.path.join(ASSETS, "code-register.png"), "图 6-1  注册与角色绑定（AuthService）", 15.4)
body(doc, "注册接口在一个事务中写入 ap_user，并根据 role 决定是否创建 wm_user；作者与审核员的业务身份"
          "通过 ap_user_id 与统一账号关联，密码使用 BCrypt 加密。")

picture(doc, os.path.join(ASSETS, "code-upload.png"), "图 6-2  封面图片写入数据库（MediaService）", 15.4)
body(doc, "上传接口读取 MultipartFile 字节数组，解析图片尺寸后写入 material.data，再把 url 设置为"
          "/api/files/material/{id}，前端列表、发文页与用户端都通过该接口读取数据库中的图片。")

picture(doc, os.path.join(ASSETS, "code-audit.png"), "图 6-3  声明式事务审核（AuditService）", 15.4)
body(doc, "审核方法使用 @Transactional 将“更新文章状态”和“写入审核记录”放在同一事务中；通过时设置发布时间，"
          "驳回时要求填写意见，任意一步失败都会回滚。")

picture(doc, os.path.join(ASSETS, "code-aop.png"), "图 6-4  Spring AOP 日志切面（LogAspect）", 15.4)
body(doc, "切面拦截 controller 包下所有 public 方法，使用 @Around 统计执行耗时并记录异常，"
          "体现 Spring AOP 与 IoC 的配合。")

picture(doc, os.path.join(ASSETS, "code-sql.png"), "图 6-5  MyBatis 动态 SQL（NewsMapper.xml）", 15.4)
body(doc, "XML 中使用 where、if、choose 完成作者内容列表与审核列表的多条件查询，"
          "并在频道统计中使用 foreach 批量统计，体现 MyBatis 动态 SQL 与 MyBatis-Plus 分页插件的结合。")

# ================= 七、项目总结 =================
h = heading(doc, "七、项目总结")
h.paragraph_format.page_break_before = True
body(doc, "本次课程设计完成了校园头条系统的三端功能：普通用户浏览资讯、作者发布并提交审核、审核员审核稿件。"
          "系统采用 SSM 架构，完成了注册登录、JWT 鉴权、角色权限、素材管理、富文本发文、草稿与审核、"
          "文章浏览、点赞评论、个人资料修改、头像上传、退出登录等功能。")
body(doc, "在技术层面，项目综合运用了 Spring IoC、Spring AOP、声明式事务、Spring MVC 拦截器、文件上传、"
          "MyBatis 动态 SQL 与 MyBatis-Plus。尤其是将头像与新闻封面以 LONGBLOB 保存到数据库，"
          "解决了图片随本地目录丢失的问题；审核操作通过事务同时更新文章状态与审核记录，保证了数据一致性。")
body(doc, "实现过程中也遇到了一些问题：例如三端账号如何统一、作者与审核员如何共用一套登录体系、"
          "图片二进制如何返回给前端等。最终通过 ap_user + wm_user 的一对一关联、JWT 中携带 userRole 与 "
          "wmUserId、以及独立的图片读取接口解决了这些问题。")
body(doc, "系统仍有改进空间：审核员注册目前是开放的，实际部署时应增加邀请码或管理员审批；"
          "JWT 退出登录只清除客户端 token，服务端可引入 Redis 黑名单；图片二进制存储在数据库中，"
          "数据量增大后可迁移到对象存储；后续还可以增加全文检索、消息通知与个性化推荐。")

# ================= 八、提交材料清单 =================
h = heading(doc, "八、提交材料清单")
h.paragraph_format.page_break_before = True
for line in [
    "1. 项目源代码（前端代码、后端代码、数据库 SQL）。",
    "2. 数据库脚本与备份（schema.sql、data.sql、campus_headlines.sql）。",
    "3. 项目部署文档（docx，含 DBeaver 连接与启动步骤）。",
    "4. 课程设计报告（本文档）。",
    "5. 演示视频按课程要求由学委统一收集（本项目未额外录制）。",
]:
    body(doc, line, indent=False)

# ================= 九、评分表 =================
h = heading(doc, "九、评分表（教师使用）")
h.paragraph_format.page_break_before = True
score_rows = [
    ["功能实现", "注册登录、素材管理、资讯发布草稿、审核、资讯浏览；必做功能每缺一项扣对应分数", "40", ""],
    ["SSM 框架技术运用", "考察 Spring IoC/AOP、声明式事务、SpringMVC 拦截器、文件上传、MyBatis 动态 SQL、MyBatis-Plus 的使用情况", "25", ""],
    ["数据库设计合理性", "数据表设计、主外键、字段设计、SQL 脚本完整性", "15", ""],
    ["工程规范", "1. 代码格式规范、命名清晰、注释恰当；2. 项目文档完整，说明清晰", "10", ""],
    ["课程设计报告", "报告格式规范，截图齐全，分析总结完整", "10", ""],
    ["总分", "", "100", ""],
]
add_table(doc, ["评分项", "说明", "分值", "得分"], score_rows, [3.2, 9.4, 2.0, 2.0])
heading(doc, "评语（教师填写）", 2)
for _ in range(6):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(10)
    run = p.add_run(" " * 4 + "_" * 70)
    set_run_font(run, "宋体", 12)

footer_page_numbers(doc)

os.makedirs(os.path.dirname(OUT_DOCS), exist_ok=True)
doc.save(OUT_DOCS)
import shutil
shutil.copyfile(OUT_DOCS, OUT_DESKTOP)
print("SAVED", OUT_DOCS)
print("SAVED", OUT_DESKTOP)
print("paragraphs", len(doc.paragraphs), "tables", len(doc.tables))
