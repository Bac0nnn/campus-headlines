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
f_note = ImageFont.truetype(FONT, 23)

BLACK = "#111111"
GRAY = "#444444"


def text(x, y, s, font, fill=BLACK, anchor="mm"):
    d.text((x, y), s, font=font, fill=fill, anchor=anchor)


def rect(x, y, w, h, label):
    d.rectangle([x-w/2, y-h/2, x+w/2, y+h/2], fill="white", outline=BLACK, width=3)
    text(x, y, label, f_ent)


def ellipse(x, y, label, w=180, h=58):
    d.ellipse([x-w/2, y-h/2, x+w/2, y+h/2], fill="white", outline=BLACK, width=2)
    text(x, y, label, f_attr)


def diamond(x, y, label, rx=108, ry=56):
    pts = [(x, y-ry), (x+rx, y), (x, y+ry), (x-rx, y)]
    d.polygon(pts, fill="white", outline=BLACK, width=2)
    text(x, y, label, f_rel)


def line(p1, p2):
    d.line([p1, p2], fill=BLACK, width=2)


def card(x, y, s):
    w = d.textlength(s, font=f_card)
    d.rounded_rectangle([x-w/2-5, y-17, x+w/2+5, y+17], radius=4, fill="white")
    text(x, y, s, f_card, BLACK)


U = (420, 300)
C = (1500, 300)
A = (980, 700)
S = (1660, 700)
R = (980, 1240)

# 属性
attrs = [
    (300, 180, "账号ID"), (540, 190, "角色"),
    (1400, 180, "频道ID"), (1600, 190, "名称"),
    (840, 830, "文章ID"), (1120, 830, "状态"),
    (1560, 590, "素材ID"), (1780, 600, "地址"),
    (840, 1370, "记录ID"), (1120, 1370, "审核结果"),
]

# 先画所有连线（图形后覆盖，线从边框处露出）
for (ax, ay), (bx, by, label) in [
    ((U[0], U[1]), (300, 180, "账号ID")), ((U[0], U[1]), (540, 190, "角色")),
    ((C[0], C[1]), (1400, 180, "频道ID")), ((C[0], C[1]), (1600, 190, "名称")),
    ((A[0], A[1]), (840, 830, "文章ID")), ((A[0], A[1]), (1120, 830, "状态")),
    ((S[0], S[1]), (1560, 590, "素材ID")), ((S[0], S[1]), (1780, 600, "地址")),
    ((R[0], R[1]), (840, 1370, "记录ID")), ((R[0], R[1]), (1120, 1370, "审核结果")),
]:
    line((ax, ay), (bx, by))

# 联系位置
D_FB = (680, 470)
D_GS = (1250, 470)
D_YY = (1400, 700)
D_SH = (230, 960)
D_CS = (980, 990)

# 发布
line((420, 340), (575, 470)); line((785, 470), (880, 660))
# 归属
line((1500, 340), (1355, 470)); line((1145, 470), (1080, 660))
# 引用
line((1110, 700), (1295, 700)); line((1505, 700), (1540, 700))
# 产生
line((980, 745), (980, 938)); line((980, 1042), (980, 1195))
# 审核（左侧折线）
line((300, 300), (230, 300)); line((230, 300), (230, 908))
line((230, 1012), (230, 1240)); line((230, 1240), (840, 1240))

# 图形
rect(*U, 240, 80, "自媒体账号")
rect(*C, 220, 80, "频道")
rect(*A, 260, 90, "文章")
rect(*S, 240, 90, "素材")
rect(*R, 280, 90, "审核记录")

for (x, y, label) in [(D_FB[0], D_FB[1], "发布"), (D_GS[0], D_GS[1], "归属"),
                      (D_YY[0], D_YY[1], "引用"), (D_SH[0], D_SH[1], "审核"),
                      (D_CS[0], D_CS[1], "产生")]:
    diamond(x, y, label)

for x, y, label in attrs:
    ellipse(x, y, label)

# 基数
for x, y, s in [
    (390, 375, "1"), (850, 585, "N"),
    (1540, 375, "1"), (1135, 585, "N"),
    (1195, 660, "M"), (1475, 660, "N"),
    (260, 390, "1"), (260, 1145, "N"),
    (1002, 805, "1"), (1002, 1135, "N"),
]:
    card(x, y, s)

out = r"F:\IDEA\YXP-QM\campus-headlines\docs\概念E-R图_简洁版.png"
img.save(out, "PNG", optimize=True)
print("SAVED", out, os.path.getsize(out), img.size)
