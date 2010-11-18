============
Cryptostream
============

Cryptostream is a WSGI app serving as a very light security layer to protect
files. For example, if a user purchases some software, the store app would
use this WSGI app to generate a download URL that is only valid for a certain
amount of time.

A typical download works like this:

* As per the *Using* section below, your app uses encrypt_url() to generate
  a GET string.
* The GET string is sent to the cryptostream WSGI app.
* Cryptostream uses the `X-Accel-Redirect` header to pass the file directly
  to nginx, instead of serving it from within the WSGI app. 

Source: https://github.com/duointeractive/cryptostream

---------------------------
Cryptostream is good for...
---------------------------

* Disguising paths to downloads on your protected media server.
* Cases where you're just looking for a deterrent for someone passing out
  download links to their buddies.
  
-------------------------------
Cryptostream is not good for...
-------------------------------

* Cases where absolute maximum security is desired.

-------
Running
-------

Launch the main:app using gunicorn::

    gunicorn main:app

--------------------------------------
Using Cryptostream in your application
--------------------------------------

Application does two things:

1. Checks a timestamp to make sure the link was recently given to the user.
2. Redirect user to a static URL without giving this URL to the user.

To encrypt a url for cryptostream to decode, do something like this within
your app::

    >> from cryptostream.main import encrypt_url
    >> encrypt_url("/foo/bar/")
    'path=SQkADU4QBx0%3D&ts=V11XVVFAVFlaVE9AUg%3D%3D'

Then use these as GET keywords to the url cryptostream is running on.

-----------------
Configuring Nginx
-----------------

There are two variables in `main.py` that control behavior::

    # A Plain text encryption key
    KEY = 'foobar'  
    # Maximum time the link will be alive.
    LINK_EXPIRE_TDELTA = datetime.timedelta(hours=4)

Sample Nginx Server Config::

    server {
    	listen   80 default;
    	server_name  localhost;
    
    	access_log  /var/log/nginx/localhost.access.log;
    
    	# Serves up jpegs in my picture directory at root
    	location ~ \.(jpg|JPG)$ {
    		root   /home/dylan/Pictures;
    	}
    
    	# Gunicorn running the Cryptostream app
            location / {
                    proxy_pass http://127.0.0.1:8000/;
            }
    }
