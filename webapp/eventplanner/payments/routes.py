import os
import stripe
import json

from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint, jsonify, session, current_app)
from flask_login import current_user, login_required
from eventplanner import db, csrf
from eventplanner.models import User, Role, UserRoles, UserBookings, Event, EventStaff, Ticket, event_schema, events_schema
import qrcode
import secrets
from eventplanner.emails.routes import generate_email
from eventplanner.utilities.pdfGen import create_pdf_receipt


payments = Blueprint('payments', __name__)
stripe_keys = {

    'publishable_key': 'pk_test_51HAcdOHk1k68YjNlM3haniXPodOjeiqNyaBdDiZQUoTDGI81mzuaGe5RDwfgkk6ZZCH2n3w2SrzQeyOpKlS49X7Y009EVPj3jn',
    'secret_key': 'sk_test_51HAcdOHk1k68YjNlZdjWEVpvubke2tohmrK7U4CXEl4qXFJd0wpwoFtAUx64VrsBILvTXQ51M4e9fPhi5I4NTVZ400GySKRQxc'
}

stripe.api_key = stripe_keys['secret_key']

# Event title

# event date
# event location
# ticket type1
# ticket cost1
# ticket type2
# ticket cost2

@payments.route('/start-payment-flow', methods=['POST', 'GET'])
@csrf.exempt
@login_required
def start_payment_flow():
    if request.method == 'POST':
        # booked_tickets = [ {ticket_id: 2, booked_num: 2}, {ticket_id: 12, booked_num: 4}]
        payment_data = request.get_json()
        session['payment_data'] = payment_data
        ticket_id = payment_data[0]["ticket_id"]
        ticket = Ticket.query.get(ticket_id)
        event = Event.query.get(ticket.event_id)
        eventTitle = event.title
        eventDate = event.event_date
        eventLocation = event.location
        session['event-info'] = [eventTitle,eventDate,eventLocation]
        # session['event-date'] = eventDate
        # session['event-location'] = eventLocation
        tickets_info = []
        for ticket in payment_data:
            tt = Ticket.query.get(ticket["ticket_id"])
            tickets_info.append((tt.ticket_type, tt.price * int(ticket["booked_num"]) ))
        session["ticket-info"] = tickets_info
    return redirect(url_for('payments.get_example'), code=302)


@payments.route('/payment', methods=['GET'])
def get_example():
    # Display checkout page
    payment_data = session.get("payment_data", None)
    tot_price = calculate_order_amount(payment_data) / 100
    return render_template('payments/payment.html',
                            payment_data=payment_data,
                            tot_price=tot_price,
                            eventInfo = session.get("event-info",None),
                            ticketsInfo = session.get("ticket-info",None))


def calculate_order_amount(items):
    # Replace this constant with a calculation of the order's amount
    # Calculate the order total on the server to prevent
    # people from directly manipulating the amount on the client
    print("items at calculate order amount", items)
    # [ {ticket_id: 2, booked_num: 2}, {ticket_id: 12, booked_num: 45}]
    total_price = 0
    for ticketToBuy in items:
        ticket_id = int(ticketToBuy["ticket_id"])
        ticket_price = Ticket.query.get(ticket_id).price
        numberToBuy = int(ticketToBuy["booked_num"])
        total_price = total_price + ticket_price * numberToBuy

    # stripe uses prices in cents
    return int(total_price * 100)


@payments.route('/stripe-key', methods=['GET'])
@csrf.exempt
@login_required
def fetch_key():
    # Send publishable key to client
    return jsonify({'publishableKey': stripe_keys["publishable_key"]})


@payments.route('/pay', methods=['POST'])
@csrf.exempt
@login_required
def pay():
    data = request.get_json()
    print("data received at /pay", data)
    try:
        if 'paymentMethodId' in data:
            # order_amount = calculate_order_amount(
            #     data['items'])  # the orderItems
            order_amount = calculate_order_amount(
                session.get("payment_data", None))

            # Create new PaymentIntent with a PaymentMethod ID from the client.
            customer = stripe.Customer.create(
                # email='bre@customer.com',
                email=current_user.email
            )
            intent = stripe.PaymentIntent.create(
                customer=customer.id,
                description=data["items"],
                amount=order_amount,
                currency=data['currency'],
                payment_method=data['paymentMethodId'],
                confirmation_method='manual',
                confirm=True,
                # If a mobile client passes `useStripeSdk`, set `use_stripe_sdk=true`
                # to take advantage of new authentication features in mobile SDKs.
                use_stripe_sdk=True if 'useStripeSdk' in data and data['useStripeSdk'] else None,
            )
            # After create, if the PaymentIntent's status is succeeded, fulfill the order.
        elif 'paymentIntentId' in data:
            # Confirm the PaymentIntent to finalize payment after handling a required action
            # on the client.
            intent = stripe.PaymentIntent.confirm(data['paymentIntentId'])
            # After confirm, if the PaymentIntent's status is succeeded, fulfill the order.

        return generate_response(intent)
    except stripe.error.CardError as e:
        return jsonify({'error': e.user_message})


