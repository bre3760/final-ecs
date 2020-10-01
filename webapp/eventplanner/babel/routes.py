from flask import render_template, request, Blueprint
from flask import ( url_for, flash,
                   redirect, abort, jsonify,session)
from eventplanner.models import Event
from eventplanner import babell, gettext
import os
from eventplanner import db, bcrypt, csrf

babel = Blueprint('babel', __name__)

@babell.localeselector
def get_locale():
    if session['lang']:
        return session['lang']
    else:
        return 'en'

@babel.route('/lang',methods = ['GET','POST'])
@csrf.exempt
def get_lang():
    if request.method == 'POST':
        if request.form['lang']:
            lang = request.form['lang']
            session['lang'] = lang
            print("from form",lang)
    return render_template('multi_lang.html')

# @babel.route('/lang',methods=['POST'])
# @csrf.exempt
# def chenge_lang():
#     if request.form['lang']:
#         lang = request.form['lang']
#         print("from form",lang)
#     return redirect(url_for('babel.get_lang'))
"""
flash(gettext("string to translate"))
jsonify(gettext("string"))
gettext("string")


for html
{{_('to translate')}}

"""
