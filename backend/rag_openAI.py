import json
import os
import re
import logging
import json
import requests
import re
import os
import openai
import csv
import psycopg2
import re

from dotenv import load_dotenv
from collections import deque
from tabulate import tabulate
from .lookup_table import hockey_stats_schema
from .simplified_hockey_stats_schema import simplified_hockey_stats_schema
from openai import OpenAI
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from typing import Dict, Any, List

# Load environment variables from a .env file if it exists
load_dotenv()

# Ensure you have set the OPENAI_API_KEY environment variable
api_key = os.environ.get('OPENAI_API_KEY')
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set")

# Set the API key for the OpenAI library
openai.api_key = api_key

# Initialize the OpenAI client with your API key
client = OpenAI(api_key=api_key)


# Database connection parameters
db_params = {
    "dbname": os.environ.get("DB_NAME", "hockey_stats"),
    "user": os.environ.get("DB_USER", "sauhumatti"),
    "host": os.environ.get("DB_HOST", "localhost"),
    "password": os.environ.get("DB_PASSWORD", "")
}

# Chat memory implementation
chat_history = deque(maxlen=3)

logging.basicConfig(level=logging.DEBUG)

def generate_response(messages: List[Dict[str, str]], model: str = "gpt-4o-mini", max_tokens: int = 300) -> str:
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens
    )
    return response.choices[0].message.content

def update_chat_history(query: str, response: str) -> None:
    chat_history.append({"query": query, "response": response})

def get_chat_history() -> deque:
    return chat_history

def query_requires_history(current_query: str) -> bool:
    logging.debug(f"Analyzing query for history requirement: '{current_query}'")

    system_content = """
    Your task is to determine if the current query requires context from a previous conversation to be answered accurately and completely.
    Look for references to previous information, follow-up questions, or implicit context that relies on a previous exchange.
    """

    prompt = f"""
    Current Query: "{current_query}"

    Does the current query require information from a previous conversation to be answered accurately?
    Respond with only True or False, followed by a brief explanation."""

    messages = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": prompt}
    ]

    response = generate_response(messages)
    logging.debug(f"Model's response for history requirement: {response}")

    decision, explanation = response.strip().split('\n', 1) if '\n' in response else (response.strip(), "")
    requires_history = decision.lower() == 'true'

    logging.debug(f"Query {'requires' if requires_history else 'does not require'} historical context.")
    logging.debug(f"Explanation: {explanation.strip()}")

    return requires_history


def generate_context_from_history(query: str) -> str:
    if not query_requires_history(query):
        return ""

    context = "Previous conversation:\n"
    for exchange in chat_history:
        context += f"User: {exchange['query']}\nAssistant: {exchange['response']}\n\n"

    return context.strip()

