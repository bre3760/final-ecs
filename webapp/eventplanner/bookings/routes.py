import os
import json
from flask import (render_template, url_for, flash, send_file,
                   redirect, request, abort, Blueprint, jsonify, current_app, make_response, send_from_directory)
from flask_login import current_user, login_required
from eventplanner import db, csrf
from eventplanner.models import User, Role, UserRoles, Event, EventStaff, Ticket, event_schema, events_schema, UserBookings

import qrcode
from PIL import Image
import secrets
from datetime import datetime
# for emails
from eventplanner.emails.routes import generate_email
from eventplanner.utilities.pdfGen import create_pdf_receipt


# for payments
bookings = Blueprint('bookings', __name__)


def createQR(data):
    # data = "https://www.thepythoncode.com"
    random_hex = secrets.token_hex(16)
    # output file name
    filename = random_hex + ".png"
    # generate qr code
    img = qrcode.make(data)
    # save img to a file
    picture_path = os.path.join(
        current_app.root_path, 'static/booking_qr_codes/', filename)
    img.save(picture_path)

    return filename


@bookings.route("/generate-booking/", methods=['POST', 'GET'])
@csrf.exempt
@login_required
def create_booking():
    all_qr_names = []
    all_event_ticket_info = []
    total_for_booking = 0
    total_for_tickets = 0.00
    if request.method == 'POST':
        try:
            # // booked_tickets = [ {ticket_id: 2, booked_num: 2}, {ticket_id: 12, booked_num: 4}]
            data = request.get_json()
            print("data received is: ", data)
            statusOfPayment = "not payed"

            # check if booking user is a manager or not
            isManager = False
            userToCheck = User.query.get(current_user.id)
            for role in userToCheck.roles:
                if "Manager" in role.name:
                    isManager = True

            if isManager is False:
                # print("user is not a manager", userToCheck.id)

                for ticketToBook in data:
                    total_for_tickets = 0
                    if int(ticketToBook["booked_num"]) == 0:
                        continue
                    else:
                        # check if the user is buying more tickets of the same type for the same event
                        eventOfTicketID = Ticket.query.get(
                            ticketToBook["ticket_id"]).event_id
                        eventInQuestion = Event.query.get(
                            eventOfTicketID)
                        print("event",eventOfTicketID)
                        if UserBookings.query.filter_by(user_id=current_user.id,
                                                        event_id=eventOfTicketID,
                                                        ticket_id=ticketToBook["ticket_id"],
                                                        payment_status=statusOfPayment).first():

                            if Ticket.query.get(ticketToBook["ticket_id"]):

                                ticketInQuestion = Ticket.query.get(
                                    int(ticketToBook["ticket_id"]))
                                print("ticket",ticketInQuestion)
                                availableToPurchase = ticketInQuestion.num_tickets - \
                                    int(ticketInQuestion.num_bought)
                                if availableToPurchase >= int(ticketToBook["booked_num"]):
                                    print("here")
                                    ExistingBooking = UserBookings.query.filter_by(user_id=current_user.id,
                                                                                   event_id=eventOfTicketID,
                                                                                   ticket_id=ticketToBook["ticket_id"],
                                                                                   payment_status=statusOfPayment).first()
                                    ExistingBooking.number_booked += int(
                                        ticketToBook["booked_num"])
                                    ticketInQuestion.num_bought += int(
                                        ticketToBook["booked_num"])
                                    ticketActualPriceFromDB = ticketInQuestion.price

                                    total_for_tickets += ticketActualPriceFromDB * \
                                        ExistingBooking.number_booked  # number booked by user

                                    # print("partial total", total_for_booking)
                                    if ExistingBooking.image_file == 'default_qr':
                                        dataForQR = {"ticket_id": ticketToBook["ticket_id"],
                                                     "event_id": eventOfTicketID,
                                                     "user_id": current_user.id,
                                                     "status": statusOfPayment}
                                        qr_image = createQR(dataForQR)

                                        ExistingBooking.image_file = qr_image
                                    all_qr_names.append(
                                        ExistingBooking.image_file)
                                    # for the pdf
                                    # print("before data for pdf")
                                    # try:
                                    if statusOfPayment == 'not payed':
                                        stat = 'Not Paid'
                                    else:
                                        stat = 'Paid'
                                    dataForPDF = {
                                        "event-title": str(eventInQuestion.title),
                                        "ticket-type": ticketInQuestion.ticket_type,
                                        "num": str(ExistingBooking.number_booked),
                                        "status": stat,
                                        "total":  "{:.2f}".format(total_for_tickets),
                                        "start time": str(eventInQuestion.time_from.strftime("%H:%M")),
                                        "date": str(eventInQuestion.event_date.strftime("%Y-%m-%d")),
                                        "location": str(eventInQuestion.location),
                                        "info": str(eventInQuestion.address) + ' ' + str(eventInQuestion.city)
                                    }
                                    # print(dataForPDF, "data foe pdf")
                                    all_event_ticket_info.append(
                                        dataForPDF)
                                    # except Exception as e:
                                    #     print(str(e))

                                    db.session.commit()  #
                                else:
                                    result = {
                                        "result": "not enough ticket available"}
                                    return jsonify(result)

                        else:  # the booking combination does not already exist so create a new one
                            print("in the else")
                            if Ticket.query.get(ticketToBook["ticket_id"]):
                                print("if ticket")
                                ticketInQuestion = Ticket.query.get(
                                    ticketToBook["ticket_id"])
                                availableToPurchase = ticketInQuestion.num_tickets - \
                                    int(ticketInQuestion.num_bought)
                                if availableToPurchase >= int(ticketToBook["booked_num"]):
                                    print("if available")
                                    ticketTYPE = Ticket.query.get(
                                        ticketToBook["ticket_id"]).ticket_type
                                    ticketActualPriceFromDB = Ticket.query.get(
                                        ticketToBook["ticket_id"]).price

                                    dataForQR = {"ticket_id": ticketToBook["ticket_id"],
                                                 "event_id": eventOfTicketID,
                                                 "user_id": current_user.id,
                                                 "status": statusOfPayment}
                                    print("after qr data")
                                    qr_image = createQR(dataForQR)
                                    all_qr_names.append(qr_image)
                                    bookingToAdd = UserBookings(user_id=current_user.id,
                                                                event_id=eventOfTicketID,
                                                                ticket_id=ticketToBook["ticket_id"],
                                                                ticket_type=ticketTYPE,
                                                                number_booked=int(
                                                                    ticketToBook["booked_num"]),
                                                                number_scanned=0,
                                                                payment_status=statusOfPayment,
                                                                image_file=qr_image)
                                    print("after booking to add")
                                    ticketInQuestion.num_bought += int(
                                        ticketToBook["booked_num"])
                                    total_for_tickets += ticketActualPriceFromDB * bookingToAdd.number_booked
                                    if statusOfPayment == 'not payed':
                                        stat = 'Not Paid'
                                    else:
                                        stat = 'Paid'
                                    db.session.add(bookingToAdd)
                                    print("after db.add")
                                    dataForPDF = {
                                        "event-title": eventInQuestion.title,
                                        "ticket-type": ticketInQuestion.ticket_type,
                                        "num": str(bookingToAdd.number_booked),
                                        "status": stat,
                                        "total": "{:.2f}".format(total_for_tickets),
                                        "start time": str(eventInQuestion.time_from.strftime("%H:%M")),
                                        "date": str(eventInQuestion.event_date.strftime("%Y-%m-%d")),
                                        "location": eventInQuestion.location,
                                        "info": eventInQuestion.address + ' ' + eventInQuestion.city
                                    }
                                    all_event_ticket_info.append(dataForPDF)
                                    print("after append")
                                else:
                                    result = {
                                        "result": "not enough ticket available"}
                                    return jsonify(result)
                print("before commit")
                db.session.commit()
                # pdf generation
                # print(dataForPDF)
                # print("befpre")
                random_hex = secrets.token_hex(16)
                # pdfname = 'testingpdfbooking'
                pdfname = random_hex
                # print(pdfname, "name of pdf ")
                # print(all_qr_names)

                pdf_receipt = create_pdf_receipt(
                    pdfname, all_qr_names, all_event_ticket_info)
                # print("aftrer pdf")
                # print("before email")
                # send email receipt
                subject = 'Your receipt'
                # emailTo = 'brendandavidpolidori@gmail.com'
                emailTo = current_user.email
                content = 'Thank you for your purchase. Please find your tickets attached'
                filename = pdf_receipt
                # print("filename of pdf", filename)
                email = generate_email(subject, emailTo, content, filename)
                print("after email")
                return redirect(url_for('bookings.display_booking'), code=302)
            else:
                result = {"result": "error",
                          "type": "As a Manager you cannot book an event"}
                return jsonify(result)
            # return redirect(url_for('bookings.display_booking'), code=302)
        except Exception as e:
            result = {"result": "error", "type": str(e)}
            return jsonify(result)


