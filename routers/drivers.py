# drivers.py
# FastAPI application for Washington State Patrol system - Driver endpoints.
# =========================================================


from fastapi import APIRouter, Depends, HTTPException
import database.database as database, models as models
from typing import List
import auth

router = APIRouter(prefix="/drivers", tags=["Drivers"])

@router.get("/", response_model=List[models.DriverResponse])
def read_all_drivers(
    connection=Depends(database.get_db_connection), 
    current_user: str=Depends(auth.verify_token)):
    """ Retrieve a list of all drivers. """ 
    
    query = "SELECT * FROM Driver"
    
    return database.execute_query(connection, query)

@router.get("/{driver_id}", response_model=models.DriverResponse)
def read_driver(
    driver_id: int, 
    connection=Depends(database.get_db_connection),
    current_user: str=Depends(auth.verify_token)):
    """ Retrieve a driver by their ID. """
    
    query = "SELECT * FROM Driver WHERE Driver_ID = %s"
    
    return database.execute_query(connection, query, (driver_id,), fetch="one")

@router.post("/", response_model=models.DriverResponse, status_code=201)
def create_driver(
    driver: models.DriverCreate, 
    connection=Depends(database.get_db_connection),
    current_user: str=Depends(auth.verify_token)):
    """ Create a new driver record. """
    
    try:
        # Use the helper function to execute the insert
        driver_id = database.execute_insert(
            connection,
            "INSERT INTO Driver (First_Name, Last_Name, Address, Birth_Date, License_Number, License_State) VALUES (%s, %s, %s, %s, %s, %s)",
            (driver.First_Name, driver.Last_Name, driver.Address, driver.Birth_Date, driver.License_Number, driver.License_State)
        )
        
        # Retrieve and return the newly created driver
        return database.execute_query(connection, "SELECT * FROM Driver WHERE Driver_ID = %s", (driver_id,), fetch="one")
    
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")

@router.put("/{driver_id}/address", status_code=204)
def update_driver_address(
    driver_id: int, new_address: str, 
    connection=Depends(database.get_db_connection),
    current_user: str=Depends(auth.verify_token)):
    """ Update the address of a driver. """
    
    try:
        # Update the driver's address
        database.execute_query(connection, "UPDATE Driver SET Address = %s WHERE Driver_ID = %s", (new_address, driver_id), fetch=None)

    
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")

@router.delete("/{driver_id}", status_code=204)
def delete_driver(
    driver_id: int, 
    connection=Depends(database.get_db_connection),
    current_user: str=Depends(auth.verify_token)):
    """ Delete a driver record by ID. """
    
    # Check if the driver exists before attempting to delete
    database.execute_query(connection, "SELECT * FROM Driver WHERE Driver_ID = %s", (driver_id,), fetch="one")
    
    # Attempt to delete the driver and handle any database errors
    try:
        # Use the helper function to execute the delete
        database.execute_insert(connection, "DELETE FROM Driver WHERE Driver_ID = %s", (driver_id,))
    
    # Handle any database errors
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")#


# end of drivers.py