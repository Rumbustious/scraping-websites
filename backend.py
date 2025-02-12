# Language: Python
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from scraper import JarirScraper  # [jarir_scraper.py](jarir_scraper.py)
import uvicorn

app = FastAPI()

# Allow CORS from React development server
origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/search")
def search_products(q: str = Query(..., min_length=1)):
    scraper = JarirScraper("Jarir")
    try:
        products = list(scraper.scrape_products(q, max_scrolls=3))
        return {"products": products}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        scraper.quit_driver()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)