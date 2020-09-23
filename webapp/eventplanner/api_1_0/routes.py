from flask import Blueprint, jsonify, request, g, url_for, current_app, make_response, abort
from flask_httpauth import HTTPBasicAuth
from eventplanner.errors.handlers import forbidden
from eventplanner import db, bcrypt, csrf
from flask_login import login_required
from eventplanner.models import event_schema, events_schema, users_schema, user_schema, ticket_schema, tickets_schema, eventstaff_schema, eventstaffs_schema, userbooking_schema
from ..models import User, Event, Ticket, Role, UserRoles, UserBookings, EventStaff
from functools import wraps
from datetime import datetime
from eventplanner.events.utils_events import save_picture_api

import os
from werkzeug.utils import secure_filename
import urllib.request

from flask_cors import CORS
api = Blueprint('api', __name__)
CORS(api)
auth = HTTPBasicAuth()

# In order to remove the CSRF protection that blocked login and new event
# https://flask-wtf.readthedocs.io/en/stable/csrf.html
# this is the decorator to use the token
# try:

# except Exception as e:
#     result = {"result": "error", "type": str(e)}
#     return jsonify(result)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # this header is where the token will be if there is one
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            current_user_api = User.verify_auth_token(token)
            # current_user_api_id = current_user_api.id
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(current_user_api, *args, **kwargs)
    return decorated


######### API USERS #########


@api.route("/login/", methods=['POST'])
@csrf.exempt
def api_login():
    # requesting the authorization info
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})
    # if there is auth information i want to get the user
    # email = username is confusing but correct
    user = User.query.filter_by(email=auth.username).first()
    # if no user found
    if not user:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})
    # if i passed the not user check it means that the user exists in the database,
    # so i need to check the password or the token
    if bcrypt.check_password_hash(user.password, auth.password):
        token = user.generate_auth_token()
        # role = user.roles[0].name
        response_roles = []
        for role in user.roles:
            response_roles.append(role.name)
        user_id = user.id
        return jsonify({'token': token, 'roles': response_roles, 'user_id': user_id})

    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})


