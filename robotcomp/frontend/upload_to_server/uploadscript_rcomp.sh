#!/bin/bash
echo "Press [CTRL+C] to stop.."
while :
do
    rm -Rf 127.0.0.1+8000
	wget --recursive  --html-extension --convert-links --restrict-file-names=windows --domains localhost --no-parent http://127.0.0.1:8000/public_data/
	sshpass -p "1HlLBytq2hCH" scp -P 21098 ./127.0.0.1+8000/public_data/index.html rcomhyvk@198.54.116.137:www
	sleep 5
done
