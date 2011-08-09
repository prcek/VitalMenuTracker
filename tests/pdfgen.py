#!/usr/bin/python2.6

import sys
import os

pathname, scriptname = os.path.split(sys.argv[0])
sys.path.insert(0, os.path.join(pathname,'../libs/reportlab.zip'))

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.lib.units import inch,mm,cm

CARDS_PAGE_SIZE=A4 #(22*cm,30*cm)
CARDS_PAGE_BORDER_RECT=(cm,cm,CARDS_PAGE_SIZE[0]-2*cm,CARDS_PAGE_SIZE[1]-2*cm)

CARDS_PAGE_BORDER_COLOR=HexColor('#f0f0f0')

CARDS_COLS=2
CARDS_ROWS=5


def draw_card(c,max_width,max_height):
    c.saveState()
    c.setFont("Helvetica", 10)
    # choose some colors
    c.setStrokeColorRGB(0.2,0.5,0.3)
    c.setFillColorRGB(1,0,1)
#    c.translate(0,3*mm)
    c.rect(0,0,max_width,max_height)
    c.drawString(0,0, "Hello Worlxxxd")
    c.restoreState()

def draw_cards(c):
#    c.setFont("Helvetica", 80) 
    c.setStrokeColor(CARDS_PAGE_BORDER_COLOR)
    c.rect(*CARDS_PAGE_BORDER_RECT)
    for x in range(0,CARDS_COLS):
        for y in range(0,CARDS_ROWS):
            c.saveState()
            c.translate(CARDS_PAGE_BORDER_RECT[0]+x*(CARDS_PAGE_BORDER_RECT[2]/CARDS_COLS),CARDS_PAGE_BORDER_RECT[1]+y*(CARDS_PAGE_BORDER_RECT[3]/CARDS_ROWS))
            draw_card(c,CARDS_PAGE_BORDER_RECT[2]/CARDS_COLS, CARDS_PAGE_BORDER_RECT[3]/CARDS_ROWS)
            c.restoreState()

def cards():
    c = canvas.Canvas(os.path.join(pathname,"cards.pdf"),pagesize=CARDS_PAGE_SIZE)    
    draw_cards(c)
    c.showPage()
    draw_cards(c)
    c.showPage()
    c.save()

def hello_pdf():
    c = canvas.Canvas(os.path.join(pathname,"hello.pdf"))
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
    c.drawString(3*inch, -3*inch, "Hello Worlxxxd")
    c.showPage()
    c.save()

if __name__ == "__main__":
    hello_pdf()
    cards()
