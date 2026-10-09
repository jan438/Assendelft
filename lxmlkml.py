from lxml import etree as ET

tree = ET.parse('sample.kml')
root = tree.getroot

print (root.find('.//{http://earth.google.com/kml/2.1}coordinates').text)


nsmap = {"k": root.nsmap[None]}
print (root.find('.//k:coordinates', nsmap).text)


ns = root.nsmap[None]
print (root.find('.//{{{0}}}coordinates'.format(ns)).text)
