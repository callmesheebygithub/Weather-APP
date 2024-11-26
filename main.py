from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import os
import httpx

# Load environment variables
load_dotenv()

app = FastAPI()

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

API_HOST = os.getenv("API_HOST")
API_KEY = os.getenv("API_KEY")

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "weather": None})

@app.post("/get-weather", response_class=HTMLResponse)
async def get_weather(request: Request, city: str = Form(...), country: str = Form(...)):
    url = f"https://{API_HOST}/city/{city}/{country}"
    headers = {
        "x-rapidapi-host": API_HOST,
        "x-rapidapi-key": API_KEY,
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        weather = {
            "city": data.get("name", "Unknown"),
            "temp": data.get("main", {}).get("temp", "N/A"),
            "desc": data.get("weather", [{}])[0].get("description", "N/A"),
            "humidity": data.get("main", {}).get("humidity", "N/A"),
        }
    else:
        weather = {"error": "Unable to fetch weather data. Check your inputs."}

    return templates.TemplateResponse("index.html", {"request": request, "weather": weather})
