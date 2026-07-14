import warnings
import sqlite3
import os

warnings.warn("database.py is deprecated and will be removed. Use Scoped MemoryRepository instead.", DeprecationWarning, stacklevel=2)

def get_connection():
    raise NotImplementedError("database.py is deprecated.")
