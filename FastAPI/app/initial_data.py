#!/usr/bin/env python3

import sys
import os
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation

# ================== #
# PATH FIX FOR RUNNING DIRECTLY
# ================== #

# TODO: This path addition is probably unnecessary. Remove.
## add the parent directory into pythonpath
dirname = os.path.dirname(os.path.abspath(__file__))
sys.path.append(dirname + "/..")

from app.core.session import SessionLocal


# ================== #
# REQUIRED FEAT DATA
# ================== #

initial_data=list()

from app.user.data import init_superuser
initial_data.append({"message":"Init super user", "fun":init_superuser})


# ================== #
# OPTIONAL FEAT DATA
# ================== #

try:
    from app.opt.subscription.data import init_billing_cycles, init_plans, init_prices
    initial_data.extend([
        {"message":"Init billing cycles", "fun":init_billing_cycles},
        {"message":"Init plans",          "fun":init_plans},
        {"message":"Init prices",         "fun":init_prices},
    ])
except:
    pass


# ==================== #
# INITIALIZOR FUNCTION
# ==================== #

def init_all(db,show_messages=False):
    """Used by tests and __main__"""

    for init in initial_data:
        if show_messages: 
            print(init["message"],": ",)
        try:
            init["fun"](db)
            if show_messages:
                print("Done.")
        except IntegrityError as e:
            assert isinstance(e.orig, UniqueViolation)
            if show_messages:
                print("Skipping, already initialized.")
            db.rollback()
        except Exception as e:
            print(e)
            db.rollback()

        
# ==================== #
# MAIN
# ==================== #

if __name__ == "__main__":
    print("In initial_data.py")
    db = SessionLocal()
    if not db:
        print("could not connect to db")
    init_all(db,True)    
        
