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
pointsz = (52.5258, 4.6671, 52.4139, 4.8714)
w_hz = (199.5, 177.9)
pointsa = (52.5242, 4.6596 , 52.4225 , 4.7942)
w_ha = (72.9, 90.8)
resp = requests.Response
geodata = []
zaanstaddata = []
factor = 2.5
xz = 40
yz = 15
xa1 = 75
ya1 = 550
xa2 = 300
ya2 = 550
xf = 40
yf = 475
df = 130

def lookupmonument(name):
    index = -1
    for l in range(len(zaanstaddata)):
        if zaanstaddata[l][0] == name:
            index = l
    return index

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
    radius = 2.0
    x = 0
    y = 0
    inkader = True
    if lat > points[0] or lat < points[2] or lon < points[1] or lon > points[3]:
        inkader = False
    if inkader:
        (x, y) = scale_to_img((lat, lon), points, w_h, factor)
    c.circle(bx + x, by + y, radius, stroke=0, fill=1)
    linkx1 = bx + x - 0.5 * radius
    linky1 = by + y - 0.5 * radius
    linkx2 = bx + x + radius
    linky2 = by + y + radius
    linkarea = (linkx1, linky1, linkx2, linky2)
    code = name[:7]
    if code[:2] == "RM":
        mi = lookupmonument(code)
        if mi >= 0:
            c.linkAbsolute("Find ", code + 'I', linkarea, addtopage = 1, thickness = 0, color = None)
            c.bookmarkPage(code + 'L', fit = "FitR", left = linkx1, bottom = linky1, right = linkx2, top = linky2)
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
file_to_open = "CSV/zaanstad.csv"
with open(file_to_open, 'r') as file:
    csvreader = csv.reader(file, delimiter = ';')
    count = 0
    for row in csvreader:
        zaanstaddata.append(row)
        count += 1
