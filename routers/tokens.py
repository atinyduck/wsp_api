# tokens.py
# FastAPI application for New York Police Department Citation system - Token endpoints.
# =========================================================

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
import auth, database.database as database, models

router = APIRouter(prefix="/token", tags=["Authentication Tokens"])

@router.post("", response_model=models.Token, status_code=201)
def login(form_data: OAuth2PasswordRequestForm = Depends(), 
          connection=Depends(database.get_db_connection)):
    """ 
    Login endpoint for the NYPD Citation system.
    
    This endpoint authenticates both drivers and officers. It attempts to find
    the user in the Officer table first, then falls back to the Driver table.
    The response includes the user type for the frontend to redirect appropriately.
    
    Args:
        form_data: OAuth2PasswordRequestForm with username and password
        connection: Database connection dependency
    
    Returns:
        dict: Access token and token type
    
    Raises:
        HTTPException: If credentials are invalid (401)
    """
    
    user = None
    user_type = None
    
    # Step 1: Try to authenticate as an Officer (Badge Number)
    officer_query = "SELECT * FROM Officer WHERE Badge_Number = %s"
    
    try:
        user = database.execute_query(connection, officer_query, (form_data.username,), fetch="one")
        user_type = "officer"
    except HTTPException:
        # Officer not found, try driver
        user = None
    
    # Step 2: If not an officer, try to authenticate as a Driver (License Number)
    if user is None:
        driver_query = "SELECT * FROM Driver WHERE License_Number = %s"
        
        try:
            user = database.execute_query(connection, driver_query, (form_data.username,), fetch="one")
            user_type = "driver"
        except HTTPException:
            # Driver not found either
            user = None
    
    # Step 3: If no user found, return 401
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Step 4: Verify password based on user type
    password_field = 'Secret_Hash' if user_type == 'officer' else 'Password'
    
    if password_field not in user or not auth.verify_password(form_data.password, user.get(password_field, '')):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Step 5: Create access token with user type and ID
    user_id = user.get('Badge_Number') if user_type == 'officer' else user.get('License_Number')
    
    access_token = auth.create_access_token(
        data={
            "sub": str(user_id),
            "user_type": user_type
        }
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.put("", response_model=models.Token)
def refresh_token(current_user: str = Depends(auth.verify_token)):
    """ 
    Refresh access token endpoint for the NYPD Citation system.
    
    Allows authenticated users to get a fresh access token.
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        dict: New access token and token type
    """
    
    # Issue a new access token for the current user
    access_token = auth.create_access_token(data={"sub": current_user})
    return {"access_token": access_token, "token_type": "bearer"}

@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def logout(current_user: str = Depends(auth.verify_token)):
    """ 
    Logout endpoint for the NYPD Citation system.
    
    Invalidates the current session by having the frontend remove the token.
    
    Args:
        current_user: Current authenticated user
    """
    return

# end of tokens.py