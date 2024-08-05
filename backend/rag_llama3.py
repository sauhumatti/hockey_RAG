import requests
import re
import json
from lookup_table import hockey_stats_schema
import psycopg2
from psycopg2 import sql



# Database connection parameters
db_params = {
    "dbname": "hockey_stats",
    "user": "sauhumatti",
    "host": "localhost"
}


def expand_user_query(query):
    prompt = f"""
    Original user query: "{query}"

    Please provide a concise, expanded version of this query that clarifies any ambiguities and includes implicit information. The expanded query should be a single sentence or short paragraph.

    Consider the following when expanding the query:
    1. Clarify player names if abbreviated or ambiguous.
    2. Specify whether the query is about regular season, playoffs, or both if not mentioned.
    3. Clarify the time frame (e.g., specific season, career total) if not specified.
    4. Ensure all relevant statistical categories are explicitly mentioned.

    Return your response as a JSON object with the following structure:
    {{
        "expanded_query": "Your expanded query here"
    }}

    Provide only the JSON object without any additional text or explanations.
    """

    response = requests.post(
        'http://localhost:11434/api/generate',
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        }
    )

    if response.status_code == 200:
        response_text = response.json().get('response', '').strip()
        try:
            response_json = json.loads(response_text)
            expanded_query = response_json.get('expanded_query', query)
            print("Expanded Query:")
            print(expanded_query)
            return expanded_query
        except json.JSONDecodeError:
            print("Error: Invalid JSON in model response")
            print("Raw response:", response_text)
            return query
    else:
        print(f"Error: Unable to expand query. Status code: {response.status_code}")
        return query  # Return original query if expansion fails





def extract_intent(query):
    prompt = f"""System: You are an AI assistant specialized in analyzing hockey statistics queries. You have access to the following tables in the hockey statistics database:

goalie_stats_playoffs: Contains goalie statistics for playoff games.
goalie_stats_regular_season: Contains goalie statistics for regular season games.
lines_and_pairings: Information about player lines and defensive pairings for regular season.
lines_and_pairings_playoffs: Information about player lines and defensive pairings for playoffs.
player_stats_regular_season: Contains individual player statistics for regular season games (excluding goalies).
player_stats_playoffs: Contains individual player statistics for playoff games (excluding goalies).
team_games: Contains game-by-game statistics for teams.
team_stats: Contains aggregated team statistics for regular season.
team_stats_playoffs: Contains aggregated team statistics for playoffs.

User: Analyze the following hockey query and provide a JSON output with specific fields:

Query: '{query}'

Assistant: Based on the given query, here's the JSON analysis:

{{
    "hockey_statistics_required": ,
    "player_names": [],
    "team_names": [],
    "team_abbreviations": [],
    "required_tables": [],
    "situation": "",
    "seasons": "[]"
}}

Please fill in the JSON fields as follows:
- "hockey_statistics_required": true if the query requires hockey statistics, false otherwise.
- "player_names": An array of specific player names mentioned in the query. Include full names if available.
- "team_names": An array of specific team names mentioned in the query.
- "team_abbreviations": An array of three-letter abbreviations for the teams mentioned in the query.
- "required_tables": An array of table names from the list provided that are relevant to the query.
- "situation": "all", "5on5", "5on4", "4on5", or "other". Use "all" if not specified in the query.
- "seasons": The season(s) mentioned in the query, or "Not specified".

Ensure the JSON is properly formatted and all fields are included, even if some are empty arrays or "Not specified".

Return only the JSON part!

"""

    response = requests.post(
        'http://localhost:11434/api/generate',  # Ollama API endpoint
        json={
            "model": "llama3",  # or whichever model you're using
            "prompt": prompt,
            "stream": False
        }
    )
    
    if response.status_code == 200:
        # Extract only the JSON part from the response
        response_text = response.json().get('response', '').strip()
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            try:
                # Parse the JSON to ensure it's valid, then return it as a string
                json_str = json_match.group()
                json.loads(json_str)  # This will raise an exception if the JSON is invalid
                return json_str
            except json.JSONDecodeError:
                return json.dumps({"error": "Invalid JSON in model response"})
        else:
            return json.dumps({"error": "No JSON found in model response"})
    else:
        return json.dumps({"error": f"Unable to retrieve intent. Status code: {response.status_code}"})




