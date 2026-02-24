# tokens.py
# FastAPI application for Washington State Patrol system - Token endpoints.
# =========================================================

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
import auth, database.database as database, models

router = APIRouter(prefix="/token", tags=["Authentication Tokens"])

@router.post("", response_model=models.Token, status_code=201)
def login(form_data: OAuth2PasswordRequestForm = Depends(), 
          connection=Depends(database.get_db_connection)):
    """ Login endpoint for the Washington State Patrol system. """
    
    query = "SELECT * FROM Officer WHERE Badge_Number = %s"
    
    try:
        # Attempt to fetch the user
        user = database.execute_query(connection, query, (form_data.username,), fetch="one")
    except HTTPException as e:
        # If the helper raised a 404, we turn it into a 401 for security
        if e.status_code == 404:
            raise HTTPException(status_code=401, detail="Incorrect username or password")
        raise e

    # Check the password 
    if not auth.verify_password(form_data.password, user['Secret_Hash']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token = auth.create_access_token(data={"sub": str(user['Badge_Number'])})
    return {"access_token": access_token, "token_type": "bearer"}

@router.put("", response_model=models.Token)
def refresh_token(current_user: str = Depends(auth.verify_token)):
    """ Refresh access token endpoint for the Washington State Patrol system. """
    
    # Issue a new access token for the current user
    access_token = auth.create_access_token(data={"sub": current_user})
    return {"access_token": access_token, "token_type": "bearer"}

@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def logout(current_user: str = Depends(auth.verify_token)):
    """ Logout endpoint for the Washington State Patrol system. """
    return

# end of tokens.py
