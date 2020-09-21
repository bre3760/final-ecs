from eventplanner import db, login_manager
from flask import current_app
from datetime import datetime
from flask_login import UserMixin, AnonymousUserMixin
from flask_user import roles_required
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired
# for the schemas
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow_sqlalchemy.fields import Nested

# https://docs.sqlalchemy.org/en/13/orm/basic_relationships.html
# is hould have done this (see below link)
# https://docs.sqlalchemy.org/en/13/orm/inheritance.html#mapping-class-inheritance-hierarchies
# https://marshmallow-sqlalchemy.readthedocs.io/en/latest/#
# https://stackoverflow.com/questions/40123990/understanding-marshmallow-nested-schema-with-list-data
# https://opensource.com/article/19/5/python-3-default-mac


# for staff
# https://stackoverflow.com/questions/44434410/sqlalchemy-multiple-foreign-key-pointing-to-same-table-same-attribute

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    # username and email are the only ones decided by the user upon registration
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    # image file is automatically done by default
    image_file = db.Column(db.String(20), nullable=False,
                           default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    first_name = db.Column(
        db.String(100), nullable=False, server_default='')
    last_name = db.Column(
        db.String(100), nullable=False, server_default='')
    # backref is like adding another column to an event
    # what it does is when we have an event we can use the manager attribute to see who made the event
    events = db.relationship('Event', backref='manager',
                             lazy=True)
    bookings = db.relationship('UserBookings', backref='customer',
                               lazy=True)

    roles = db.relationship('Role', secondary='user_roles',
                            backref=db.backref('users', lazy='dynamic'))

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    def generate_auth_token(self, expires_sec=600):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
            # data = s.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token
        # user = User.query.get(data['user_id'])
        user = User.query.get(user_id)
        return user

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def __repr__(self):  # how our object is printed
        return f"User('{self.username}','{self.email}','{self.image_file}')"


class Role(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=False)


class UserRoles(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey(
        'user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey(
        'role.id', ondelete='CASCADE'))


class UserBookings(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey(
        'user.id', ondelete='CASCADE'))

    event_id = db.Column(db.Integer(), nullable=False)
    ticket_id = db.Column(db.Integer(), nullable=False)
    ticket_type = db.Column(db.String(100), nullable=False)
    number_booked = db.Column(db.Integer(), nullable=False)
    number_scanned = db.Column(db.Integer(), nullable=False)
    payment_status = db.Column(db.String(100), nullable=False)

    image_file = db.Column(db.String(50), nullable=False,
                           default='default_qr.jpeg')
    # event_id = db.Column(db.Integer(), db.ForeignKey(
    #     'event.id', ondelete='CASCADE'))
    # user_id = db.Column(db.Integer(), db.ForeignKey(
    #     'user.id', ondelete='CASCADE'))
    # # can get name and surname of user from here
    # ticket_id = db.Column(db.Integer(), db.ForeignKey(
    #     'ticket.id', ondelete='CASCADE'))


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # controllable items start here
    title = db.Column(db.String(100), nullable=False)
    event_type = db.Column(db.Text, nullable=False)
    # date and time will be the event date and time

    event_date = db.Column(db.Date, nullable=False)
    time_from = db.Column(db.Time, nullable=False)
    time_to = db.Column(db.Time, nullable=False)

    # num_tickets = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    content_eng = db.Column(db.Text, nullable=True)
    address = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)

    tickets = db.relationship(
        'Ticket', backref='event', lazy=True, cascade='all,delete-orphan')

    image_file = db.Column(db.String(20), nullable=False,
                           default='default_event.jpg')

    # automatically set items start here
    # date_posted will be for when the event is created
    date_posted = db.Column(db.DateTime, nullable=False,
                            default=datetime.utcnow)
    # lower case, table and column name is referenced
    # for backref/relationship purposes
    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id'), nullable=False)

    staffers = db.relationship('User', secondary='event_staff',
                               backref=db.backref('users', lazy='dynamic'))
    # automatically set items stop here

    def __repr__(self):  # how our object is printed
        return f"Event('{self.title}','{self.date_posted}','{self.content}')"


class EventStaff(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey(
        'user.id', ondelete='CASCADE'))
    event_id = db.Column(db.Integer(), db.ForeignKey(
        'event.id', ondelete='CASCADE'))


class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey(
        'event.id', ondelete='CASCADE'), nullable=False)
    ticket_type = db.Column(db.String(30), nullable=False)
    # number of tickets per type
    num_tickets = db.Column(db.Integer, nullable=False)
    num_bought = db.Column(db.Integer, nullable=False, server_default="0")
    price = db.Column(db.Float, nullable=False)


####### SCHEMAS ########
# https://marshmallow-sqlalchemy.readthedocs.io/en/latest/
# https://marshmallow.readthedocs.io/en/stable/api_reference.html

class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_relationships = True
        load_instance = True
        exclude = ("password",)
        # sqla_session = db.session


class EventSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Event
        include_relationships = True
        include_fk = True
        load_instance = True
        # sqla_session = db.session


class TicketSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Ticket
        include_fk = True
        load_instance = True
        # sqla_session = db.session


class EventStaffSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = EventStaff
        include_fk = True
        load_instance = True
        include_relationships = True


class UserBookingsSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = UserBookings
        include_fk = True
        load_instance = True
        include_relationships = True


user_schema = UserSchema()
users_schema = UserSchema(many=True)
event_schema = EventSchema()
events_schema = EventSchema(many=True)
ticket_schema = TicketSchema()
tickets_schema = TicketSchema(many=True)
eventstaff_schema = EventStaffSchema()
eventstaffs_schema = EventStaffSchema(many=True)
userbooking_schema = UserBookingsSchema()
userbookings_schema = UserBookingsSchema(many=True)

# to delete child object when parent is deleted
# https://gist.github.com/davewsmith/ab41cc4c2a189ecd4677c624ee594db3
# https://docs.sqlalchemy.org/en/13/orm/cascades.html#delete
