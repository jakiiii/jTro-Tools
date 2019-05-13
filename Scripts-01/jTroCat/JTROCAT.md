# jtrocat.py

## Use

Open a terminal and type

`./jtrocat -l localhost -p 9999 -c`

Then open another terminal and use this command,

`./jtrocat.py -t localhost -p 9999`

We can run some local commands and receive back some output as if we had logged in via SSH or on the box locally.

`echo "GET / HTTP/1.1/r/nHOST: www.facebook.com\r\n\r\n" | ./jtrocat.py -t www.facebook.com -p 80`
