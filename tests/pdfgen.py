#!/usr/bin/python2.6
 # -*- coding: utf-8 -*-

import sys
import os

pathname, scriptname = os.path.split(sys.argv[0])
sys.path.insert(0, os.path.join(pathname,'../libs/reportlab.zip'))

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.lib.units import inch,mm,cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


import reportlab
folderFonts = os.path.dirname(reportlab.__file__) + os.sep + 'fonts'
pdfmetrics.registerFont(TTFont('DejaVuSansMono', os.path.join(folderFonts,'DejaVuSansMono.ttf')))
pdfmetrics.registerFont(TTFont('DejaVuSans', os.path.join(folderFonts,'DejaVuSans.ttf')))
pdfmetrics.registerFont(TTFont('DejaVuSansBold', os.path.join(folderFonts,'DejaVuSansBold.ttf')))


TEST_TEXT = "Příliš žluťoučký kůň úpěl ďábelské ódy"

CARDS_PAGE_SIZE=A4 #(22*cm,30*cm)
CARDS_PAGE_BORDER_RECT=(2*cm,1.5*cm,CARDS_PAGE_SIZE[0]-4*cm,CARDS_PAGE_SIZE[1]-2.5*cm)

CARDS_PAGE_BORDER_COLOR=None # HexColor('#f0f0f0')
CARDS_PAGE_CARD_CROP_BORDER_COLOR=HexColor('#e0e0e0')
CARDS_PAGE_CARD_BLACK_COLOR=HexColor('#000000')
CARDS_PAGE_CARD_WHITE_COLOR=HexColor('#FFFFFF')
CARDS_PAGE_CARD_TEXT_TOP_LINE_0 = "TOP TEXT L 0"
CARDS_PAGE_CARD_TEXT_TOP_LINE_1 = "TOP TEXT L 1"
CARDS_PAGE_CARD_TEXT_TOP_LINE_2 = "TOP TEXT L 2"

CARDS_COLS=2
CARDS_ROWS=5


def draw_card(c,max_width,max_height):
    c.saveState()
#    c.setFont("Helvetica", 10)
    c.setFont('DejaVuSansBold', 10)

    # choose some colors
    if CARDS_PAGE_CARD_CROP_BORDER_COLOR:
        c.setStrokeColor(CARDS_PAGE_CARD_CROP_BORDER_COLOR)
        c.rect(0,0,max_width,max_height)

    c.translate(5*mm,5*mm)
    width = max_width-10*mm
    height = max_height -10*mm
    widths=(width-15*mm,15*mm) 
    heights=(15*mm,height-25*mm,10*mm)

    c.setStrokeColor(CARDS_PAGE_CARD_BLACK_COLOR) 
    c.setFillColor(CARDS_PAGE_CARD_BLACK_COLOR)
    c.rect(0,0,width,height)


    c.rect(0,height-heights[0],widths[0],heights[0],fill=1)
    c.line(0,height-heights[0],width,height-heights[0])
    c.setFillColor(CARDS_PAGE_CARD_WHITE_COLOR)
    hs = heights[0]/20
    h = (heights[0]-hs)/2
    c.setFontSize(h-hs)
    c.drawCentredString(widths[0]/2,height-h+hs,CARDS_PAGE_CARD_TEXT_TOP_LINE_0)
    c.setFontSize(h/2-hs)
    c.drawCentredString(widths[0]/2,height-h+hs-(h/2),CARDS_PAGE_CARD_TEXT_TOP_LINE_1)
    c.drawCentredString(widths[0]/2,height-h+hs-(h),CARDS_PAGE_CARD_TEXT_TOP_LINE_2)
    c.setFillColor(CARDS_PAGE_CARD_BLACK_COLOR)

    c.rect(0,0,widths[0],heights[2],fill=1)
    c.line(0,heights[2],width,heights[2])

    c.line(widths[0],0,widths[0],height)

    c.setStrokeColor(CARDS_PAGE_CARD_WHITE_COLOR) 
    c.setFillColor(CARDS_PAGE_CARD_WHITE_COLOR)
    c.drawString(0,0, "Hello Worlxxxd")
    c.restoreState()

def draw_cards(c):
#    c.setFont("Helvetica", 80) 
    if CARDS_PAGE_BORDER_COLOR:
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
    #c.setFont("Helvetica", 80)
    c.setFont('DejaVuSansBold', 30)
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
    c.setFont('DejaVuSansBold', 20)
    c.drawString(0, -3*inch, "DejaVuSansBold %s"% TEST_TEXT)
    c.setFont('DejaVuSans', 20)
    c.drawString(0, -4*inch, "DejaVuSans %s" %TEST_TEXT)
    c.setFont('DejaVuSansMono', 20)
    c.drawString(0, -5*inch, "DejaVuSansMono %s" %TEST_TEXT)



    c.showPage()
    c.save()

if __name__ == "__main__":
    hello_pdf()
    cards()
