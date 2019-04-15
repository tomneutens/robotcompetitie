run the django server with the following command to have access over the network:

sudo python manage.py runserver 0.0.0.0:8000 --insecure

This required the debug mode to be false in the settings.py file!