@bookings.route("/display-booking/", methods=['POST', 'GET'])
@csrf.exempt
def display_booking():
    userbookingsAll = UserBookings.query.filter_by(user_id=current_user.id)
    eventsOfBookings = []
    for booking in userbookingsAll:
        ev = Event.query.get(booking.event_id)
        eventsOfBookings.append(ev)
    return render_template('bookings/user_bookings.html', all_bookings=userbookingsAll, user=current_user,events = eventsOfBookings)


@bookings.route('/download/<bid>', methods=['GET', 'POST'])
def download(bid):
    print(bid)
    # It is important to reiterate that UPLOAD_FOLDER must be relative for this to work, e.g. not start with a /.
    # uploads = os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER'])
    # return send_from_directory(directory=uploads, filename=filename)
    booking = UserBookings.query.get(bid)
    eventInQuestion = Event.query.get(booking.event_id)
    ticketInQuestion = Ticket.query.get(booking.ticket_id)
    total_for_tickets = booking.number_booked * ticketInQuestion.price

    dataForPDF = {
        "event-title": eventInQuestion.title,
        "ticket-type": ticketInQuestion.ticket_type,
        "num": str(booking.number_booked),
        "status": booking.payment_status,
        "total": "{:.2f}".format(total_for_tickets),
        "start time": str(eventInQuestion.time_from.strftime("%H:%M")),
        "date": str(eventInQuestion.event_date.strftime("%Y-%m-%d")),
        "location": eventInQuestion.location,
        "info": eventInQuestion.address + ' ' + eventInQuestion.city
    }

    random_hex = secrets.token_hex(16)
    pdfname = random_hex
    all_event_ticket_info = []
    all_event_ticket_info.append(dataForPDF)
    all_qr_names = [booking.image_file]
    pdf_receipt = create_pdf_receipt(
        pdfname, all_qr_names, all_event_ticket_info)

    return send_file(pdf_receipt, as_attachment=True)
