# -*- coding: utf-8 -*-
import os
from PIL import Image, ImageDraw, ImageFont

BASE = r"F:\IDEA\YXP-QM\campus-headlines"
OUT = os.path.join(BASE, "docs", "report_assets")
os.makedirs(OUT, exist_ok=True)

FONT = r"C:\Windows\Fonts\msyh.ttc"
FONT_B = r"C:\Windows\Fonts\msyhbd.ttc"
MONO = r"C:\Windows\Fonts\consola.ttf"

def font(size, bold=False):
    path = FONT_B if bold else FONT
    return ImageFont.truetype(path, size)

def center_text(draw, box, text, f, fill):
    x1, y1, x2, y2 = box
    lines = text.split("\n")
    heights = [draw.textbbox((0, 0), line, font=f)[3] for line in lines]
    total = sum(heights) + (len(lines) - 1) * 6
    y = y1 + (y2 - y1 - total) / 2
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=f)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        draw.text((x1 + (x2 - x1 - w) / 2, y - bbox[1]), line, font=f, fill=fill)
        y += h + 6

def box(draw, x, y, w, h, text, fill, border, f):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=12, fill=fill, outline=border, width=3)
    center_text(draw, (x, y, x + w, y + h), text, f, "#1f2430")

def arrow(draw, x1, y1, x2, y2, color="#5a6474", label=None, f=None, dashed=False):
    if dashed:
        # simple dashed line
        import math
        dist = math.hypot(x2 - x1, y2 - y1)
        steps = max(1, int(dist / 14))
        for i in range(steps):
            if i % 2 == 0:
                a = i / steps
                b = (i + 0.6) / steps
                draw.line([x1 + (x2 - x1) * a, y1 + (y2 - y1) * a,
                           x1 + (x2 - x1) * b, y1 + (y2 - y1) * b], fill=color, width=3)
    else:
        draw.line([x1, y1, x2, y2], fill=color, width=3)
    import math
    ang = math.atan2(y2 - y1, x2 - x1)
    size = 13
    p1 = (x2 - size * math.cos(ang - 0.45), y2 - size * math.sin(ang - 0.45))
    p2 = (x2 - size * math.cos(ang + 0.45), y2 - size * math.sin(ang + 0.45))
    draw.polygon([(x2, y2), p1, p2], fill=color)
    if label and f:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        draw.text((mx + 6, my - 18), label, font=f, fill="#5a6474")


