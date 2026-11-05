# -*- coding: utf-8 -*-
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 3600, 2400
img = Image.new("RGB", (W, H), "#FFFFFF")
d = ImageDraw.Draw(img)

FONT = r"C:\Windows\Fonts\msyh.ttc"
FONT_B = r"C:\Windows\Fonts\msyhbd.ttc"
f_attr = ImageFont.truetype(FONT, 31)
f_attr_b = ImageFont.truetype(FONT_B, 31)
f_ent = ImageFont.truetype(FONT_B, 40)
f_rel = ImageFont.truetype(FONT_B, 34)
f_card = ImageFont.truetype(FONT_B, 32)
f_title = ImageFont.truetype(FONT_B, 62)
f_sub = ImageFont.truetype(FONT, 29)
f_leg = ImageFont.truetype(FONT, 29)
f_note = ImageFont.truetype(FONT, 25)

C_ENTITY_FILL = "#EAF2FF"
C_ENTITY_EDGE = "#1F4E9E"
C_ATTR_FILL = "#FFF8E1"
C_ATTR_EDGE = "#C58B1B"
C_REL_FILL = "#E9F8EF"
C_REL_EDGE = "#1E7A4D"
C_LINE = "#5B6B82"
C_TEXT = "#152238"
C_MUTED = "#5A6474"


def tw(s, font):
    return d.textlength(s, font=font)


def text(x, y, s, font, fill=C_TEXT, anchor="mm", bold=False):
    d.text((x, y), s, font=font, fill=fill, anchor=anchor)


def underline_text(x, y, s, font, fill=C_TEXT):
    d.text((x, y), s, font=font, fill=fill, anchor="mm")
    box = d.textbbox((x, y), s, font=font, anchor="mm")
    d.line([(box[0], box[3] + 3), (box[2], box[3] + 3)], fill=fill, width=3)


def entity(x, y, w, h, label):
    d.rounded_rectangle([x-w/2+9, y-h/2+9, x+w/2+9, y+h/2+9], radius=12, fill="#DCE6F5")
    d.rounded_rectangle([x-w/2, y-h/2, x+w/2, y+h/2], radius=12,
                        fill=C_ENTITY_FILL, outline=C_ENTITY_EDGE, width=4)
    text(x, y, label, f_ent, C_ENTITY_EDGE)


def attribute(x, y, s, pk=False):
    label = s + ("  (PK)" if pk else "")
    w = max(220, tw(label, f_attr) + 58)
    h = 62
    d.ellipse([x-w/2, y-h/2, x+w/2, y+h/2], fill=C_ATTR_FILL, outline=C_ATTR_EDGE, width=3)
    if pk:
        underline_text(x, y, label, f_attr)
    else:
        text(x, y, label, f_attr)


def diamond(cx, cy, label, rx=118, ry=62):
    pts = [(cx, cy-ry), (cx+rx, cy), (cx, cy+ry), (cx-rx, cy)]
    d.polygon(pts, fill=C_REL_FILL, outline=C_REL_EDGE, width=3)
    text(cx, cy, label, f_rel, C_REL_EDGE)


def line(p1, p2, width=3, color=C_LINE):
    d.line([p1, p2], fill=color, width=width)


def card(x, y, s):
    box = d.textbbox((x, y), s, font=f_card, anchor="mm")
    pad = 5
    d.rounded_rectangle([box[0]-pad, box[1]-pad, box[2]+pad, box[3]+pad], radius=5, fill="#FFFFFF")
    text(x, y, s, f_card, "#B3261E")


# 实体
U = (450, 1250); M = (1300, 480); A = (1900, 1150); C = (2850, 1900); S = (2750, 480)

attr_groups = [
    (U, [(230, 980, "用户ID", True), (140, 1170, "手机号", False),
         (150, 1370, "昵称", False), (260, 1570, "角色", False),
         (460, 1720, "密码", False), (680, 1740, "头像", False),
         (850, 1500, "简介", False)]),
    (M, [(1020, 240, "媒体ID", True), (1230, 190, "用户ID (FK)", False),
         (1450, 210, "名称", False), (1640, 300, "账号", False),
         (1720, 430, "角色", False), (1150, 360, "状态", False)]),
    (S, [(2700, 220, "素材ID", True), (2920, 190, "地址", False),
         (3120, 270, "类型", False), (3280, 400, "大小", False),
         (3320, 550, "图片数据", False), (3180, 680, "内容类型", False)]),
    (A, [(1900, 860, "文章ID", True), (2120, 900, "标题", False),
         (2330, 1030, "正文", False), (2380, 1180, "状态", False),
         (2130, 1460, "发布时间", False), (1900, 1540, "阅读量", False),
         (1660, 1380, "封面类型", False)]),
    (C, [(2850, 2110, "频道ID", True), (2600, 2200, "名称", False),
         (3070, 2200, "排序", False), (3270, 2070, "状态", False)]),
]

