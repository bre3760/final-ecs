from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, TextAreaField, IntegerField, SelectField, FieldList, FormField, DecimalField
from wtforms.validators import DataRequired, Required, Length, Email, EqualTo, ValidationError
from wtforms.fields.html5 import DateTimeLocalField, TimeField, DateField
from wtforms import Form
from eventplanner.models import Event, Ticket
# https://stackoverflow.com/questions/49697545/flask-wtform-datetimefield-rendering-issue
# https://wtforms.readthedocs.io/en/2.3.x/fields/#wtforms.fields.SelectField
# https://stackoverflow.com/questions/52825708/wtforms-datetimelocalfield-data-is-none-after-submit
# https://wtforms.readthedocs.io/en/2.3.x/fields/
# https://github.com/sebkouba/dynamic-flask-form for e fieldlist and formfield together


class TicketForm(Form):
    #     ticket_type = StringField(validators=[DataRequired()])
    #     num_tickets = IntegerField(validators=[DataRequired()])
    #     price = DecimalField(validators=[DataRequired()])
    ticket_type = StringField()
    num_tickets = IntegerField()
    price = DecimalField()


class EventForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    event_type = SelectField(u'Event type', choices=[(
        '0', 'music'), ('1', 'theatre'), ('2', 'sports'), ('3', 'movies'), ('4', 'culture'), ('5', 'other')])
    event_date = DateField(
        'Date of Event', format='%Y-%m-%d', validators=[Required()])
    time_from = TimeField(
        'Start time',  format='%H:%M', validators=[Required()])
    time_to = TimeField(
        'End time',  format='%H:%M', validators=[Required()])

    content = TextAreaField('Content', validators=[DataRequired()])
    content_eng = TextAreaField('English Content (Optional)')
    address = StringField('Address', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])

    tickets = FieldList(
        FormField(TicketForm, default=lambda: Ticket()),
        min_entries=1,
        max_entries=20
    )
    picture = FileField('Event Picture', validators=[
                        FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Create Event')


class UpdateEventTicketsForm(FlaskForm):
    tickets = FieldList(
        FormField(TicketForm, default=lambda: Ticket()),
        min_entries=0,
        max_entries=20
    )
    submit = SubmitField('Update Tickets')


class AddTicketsForm(FlaskForm):
    tickets = FieldList(
        FormField(TicketForm, default=lambda: Ticket()),
        min_entries=1,
        max_entries=20
    )
    submit = SubmitField('Add Tickets')


class StaffForm(FlaskForm):
    staffer_email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Add Staffer')
