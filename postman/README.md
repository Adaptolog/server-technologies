# Postman Collection for Expense Tracker API

This directory contains Postman collections and environments for testing the Expense Tracker API.

## Files

1. `expense-tracker-api.postman_collection.json` - Main collection with all API endpoints
2. `environments/local.postman_environment.json` - Environment for local development
3. `environments/production.postman_environment.json` - Environment for production

## How to Use

1. Import the collection into Postman:
   - Open Postman
   - Click "Import"
   - Select the `expense-tracker-api.postman_collection.json` file

2. Import environments:
   - Click "Import" for each environment file
   - Or create environments manually with the variables:
     - `base_url`: Base URL of the API (http://localhost:5000 for local, your Render URL for production)
     - `user_id`: Will be automatically set when creating users
     - `category_id`: Will be automatically set when creating categories
     - `record_id`: Will be automatically set when creating records

3. Run the "Complete Flow" folder to test the full workflow

## Complete Flow

The collection includes a "Complete Flow" folder that demonstrates the full API workflow:
1. Health check
2. Create a user
3. Create a category
4. Create an expense record
5. Get user's records
6. Clean up (delete record)

Variables are automatically passed between requests using Postman tests.