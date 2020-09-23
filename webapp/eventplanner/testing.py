# class Roles():
# yo
#     def setname(self, name):
#         self.name = name

#     def getname():
#         return self.name


# role1 = Roles()
# role1.setname('Manager')
# print(role1.name)
# role2 = Roles()
# role2.setname('Moderator')
# print(role2.name)

# listofroles = []
# listofroles.append(role1)
# listofroles.append(role2)

# for role in listofroles:
#     if 'Manager' in role.name:
#         print('found')
# nuu = [x for x in range(1, 10)]
# print(nuu)
# class role1:
#     x = 1
#     name = ['Manager']


# class role2:
#     x = 2
#     name = ['Staff']


# class user:
#     y = 1
#     roles = [role1(), role2()]


# userme = user()
# # print(userme.roles[1].name)
# # for role in userme.roles:
# #     print(role.name)
# for role in userme.roles:
#     if 'Staff' in role.name:
#         print('found')
# class ticket:
#     def __init__(self, ticket_type, num_tickets, price):
#         self.ticket_type = ticket_type
#         self.num_tickets = num_tickets
#         self.price = price


# tickets = []
# ticket1 = ticket('ticket1', 22, 13)
# tickets.append(ticket1)
# for tik in tickets:
#     print(tik.ticket_type, tik.num_tickets, tik.price)
# ticket2 = ticket('ticket1', 27, 13)


# st = [1, 2, 3]
# pp = st.pop(2)
# print(pp)
# print(st)


# ev_and_st = [(1, "not"), (1, "yes"), (1, "not"), (1, "yes")]
# ll = []
# for tp in ev_and_st:
#     if tp not in ll:
#         ll.append(tp)
# print(ll)
################################################################################
################################################################################
################################################################################
################################################################################

# import os
# import reportlab
# from PIL import Image
# from reportlab.pdfgen import canvas
# from reportlab.lib.pagesizes import letter
# # ###################################
# # Help


# def drawMyRuler(pdf):
#     pdf.drawString(100, 810, 'x100')
#     pdf.drawString(200, 810, 'x200')
#     pdf.drawString(300, 810, 'x300')
#     pdf.drawString(400, 810, 'x400')
#     pdf.drawString(500, 810, 'x500')

#     pdf.drawString(10, 100, 'y100')
#     pdf.drawString(10, 200, 'y200')
#     pdf.drawString(10, 300, 'y300')
#     pdf.drawString(10, 400, 'y400')
#     pdf.drawString(10, 500, 'y500')
#     pdf.drawString(10, 600, 'y600')
#     pdf.drawString(10, 700, 'y700')
#     pdf.drawString(10, 800, 'y800')


# # ###################################
# # Content
# fileName = 'MyDoc.pdf'
# documentTitle = 'Document title!'
# title = 'Tasmanian devil'
# subTitle = 'The largest carnivorous marsupial'
# textLines = [
#     'The Tasmanian devil (Sarcophilus harrisii) is',
#     'a carnivorous marsupial of the family',
#     'Dasyuridae.'
# ]

# picture_path = os.path.join(
#     '/Users/brendanpolidori/Desktop/final-ecs/webapp/eventplanner', 'static/emails', 'logo_events.jpeg')
# filepath = os.path.join(
#     '/Users/brendanpolidori/Desktop/final-ecs/webapp/eventplanner', 'static/emails/', fileName)
# # # image = 'tasmanianDevil.jpg'
# image = picture_path
# savename = '/Users/brendanpolidori/Desktop/final-ecs/webapp/eventplanner/static/emails/MyDoc.pdf'
# # # #########################################################################################################
# # #########################################################################################################
# # #########################################################################################################
# # #########################################################################################################
# # 0) Create document

# pdf = canvas.Canvas(savename, pagesize=letter)
# width, height = letter
# pdf.setTitle(documentTitle)
# drawMyRuler(pdf)

# from reportlab.pdfbase import pdfmetrics
# pdf.setFont('Helvetica', 12)


# # ###################################
# # 2) Title
# pdf.drawCentredString(300, 770, title)


# # ###################################
# # 2) Sub Title
# # RGB - Red Green and Blue
# pdf.setFillColorRGB(0, 0, 255)
# pdf.setFont("Courier-Bold", 24)
# pdf.drawCentredString(290, 720, subTitle)


# # ###################################
# # 3) Draw a line
# # pdf.line(30, 690, 550, 690)
# # pdf.setLineWidth(.3)
# # pdf.drawString(30, 750, 'OFFICIAL COMMUNIQUE')
# # pdf.drawString(30, 735, 'OF ACME INDUSTRIES')
# # pdf.drawString(500, 750, "12/12/2010")
# # pdf.line(480, 747, 580, 747)
# # pdf.drawString(275, 725, 'AMOUNT OWED:')
# # pdf.drawString(500, 725, "$1,000.00")
# # pdf.line(378, 723, 580, 723)
# # pdf.drawString(30, 703, 'RECEIVED BY:')
# # pdf.line(120, 700, 580, 700)
# # pdf.drawString(120, 703, "JOHN DOE")

# # ###################################
# # 4) Text object :: for large amounts of text
# # from reportlab.lib import colors

