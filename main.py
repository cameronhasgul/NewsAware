from fastapi import FastAPI

# Initialize the FastAPI application instance
app = FastAPI(title="NewsAware API")

# Define a root GET endpoint
@app.get("/")
def read_root():
    return {
        "status": "online",
        "app": "NewsAware Backend",
        "message": "Welcome to the NewsAware API!"
    }