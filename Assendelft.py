from reportlab.lib.pagesizes import A3, A4
from reportlab.pdfgen import canvas
import os
import csv
import sys
import json
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from svglib.svglib import svg2rlg, load_svg_file, SvgRenderer
from reportlab.graphics import renderPDF
from reportlab.lib.colors import yellow, green, red, blue, black, white, tan, HexColor
from reportlab.lib.units import inch, cm, mm
from math import pi, cos, sin, radians, sqrt
import xml.etree.ElementTree as ET

assendelftfont = "LiberationSerif"
version = "1"
left_padding = 0
bottom_padding = 0
A4_width = A4[0]
A4_height = A4[1]
width = A4_width
height = A4_height

def readjson(jsonfile):
    countyears = 0
    totalcoords1 = []
    totalcoords2 = []
    with open(jsonfile, 'r') as file:
        data = json.load(file)
        geo = data["geometries"]
        for year in geo:
            countyears += 1
            item = geo[year]
            for subitem in item:
                if subitem == "features":
                    features = item[subitem]
                    for feature in features:
                        geom = feature["geometry"]
                        coords = geom["coordinates"]
                        coords0 = coords[0]
                        if countyears == 1:
                            totalcoords1 = coords0[0]
                        if countyears == 2:
                            totalcoords2 = coords0[0]
    return [totalcoords1, totalcoords2]
    
if sys.platform[0] == 'l':
    path = '/home/jan/git/Assendelft'
if sys.platform[0] == 'w':
    path = "C:/Users/janbo/OneDrive/Documents/GitHub/Assendelft"
os.chdir(path)
pdfmetrics.registerFont(TTFont('LiberationSerif', 'LiberationSerif-Regular.ttf'))
pdfmetrics.registerFont(TTFont('LiberationSerifBold', 'LiberationSerif-Bold.ttf'))
pdfmetrics.registerFont(TTFont('LiberationSerifItalic', 'LiberationSerif-Italic.ttf'))
pdfmetrics.registerFont(TTFont('LiberationSerifBoldItalic', 'LiberationSerif-BoldItalic.ttf'))
my_canvas = canvas.Canvas("PDF/Assendelft" + version + ".pdf")
my_canvas.setFillColor(HexColor("#50ff3c"))
my_canvas.rect(left_padding, bottom_padding, width, height, fill=1)
my_canvas.setTitle("Assendelft" + version)
my_canvas.setFont(assendelftfont, 30)
my_canvas.setFillColor(HexColor("#000000"))
my_canvas.drawString(50, 800, "Assendelft" + version)
[totalcoords1, totalcoords2] = readjson("JSON/assendelft.json")
my_canvas.drawString(50, 500, "totalcoords1:" + str(len(totalcoords1)))
beginlat = totalcoords1[0][0]
beginlon = totalcoords1[0][1]
dx = 0
dy = 0
p = my_canvas.beginPath()
p.moveTo(50 + dx, 450 + dy)
p.lineTo(50 + dx, 450 + dy)
for i in range(len(totalcoords1) - 1):
    if i == 8:
        break
    dx = totalcoords1[i][0] - totalcoords1[i + 1][0]
    dy = totalcoords1[i][1] - totalcoords1[i + 1][1]
    p.lineTo(50 + dx * 1000, 450 + dy * 1000)
my_canvas.drawPath(p, fill=0, stroke=1)
my_canvas.drawString(50, 300, "totalcoords2:" + str(len(totalcoords2)))
my_canvas.save()
key = input("Wait")
