from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def create_linked_pdf(filename):
    c = canvas.Canvas(filename, pagesize=letter)
    c.bookmarkPage("pagina_1")
    c.drawString(100, 700, "Dit is Pagina 1")
    radius = 2.0
    c.drawString(100, 650, "Klik hieronder om naar Pagina 2 te gaan:")
    c.circle(100, 650, radius, stroke=0, fill=1)
    linkx1 = 100 - 0.5 * radius
    linky1 = 650 - 0.5 * radius
    linkx2 = 100 + radius
    linky2 = 650 + radius
    linkarea1 = (linkx1, linky1, linkx2, linky2)
    c.linkAbsolute("Find ", "pagina_2", linkarea1, addtopage = 1, thickness = 0, color = None)
    c.showPage()
    c.bookmarkPage("pagina_2")
    c.drawString(100, 700, "Dit is Pagina 2")
    c.drawString(100, 650, "Klik hieronder om weer terug te gaan:")
    c.drawString(100, 600, "[ Terug naar Pagina 1 ]")
    linkx1 = 0
    linky1 = 0
    linkx2 = 200
    linky2 = 200
    linkarea2 = (linkx1, linky1, linkx2, linky2)    
    c.linkAbsolute("Find ", "pagina_1", linkarea2, addtopage = 1, thickness = 0, color = None)    
    c.save()

if __name__ == "__main__":
    create_linked_pdf("PDF/heen_en_terug.pdf")
key = input("Wait")
