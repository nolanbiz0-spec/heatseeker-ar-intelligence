from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Heatseeker A&R Intelligence")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "operational", "message": "Heatseeker A&R Intelligence API"}

@app.get("/health") 
async def health():
    return {"status": "healthy"}
