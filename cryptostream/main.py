"""
Contains a basic WSGI app to secure media with a time-limited download.
See README.rst for full details.
"""
import os
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
KEY = 'CnQ2!7@!r$Q#nDA@aWFg'
# Time for link to remain active. Can be any amount of time.
LINK_EXPIRE_TDELTA = datetime.timedelta(hours=1)

def app(environ, start_response):
    """
    WSGI app method. You'll want to point your WSGI server at this method.
    """
    data = environ['PATH_INFO']
    # GET querystring.
    qs = urlparse.parse_qs(environ['QUERY_STRING'])

    # Decode from base64.
    try:
        path = base64.b64decode(qs['path'][0])
        ts = base64.b64decode(qs['ts'][0])
    except:
        return render_error_page(environ, start_response)

    # Decrypt using XOR.
    try:
        path = XOR.new(KEY).decrypt(path)
        ts = datetime.datetime.fromtimestamp(float(XOR.new(KEY).decrypt(ts)))
    except:
        return render_error_page(environ, start_response)

    # Determine what the file will be named for the user's browser.
    if qs.has_key('dl_filename'):
        # Filename was passed as a GET keyword.
        dl_filename = qs['dl_filename'][0]
    else:
        # No filename specified, use the name on the filesystem.
        dl_filename = os.path.basename(path)

    dbg = path
    now = datetime.datetime.now()
    if (now - ts) > LINK_EXPIRE_TDELTA:
        # Expired, show vague error page.
        return render_error_page(environ, start_response)
    else:
        # Everything is good, serve the file through X-Accel-Redirect.
        status = '200 OK'

        response_headers = [
            ('X-Accel-Redirect', path),
            ('Content-Disposition', 'attachment; filename=%s' % dl_filename),
        ]

        start_response(status, response_headers)
        # This needs to be an empty string or we'll get premature socket
        # closing errors. The body is ignored by Nginx, and the connection is
        # closed before this returned value can be read, causing the error.
        return ""

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

def encrypt_url(path, dl_filename=None):
    """
    Call this within your client app to generate a URL to query the
    Cryptostream WSGI app server with.
    
    path: (str) The URL path to the internal-flagged location
        on the Nginx server that the files will be served from via
        X-Accel-Redirect.
    dl_filename: (str/None) If specified, the file that the user downloads will
        be named according to the value, instead of from the name on 
        the filesystem.
    """
    # Encrypt the path and the timestamp.
    path = XOR.new(KEY).encrypt(path)
    ts = XOR.new(KEY).encrypt(time.time().__str__())
    # Encode path/ts to base 64.
    path = base64.b64encode(path)
    ts = base64.b64encode(ts)

    # This dict will get urlencoded as GET keywords.
    value_dict = {"path": path, "ts": ts}

    # Check for download filename override.
    if dl_filename:
        value_dict['dl_filename'] = dl_filename

    return urllib.urlencode(value_dict)
