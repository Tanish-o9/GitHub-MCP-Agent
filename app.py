import asyncio
import os
import streamlit as st
from github_agent import run_github_agent

st.set_page_config(page_title="🐙 GitHub MCP Agent", page_icon="🐙", layout="wide")

st.markdown("<h1 class='main-header'>🐙 GitHub MCP Agent</h1>", unsafe_allow_html=True)
st.markdown("Explore GitHub repositories with natural language using the Model Context Protocol")

with st.sidebar:
    st.header("🔑 Authentication")
    
    env_openai_key = os.getenv("OPENAI_API_KEY", "")
    openai_key_input = st.text_input(
        "OpenAI API Key", 
        value=env_openai_key,
        type="password",
        help="Required for the AI agent to interpret queries and format results"
    )
    if openai_key_input:
        os.environ["OPENAI_API_KEY"] = openai_key_input
        openai_key = openai_key_input
    else:
        openai_key = env_openai_key
    
    env_github_token = os.getenv("GITHUB_TOKEN", "")
    github_token_input = st.text_input(
        "GitHub Token", 
        value=env_github_token,
        type="password", 
        help="Create a token with repo scope at github.com/settings/tokens"
    )
    if github_token_input:
        os.environ["GITHUB_TOKEN"] = github_token_input
        github_token = github_token_input
    else:
        github_token = env_github_token

    st.markdown("---")
    st.header("⚙️ MCP Server Config")
    server_runner = st.selectbox(
        "Server Runner",
        ["npx (Node.js)", "Docker"],
        index=0,
        help="Choose 'npx' if Docker Desktop is not running"
    )
    
    st.markdown("---")
    st.markdown("### Example Queries")
    
    st.markdown("**Issues**")
    st.markdown("- Show me issues by label")
    st.markdown("- What issues are being actively discussed?")
    
    st.markdown("**Pull Requests**")
    st.markdown("- What PRs need review?")
    st.markdown("- Show me recent merged PRs")
    
    st.markdown("**Repository**")
    st.markdown("- Show repository health metrics")
    st.markdown("- Show repository activity patterns")
    
    st.markdown("---")
    st.caption("Note: Always specify the repository in your query if not already selected in the main input.")

col1, col2 = st.columns([3, 1])
with col1:
    repo = st.text_input("Repository", value="Tanish-o9/GitHub-MCP-Agent", help="Format: owner/repo")
with col2:
    query_type = st.selectbox("Query Type", [
        "Issues", "Pull Requests", "Repository Activity", "Custom"
    ])

if query_type == "Issues":
    query_template = f"Find issues labeled as bugs in {repo}"
elif query_type == "Pull Requests":
    query_template = f"Show me recent merged PRs in {repo}"
elif query_type == "Repository Activity":
    query_template = f"Analyze code quality trends in {repo}"
else:
    query_template = ""

query = st.text_area(
    "Your Query", 
    value=query_template, 
    placeholder="What would you like to know about this repository?"
)

if st.button("🚀 Run Query", type="primary", use_container_width=True):
    if not openai_key:
        st.error("Please enter your OpenAI API key in the sidebar")
    elif not github_token:
        st.error("Please enter your GitHub token in the sidebar")
    elif not query:
        st.error("Please enter a query")
    else:
        with st.spinner("Analyzing GitHub repository..."):
            if repo and repo not in query:
                full_query = f"{query} in {repo}"
            else:
                full_query = query
                
            result = asyncio.run(run_github_agent(full_query, runner_type=server_runner))
        
        st.markdown("### Results")
        st.markdown(result)

if 'result' not in locals():
    st.markdown(
        """<div class='info-box'>
        <h4>How to use this app:</h4>
        <ol>
            <li>Enter your <strong>OpenAI API key</strong> in the sidebar (powers the AI agent)</li>
            <li>Enter your <strong>GitHub token</strong> in the sidebar</li>
            <li>Select your preferred MCP Server Runner (Node.js/npx or Docker)</li>
            <li>Specify a repository (e.g., Tanish-o9/GitHub-MCP-Agent)</li>
            <li>Select a query type or write your own</li>
            <li>Click 'Run Query' to see results</li>
        </ol>
        <p><strong>How it works:</strong></p>
        <ul>
            <li>Uses the official GitHub MCP server (via npx or Docker) for real-time access to GitHub API</li>
            <li>AI Agent (powered by OpenAI) interprets your queries and calls appropriate GitHub APIs</li>
            <li>Results are formatted in readable markdown with insights and links</li>
            <li>Queries work best when focused on specific aspects like issues, PRs, or repository info</li>
        </ul>
        </div>""", 
        unsafe_allow_html=True
    )
