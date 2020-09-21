# now we have an sqlalchemy database instance, we can represent our database structure as classes and we will call those classes models
# very intuitive
# each class is a database table

# url_for is a funcion that will find the exact locatioj of routes for us
# (flaskproject) brendanpolidori@BP flask_blog % export FLASK_APP=flaskblog.py
# (flaskproject) brendanpolidori@BP flask_blog % flask run
# export FLASK_DEBUG=1 to have the server update and not have to stop and run again
# one to many relationship for the database
from eventplanner import create_app

app = create_app()

if __name__ == '__main__':  # conditional only true if we run the script directly
    app.run(debug=True)