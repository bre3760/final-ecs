import os
# need to be set as environment variables


# class Config:
#      SECRET_KEY = '483757cd797387a0e9855ac1dc2d8aaa'
#      SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:WebDevelopment123!@localhost/eventsbypolito'
#      # SECRET_KEY = os.environ.get('SECRET_KEY')
#      # SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
#      MAIL_SERVER = 'smtp.googlemail.com'
#      MAIL_PORT = 587
#      MAIL_USE_TLS = True
#      # environment variable watch video later
#      # MAIL_USENAME = os.environ.get('EMAIL_USER')
#      # MAIL_PASSWORD = os.environ.get('EMAIL_PASS')  # jacopo & WebDevelopment123!
#      MAIL_USENAME = 'jacopo'
#      MAIL_PASSWORD = 'WebDevelopment123!'
#      ADMIN = 'brendandavidpolidori@gmail.com'

#
class Config:
    SECRET_KEY = '483757cd797387a0e9855ac1dc2d8aaa'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    # SQLALCHEMY_DATABASE_URI = 'postgresql:///site.db'#

    # SECRET_KEY = os.environ.get('SECRET_KEY')
    # SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    # environment variable watch video later
    # MAIL_USENAME = os.environ.get('EMAIL_USER')
    # MAIL_PASSWORD = os.environ.get('EMAIL_PASS')  # jacopo & WebDevelopment123!
    MAIL_USENAME = 'jacopo'
    MAIL_PASSWORD = 'WebDevelopment123!'
    ADMIN = 'brendandavidpolidori@gmail.com'
# https://github.com/antkahn/flask-api-starter-kit


# While there are a lot of nice answers here, I didn't see a solution posted that both includes unsetting
# environment variables on deactivate and doesn't require additional libraries beyond virtualenv, so here's my
# solution that just involves editing /bin/activate, using the variables MY_SERVER_NAME and MY_DATABASE_URL as examples:

# There should be a definition for deactivate in the activate script, and you want to unset your variables at the end of it:

# deactivate () {
#     ...

#     # Unset My Server's variables
#     unset MY_SERVER_NAME
#     unset MY_DATABASE_URL
# }
# Then at the end of the activate script, set the variables:

# # Set My Server's variables
# export MY_SERVER_NAME="<domain for My Server>"
# export MY_DATABASE_URL="<url for database>"
# This way you don't have to install anything else to get it working, and you don't end up with the variables being left over when you deactivate the virtualenv.


# export SECRET_KEY="483757cd797387a0e9855ac1dc2d8aaa"