@api.route('/register/', methods=['POST'])
def api_register():
    data = request.get_json()
    username = data['username']
    email = data['email']
    password = data['password']
    confirm_password = data['confirm_password']
    if email is None or password is None or confirm_password is None:
        abort(400)  # missing arguments
    if User.query.filter_by(username=username).first() is not None:
        abort(400)  # existing user
    hashed_password = bcrypt.generate_password_hash(
        password).decode('utf-8')
    user = User(username=username,
                email=email, password=hashed_password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': "User has been created"}), 201


@api.route('/users/<int:id>/')
def get_user(id):
    user = User.query.get(id)
    if not user:
        abort(400)
    result = user_schema.dump(user)
    return jsonify(result)


@api.route('/users/', methods=['GET'])
def get_all_users():
    all_users = User.query.all()
    result = users_schema.dump(all_users, many=True)
    return jsonify(result)


# @api.route('/users/<int:id>/events/', methods=['GET'])
# def get_user_events(id):
#     # check if the user exists
#     isManager = False
#     user = User.query.get(id)
#     if not user:
#         abort(400)
#     for role in user.roles:
#         if role.name == 'Manager':
#             isManager = True
#     if isManager:
#         manager_events = user.events
#         result = events_schema.dump(manager_events, many=True)
#         return jsonify(result)


# @api.route('/staffer/<int:staff_id>/events/', methods=['GET'])
# def get_events_of_staffer(staff_id):
#     isStaffer = False
#     user = User.query.get(staff_id)
#     if not user:
#         abort(400)
#     for role in user.roles:
#         if role.name == 'Staff':
#             isStaffer = True
#     if isStaffer:
#         staffer_id = user.id
#         staffer_events = EventStaff.query.filter_by(
#             user_id=staffer_id).all()

#         # staffer_events = EventStaff.query.filter_by(id=event_staff_rows)
#         result = eventstaffs_schema.dump(staffer_events, many=True)
#         return jsonify(result)

@api.route('/users/existing/', methods=['GET', 'POST'])
@csrf.exempt
def check_if_email_exists():
    data = request.get_json()
    email = data['email']

    # check the db for this email
    if User.query.filter_by(email=email).first() is not None:  #  user exists
        response = {'response': 'email already in use, try another one!'}
        return jsonify(response)
    else:
        response = {'response': 'email not in use!'}
        return jsonify(response)


@api.route('/users/<int:id>/events/', methods=['GET'])
def get_for_all_user_events(id):
    isManager = False
    isStaffer = False
    isSimpleUser = False
    # get the user in question
    user = User.query.get(id)
    if user:

        for role in user.roles:
            if role.name == 'Manager':
                isManager = True
            elif role.name == 'Staff':
                isStaffer = True
            else:
                isSimpleUser = True
        if isManager:
            manager_events = user.events
            # print(manager_events)
            result = events_schema.dump(manager_events, many=True)
            return jsonify(result)
        elif isStaffer:
            staffer_id = user.id
            staffer_events = EventStaff.query.filter_by(
                user_id=staffer_id).all()

            staff_works_at_event_id = []
            for event in staffer_events:
                staff_works_at_event_id.append(event.event_id)
            print(staff_works_at_event_id)

            staffer_events_all = []
            for event_id in staff_works_at_event_id:
                staffer_events_all.append(
                    Event.query.get(event_id))
            # result = eventstaffs_schema.dump(staffer_events, many=True)
            print(staffer_events_all)
            result = events_schema.dump(staffer_events_all, many=True)
            return jsonify(result)
            # ev = Event.query.get(1)
            # result = event_schema.dump(ev)
            # return jsonify(result)
        else:
            result = {'result': 'User is neither manager nor staff'}
            return jsonify(result)
    else:
        result = {'result': 'User does not exist'}
        return jsonify(result)


##################################################################
##################################################################
##################################################################
##################################################################
########################### API EVENTS ###########################
##################################################################
##################################################################
##################################################################
##################################################################

@api.route('/event/new/', methods=['POST'])
@token_required
@csrf.exempt
def api_new_event(current_user_api):
    data = request.get_json()

    isManager = False
    for role in current_user_api.roles:
        if "Manager" in role.name:
            isManager = True

    if isManager:
        manager = current_user_api
        try:
            title = data['title']
            event_type = data['event_type']
            event_date = data['event_date']
            date_object = datetime.strptime(event_date, '%Y-%m-%d')
            time_from = data['time_from']
            time_from_obj = datetime.strptime(time_from, '%H:%M').time()
            time_to = data['time_to']
            time_to_obj = datetime.strptime(time_to, '%H:%M').time()
            content = data['content']
            content_eng = data['content_eng']
            address = data['address']
            city = data['city']
            location = data['location']
            tickets = data['tickets']

            event = Event(title=title, event_type=event_type,
                          event_date=date_object, time_from=time_from_obj, time_to=time_to_obj,
                          content=content,content_eng=content_eng, address=address, city=city, location=location,
                          manager=manager)

            for ticket in tickets:
                new_ticket = Ticket(event_id=event.id, ticket_type=ticket['ticket_type'],
                                    num_tickets=ticket['num_tickets'], price=ticket['price'])
                # Add to event
                event.tickets.append(new_ticket)

            db.session.add(event)
            db.session.commit()

            result = event_schema.dump(event)
            return jsonify(result)
        except Exception as e:
            result = {"result": "error", "type": str(e)}
            return jsonify(result)
    else:
        result = {"result": "error", "type": "As a simple user you cannot create an event"}
        return jsonify(result)


@api.route('/events/', methods=['GET'])
def api_get_events():
    """to get all events"""
    all_events = Event.query.all()
    result = events_schema.dump(all_events, many=True)
    return jsonify(result)


@api.route('/events/<event_type>/', methods=['GET'])
def api_get_events_by_type(event_type):
    events_by_type = Event.query.filter_by(event_type=event_type).all()
    result = events_schema.dump(events_by_type, many=True)
    return jsonify(result)


@api.route('/event/<int:event_id>/', methods=['GET'])
def api_get_event(event_id):
    # event = Event.query.filter_by(id=event_id).first()
    event = Event.query.get_or_404(event_id)
    result = event_schema.dump(event)
    return jsonify(result)


@api.route('/event/<int:id>/tickets/', methods=['GET'])
def api_get_event_tickets(id):
    event = Event.query.get_or_404(id)
    tickets = event.tickets
    result = ticket_schema.dump(tickets, many=True)
    return jsonify(result)


@api.route("/event/<int:event_id>/delete/tickets/", methods=['POST'])
@token_required
@csrf.exempt
def api_delete_event_tickets(current_user_api, event_id):
    # get the tickets already present and expose them to be updated/edited
    tickets_not_found = []
    some_not_found = False
    event = Event.query.get_or_404(event_id)
    if current_user_api != event.manager:
        return forbidden('Insufficient permissions')
    data = request.get_json()
    # {"to_delete":[{"ticket_id":2},{"ticket_id":3}]}
    tickets_to_delete = data["to_delete"]

    for ticket in tickets_to_delete:
        tik_to_del = Ticket.query.get(ticket["ticket_id"])
        if tik_to_del:

            # tik_to_del = Ticket.query.get_or_404(ticket["ticket_id"])
            db.session.delete(tik_to_del)
            db.session.commit()
        else:
            tickets_not_found.append(ticket)
            some_not_found = True

    if some_not_found:
        result = {"result": "Tickets not found",
                  "not found": tickets_not_found}
        return jsonify(result)
    else:
        result = {"result": "Tickets have been deleted"}
        return jsonify(result)


@api.route('/update/event/<int:id>/', methods=['PUT'])
@token_required
@csrf.exempt
def api_update_event(current_user_api, id):
    event = Event.query.get_or_404(id)
    if current_user_api != event.manager:
        return forbidden('Insufficient permissions')

    data = request.get_json()
    manager = current_user_api

    title = data['title']
    event_type = data['event_type']
    event_date = data['event_date']
    date_object = datetime.strptime(event_date, '%Y-%m-%d')
    time_from = data['time_from']
    time_from_obj = datetime.strptime(time_from, '%H:%M').time()
    time_to = data['time_to']
    time_to_obj = datetime.strptime(time_to, '%H:%M').time()
    content = data['content']
    content_eng = data['content_eng']
    address = data['address']
    city = data['city']
    location = data['location']

    event.title = title
    event.event_type = event_type
    event.event_date = date_object
    event.time_from = time_from_obj
    event.time_to = time_to_obj
    event.content = content
    event.content_eng = content_eng
    event.address = address
    event.city = city
    event.location = location

    db.session.commit()
    result = event_schema.dump(event)
    return jsonify(result)


@api.route('/update/event/<int:event_id>/tickets/', methods=['PUT'])
@token_required
@csrf.exempt
def api_update_event_tickets(current_user_api, event_id):
    event = Event.query.get_or_404(event_id)
    if current_user_api != event.manager:
        return forbidden('Insufficient permissions')

    data = request.get_json()
    manager = current_user_api
    tickets_modified = []
    # {'tickets':[{'ticket_id':9,'ticket_type':'music','num_tickets':32,'price':99},{'id':10,'ticket_type':'movies','num_tickets':120,'price':12}]}
    tickets = data['tickets']
    for ticket in tickets:
        ticket_to_change_id = ticket['ticket_id']
        ticket_to_change = Ticket.query.get_or_404(ticket_to_change_id)
        ticket_to_change.ticket_type = ticket['ticket_type']
        ticket_to_change.num_tickets = ticket['num_tickets']
        ticket_to_change.price = ticket['price']
        db.session.commit()
        tickets_modified.append(ticket_to_change)

    result = ticket_schema.dump(tickets_modified, many=True)
    return jsonify(result)


@api.route('/update/event/<int:event_id>/new-tickets/', methods=['POST'])
@token_required
@csrf.exempt
def api_event_new_tickets(current_user_api, event_id):
    event = Event.query.get_or_404(event_id)
    if current_user_api != event.manager:
        return forbidden('Insufficient permissions')

    data = request.get_json()
    manager = current_user_api
    tickets_added = []
    # {'tickets':[{'ticket_type':'music','num_tickets':32,'price':99},{'ticket_type':'movies','num_tickets':120,'price':12}]}
    tickets = data['tickets']
    for ticket in tickets:
        new_ticket = Ticket(event_id=event_id, ticket_type=ticket['ticket_type'],
                            num_tickets=ticket['num_tickets'], price=ticket['price'])
        event.tickets.append(new_ticket)
        db.session.commit()
        tickets_added.append(new_ticket)

    result = ticket_schema.dump(tickets_added, many=True)
    return jsonify(result)
# needs to be logged in


@api.route('/ticket/<int:ticket_id>/', methods=['GET'])
def get_ticket_info(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    result = ticket_schema.dump(ticket)
    return jsonify(result)


@api.route('/delete/event/<int:id>/', methods=['DELETE'])
@token_required
@csrf.exempt
def api_delete_event(current_user_api, id):
    event = Event.query.get(id)
    db.session.delete(event)
    db.session.commit()
    return {'response': 'Event has been deleted'}


@api.route("/event/<int:event_id>/add-staff/", methods=['GET', 'POST'])
@token_required
@csrf.exempt
def api_add_staff(current_user_api, event_id):
    found = False
    already_staffer = False
    emails_not_found = []
    users_not_found = False
    staff_added = False
    event_to_staff = Event.query.get_or_404(event_id)
    if current_user_api != event_to_staff.manager:
        return forbidden('Insufficient permissions')
    data = request.get_json()

    # staff in the format
    # {‘staffers’:[{‘email’:’pippo@gmail.com’}]}
    for staffer in data['staffers']:
        # check if user exists
        if User.query.filter_by(email=staffer['email']).first():
            # user exists
            user_to_add_as_staff = User.query.filter_by(
                email=staffer['email']).first()
            # see if already has been added as a staff user type
            for role in user_to_add_as_staff.roles:
                if 'Staff' in role.name:
                    found = True
                if found == False:
                    user_to_add_as_staff.roles.append(Role(name='Staff'))

            # need to check if staffer is already in staff list
            for staffer in event_to_staff.staffers:
                if staffer.id == user_to_add_as_staff.id:
                    already_staffer = True
                    # the user is already a staffer for this event

            if already_staffer == False:
                event_to_staff.staffers.append(user_to_add_as_staff)
                staff_added = True
                db.session.commit()

        else:
            # user not found
            emails_not_found.append(staffer['email'])
            users_not_found = True
    if users_not_found:
        result = {"result": "these users where not found",
                  'emails': emails_not_found}
        return jsonify(result)
    elif staff_added:
        result = {"result": "Your staff has been added"}
        return jsonify(result)
    elif already_staffer:
        result = {"result": "staffer is alreafy present"}
        return jsonify(result)


@api.route('/event/<int:event_id>/staffers/', methods=['GET'])
def get_staff_of_event(event_id):
    event = Event.query.get(event_id)
    if event:
        staffers = event.staffers
        if staffers:
            result = users_schema.dump(staffers, many=True)
            return jsonify(result)
        else:
            result = {'result': 'event not staffed'}
            return jsonify(result)
    else:
        result = {'result': 'event not found'}
        return jsonify(result)


@api.route('/event/<int:event_id>/remove-staffer/', methods=['POST'])
@token_required
@csrf.exempt
def remove_Staff_from_event(current_user_api, event_id):
    FoundToRemove = False
    event = Event.query.get(event_id)
    if current_user_api != event.manager:
        return forbidden('Insufficient permissions')

    data = request.get_json()
    staff_id = data['staff_id']
    if event:
        staffers = event.staffers
        staffer_to_remove = staff_id
        i = 0
        for staffer in staffers:
            if staffer.id == staff_id:
                FoundToRemove = True
                indextoremove = i
            else:
                i = i + 1
        if FoundToRemove:
            staffer_removed = staffers.pop(indextoremove)
            event.staffers = staffers
            db.session.commit()
            result = {'result': 'user removed successfully'}
            return jsonify(result)
        else:
            result = {'result': 'staffer not found'}
            return jsonify(result)
    else:
        result = {'result': 'event not found'}
        return jsonify(result)


ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@api.route('/event/<int:event_id>/file-upload/', methods=['POST'])
@csrf.exempt
def upload_file(event_id):
    event = Event.query.get_or_404(event_id)
    # check if the post request has the file part
    if 'file' not in request.files:
        resp = jsonify({'message': 'No file part in the request'})
        resp.status_code = 400
        return resp
    file = request.files['file']
    if file.filename == '':
        resp = jsonify({'message': 'No file selected for uploading'})
        resp.status_code = 400
        return resp
    if file and allowed_file(file.filename):
        # # filename = secure_filename(file.filename)
        # f_name, f_ext = os.path.splitext(file.filename)
        # filename = str(event_id) + f_ext
        # file.save(os.path.join(current_app.root_path,
        #                        'static/event_pics', filename))
        picture_file = save_picture_api(file, event.id)
        event.image_file = picture_file
        db.session.commit()
        resp = jsonify({'message': 'File successfully uploaded'})
        resp.status_code = 201
        return resp
    else:
        resp = jsonify(
            {'message': 'Allowed file types are txt, pdf, png, jpg, jpeg, gif'})
        resp.status_code = 400
        return resp


##################################################################
##################################################################
##################################################################
##################################################################
########################### API BOOKINGS #########################
##################################################################
##################################################################
##################################################################
##################################################################

@api.route('/create-booking/', methods=['POST'])
@token_required
@csrf.exempt
def create_booking_api(current_user_api):
    try:
        data = request.get_json()
        # json for a booking
        # examplebookingJSON = {"event_id":1,
        #                     "user_id":2,
        #                     "total_price":22,
        #                     "status":"not payed",
        #                     "selected_tickets":[{"ticket_id":2,"quantity":3},{"ticket_id":3,"quantity":2}]}
        eventID = data["event_id"]
        userID = data["user_id"]
        #totalPrice = data["total_price"]
        statusOfPayment = data["status"]
        selectedTickets = data["selected_tickets"]

        # check if the user is a simple user or at least not a manager
        isManager = False
        userToCheck = User.query.get(userID)
        for role in userToCheck.roles:
            if "Manager" in role.name:
                isManager = True


        if isManager == False:
            for ticketToBook in selectedTickets:
                # check if the user is buying more tickets of the same type for the same event
                if UserBookings.query.filter_by(user_id = userID,\
                                                event_id = eventID,\
                                                ticket_id = ticketToBook["ticket_id"],\
                                                payment_status = statusOfPayment).first():
                    if Ticket.query.get(ticketToBook["ticket_id"]):
                        ticketInQuestion = Ticket.query.get(
                            ticketToBook["ticket_id"])
                        availableToPurchase = ticketInQuestion.num_tickets - int(ticketInQuestion.num_bought)
                        if availableToPurchase >= int(ticketToBook["quantity"]):
                            ExistingBooking = UserBookings.query.filter_by(user_id = userID, event_id = eventID ,ticket_id = ticketToBook["ticket_id"], payment_status = statusOfPayment).first()
                            ExistingBooking.number_booked += ticketToBook["quantity"]
                            ticketInQuestion.num_bought += int(ticketToBook["quantity"])
                            db.session.commit()
                        else:
                            result = {"result":"not enough ticket available"}
                            return jsonify(result)
                else: # the booking combination does not already exist so create a new one
                    if Ticket.query.get(ticketToBook["ticket_id"]):
                        ticketInQuestion = Ticket.query.get(
                            ticketToBook["ticket_id"])
                        availableToPurchase = ticketInQuestion.num_tickets - int(ticketInQuestion.num_bought)
                        if availableToPurchase >= int(ticketToBook["quantity"]):
                            ticketTYPE = Ticket.query.get(
                                ticketToBook["ticket_id"]).ticket_type
                            ticketActualPriceFromDB = Ticket.query.get(
                                ticketToBook["ticket_id"]).price

                            dataForQR = {"ticket_id": ticketToBook["ticket_id"],
                                         "event_id": eventID,
                                         "user_id": userID,
                                         "status": statusOfPayment}
                            qr_image = createQR(dataForQR)

                            bookingToAdd = UserBookings(user_id=userID,
                                                        event_id=eventID,
                                                        ticket_id=ticketToBook["ticket_id"],
                                                        ticket_type=ticketTYPE,
                                                        number_booked=ticketToBook["quantity"],
                                                        number_scanned=0,
                                                        payment_status=statusOfPayment,
                                                        image_file=qr_image)

                            db.session.add(bookingToAdd)
                        else:
                            result = {"result":"not enough ticket available"}
                            return jsonify(result)
            db.session.commit()
            result = {"result": "booking completed"}
            return jsonify(result)
        else:
            result = {"result": "error", "type": "As a Manager you cannot book an event"}
            return jsonify(result)
    except Exception as e:
        result = {"result": "error", "type": str(e)}
        return jsonify(result)


@api.route('/user-bookings/', methods=['POST'])
@csrf.exempt
def get_user_bookings_api():
    try:
        data = request.get_json()
    # json has {"user_id":2}
    except Exception as e:
        result = {"result": "error", "type": str(e)}
        return jsonify(result)
    try:
        if User.query.get(data["user_id"]):
            user = User.query.get(data["user_id"])
            events_and_status = []
            for singleBooking in user.bookings:
                tp = (singleBooking.event_id,singleBooking.payment_status)
                if tp not in events_and_status:
                    events_and_status.append(tp)
            # list with the (event-id)
            all_bookings = []
            i = 0
            for tupla_evID_status in events_and_status:  # check all event ids
                eventID = tupla_evID_status[0]
                status = tupla_evID_status[1]
                dict_for_ev = {}
                dict_for_ev["event_id"] = eventID
                dict_for_ev["status"] = status
                all_bookings.append(dict_for_ev)
                selectedTickets = []
                totalPriceOfBooking = 0
                for singleBooking in user.bookings:  # check through all bookings
                    if singleBooking.event_id == eventID and singleBooking.payment_status == status:
                        selectedTickets.append({
                            "quantity": singleBooking.number_booked,
                            "ticket_id": singleBooking.ticket_id
                        })
                        try:
                            tick = Ticket.query.get(singleBooking.ticket_id)
                        except Exception as e:
                            result = {"result": "error", "type": str(e)}
                            return jsonify(result)
                        totalPriceOfBooking = totalPriceOfBooking + \
                            tick.price * singleBooking.number_booked

                all_bookings[i]["selected_tickets"] = selectedTickets
                all_bookings[i]["total_price"] = totalPriceOfBooking
                all_bookings[i]["user_id"] = user.id
                i = i + 1

            return jsonify(all_bookings)

        else:
            result = {"result": "user not found"}
            return jsonify(result)
    except Exception as e:
        result = {"result": "error", "type": str(e)}
        return jsonify(result)


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








# @api.route('/user-bookings/', methods=['POST'])
# @csrf.exempt
# def get_user_bookings_api():
#     try:
#         data = request.get_json()
#     # json has {"user_id":2}
#     except Exception as e:
#         result = {"result": "error", "type": str(e)}
#         return jsonify(result)
#     try:
#         if User.query.get(data["user_id"]):
#             user = User.query.get(data["user_id"])
#             events_booked = []
#             for singleBooking in user.bookings:
#                 if singleBooking.event_id not in events_booked:
#                     events_booked.append((singleBooking.event_id,singleBooking.payment_status)) # list of tuples (eventid,status)
#             # list with the (event-id)

#             all_bookings = []
#             i = 0
#             for tupla_evID_status in events_booked:  # check all event ids
#                 eventID = tupla_evID_status[0]
#                 status = tupla_evID_status[1]
#                 dict_for_ev = {}
#                 dict_for_ev["event_id"] = eventID
#                 dict_for_ev["status"] = status
#                 all_bookings.append(dict_for_ev)
#                 selectedTickets = []
#                 totalPriceOfBooking = 0
#                 for singleBooking in user.bookings:  # check through all bookings
#                     if singleBooking.event_id == eventID and singleBooking.payment_status == status:
#                         selectedTickets.append({
#                             "quantity": singleBooking.number_booked,
#                             "ticket_id": singleBooking.ticket_id
#                         })
#                         try:
#                             tick = Ticket.query.get(singleBooking.ticket_id)
#                         except Exception as e:
#                             result = {"result": "error", "type": str(e)}
#                             return jsonify(result)
#                         totalPriceOfBooking = totalPriceOfBooking + \
#                             tick.price * singleBooking.number_booked

#                 all_bookings[i]["selected_tickets"] = selectedTickets
#                 all_bookings[i]["total_price"] = totalPriceOfBooking
#                 all_bookings[i]["user_id"] = user.id
#                 i = i + 1

#             return jsonify(all_bookings)

#         else:
#             result = {"result": "user not found"}
#             return jsonify(result)
#     except Exception as e:
#         result = {"result": "error", "type": str(e)}
#         return jsonify(result)

# @api.route('/create-booking/', methods=['POST'])
# @token_required
# @csrf.exempt
# def create_booking_api(current_user_api):
#     try:
#         data = request.get_json()
#         # json for a booking
#         # examplebookingJSON = {"event_id":1,
#         #                     "user_id":2,
#         #                     "total_price":22,
#         #                     "status":"not payed",
#         #                     "selected_tickets":[{"ticket_id":2,"quantity":3},{"ticket_id":3,"quantity":2}]}
#         eventID = data["event_id"]
#         userID = data["user_id"]
#         #totalPrice = data["total_price"]
#         statusOfPayment = data["status"]
#         selectedTickets = data["selected_tickets"]

#         # check if the user is a simple user or at least not a manager
#         isManager = False
#         userToCheck = User.query.get(userID)
#         for role in userToCheck.roles:
#             if "Manager" in role.name:
#                 isManager = True


#         if isManager == False:
#             for ticketToBook in selectedTickets:
#                 # check if the user is buying more tickets of the same type for the same event
#                 if UserBookings.query.filter_by(user_id = userID , event_id = eventID , ticket_id = ticketToBook["ticket_id"]).first():
#                     ExistingBooking = UserBookings.query.filter_by(user_id = userID , event_id = eventID , ticket_id = ticketToBook["ticket_id"]).first()
#                     ExistingBooking.number_booked += ticketToBook["quantity"]
#                     db.session.commit()
#                 else: # the booking combination does not already exist so create a new one
#                     if Ticket.query.get(ticketToBook["ticket_id"]):
#                         ticketTYPE = Ticket.query.get(
#                             ticketToBook["ticket_id"]).ticket_type
#                         ticketActualPriceFromDB = Ticket.query.get(
#                             ticketToBook["ticket_id"]).price

#                         bookingToAdd = UserBookings(user_id=userID,
#                                                     event_id=eventID,
#                                                     ticket_id=ticketToBook["ticket_id"],
#                                                     ticket_type=ticketTYPE,
#                                                     number_booked=ticketToBook["quantity"],
#                                                     number_scanned=0,
#                                                     payment_status=statusOfPayment)

#                         db.session.add(bookingToAdd)
#             db.session.commit()
#             result = {"result": "booking completed"}
#             return jsonify(result)
#         else:
#             result = {"result": "error", "type": "As a Manager you cannot book an event"}
#             return jsonify(result)
#     except Exception as e:
#         result = {"result": "error", "type": str(e)}
#         return jsonify(result)


# @api.route('/user-bookings/', methods=['POST'])
# @csrf.exempt
# def get_user_bookings_api():
#     try:
#         data = request.get_json()
#     # json has {"user_id":2}
#     except Exception as e:
#         result = {"result": "error", "type": str(e)}
#         return jsonify(result)
#     try:
#         if User.query.get(data["user_id"]):
#             user = User.query.get(data["user_id"])
#             events_booked = []
#             for singleBooking in user.bookings:
#                 if singleBooking.event_id not in events_booked:
#                     events_booked.append(singleBooking.event_id)
#             # list with the event ids

#             all_bookings = []
#             i = 0
#             for eventID in events_booked:  # check all event ids
#                 dict_for_ev = {}
#                 dict_for_ev["event_id"] = eventID
#                 all_bookings.append(dict_for_ev)
#                 selectedTickets = []
#                 totalPriceOfBooking = 0
#                 for singleBooking in user.bookings:  # check through all bookings
#                     if singleBooking.event_id == eventID:
#                         all_bookings[i]["status"] = singleBooking.payment_status
#                         selectedTickets.append({
#                             "quantity": singleBooking.number_booked,
#                             "ticket_id": singleBooking.ticket_id
#                         })
#                         try:
#                             tick = Ticket.query.get(singleBooking.ticket_id)
#                         except Exception as e:
#                             result = {"result": "error", "type": str(e)}
#                             return jsonify(result)
#                         totalPriceOfBooking = totalPriceOfBooking + \
#                             tick.price * singleBooking.number_booked

#                 all_bookings[i]["selected_tickets"] = selectedTickets
#                 all_bookings[i]["total_price"] = totalPriceOfBooking
#                 all_bookings[i]["user_id"] = user.id
#                 i = i + 1

#             return jsonify(all_bookings)

#         else:
#             result = {"result": "user not found"}
#             return jsonify(result)
#     except Exception as e:
#         result = {"result": "error", "type": str(e)}
#         return jsonify(result)
