from reportlab.lib.pagesizes import A3, A4
from reportlab.pdfgen import canvas
from pathlib import Path
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
from reportlab.lib import utils
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
fa1 = 4.0
fa2 = 4.0
fa3 = 6.0
xz = 40
yz = 15
xa1 = 65
ya1 = 500
xa2 = 310
ya2 = 500
xa3 = 140
ya3 = 45
xf = 40
yf = 365
df = 130
dfy = 20

def lookupmonument(name):
    index = -1
    code = ""
    displayname = ""
    if name[:2] == "RM" and name[7] == ' ':
        code = name[:7]
        for l in range(len(assendelftrijkdata)):
            if code == assendelftrijkdata[l][0][:7]:
               displayname = assendelftrijkdata[l][0][9:]
               index = l
    elif name[:2] == "RM" and name[8] == ' ':
        code = name[:8]
        for l in range(len(assendelftrijkdata)):
            if code == assendelftrijkdata[l][0][:8]:
               displayname = assendelftrijkdata[l][0][10:]
               index = l
    elif name[:4] == "GMNH":
        code = name[5:10]
        for l in range(len(provinciedata)):
            if code == provinciedata[l][0][5:10]:
               displayname = provinciedata[l][0][12:]
               index = l
    elif name[:4] == "GMWN":
        code = name[2:7]
        for l in range(len(gemeentedata)):
            if code == gemeentedata[l][0][2:7]:
               displayname = gemeentedata[l][0][10:]
               index = l 
    return (index, code, displayname)
def scaleSVG(svgfile, scaling_factor):
    svg_root = load_svg_file(svgfile)
    svgRenderer = SvgRenderer(svgfile)
    drawing = svgRenderer.render(svg_root)
    scaling_x = scaling_factor
    scaling_y = scaling_factor
    drawing.width = drawing.minWidth() * scaling_x
    drawing.height = drawing.height * scaling_y
    drawing.scale(scaling_x, scaling_y)
    return drawing    
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
def retrievecoords(kmlfile, points):
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
            for (lon, lat, heig) in coord:
                if i.find('.//def:Point', ns):
                    lat = float(lat)
                    lon = float(lon)
                    if lat < points[0] and lat > points[2] and lon > points[1] and lon < points[3]:
                        data.append([name, lat, lon])
    return data
def cutoff(crd1, crd2, points):
    return crd1
def get_image(path, width=1*cm):
    img = utils.ImageReader(path)
    iw, ih = img.getSize()
    aspect = ih / float(iw)
    return Image(path, width=width, height=(width * aspect))
def scale_to_img(lat_lon, points, w_h, factor):
    old = (points[2], points[0])
    new = (0, w_h[1])
    y = ((lat_lon[0] - old[0]) * (new[1] - new[0]) / (old[1] - old[0]))
    old = (points[1], points[3])
    new = (0, w_h[0])
    x = ((lat_lon[1] - old[0]) * (new[1] - new[0]) / (old[1] - old[0]))
    return int(x) * factor, int(y * factor)
def markplace(c, bx, by, lat, lon, points, w_h, color, factor, name, radius, lnk, displayname):
    c.setFillColor(HexColor(color))
    x = 0
    y = 0
    if lat < points[0] and lat > points[2] and lon > points[1] and lon < points[3]:
        (x, y) = scale_to_img((lat, lon), points, w_h, factor)
    c.circle(bx + x, by + y, radius, stroke=0, fill=1)
    if len(displayname) > 0:
        c.setFont(assendelftfont, 5)
        c.setFillColor(HexColor("#000000"))
        c.drawString(bx + x + 5, by + y, displayname)
    linkx1 = bx + x - 1.5 * radius
    linky1 = by + y - 1.5 * radius
    linkx2 = bx + x + 1.5 * radius
    linky2 = by + y + 1.5 * radius
    linkarea = (linkx1, linky1, linkx2, linky2)
    (mi, code) = lookupgeo(name)
    if mi >= 0 and lnk == "y":
        c.linkAbsolute(code, code + 'I', linkarea, addtopage = 1, thickness = 0, color = None)
        c.bookmarkPage(code + 'L', fit = "XYZ", left = linkx1, top = linky2, zoom = 10)
    else:
        (mi, code, displayname) = lookupmonument(name)
        if mi >= 0:
            c.linkAbsolute(code, code + 'I', linkarea, addtopage = 1, thickness = 0, color = None)
            c.bookmarkPage(code + 'L', fit = "XYZ", left = linkx1, top = linky2, zoom = 10)
        else:
            (mi, code, displayname) = lookupmonument(name)
            if mi >= 0:
                c.linkAbsolute(code, code + 'I', linkarea, addtopage = 1, thickness = 0, color = None)
                c.bookmarkPage(code + 'L', fit = "XYZ", left = linkx1, top = linky2, zoom = 10)
            else:
                (mi, code, displayname) = lookupmonument(name)
                if mi >= 0:
                    c.linkAbsolute(code, code + 'I', linkarea, addtopage = 1, thickness = 0, color = None)
                    c.bookmarkPage(code + 'L', fit = "XYZ", left = linkx1, top = linky2, zoom = 10)
    return
