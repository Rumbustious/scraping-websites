from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from scraper import JarirScraper, AmazonScraper
import uvicorn

app = FastAPI()

# Allow CORS from React development server and Vercel deployment
origins = [
    "http://localhost:3000",
    "https://scrape-project-freelance.vercel.app/"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/search")
def search_products(q: str = Query(..., min_length=1)):
    jarir_scraper = JarirScraper("Jarir")
    amazon_scraper = AmazonScraper("Amazon")
    try:
        products = list(jarir_scraper.scrape_products(q, max_scrolls=3))
        products += list(amazon_scraper.scrape_products(q, max_pages=1))
        return {"products": products}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        jarir_scraper.quit_driver()
        amazon_scraper.quit_driver()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)