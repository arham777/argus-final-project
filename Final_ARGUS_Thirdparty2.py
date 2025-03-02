import os
import requests
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from urllib.parse import quote
from ragas import EvaluationDataset, evaluate
from ragas.metrics import LLMContextRecall, Faithfulness, FactualCorrectness
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Load environment variables
load_dotenv()

# Third-Party RAG API Endpoint
# BASE_RAG_ENDPOINT = "http://10.229.222.15:8000/knowledgebase"

# def query_rag(prompt):
#     """Send a request to the third-party RAG system and return the response."""
#     try:
#         encoded_query = quote(prompt)  # URL encode the query
#         full_url = f"{BASE_RAG_ENDPOINT}/{encoded_query}"  # Include query in path
#         headers = {"accept": "application/json"}  # Ensure correct headers

#         response = requests.get(full_url, headers=headers)
#         response.raise_for_status()  # Raise error if status is 4xx/5xx

#         # Try to parse JSON
#         try:
#             data = response.json()
#             if isinstance(data, dict) and "answer" in data:
#                 return data["answer"]  # Return the actual answer
#             else:
#                 return f"Unexpected API Response: {data}"  # Handle cases where 'answer' is missing
#         except ValueError:  # JSON parsing fails
#             return f"Invalid JSON Response: {response.text}"  

#     except requests.exceptions.RequestException as e:
#         return f"Error: {e}"  # Handle network/API errors

# Correct API Endpoint
BASE_RAG_ENDPOINT = "http://10.229.222.15:8000/knowledgebase"
DEFAULT_GROUP_ID = 12
DEFAULT_SESSION_ID = 111

def query_rag(prompt, group_id=DEFAULT_GROUP_ID, session_id=DEFAULT_SESSION_ID):
    """Send a request to the third-party RAG system with the correct query format."""
    try:
        # Create session with retry strategy
        session = requests.Session()
        retry_strategy = Retry(
            total=3,  # number of retries
            backoff_factor=1,  # wait 1, 2, 4 seconds between retries
            status_forcelist=[500, 502, 503, 504]  # retry on these status codes
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        headers = {"accept": "application/json"}
        params = {
            "groupid": group_id,
            "query": prompt,
            "session_id": session_id
        }

        # Make the GET request with timeout
        response = session.get(
            BASE_RAG_ENDPOINT, 
            params=params, 
            headers=headers,
            timeout=(5, 10)  # (connect timeout, read timeout)
        )
        response.raise_for_status()

        print(f"DEBUG: API Request URL: {response.url}")
        print(f"DEBUG: Raw API Response for '{prompt}':\n{response.text}")

        try:
            data = response.json()
            if isinstance(data, dict) and "answer" in data:
                return data["answer"]
            else:
                return f"Unexpected API Response: {data}"
        except ValueError:
            return f"Invalid JSON Response: {response.text}"

    except requests.exceptions.Timeout:
        return "Error: Request timed out. The server is taking too long to respond."
    except requests.exceptions.ConnectionError:
        return "Error: Unable to connect to the RAG server. Please verify the server address and port."
    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}"
    finally:
        session.close()

# Sample Queries and Expected Responses
sample_queries = [
    "Who introduced the theory of relativity?",
    "Who was the first computer programmer?",
    "What did Isaac Newton contribute to science?",
    "Who won two Nobel Prizes for research on radioactivity?",
    "What is the theory of evolution by natural selection?"
]

expected_responses = [
    "Albert Einstein proposed the theory of relativity, which transformed our understanding of time, space, and gravity.",
    "Ada Lovelace is regarded as the first computer programmer for her work on Charles Babbage's early mechanical computer, the Analytical Engine.",
    "Isaac Newton formulated the laws of motion and universal gravitation, laying the foundation for classical mechanics.",
    "Marie Curie was a physicist and chemist who conducted pioneering research on radioactivity and won two Nobel Prizes.",
    "Charles Darwin introduced the theory of evolution by natural selection in his book 'On the Origin of Species'."
]

# Collect Evaluation Data
dataset = []
for query, reference in zip(sample_queries, expected_responses):
    response = query_rag(query)
    
    # Ensure response is a string
    if not isinstance(response, str):
        response = str(response)
    
    # Create proper context format
    response_list = [response] if isinstance(response, str) else response

    dataset.append({
        "user_input": query,
        "retrieved_contexts": response_list,
        "response": response,
        "reference": reference
    })

# Convert dataset into EvaluationDataset
try:
    evaluation_dataset = EvaluationDataset.from_list(dataset)
except Exception as e:
    print(f"Error while creating EvaluationDataset: {e}")
    exit()

# Replace Ragas evaluation with simple metrics
def calculate_metrics(dataset):
    total = len(dataset)
    successful_responses = 0
    error_responses = 0
    
    for data in dataset:
        response = data["response"]
        if "Error:" in response or "Unexpected API Response:" in response:
            error_responses += 1
        else:
            successful_responses += 1
    
    metrics = {
        "Total Queries": total,
        "Successful Responses": successful_responses,
        "Error Responses": error_responses,
        "Success Rate": f"{(successful_responses/total)*100:.2f}%"
    }
    return metrics

# Evaluate Responses
try:
    metrics = calculate_metrics(dataset)
    print("\nEvaluation Results:")
    for metric, value in metrics.items():
        print(f"{metric}: {value}")
except Exception as e:
    print(f"Error during evaluation: {e}")

# Generate an HTML Report
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RAG Evaluation Results</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; padding: 20px; background-color: #f4f4f4; }
        h2 { text-align: center; }
        table { width: 100%; border-collapse: collapse; background: white; box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1); }
        th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
        th { background-color: #007bff; color: white; }
        tr:nth-child(even) { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <h2>RAG Evaluation Results</h2>
    <table>
        <tr>
            <th>User Query</th>
            <th>Generated Response</th>
            <th>Reference Answer</th>
        </tr>
"""

# Populate Table Rows
for data in dataset:
    html_content += f"""
        <tr>
            <td>{data["user_input"]}</td>
            <td>{data["response"]}</td>
            <td>{data["reference"]}</td>
        </tr>
    """

# Close HTML Tags
html_content += """
    </table>
</body>
</html>
"""

# Write HTML to File
output_file = "rag_evaluation_results.html"
with open(output_file, "w", encoding="utf-8") as file:
    file.write(html_content)

print(f"HTML file has been generated: {output_file}")