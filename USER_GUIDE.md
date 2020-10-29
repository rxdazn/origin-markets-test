# User guide

## Running the project locally

- create a virtual environment and activate it
- Install dependencies: `pip install -r requirements.txt`
- Move to the `origin/` folder
- Run database migrations `python manage.py migrate`
- Start the local server `python manage.py runserver`
- Create a user account `localhost:8080/login`

## Running the tests

- `python manage.py test`

## Populating the database with bonds

### Automated script

After having created a user account to obtain an API key, from the root of the
repository

`OM_TEST_API_KEY=your_key ./utils/populate_db.py`

Edit the contents of `populate_db.py` if you wish to change which entries are
created


## Seeing your bonds

Load up `http://localhost:8000/bonds/?api_key=your_key` in your browser
