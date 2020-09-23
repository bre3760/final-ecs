import json
from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint, jsonify, current_app, make_response)
from flask_login import current_user, login_required
from eventplanner import db, csrf
from eventplanner.models import User, Role, UserRoles, Event, EventStaff, Ticket, event_schema, events_schema, UserBookings

import qrcode
from PIL import Image
import secrets
from datetime import datetime
import os
import reportlab
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
# ###################################
# Help


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
# title = 'Your Tickets'
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

# pdf = canvas.Canvas(savename)
# # drawMyRuler(pdf)

# # logo
# y_logo = 720
# x_logo = 250
# pdf.drawInlineImage(image, x_logo, y_logo, 90, 90)
# pdf.line(30, y_logo - 10, 570, y_logo - 10)  # y 710


# # ###################################
# # 2) Title
# from reportlab.pdfbase import pdfmetrics
# pdf.setFont('Helvetica', 16)
# y_title = y_logo - 30
# x_title = 295
# pdf.drawCentredString(x_title, y_title, title)
# # ###################################
# # ticket indormation

# y_start = 500
# x_start = 390
# tickets_booked = ['0d41b98c53b532874bb2d939f72d43c7.png',
#                   '303b4894daf50d6cb41c84b2480b488c.png',
#                   '40beaef9d16b464260e090f3b4d4e35d.png',
#                   '50f4aa559e2c6b79d4331f040afb516f.png',
#                   '789c1b50dff97de840dd86919792d141.png']


# def textforticket(x_start, y_start):
#     textLines = [
#         'Event title',
#         'total payed',
#         'start time',
#         'date of event',
#         'event location',
#         'additional info'
#     ]
#     text = pdf.beginText(x_start, y_start)
#     text.setFont("Courier", 12)
#     text.setFillColor(colors.black)
#     for line in textLines:
#         text.textLine(line)
#     pdf.drawText(text)


# remove_each_iter = 0
# i = 0
# for ticket in tickets_booked:
#     base = os.path.join(
#         '/Users/brendanpolidori/Desktop/final-ecs/webapp/eventplanner', 'static/emails/test_bookings/')
#     abs_path_ticket = base + ticket
#     if i < 3:
#         textforticket(30, y_start - remove_each_iter + 150)
#         #        x1   y1    x2     y2
#         pdf.line(30, y_start - remove_each_iter + 165,
#                  350, y_start - remove_each_iter + 165)
#         pdf.drawInlineImage(abs_path_ticket, x_start,
#                             y_start - remove_each_iter, 180, 180)
#     else:
#         i = 0
#         remove_each_iter = 0
#         pdf.showPage()
#         pdf.line(30, y_start - remove_each_iter + 165,
#                  350, y_start - remove_each_iter + 165)
#         textforticket(30, y_start - remove_each_iter + 150)
#         pdf.drawInlineImage(abs_path_ticket, x_start,
#                             y_start - remove_each_iter, 180, 180)

#     remove_each_iter += 180
#     i = i + 1

# pdf.save()


def create_pdf_receipt(pdfName, ticketsBooked, ticket_event_info):
    print("pdf gen function")
    print(ticketsBooked)
    print(ticket_event_info)
    print("all data inside")
    try:

        fileName = pdfName + '.pdf'
        title = 'Your Tickets'

        # where the logo is stored
        picture_path = os.path.join(
            current_app.root_path, 'static/', 'logo_events.jpeg')
        print(picture_path)
        # where to save the pdf file
        # filepath = os.path.join(
        #     current_app.root_path, '/static/booking-payment-pdf/', fileName)
        image = picture_path
        # name with which to save the pdf file
        savename = os.path.join(current_app.root_path,
                                'static/booking-payment-pdf/', fileName)
        print("after paths")
        pdf = canvas.Canvas(savename)
        y_logo = 720
        x_logo = 250
        pdf.drawInlineImage(image, x_logo, y_logo, 90, 90)
        pdf.line(30, y_logo - 10, 570, y_logo - 10)  # y 710

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
        tickets_booked = ticketsBooked

        def textforticket(x_start, y_start, dict_with_info):
            textLines = [
                'Event Title: ' + dict_with_info["event-title"],
                'Total price: ' + str(dict_with_info["total"]) + '€',
                'Start Time: ' + dict_with_info["start time"],
                'Date of Event: ' + dict_with_info["date"],
                'Event Location: ' + dict_with_info["location"],
                'Additional Information: ' + dict_with_info["info"]
            ]
            text = pdf.beginText(x_start, y_start)
            text.setFont("Courier", 12)
            text.setFillColor(colors.black)
            for line in textLines:
                text.textLine(line)
            pdf.drawText(text)

        remove_each_iter = 0
        i = 0
        j = 0
        for ticket in tickets_booked:
            base = os.path.join(current_app.root_path,
                                'static/booking_qr_codes/')
            abs_path_ticket = base + ticket
            if i < 3:
                textforticket(30, y_start - remove_each_iter +
                              150, ticket_event_info[j])
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
                textforticket(30, y_start - remove_each_iter +
                              150, ticket_event_info[j])
                pdf.drawInlineImage(abs_path_ticket, x_start,
                                    y_start - remove_each_iter, 180, 180)

            remove_each_iter += 180
            i = i + 1
            j = j + 1

        pdf.save()
    except Exception as e:
        print(str(e))
    return savename
