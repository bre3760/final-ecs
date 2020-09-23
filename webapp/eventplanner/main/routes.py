from flask import render_template, request, Blueprint
from eventplanner.models import Event
import os
main = Blueprint('main', __name__)


@main.route("/")  # route
@main.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    # passing an argument to a template
    # we want to paginate them
    events = Event.query.order_by(
        Event.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('home.html', events=events)


@main.route("/about")
def about():

    return render_template('about.html', title='About')


# print(os.path.join(current_app.root_path))

# /Users/brendanpolidori/Desktop/final-ecs/webapp/eventplanner
