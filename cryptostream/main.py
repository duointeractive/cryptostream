"""
Contains a basic WSGI app to secure media with a time-limited download.
See README.rst for full details.
"""
import datetime
import urlparse
import datetime
import time
import base64
import urllib
from Crypto.Cipher import XOR

"""
Configuration.
"""
# Encryption key. This needs to be kept secret.
KEY = 'foobar'
# Time for link to remain active. Can be any amount of time.
LINK_EXPIRE_TDELTA = datetime.timedelta(hours=1)

def app(environ, start_response):
    """
    WSGI app method. You'll want to point your WSGI server at this method.
    """
    data = environ['PATH_INFO']
    qs = urlparse.parse_qs(environ['QUERY_STRING'])

    # Decode from base64
    try:
        path = base64.b64decode(qs['path'][0])
        ts = base64.b64decode(qs['ts'][0])
    except:
        return render_error_page(environ, start_response)

    # Decrypt using XOR
    try:
        path = XOR.new(KEY).decrypt(path)
        ts = datetime.datetime.fromtimestamp(float(XOR.new(KEY).decrypt(ts)))
    except:
        return render_error_page(environ, start_response)

    dbg = path

    now = datetime.datetime.now()
    if (now - ts) > LINK_EXPIRE_TDELTA:
        # Expired
        return render_error_page(environ, start_response)
    else:
        # Recent Enough
        status = '200 OK'
        response_headers = [
            ('Content-type', 'text/plain'),
            ('X-Accel-Redirect', path),
            ('Content-Length', str(len(dbg)))
        ]
        start_response(status, response_headers)
        return dbg

def render_error_page(environ, start_response):
    """
    We're intentionally pretty vague with the error pages shown to the user.
    Just give them enough details to know that they're out of luck.
    """
    status = '200 OK'
    message = "This page has expired!"
    response_headers = [
        ('Content-type', 'text/plain'),
        ('Content-Length', str(len(message)))
    ]
    start_response(status, response_headers)
    return message

def encrypt_url(path):
    """
    Call this within your client app to generate a URL to query the
    Cryptostream WSGI app server with.
    """
    path = XOR.new(KEY).encrypt(path)
    ts = XOR.new(KEY).encrypt(time.time().__str__())
    path = base64.b64encode(path)
    ts = base64.b64encode(ts)

    return urllib.urlencode({"path": path, "ts": ts})
