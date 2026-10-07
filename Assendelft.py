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
#map1
#points = (52.5496, 4.6510 , 52.4104 , 4.7966)
#w_h = (92.3, 126.0)
points = (52.5242, 4.6596 , 52.4225 , 4.7942)
w_h = (72.9, 90.8)
resp = requests.Response
geodata = []
mapscale = 0.5
mapdx = 25
mapdy = 20

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
    
def markplace(c, bx, by, lat, lon, w_h):
    c.setFillColor(HexColor("#ff7462"))
    x, y = scale_to_img((lat, lon), w_h)
    c.circle(bx + x, by + y, 3, stroke=0, fill=1)
    return
    
def drawbounderies(c, bx, by, coords, year):
    c.setFont(assendelftfont, 10)
    c.drawString(bx, by - 15, year + "   " + str(len(coords)))
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
    c.drawString(bx, by - 30, str(round(gcircle, 1)) + "km")
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
file_to_open = "CSV/geo.csv"
with open(file_to_open, 'r') as file:
    csvreader = csv.reader(file, delimiter = ';')
    count = 0
    for row in csvreader:
        geodata.append(row)
        count += 1
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
my_canvas.drawImage("Photos/map2.png", 75 + mapdx, 100 + mapdy, 92.3 * mapscale, 126.0 * mapscale)
my_canvas.drawImage("Photos/map2.png", 175 + mapdx, 100 + mapdy, 92.3 * mapscale, 126.0 * mapscale)
my_canvas.saveState()
my_canvas.translate(0, 0)
my_canvas.scale(1.0, 1.0)
drawbounderies(my_canvas, 75, 100, totalcoords1, year1)
drawbounderies(my_canvas, 175, 100, totalcoords2, year2)
for i in range(len(geodata)):
    markplace(my_canvas, 75, 100, float(geodata[i][1]), float(geodata[i][2]), w_h)
    markplace(my_canvas, 175, 100, float(geodata[i][1]), float(geodata[i][2]), w_h)
my_canvas.restoreState()
scalepics = 0.4
my_canvas.drawImage("Photos/deHuisman2e.jpg", 25, 700, 400 * scalepics, 250 * scalepics)
my_canvas.drawImage("Photos/hetHuisAssumburg.jpg", 25, 600, 400 * scalepics, 250 * scalepics)
my_canvas.drawImage("Photos/dePauw.jpg", 25, 500, 400 * scalepics, 250 * scalepics)
my_canvas.drawImage("Photos/huisvrouw.jpg", 25, 400, 400 * scalepics, 250 * scalepics)
my_canvas.save()
key = input("Wait")
