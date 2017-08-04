# Marcus

A simple Django app to allow users to view footage from Raspberry Pi's set up as security cameras. Snapshots are stored on S3 to make destruction of the security camera a non issue. Additionally footage is accessible from anywhere AWS is accessible, this also means the RaspberryPi/Security camera must also be able to access AWS to upload footage.

Designed to be deployed using sqlite3 database on a nano instance with nginx and uwsgi. Maybe if you are planning on using this to secure a larger site, a full scale client/server DBMS may be required.
