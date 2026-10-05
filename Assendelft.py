from reportlab.lib.pagesizes import A3, A4
from reportlab.pdfgen import canvas
import os
import csv
import sys
import json
import math
import requests
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
import warnings
from gps_class import GPSVis

warnings.filterwarnings('ignore')

assendelftfont = "LiberationSerif"
version = "1"
left_padding = 0
bottom_padding = 0
A4_width = A4[0]
A4_height = A4[1]
width = A4_width
height = A4_height
points = (52.51, 4.67, 52.43, 4.77)
w_h = (100, 100)
resp = requests.Response

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
    
def scale_to_img(lat_lon, w_h):
    old = (points[2], points[0])
    new = (0, w_h[1])
    y = ((lat_lon[0] - old[0]) * (new[1] - new[0]) / (old[1] - old[0])) + new[0]
    old = (points[1], points[3])
    new = (0, w_h[0])
    x = ((lat_lon[1] - old[0]) * (new[1] - new[0]) / (old[1] - old[0])) + new[0]
    return int(x), int(y)
    
def drawbounderies(c, bx, by, coords):
    c.drawString(bx, by, year1 + "   " + str(len(totalcoords1)))
    for i in range(len(coords)):
        temp = coords[i][0]
        coords[i][0] = coords[i][1]
        coords[i][1] = temp
    p = c.beginPath()
    gcircle = 0
    for i in range(len(coords)):
        x, y = scale_to_img(coords[i], w_h)
        x1 = bx + x
        y1 = by + y
        if i == 0:
            p.moveTo(x1, y1)
        p.lineTo(x1, y1)
        lat1, lon1 = coords[i]
        if i < len(coords) - 1:
            lat2, lon2 = coords[i + 1]
        else:
            lat2, lon2 = coords[0]
        coord1 = (lon1, lat1)
        coord2 = (lon2, lat2)
        d = great_circle(coord1, coord2).km
        gcircle += d
    c.drawPath(p, fill=0, stroke=1)
    c.drawString(bx, by, str(round(gcircle, 1)) + "km")
    return

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
my_canvas.drawString(50, 800, "Assendelft")
response = requests.get("https://gemeentegeschiedenis.nl/gemeentenaam/json/Assendelft")
if response.status_code == 200:
    history = response.content
    data = json.loads(history.decode('utf-8'))
    with open('JSON/Assendelft.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
[year1, year2, totalcoords1, totalcoords2] = readjson("JSON/Assendelft.json")
vis = GPSVis(data_path='CSV/data1.csv',map_path='Photos/map1.png',points=points)
vis.create_image(color=(0, 0, 255), width=3)
vis.plot_map(output='save')
drawbounderies(my_canvas, 75, 100, totalcoords1)
drawbounderies(my_canvas, 175, 100, totalcoords2)
scalepics = 0.4
my_canvas.drawImage("Photos/resultMap.png", 300, 400, 200, 200)
my_canvas.drawImage("Photos/deHuisman2e.jpg", 25, 600, 400 * scalepics, 250 * scalepics)
my_canvas.drawImage("Photos/hetHuisAssumburg.jpg", 25, 400, 400 * scalepics, 250 * scalepics)
my_canvas.drawImage("Photos/dePauw.jpg", 25, 200, 400 * scalepics, 250 * scalepics)
my_canvas.save()
key = input("Wait")
