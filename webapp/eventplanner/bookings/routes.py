import os
import json
from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint, jsonify, current_app, make_response)
from flask_login import current_user, login_required
from eventplanner import db, csrf
from eventplanner.models import User, Role, UserRoles, Event, EventStaff, Ticket, event_schema, events_schema, UserBookings

import qrcode
from PIL import Image
import secrets


# for payments
bookings = Blueprint('bookings', __name__)


def createQR(data):
    #data = "https://www.thepythoncode.com"
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


# @bookings.route("/book/event/<int:event_id>/")
# def book(event_id):
#     event = Event.query.get_or_404(event_id)
#     # return render_template('bookings/book.html', title=event.title, event=event)
#     return render_template('bookings/frankenstein.html', title=event.title, event=event)
# https://stackoverflow.com/questions/26954122/how-can-i-pass-arguments-into-redirecturl-for-of-flask/26957478

@bookings.route("/generate-booking/", methods=['POST', 'GET'])
@csrf.exempt
@login_required
def create_booking():
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
                print("user is not a manager", userToCheck.id)

                for ticketToBook in data:
                    if int(ticketToBook["booked_num"]) == 0:
                        continue
                    else:
                        # check if the user is buying more tickets of the same type for the same event
                        eventOfTicketID = Ticket.query.get(
                            ticketToBook["ticket_id"]).event_id

                        if UserBookings.query.filter_by(user_id=current_user.id,
                                                        event_id=eventOfTicketID,
                                                        ticket_id=ticketToBook["ticket_id"],
                                                        payment_status=statusOfPayment).first():
                            if Ticket.query.get(ticketToBook["ticket_id"]):
                                ticketInQuestion = Ticket.query.get(
                                    ticketToBook["ticket_id"])
                                availableToPurchase = ticketInQuestion.num_tickets - \
                                    int(ticketInQuestion.num_bought)
                                if availableToPurchase >= ticketToBook["booked_num"]:
                                    ExistingBooking = UserBookings.query.filter_by(user_id=current_user.id,
                                                                                   event_id=eventOfTicketID,
                                                                                   ticket_id=ticketToBook["ticket_id"],
                                                                                   payment_status=statusOfPayment).first()
                                    ExistingBooking.number_booked += int(
                                        ticketToBook["booked_num"])
                                    ticketInQuestion.num_bought += int(
                                        ticketToBook["booked_num"])
                                    db.session.commit()  #
                                else:
                                    result = {
                                        "result": "not enough ticket available"}
                                    return jsonify(result)

                        else:  # the booking combination does not already exist so create a new one
                            if Ticket.query.get(ticketToBook["ticket_id"]):
                                ticketInQuestion = Ticket.query.get(
                                    ticketToBook["ticket_id"])
                                availableToPurchase = ticketInQuestion.num_tickets - \
                                    int(ticketInQuestion.num_bought)
                                if availableToPurchase >= ticketToBook["booked_num"]:
                                    ticketTYPE = Ticket.query.get(
                                        ticketToBook["ticket_id"]).ticket_type
                                    ticketActualPriceFromDB = Ticket.query.get(
                                        ticketToBook["ticket_id"]).price

                                    dataForQR = {"ticket_id": ticketToBook["ticket_id"],
                                                 "event_id": eventOfTicketID,
                                                 "user_id": current_user.id,
                                                 "status": statusOfPayment}
                                    qr_image = createQR(dataForQR)

                                    bookingToAdd = UserBookings(user_id=current_user.id,
                                                                event_id=eventOfTicketID,
                                                                ticket_id=ticketToBook["ticket_id"],
                                                                ticket_type=ticketTYPE,
                                                                number_booked=int(
                                                                    ticketToBook["booked_num"]),
                                                                number_scanned=0,
                                                                payment_status=statusOfPayment,
                                                                image_file=qr_image)
                                    db.session.add(bookingToAdd)
                                else:
                                    result = {
                                        "result": "not enough ticket available"}
                                    return jsonify(result)
                db.session.commit()
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
    return render_template('bookings/user_bookings.html', all_bookings=userbookingsAll, user=current_user)


# try:
#     data = request.get_json()
#     # json for a booking
#     # examplebookingJSON = {"event_id":1,
#     #                     "user_id":2,
#     #                     "total_price":22,
#     #                     "status":"not payed",
#     #                     "selected_tickets":[{"ticket_id":2,"quantity":3},{"ticket_id":3,"quantity":2}]}
#     eventID = data["event_id"]
#     userID = data["user_id"]
#     #totalPrice = data["total_price"]
#     statusOfPayment = data["status"]
#     selectedTickets = data["selected_tickets"]

#     # check if the user is a simple user or at least not a manager
#     isManager = False
#     userToCheck = User.query.get(userID)
#     for role in userToCheck.roles:
#         if "Manager" in role.name:
#             isManager = True

#     if isManager == False:
#         for ticketToBook in selectedTickets:
#             # check if the user is buying more tickets of the same type for the same event
#             if UserBookings.query.filter_by(user_id=userID,
#                                             event_id=eventID,
#                                             ticket_id=ticketToBook["ticket_id"],
#                                             payment_status=statusOfPayment).first():

#                 ExistingBooking = UserBookings.query.filter_by(
#                     user_id=userID, event_id=eventID, ticket_id=ticketToBook["ticket_id"], payment_status=statusOfPayment).first()
#                 ExistingBooking.number_booked += ticketToBook["quantity"]
#                 db.session.commit()
#             else:  # the booking combination does not already exist so create a new one
#                 if Ticket.query.get(ticketToBook["ticket_id"]):
#                     ticketTYPE = Ticket.query.get(
#                         ticketToBook["ticket_id"]).ticket_type
#                     ticketActualPriceFromDB = Ticket.query.get(
#                         ticketToBook["ticket_id"]).price

#                     bookingToAdd = UserBookings(user_id=userID,
#                                                 event_id=eventID,
#                                                 ticket_id=ticketToBook["ticket_id"],
#                                                 ticket_type=ticketTYPE,
#                                                 number_booked=ticketToBook["quantity"],
#                                                 number_scanned=0,
#                                                 payment_status=statusOfPayment)

#                     db.session.add(bookingToAdd)
#         db.session.commit()
#         result = {"result": "booking completed"}
#         return jsonify(result)
#     else:
#         result = {"result": "error",
#                   "type": "As a Manager you cannot book an event"}
#         return jsonify(result)
# except Exception as e:
#     result = {"result": "error", "type": str(e)}
#     return jsonify(result)

    # creating qr_codes
    # qr_names = []
    # for ticket in data:
    #         # print("hi", ticket)
    #     ticketJSON = ticket
    #     ticketJSON["user_id"] = current_user.id
    #     eventOfTicketID = Ticket.query.get(
    #         ticketJSON["ticket_id"]).event_id
    #     ticketJSON["event_id"] = eventOfTicketID
    #     ticketJSON["payment_status"] = "not payed"
    #     qr_names.append(createQR(ticketJSON))

    #     # creating the bookings in the db
    #     eventID = ticketJSON["event_id"]
    #     userID = data["user_id"]
    #     #totalPrice = data["total_price"]
    #     statusOfPayment = data["status"]
    #     selectedTickets = data["selected_tickets"]

    # check if the user is a simple user or at least not a manager
