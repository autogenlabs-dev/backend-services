# System Patterns

## Pattern 1: RESTful API with FastAPI

- **Description:** The backend is structured as a RESTful API using the FastAPI framework.
- **Use Cases:** This pattern is used to expose the application's functionality to clients, such as the VS Code extension, through a set of HTTP endpoints.
- **Implementation:** The `minimal_auth_server.py` file defines the API endpoints using FastAPI decorators (`@app.get`, `@app.post`, etc.).

## Pattern 2: Object-Document Mapper (ODM) with Beanie

- **Description:** The application uses Beanie as an ODM to interact with the MongoDB database.
- **Use Cases:** This pattern simplifies database operations by allowing developers to work with Python objects instead of raw MongoDB queries.
- **Implementation:** The `app/models` directory contains the Beanie models that map to the MongoDB collections.