from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint, jsonify)
from flask_login import current_user, login_required
from eventplanner import db, csrf
from eventplanner.models import User, Role, UserRoles, Event, EventStaff, Ticket, event_schema, events_schema
from eventplanner.events.forms import EventForm, TicketForm, StaffForm, UpdateEventTicketsForm, AddTicketsForm
from eventplanner.events.utils_events import save_picture

# for payments


events = Blueprint('events', __name__)


@events.route("/event/new/", methods=['GET', 'POST'])
@login_required
def new_event():
    form = EventForm()

    if form.validate_on_submit():
        event = Event(title=form.title.data, event_type=form.event_type.data,
                      event_date=form.event_date.data, time_from=form.time_from.data, time_to=form.time_to.data,
                      content=form.content.data, address=form.address.data, city=form.city.data, location=form.location.data,
                      manager=current_user)
        for ticket in form.tickets.data:
            new_ticket = Ticket(event_id=event.id, ticket_type=ticket['ticket_type'],
                                num_tickets=ticket['num_tickets'], price=ticket['price'])
            # Add to event
            event.tickets.append(new_ticket)
        if form.picture.data:
            picture_file = save_picture(form.picture.data, event.id)
            event.image_file = picture_file

        db.session.add(event)
        db.session.commit()
        flash('Your event has been created', 'success')
        return redirect(url_for('main.home'))
    return render_template('create_event.html', title='New Event', form=form, legend='New Event')

# to find an event by id


@events.route("/event/<int:event_id>/")
def event(event_id):
    event = Event.query.get_or_404(event_id)
    return render_template('event.html', title=event.title, event=event)


# to update an event
@events.route("/event/<int:event_id>/update/", methods=['GET', 'POST'])
@login_required
def update_event(event_id):
    event = Event.query.get_or_404(event_id)
    if event.manager != current_user:
        abort(403)  # forbidden route
    form = EventForm()
    if form.validate_on_submit():
        event.title = form.title.data
        event.event_type = form.event_type.data
        event.event_date = form.event_date.data
        event.time_from = form.time_from.data
        event.time_to = form.time_to.data
        event.content = form.content.data
        event.address = form.address.data
        event.city = form.city.data
        event.location = form.location.data

        if form.picture.data:
            picture_file = save_picture(form.picture.data, event.id)
            event.image_file = picture_file

        db.session.commit()
        flash('Your event has been updated', 'success')
        return redirect(url_for('events.event', event_id=event.id))
    elif request.method == 'GET':
        form.title.data = event.title
        form.event_type.data = event.event_type
        form.event_date.data = event.event_date
        form.time_from.data = event.time_from
        form.time_to.data = event.time_to
        form.content.data = event.content
        form.address.data = event.address
        form.city.data = event.city
        form.location.data = event.location

    return render_template('update_event.html', title='Updated event', form=form, legend='Update event', event=event)


@events.route("/event/<int:event_id>/update/tickets/", methods=['GET', 'POST'])
@login_required
def update_event_tickets(event_id):
    # get the tickets already present and expose them to be updated/edited
    event = Event.query.get_or_404(event_id)
    if event.manager != current_user:
        abort(403)  # forbidden route
    form = UpdateEventTicketsForm()
    if request.method == 'GET':
        for ticket in event.tickets:
            ticketForm = TicketForm()
            ticketForm.ticket_type = ticket.ticket_type
            ticketForm.num_tickets = ticket.num_tickets
            ticketForm.price = ticket.price
            form.tickets.append_entry(ticketForm)

    if form.validate_on_submit():
        for ticket in event.tickets:
            db.session.delete(ticket)
        db.session.commit()
        for ticket in form.tickets.data:
            new_ticket = Ticket(event_id=event.id, ticket_type=ticket['ticket_type'],
                                num_tickets=ticket['num_tickets'], price=ticket['price'])
            event.tickets.append(new_ticket)
        db.session.commit()

        flash('Your event tickets have been updated', 'success')
        return redirect(url_for('events.event', event_id=event.id))

    return render_template('update_event_tickets.html', title='Updated event tickets', form=form, legend='Update event tickets', event=event)


@events.route("/event/<int:event_id>/delete/tickets/", methods=['GET', 'POST'])
@login_required
def delete_event_tickets(event_id):
    # get the tickets already present and expose them to be updated/edited
    event = Event.query.get_or_404(event_id)
    if event.manager != current_user:
        abort(403)  # forbidden route
    form = UpdateEventTicketsForm()
    if request.method == 'GET':
        for ticket in event.tickets:
            ticketForm = TicketForm()
            ticketForm.ticket_type = ticket.ticket_type
            ticketForm.num_tickets = ticket.num_tickets
            ticketForm.price = ticket.price
            form.tickets.append_entry(ticketForm)

    if form.validate_on_submit():

        form_ticket_keys = request.form.getlist("ticket_keys")
        for ticket_id in form_ticket_keys:
            ticket_to_delete = Ticket.query.get_or_404(int(ticket_id))
            db.session.delete(ticket_to_delete)
            db.session.commit()

        flash('Your event tickets have been deleted', 'success')
        return redirect(url_for('events.event', event_id=event.id))

    return render_template('delete_event_tickets.html', title='Delete event tickets', legend='Delete event tickets', event=event, form=form)