def parse_and_expand_query(query: str) -> Dict[str, Any]:
    logging.debug(f"Entering parse_and_expand_query with query: {query}")

    system_content = """You are an AI assistant specialized in analyzing hockey statistics queries. You have access to the following tables in the hockey statistics database:

    List of tables in database:
    player_stats_regular_season: Contains individual statistics for skaters (excluding goalies) during regular season games, such as goals, assists, points, plus/minus, and penalty minutes.
    player_stats_playoffs: Contains individual statistics for skaters (excluding goalies) during playoff games, including goals, assists, points, plus/minus, and penalty minutes.
    goalie_stats_regular_season: Contains detailed statistics for goalies during regular season games, such as save percentage, goals against average, and total saves.
    goalie_stats_playoffs: Contains detailed statistics for goalies during playoff games, such as save percentage, goals against average, and total saves.
    team_stats: Contains aggregated statistics for teams over the course of the regular season, such as total wins, losses, goals for, goals against, power play percentage, and penalty kill percentage.
    team_stats_playoffs: Contains aggregated statistics for teams during the playoffs, including total wins, losses, goals for, goals against, power play percentage, and penalty kill percentage.
    team_games: Includes game-by-game statistics for teams, detailing the results of each game, including goals scored, goals allowed, and other team performance metrics.
    lines_and_pairings: Provides information about player lines and defensive pairings for regular season games, indicating which players were on the ice together.
    lines_and_pairings_playoffs: Provides information about player lines and defensive pairings for playoff games, showing the combinations of players on the ice.

    Analyze hockey queries and provide a JSON output with specific fields. Follow these instructions:

    - "expanded_query": Provide a concise, expanded version of the query that clarifies ambiguities and provides full player names.
    - "hockey_related": Set to true if the query is related to hockey, false otherwise.
    - "query_intent": Set to "stats" if the query asks for specific statistics, "general" if it can be answered with general hockey knowledge.
    - "player_names": Include an array of specific player names mentioned in the query. Use full names if available.
    - "team_abbreviations": Include an array of three-letter abbreviations for the teams mentioned in the query.
    - "required_tables": Include an array of table names from the list provided that are relevant to the query.
    - "situation": Use "all", "5on5", "5on4", "4on5", or "other". Use "all" if not specified in the query.
    - "seasons": Include the season(s) mentioned in the query, or an empty array if not specified.

    If "query_intent" is "stats" but "required_tables" is empty, analyze the query again and select the most appropriate table(s) based on the statistics requested."""

    prompt = f"""Analyze the following hockey query and provide a JSON output with specific fields:

    Query: '{query}'

    {{
        "expanded_query": "",
        "hockey_related": true/false,
        "query_intent": "general" / "stats",
        "player_names": [],
        "team_abbreviations": [],
        "required_tables": [],
        "situation": "",
        "seasons": []
    }}

    Provide only the JSON output, without any additional explanation."""

    messages = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": prompt}
    ]

    def clean_response(response: str) -> str:
        response = re.sub(r'^```json\s*', '', response)
        response = re.sub(r'\s*```$', '', response)
        return response.strip()

    logging.debug("Sending request to generate_response")
    response = generate_response(messages)
    logging.debug(f"Received response from generate_response: {response}")

    try:
        cleaned_response = clean_response(response)
        parsed_data = json.loads(cleaned_response)
        logging.debug("Successfully parsed JSON response")

        if parsed_data["query_intent"] == "stats" and not parsed_data["required_tables"]:
            logging.debug("Query intent is stats but no tables selected. Sending for table selection.")
            table_selection_prompt = f"""The following query requires statistics, but no tables were selected. Please analyze the query again and select the most appropriate table(s) based on the statistics requested:

            {json.dumps(parsed_data, indent=2)}

            Update the "required_tables" field with the most relevant table(s) for this query."""

            table_selection_messages = [
                {"role": "system", "content": system_content},
                {"role": "user", "content": table_selection_prompt}
            ]

            table_selection_response = generate_response(table_selection_messages)
            logging.debug(f"Received table selection response: {table_selection_response}")
            cleaned_table_selection_response = clean_response(table_selection_response)
            parsed_data = json.loads(cleaned_table_selection_response)

        parsed_data["required_columns"] = {}
        for table in parsed_data["required_tables"]:
            if table in simplified_hockey_stats_schema:
                parsed_data["required_columns"][table] = list(simplified_hockey_stats_schema[table].keys())

        logging.debug(f"Final parsed_data: {json.dumps(parsed_data, indent=2)}")
        return parsed_data
    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error: {str(e)}")
        logging.error(f"Raw response causing the error: {response}")
        return None

