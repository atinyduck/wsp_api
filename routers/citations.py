# citations.py
# FastAPI application for New York Police Department Citation system - Citations endpoints.
# This router adapts the "notices" terminology from the database to "citations" for the frontend.
# =========================================================

from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime
import auth
import database.database as database
import models as models
from typing import List

router = APIRouter(prefix="/citations", tags=["Citations"])

# ========================================================
# --- GET ALL CITATIONS ---

@router.get("", response_model=List[dict])
def read_all_citations(
    connection=Depends(database.get_db_connection),
    current_user: str = Depends(auth.verify_token)):
    """ 
    Retrieve all citations (correction notices) from the system.
    
    This endpoint queries the Correction_Notice table and joins with Driver, Officer, 
    and Violation tables to return formatted citation data for officers.
    
    Args:
        connection: Database connection dependency
        current_user: Current authenticated user (badge number)
    
    Returns:
        List[dict]: List of all citations with driver and violation information
    """
    
    # Query to retrieve all citations with related information
    # Uses GROUP_CONCAT to combine multiple violations for a single citation
    query = """
        SELECT 
            cn.Notice_ID as citation_id,
            cn.Notice_ID as citation_number,
            d.License_Number as driver_license,
            d.First_Name,
            d.Last_Name,
            GROUP_CONCAT(nv.Violation_Code) as violation_codes,
            GROUP_CONCAT(v.Violation_Description) as violation_types,
            cn.Violation_Date as date_issued,
            cn.Location as violation_location,
            0 as fine_amount,
            'active' as status,
            o.Badge_Number as issued_by_badge,
            cn.Violation_Time as violation_time
        FROM Correction_Notice cn
        JOIN Driver d ON cn.Driver_ID = d.Driver_ID
        JOIN Officer o ON cn.Officer_ID = o.Officer_ID
        LEFT JOIN Notice_Violation nv ON cn.Notice_ID = nv.Notice_ID
        LEFT JOIN Violation v ON nv.Violation_Code = v.Violation_Code
        GROUP BY cn.Notice_ID
        ORDER BY cn.Violation_Date DESC
    """
    
    try:
        # Execute the query to get all citations
        results = database.execute_query(connection, query, fetch="all")
    except HTTPException:
        # Return empty list if no citations found instead of 404
        return []
    
    # Transform results to match frontend expectations
    citations = []
    for row in results:
        citations.append({
            "citation_id": row['citation_id'],
            "citation_number": f"CIT-{row['citation_number']:06d}",
            "driver_license": row['driver_license'],
            "driver_name": f"{row['First_Name']} {row['Last_Name']}",
            "violation_type": row['violation_types'] or 'Unknown',
            "violation_code": row['violation_codes'],
            "date_issued": row['date_issued'].isoformat(),
            "violation_location": row['violation_location'],
            "fine_amount": row['fine_amount'],
            "status": row['status'],
            "issued_by_badge": row['issued_by_badge']
        })
    
    return citations

# --- End of GET ALL CITATIONS ---
# ========================================================
# --- GET CITATIONS BY DRIVER LICENSE ---

@router.get("/driver/{license_number}", response_model=List[dict])
def read_driver_citations(
    license_number: str,
    connection=Depends(database.get_db_connection),
    current_user: str = Depends(auth.verify_token)):
    """ 
    Retrieve all citations for a specific driver by their license number.
    
    This endpoint allows drivers to view their own citations and officers to 
    look up citations for a specific driver.
    
    Args:
        license_number: Driver's license number (e.g., D1234567)
        connection: Database connection dependency
        current_user: Current authenticated user (badge number or license)
    
    Returns:
        List[dict]: List of citations for the specified driver
    """
    
    # Query to retrieve citations filtered by driver license number
    query = """
        SELECT 
            cn.Notice_ID as citation_id,
            cn.Notice_ID as citation_number,
            d.License_Number as driver_license,
            d.First_Name,
            d.Last_Name,
            GROUP_CONCAT(nv.Violation_Code) as violation_codes,
            GROUP_CONCAT(v.Violation_Description) as violation_types,
            cn.Violation_Date as date_issued,
            cn.Location as violation_location,
            0 as fine_amount,
            'active' as status,
            o.Badge_Number as issued_by_badge,
            cn.Violation_Time as violation_time
        FROM Correction_Notice cn
        JOIN Driver d ON cn.Driver_ID = d.Driver_ID
        JOIN Officer o ON cn.Officer_ID = o.Officer_ID
        LEFT JOIN Notice_Violation nv ON cn.Notice_ID = nv.Notice_ID
        LEFT JOIN Violation v ON nv.Violation_Code = v.Violation_Code
        WHERE d.License_Number = %s
        GROUP BY cn.Notice_ID
        ORDER BY cn.Violation_Date DESC
    """
    
    try:
        # Execute the query with the provided license number
        results = database.execute_query(connection, query, (license_number,), fetch="all")
    except HTTPException:
        # Return empty list if no citations found instead of 404
        return []
    
    # Transform results to match frontend expectations
    citations = []
    for row in results:
        citations.append({
            "citation_id": row['citation_id'],
            "citation_number": f"CIT-{row['citation_number']:06d}",
            "driver_license": row['driver_license'],
            "driver_name": f"{row['First_Name']} {row['Last_Name']}",
            "violation_type": row['violation_types'] or 'Unknown',
            "violation_code": row['violation_codes'],
            "date_issued": row['date_issued'].isoformat(),
            "violation_location": row['violation_location'],
            "fine_amount": row['fine_amount'],
            "status": row['status'],
            "issued_by_badge": row['issued_by_badge']
        })
    
    return citations

