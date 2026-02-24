# vehicles.py
# FastAPI application for Washington State Patrol system - Vehicle endpoints.
# =========================================================

from fastapi import APIRouter, Depends, HTTPException
import auth
import database.database as database, models as models

router = APIRouter(prefix="/vehicles", tags=["Vehicles"])

@router.delete("/{vin}", status_code=204)
def delete_vehicle(vin: str, connection=Depends(database.get_db_connection)):
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