def flowchart():
    img = Image.new("RGB", (1500, 900), "white")
    d = ImageDraw.Draw(img)
    f_title = font(34, True)
    f_box = font(21)
    f_small = font(18)
    d.text((60, 40), "校园头条核心业务流程图", font=f_title, fill="#1f3a7a")
    d.line([60, 92, 1440, 92], fill="#2f6bff", width=4)

    blue = ("#eef3ff", "#2f6bff")
    orange = ("#fff7e6", "#f59e0b")
    green = ("#e9f9ef", "#22c55e")
    red = ("#fdecec", "#ef4444")

    box(d, 80, 130, 300, 82, "作者注册 / 登录\n（手机号 + 密码）", *blue, f_box)
    box(d, 80, 260, 300, 82, "上传封面图片\n保存到 material.data", *blue, f_box)
    box(d, 80, 390, 300, 82, "撰写文章 / 选择封面\n存草稿或提交审核", *blue, f_box)
    box(d, 80, 520, 300, 82, "提交审核\nnews.status = 1", *blue, f_box)

    box(d, 500, 130, 300, 82, "审核员注册 / 登录\n（role = 2）", *orange, f_box)
    box(d, 500, 300, 300, 82, "审核工作台\n查看全文 / 审核记录", *orange, f_box)

    # diamond
    cx, cy = 760, 520
    pts = [(cx, cy - 70), (cx + 110, cy), (cx, cy + 70), (cx - 110, cy)]
    d.polygon(pts, fill="white", outline="#f59e0b", width=3)
    center_text(d, (cx - 80, cy - 45, cx + 80, cy + 45), "审核\n通过？", f_small, "#1f2430")

    box(d, 1010, 430, 320, 82, "通过并发布\nstatus = 2，写入发布时间", *green, f_box)
    box(d, 1010, 620, 320, 82, "驳回并填写意见\nstatus = 3 + audit_record", *red, f_box)
    box(d, 1010, 130, 320, 82, "普通用户浏览\n首页 / 频道 / 文章详情", *green, f_box)
    box(d, 1010, 270, 320, 82, "封面从数据库读取\n/api/files/material/{id}", *green, f_box)

    arrow(d, 230, 212, 230, 260, label="", f=f_small)
    arrow(d, 230, 342, 230, 390, label="", f=f_small)
    arrow(d, 230, 472, 230, 520, label="", f=f_small)
    arrow(d, 380, 561, 500, 360, label="提交审核", f=f_small)
    arrow(d, 650, 212, 650, 300, label="", f=f_small)
    arrow(d, 650, 382, 720, 455, label="", f=f_small)
    arrow(d, 870, 500, 1010, 470, label="是", f=f_small)
    arrow(d, 760, 590, 1010, 660, label="否", f=f_small)
    arrow(d, 1170, 620, 1170, 540, label="", f=f_small)  # not ideal
    # 驳回后修改重提：沿底部折线
    for a, b in [((1170, 702), (1170, 790)), ((1170, 790), (230, 790)), ((230, 790), (230, 606))]:
        d.line([a, b], fill="#5a6474", width=3)
    d.polygon([(230, 604), (223, 620), (237, 620)], fill="#5a6474")
    d.text((560, 798), "修改后重新提交", font=f_small, fill="#5a6474")
    arrow(d, 1010, 430, 1010, 352, label="", f=f_small)
    arrow(d, 1010, 270, 1010, 212, label="", f=f_small)

    d.text((60, 840), "说明：作者发布、审核员审核、普通用户浏览三端分离；封面与头像均从 MySQL 读取。", font=f_small, fill="#5a6474")
    img.save(os.path.join(OUT, "flowchart.png"))
    print("flowchart saved")


def er():
    img = Image.new("RGB", (1600, 1100), "white")
    d = ImageDraw.Draw(img)
    f_title = font(32, True)
    f_name = font(20, True)
    f_field = font(15)
    d.text((50, 30), "校园头条系统 E-R 图", font=f_title, fill="#1f3a7a")
    d.line([50, 78, 1550, 78], fill="#2f6bff", width=4)

    def entity(x, y, name, fields, color="#eef3ff", border="#2f6bff"):
        w, h = 260, 40 + 26 * len(fields)
        d.rounded_rectangle([x, y, x + w, y + h], radius=10, fill=color, outline=border, width=3)
        d.rectangle([x, y, x + w, y + 38], fill=border)
        d.text((x + 12, y + 8), name, font=f_name, fill="white")
        for i, field in enumerate(fields):
            d.text((x + 12, y + 48 + i * 26), field, font=f_field, fill="#1f2430")
        return (x, y, x + w, y + h)

    ap = entity(60, 120, "ap_user 用户", ["PK id", "phone 唯一", "password", "role 0/1/2", "avatar_data BLOB"])
    wm = entity(400, 120, "wm_user 作者/审核员", ["PK id", "FK ap_user_id", "username", "role 0/1", "name"])
    news = entity(760, 120, "news 文章", ["PK id", "FK wm_user_id", "FK channel_id", "title / content", "cover_images", "status 0-3"])
    mat = entity(1120, 120, "material 素材", ["PK id", "FK wm_user_id", "url", "data BLOB", "content_type"])
    ch = entity(760, 470, "channel 频道", ["PK id", "name 唯一", "sort", "status"])
    nm = entity(1120, 470, "news_material", ["PK id", "FK news_id", "FK material_id", "sort"])
    like = entity(60, 470, "news_like 点赞", ["PK id", "FK news_id", "FK user_id"])
    com = entity(60, 780, "news_comment 评论", ["PK id", "FK news_id", "FK user_id", "content"])
    audit = entity(760, 800, "audit_record 审核", ["PK id", "FK news_id", "FK auditor_id", "result / reason"])

    def line(p1, p2, label, color="#5a6474"):
        d.line([p1, p2], fill=color, width=3)
        mx, my = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
        d.text((mx + 4, my - 22), label, font=f_field, fill=color)

    line((320, 180), (400, 180), "1 : 0..1")
    line((660, 180), (760, 180), "1 : N")
    d.line([(530, 120), (530, 95), (1250, 95), (1250, 120)], fill="#5a6474", width=3)
    d.text((880, 72), "1 : N", font=f_field, fill="#5a6474")
    line((890, 300), (890, 470), "1 : N")
    line((1020, 300), (1250, 470), "1 : N")
    line((1250, 300), (1250, 470), "1 : N")
    line((160, 300), (160, 470), "1 : N")
    line((760, 300), (320, 500), "N : 1")
    d.line([(350, 300), (350, 720), (320, 720), (320, 780)], fill="#5a6474", width=3)
    d.text((356, 520), "1 : N", font=f_field, fill="#5a6474")
    d.line([(730, 300), (730, 760), (850, 760), (850, 800)], fill="#98a2b3", width=3)
    d.text((676, 530), "1 : N", font=f_field, fill="#98a2b3")
    line((530, 300), (760, 840), "1 : N", "#98a2b3")

    d.text((50, 1040), "说明：ap_user 与 wm_user 一对一（作者/审核员）；文章、素材、评论、点赞、审核记录均通过外键关联。",
           font=f_field, fill="#5a6474")
    img.save(os.path.join(OUT, "er.png"))
    print("er saved")


