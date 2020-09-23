import json
from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint, jsonify, current_app, make_response)
from flask_login import current_user, login_required
from eventplanner import db, csrf
from eventplanner.models import User, Role, UserRoles, Event, EventStaff, Ticket, event_schema, events_schema, UserBookings

import qrcode
from PIL import Image
import secrets

import os
import smtplib
import imghdr
from email.message import EmailMessage
from eventplanner.utilities.pdfGen import create_pdf_receipt

# for payments
emails = Blueprint('emails', __name__)


# # EMAIL_ADDRESS = os.environ.get('EMAIL_USER')
# # EMAIL_PASSWORD = os.environ.get('EMAIL_PASS')
EMAIL_ADDRESS = 'eventsbypolito@gmail.com'
EMAIL_PASSWORD = 'WebDevelopment123!'


def generate_email(subject, emailTo, content, filename):
    print("yo")
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = emailTo

    msg.set_content(content)

    files = filename  # filenames have complete path
    for file in files:
        with open(file, 'rb') as f:
            file_data = f.read()
            file_name = f.name

    msg.add_attachement(file_data, maintype='application',
                        subtype='octet-stream', filename=file_name)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)
    return ('sent')


@emails.route('/testing-email')
def send_email():
    generate_email()
    return render_template('emails/testing_emails.html')
