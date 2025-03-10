# main.py
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import logging
from pydantic import BaseModel, HttpUrl, field_validator
from database import (
    get_url_by_short_url,
    get_url_by_original_url,
    insert_url,
    update_clicks,
)
import uuid
import socket
from datetime import datetime, timedelta

# Create a FastAPI instance
app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO,
                 format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                 datefmt="%Y-%m-%d %H:%M:%S",
                 filename="app.log",
                 filemode="a")

logger = logging.getLogger(__name__)

# Constants for expiry days
DEFAULT_EXPIRY_DAYS = 365
MIN_EXPIRY_DAYS = 1
MAX_EXPIRY_DAYS = 1825  # 5 years in days
BASE_DOMAIN = "myurlshortener.live/"

# Enable CORS (Cross-Origin Resource Sharing) to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


"""
URLRequest: Request model for the /shorten API
route to accept the original URL and optional expiry period.
original_url: str (required)
expiry_days: int default=365 (optional)
"""
class URLRequest(BaseModel):
    original_url: HttpUrl
    expiry_days: int = Query(
        default=DEFAULT_EXPIRY_DAYS,
        ge=MIN_EXPIRY_DAYS,
        le=MAX_EXPIRY_DAYS,
        description=f"Optional expiry period in days (min: {MIN_EXPIRY_DAYS}, max: {MAX_EXPIRY_DAYS})",
        example=365,
    )


"""
ShortURLResponse: Response model for the /shorten API
route to return the shortened URL.
original_url: HttpUrl
short_url: str 
expiry_date: str | None
"""
class ShortURLResponse(BaseModel):
    short_url: str
    expiry_date: str | None = None

"""
OriginalURLResponse: Response model for the /expand API 
route to return the original URL.
"""
class OriginalURLResponse(BaseModel):
    original_url: HttpUrl
    short_url: str
    expiry_date: str | None = None
    clicks: int = 0

"""
dns_lookup: Perform a DNS lookup on the URL to ensure it is valid.
params: url: str
returns: bool (True if the URL is valid, False otherwise)
"""
def dns_lookup(url: str) -> bool:
    try:
        hostname = url.split("//")[-1].split("/")[0]
        socket.gethostbyname(hostname)
        return True
    except socket.gaierror:
        logger.error(f"DNS lookup failed for URL: {url}")
        return False


# Define the API routes

"""
POST /shorten: Shorten a URL
Request Body: URLRequest
Response Body: URLResponse
"""
@app.post(
    "/shorten",
    response_model=ShortURLResponse,
    tags=["URL Shortening"],
    summary="Shorten a URL",
    description="Provide any URL and return a valid shortened URL",
)
async def shorten_url(request: URLRequest):
    original_url = request.original_url

    # Perform DNS lookup
    if not dns_lookup(str(original_url)):
        raise HTTPException(
            status_code=400, detail="Invalid URL: DNS lookup failed"
        )

    # Validate the original URL
    if BASE_DOMAIN in original_url.host:
        raise HTTPException(
            status_code=400,
            detail="Invalid URL: Cannot shorten a URL from the same domain",
        )

    original_url = str(original_url)
    url = get_url_by_original_url(original_url)
    if url:
        raise HTTPException(
            status_code=400,
            detail="URL already shortened. Here is the shortened URL: "
            + url["short_url"],
        )

    short_url = BASE_DOMAIN + str(uuid.uuid4())[:9]

    creation_date = datetime.now()
    expiry_date = (
        creation_date + timedelta(days=request.expiry_days)
        if request.expiry_days
        else 0
    )
    expiry_date = expiry_date.strftime("%Y-%m-%d")
    insert_url(original_url, short_url, expiry_date)
    return ShortURLResponse(
        short_url=short_url, expiry_date=expiry_date
    )


@app.get("/expand", response_model=OriginalURLResponse)
async def expand_url(
    short_url: str = Query(
        ...,
        max_length=29,
        min_length=29,
        regex=r"^myurlshortener\.live/",
        example=f"{BASE_DOMAIN}123456789"
    )
):

    url = get_url_by_short_url(short_url)

    if not url:
        logger.error(f"Matching original URL not found for given input: {short_url}")
        raise HTTPException(status_code=404, detail="URL not found")
    if url["expiry_date"] < datetime.now().strftime("%Y-%m-%d"):
        logger.error(f"Resource requested has expired: {short_url}")
        raise HTTPException(
            status_code=410,
            detail="This URL has expired and is no longer available."
            " Please create a new shortened URL.",
        )

    return OriginalURLResponse(
        original_url=url["original_url"],
        short_url=url["short_url"],
        clicks=url["clicks"],
        expiry_date=url["expiry_date"],
    )


@app.get("/redirect")
async def redirect_url(
    short_url: str = Query(
        ...,
        max_length=29,
        min_length=29,
        regex=r"^myurlshortener\.live/",
        example="myurlshortener.live/123456789",
    )
):
    url = get_url_by_short_url(short_url)
    if not url:
        logger.error(f"Matching original URL not found for given"
                     " input: {short_url}. Redirect failed.")
        raise HTTPException(status_code=404, detail="URL not found")
    original_url = url["original_url"]
    
    # Updated the clicks on every redirection to the original URL
    update_clicks(short_url)
    return RedirectResponse(url=original_url)
