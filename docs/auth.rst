================
 Authentication
================

Merlyn exclusively uses TLS with certificate-based authentication.

Server authentication
---------------------

Clients come shipped with the server's certificate, and only accept
that certificate.

Client authentication
---------------------

When a client connects to the server for the first time, it generates
a client certificate. It uses the client certificate to connect. The
server refuses to perform any commands except the registration
command, which registers a user's e-mail address to the fingerprint of
the newly generated client certificate.

When the client connects to the server in the future, the server
automatically authenticates the client by checking the key
fingerprint.

This is essentially TOFU-POP (trust on first use, persistence of
pseudonym), except that the e-mail address is checked.