def process_intent(query, intent_json):
    try:
        print("=== Starting process_intent ===")
        print(f"Original query: {query}")
        print(f"Intent JSON: {intent_json}")
        
        intent = json.loads(intent_json)
        
        processed_intent = {
            "original_query": query,
            "processed_data": {}
        }
        
        hockey_stats_required = intent.get("hockey_statistics_required", False)
        processed_intent["processed_data"]["hockey_statistics_required"] = hockey_stats_required
        print(f"Hockey stats required: {hockey_stats_required}")

        if not hockey_stats_required:
            print("Hockey stats not required. Returning early.")
            return processed_intent

        processed_intent["processed_data"]["player_names"] = [
            name.strip() for name in intent.get("player_names", [])
        ]
        print(f"Processed player names: {processed_intent['processed_data']['player_names']}")
        
        processed_intent["processed_data"]["team_names"] = [
            name.strip() for name in intent.get("team_names", [])
        ]
        print(f"Processed team names: {processed_intent['processed_data']['team_names']}")
        
        processed_intent["processed_data"]["team_abbreviations"] = [
            abbr.strip().upper() for abbr in intent.get("team_abbreviations", [])
        ]
        print(f"Processed team abbreviations: {processed_intent['processed_data']['team_abbreviations']}")
        
        print("Available tables in schema:", list(hockey_stats_schema.keys()))
        
        required_tables = intent.get("required_tables", [])
        print(f"Required tables from intent: {required_tables}")
        processed_tables = []
        for table in required_tables:
            print(f"Processing table: {table}")
            if table in hockey_stats_schema:
                processed_tables.append(table)
                print(f"Table '{table}' found in schema.")
            else:
                print(f"Warning: Table '{table}' not found in schema.")
        
        processed_intent["processed_data"]["required_tables"] = processed_tables
        print(f"Final processed tables: {processed_tables}")
        
        valid_situations = ["all", "5on5", "5on4", "4on5", "other"]
        processed_intent["processed_data"]["situation"] = (
            intent.get("situation", "all") if intent.get("situation") in valid_situations else "all"
        )
        print(f"Processed situation: {processed_intent['processed_data']['situation']}")
        
        seasons = intent.get("seasons", [])
        print(f"Seasons from intent: {seasons}")
        if isinstance(seasons, list):
            processed_seasons = []
            for season in seasons:
                match = re.search(r'\d{4}', str(season))
                if match:
                    processed_seasons.append(int(match.group()))
            processed_intent["processed_data"]["seasons"] = processed_seasons
        elif seasons == "Not specified":
            processed_intent["processed_data"]["seasons"] = []
        else:
            processed_intent["processed_data"]["seasons"] = [int(seasons)] if seasons.isdigit() else []
        print(f"Processed seasons: {processed_intent['processed_data']['seasons']}")

        category_explanations = get_category_explanations(processed_tables)
        print("Category explanations:", json.dumps(category_explanations, indent=2))
        
        required_subcategories = get_required_subcategories(query, intent, category_explanations)
        print("Required subcategories:", json.dumps(required_subcategories, indent=2))
        
        column_descriptions = {}
        for table, subcategories in required_subcategories.items():
            column_descriptions[table] = get_column_descriptions(table, subcategories)
        
        processed_intent["processed_data"]["required_subcategories"] = required_subcategories
        processed_intent["processed_data"]["column_descriptions"] = column_descriptions
        
        print("=== Finished process_intent ===")
        return processed_intent
    except json.JSONDecodeError:
        print("Error: Invalid JSON input")
        return {"error": "Invalid JSON input"}
    except Exception as e:
        print(f"Error: Processing error - {str(e)}")
        return {"error": f"Processing error: {str(e)}"}


def get_category_explanations(required_tables):
    explanations = {}
    for table in required_tables:
        if table in hockey_stats_schema:
            explanations[table] = hockey_stats_schema[table].get('category_explanations', {})
    return explanations