def generate_sql_query(analyzed_data: Dict[str, Any]) -> str:
    system_content = """You are a SQL expert specialized in querying hockey statistics databases.
    Generate a PostgreSQL query based on the provided information. Follow these rules:

    1. Use only the specified tables and columns.
    2. Include appropriate JOINs if multiple tables are required.
    3. Always include the situation in the WHERE clause, even if it's 'all'.
    4. Use the season from additional information.
    5. Include relevant player info columns (like name, team, season) in the SELECT statement for clarity.
    6. Use GROUP BY when using aggregate functions like SUM.
    7. If no specific season is mentioned, assume the query is for all available seasons.
    8. Use the correct column names as provided in the required columns list.
    9. Structure complex queries with appropriate subqueries or CTEs if necessary.
    10. Optimize the query for performance where possible.
    11. Aim to use around 10 of the most relevant columns for the query, but this is a flexible guideline.
        Choose columns that best answer the query while keeping the result concise and informative.
        You may use more or fewer columns if it makes sense for the specific query.
    12. For assists, always use (i_f_primaryassists + i_f_secondaryassists) instead of i_f_assists.
    13. USE THE SITUATION PROVIDED!
    14. Limit results to 50 rows maximum.

    Return only the SQL query, without any additional explanation."""

    prompt = f"""
    Generate a PostgreSQL query for the following:

    Expanded Query: {analyzed_data['expanded_query']}

    Required Tables and Columns:
    {json.dumps(analyzed_data['required_columns'], indent=2)}

    Additional Information:
    - Player Names: {', '.join(analyzed_data['player_names'])}
    - Team Abbreviations: {', '.join(analyzed_data['team_abbreviations'])}
    - Situation: {analyzed_data['situation']}
    - Seasons: {', '.join(map(str, analyzed_data['seasons'])) if analyzed_data['seasons'] else 'All'}

    USE THE SEASON PROVIDED IN HERE NOT IN THE QUERY!

    """

    messages = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": prompt}
    ]

    raw_response = generate_response(messages)

    sql_match = re.search(r'```sql\n(.*?)\n```', raw_response, re.DOTALL)
    if sql_match:
        sql_query = sql_match.group(1).strip()
    else:
        sql_query = raw_response.strip()

    sql_query = sql_query.replace("i_f_assists", "(i_f_primaryassists + i_f_secondaryassists)")

    if 'player_stats_regular_season' in analyzed_data['required_tables'] or 'player_stats_playoffs' in analyzed_data['required_tables']:
        sql_query = sql_query.replace("i_f_assists", "(i_f_primaryassists + i_f_secondaryassists)")

        if "WHERE" in sql_query and "situation" not in sql_query:
            sql_query = sql_query.replace("WHERE", f"WHERE situation = '{analyzed_data['situation']}' AND")
        elif "WHERE" not in sql_query:
            sql_query += f" WHERE situation = '{analyzed_data['situation']}'"

        if "situation = " not in sql_query:
            sql_query += " WHERE situation = 'all'"

    return sql_query

def test_sql_query(query: str, analyzed_data: Dict[str, Any]) -> Dict[str, Any]:
    def execute_query(cursor, query: str) -> Dict[str, Any]:
        cursor.execute(query)
        results = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        results_dicts = [dict(zip(column_names, row)) for row in results]
        return {
            "success": True,
            "column_names": column_names,
            "results": results_dicts,
            "row_count": len(results)
        }

    try:
        with psycopg2.connect(**db_params) as conn:
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            with conn.cursor() as cursor:
                try:
                    return execute_query(cursor, query)
                except psycopg2.Error as e:
                    error_message = str(e)
                    logging.error(f"First attempt failed: {error_message}")

                    corrected_query = correct_query(query, error_message, analyzed_data)
                    if corrected_query != query:
                        logging.debug("Attempting with corrected query:")
                        logging.debug(corrected_query)
                        try:
                            return execute_query(cursor, corrected_query)
                        except psycopg2.Error as e2:
                            return {
                                "success": False,
                                "error_message": f"Corrected query also failed: {str(e2)}"
                            }
                    else:
                        return {
                            "success": False,
                            "error_message": f"Unable to correct query: {error_message}"
                        }

    except psycopg2.Error as e:
        return {
            "success": False,
            "error_message": f"Database connection error: {str(e)}"
        }

def correct_query(query: str, error_message: str, analyzed_data: Dict[str, Any]) -> str:
    system_content = """You are a SQL expert specialized in correcting and optimizing queries for hockey statistics databases.
    Your task is to analyze the given SQL query, the error message, and the original query requirements, then generate a corrected SQL query.
    Follow these guidelines:

    1. Carefully review the error message and identify the specific issue.
    2. Examine the original query and the requirements to understand the intent.
    3. Make necessary corrections to address the error while preserving the original query's intent.
    4. Ensure all column names used exist in the specified tables.
    5. Verify that the corrected query adheres to all the original requirements.
    6. If a specific column doesn't exist, consider using a suitable alternative or combination of columns.
    7. Maintain the query's structure and logic as much as possible while making corrections.
    8. If the error is related to GROUP BY clauses, ensure all non-aggregated columns in the SELECT statement are included in the GROUP BY clause.
    9. Provide only the corrected SQL query without any additional explanation.

    Remember, your goal is to produce a working query that fulfills the original requirements while addressing the specific error."""

    prompt = f"""
    Original Query:
    {query}

    Error Message:
    {error_message}

    Original Query Requirements:
    Expanded Query: {analyzed_data['expanded_query']}
    Required Tables and Columns: {analyzed_data['required_columns']}
    Player Names: {', '.join(analyzed_data['player_names'])}
    Team Abbreviations: {', '.join(analyzed_data['team_abbreviations'])}
    Situation: {analyzed_data['situation']}
    Seasons: {', '.join(map(str, analyzed_data['seasons'])) if analyzed_data['seasons'] else 'All'}

    Please generate a corrected SQL query that addresses the error and meets the original requirements.
    """

    messages = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": prompt}
    ]

    response = generate_response(messages)

    corrected_query = response.strip()
    corrected_query = corrected_query.replace('```sql', '').replace('```', '').strip()

    return corrected_query

