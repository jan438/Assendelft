from reportlab.lib.pagesizes import A3, A4
from reportlab.pdfgen import canvas
import os
import csv
import sys
import json
import math
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
    return int(x), w_h[1] - int(y)

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
[year1, year2, totalcoords1, totalcoords2] = readjson("JSON/assendelft.json")
minlat = math.inf
maxlat = -math.inf
minlon = math.inf
maxlon = -math.inf
for i in range(len(totalcoords1)):
    lon = float(totalcoords1[i][0])
    lat = float(totalcoords1[i][1])
    if lon > maxlon:
        maxlon = lon
    if lon < minlon:
        minlon = lon  
    if lat > maxlat:
        maxlat = lat
    if lat < minlat:
        minlat = lat
minlat = math.inf
maxlat = -math.inf
minlon = math.inf
maxlon = -math.inf
for i in range(len(totalcoords2)):
    lon = float(totalcoords2[i][0])
    lat = float(totalcoords2[i][1])
    if lon > maxlon:
        maxlon = lon
    if lon < minlon:
        minlon = lon
    if lat > maxlat:
        maxlat = lat
    if lat < minlat:
        minlat = lat
vis = GPSVis(data_path='CSV/data1.csv',map_path='Photos/map1.png',points=points)
vis.create_image(color=(0, 0, 255), width=3)
vis.plot_map(output='save')
my_canvas.drawString(50, 500, year1 + "   " + str(len(totalcoords1)))
for i in range(len(totalcoords1)):
    temp = totalcoords1[i][0]
    totalcoords1[i][0] = totalcoords1[i][1]
    totalcoords1[i][1] = temp
p = my_canvas.beginPath()
bx = 250
by = 450
x0 = bx
y0 = by
p.moveTo(bx, by)
p.lineTo(bx, by)
for i in range(len(totalcoords1)):
    x1, y1 = scale_to_img(totalcoords1[i], w_h)
    p.lineTo(x1, y1)
    x0 = x1
    y0 = y1
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
scalepics = 0.4
my_canvas.drawString(200, 300, str(round(gcircle, 1)) + " km")
my_canvas.drawImage("Photos/resultMap.png", 300, 400, 200, 200)
my_canvas.drawImage("Photos/deHuisman2e.jpg", 25, 600, 400 * scalepics, 250 * scalepics)
my_canvas.drawImage("Photos/hetHuisAssumburg.jpg", 25, 400, 400 * scalepics, 250 * scalepics)
my_canvas.drawImage("Photos/dePauw.jpg", 25, 200, 400 * scalepics, 250 * scalepics)
my_canvas.save()
key = input("Wait")
