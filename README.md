# interior-generator

1) clone the repository

2) create virtualenv via virtualenv --python=/usr/bin/python3.7 venv

3) active virtualenv via source venv/bin/activate\ 

Or just use PyCharm for making virtualenv for you.

4) install the dependencies via pip install -r requirements.txt

5) change directory to webapp via cd webapp

6) download static files with:  python manage.py collectstatic (now it is about server part)

7) run migrations via python manage.py migrate (it is a optional, not used for now)

8) run the web application server via python manage.py runserver
