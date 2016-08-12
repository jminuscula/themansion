# The Mansion
App-driven board game. *Cluedo* meets *Werewolves of Millers Hollow*.

# Installation

This project requires Python 3.5

  1. Clone this repository

      `$ git clone git@github.com:jminuscula/themansion.git`

  2. Create a new virtual env

      `./themansion $ pyvenv-3.5 env`

  3. Activate your environment

      `./themansion $ source env/bin/activate`

  4. Install requirements

      `./themansion/server $ pip install -r requirements.txt -r dev-requirements.txt`

  5. Create database

      `./themansion/server $ ./manage.py migrate`

  6. Run development server

      `./themansion/server $ ./manage.py runserver`