assendelftrijkdata = retrievecoords("assendelftrijk")
koogaandezaanrijkdata = retrievecoords("koogaandezaanrijk")
krommeniedijkrijkdata = []
krommeniedijkrijkdata.append(["RM342003 -", 52.51808, 4.76451])
krommeniedijkrijkdata.append(["RM39970 - Krommeniedijk 182", 52.51741, 4.75054])
krommenierijkdata = retrievecoords("krommenierijk")
westzaanrijkdata = retrievecoords("westzaanrijk")
wormerveerrijkdata = retrievecoords("wormerveerrijk")
zaandamrijkdata = retrievecoords("zaandamrijk")
zaandijkrijkdata = retrievecoords("zaandijkrijk")
provinciedata = retrievecoords("provincie")
gemeentedata = retrievecoords("gemeente")
provinciedata = retrievecoords("provincie")
my_canvas = canvas.Canvas("PDF/Assendelft" + version + ".pdf")
my_canvas.setFillColor(HexColor("#50ff3c"))
my_canvas.rect(left_padding, bottom_padding, width, height, fill=1)
my_canvas.setTitle("Assendelft" + version)
my_canvas.setFont(assendelftfont, 30)
my_canvas.setFillColor(HexColor("#000000"))
my_canvas.drawString(50, 800, "Assendelft")
response = requests.get("https://gemeentegeschiedenis.nl/gemeentenaam/json/Zaanstad")
if response.status_code == 200:
    history = response.content
    data = json.loads(history.decode('utf-8'))
    with open('JSON/Zaanstad.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
[year1z, year2z, totalcoords1z, totalcoords2z] = readjson("JSON/Zaanstad.json")
response = requests.get("https://gemeentegeschiedenis.nl/gemeentenaam/json/Assendelft")
if response.status_code == 200:
    history = response.content
    data = json.loads(history.decode('utf-8'))
    with open('JSON/Assendelft.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
[year1a, year2a, totalcoords1a, totalcoords2a] = readjson("JSON/Assendelft.json")
my_canvas.drawImage("Photos/mapzaanstad.png", xz, yz, w_hz[0] * factor, w_hz[1] * factor)
my_canvas.drawImage("Photos/mapassendelft.png", xa1, ya1, w_ha[0] * factor, w_ha[1] * factor)
my_canvas.drawImage("Photos/mapassendelft.png", xa2, ya2, w_ha[0] * factor, w_ha[1] * factor)
drawbounderies(my_canvas, xz, yz, totalcoords1z, year1z, pointsz, w_hz, factor)
drawbounderies(my_canvas, xa1, ya1, totalcoords1a, year1a, pointsa, w_ha, factor)
drawbounderies(my_canvas, xa2, ya2, totalcoords2a, year2a, pointsa, w_ha, factor)
for i in range(len(geodata)):
    markplace(my_canvas, xa1, ya1, float(geodata[i][1]), float(geodata[i][2]), pointsa, w_ha, '#00aaff', factor, geodata[i][0])
    markplace(my_canvas, xa2, ya2, float(geodata[i][1]), float(geodata[i][2]), pointsa, w_ha, '#aa55ff', factor,geodata[i][0])
for i in range(len(assendelftrijkdata)):
    markplace(my_canvas, xz, yz, float(assendelftrijkdata[i][1]), float(assendelftrijkdata[i][2]), pointsz, w_hz, '#55557f', factor, assendelftrijkdata[i][0])
for i in range(len(koogaandezaanrijkdata)):
    markplace(my_canvas, xz, yz, float(koogaandezaanrijkdata[i][1]), float(koogaandezaanrijkdata[i][2]), pointsz, w_hz, '#55557f', factor, koogaandezaanrijkdata[i][0])   
for i in range(len(krommeniedijkrijkdata)):
    markplace(my_canvas, xz, yz, float(krommeniedijkrijkdata[i][1]), float(krommeniedijkrijkdata[i][2]), pointsz, w_hz, '#55557f', factor, krommeniedijkrijkdata[i][0])
for i in range(len(krommenierijkdata)):
    markplace(my_canvas, xz, yz, float(krommenierijkdata[i][1]), float(krommenierijkdata[i][2]), pointsz, w_hz, '#55557f', factor, krommenierijkdata[i][0])
for i in range(len(westzaanrijkdata)):
    markplace(my_canvas, xz, yz, float(westzaanrijkdata[i][1]), float(westzaanrijkdata[i][2]), pointsz, w_hz, '#55557f', factor, westzaanrijkdata[i][0])
for i in range(len(wormerveerrijkdata)):
    markplace(my_canvas, xz, yz, float(wormerveerrijkdata[i][1]), float(wormerveerrijkdata[i][2]), pointsz, w_hz, '#55557f', factor, wormerveerrijkdata[i][0])
for i in range(len(zaandamrijkdata)):
    markplace(my_canvas, xz, yz, float(zaandamrijkdata[i][1]), float(zaandamrijkdata[i][2]), pointsz, w_hz, '#55557f', factor, zaandamrijkdata[i][0])
for i in range(len(zaandijkrijkdata)):
    markplace(my_canvas, xz, yz, float(zaandijkrijkdata[i][1]), float(zaandijkrijkdata[i][2]), pointsz, w_hz, '#55557f', factor, zaandijkrijkdata[i][0])
for i in range(len(provinciedata)):
    markplace(my_canvas, xz, yz, float(provinciedata[i][1]), float(provinciedata[i][2]), pointsz, w_hz, '#00ffff', factor, provinciedata[i][0])
for i in range(len(gemeentedata)):
    markplace(my_canvas, xz, yz, float(gemeentedata[i][1]), float(gemeentedata[i][2]), pointsz, w_hz, '#ffb592', factor, gemeentedata[i][0])
scalepics = 0.3
my_canvas.drawImage("Photos/deHuisman2e.jpg", xf, yf, 400 * scalepics, 250 * scalepics)
my_canvas.drawImage("Photos/hetHuisAssumburg.jpg", xf + df, yf, 400 * scalepics, 250 * scalepics)
my_canvas.drawImage("Photos/dePauw.jpg", xf + 2 * df, yf, 400 * scalepics, 250 * scalepics)
my_canvas.drawImage("Photos/huisvrouw.jpg", xf + 3 * df, yf, 400 * scalepics, 250 * scalepics)
my_canvas.showPage()
my_canvas.setFillColor(HexColor('#000000'))
my_canvas.setFont(assendelftfont, 10)
col = 0
row = 3
colwidth = 200
rowheight = 150
for i in range(len(zaanstaddata)):
    my_canvas.drawString(col * 95 + 10, row * 20, zaanstaddata[i][0])
    my_canvas.drawImage("Photos/" + zaanstaddata[i][0] + ".JPG", col * colwidth, row * rowheight, 400 * scalepics, 250 * scalepics)
    my_canvas.circle(col * colwidth + 20, row * rowheight - 40, 4.0, stroke=0, fill=1)
    my_canvas.bookmarkPage(zaanstaddata[i][0][:7] + 'I', fit = "FitR", left = 10, bottom = 10, right = 50, top = 50)
    linkx1 = col * colwidth
    linky1 = row * rowheight
    linkx2 = col * colwidth + colwidth
    linky2 = row * rowheight + rowheight
    linkarea = (linkx1, linky1, linkx2, linky2)
    my_canvas.linkAbsolute("Find ", zaanstaddata[i][0][:7] + 'I', linkarea, addtopage = 1, thickness = 0, color = None)
    col += 1
    if col == 6:
        col = 0
        row -=1
my_canvas.save()
key = input("Wait")
