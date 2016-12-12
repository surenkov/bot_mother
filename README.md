## Installation instructions:
### Download pypy3
Download and unpack pypy3 under `env` folder from [PyPy website](http://pypy.org/download.html#default-with-a-jit-compiler)

### Install pip and dependencied
```
./env/bin/pypy3 -m ensurepip
./env/bin/pip install -r requirements.txt
```

### Make database migrations
```
./env/bin/pypy3 manage.py makemigrations
./env/bin/pypy3 manage.py migrate
```

### Run tests (optional)
```
./env/bin/pypy3 manage.py test
```

### Run Django dev server
```
./env/bin/pypy3 manage.py runserver
```
