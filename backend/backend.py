from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import json
from scraper import JarirScraper, AmazonScraper, NoonScraper, ExtraScraper, CarrefourScraper
import uvicorn
import heapq

app = FastAPI()

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

def generate_search_results(search_query):
    """Generator function that yields products as they're scraped"""
    scrapers = [
        (JarirScraper("Jarir"), "scrape_products", {"max_scrolls": 1}),
        (AmazonScraper("Amazon"), "scrape_products", {"max_pages": 1}),
        (NoonScraper("Noon"), "scrape_products", {"max_pages": 1}),
        (ExtraScraper("Extra"), "scrape_products", {"max_pages": 1}),
        (CarrefourScraper("Carrefour"), "scrape_products", {"max_pages": 1})  # Add CarrefourScraper
    ]

    results = []
    for scraper, method_name, kwargs in scrapers:
        try:
            scraper_instance = scraper
            method = getattr(scraper_instance, method_name)
            # Collect products from the scraper
            for product in method(search_query, **kwargs):
                results.append(product)
        except Exception as e:
            results.append({
                "error": f"Error scraping {scraper_instance.store_name}: {str(e)}"
            })
        finally:
            scraper_instance.quit_driver()

    # Sort results based on a criteria (e.g., rating, price)
    results.sort(key=lambda x: (x.get('rating', 0), x.get('price', float('inf'))), reverse=True)

    # Interleave results from all stores
    jarir_results = [r for r in results if r.get('store') == 'Jarir']
    amazon_results = [r for r in results if r.get('store') == 'Amazon']
    noon_results = [r for r in results if r.get('store') == 'Noon']
    extra_results = [r for r in results if r.get('store') == 'Extra']
    carrefour_results = [r for r in results if r.get('store') == 'Carrefour']
    interleaved_results = []

    while jarir_results or amazon_results or noon_results or extra_results or carrefour_results:
        if jarir_results:
            interleaved_results.append(jarir_results.pop(0))
        if amazon_results:
            interleaved_results.append(amazon_results.pop(0))
        if noon_results:
            interleaved_results.append(noon_results.pop(0))
        if extra_results:
            interleaved_results.append(extra_results.pop(0))
        if carrefour_results:
            interleaved_results.append(carrefour_results.pop(0))

    for product in interleaved_results:
        yield json.dumps(product) + "\n"

@app.get("/api/search")
def search_products(q: str = Query(..., min_length=1)):
    try:
        return StreamingResponse(
            generate_search_results(q),
            media_type="application/x-ndjson"  # Newline-delimited JSON
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)