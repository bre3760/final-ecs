from flask import render_template, request, Blueprint
from flask import ( url_for, flash,
                   redirect, abort, jsonify,session)
from eventplanner.models import Event
from eventplanner import babell, gettext
import os
from eventplanner import db, bcrypt, csrf

babel = Blueprint('babel', __name__)

@babell.localeselector
def get_locale_user():
    print("in localeselector")
    if session.get('lingua',None) :
        return session.get("lingua",None)
    else:
        return 'en'

@babel.route('/lang',methods = ['GET','POST'])
@csrf.exempt
def get_lang():
    if request.method == 'POST':
        if request.form['lello'] == 'en':
            lang = request.form['lello']
            session['lingua'] = lang
            print("from form",lang)
        if request.form['lello'] == 'it':
            lang = request.form['lello']
            session['lingua'] = lang
            print("from form",lang)
        return render_template('multi_lang.html')
    if request.method == 'GET':
        return render_template('multi_lang.html')


"""
flash(gettext("string to translate"))
jsonify(gettext("string"))
gettext("string")


for html
{{_('to translate')}}

"""
