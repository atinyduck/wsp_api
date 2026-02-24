# database.py

import mysql.connector
from mysql.connector import Error
from fastapi import HTTPException

# Helper for GET endpoints
def execute_query(connection, query, params=None, fetch="all"):
    """ A helper function to execute a query and fetch results. fetch: 'one' or 'all' """
    cursor = connection.cursor(dictionary=True)
    
    # Attempt to execute the query
    try:
        cursor.execute(query, params or ())
        
        result = cursor.fetchone() if fetch == "one" else cursor.fetchall()
        
        # Check if it exists and raise 404 if not found
        if result is None:
            raise HTTPException(status_code=404, detail="Record not found")
        
        return result
    
    # Handle any database errors
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    
    # Ensure the cursor is closed after operation
    finally:
        cursor.close()

# Helper for POST endpoints
def execute_insert(connection, query, params):
    """ A helper function to execute an insert query. """
    cursor = connection.cursor()
    
    # Attempt to execute the insert
    try:
        cursor.execute(query, params)
        connection.commit()
        return cursor.lastrowid
    
    # Handle any database errors
    except mysql.connector.Error as err:
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    
    # Ensure the cursor is closed after operation
    finally:
        cursor.close()

# Database connection dependency
def get_db_connection():
    """ Establish a connection to the Washing State Patrol MySQL databse """
    connection = None
    
    # Attempt to connect to the database
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='WSP_System',
            user='root',
            password='awsp3142'
        )
        if connection.is_connected():
            yield connection
    
    # Handle any connection errors
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
    
    # Ensure the connection is closed after use
    finally:
        if connection and connection.is_connected():
            connection.close()
            
# end of database.py