rels = {
    "拥有": (830, 820, 110, 56),
    "发布": (1560, 740, 110, 56),
    "审核": (1640, 950, 110, 56),
    "上传": (2000, 480, 110, 56),
    "使用": (2370, 780, 110, 56),
    "归类": (2420, 1560, 110, 56),
    "点赞": (1120, 1120, 110, 56),
    "评论": (1250, 1450, 110, 56),
}

rel_attrs = [
    ((2370, 780), [(2440, 620, "排序")]),
    ((1120, 1120), [(980, 1000, "点赞时间")]),
    ((1250, 1450), [(1000, 1660, "评论内容"), (1220, 1780, "评论时间")]),
]

# 1. 先画全部连线（随后用图形覆盖线头，视觉上从边框发散）
for (ex, ey), items in attr_groups:
    for x, y, label, pk in items:
        line((ex, ey), (x, y), 2, "#9AA8BD")

line((585, 1180), (830, 820)); line((830, 820), (1145, 545))
line((1450, 520), (1560, 740)); line((1560, 740), (1745, 1080))
line((1300, 550), (1450, 950)); line((1450, 950), (1530, 950)); line((1640, 950), (1740, 1120))
line((1465, 480), (2000, 480)); line((2000, 480), (2585, 480))
line((2050, 1090), (2370, 780)); line((2370, 780), (2615, 545))
line((2050, 1215), (2420, 1560)); line((2420, 1560), (2700, 1850))
line((600, 1250), (1120, 1120)); line((1120, 1120), (1730, 1120))
line((470, 1320), (1250, 1450)); line((1250, 1450), (1750, 1220))

for (rx, ry), items in rel_attrs:
    for x, y, label in items:
        line((rx, ry), (x, y), 2)

# 2. 实体与联系图形覆盖线头
entity(*U, 300, 140, "用户")
entity(*M, 330, 140, "媒体身份")
entity(*A, 340, 150, "文章")
entity(*C, 300, 140, "频道")
entity(*S, 330, 140, "素材")

for label, (x, y, rx, ry) in rels.items():
    diamond(x, y, label, rx, ry)

# 3. 联系属性
for (rx, ry), items in rel_attrs:
    for x, y, label in items:
        w = max(220, tw(label, f_attr) + 58)
        d.ellipse([x-w/2, y-31, x+w/2, y+31], fill=C_ATTR_FILL, outline=C_ATTR_EDGE, width=3)
        text(x, y, label, f_attr)

# 4. 实体属性
for (ex, ey), items in attr_groups:
    for x, y, label, pk in items:
        attribute(x, y, label, pk)

# 基数
pairs = [
    (690, 1080, "1"), (1040, 650, "N"),
    (1415, 640, "1"), (1700, 980, "N"),
    (1350, 780, "M"), (1600, 1100, "N"),
    (1900, 430, "1"), (2230, 430, "N"),
    (2240, 960, "M"), (2530, 630, "N"),
    (2180, 1300, "N"), (2580, 1700, "1"),
    (1010, 1185, "M"), (1370, 1075, "N"),
    (1050, 1360, "M"), (1450, 1335, "N"),
]
for x, y, s in pairs:
    card(x, y, s)

# 标题
text(W/2, 80, "校园头条系统  概念 E-R 图", f_title, "#11224A")
text(W/2, 132, "Chen 表示法：矩形 = 实体，椭圆 = 属性，菱形 = 联系", f_sub, C_MUTED)

# 图例
lx, ly = 110, 2130
d.rectangle([lx, ly-22, lx+82, ly+22], fill=C_ENTITY_FILL, outline=C_ENTITY_EDGE, width=3)
text(lx+100, ly, "实体", f_leg, C_TEXT, "lm")
d.ellipse([lx+202, ly-22, lx+298, ly+22], fill=C_ATTR_FILL, outline=C_ATTR_EDGE, width=3)
text(lx+315, ly, "属性", f_leg, C_TEXT, "lm")
d.polygon([(lx+470, ly-24), (lx+525, ly), (lx+470, ly+24), (lx+415, ly)], fill=C_REL_FILL, outline=C_REL_EDGE, width=3)
text(lx+540, ly, "联系", f_leg, C_TEXT, "lm")
text(lx+620, ly, "下划线 = 主键", f_leg, "#B3261E", "lm")

text(W-110, 2325, "说明：点赞、评论以联系属性表示；审核记录的结果、意见、时间等字段见数据表说明。",
     f_note, C_MUTED, "rm")

out = r"F:\IDEA\YXP-QM\campus-headlines\docs\概念E-R图.png"
img.save(out, "PNG", optimize=True)
print("SAVED", out, os.path.getsize(out), img.size)
