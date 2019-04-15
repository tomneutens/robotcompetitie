uploadscript.sh sends the public data page to a webserver every 25 seconds.

since the server is behind a ugent firewall you need to tunnel your ssh connection through the elis ssh server with the following command.

ssh -L 1234:smartproducts.ugent.be:22 tnneuten@ssh.elis.ugent.be cat -
