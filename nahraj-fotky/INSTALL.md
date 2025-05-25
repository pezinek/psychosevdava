Install instructions for Ubuntu:
--------------------------------

# needed to compile pillow (likely optional if wheel is available)
sudo apt install libtiff5-dev libjpeg8-dev libopenjp2-7-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python3-tk libharfbuzz-dev libfribidi-dev libxcb1-dev
sudo apt install python3-dev

# for converting movies to thumbnails
sudo apt install ffmpeg

cd /var/www/

git clone git@github.com:pezinek/psychosevdava.git

cd /var/www/psychosevdava/nahraj-fotky/
make clean venv setup-dirs install-service


# setup nginx
ln -s /var/www/psychosevdava/psychosevdava.nginx /etc/nginx/sites-available/psychosevdava
nginx -t
systemctl restart nginx

