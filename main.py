# main.py
# FastAPI application for New York Police Department Citation system.
"""
Title: New York Police Department API
Version: 0.0.1
Description: API for managing drivers, correction notices, violations, and notice violations in the New York Police Department.
Author: Jake Morgan
Last Modified: 16-02-2026
"""
from fastapi import FastAPI
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import drivers, notices, tokens, vehicles, citations

app = FastAPI(title="New York Police Department API")

# Add CORS middleware BEFORE including routers
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://localhost:5500", 
        "http://localhost:3000",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(drivers.router)
app.include_router(notices.router)
app.include_router(citations.router)
app.include_router(tokens.router)
app.include_router(vehicles.router)

# end of main.py
