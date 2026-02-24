# main.py
# FastAPI application for Washington State Patrol system.
"""
Title: Washington State Patrol API
Version: 0.0.1
Description: API for managing drivers, correction notices, violations, and notice violations in the Washington State Patrol system.
Author: Jake Morgan
Last Modified: 16-02-2026
"""
from fastapi import FastAPI
from routers import drivers, notices, tokens, vehicles

app = FastAPI(title="Washington Sate Patrol API")

app.include_router(drivers.router)
app.include_router(notices.router)
app.include_router(tokens.router)
app.include_router(vehicles.router)

# end of main.py