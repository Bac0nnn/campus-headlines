# -*- coding: utf-8 -*-
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 2000, 1500
img = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(img)

FONT = r"C:\Windows\Fonts\msyh.ttc"
FONT_B = r"C:\Windows\Fonts\msyhbd.ttc"
f_attr = ImageFont.truetype(FONT, 32)
f_ent = ImageFont.truetype(FONT_B, 38)
f_rel = ImageFont.truetype(FONT, 31)
f_card = ImageFont.truetype(FONT_B, 28)

BLACK = "#111111"


def text(x, y, s, font, fill=BLACK, anchor="mm"):
    d.text((x, y), s, font=font, fill=fill, anchor=anchor)


def rect(x, y, w, h, label):
    d.rectangle([x-w/2, y-h/2, x+w/2, y+h/2], fill="white", outline=BLACK, width=3)
    text(x, y, label, f_ent)


def ellipse(x, y, label, w=180, h=58):
    d.ellipse([x-w/2, y-h/2, x+w/2, y+h/2], fill="white", outline=BLACK, width=2)
    text(x, y, label, f_attr)


def diamond(x, y, label, rx=105, ry=54):
    pts = [(x, y-ry), (x+rx, y), (x, y+ry), (x-rx, y)]
    d.polygon(pts, fill="white", outline=BLACK, width=2)
    text(x, y, label, f_rel)


def line(p1, p2):
    d.line([p1, p2], fill=BLACK, width=2)


def card(x, y, s):
    w = d.textlength(s, font=f_card)
    d.rounded_rectangle([x-w/2-5, y-17, x+w/2+5, y+17], radius=4, fill="white")
    text(x, y, s, f_card, BLACK)


U = (300, 300)
M = (650, 520)
C = (1550, 300)
A = (1150, 760)
S = (1750, 760)
R = (1150, 1250)

# 属性
attrs = [
    (180, 190, "用户ID"), (430, 200, "角色"),
    (620, 380, "媒体ID"), (820, 400, "名称"),
    (1450, 190, "频道ID"), (1650, 200, "名称"),
    (1000, 880, "文章ID"), (1300, 880, "状态"),
    (1650, 630, "素材ID"), (1850, 640, "地址"),
    (1000, 1360, "记录ID"), (1300, 1360, "审核结果"),
]

# 先画属性连线
for (ex, ey), (x, y, label) in [
    (U, (180, 190, "用户ID")), (U, (430, 200, "角色")),
    (M, (620, 380, "媒体ID")), (M, (820, 400, "名称")),
    (C, (1450, 190, "频道ID")), (C, (1650, 200, "名称")),
    (A, (1000, 880, "文章ID")), (A, (1300, 880, "状态")),
    (S, (1650, 630, "素材ID")), (S, (1850, 640, "地址")),
    (R, (1000, 1360, "记录ID")), (R, (1300, 1360, "审核结果")),
]:
    line((ex, ey), (x, y))

# 联系位置
D1 = (410, 450)
D2 = (860, 640)
D3 = (1380, 540)
D4 = (1450, 760)
D5 = (500, 950)
D6 = (1150, 1030)

# 联系线
line((390, 340), D1); line(D1, (570, 480))       # 拥有
line((730, 560), D2); line(D2, (1040, 715))      # 发布
line((1550, 340), D3); line(D3, (1240, 715))     # 归类
line((1280, 760), D4); line(D4, (1630, 760))     # 使用
line((530, 520), (500, 520)); line((500, 520), D5)
line((500, 1000), (500, 1250)); line((500, 1250), (1010, 1250))  # 审核
line((1150, 805), D6); line(D6, (1150, 1205))    # 产生

# 图形
rect(*U, 220, 80, "用户")
rect(*M, 240, 80, "媒体身份")
rect(*C, 220, 80, "频道")
rect(*A, 260, 90, "文章")
rect(*S, 240, 90, "素材")
rect(*R, 280, 90, "审核记录")

for x, y, label in [(D1[0], D1[1], "拥有"), (D2[0], D2[1], "发布"),
                    (D3[0], D3[1], "归类"), (D4[0], D4[1], "使用"),
                    (D5[0], D5[1], "审核"), (D6[0], D6[1], "产生")]:
    diamond(x, y, label)

for x, y, label in attrs:
    ellipse(x, y, label)

# 基数
for x, y, s in [
    (365, 370, "1"), (535, 435, "N"),
    (760, 590, "1"), (990, 690, "N"),
    (1500, 380, "1"), (1270, 650, "N"),
    (1320, 730, "M"), (1580, 730, "N"),
    (470, 560, "1"), (470, 1145, "N"),
    (1170, 850, "1"), (1170, 1160, "N"),
]:
    card(x, y, s)

out = r"F:\IDEA\YXP-QM\campus-headlines\docs\概念E-R图_内容简洁版.png"
img.save(out, "PNG", optimize=True)
print("SAVED", out, os.path.getsize(out), img.size)
