# Actuate Coding Exercise

## Technologies/Libraries Used

- **FastAPI**: Provides great documentation using SwaggerUI and integration with Pydantic models for type safety and async functionality.
- **Pydantic**: Eases user input validation. Has various data types such as `HttpUrl`, `Datetime`, as well as functionality to create custom data types using field validators.
- **SQLite3**: Easy to use database for prototyping and development purposes.
- **Docker**: Containerization platform to package the application and its dependencies. Easy to run and test

## Project Structure
main.py file as the APIs
database.py creates the database and has other functions for database manipulation
docker

## APIs
### Shorten URL

**Endpoint**: `/shorten`

**Method**: `POST`

**Description**: Takes a long URL and returns a shortened URL.

**Request Body**:
```json
{
    "url": "string"
}
```

**Response**:
```json
{
  "short_url": "string",
  "expiry_date": "string"
}
```

### Redirects to Original URL

**Endpoint**: `/redirect/{shortened_url}`

**Method**: `GET`

**Description**: Redirects to the original long URL based on the shortened URL and updates the click value as well.

**Response**: Redirects to the original URL.

### Get Original URL

**Endpoint**: `/expand/{shortened_url}`

**Method**: `GET`

**Description**: Retrieves details about the URL, such as the original URL, URL Expiry and clicks on the URL. 

**Response**:
```json
{
  "original_url": "https://example.com/",
  "short_url": "string",
  "expiry_date": "string",
  "clicks": 0
}
```

## Instructions to Run

### Using Docker

1. **Build the Docker image**:
    ```docker build --pull --rm -f 'URLShortener\dockerfile' -t 'actuate:latest' 'URLShortener' ```

2. **Run the Docker container**:
    ```docker run --rm -d -p 8000:8000/tcp actuate:latest ```

3. **API Documentation and Testing**:
    You can access the API documentation at `http://localhost:8000/docs`.

    You can alternatively test using Postman as well
