# MyQttHub.com Python support for MyQttHub API
# Copyright 2019 Advanced Software Production Line, S.L
# 
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import json
import httplib
import base64

verbose = False

def dbg (msg):
    if verbose:
        print msg
    return

def create_session (client_id, user_name, password, clean_session = True, host = "node02.myqtthub.com", port = 443):
    """
    Login to the platform.

    Allows to create a HTTPS session with MyQttHub.com using host and
    port provided.
    
    During authentication process, provided client_id, user_name and
    password will be used.
    
    
    Function returns a tuple containing (status, info, session), where
    status is a True/False according to login session status, info is
    a textual diagnotic message and session is the object used in next
    calls to the API to identify your session.


    Working connect example is:

    # connect to MyQttHub : REST API (use default host and port)
    import myqtthub
    (status, info, session) = myqtthub.create_session (client_id, user_name, password)
    if not status:
        print "ERROR: failed to connect to MyQttHub.com. Error was: %s" % session
        sys.exit (-1)
    # Reached this point, session holds a session token that will be required for next steps

    You can enable debug during operation by enabling verbose flag
    before any call:
    
    import myqtthub
    myqtthub.verbose = True

    """
    
    
    # get connection to the host configured
    dbg ("MYQTT CONNECT: connecting to %s:%s (clientId=%s, userName=%s)" % (host, "443", client_id, user_name))
    conn = httplib.HTTPSConnection (host, port)

    # build login parameters do login
    params = {
        'clientId' : client_id,
        'userName' : user_name,
        'password' : password,
        'cleanSession' : clean_session
    }
    # send request
    conn.request ("POST", "/login", json.dumps (params), headers = {"Connection":" keep-alive"})
    result = conn.getresponse()
    body   = result.read ()
    
    dbg ("INFO: login request result: %s" % result)
    if result.status != 200:
        # close connection
        conn.close ()
        return (False, "LOGIN ERROR: status=%d, reason=%s :: %s" % (result.status, result.reason, body), None)

    # Login ok
    login_data = json.loads (body)
    dbg ("MYQTT CONNECT: login request: status=%d, reason=%s :: %s (token: %s)" % (result.status, result.reason, login_data, login_data['tokenId']))

    # return data from login
    session = {'login_data' : login_data, 'conn' : conn, 'client_id' : client_id, 'user_name' : user_name}
    return (True, "Login ok", session)


def __prepare_headers (session):
    """
    Internal helper function to handle session when calling MyQttHub
    API

    """

    # get login session and connection
    login_data = session['login_data']
    conn       = session['conn']

    # build login parameters do login
    params  = { 'tokenId' : login_data['tokenId'] }
    headers = {
        'Cookie' : "tokenId=%s" % login_data['tokenId'],
        "Connection":" keep-alive"
    }

    # return common headers
    return (conn, login_data, params, headers)


def publish (session, topic, qos, msg, retain = False, dup = False):
    """
    
    Allows to publish a message over a open MyQttHub session (see
    create_session), by publishing a message with the provided topic,
    qos and message.

    Params:

    session -- [Object] created by create_session
    topic   -- [String] plain string representing the topic to publish to: test/this/topic, temp/device/001
    qos     -- [Int]  valid QoS value, 0, 1 or 2
    msg     -- [Opaque] Opaque string, binary, json, textual message to send as body content for the message.
    
    Example:
    
    # session is the object you got as a result of calling to myqtthub.create_session
    myqtthub.publish (session, "this/is/a/test", 0, "Your message content")


    """

    # get login session and connection 
    (conn, login_data, params, headers) = __prepare_headers (session)

    # params 
    params['topic'] = topic # String value 
    params['qos'] = qos  # Int value, 0, 1, 2
    params['payload'] = base64.b64encode (msg)  # Message base64 encoded
    params['retain'] = False
    params['dup'] = False
    
    # send PUBLISH
    dbg ("PUBLISH :: (%s) by (clientId=%s, userName=%s).." % (topic, session['client_id'], session['user_name']))
    conn.request ("POST", "/publish", json.dumps (params), headers)
    
    dbg ("INFO: publish request sent, waiting for response..")
    result = conn.getresponse()
    body   = result.read ()
    dbg ("INFO: publish request result: %s" % result)
    if result.status != 200:
        return (False, "PUBLISH ERROR: status=%d, reason=%s :: %s" % (result.status, result.reason, body))
    # end if

    return (True, "PUBLISH: message published without error")

def domain_view (domain_name, session):
    """
    Implements /domain/view API: allows to get complete reference of
    the domain/hub object by the provided name, according to current
    permissions.
    
    Connected session needs to be an admin with access to the provided
    domain in order to get valid data.
    """

    # get login session and connection 
    (conn, login_data, params, headers) = __prepare_headers (session)

    # params 
    params['domain'] = domain_name
    
    # send PUBLISH
    dbg ("DOMAIN-VIEW :: (%s) by (clientId=%s, userName=%s).." % (domain_name, session['client_id'], session['user_name']))
    conn.request ("POST", "/domain/view", json.dumps (params), headers)
    
    dbg ("INFO: request sent, waiting for response..")
    result = conn.getresponse()
    body   = result.read ()
    dbg ("INFO: request result: %s" % result)
    if result.status != 200:
        return (False, "ERROR: status=%d, reason=%s :: %s" % (result.status, result.reason, body))
    # end if

    return (True, json.loads (body))

def list_domains (session):
    """
    Implements /domain/list API: allows to list all domains (MyQtt Hubs) available
    for the current admin logged.
    
    Connected session needs to be an admin of at last one domain (MyQtt Hubs).

    """

    # get login session and connection 
    (conn, login_data, params, headers) = __prepare_headers (session)

    # send PUBLISH
    dbg ("DOMAIN-LIST :: by (clientId=%s, userName=%s).." % (session['client_id'], session['user_name']))
    conn.request ("POST", "/domain/list", headers = headers)
    
    dbg ("INFO: request sent, waiting for response..")
    result = conn.getresponse()
    body   = result.read ()
    dbg ("INFO: request result: %s" % result)
    if result.status != 200:
        return (False, "ERROR: status=%d, reason=%s :: %s" % (result.status, result.reason, body))
    # end if

    return (True, json.loads (body))


def logout (session):
    """
    Allows to close an open MyQttHub session returned by create_session
    
    Example:
    
    # logoout from MyQttHub.com
    myqtt.logout (session)
    """

    # get login session and connection 
    (conn, login_data, params, headers) = __prepare_headers (session)
    
    # send request
    conn.request ("POST", "/logout", json.dumps (params), headers)
    result = conn.getresponse()
    body   = result.read ()
    
    dbg ("LOGOUT :: response status=%d, reason=%s :: %s" % (result.status, result.reason, body))
    conn.close ()
    
    if result.status != 200:
        return (False, "LOGOUT ERROR: status=%d, reason=%s :: %s" % (result.status, result.reason, body))
        
    return (True, "INFO: logout request OK: status=%d, reason=%s :: %s" % (result.status, result.reason, body))
