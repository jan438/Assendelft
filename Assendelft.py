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
    totalcoords = []
    with open(jsonfile, 'r') as file:
        data = json.load(file)
        geo = data["geometries"]
        for year in geo:
            print(year)
            item = geo[year]
            for subitem in item:
                if subitem == "features":
                    features = item[subitem]
                    for feature in features:
                        geom = feature["geometry"]
                        coords = geom["coordinates"]
                        coords0 = coords[0]
                        totalcoords = coords0[0]
    return totalcoords
    
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
totalcoords = readjson("JSON/assendelft.json")
my_canvas.drawString(50, 500, "totalcoords:" + str(len(totalcoords)))
my_canvas.save()
key = input("Wait")