def drawbounderies(c, bx, by, coords, year, points, w_h, factor):
    crds = []
    c.setFont(assendelftfont, 15)
    c.drawString(bx, by - 15, year)
    lat = coords[0][1]
    lon = coords[0][0]
    beginside = (lat < points[0] and lat > points[2] and lon > points[1] and lon < points[3])
    if not beginside:
        for i in range(len(coords)):
            print("hallobeginout")
    lat = coords[len(coords)-1][1]
    lon = coords[len(coords)-1][0]
    endinside = (lat < points[0] and lat > points[2] and lon > points[1] and lon < points[3])
    print(beginside, endinside)
    for i in range(len(coords)):
        lat = coords[i][1]
        lon = coords[i][0]
        if lat < points[0] and lat > points[2] and lon > points[1] and lon < points[3]:
            temp = coords[i][0]
            coords[i][0] = coords[i][1]
            coords[i][1] = temp
            crds.append(coords[i])
    p = c.beginPath()
    gcircle = 0
    for i in range(len(crds)):
        x, y = scale_to_img(crds[i], points, w_h, factor)
        x1 = bx + x
        y1 = by + y
        if i == 0:
            p.moveTo(x1, y1)
        p.lineTo(x1, y1)
        lat1, lon1 = crds[i]
        if i < len(crds) - 1:
            lat2, lon2 = crds[i + 1]
        else:
            lat2, lon2 = crds[0]
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
assendelftrijkdata = retrievecoords("assendelftrijk", pointsa)
provinciedata = retrievecoords("provincie", pointsa)
gemeentedata = retrievecoords("gemeente", pointsa)
my_canvas = canvas.Canvas("PDF/Assendelft.pdf")
my_canvas.setFillColor(HexColor("#50ff3c"))
my_canvas.rect(left_padding, bottom_padding, width, height, fill=1)
my_canvas.setTitle("Assendelft")
my_canvas.setFont(assendelftfont, 30)
my_canvas.setFillColor(HexColor("#000000"))
renderPDF.draw(scaleSVG("SVG/Assendelft_wapen.svg", 0.07), my_canvas, 45, 795)
my_canvas.drawString(80, 800, "Assendelft")
response = requests.get("https://gemeentegeschiedenis.nl/gemeentenaam/json/Assendelft")
if response.status_code == 200:
    history = response.content
    data = json.loads(history.decode('utf-8'))
    with open('JSON/Assendelft.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
[year1a, year2a, totalcoords1a, totalcoords2a] = readjson("JSON/Assendelft.json")
response = requests.get("https://gemeentegeschiedenis.nl/gemeentenaam/json/Zaanstad")
if response.status_code == 200:
    history = response.content
    data = json.loads(history.decode('utf-8'))
    with open('JSON/Zaanstad.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
[year3a, year4a, totalcoords3a, totalcoords4a] = readjson("JSON/Zaanstad.json")
my_canvas.drawImage("Photos/mapAssendelft.png", xa1, ya1, w_ha[0] * fa1, w_ha[1] * fa1)
my_canvas.drawImage("Photos/mapAssendelft.png", xa2, ya2, w_ha[0] * fa2, w_ha[1] * fa2)
my_canvas.drawImage("Photos/mapAssendelft.png", xa3, ya3, w_ha[0] * fa3, w_ha[1] * fa3)
drawbounderies(my_canvas, xa1, ya1, totalcoords1a, year1a, pointsa, w_ha, fa1)
drawbounderies(my_canvas, xa2, ya2, totalcoords2a, year2a, pointsa, w_ha, fa2)
drawbounderies(my_canvas, xa3, ya3, totalcoords3a, year3a, pointsa, w_ha, fa3)
for i in range(len(geodata)):
    buildyear = int(geodata[i][3])
    disappeared = int(geodata[i][4])
    if disappeared < 1875:
        markplace(my_canvas, xa1, ya1, float(geodata[i][1]), float(geodata[i][2]), pointsa, w_ha, '#00aaff', fa1, geodata[i][0], 3.0, geodata[i][5], geodata[i][6])
    elif disappeared < 2027:
        markplace(my_canvas, xa2, ya2, float(geodata[i][1]), float(geodata[i][2]), pointsa, w_ha, '#aa55ff', fa2,geodata[i][0], 3.0, geodata[i][5], geodata[i][6])
    else:
        markplace(my_canvas, xa3, ya3, float(geodata[i][1]), float(geodata[i][2]), pointsa, w_ha, '#ff15e8', fa3,geodata[i][0], 2.0, geodata[i][5], geodata[i][6])
for i in range(len(assendelftrijkdata)):
    markplace(my_canvas, xa3, ya3, float(assendelftrijkdata[i][1]), float(assendelftrijkdata[i][2]), pointsa, w_ha, '#55557f', fa3, assendelftrijkdata[i][0], 2.0, "n", "")
for i in range(len(provinciedata)):
    markplace(my_canvas, xa3, ya3, float(provinciedata[i][1]), float(provinciedata[i][2]), pointsa, w_ha, '#0cff08', fa3, provinciedata[i][0], 2.0, "n", "") 
for i in range(len(gemeentedata)):
    markplace(my_canvas, xa3, ya3, float(gemeentedata[i][1]), float(gemeentedata[i][2]), pointsa, w_ha, '#ff5a23', fa3, gemeentedata[i][0], 2.0, "n", "")
my_canvas.showPage()
my_canvas.setFillColor(HexColor('#000000'))
my_canvas.setFont(assendelftfont, 10)
maxrows = 4
scalepics = 0.3
col = 0
row = maxrows
colwidth = 150
rowheight = 160
bottommargin = 25
infos = 0
maxinfospage = 24
for i in range(len(geodata)):
    if geodata[i][5] == "y":
        code = geodata[i][0]
        img = utils.ImageReader("Photos/" + code + ".jpg")
        iw, ih = img.getSize()
        aspect = ih / float(iw)
        my_canvas.drawImage(img, col * colwidth, bottommargin + row * rowheight, iw * scalepics, ih * scalepics)
        my_canvas.drawString(col * colwidth, bottommargin + row * rowheight - 5, code)
        linkx1 = col * colwidth
        linky1 = row * rowheight
        linkx2 = col * colwidth + colwidth
        linky2 = row * rowheight + rowheight
        linkarea = (linkx1, linky1, linkx2, linky2)
        my_canvas.linkAbsolute(code, code + 'L', linkarea, addtopage = 1, thickness = 0, color = None)
        my_canvas.bookmarkPage(code + 'I', fit = "XYZ", left = linkx1, top = linky2, zoom = 8)
        infos += 1
        col += 1
        if col == 4:
            col = 0
            row -=1
        if infos == maxinfospage:
            my_canvas.showPage()
            infos = 0
            col = 0
            row = maxrows
for i in range(len(assendelftrijkdata)):
    (mi, code, displayname) = lookupmonument(assendelftrijkdata[i][0])
    if mi >= 0:
        my_canvas.drawImage("Photos/" + code + ".JPG", col * colwidth, bottommargin + row * rowheight + dfy, 400 * scalepics, 250 * scalepics)
        my_canvas.drawString(col * colwidth, bottommargin + row * rowheight, displayname)
        linkx1 = col * colwidth
        linky1 = row * rowheight
        linkx2 = col * colwidth + colwidth
        linky2 = row * rowheight + rowheight
        linkarea = (linkx1, linky1, linkx2, linky2)
        my_canvas.linkAbsolute(code, code + 'L', linkarea, addtopage = 1, thickness = 0, color = None)
        my_canvas.bookmarkPage(code + 'I', fit = "XYZ", left = linkx1, top = linky2, zoom = 8)
        infos += 1
        col += 1
        if col == 4:
            col = 0
            row -=1
        if infos == maxinfospage:
            my_canvas.showPage()
            infos = 0
            col = 0
            row = maxrows
for i in range(len(provinciedata)):
    (mi, code, displayname) = lookupmonument(provinciedata[i][0])
    if mi >= 0:
        a = Path("Photos/" + code + ".JPG")
        if a.exists():
            my_canvas.drawImage(a, col * colwidth, bottommargin + row * rowheight + dfy, 400 * scalepics, 250 * scalepics)
        my_canvas.drawString(col * colwidth, bottommargin + row * rowheight, displayname)
        linkx1 = col * colwidth
        linky1 = row * rowheight
        linkx2 = col * colwidth + colwidth
        linky2 = row * rowheight + rowheight
        linkarea = (linkx1, linky1, linkx2, linky2)
        my_canvas.linkAbsolute(code, code + 'L', linkarea, addtopage = 1, thickness = 0, color = None)
        my_canvas.bookmarkPage(code + 'I', fit = "XYZ", left = linkx1, top = linky2, zoom = 8)
        infos += 1
        col += 1
        if col == 4:
            col = 0
            row -=1
        if infos == maxinfospage:
            my_canvas.showPage()
            infos = 0
            col = 0
            row = maxrows
for i in range(len(gemeentedata)):
    (mi, code, displayname) = lookupmonument(gemeentedata[i][0])
    if mi >= 0:
        a = Path("Photos/" + code + ".JPG")
        if a.exists():
            my_canvas.drawImage(a, col * colwidth, bottommargin + row * rowheight + dfy, 400 * scalepics, 250 * scalepics)
        my_canvas.drawString(col * colwidth, bottommargin + row * rowheight, displayname)
        linkx1 = col * colwidth
        linky1 = row * rowheight
        linkx2 = col * colwidth + colwidth
        linky2 = row * rowheight + rowheight
        linkarea = (linkx1, linky1, linkx2, linky2)
        my_canvas.linkAbsolute(code, code + 'L', linkarea, addtopage = 1, thickness = 0, color = None)
        my_canvas.bookmarkPage(code + 'I', fit = "XYZ", left = linkx1, top = linky2, zoom = 8)
        infos += 1
        col += 1
        if col == 4:
            col = 0
            row -=1
        if infos == maxinfospage:
            my_canvas.showPage()
            infos = 0
            col = 0
            row = maxrows
my_canvas.save()
key = input("Wait")
