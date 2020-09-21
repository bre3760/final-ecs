import os
import secrets
from PIL import Image
from flask import url_for, current_app

from flask_mail import Message
from eventplanner import mail
import string


# def save_picture(form_picture, eventid):
#     f_name, f_ext = os.path.splitext(form_picture.filename)
#     picture_fn = str(eventid) + f_ext
#     picture_path = os.path.join(
#         current_app.root_path, 'static/event_pics', picture_fn)
#     # we risize the picture
#     output_size = (250, 250)
#     i = Image.open(form_picture)
#     i.thumbnail(output_size)
#     i.save(picture_path)
#     return picture_fn

def save_picture(form_picture, eventid):
    random_hex = secrets.token_hex(8)
    f_name, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(
        current_app.root_path, 'static/event_pics', picture_fn)
    # we risize the picture
    output_size = (250, 250)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn


def save_picture_api(file, event_id):
    f_name, f_ext = os.path.splitext(file.filename)
    filename = str(event_id) + f_ext
    # file.save(os.path.join(current_app.root_path,
    #                            'static/event_pics', filename))
    picture_path = os.path.join(
        current_app.root_path, 'static/event_pics', filename)
    # we risize the picture
    output_size = (250, 250)
    i = Image.open(file)
    # i.thumbnail(output_size)
    i.save(picture_path)
    return filename
