"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from pathlib import Path
from pymongo import MongoClient
from typing import Dict, Any

# Initialize FastAPI app
app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Add cache control headers
@app.middleware("http")
async def add_cache_control_header(request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# Initialize MongoDB connection
client = None
db = None
activities_collection = None

@app.on_event("startup")
async def startup_db_client():
    global client, db, activities_collection
    try:
        print("Connecting to MongoDB...")
        client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
        # Force a connection to verify it works
        client.admin.command('ping')
        print("Successfully connected to MongoDB")
        
        db = client['mergington_high']
        activities_collection = db['activities']
        
        # Initialize database with data if empty
        count = activities_collection.count_documents({})
        print(f"Found {count} existing activities")
        
        if count == 0:
            print("Initializing database with initial activities...")
            for name, activity in initial_activities.items():
                activities_collection.insert_one({"name": name, **activity})
            print(f"Initialized database with {len(initial_activities)} activities")
    except Exception as e:
        print(f"Failed to initialize MongoDB: {str(e)}")
        raise

# Mount the static files directory
current_dir = Path(__file__).parent
static_path = os.path.join(current_dir, "static")
print(f"Mounting static files from: {static_path}")
app.mount("/static", StaticFiles(directory=static_path, html=True), name="static")

# Initial activities data
initial_activities = {
    "Soccer Team": {
        "description": "Join the school soccer team and compete in local leagues",
        "schedule": "Wednesdays and Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 18,
        "participants": ["lucas@mergington.edu", "mia@mergington.edu"]
    },
    "Basketball Club": {
        "description": "Practice basketball skills and play friendly matches",
        "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
        "max_participants": 15,
        "participants": ["liam@mergington.edu", "ava@mergington.edu"]
    },
    "Drama Club": {
        "description": "Participate in theater productions and acting workshops",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "noah@mergington.edu"]
    },
    "Art Workshop": {
        "description": "Explore painting, drawing, and other visual arts",
        "schedule": "Mondays, 3:30 PM - 5:00 PM",
        "max_participants": 16,
        "participants": ["grace@mergington.edu", "jack@mergington.edu"]
    },
    "Math Olympiad": {
        "description": "Prepare for math competitions and solve challenging problems",
        "schedule": "Fridays, 2:00 PM - 3:30 PM",
        "max_participants": 10,
        "participants": ["william@mergington.edu", "amelia@mergington.edu"]
    },
    "Science Club": {
        "description": "Conduct experiments and explore scientific concepts",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 14,
        "participants": ["charlotte@mergington.edu", "benjamin@mergington.edu"]
    },
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    }
}

@app.get("/")
def root():
    return FileResponse(os.path.join(current_dir, "static", "index.html"))


@app.get("/activities")
def get_activities():
    try:
        print("\n=== Fetching Activities ===")
        print("Request received for activities")
        
        if activities_collection is None:
            print("Error: activities_collection is None")
            raise HTTPException(status_code=500, detail="Database not initialized")
            
        print("Database connection verified")
        activities_dict = {}
        
        try:
            # Test MongoDB connection
            client.admin.command('ping')
            print("MongoDB connection test successful")
            
            # Count documents
            count = activities_collection.count_documents({})
            print(f"Found {count} documents in collection")
            
            # Fetch all activities
            cursor = activities_collection.find()
            for activity in cursor:
                name = activity.pop('name')
                activity.pop('_id')  # Remove MongoDB _id field
                activities_dict[name] = activity
                print(f"Processed activity: {name}")
            
            print(f"Successfully processed {len(activities_dict)} activities")
            return activities_dict
            
        except Exception as db_error:
            error_msg = f"Database operation error: {str(db_error)}"
            print(error_msg)
            print(f"Error type: {type(db_error)}")
            raise HTTPException(status_code=500, detail=error_msg)
            
    except Exception as e:
        error_msg = f"Error fetching activities: {str(e)}"
        print(error_msg)
        print(f"Error type: {type(e)}")
        raise HTTPException(status_code=500, detail=error_msg)


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    activity = activities_collection.find_one({"name": activity_name})
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(status_code=400, detail="Already signed up for this activity")

    # Check if activity is full
    if len(activity["participants"]) >= activity["max_participants"]:
        raise HTTPException(status_code=400, detail="Activity is full")

    # Add student to the activity
    result = activities_collection.update_one(
        {"name": activity_name},
        {"$push": {"participants": email}}
    )
    
    if result.modified_count == 1:
        return {"message": f"Signed up {email} for {activity_name}"}
    else:
        raise HTTPException(status_code=500, detail="Failed to sign up for activity")
