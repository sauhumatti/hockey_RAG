# Hockey Statistics RAG System Documentation

## Table of Contents

1. [Project Overview](#project-overview)
2. [Project Structure](#project-structure)
3. [Backend](#backend)
    - [Key Files](#backend-key-files)
    - [Setup and Installation](#backend-setup-and-installation)
    - [Running the Backend](#running-the-backend)
4. [Frontend](#frontend)
    - [Key Files and Directories](#frontend-key-files-and-directories)
    - [Setup and Installation](#frontend-setup-and-installation)
    - [Running the Frontend](#running-the-frontend)
5. [Detailed Component Documentation](#detailed-component-documentation)
    - [rag_openAI.py](#rag_openAIpy)
    - [app.py](#apppy)
6. [Running the Full Stack Application](#running-the-full-stack-application)
7. [Additional Notes](#additional-notes)

## Project Overview

The Hockey Statistics Retrieval-Augmented Generation (RAG) system is a full-stack application designed to provide an interface for querying and displaying hockey statistics using advanced natural language processing techniques. The backend is built with Python, while the frontend is developed using React.

## Project Structure

```
RAG/
├── hockey_RAG/
│   ├── backend/
│   │   ├── __pycache__/
│   │   ├── app.py
│   │   ├── lookup_table.py
│   │   ├── new_table.py
│   │   ├── rag_llama3.py
│   │   ├── rag_openAI.py
│   │   ├── requirements.txt
│   │   └── simplified_hockey_stats_schema.py
│   ├── classic_html/
│   └── frontend/
│       ├── build/
│       ├── node_modules/
│       ├── public/
│       ├── src/
│       │   ├── assets/
│       │   ├── components/
│       │   ├── App.css
│       │   ├── App.js
│       │   ├── App.test.js
│       │   ├── index.css
│       │   ├── index.js
│       │   ├── logo.svg
│       │   ├── reportWebVitals.js
│       │   └── setupTests.js
│       ├── .gitignore
│       ├── index.css
│       ├── package-lock.json
│       ├── package.json
│       ├── postcss.config.js
│       ├── README.md
│       └── tailwind.config.js
```

## Backend

The backend is built with Python and is located in the `hockey_RAG/backend/` directory.

### Backend Key Files

1. **app.py**: Main application file containing the Flask server setup and API routes.
2. **rag_openAI.py**: Implements the RAG system using OpenAI's language models.
3. **rag_llama3.py**: Alternative implementation of the RAG system using the Llama 3 model.
4. **simplified_hockey_stats_schema.py**: Defines the schema for hockey statistics data.
5. **lookup_table.py**: Contains mappings or reference data for the system.
6. **new_table.py**: Handles creation or updates of database tables.
7. **requirements.txt**: Lists Python dependencies for the backend.

### Backend Setup and Installation

1. Navigate to the `hockey_RAG/backend/` directory.
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - On Windows: `venv\Scripts\activate`
   - On macOS and Linux: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`

### Running the Backend

1. Navigate to the `hockey_RAG/backend/` directory.
2. Run: `python app.py`

## Frontend

The frontend is a React application located in the `hockey_RAG/frontend/` directory.

### Frontend Key Files and Directories

1. **src/**: Contains the source code for the React application.
   - **App.js**: Main component of the React application.
   - **index.js**: Entry point of the React application.
   - **components/**: Directory for React components.
2. **public/**: Contains public assets and the HTML template.
3. **package.json**: Defines npm dependencies and scripts for the frontend.
4. **tailwind.config.js**: Configuration file for Tailwind CSS, a utility-first CSS framework.

### Frontend Setup and Installation

1. Navigate to the `hockey_RAG/frontend/` directory.
2. Install dependencies: `npm install`

### Running the Frontend

1. Navigate to the `hockey_RAG/frontend/` directory.
2. Run: `npm start`

## Detailed Component Documentation

### rag_openAI.py

The `rag_openAI.py` file is a core component of the backend, implementing the Retrieval-Augmented Generation (RAG) system using OpenAI's language models. Here's a detailed breakdown of its main components and functionalities:

1. **Imports and Setup**:
   - Imports necessary libraries including `json`, `os`, `re`, `logging`, `openai`, `pandas`, `psycopg2`, and custom modules.
   - Sets up the OpenAI API key from environment variables.
   - Defines database connection parameters.

2. **Chat History Management**:
   - Implements a `deque` to maintain chat history, limited to the last 3 interactions.
   - Functions `update_chat_history()` and `get_chat_history()` manage this history.

3. **Query Processing**:
   - `generate_response()`: Generates responses using OpenAI's API.
   - `parse_and_expand_query()`: Analyzes and expands user queries, determining intent and required data.
   - `generate_sql_query()`: Converts the parsed query into an SQL query for database retrieval.

4. **Database Interaction**:
   - `test_sql_query()`: Executes the generated SQL query against the database.
   - `correct_query()`: Attempts to correct SQL queries if they fail.

5. **Natural Language Answer Generation**:
   - Several functions (`generate_natural_language_answer_*`) create human-readable responses based on query results or general hockey knowledge.

6. **Main Processing Pipeline**:
   - `process_query()`: The main function that orchestrates the entire query processing pipeline, from user input to final response.

7. **Error Handling and Logging**:
   - Implements comprehensive error handling and logging throughout the file.

8. **Constants and Configuration**:
   - Defines constants like `simplified_hockey_stats_schema` for data structure reference.

This file is the heart of the RAG system, handling the complex task of interpreting natural language queries, retrieving relevant data, and generating informative responses.

### app.py

The `app.py` file serves as the main entry point for the backend Flask application. It sets up the web server and defines the API endpoints. Here's a detailed overview:

1. **Imports and Setup**:
   - Imports Flask, CORS, and the `process_query` function from `rag_openAI`.
   - Sets up the Flask application and enables CORS for cross-origin requests.

2. **API Endpoints**:
   - `/api/query` (POST): The main endpoint for processing hockey statistics queries.
     - Accepts JSON data with a 'query' field.
     - Calls `process_query()` from `rag_openAI.py` to handle the query.
     - Returns the result as JSON.

3. **Static File Serving**:
   - Configures the app to serve the React frontend from the `../frontend/build` directory.
   - Implements a catch-all route to serve `index.html` for any unmatched routes, enabling client-side routing in the React app.

4. **Error Handling**:
   - Implements basic error handling for the query processing endpoint.

5. **Application Runner**:
   - Includes a conditional to run the Flask app in debug mode when the script is executed directly.

Key functionalities:

- Acts as the bridge between the frontend and the RAG system.
- Handles HTTP requests and responses.
- Manages CORS to allow the frontend to communicate with the backend.
- Serves the static files of the React application, creating a seamless full-stack application.

This file is crucial for setting up the web server and defining how the frontend interacts with the backend RAG system. It encapsulates the server-side logic and API definition, keeping it separate from the core RAG functionality in `rag_openAI.py`.

## Running the Full Stack Application

To run the full stack application:

1. Ensure the backend is running:
   ```
   cd hockey_RAG/backend
   python app.py
   ```
   This will start the Flask server, typically on `http://localhost:5000`.

2. In a separate terminal, start the frontend:
   ```
   cd hockey_RAG/frontend
   npm start
   ```
   This will launch the React application, usually on `http://localhost:3000`.

With both parts running, you can interact with the hockey statistics RAG system through the web interface, which will communicate with the backend to process queries and retrieve information.

## Additional Notes

- The project uses both OpenAI and Llama 3 models for the RAG system, providing flexibility in model choice.
- The frontend uses Tailwind CSS for styling, which allows for rapid UI development.
- Ensure all necessary API keys and environment variables are set before running the application.

For more detailed information on specific components or usage, refer to the individual file documentations or comments within the code.