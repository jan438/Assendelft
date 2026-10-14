from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def create_linked_pdf(filename):
    c = canvas.Canvas(filename, pagesize=letter)
    c.bookmarkPage("pagina_1")
    c.drawString(100, 700, "Dit is Pagina 1")
    c.drawString(100, 650, "Klik hieronder om naar Pagina 2 te gaan:")
    c.drawString(100, 600, "[ Ga naar Pagina 2 ]")
#    c.linkAbsolute("pagina_2", 95, 595, 200, 615)
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
