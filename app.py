import streamlit as st

# Title of the Streamlit App
st.title("MLOps Flow")

# Get input details from the user
repo_owner = st.text_input("GitHub Repository Owner")
repo_name = st.text_input("GitHub Repository Name")
branch_name = st.text_input("Branch Name")
github_token = st.text_input("GitHub Token", type="password")

# Upload model file (e.g., pickle file)
uploaded_model = st.file_uploader("Upload Model (.pkl format)", type=["pkl"])
uploaded_dataset = st.file_uploader("Upload Dataset (.csv format)", type=["csv"])

if st.button("Upload Model"):
    
    if repo_owner and repo_name and branch_name and github_token and uploaded_model and uploaded_dataset:

        create_branch_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/actions/workflows/create-branch.yml/dispatches"
        