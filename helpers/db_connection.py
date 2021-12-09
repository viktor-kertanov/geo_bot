import sqlite3

class DatabaseCursor:
    """
    Creating a context manager for a database in order to make it more stable -- commit when there's no
    exceptions; close connection when there's an exception in order not to leave an open connections.
    """
    def __init__(self, host):
        self.connection = None
        self.host = host

    def __enter__(self):
        self.connection = sqlite3.connect(self.host)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_value, exc_tb):
        if exc_type or exc_value or exc_tb:
            self.connection.close()
        else:
            self.connection.commit()
            self.connection.close()