# --- End of GET CITATIONS BY DRIVER LICENSE ---
# ========================================================
# --- POST CREATE CITATION ---

@router.post("", status_code=201)
def create_citation(
    citation_data: dict,
    connection=Depends(database.get_db_connection),
    current_user: str = Depends(auth.verify_token)):
    """ 
    Create a new citation (correction notice) in the system.
    
    This endpoint creates a new citation by:
    1. Verifying or creating the driver record
    2. Looking up the officer from the current user
    3. Creating a correction notice
    4. Linking violations to the notice
    
    Args:
        citation_data: Dictionary containing citation details
            - driver_license: Driver's license number
            - driver_name: Driver's full name
            - violation_location: Location where violation occurred
            - violation_type: Type of violation
            - fine_amount: Fine amount for the citation
        connection: Database connection dependency
        current_user: Current authenticated user (badge number)
    
    Returns:
        dict: Newly created citation information
    
    Raises:
        HTTPException: If officer not found or database error occurs
    """
    
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Step 1: Look up or create the driver record
        driver_query = "SELECT Driver_ID FROM Driver WHERE License_Number = %s"
        
        try:
            driver_result = database.execute_query(
                connection, 
                driver_query, 
                (citation_data.get('driver_license'),),
                fetch="one"
            )
            driver_id = driver_result['Driver_ID']
        except HTTPException:
            # Driver does not exist, so create a new driver record
            driver_name = citation_data.get('driver_name', 'Unknown')
            name_parts = driver_name.split()
            first_name = name_parts[0] if len(name_parts) > 0 else 'Unknown'
            last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else 'Unknown'
            
            insert_driver_query = """
                INSERT INTO Driver (First_Name, Last_Name, Address, Birth_Date, License_Number, License_State)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            driver_id = database.execute_insert(
                connection,
                insert_driver_query,
                (first_name, last_name, 'Unknown', '2000-01-01', citation_data.get('driver_license'), 'NY')
            )
        
        # Step 2: Look up the officer from the current user (badge number)
        officer_query = "SELECT Officer_ID FROM Officer WHERE Badge_Number = %s"
        
        try:
            officer_result = database.execute_query(
                connection,
                officer_query,
                (current_user,),
                fetch="one"
            )
            officer_id = officer_result['Officer_ID']
        except HTTPException:
            raise HTTPException(status_code=400, detail="Officer not found in system")
        
        # Step 3: Get a vehicle VIN (use first available or placeholder)
        vehicle_query = "SELECT VIN FROM Vehicle LIMIT 1"
        
        try:
            vehicle_result = database.execute_query(connection, vehicle_query, fetch="one")
            vin = vehicle_result['VIN']
        except HTTPException:
            # No vehicles in database, use placeholder
            vin = "UNKNOWN00000000000"
        
        # Step 4: Create the correction notice
        insert_notice_query = """
            INSERT INTO Correction_Notice (Violation_Date, Violation_Time, Location, Driver_ID, Officer_ID, VIN)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        violation_date = datetime.now().date()
        violation_time = datetime.now().strftime("%H:%M:%S")
        
        notice_id = database.execute_insert(
            connection,
            insert_notice_query,
            (
                violation_date,
                violation_time,
                citation_data.get('violation_location', 'Unknown'),
                driver_id,
                officer_id,
                vin
            )
        )
        
        # Step 5: Link violation to the notice using the bridge table
        violation_type = citation_data.get('violation_type', 'Other')
        
        # Look up the violation code for the given violation type
        violation_query = "SELECT Violation_Code FROM Violation WHERE Violation_Description LIKE %s LIMIT 1"
        
        try:
            violation_result = database.execute_query(
                connection,
                violation_query,
                (f"%{violation_type}%",),
                fetch="one"
            )
            violation_code = violation_result['Violation_Code']
        except HTTPException:
            # Violation type not found, use generic code
            violation_code = 'OTHER'
        
        # Insert into the bridge table (Notice_Violation)
        insert_bridge_query = "INSERT INTO Notice_Violation (Notice_ID, Violation_Code) VALUES (%s, %s)"
        database.execute_insert(connection, insert_bridge_query, (notice_id, violation_code))
        
        # Return the newly created citation
        return {
            "citation_id": notice_id,
            "citation_number": f"CIT-{notice_id:06d}",
            "driver_license": citation_data.get('driver_license'),
            "driver_name": citation_data.get('driver_name'),
            "vehicle_plate": citation_data.get('vehicle_plate', 'Unknown'),
            "violation_type": violation_type,
            "date_issued": violation_date.isoformat(),
            "violation_location": citation_data.get('violation_location'),
            "fine_amount": citation_data.get('fine_amount', 0),
            "status": "active",
            "issued_by_badge": current_user,
            "message": "Citation issued successfully"
        }
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as err:
        # Handle unexpected database errors
        connection.rollback()
        print(f"Error creating citation: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Error creating citation: {str(err)}"
        )
    finally:
        cursor.close()

# --- End of POST CREATE CITATION ---
# ========================================================

# end of citations.py