# # text = pdf.beginText(40, 650)
# # text.setFont("Courier", 12)
# # text.setFillColor(colors.red)
# # for line in textLines:
# #     text.textLine(line)

# # pdf.drawText(text)


# # ###################################
# # 5) Draw a image
# pdf.drawInlineImage(image, 250, 700, 100, 100)

# # canvas.drawInlineImage(self, image, x, y, width=None, height=None)
# """
# The drawInlineImage method places an image on the canvas.
# The image parameter may be either a PIL Image object or an image filename.
# Many common file formats are accepted including GIF and JPEG.
# It returns the size of the actual image in pixels as a (width, height) tuple.
# """
# pdf.save()
#########################################################################################################
#########################################################################################################
#########################################################################################################
#########################################################################################################
import os
import reportlab
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
# ###################################
# Help


def drawMyRuler(pdf):
    pdf.drawString(100, 810, 'x100')
    pdf.drawString(200, 810, 'x200')
    pdf.drawString(300, 810, 'x300')
    pdf.drawString(400, 810, 'x400')
    pdf.drawString(500, 810, 'x500')

    pdf.drawString(10, 100, 'y100')
    pdf.drawString(10, 200, 'y200')
    pdf.drawString(10, 300, 'y300')
    pdf.drawString(10, 400, 'y400')
    pdf.drawString(10, 500, 'y500')
    pdf.drawString(10, 600, 'y600')
    pdf.drawString(10, 700, 'y700')
    pdf.drawString(10, 800, 'y800')


# ###################################
# Content
fileName = 'MyDoc.pdf'
documentTitle = 'Document title!'
title = 'Your Tickets'
subTitle = 'The largest carnivorous marsupial'
textLines = [
    'The Tasmanian devil (Sarcophilus harrisii) is',
    'a carnivorous marsupial of the family',
    'Dasyuridae.'
]

picture_path = os.path.join(
    '/Users/brendanpolidori/Desktop/final-ecs/webapp/eventplanner', 'static/', 'logo_events.jpeg')
filepath = os.path.join(
    '/Users/brendanpolidori/Desktop/final-ecs/webapp/eventplanner', 'static/emails/', fileName)
# # image = 'tasmanianDevil.jpg'
image = picture_path
savename = '/Users/brendanpolidori/Desktop/final-ecs/webapp/eventplanner/static/emails/MyDoc.pdf'
# # #########################################################################################################
# #########################################################################################################
# #########################################################################################################
# #########################################################################################################
# 0) Create document

pdf = canvas.Canvas(savename)
drawMyRuler(pdf)

# logo
y_logo = 720
x_logo = 250
pdf.drawInlineImage(image, x_logo, y_logo, 90, 90)
pdf.line(30, y_logo - 10, 570, y_logo - 10)  # y 710

# event by polito info
pdf.setFont('Helvetica', 16)
pdf.drawString(30, 790, 'EventsByPolito')
pdf.setFont('Helvetica', 12)
pdf.setFillColorRGB(0, 0, 255)
pdf.drawString(30, 775, 'http://homeserverngg.ddns.net/')
pdf.setFillColorRGB(0, 0, 0)
pdf.drawString(30, 760, '1600 Pennsylvania Avenue NW')


# ###################################
# 2) Title
from reportlab.pdfbase import pdfmetrics
pdf.setFont('Helvetica', 16)
y_title = y_logo - 30
x_title = 295
pdf.drawCentredString(x_title, y_title, title)
# ###################################
# ticket indormation

y_start = 500
x_start = 390
tickets_booked = ['0d41b98c53b532874bb2d939f72d43c7.png',
                  '303b4894daf50d6cb41c84b2480b488c.png',
                  '40beaef9d16b464260e090f3b4d4e35d.png',
                  '50f4aa559e2c6b79d4331f040afb516f.png',
                  '789c1b50dff97de840dd86919792d141.png']


def textforticket(x_start, y_start):
    textLines = [
        'Event title',
        'total payed',
        'start time',
        'date of event',
        'event location',
        'additional info'
    ]
    text = pdf.beginText(x_start, y_start)
    text.setFont("Courier", 12)
    text.setFillColor(colors.black)
    for line in textLines:
        text.textLine(line)
    pdf.drawText(text)


remove_each_iter = 0
i = 0
for ticket in tickets_booked:
    base = os.path.join(
        '/Users/brendanpolidori/Desktop/final-ecs/webapp/eventplanner', 'static/emails/test_bookings/')
    abs_path_ticket = base + ticket
    if i < 3:
        textforticket(30, y_start - remove_each_iter + 150)
        #        x1   y1    x2     y2
        pdf.line(30, y_start - remove_each_iter + 165,
                 350, y_start - remove_each_iter + 165)
        pdf.drawInlineImage(abs_path_ticket, x_start,
                            y_start - remove_each_iter, 180, 180)
    else:
        i = 0
        remove_each_iter = 0
        pdf.showPage()
        pdf.line(30, y_start - remove_each_iter + 165,
                 350, y_start - remove_each_iter + 165)
        textforticket(30, y_start - remove_each_iter + 150)
        pdf.drawInlineImage(abs_path_ticket, x_start,
                            y_start - remove_each_iter, 180, 180)

    remove_each_iter += 180
    i = i + 1

pdf.save()