def generate_natural_language_answer_non_hockey(original_query: str, expanded_query: str) -> str:
    system_content = """Answer to the user as normally but
    if the query is not about hockey, suggest to the user to ask something hockey statistics related.
    The database contains player and team statistics from 2008-2024.
    You can suggest questions to ask if the user is lost.
    """

    prompt = f"""
    Original Query: {original_query}

    Expanded Query: {expanded_query}

    """

    messages = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": prompt}
    ]

    response = generate_response(messages, max_tokens=300)

    return response

def generate_natural_language_answer_hockey_without_data(original_query: str, parsed_result: Dict[str, Any]) -> str:
    system_content = """You are an AI assistant and you know everything about the NHL.
    Provide the user with a general answer based on common hockey knowledge.
    Use the information provided in the parsed query to give a more accurate and relevant response.
    If specific players or teams are mentioned, include information about them in your answer."""

    prompt = f"""
    Original Query: {original_query}

    Expanded Query: {parsed_result['expanded_query']}

    Player Names: {', '.join(parsed_result['player_names']) if parsed_result['player_names'] else 'None specified'}

    Team Abbreviations: {', '.join(parsed_result['team_abbreviations']) if parsed_result['team_abbreviations'] else 'None specified'}

    Seasons: {', '.join(map(str, parsed_result['seasons'])) if parsed_result['seasons'] else 'Not specified'}

    Situation: {parsed_result['situation']}

    Please provide a comprehensive answer to the query using this information.
    """

    messages = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": prompt}
    ]

    response = generate_response(messages, max_tokens=300)

    return response

def generate_natural_language_answer_with_data(original_query: str, expanded_query: str, sql_query: str, query_result: List[Dict[str, Any]]) -> str:
    table = ""
    if query_result:
        try:
            headers = query_result[0].keys()
            rows = [list(row.values()) for row in query_result]
            table = tabulate(rows, headers=headers, tablefmt="fancy_grid",
                             numalign="right", stralign="left",
                             colalign=("left",) + ("right",) * (len(headers) - 1),
                             maxcolwidths=[None] + [20] * (len(headers) - 1),
                             floatfmt=".2f")
        except (IndexError, AttributeError):
            table = "Error: Unable to generate table from query results."

    system_content = """You are an AI assistant specialized in interpreting hockey statistics.
    Your task is to provide a clear, concise answer based on the original query, the expanded query,
    the SQL query used (if any), and the results obtained (if any). Start your response with a formatted table
    of the results if available. Then explain the results in a way that's easy for a hockey fan to understand,
    highlighting key points and providing context where necessary. If no SQL query was run, provide a general
    answer based on your knowledge of hockey. If the query is not about hockey, suggest to the user to ask
    something hockey related."""

    prompt = f"""
    Original Query: {original_query}

    Expanded Query: {expanded_query}

    SQL Query Used to fetch stats from database: {'None' if sql_query is None else sql_query}

    Query Results Table:
    {table}

    Please provide a clear, concise answer to the original query. Start with the table of results (if available),
    then explain the data. If SQL query and results are available, base your answer on these results.
    Otherwise, provide a general answer based on common hockey knowledge. Explain any relevant statistics
    or trends, and provide context if necessary."""

    messages = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": prompt}
    ]

    response = generate_response(messages, max_tokens=1200)

    return response