def get_required_subcategories(query, intent, category_explanations):
    print("=== Starting get_required_subcategories ===")
    print(f"Query: {query}")
    print(f"Intent: {json.dumps(intent, indent=2)}")
    print(f"Category explanations: {json.dumps(category_explanations, indent=2)}")

    prompt = f"""
    Analyze the following hockey query and the extracted intent to determine which subcategories of statistics are required to answer the query. Use the provided category explanations for reference.

    Query: {query}

    Extracted Intent: {json.dumps(intent, indent=2)}

    Category Explanations for Required Tables:
    {json.dumps(category_explanations, indent=2)}

    Based on the query, intent, and the category explanations, list the required subcategories for each table mentioned in the 'required_tables' field. Use the format:

    {{
        "table_name": ["subcategory1", "subcategory2", ...]
    }}

    Only include relevant subcategories that are necessary to answer the query. Refer to the category explanations to understand what each subcategory represents and determine its relevance to the query.
    """

    print(f"Prompt for AI model: {prompt}")

    response = requests.post(
        'http://localhost:11434/api/generate',
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        }
    )

    print(f"AI model response status code: {response.status_code}")

    if response.status_code == 200:
        response_text = response.json().get('response', '').strip()
        print(f"AI model response: {response_text}")

        # Try to extract JSON from the response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            try:
                result = json.loads(json_match.group())
                print(f"Parsed subcategories: {json.dumps(result, indent=2)}")
                return result
            except json.JSONDecodeError:
                print("Failed to parse extracted JSON")
        else:
            print("No JSON found in the response")

        # If JSON extraction fails, try to parse the response manually
        result = {}
        for line in response_text.split('\n'):
            if ':' in line:
                table, subcategories = line.split(':', 1)
                table = table.strip().strip('"')
                subcategories = [s.strip().strip('"[]') for s in subcategories.split(',')]
                result[table] = subcategories

        if result:
            print(f"Manually parsed subcategories: {json.dumps(result, indent=2)}")
            return result
        else:
            print("Failed to parse subcategories")
            return {}
    else:
        print(f"Failed to get response from AI model. Status code: {response.status_code}")
        return {}

    print("=== Finished get_required_subcategories ===")



def get_column_descriptions(table, subcategories):
    descriptions = {}
    if table in hockey_stats_schema:
        for subcategory in subcategories:
            if subcategory in hockey_stats_schema[table]['descriptions']:
                descriptions.update(hockey_stats_schema[table]['descriptions'][subcategory])
    return descriptions



def process_and_test_query(query, processed_intent):
    # Determine required columns
    required_columns = determine_required_columns(processed_intent)
    print("Required Columns:")
    print(json.dumps(required_columns, indent=2))
    print()

    # Generate SQL query
    sql_query = generate_sql_query(query, processed_intent, required_columns)
    print("Generated SQL Query:")
    print(sql_query)
    print()

    # Test the generated SQL query
    test_result = test_sql_query(sql_query)
    
    if test_result["success"]:
        print("Query executed successfully!")
        print(f"Columns: {', '.join(test_result['column_names'])}")
        print(f"Number of rows: {test_result['row_count']}")
        print("Sample results:")
        for row in test_result['results']:
            print(row)
        if test_result['truncated']:
            print("(Results truncated)")
    else:
        print("Query execution failed!")
        print(f"Error Type: {test_result['error_type']}")
        print(f"Error Message: {test_result['error_message']}")

    return test_result



def determine_required_columns(processed_intent):
    context = json.dumps(processed_intent, indent=2)
    
    prompt = f"""
    Context:
    {context}

    Based on context, determine which columns from each required table are necessary to answer the query.

    Explain the thought prosess of choosing these columns.

    Return the columns in this format and use the exact same table names:

    {{
        "table_name": ["column1", "column2", ...]
    }}

    """
    print("Required columns query: " + prompt)
    response = requests.post(
        'http://localhost:11434/api/generate',
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        }
    )
    if response.status_code == 200:
        response_text = response.json().get('response', '').strip()
        print("Model's response:")
        print(response_text)

    if response.status_code == 200:
        response_text = response.json().get('response', '').strip()
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            try:
                required_columns = json.loads(json_match.group())
                return required_columns
            except json.JSONDecodeError:
                return {"error": "Invalid JSON in model response"}
        else:
            return {"error": "No JSON found in model response"}
    else:
        return {"error": f"Unable to determine required columns. Status code: {response.status_code}"}




