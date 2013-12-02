#!/bin/sh

if  [ -z "$1" ] || [ -z "$2" ]; then
  echo '\nUSAGE: update_via_git.sh <username> <directory>\n'
  exit 1
fi

USERNAME=$1
DIRECTORY=$2

sudo chown $USERNAME:www-data $DIRECTORY -R
git reset --hard HEAD
git pull
sudo chown $USERNAME:www-data $DIRECTORY -R
pip install -r libre/requirements.txt
./manage.py migrate
sudo rm `find -name "*.pyc*"` -f
./manage.py collectstatic --noinput
sudo chown www-data:www-data $DIRECTORY -R
sudo /etc/init.d/apache2 restart
