while true; do
    # get the generated HTML file
    wget http://localhost:8000/public_data -O /tmp/public_data.html
    # copy the generated HTML file to the public server
    scp /tmp/public_data.html sander@benanne.net:/var/www/robotcompetitie/index.html
    # pause
    sleep 9
done