def generate_sql_query(query, processed_intent, required_columns):
    # Extract relevant information from processed_intent
    player_names = processed_intent["processed_data"]["player_names"]
    team_abbreviations = processed_intent["processed_data"]["team_abbreviations"]
    required_tables = processed_intent["processed_data"]["required_tables"]
    situation = processed_intent["processed_data"]["situation"]
    seasons = processed_intent["processed_data"]["seasons"]

    # Prepare the context for the AI model
    context = f"""
    Original query: {query}
    Player names: {', '.join(player_names)}
    Team abbreviations: {', '.join(team_abbreviations)}
    Situation: {situation}
    Seasons: {', '.join(map(str, seasons))}

    Required tables and columns:
    """
    for table, columns in required_columns.items():
        context += f"{table}: {', '.join(columns)}\n"

    prompt = f"""
    {context}

    Generate a PostgreSQL query to fetch the statistics for the original query using the available tables and columns. 
    Use ONLY the EXACT column names provided for each table.

    IMPORTANT SQL SYNTAX RULES:
    1. Always use table aliases when referencing columns.
    2. The FROM clause must include all tables mentioned in the SELECT or WHERE clauses.
    3. Join conditions must be explicitly stated in the WHERE clause or using JOIN syntax.
    4. Always include the situation in the WHERE clause.
    5. Use ILIKE for case-insensitive name matching.
    6. Do not reference aliases that haven't been defined.
    7. Use DISTINCT or GROUP BY to avoid duplicate rows when using JOINs.
    8. Consider using UNION ALL instead of JOIN when querying from multiple similar tables.

    Example Queries:

    1. Single table query:
    SELECT pss.name, pss.i_f_points, pss.i_f_goals
    FROM player_stats_regular_season AS pss
    WHERE pss.name ILIKE '%PlayerName%' AND pss.situation = 'all'
    ORDER BY pss.i_f_points DESC;

    2. Multi-table query with DISTINCT:
    SELECT DISTINCT pss.name, pss.i_f_points AS regular_points, pspo.i_f_points AS playoff_points
    FROM player_stats_regular_season AS pss
    LEFT JOIN player_stats_playoffs AS pspo ON pss.name = pspo.name
    WHERE pss.name ILIKE '%PlayerName%' AND pss.situation = 'all' AND pspo.situation = 'all'
    ORDER BY pss.i_f_points DESC;

    3. Multi-table query with UNION ALL:
    SELECT pss.name, pss.i_f_points, 'Regular Season' as season_type
    FROM player_stats_regular_season AS pss
    WHERE pss.name ILIKE '%PlayerName%' AND pss.situation = 'all'
    UNION ALL
    SELECT pspo.name, pspo.i_f_points, 'Playoffs' as season_type
    FROM player_stats_playoffs AS pspo
    WHERE pspo.name ILIKE '%PlayerName%' AND pspo.situation = 'all'
    ORDER BY i_f_points DESC;

    Generate a valid SQL query based on these rules and examples that avoids duplicate results.
    Return ONLY the SQL query, without any additional explanation or formatting.

    Assistant: """

    response = requests.post(
        'http://localhost:11434/api/generate',
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        }
    )

    if response.status_code == 200:
        sql_query = response.json().get('response', '').strip()
        
        # Extract SQL query using regex
        sql_match = re.search(r'(?i)SELECT.*?;', sql_query, re.DOTALL)
        if sql_match:
            return sql_match.group(0)
        else:
            return "Error: No valid SQL query found in the response."
    else:
        return f"Error: Unable to generate SQL query. Status code: {response.status_code}"





def test_sql_query(sql_query, max_rows=10):
    try:
        # Connect to the database
        with psycopg2.connect(**db_params) as conn:
            with conn.cursor() as cur:
                # Execute the query
                cur.execute(sql_query)
                
                # Fetch column names
                column_names = [desc[0] for desc in cur.description]
                
                # Fetch results (limit to max_rows)
                results = cur.fetchmany(max_rows)
                
                # Prepare the result dictionary
                result_dict = {
                    "success": True,
                    "column_names": column_names,
                    "results": results,
                    "row_count": cur.rowcount,
                    "truncated": cur.rowcount > max_rows
                }
                
                return result_dict

    except psycopg2.Error as e:
        # Handle database errors
        return {
            "success": False,
            "error_type": "DatabaseError",
            "error_message": str(e)
        }
    except Exception as e:
        # Handle other exceptions
        return {
            "success": False,
            "error_type": "GeneralError",
            "error_message": str(e)
        }






if __name__ == "__main__":
    test_queries = [
        "How many points does mcdavid have?"
    ]

    for query in test_queries:
        print(f"Original Query: {query}\n")
        
        expanded_query = expand_user_query(query)
        print(f"Expanded Query: {expanded_query}\n")
        
        intent_json = extract_intent(expanded_query)
        print(f"Extracted Intent: {intent_json}\n")
        
        processed_intent = process_intent(expanded_query, intent_json)
        print("Processed Intent:")
        print(json.dumps(processed_intent, indent=2))
        print()
        
        test_result = process_and_test_query(expanded_query, processed_intent)
        print("\n" + "-"*50 + "\n")
