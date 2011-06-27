#!/usr/bin/python2.6

import sys
import os

pathname, scriptname = os.path.split(sys.argv[0])
sys.path.insert(0, os.path.join(pathname,'../libs/reportlab.zip'))

def hello_pdf():
    from reportlab.pdfgen import canvas
    c = canvas.Canvas(os.path.join(pathname,"hello.pdf"))
    from reportlab.lib.units import inch
    # move the origin up and to the left
    c.translate(inch,inch)
    # define a large font
    c.setFont("Helvetica", 80)
    # choose some colors
    c.setStrokeColorRGB(0.2,0.5,0.3)
    c.setFillColorRGB(1,0,1)
    # draw a rectangle
    c.rect(inch,inch,6*inch,9*inch, fill=1)
    # make text go straight up
    c.rotate(90)
    # change color
    c.setFillColorRGB(0,0,0.77)
    # say hello (note after rotate the y coord needs to be negative!)
    c.drawString(3*inch, -3*inch, "Hello World")
    c.showPage()
    c.save()

if __name__ == "__main__":
    hello_pdf()
