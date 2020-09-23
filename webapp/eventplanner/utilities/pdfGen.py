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
from reportlab.pdfbase import pdfmetrics


def create_pdf_receipt(pdfName, ticketsBooked, ticket_event_info):
    # print("pdf gen function")
    # print(ticketsBooked)
    # print(ticket_event_info)
    # print("all data inside")
    try:

        fileName = pdfName + '.pdf'
        title = 'Your Tickets'
        # where the logo is stored
        picture_path = os.path.join(
            current_app.root_path, 'static/', 'logo_events.jpeg')
        # print(picture_path)
        image = picture_path
        # name with which to save the pdf file
        savename = os.path.join(current_app.root_path,
                                'static/booking-payment-pdf/', fileName)
        # print("after paths")
        pdf = canvas.Canvas(savename)
        y_logo = 720
        x_logo = 250
        pdf.drawInlineImage(image, x_logo, y_logo, 90, 90)
        pdf.line(30, y_logo - 10, 570, y_logo - 10)  # y 710

        # ###################################
        # 2) Title
        pdf.setFont('Helvetica', 16)
        y_title = y_logo - 30
        x_title = 295
        pdf.drawCentredString(x_title, y_title, title)

        pdf.setFont('Helvetica', 16)
        pdf.drawString(30, 790, 'EventsByPolito')
        pdf.setFont('Helvetica', 12)
        pdf.setFillColorRGB(0, 0, 255)
        pdf.drawString(30, 775, 'http://homeserverngg.ddns.net/')
        pdf.setFillColorRGB(0, 0, 0)
        pdf.drawString(30, 760, '1600 Pennsylvania Avenue NW')

        # ###################################
        # ticket indormation
        y_start = 500
        x_start = 390
        tickets_booked = ticketsBooked

        def textforticket(x_start, y_start, dict_with_info):
            textLines = [
                'Event Title: ' + dict_with_info["event-title"],
                'Ticket type: ' + dict_with_info["ticket-type"],
                'Scan ' + dict_with_info["num"] + ' times',
                'Status of Payment: ' + dict_with_info["status"],
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
