from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def create_linked_pdf(filename):
    c = canvas.Canvas(filename, pagesize=letter)
    c.bookmarkPage("pagina_1")
    c.drawString(100, 700, "Dit is Pagina 1")
    c.drawString(100, 650, "Klik hieronder om naar Pagina 2 te gaan:")
    c.drawString(100, 600, "[ Ga naar Pagina 2 ]")
    linkx1 = 0
    linky1 = 0
    linkx2 = 20
    linky2 = 20
    linkarea = (linkx1, linky1, linkx2, linky2)
    c.linkAbsolute("Find ", "pagina_2", linkarea, addtopage = 1, thickness = 0, color = None)
    c.showPage()
    c.bookmarkPage("pagina_2")
    c.drawString(100, 700, "Dit is Pagina 2")
    c.drawString(100, 650, "Klik hieronder om weer terug te gaan:")
    c.drawString(100, 600, "[ Terug naar Pagina 1 ]")
#    c.linkAbsolute("pagina_1", 95, 595, 220, 615)
    c.save()

if __name__ == "__main__":
    create_linked_pdf("PDF/heen_en_terug.pdf")
key = input("Wait")
