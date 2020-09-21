from eventplanner import create_app
app = create_app()
app.app_context().push()
from eventplanner import db
db.drop_all()
db.create_all()
