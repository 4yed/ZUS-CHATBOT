# Error Handling and Security

This file explains how the chatbot handles errors and stays secure.

## 1. API Errors

### a. Missing Info

- **Problem:** A request is missing a required field (like the `query`).
- **Solution:** The API automatically returns a `422` error, which tells the client exactly what field is missing.

### b. API is Down

- **Problem:** The API server is not running or crashes.
- **Solution:** The chatbot is built to catch connection errors. If it can't reach the API, it will tell the user that the service is down instead of crashing.

## 2. Security

### a. SQL Injection

- **Problem:** A user tries to inject malicious SQL code.
- **Solution:** We don't use a fancy AI to turn user text into SQL. Instead, we have a simple, rule-based system that only looks for safe keywords (like "parking" or "wifi"). Malicious code like `DROP TABLE` is ignored, so the database is safe.

### b. Product Search

- **Problem:** A user provides a weird or malicious query for products.
- **Solution:** The product search uses a vector store (FAISS). This system isn't vulnerable to injection attacks because it treats the user's input as a math vector, not a command.
