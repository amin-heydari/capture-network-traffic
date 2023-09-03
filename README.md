# Web Scraping with Selenium and Redis

This Python script is designed to automate web scraping and monitoring of multiple domains using Selenium and Redis. It fetches URLs from a Redis queue, navigates to each URL, records network requests and responses, and reports on the HTTP status codes of these requests.

## Prerequisites

Before running this script, ensure you have the following dependencies installed:

- Python 3.x
- Selenium
- Redis
- Chrome WebDriver (for Selenium)

## Output

The script generates output for each processed domain, including the request ID, request URL, and HTTP status code. Example:

- Request ID: <request_id>
- Request URL: <request_url>
- statusCode: <status_code>
