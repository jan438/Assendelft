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
from geopy.distance import great_circle

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
                            year1 = year
                            totalcoords1 = coords0[0]
                        if countyears == 2:
                            year2 = year
                            totalcoords2 = coords0[0]
    return [year1, year2, totalcoords1, totalcoords2]
    
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
[year1, year2, totalcoords1, totalcoords2] = readjson("JSON/assendelft.json")
my_canvas.drawString(50, 500, year1 + "   " + str(len(totalcoords1)))
p = my_canvas.beginPath()
bx = 250
by = 450
scale = 5000
p.moveTo(bx, by)
p.lineTo(bx, by)
for i in range(len(totalcoords1) - 1):
    dx = totalcoords1[i][0] - totalcoords1[i + 1][0]
    dy = totalcoords1[i][1] - totalcoords1[i + 1][1]
    p.lineTo(bx + dx * scale, by + dy * scale)
p.lineTo(bx, by)
my_canvas.drawPath(p, fill=0, stroke=1)
my_canvas.drawString(50, 300, year2 + "   " + str(len(totalcoords2)))
p = my_canvas.beginPath()
bx = 250
by = 250
scale = 5000
gcircle = 0
p.moveTo(bx, by)
p.lineTo(bx, by)
for i in range(len(totalcoords2) - 1):
    d = great_circle(totalcoords2[i], totalcoords2[i + 1]).km
    gcircle += d
    dx = totalcoords2[i][0] - totalcoords2[i + 1][0]
    dy = totalcoords2[i][1] - totalcoords2[i + 1][1]
    p.lineTo(bx + dx * scale, by + dy * scale)
p.lineTo(bx, by)
my_canvas.drawPath(p, fill=0, stroke=1)
my_canvas.drawString(200, 300, str(round(gcircle, 1)))
my_canvas.drawImage("Photos/foto1.jpg", 150, 400, 400 * 0.75, 250 * 0.75)
my_canvas.save()
key = input("Wait")
