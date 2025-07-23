from fastapi import HTTPException
from bs4 import BeautifulSoup
import requests
from urllib.error import HTTPError
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import logging

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)

URL = "https://shop.zuscoffee.com/collections/drinkware"

RETRY_STRATEGY = Retry(
    total=3,
    allowed_methods=["GET"],
)

def get_product_names_all():
    try:
        page = requests.get(url=URL)
        page.raise_for_status()
    except requests.exceptions.RequestException as e:
        LOG.error(f"Request failed: {e}")
        raise HTTPException(status_code=404, detail="Failed to retrieve page.")

    if page.content is None:
        LOG.error("page content was found empty")
        return    
    
    soup = BeautifulSoup(page.content, "html.parser")

    product_span = soup.find_all("span", class_="product-card__title")
    all_product_titles = [product_titles.text for product_titles in product_span]

    LOG.info("sucessfully retrieved all products")

    return all_product_titles 