@events.route("/event/<int:event_id>/add-tickets/", methods=['GET', 'POST'])
@login_required
def add_tickets(event_id):
    # get the tickets already present and expose them to be updated/edited
    event = Event.query.get_or_404(event_id)
    if event.manager != current_user:
        abort(403)  # forbidden route
    form = AddTicketsForm()
    if form.validate_on_submit():
        for ticket in form.tickets.data:
            new_ticket = Ticket(event_id=event.id, ticket_type=ticket['ticket_type'],
                                num_tickets=ticket['num_tickets'], price=ticket['price'])
            # Add to event
            event.tickets.append(new_ticket)
        db.session.commit()
        flash('Your tickets have been created', 'success')
        return redirect(url_for('events.event', event_id=event.id))
    return render_template('add_tickets.html', title='Add Tickets', form=form, legend='Add Tickets', event=event)


# to delete an event


@events.route("/event/<int:event_id>/delete", methods=['POST'])
@login_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    if event.manager != current_user:
        abort(403)  # forbidden route
    db.session.delete(event)
    db.session.commit()
    flash('Your event has been deleted', 'success')
    return redirect(url_for('main.home'))


@events.route("/<int:user_id>/events/", methods=['GET'])
@login_required
def my_events(user_id):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(id=user_id).first_or_404()

    events_by_user = Event.query.filter_by(user_id=user_id)\
        .order_by(Event.date_posted.desc())\
        .paginate(page=page, per_page=5)

    return render_template('my_events.html', user=user, events=events_by_user, title='My Events', legend='My Events')


@events.route("/event/<int:event_id>/add_staff/", methods=['GET', 'POST'])
@login_required
def add_staff(event_id):
    found = False
    already_staffer = False
    # get the event to which i need to add staff
    # to add as user as staff, i add to his role the one of staff
    # to add a user as staff i add them by email
    # i add to the event database table a new column called staff
    # this column will contain the ids of the users which are staff
    form = StaffForm()
    if form.validate_on_submit():

        if User.query.filter_by(email=form.staffer_email.data).first():
            user_to_add_as_staff = User.query.filter_by(
                email=form.staffer_email.data).first()
            for role in user_to_add_as_staff.roles:
                if 'Staff' in role.name:
                    found = True
                if found == False:
                    user_to_add_as_staff.roles.append(Role(name='Staff'))
                # need to check if staffer is already in staff list
                event_to_staff = Event.query.get_or_404(event_id)

                for staffer in event_to_staff.staffers:
                    if staffer.id == user_to_add_as_staff.id:
                        already_staffer = True

                if already_staffer == False:
                    event_to_staff.staffers.append(user_to_add_as_staff)
                else:
                    flash('User already in staff', 'error')
                    return redirect(url_for('events.event', event_id=event_id))
                db.session.commit()
                flash('Your staff has been added', 'success')
                return redirect(url_for('events.event', event_id=event_id))
        else:
            flash('User not found', 'error')

    return render_template('add_staff.html', form=form, title='Add Staff')


# @users.route("/user/<string:username>")
# def user_events(username):
#     page = request.args.get('page', 1, type=int)
#     user = User.query.filter_by(username=username).first_or_404()
#     # passing an argument to a template
#     # we want to paginate them
#     events = Event.query.filter_by(manager=user)\
#         .order_by(Event.date_posted.desc())\
#         .paginate(page=page, per_page=5)
#     return render_template('user_events.html', events=events, user=user)


# ######### API #########

# @events.route('/api/event/new', methods=['POST'])
# @auth.login_required
# def api_new_event():
#     title = request.json['title']
#     event_type = request.json['event_type']
#     event_date = request.json['date_and_time']
#     num_tickets = request.json['num_of_tickets']
#     content = request.json['content']
#     address = request.json['address']
#     city = request.json['city']
#     new_event = Event(title=title, event_type=event_type,
#                       event_date=event_date, num_tickets=num_tickets,
#                       content=content, address=address, city=city,
#                       manager=current_user)

#     db.session.add(new_event)
#     db.session.commit()
#     return event_schema.jsonify(new_event)

# # get all events


# @events.route('/api/events', methods=['GET'])
# def api_get_events():
#     all_events = Event.query.all()
#     result = events_schema.dump(all_events, many=True)
#     return jsonify(result)

# # @events.route('api/events/<event_type>', methods = ['GET'])
# # def api_get_event_by_type():
# #     events_by_type = Event.query.filter_by('event_type').all()

# # get single event


# @events.route('/api/event/<id>', methods=['GET'])
# def api_get_event(id):
#     event = Event.query.get(id)
#     return events_schema.jsonify(event)


# @events.route('/api/update/event/<id>', methods=['PUT'])
# @login_required
# def api_update_event(id):
#     event = Event.query.get(id)

#     title = request.json['title']
#     event_type = request.json['event_type']
#     event_date = request.json['date_and_time']
#     num_tickets = request.json['num_of_tickets']
#     content = request.json['content']
#     address = request.json['address']
#     city = request.json['city']

#     event.title = title
#     event.event_type = event_type
#     event.event_date = event_date
#     event.num_tickets = num_tickets
#     event.content = content
#     event.address = address
#     event.city = city

#     db.session.commit()

#     return events_schema.jsonify(event)


# @events.route('/api/delete/event/<id>', methods=['DELETE'])
# @login_required
# def api_delete_event(id):
#     event = Event.query.get(id)
#     db.session.delete(event)
#     db.session.commit()
#     return event_schema.jsonify(event)
