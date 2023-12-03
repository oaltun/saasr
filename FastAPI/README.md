## SAASR BACKEND FRAMEWORK

# Requirements:

    DB: postgres 12
    OS: works on Windows WSL2 (Linux), but should work anywhere. Docker not needed.
    Python: 3.8.10
    Package Manager: Poetry

# Installation (WSL2)

## Install Requirements

- Install the Postgresql 12 db. In it create a db for your app. Lets say it is `app`. Also create a db called `app_test`. This will be used for running python tests.

- Install python 3.8.10.

  I think the easiest way to install a specific python version is through miniconda. For this, first install miniconda python distribution. That will add the command `conda` to your path. Following will create a virtual environment with python 3.8.10 in venv directory.

  > conda create -p c:\Users\oguz\Desktop\backend\venv python=3.8.10

- if you dont use conda and python 3.8.10 is already installed you can create a virtual environment with:
  > python3 -m venv venv
- Then activate that virtual enviornment. How you do this depends on OS and distribution:

  - Using conda: conda activate c:\Users\oguz\Desktop\backend\venv
  - On Unix or MacOS, using the bash shell: source /path/to/venv/bin/activate
  - On Unix or MacOS, using the csh shell: source /path/to/venv/bin/activate.csh
  - On Unix or MacOS, using the fish shell: source /path/to/venv/bin/activate.fish
  - On Windows using the Command Prompt: path\to\venv\Scripts\activate.bat
  - On Windows using PowerShell: path\to\venv\Scripts\Activate.ps1

  When you work on this project, always first activate this virtual environment. When you install python packages, they will be installed in this virtual environments. Different projects should have different virtual environments, so that package versions do not collide.

  Also in editors like vscode, select the interpreter in this environment as interpreter. This way, everything should work fine.

  When you finish working on this project, you can deactivate the virtual environment. To do that, you do something like

  > deactivate

  or something...

  But now, let us keep the virtual environment active, or re-activate it if you deactivated. Then

- install poetry into virtual environment.

  > python -m pip install poetry

- install packages into virtual environment:

  > poetry install

## Setup DB

- Using pgadmin4 or psql create two databases. Let us say first database name is app. The second database name should be app_test. First database will be for real application. Second database will be for pytest.

- copy `example_secret_values.py` to `secret_values.py`

- edit `secret_values.py`. things like iyzico key can be random strings. superuser email and password are necessary to login to the system after installation. token algorithm and database url parts also need to be correct.

## Run pytest tests

- Try running tests. If there is a mistake fix and report back.

  > pytest -x

## Create tables

- Since this will be a fresh install remove everything in app/alembic/versions.

- Create new alembic revisions:

  > python3 -m alembic.config revision --autogenerate -m "first"

  Check whether everything is OK in app/alembic/versions.

- Now create real database tables (on linux (and WSL2) python3, but on windows use python)

  > python3 -m alembic.config upgrade head

## Add initial data to the tables

- create initial data in the tables. The superuser mail and pass will come from secret_values.py, make sure they are good.:

  > python3 -m app.initial_data

## Start server

- start server. after that you can edit files and uvicorn will reload automatically

  > uvicorn app.main:app --host 0.0.0.0 --port 8888 --reload

  or

  > python3 -m app.main

- visit api documentation at http://localhost:8888/api/docs. Be carefull, address is NOT http://localhost:8888.

# CODING STYLE

## SECTIONS

Divide your code into sections with comments like:

    # ================== #
    # OPTIONAL FEAT DATA
    # ================== #

These comments can be picked up with a vscode extension called "better outline". This can make browsing code easier.

Keep the `=========`s short. They look ugly when wrapped.

## `FEAT`'s

Some frameworks call them plug-ins, some add-ins, some modules, some (like Django) apps, some blueprints... Let us call a feature that can be added and removed easily a `feat` here. Let us organize our code using these `feat`s, that are inspired from Django `app`s.

## CORE VS OPTIONAL FEATS

We consider some feats as core, so they live in the `app`. E.g. `user` is a core feat. Core feats should be there in all installations of this framework.

Some feats are optional, e.g. they may or may not be there in an installation. These feats live inside the `app/opt` . E.g. `app/opt/support` is an optional feat.

## FEAT DEPENDENCY

As optional feats like `support` may or may not exist in the installation, a core feats like `user` should not depend on their existence. E.g. they can not use names in them. They can not import their files.

Optional feats can depend on core feats. E.g. `support` can import `user` classes.

Optional feats can depend on each other, but for this the one depended on should be a python package and uploded to pypi like system. If you have more than one feats that work together, you can put them under a single directory under `opt`.

## FEAT CONTENTS

A `feat` should have all its files in a single folder.

A `feat` may includes following files:

- `__init__.py`: feats are python modules. so they need to have this file, even if it is empty. You may not be seeing these files in vscode, because vscode can be configured to hide these files.
- `router*.py`: api endpoint definitions.
- `test*.py`: test files.
- `schema*.py`: pydantic classes that define input/output of endpoints.
- `model*.py`: sqlalchemy classes that define database.
- `data*.py`: functions to populate the database.
- `crud*.py` or `util*.py`: create/read/update/delete classes/functions and other utility classes/functions.
- `html*.py`: templates for mails and such.
- ...

## NAMING CONVENTION

When should we use plural like `users` and when should we use singular like `user` when naming files and folders?

Let us keep it simple and always use singular like `user`, `test`, `schema`,... for everything.

## WRITING A NEW FEAT

You can start by making a copy of an existing feat like `user`. Let us say you want a new feature called `todo`. Just copy the `user` folder and paste into the `opt` folder. So, you should now have a `opt/user` folder. Rename it to `opt/todo`. Now you can rename/change files and contents in them.

### WIRING A NEW FEAT

Even though we have a naming convention, that does not make your `feat` recognisable by our framework. You have to wire everything manually. This is easy though, I will list necessary wiring, and you can just look at existing wiring there.

- Add routers from `router*.py` files to the `main.py`, just before `if __name__ == "__main__"`.
- Add Sqlalchemy models from `model*.py` files to alembic `env.py` file, just before `target_metadata = Base.metadata`.
- Add initial data from `data*.py` files to `app/initial_data.py`, under the `OPTIONAL FEAT DATA` section.
- This is not needed as of this code, but if your feat defines test fixtures that should be used by other feat tests, they would need proper wiring as described here: https://gist.github.com/peterhurford/09f7dcda0ab04b95c026c60fa49c2a68

Note: You will see that optional feat wirings are inside `try..except` blocks. This is to make removing their folders easier when sending framework to others.

### CREATING NEW FEAT TABLES

Database migration is done using alembic.

First create new revisions for your new models:

> python3 -m alembic.config revision --autogenerate -m "my new model"

Check whether everything is OK in the new revision file in app/alembic/versions.

- Now create real database tables:

  > python3 -m alembic.config upgrade head

### ADDING NEW FEAT INITIAL DATA

- Create new initial data in the tables.

  > python3 -m app.initial_data

Now visit the api documentation, your feat should be there.

## TYPE HINTS and MYPY

`mypy` uses type hints to find errors in your code before running it. As python is a dynamic language, if there is an error in a code block that you did not run somehow, that error will stay unnoticed. Type hints help find such errors with static analysis.

`mypy` should be already installed by poetry during package installation. There is a mypy extension in vscode. Let us use it.

This code was started without type hints. We typed it a bit, but a lot is missing. In new files all the code should be typed. Existing code should be fully typed when time permits (TODO).

## PEP 8

Python code should be written with the conventions described in https://peps.python.org/pep-0008/
