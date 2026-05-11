# vehicles.py
# FastAPI application for New York Police Department Citation system - Vehicle endpoints.
# =========================================================

from fastapi import APIRouter, Depends, HTTPException
import auth
import database.database as database, models as models
from typing import List

router = APIRouter(prefix="/vehicles", tags=["Vehicles"])

@router.get("/", response_model=List[models.VehicleResponse])
def read_all_vehicles(
    connection=Depends(database.get_db_connection),
    current_user: str=Depends(auth.verify_token)):
    """ Retrieve a list of all vehicles. """
    
    query = "SELECT * FROM Vehicle"
    
    return database.execute_query(connection, query)

@router.get("/{vin}", response_model=models.VehicleResponse)
def read_vehicle(
    vin: str, 
    connection=Depends(database.get_db_connection),
    current_user: str=Depends(auth.verify_token)):
    """ Retrieve a vehicle by its VIN. """
    
    query = "SELECT * FROM Vehicle WHERE VIN = %s"
    
    return database.execute_query(connection, query, (vin,), fetch="one")

@router.post("/", response_model=models.VehicleResponse, status_code=201)
def create_vehicle(
    vehicle: models.VehicleCreate, 
    connection=Depends(database.get_db_connection),
    current_user: str=Depends(auth.verify_token)):
    """ Create a new vehicle record. """
    
    try:
        # Check if vehicle with this VIN already exists
        existing = database.execute_query(
            connection, 
            "SELECT * FROM Vehicle WHERE VIN = %s", 
            (vehicle.VIN,), 
            fetch="one"
        )
        if existing:
            raise HTTPException(
                status_code=400, 
                detail="A vehicle with this VIN already exists"
            )
    except HTTPException as e:
        if e.status_code == 400:
            raise e
        # If 404 (not found), that's good - continue
        pass
    
    try:
        # Create the new vehicle
        database.execute_insert(
            connection,
            "INSERT INTO Vehicle (VIN, Make, Model, Color, License_Plate, License_State) VALUES (%s, %s, %s, %s, %s, %s)",
            (vehicle.VIN, vehicle.Make, vehicle.Model, vehicle.Color, vehicle.License_Plate, vehicle.License_State)
        )
        
        # Retrieve and return the newly created vehicle
        return database.execute_query(connection, "SELECT * FROM Vehicle WHERE VIN = %s", (vehicle.VIN,), fetch="one")
    
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")

@router.post("/register", response_model=models.VehicleResponse, status_code=201)
def register_vehicle(
    vehicle: models.VehicleCreate, 
    connection=Depends(database.get_db_connection)):
    """ Register a new vehicle without authentication. """
    
    try:
        # Check if vehicle with this VIN already exists
        existing = database.execute_query(
            connection, 
            "SELECT * FROM Vehicle WHERE VIN = %s", 
            (vehicle.VIN,), 
            fetch="one"
        )
        if existing:
            raise HTTPException(
                status_code=400, 
                detail="A vehicle with this VIN already exists"
            )
    except HTTPException as e:
        if e.status_code == 400:
            raise e
        # If 404 (not found), that's good - continue
        pass
    
    try:
        # Create the new vehicle
        database.execute_insert(
            connection,
            "INSERT INTO Vehicle (VIN, Make, Model, Color, License_Plate, License_State) VALUES (%s, %s, %s, %s, %s, %s)",
            (vehicle.VIN, vehicle.Make, vehicle.Model, vehicle.Color, vehicle.License_Plate, vehicle.License_State)
        )
        
        # Retrieve and return the newly created vehicle
        return database.execute_query(connection, "SELECT * FROM Vehicle WHERE VIN = %s", (vehicle.VIN,), fetch="one")
    
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")

@router.put("/{vin}", status_code=204)
def update_vehicle(
    vin: str,
    vehicle: models.VehicleCreate,
    connection=Depends(database.get_db_connection),
    current_user: str=Depends(auth.verify_token)):
    """ Update a vehicle record. """
    
    # Check if the vehicle exists
    database.execute_query(connection, "SELECT * FROM Vehicle WHERE VIN = %s", (vin,), fetch="one")
    
    try:
        # Update the vehicle
        database.execute_insert(
            connection,
            "UPDATE Vehicle SET Make = %s, Model = %s, Color = %s, License_Plate = %s, License_State = %s WHERE VIN = %s",
            (vehicle.Make, vehicle.Model, vehicle.Color, vehicle.License_Plate, vehicle.License_State, vin)
        )
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")

@router.delete("/{vin}", status_code=204)
def delete_vehicle(
    vin: str, 
    connection=Depends(database.get_db_connection),
    current_user: str=Depends(auth.verify_token)):
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM Vehicle WHERE VIN = %s", (vin,))
        connection.commit()
    except Exception as err:
        connection.rollback()
        # Check for the specific Foreign Key restrict error
        if "1451" in str(err):
            raise HTTPException(
                status_code=400, 
                detail="Cannot delete vehicle: It has active correction notices associated with it. Delete the notices first."
            )
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        cursor.close()

# end of vehicles.py