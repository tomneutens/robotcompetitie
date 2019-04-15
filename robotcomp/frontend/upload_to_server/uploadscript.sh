#!/bin/bash
echo "Press [CTRL+C] to stop.."
while :
do
	wget --recursive  --html-extension --convert-links --restrict-file-names=windows --domains localhost --no-parent 192.168.126.14:8080/public_data
	cd 192.168.126.14+8080
	cp public_data.html index.html
	sshpass -p "n3ut3n5" scp -P 1234 ./index.html tom@127.0.0.1:robotcompetition
	cd ..
	sleep 10
done
