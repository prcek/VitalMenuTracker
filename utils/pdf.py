

import sys
sys.path.insert(0, 'libs/reportlab.zip')
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import os
import reportlab
folderFonts = os.path.dirname(reportlab.__file__) + os.sep + 'fonts'


import logging
import StringIO

def pdftest(text=None):
    logging.info('pdftest')
    output = StringIO.StringIO()
   # pdfmetrics.registerTypeFace(pdfmetrics.EmbeddedType1Face(
   #         os.path.join(folderFonts, 'DarkGardenMK.afm'),
   #         os.path.join(folderFonts, 'DarkGardenMK.pfb')))
   # pdfmetrics.registerFont(pdfmetrics.Font(
   #         'DarkGardenMK', 'DarkGardenMK', 'WinAnsiEncoding'))

    pdfmetrics.registerFont(TTFont('Vera', os.path.join(folderFonts,'Vera.ttf')))


    c = canvas.Canvas(output)    
    #c.setFont('DarkGardenMK', 16)
    c.setFont('Vera', 16)
    if text:
        c.drawString(100,100,text)
    else:
        c.drawString(100,100,'pdftest')

    c.showPage()
    c.save()
    logging.info('ok')    
    return output.getvalue() 

    
