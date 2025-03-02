import streamlit as st
import pandas as pd
import requests
from ragas import EvaluationDataset, evaluate
from ragas.metrics import LLMContextRecall, Faithfulness, FactualCorrectness

# Define a function to run the evaluation (this would integrate your existing code)
def run_evaluation():
    # Sample queries and expected responses
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

    # Function to query the RAG API (assuming it's defined similarly to your code)
    def query_rag(prompt, group_id=12, session_id=111):
        BASE_RAG_ENDPOINT = "http://10.229.222.15:8000/knowledgebase"
        headers = {"accept": "application/json"}
        params = {"groupid": group_id, "query": prompt, "session_id": session_id}
        try:
            response = requests.get(BASE_RAG_ENDPOINT, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            if isinstance(data, dict) and "answer" in data:
                return data["answer"]
            else:
                return f"Unexpected API Response: {data}"
        except Exception as e:
            return f"Error: {e}"

    # Collect evaluation data
    dataset = []
    for query, reference in zip(sample_queries, expected_responses):
        response = query_rag(query)
        response_list = [response] if isinstance(response, str) else response
        dataset.append({
            "user_input": query,
            "retrieved_contexts": response_list,
            "response": response,
            "reference": reference
        })

    # Convert to EvaluationDataset and evaluate metrics
    try:
        evaluation_dataset = EvaluationDataset.from_list(dataset)
        result = evaluate(
            dataset=evaluation_dataset,
            metrics=[LLMContextRecall(), Faithfulness(), FactualCorrectness()],
            llm=None
        )
    except Exception as e:
        st.error(f"Error during evaluation: {e}")
        result = {}

    # Create a DataFrame for detailed results
    df_results = pd.DataFrame(dataset)
    return result, df_results

# Streamlit UI layout
st.title("RAG System Evaluation Dashboard")
st.write("This dashboard evaluates the performance of a RAG system against sample queries.")

if st.button("Run Evaluation"):
    with st.spinner("Running evaluation..."):
        metrics, results_df = run_evaluation()
        st.success("Evaluation complete!")

        # Display evaluation metrics
        st.subheader("Summary Metrics")
        if metrics:
            st.write(f"**Context Recall:** {metrics.get('Context Recall', 'N/A')}")
            st.write(f"**Faithfulness:** {metrics.get('Faithfulness', 'N/A')}")
            st.write(f"**Factual Correctness:** {metrics.get('Factual Correctness', 'N/A')}")
        else:
            st.write("No metrics available.")

        # Display detailed results in a table
        st.subheader("Detailed Evaluation Results")
        st.dataframe(results_df)
else:
    st.write("Click the button above to run the evaluation.")
