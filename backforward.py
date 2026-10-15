from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def create_linked_pdf(filename):
    c = canvas.Canvas(filename, pagesize=letter)
    c.bookmarkPage("AL")
    radius = 2.0
    c.circle(100, 650, radius, stroke=0, fill=1)
    linkarea1 = (100 - 0.5 * radius, 650 - 0.5 * radius, 100 + radius, 650 + radius)
    c.linkAbsolute("Find ", "AI", linkarea1, addtopage = 1, thickness = 0, color = None)
    c.showPage()
    c.bookmarkPage("AI")
    c.rect(100, 650, 100, 100)
    linkarea2 = (100, 650, 100 + 100, 650 + 100)    
    c.linkAbsolute("Find ", "AL", linkarea2, addtopage = 1, thickness = 0, color = None)    
    c.save()

if __name__ == "__main__":
    create_linked_pdf("PDF/heen_en_terug.pdf")
key = input("Wait")