def generate_response(intent):
    status = intent['status']
    if status == 'requires_action' or status == 'requires_source_action':
        # Card requires authentication
        return jsonify({'requiresAction': True, 'paymentIntentId': intent['id'], 'clientSecret': intent['client_secret']})
    elif status == 'requires_payment_method' or status == 'requires_source':
        # Card was not properly authenticated, suggest a new payment method
        return jsonify({'error': 'Your card was denied, please provide a new payment method'})
    elif status == 'succeeded':
        # Payment is complete, authentication not required
        # To cancel the payment you will need to issue a Refund (https://stripe.com/docs/api/refunds)
        print("💰 Payment received!")
        return jsonify({'clientSecret': intent['client_secret']})


@payments.route('/after-payment', methods=['POST'])
@csrf.exempt
@login_required
def after_payment():
    all_qr_names = []
    all_event_ticket_info = []
    total_for_booking = 0
    total_for_tickets = 0.00
    statusOfPayment = "payed"
    #
    for ticketToBook in session.get("payment_data", None):
        if int(ticketToBook["booked_num"]) == 0:
            continue
        else:
            print(ticketToBook)
            # check if the user is buying more tickets of the same type for the same event
            eventOfTicketID = Ticket.query.get(
                ticketToBook["ticket_id"]).event_id
            eventInQuestion = Event.query.get(
                eventOfTicketID)
            if UserBookings.query.filter_by(user_id=current_user.id,
                                            event_id=eventOfTicketID,
                                            ticket_id=ticketToBook["ticket_id"],
                                            payment_status=statusOfPayment).first():

                ticketInQuestion = Ticket.query.get(ticketToBook["ticket_id"])
                availableToPurchase = ticketInQuestion.num_tickets - \
                    int(ticketInQuestion.num_bought)
                if availableToPurchase >= int(ticketToBook["booked_num"]):
                    print("here")
                    ExistingBooking = UserBookings.query.filter_by(user_id=current_user.id,
                                                                   event_id=eventOfTicketID,
                                                                   ticket_id=ticketToBook["ticket_id"],
                                                                   payment_status=statusOfPayment).first()
                    # print("before adding")
                    ExistingBooking.number_booked += int(
                        ticketToBook["booked_num"])
                    ticketInQuestion.num_bought += int(
                        ticketToBook["booked_num"])
                    ticketActualPriceFromDB = ticketInQuestion.price
                    total_for_tickets += ticketActualPriceFromDB * \
                        ExistingBooking.number_booked
                    if ExistingBooking.image_file == 'default_qr':
                        dataForQR = {"ticket_id": ticketToBook["ticket_id"],
                                     "event_id": eventOfTicketID,
                                     "user_id": current_user.id,
                                     "status": statusOfPayment}
                        qr_image = createQR(dataForQR)
                        ExistingBooking.image_file = qr_image
                    all_qr_names.append(ExistingBooking.image_file)

                    if statusOfPayment == 'not payed':
                        stat = 'Not Paid'
                    else:
                        stat = 'Paid'
                    dataForPDF = {
                        "event-title": str(eventInQuestion.title),
                        "ticket-type": ticketInQuestion.ticket_type,
                        "num": str(ExistingBooking.number_booked),
                        "status": stat,
                        "total": "{:.2f}".format(total_for_tickets),
                        "start time": str(eventInQuestion.time_from.strftime("%H:%M")),
                        "date": str(eventInQuestion.event_date.strftime("%Y-%m-%d")),
                        "location": str(eventInQuestion.location),
                        "info": str(eventInQuestion.address) + ' ' + str(eventInQuestion.city)
                    }
                    # print(dataForPDF, "data foe pdf")
                    all_event_ticket_info.append(
                        dataForPDF)
                    db.session.commit()  # ?

            else:  # the booking combination does not already exist so create a new one
                if Ticket.query.get(ticketToBook["ticket_id"]):
                    ticketTYPE = Ticket.query.get(
                        ticketToBook["ticket_id"]).ticket_type
                    ticketActualPriceFromDB = Ticket.query.get(
                        ticketToBook["ticket_id"]).price

                    dataForQR = {"ticket_id": ticketToBook["ticket_id"],
                                 "event_id": eventOfTicketID,
                                 "user_id": current_user.id,
                                 "status": statusOfPayment}
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
                    ticketInQuestion.num_bought += int(
                        ticketToBook["booked_num"])
                    total_for_tickets += ticketActualPriceFromDB * ExistingBooking.number_booked
                    if statusOfPayment == 'not payed':
                        stat = 'Not Paid'
                    else:
                        stat = 'Paid'
                    db.session.add(bookingToAdd)
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
                    db.session.add(bookingToAdd)
    db.session.commit()
    random_hex = secrets.token_hex(16)
    # pdfname = 'testingpdfbooking'
    pdfname = random_hex
    pdf_receipt = create_pdf_receipt(
        pdfname, all_qr_names, all_event_ticket_info)
    subject = 'Your receipt'
    emailTo = current_user.email
    content = 'Thank you for your purchase. Please find your tickets attached'
    filename = pdf_receipt
    email = generate_email(subject, emailTo, content, filename)
    return redirect(url_for('payments.final'), code=302)


@payments.route('/final')
@csrf.exempt
@login_required
def final():
    # return render_template('payments/after-payment.html')
    return redirect(url_for('bookings.display_booking'), code=302)


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