def code_image(filename, title, lines, width=1280):
    f_num = ImageFont.truetype(MONO, 16)
    f_code = ImageFont.truetype(MONO, 20)
    f_cn = ImageFont.truetype(FONT, 19)
    f_title = ImageFont.truetype(FONT, 16)
    line_h = 30
    height = 70 + line_h * len(lines) + 30
    img = Image.new("RGB", (width, height), "#f7f9fc")
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, width, 52], fill="#1f2430")
    d.text((24, 14), title, font=f_title, fill="#cdd5e4")
    d.ellipse([width - 84, 18, width - 70, 32], fill="#ef4444")
    d.ellipse([width - 62, 18, width - 48, 32], fill="#f59e0b")
    d.ellipse([width - 40, 18, width - 26, 32], fill="#22c55e")
    y = 72
    for i, line in enumerate(lines, 1):
        d.text((18, y), str(i).rjust(3), font=f_num, fill="#98a2b3")
        color = "#1f2430"
        stripped = line.strip()
        if stripped.startswith("//") or stripped.startswith("<!--") or stripped.startswith("*"):
            color = "#16a34a"
        elif stripped.startswith("@"):
            color = "#b45309"
        use_cn = any(ord(ch) > 127 for ch in line)
        d.text((66, y), line, font=f_cn if use_cn else f_code, fill=color)
        y += line_h
    img.save(os.path.join(OUT, filename))
    print("code saved", filename)


flowchart()
er()

for filename, title, src in [
    ("code-register.png", "AuthService.java  ·  注册与角色绑定", "register.txt"),
    ("code-upload.png", "MediaService.java  ·  封面图片写入数据库", "upload.txt"),
    ("code-audit.png", "AuditService.java  ·  声明式事务审核", "audit.txt"),
    ("code-aop.png", "LogAspect.java  ·  Spring AOP 日志切面", "aop.txt"),
    ("code-sql.png", "NewsMapper.xml  ·  MyBatis 动态 SQL", "sql.txt"),
]:
    with open(os.path.join(OUT, "src", src), encoding="utf-8") as fh:
        code_image(filename, title, fh.read().splitlines())

print("ALL DONE")
