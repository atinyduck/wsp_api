# notices.py
# FastAPI application for Washington State Patrol system - Notice endpoints.
# =========================================================

from fastapi import APIRouter, Depends, HTTPException
import auth
import database.database as database, models as models
from typing import List

router = APIRouter(prefix="/notices", tags=["Correction Notices"])

@router.get("/officer/{badge_number}", response_model=List[models.CorrectionNoticeResponse])
def read_notices_by_officer(
    badge_number: int, 
    connection=Depends(database.get_db_connection),
    current_user: str=Depends(auth.verify_token)):
    """ Retrieve all correction notices with their violations for an officer. """ 
    
    # GROUP_CONCAT to get all violations as a single comma-separated string
    query = """
        SELECT cn.*, GROUP_CONCAT(nv.Violation_Code) as Violations
        FROM Correction_Notice cn
        JOIN Officer o ON cn.Officer_ID = o.Officer_ID
        LEFT JOIN Notice_Violation nv ON cn.Notice_ID = nv.Notice_ID
        WHERE o.Badge_Number = %s
        GROUP BY cn.Notice_ID
    """
    
    results = database.execute_query(connection, query, (badge_number,))
    
    # Transform the 'Violations' string back into a real Python List
    for row in results:
        if row['Violations']:
            row['Violations'] = row['Violations'].split(',')
        else:
            row['Violations'] = [] # Handle cases with no violations
            
    return results

@router.post("/", response_model=models.CorrectionNoticeResponse, status_code=201)
def create_correction_notice(
    notice: models.CorrectionNoticeCreate, 
    connection=Depends(database.get_db_connection),
    current_user: str=Depends(auth.verify_token)):
    """ Create a new correction notice using database helpers and transactions. """
    
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Insert the main notice
        insert_notice_query = """
            INSERT INTO Correction_Notice (Violation_Date, Violation_Time, Location, Driver_ID, Officer_ID, VIN)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_notice_query, (
            notice.Violation_Date, notice.Violation_Time, notice.Location, 
            notice.Driver_ID, notice.Officer_ID, notice.VIN
        ))
        notice_id = cursor.lastrowid
        
        # Insert into the Bridge Table for each violation
        insert_bridge_query = "INSERT INTO Notice_Violation (Notice_ID, Violation_Code) VALUES (%s, %s)"
        for violation in notice.Violations:
            cursor.execute(insert_bridge_query, (notice_id, violation))
            
        # COMMIT both actions together
        connection.commit()
        
        # Use your execute_query HELPER to fetch the final result
        fetch_query = """
            SELECT cn.*, GROUP_CONCAT(nv.Violation_Code) as Violations
            FROM Correction_Notice cn
            LEFT JOIN Notice_Violation nv ON cn.Notice_ID = nv.Notice_ID
            WHERE cn.Notice_ID = %s
            GROUP BY cn.Notice_ID
        """ 
        result = database.execute_query(connection, fetch_query, (notice_id,), fetch="one")
        
        # Convert the comma-separated string from GROUP_CONCAT into a Python List
        if result['Violations']:
            result['Violations'] = result['Violations'].split(',')
        else:
            result['Violations'] = []

        return result
    
    except Exception as err:
        # If anything fails (like a bad Driver_ID), undo everything
        connection.rollback()
        if "1452" in str(err):
            raise HTTPException(status_code=400, detail="Invalid Driver_ID, Officer_ID, or VIN.")
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        cursor.close() 

@router.put("/{notice_id}", status_code=204)
def update_correction_notice(
    notice_id: int,
    notice: models.CorrectionNoticeCreate,
    connection=Depends(database.get_db_connection),
    current_user: str=Depends(auth.verify_token)):
    """ Update an existing correction notice. """
    
    database.execute_query(connection, "SELECT * FROM Correction_Notice WHERE Notice_ID = %s", (notice_id,), fetch="one")
    
    cursor = connection.cursor()
    try: 
        # Update main record
        update_notice_query = """
            UPDATE Correction_Notice
            SET Violation_Date = %s, Violation_Time = %s, Location = %s, Driver_ID = %s, Officer_ID = %s, VIN = %s
            WHERE Notice_ID = %s
        """
        
        cursor.execute(
            update_notice_query, 
            (notice.Violation_Date, notice.Violation_Time, notice.Location, 
             notice.Driver_ID, notice.Officer_ID, notice.VIN, notice_id
             )
            )    
        
        # Sync the violations
        cursor.execute("DELETE FROM Notice_Violation WHERE Notice_ID = %s", (notice_id,))
        
        insert_bridge = "INSERT INTO Notice_Violation (Notice_ID, Violation_Code) VALUES (%s, %s)"
        for violation in notice.Violations:
            cursor.execute(insert_bridge, (notice_id, violation))
            
        connection.commit()
    except Exception as err:
        connection.rollback()
        # Catch Foreign Key failures (e.g., Driver_ID 0)
        if "1452" in str(err):
            raise HTTPException(
                status_code=400, 
                detail="Constraint Error: Ensure the Driver_ID, Officer_ID, and VIN exist in the system."
            )
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        cursor.close()
    
    
    
# end of notices.py