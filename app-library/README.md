
# App Library

The following repo will have information about an app oriented to a Library.

Some of the purposes to create the current repo were to promote the knowledge and practice of `FastApi`.

## Setup

- Start the db container:
```sh
docker-compose up -d db && docker-compose logs --tail=10 -f db
```
- Create a virtualenv and install the app dependencies:
```sh
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
- Start the app:
```sh
uvicorn app.main:app --reload --reload-exclude venv
```
- Open a browser and hit the url: http://localhost:8000/docs
- (**Optional**) To get out of the virtualenv:
```sh
deactivate
```

## DB Migrations

- Run the app migrations:
```sh
alembic upgrade head
```
- To check the current revision:
```sh
alembic current
```
- To run a specific revision:
```sh
alembic upgrade <revision-id>
```
- To check all revisions(migrations):
```sh
alembic history
```

## Unit Tests


