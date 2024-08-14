# Hockey Statistics RAG System Documentation

Certainly! Here is the updated Table of Contents with the new sections included:

## Table of Contents

# Hockey Statistics RAG System Documentation

## Table of Contents

1. [Project Overview](#project-overview)
2. [Project Structure](#project-structure)
3. [Database Setup](#database-setup)
    - [Prerequisites](#prerequisites)
    - [Database Reconstruction](#database-reconstruction)
    - [Updating Database Configuration](#updating-database-configuration)
    - [Note](#note)
    - [Connecting to DB locally](#connecting-to-db-locally)
4. [Backend](#backend)
    - [Key Files](#backend-key-files)
5. [Deployment Instructions](#deployment-instructions)
    - [Local Development](#local-development)
        - [Prerequisites](#local-development-prerequisites)
        - [Backend Setup](#backend-setup)
        - [Frontend Setup](#frontend-setup)
    - [Cloud Deployment (Heroku)](#cloud-deployment-heroku)
        - [Prerequisites](#cloud-deployment-prerequisites)
        - [Backend Deployment](#backend-deployment)
        - [Frontend Deployment](#frontend-deployment)
        - [Connecting Frontend and Backend](#connecting-frontend-and-backend)
    - [Switching Between Environments](#switching-between-environments)
6. [app.py - Flask Server for Hockey Statistics RAG System](#apppy---flask-server-for-hockey-statistics-rag-system)
    - [Overview](#overview)
    - [Key Components](#key-components)
    - [Dependencies](#dependencies)
    - [Environment Setup](#environment-setup)
    - [Routes](#routes)
    - [Usage](#usage)
    - [Development and Debugging](#development-and-debugging)
    - [Note on Frontend Integration](#note-on-frontend-integration)
7. [Overview of rag_OpenAI.py](#overview-of-rag_openaIpy)
    - [How It Works](#how-it-works)
    - [Key Components](#key-components-1)
    - [Main Function](#main-function)
    - [Usage](#usage-1)
8. [Additional Notes](#additional-notes)

## Project Overview

The Hockey Statistics Retrieval-Augmented Generation (RAG) system is a full-stack application designed to provide an interface for querying and displaying hockey statistics using advanced natural language processing techniques. The backend is built with Python and Flask, while the frontend is developed using React.

## Project Structure

```
hockey_RAG/
├── backend/
│   ├── __pycache__/
│   ├── app.py
│   ├── lookup_table.py
│   ├── rag_llama3.py
│   ├── rag_openAI.py
│   └── simplified_hockey_stats_schema.py
├── database/
│   └── hockey_stats.sql
├── frontend/
│   ├── build/
│   │   ├── static/
│   │   ├── asset-manifest.json
│   │   ├── favicon.ico
│   │   ├── index.html
│   │   ├── logo192.png
│   │   ├── logo512.png
│   │   ├── manifest.json
│   │   └── robots.txt
│   ├── node_modules/
│   ├── public/
│   │   ├── favicon.ico
│   │   ├── index.html
│   │   ├── logo192.png
│   │   ├── logo512.png
│   │   ├── manifest.json
│   │   └── robots.txt
│   ├── src/
│   │   ├── assets/
│   │   │   ├── hockey_background.jpg
│   │   │   └── hockeyAI.png
│   │   ├── components/
│   │   │   ├── ChatContainer.js
│   │   │   ├── Header.js
│   │   │   ├── QueryInput.js
│   │   │   └── api.js
│   │   ├── App.css
│   │   ├── App.js
│   │   ├── App.test.js
│   │   ├── index.css
│   │   ├── index.js
│   │   ├── logo.svg
│   │   ├── reportWebVitals.js
│   │   └── setupTests.js
│   ├── .gitignore
│   ├── index.css
│   ├── package-lock.json
│   ├── package.json
│   ├── postcss.config.js
│   ├── README.md
│   └── tailwind.config.js
├── package.json
├── Procfile
├── readme.md
├── requirements.txt
└── runtime.txt
```

# Database Setup

This project uses a PostgreSQL database to store hockey statistics. The database dump is provided in the `database/hockey_stats.sql` file.

## Prerequisites

- PostgreSQL installed on your system
- psql command-line tool (usually comes with PostgreSQL installation)

## Database Reconstruction

Follow these steps to set up the database:

1. Open a terminal and navigate to the project's root directory.

2. Create a new PostgreSQL database (you can choose any name, but we'll use 'hockey_stats' in this example):

   ```bash
   createdb hockey_stats
   ```

3. Import the database dump:

   ```bash
   psql -d hockey_stats < database/hockey_stats.sql
   ```

   This command will create all necessary tables and populate them with the data from the dump file.

4. Verify the import by connecting to the database and checking the tables:

   ```bash
   psql -d hockey_stats
   ```

   Once connected, you can list all tables with the following command:

   ```sql
   \dt
   ```

   You should see a list of tables related to hockey statistics.

5. Exit the psql prompt:

   ```sql
   \q
   ```

## Updating Database Configuration

After setting up the database, make sure to update the database connection settings in your application. 

In the `backend/app.py` file (or wherever your database configuration is located), update the following lines with your database details:

```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/hockey_stats'
```

Replace `username` and `password` with your PostgreSQL credentials, and `hockey_stats` with the name of the database you created if different.

## Note

The provided SQL dump contains both the schema and data for the hockey statistics database. If you need to reset the database at any point, you can drop the existing database and repeat the reconstruction process:

```bash
dropdb hockey_stats
createdb hockey_stats
psql -d hockey_stats < database/hockey_stats.sql
```

If you encounter any issues during the database setup, please check your PostgreSQL installation and ensure you have the necessary permissions to create and modify databases.

## Connecting to DB locally

sudo service postgresql start
psql -U user -d hockey_stats -h localhost


### Backend Key Files

1. **app.py**: Main application file containing the Flask server setup and API routes.
2. **rag_openAI.py**: Implements the RAG system using OpenAI's language models.
3. **rag_llama3.py**: Alternative implementation of the RAG system using the Llama 3 model.
4. **simplified_hockey_stats_schema.py**: Defines the schema for hockey statistics data.
5. **lookup_table.py**: Contains mappings or reference data for the system.
6. **new_table.py**: Handles creation or updates of database tables.
7. **requirements.txt**: Lists Python dependencies for the backend.

# Deployment Instructions

This document provides instructions for both local development and cloud deployment of the Hockey Statistics RAG System.

## Local Development

### Prerequisites
- Python 3.8+
- Node.js 14+
- PostgreSQL

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd ~/RAG/hockey_RAG/backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the database:
   ```bash
   createdb hockey_stats
   psql -d hockey_stats < ../database/hockey_stats.sql
   ```

5. Create a `.env` file with necessary environment variables:
   ```
   DATABASE_URL=postgresql://username:password@localhost/hockey_stats
   OPENAI_API_KEY=your_openai_api_key
   ```

6. Run the backend server:
   ```bash
   python app.py
   ```

   The backend should now be running on `http://localhost:5000`.

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd ~/RAG/hockey_RAG/frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create a `.env` file with the backend URL:
   ```
   REACT_APP_API_URL=http://localhost:5000
   ```

4. Start the development server:
   ```bash
   npm start
   ```

   The frontend should now be accessible at `http://localhost:3000`.

## Cloud Deployment (Heroku)

### Prerequisites
- Heroku CLI installed
- Git

### Backend Deployment

1. Create a new Heroku app for the backend:
   ```bash
   heroku create hockeyai-backend
   ```

2. Add PostgreSQL addon:
   ```bash
   heroku addons:create heroku-postgresql:hobby-dev
   ```

3. Set environment variables:
   ```bash
   heroku config:set OPENAI_API_KEY=your_openai_api_key
   ```

4. Deploy the backend:
   ```bash
   git subtree push --prefix backend heroku main
   ```

5. Import the database:
   ```bash
   heroku pg:psql < database/hockey_stats.sql
   ```

### Frontend Deployment

1. Create a new Heroku app for the frontend:
   ```bash
   heroku create hockeyai-frontend
   ```

2. Set the backend URL:
   ```bash
   heroku config:set REACT_APP_API_URL=https://hockeyai-backend.herokuapp.com
   ```

3. Add this script to `package.json`:
   ```json
   "scripts": {
     "heroku-postbuild": "npm run build"
   }
   ```

4. Deploy the frontend:
   ```bash
   git subtree push --prefix frontend heroku main
   ```

### Connecting Frontend and Backend

1. In the frontend Heroku app settings, add this buildpack:
   ```
   https://buildpack-registry.s3.amazonaws.com/buildpacks/mars/create-react-app.tgz
   ```

2. Ensure CORS is properly configured in the backend to allow requests from the frontend domain.

## Switching Between Environments

- For local development, ensure your frontend `.env` file points to `http://localhost:5000`.
- For cloud deployment, update the frontend's `REACT_APP_API_URL` to point to your Heroku backend URL.

Remember to never commit sensitive information like API keys to your repository. Always use environment variables for such data.


# app.py - Flask Server for Hockey Statistics RAG System

## Overview

`app.py` is the main server file for the Hockey Statistics RAG (Retrieval-Augmented Generation) System. It sets up a Flask web server that serves the frontend application and provides an API endpoint for processing hockey-related queries.

## Key Components

1. **Flask App Setup**: 
   - Initializes a Flask application
   - Configures CORS (Cross-Origin Resource Sharing)
   - Sets up static file serving for the React frontend

2. **API Endpoints**:
   - `/api/query`: Handles POST requests for processing hockey queries
   - `/api/health`: A simple health check endpoint

3. **Static File Serving**:
   - Serves the React frontend application
   - Implements a catch-all route for client-side routing

## Dependencies

- Flask: Web framework
- Flask-CORS: Handles Cross-Origin Resource Sharing
- dotenv: Loads environment variables
- rag_openAI: Custom module containing the `process_query` function

## Environment Setup

The application uses environment variables loaded from a `.env` file. Ensure this file is present and contains necessary configurations (e.g., API keys, database credentials).

## Routes

1. `/api/query` (POST):
   - Accepts JSON payload with a 'query' field
   - Processes the query using the RAG system
   - Returns the result as JSON

2. `/api/health` (GET):
   - Returns a simple health status

3. `/*` (GET):
   - Serves static files for the React frontend
   - Falls back to `index.html` for client-side routing

## Usage

To run the server:

1. Ensure all dependencies are installed:
   ```
   pip install flask flask-cors python-dotenv
   ```

2. Set up the environment variables in a `.env` file.

3. Run the script:
   ```
   python app.py
   ```

The server will start on `http://0.0.0.0:5000` by default, or on the port specified by the `PORT` environment variable.

## Development and Debugging

- The script includes several debug print statements to help with troubleshooting.
- It prints information about the current working directory, Python path, and static folder configuration.

## Note on Frontend Integration

This server is designed to work with a React frontend. Ensure that the frontend build is located in the correct directory (`/app/frontend/build` by default) for proper static file serving.


## Overview of rag_OpenAI.py

This system is a Retrieval-Augmented Generation (RAG) application designed to process natural language queries about hockey statistics and provide informative responses. It combines the power of large language models with a structured database of hockey statistics to offer accurate and context-aware answers.

## How It Works

1. **Query Processing** (`process_query`):
   - The system takes a natural language query as input.
   - It uses OpenAI's language model to parse and expand the query (`parse_and_expand_query`), extracting key information such as player names, team abbreviations, and the specific statistics being requested.

2. **Context Management** (`generate_context_from_history`, `query_requires_history`):
   - The system maintains a short-term memory of recent queries and responses (`chat_history`).
   - It analyzes each new query to determine if context from previous interactions is needed to provide an accurate response.

3. **Query Classification** (part of `parse_and_expand_query`):
   - Queries are classified as either hockey-related or non-hockey-related.
   - Hockey-related queries are further categorized as requiring specific statistical data or general knowledge.

4. **Data Retrieval** (`generate_sql_query`, `test_sql_query`):
   - For queries requiring specific statistics, the system generates an SQL query based on the parsed information.
   - This SQL query is executed against a PostgreSQL database containing comprehensive hockey statistics.

5. **Response Generation**:
   - For non-hockey queries, the system provides a general response and suggests hockey-related topics (`handle_non_hockey_query`, `generate_natural_language_answer_non_hockey`).
   - For hockey queries not requiring specific data, it generates a response based on general hockey knowledge (`handle_hockey_query_without_data`, `generate_natural_language_answer_hockey_without_data`).
   - For data-driven queries, it combines the retrieved statistics with natural language generation to create an informative response (`handle_hockey_query_with_data`, `generate_natural_language_answer_with_data`).

6. **Error Handling** (`correct_query`, `generate_error_response`):
   - If data retrieval fails, the system attempts to correct the SQL query.
   - If correction fails, it generates an error response explaining the issue and suggesting how to rephrase the query.

7. **Output** (part of `process_query`):
   - The final output includes a natural language response, and when applicable, the SQL query used and a summary of the data retrieved.

## Key Components

- **OpenAI API Integration** (`generate_response`): Used for query parsing, expansion, and natural language generation.
- **PostgreSQL Database**: Stores the hockey statistics data.
- **SQL Query Generation and Execution** (`generate_sql_query`, `test_sql_query`): Dynamically creates and runs SQL queries based on user input.
- **Context Management** (`update_chat_history`, `get_chat_history`): Maintains recent conversation history to provide context-aware responses.
- **Error Handling and Query Correction** (`correct_query`, `generate_error_response`): Ensures robust performance even with complex or ambiguous queries.

## Main Function

The `main()` function serves as the entry point for the application. It runs an interactive loop where:
1. It prompts the user for a query.
2. Processes the query using `process_query()`.
3. Displays the result to the user.
4. Continues this loop until the user chooses to exit.

## Usage

The system is designed to be interactive, allowing users to input natural language queries about hockey statistics and receive detailed, data-driven responses. It can handle a wide range of queries, from simple stat lookups to complex analytical questions about player and team performance.

To use the system, run the script and enter your hockey-related queries when prompted. The system will process your query, retrieve relevant data if necessary, and provide a detailed response.





## Additional Notes

- The project uses both OpenAI and Llama 3 models for the RAG system, providing flexibility in model choice.
- The frontend uses Tailwind CSS for styling, which allows for rapid UI development.
- Ensure all necessary API keys and environment variables are set in your Heroku app settings.
- When making changes, always ensure you're in the correct directory for the part of the application you're modifying.
- Remember to update the frontend API endpoint URLs if you change the backend URL.

For more detailed information on specific components or usage, refer to the individual file documentations or comments within the code.