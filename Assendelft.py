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
import re
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
pointsa = (52.5058, 4.6761, 52.4250, 4.7852)
w_ha = (55.6, 67.9)
resp = requests.Response
geodata = []
zaanstaddata = []
factor = 4.0
xz = 40
yz = 15
xa1 = 65
ya1 = 450
xa2 = 310
ya2 = 450
xa3 = 200
ya3 = 25
xf = 40
yf = 365
df = 130

def lookupmonument(name):
    index = -1
    code = ""
    if name[:2] == "RM" and name[7] == ' ':
        code = name[:7]
        for l in range(len(zaanstaddata)):
            if zaanstaddata[l][0] == code:
                index = l
    if name[:2] == "RM" and name[8] == ' ':
        code = name[:8]
        for l in range(len(zaanstaddata)):
            if zaanstaddata[l][0] == code:
                index = l
    return (index, code)
    
def lookupgeo(name):
    index = -1
    code = ""
    for l in range(len(geodata)):
        if geodata[l][0] == name:
            index = l
            code = name
    return (index, code)

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
    
def retrievecoords(kmlfile):
    data = []
    tree = ET.parse('KML/' + kmlfile + ".kml")
    root = tree.getroot()
    namespace = re.match('\{(.*?)\}kml', root.tag).group(1)
    ns = {'def': namespace}
    coord_ex = '(-?\d+\.\d+),'
    heig_ex = '(\d+)'
    regex = coord_ex + coord_ex + heig_ex
    for i in root.findall('.//def:Placemark', ns):
        name = i.find('def:name', ns).text
        coord = i.find('.//def:coordinates', ns)
        if not coord is None:
            coord = coord.text.strip()
            coord = re.findall(regex, coord)
            for (long, lat, heig) in coord:
                if i.find('.//def:Point', ns):
                    data.append([name, lat, long])
    return data
    
def scale_to_img(lat_lon, points, w_h, factor):
    old = (points[2], points[0])
    new = (0, w_h[1])
    y = ((lat_lon[0] - old[0]) * (new[1] - new[0]) / (old[1] - old[0]))
    old = (points[1], points[3])
    new = (0, w_h[0])
    x = ((lat_lon[1] - old[0]) * (new[1] - new[0]) / (old[1] - old[0]))
    return int(x) * factor, int(y * factor)
    
def markplace(c, bx, by, lat, lon, points, w_h, color, factor, name):
    c.setFillColor(HexColor(color))
    radius = 3.0
    x = 0
    y = 0
    inkader = True
    if lat > points[0] or lat < points[2] or lon < points[1] or lon > points[3]:
        inkader = False
    if inkader:
        (x, y) = scale_to_img((lat, lon), points, w_h, factor)
    c.circle(bx + x, by + y, radius, stroke=0, fill=1)
    linkx1 = bx + x - 1.5 * radius
    linky1 = by + y - 1.5 * radius
    linkx2 = bx + x + 1.5 * radius
    linky2 = by + y + 1.5 * radius
    linkarea = (linkx1, linky1, linkx2, linky2)
    (mi, code) = lookupgeo(name)
    print(name, code, mi)
    if mi >= 0:
        c.linkAbsolute(code, code + 'I', linkarea, addtopage = 1, thickness = 0, color = None)
        c.bookmarkPage(code + 'L', fit = "XYZ", left = linkx1, top = linky2, zoom = 10)
    return
    
def drawbounderies(c, bx, by, coords, year, points, w_h, factor):
    c.setFont(assendelftfont, 10)
    c.drawString(bx, by - 15, year + "   " + str(len(coords)))
    for i in range(len(coords)):
        temp = coords[i][0]
        coords[i][0] = coords[i][1]
        coords[i][1] = temp
    p = c.beginPath()
    gcircle = 0
    for i in range(len(coords)):
        x, y = scale_to_img(coords[i], points, w_h, factor)
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
assendelftrijkdata = retrievecoords("assendelftrijk")
provinciedata = retrievecoords("provincie")
gemeentedata = retrievecoords("gemeente")
provinciedata = retrievecoords("provincie")
my_canvas = canvas.Canvas("PDF/Assendelft.pdf")
my_canvas.setFillColor(HexColor("#50ff3c"))
my_canvas.rect(left_padding, bottom_padding, width, height, fill=1)
my_canvas.setTitle("Assendelft")
my_canvas.setFont(assendelftfont, 30)
my_canvas.setFillColor(HexColor("#000000"))
my_canvas.drawString(50, 800, "Assendelft")
response = requests.get("https://gemeentegeschiedenis.nl/gemeentenaam/json/Assendelft")
if response.status_code == 200:
    history = response.content
    data = json.loads(history.decode('utf-8'))
    with open('JSON/Assendelft.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
[year1a, year2a, totalcoords1a, totalcoords2a] = readjson("JSON/Assendelft.json")
my_canvas.drawImage("Photos/mapAssendelft.png", xa1, ya1, w_ha[0] * factor, w_ha[1] * factor)
my_canvas.drawImage("Photos/mapAssendelft.png", xa2, ya2, w_ha[0] * factor, w_ha[1] * factor)
my_canvas.drawImage("Photos/mapAssendelft.png", xa3, ya3, w_ha[0] * factor, w_ha[1] * factor)
drawbounderies(my_canvas, xa1, ya1, totalcoords1a, year1a, pointsa, w_ha, factor)
drawbounderies(my_canvas, xa2, ya2, totalcoords2a, year2a, pointsa, w_ha, factor)
for i in range(len(geodata)):
    markplace(my_canvas, xa1, ya1, float(geodata[i][1]), float(geodata[i][2]), pointsa, w_ha, '#00aaff', factor, geodata[i][0])
    markplace(my_canvas, xa2, ya2, float(geodata[i][1]), float(geodata[i][2]), pointsa, w_ha, '#aa55ff', factor,geodata[i][0])
for i in range(len(assendelftrijkdata)):
    markplace(my_canvas, xa3, ya3, float(assendelftrijkdata[i][1]), float(assendelftrijkdata[i][2]), pointsa, w_ha, '#55557f', factor, assendelftrijkdata[i][0])
for i in range(len(provinciedata)):
    markplace(my_canvas, xa3, ya3, float(provinciedata[i][1]), float(provinciedata[i][2]), pointsa, w_ha, '#00ffff', factor, provinciedata[i][0])   
my_canvas.showPage()
my_canvas.setFillColor(HexColor('#000000'))
my_canvas.setFont(assendelftfont, 10)
scalepics = 0.3
col = 0
row = 5
colwidth = 150
rowheight = 145
bottommargin = 25
for i in range(len(geodata)):
    code = geodata[i][0]
    my_canvas.drawImage("Photos/" + code + ".jpg", col * colwidth, bottommargin + row * rowheight, 400 * scalepics, 250 * scalepics)
    my_canvas.drawString(col * colwidth, bottommargin + row * rowheight - 5, code)
    linkx1 = col * colwidth
    linky1 = row * rowheight
    linkx2 = col * colwidth + colwidth
    linky2 = row * rowheight + rowheight
    linkarea = (linkx1, linky1, linkx2, linky2)
    my_canvas.linkAbsolute(code, code + 'L', linkarea, addtopage = 1, thickness = 0, color = None)
    my_canvas.bookmarkPage(code + 'I', fit = "XYZ", left = linkx1, top = linky2, zoom = 8)
    col += 1
    if col == 4:
        col = 0
        row -=1
    if i == 23:
        my_canvas.showPage()
        col = 0
        row = 5
my_canvas.save()
key = input("Wait")
