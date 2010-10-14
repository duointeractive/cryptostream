from Crypto.Cipher import XOR
import datetime
import urlparse
import datetime
import time
import base64
import urllib


# Encryption Key
KEY = 'foobar'

# Time for link to remain active.  Can be any amount of time.
timedelta = datetime.timedelta(hours=4)

def app(environ, start_response):
    data = environ['PATH_INFO']
    qs = urlparse.parse_qs(environ['QUERY_STRING'])

    ### Decode from base64
    try:
        path = base64.b64decode(qs['path'][0])
        ts = base64.b64decode(qs['ts'][0])
    except:
        return ErrorPage(environ, start_response)

    ### Decrypt using XOR
    try:
        path = XOR.new(KEY).decrypt(path)
        ts = datetime.datetime.fromtimestamp(float(XOR.new(KEY).decrypt(ts)))
    except:
        return ErrorPage(environ, start_response)

    dbg = path

    now = datetime.datetime.now()
    if (now-ts) > timedelta:
        ### Expired
        return ErrorPage(environ, start_response)
    else:
        ### Recent Enough
        status = '200 OK'
        response_headers = [
            ('Content-type','text/plain'),
            ('X-Accel-Redirect', path),
            ('Content-Length', str(len(dbg)))
        ]
        start_response(status, response_headers)
        return dbg


def ErrorPage(environ, start_response):
    status = '200 OK'
    message = "This page has expired!"
    response_headers = [
        ('Content-type','text/plain'),
        ('Content-Length', str(len(message)))
    ]
    start_response(status, response_headers)
    return message

def EncryptURL(path):
    path = XOR.new(KEY).encrypt(path)
    ts = XOR.new(KEY).encrypt(time.time().__str__())
    path = base64.b64encode(path)
    ts = base64.b64encode(ts)

    return urllib.urlencode({"path": path, "ts": ts})


