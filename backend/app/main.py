from fastapi import FastAPI, HTTPException, status

app = FastAPI(title="DALIA", version="0.1.0")


@app.get("/health", status_code=status.HTTP_200_OK)
def get_health():
    return {
        "status":"healthy",
        "current":"App is running" 
    }