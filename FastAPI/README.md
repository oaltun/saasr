## SAASR FastAPI

A SaaS starter / template for FastAPI.

After the [installation](INSTALL.md), you should be able to see api documentation at http://localhost:8888/api/docs. Be carefull, address is NOT http://localhost:8888.

The superuser account you set up in .env file is active, so you can login with it.

The sign-up functionality is also active!

# ON THE CODING STYLE

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
