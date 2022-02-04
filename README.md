# Foobartory Back (Alma technical test)

Project developed for the Foobartory Back technical test

## Global infos:

### Contact

[Valentin Dulong](https://github.com/Imowt)

valentin.dulong.pro@gmail.com or 06 63 61 14 10 if you have any question

### Test feedback

It was very original and cool subject to work on

## How to run

### docker-compose

#### Requirements

- Docker to be running

#### Run

In the root directory:
```
docker-compose up --build
```

### Using foobartory/main.py

#### Requirements

- Python ~=3.9
- pipenv to be installed (pip install pipenv)
- run `pipenv sync --dev` (--dev option is needed to be able to run the tests)

#### Run

If your environment is setup, you can now launch the project using the foobartory/main.py.

In the root directory:
```
python -m foobartory.main
```

### Tests

All the method are tested, you can find the tests in the `tests` folder

#### Run

**You first need to setup your pipenv environment**

Then in the root directory you can run:
```
coverage run -m pytest
coverage report
```

## .env

All the subject variables can be found and modified in the .env file

