# MyQttHub
MyQttHub resources to work with MyQtthub.com cloud MQTT platform

See more at:
https://myqtthub.com

# How to integrate MyQttHub python/HTTP API into your project

## Summary

The following document explains how to connect your Python application
to MyQttHub using its HTTPS API. The document will walk you through:

1) Indications to open your MyQttHub
2) Create your MQTT devices
3) Connect using myqtthub helper file (using Python)

## Activate your MQTT Hub

1) Before you continue, you need to have a MyQttHub. For that, register
   and activate your MQTT hub at:

   https://myqtthub.com

   More information about MyQttHub Open Account at:
  
   https://support.asplhosting.com/t/how-to-create-your-myqtthub-com-open-account/30

2) Then you will need one or two credentials depending on your context
   and the kind of integration you want to do. Look here to create your devices/credentials:

   https://support.asplhosting.com/t/how-to-create-and-manage-your-mqtt-devices-with-myqtthub-com/32

## Download helper file to connect MyQtthub

3) Download first a copy of the following file or github fork:

  ```bash
  >> wget https://github.com/ASPLes/MyQttHub/blob/master/python/myqtthub.py
  ```

4) Now at your python files include it with:
  
  import myqtthub

## Basic example to connect, publish and disconnect

5) CONNECT: After that, create a session with:

   ```python
   # connect to MyQttHub : REST API (use default host and port)
   (status, info, session) = myqtthub.create_session (client_id, user_name, password)
   if not status:
       print "ERROR: failed to connect to MyQttHub.com. Error was: %s" % session
       sys.exit (-1)
   # Reached this point, session holds a session token that will be required for next steps
   ```

6) PUBLISH: to publish, send a message with:

   ```python
   # session is the object you got as a result of calling to myqtthub.create_session
   myqtthub.publish (session, "this/is/a/test", 0, "Your message content")
   ```


7) LOGOUT: remember to disconnect after finished to avoid leaving your session
   opened, holding connection space that might limit other connections:

   ```python
   # logoout from MyQttHub.com
   myqtt.logout (session)
   ```

## More information

See https://myqtthub.com for more information. 

You have an API manual here:

https://support.asplhosting.com/t/rest-api-to-manage-myqtthub-service/86

Use your MyQttHub to get support at:

https://support.asplhosting.com/c/myqtthub-en
https://support.asplhosting.com/c/myqtthub