def generate_error_response(query: str, expanded_query: str, error_message: str) -> str:
    system_content = """You are an AI assistant specialized in hockey statistics.
    An error occurred while trying to fetch specific data for the user's query.
    Your task is to:
    1. Inform the user about the error in fetching the data.
    2. Provide a general answer to their query based on your knowledge of hockey.
    3. Suggest how they might rephrase their query to be more precise or easier to process.
    4. Optionally, provide an example of a similar query that might work better."""

    prompt = f"""
    Original Query: {query}

    Expanded Query: {expanded_query}

    Error Message: {error_message}

    Please provide a response that addresses the points mentioned in the system message."""

    messages = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": prompt}
    ]

    response = generate_response(messages, max_tokens=500)

    return response

def handle_non_hockey_query(query: str, result: Dict[str, Any]) -> Dict[str, Any]:
    logging.debug("Query is not related to hockey statistics. Skipping SQL query generation and testing.")
    nl_answer = generate_natural_language_answer_non_hockey(
        query,
        result['expanded_query']
    )
    logging.debug("\nNatural Language Answer:")
    logging.debug(nl_answer)
    return {"natural_language_answer": nl_answer, "hockey_related": False}

def handle_hockey_query_without_data(query: str, result: Dict[str, Any]) -> Dict[str, Any]:
    logging.debug("Query is hockey-related but doesn't require specific table data. Generating general answer.")
    nl_answer = generate_natural_language_answer_hockey_without_data(
        query,
        result  # Pass the full parsed result instead of just the expanded query
    )
    logging.debug("\nNatural Language Answer:")
    logging.debug(nl_answer)
    return {"natural_language_answer": nl_answer, "hockey_related": True, "requires_data": False}

def handle_hockey_query_with_data(query: str, result: Dict[str, Any]) -> Dict[str, Any]:
    sql_query = generate_sql_query(result)
    logging.debug("\nGenerated SQL Query:")
    logging.debug(sql_query)

    test_result = test_sql_query(sql_query, result)
    if test_result["success"]:
        logging.debug("\nQuery executed successfully!")
        logging.debug(f"Columns: {', '.join(test_result['column_names'])}")
        logging.debug(f"Number of rows: {test_result['row_count']}")
        logging.debug("All results:")
        for row in test_result['results']:
            logging.debug(row)

        nl_answer = generate_natural_language_answer_with_data(
            query,
            result['expanded_query'],
            sql_query,
            test_result['results']
        )
        logging.debug("\nNatural Language Answer:")
        logging.debug(nl_answer)

        response = {
            "natural_language_answer": nl_answer,
            "sql_query": sql_query,
            "result_summary": {
                "row_count": test_result['row_count'],
                "columns": test_result['column_names']
            }
        }
    else:
        logging.debug("\nQuery execution failed!")
        logging.debug(f"Error: {test_result['error_message']}")
        error_response = generate_error_response(query, result['expanded_query'], test_result['error_message'])
        logging.debug("\nError Response:")
        logging.debug(error_response)
        response = {
            "natural_language_answer": error_response,
            "sql_query": sql_query,
            "error": test_result['error_message']
        }

    logging.debug("\n" + "="*50)  # Separator between queries
    return response

def handle_failed_query() -> Dict[str, Any]:
    logging.debug("Failed to parse and expand query.")
    response = {
        "natural_language_answer": "Failed to parse and expand query.",
        "hockey_related": None
    }
    logging.debug("\n" + "="*50)  # Separator between queries
    return response

def process_query(query: str) -> Dict[str, Any]:
    logging.debug(f"\n--- Processing Query: {query} ---")

    context = generate_context_from_history(query)

    full_query = f"{context}\n\nCurrent query: {query}" if context else query

    result = parse_and_expand_query(full_query)
    if result:
        logging.debug("\nParsed and expanded query:")
        logging.debug(json.dumps(result, indent=2))

        if not result['hockey_related']:
            response = handle_non_hockey_query(query, result)
        elif result['hockey_related'] and result['query_intent'] == 'general':
            response = handle_hockey_query_without_data(query, result)
        else:
            response = handle_hockey_query_with_data(query, result)

        update_chat_history(query, response['natural_language_answer'])

        return response
    else:
        return handle_failed_query()

def main():
    print("Welcome to the Hockey Stats Query System!")
    print("Enter your queries below. Type 'exit' to quit the program.")

    while True:
        user_query = input("\nEnter your query: ").strip()

        if user_query.lower() == 'exit':
            print("Thank you for using the Hockey Stats Query System. Goodbye!")
            break

        result = process_query(user_query)
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()



