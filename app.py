import streamlit as st
import requests,time
import json
import os
import base64
from github import Github
from github import InputGitTreeElement

# Title of the Streamlit App
st.title("MLOps Flow")

# Get input details from the user
repo_owner = st.text_input("GitHub Repo Owner")
repo_name = st.text_input("GitHub Repository Name")
branch_name = st.text_input("Branch Name")
github_token = st.text_input("GitHub Token", type="password")

# Upload model file (e.g., pickle file)
uploaded_model = st.file_uploader("Upload Model File (.pkl format)", type=["pkl"])
uploaded_dataset = st.file_uploader("Upload Dataset File (.csv format)", type=["csv"])


# Metrics input for tracking (key-value pairs)
# metrics = st.text_area("Metrics to Track (in JSON format)", "{ \"accuracy\": 0.95, \"f1_score\": 0.89 }")

# Custom inputs that can be passed to the workflow
# custom_inputs = st.text_area("Additional Custom Inputs (in JSON format)", "{ \"key\": \"value\" }")

# Button to trigger GitHub Actions
if st.button("Upload Model"):
    
    if repo_owner and repo_name and branch_name and github_token and uploaded_model and uploaded_dataset:

        # GitHub API URL for triggering the create branch workflow
        create_branch_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/actions/workflows/create-branch.yml/dispatches"
        

        # Prepare headers for GitHub API request
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }

        # First, trigger the create branch workflow
        create_branch_payload = {
            "ref": "main",  # Reference branch to create the new branch from
            "inputs": {
                "branch_name": branch_name
            }
        }

        # Send the POST request to trigger the create branch workflow
        response_create_branch = requests.post(create_branch_url, headers=headers, json=create_branch_payload)

        # Check response for branch creation
        if response_create_branch.status_code == 204:
            st.success(f"Branch '{branch_name}' creation triggered. Waiting for branch creation to complete...")

            # Retry mechanism to check if the branch exists
            max_retries = 5
            retry_delay = 5  # seconds
            branch_exists = False

            for attempt in range(max_retries):
                # Verify that the branch was created by checking the repo for the new branch
                branch_check_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/git/refs/heads/{branch_name}"
                branch_check_response = requests.get(branch_check_url, headers=headers)

                if branch_check_response.status_code == 200:
                    branch_exists = True
                    st.success(f"Branch '{branch_name}' was successfully created!")
                    break
                else:
                    # st.info(f"Branch '{branch_name}' not found. Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)

            if branch_exists:
                # Encode model and dataset to base64 for the upload workflow
                model_content_base64 = base64.b64encode(uploaded_model.read()).decode("utf-8")
                dataset_content_base64 = base64.b64encode(uploaded_dataset.read()).decode("utf-8")

                # GitHub API URL for triggering the upload files workflow
                upload_files_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/actions/workflows/upload-files.yml/dispatches"

                # Get model name
                # model_name = os.path.splitext(uploaded_model.name)[0]
                model_name = uploaded_model.name
                dataset_name = uploaded_dataset.name

                # Prepare payload for the upload files workflow
                upload_files_payload = {
                    "ref": branch_name,  # Reference the new branch
                    "inputs": {
                        "branch_name": branch_name,
                        "model_file": model_content_base64,
                        "dataset_file": dataset_content_base64,
                        "model_name" : model_name,
                        "dataset_name" : dataset_name
                    }
                }

                # Send the POST request to trigger the upload files workflow
                response_upload_files = requests.post(upload_files_url, headers=headers, json=upload_files_payload)

                # Check response for file uploads
                if response_upload_files.status_code == 204:
                    st.success(f"Files uploaded successfully to branch '{branch_name}'!")
                else:
                    st.error(f"Failed to upload files! Status code: {response_upload_files.status_code}")
                    st.write(response_upload_files.json())
            else:
                st.error(f"Branch '{branch_name}' was not found after multiple attempts! Please try again.")
        else:
            st.error(f"Failed to create branch! Status code: {response_create_branch.status_code}")
            st.write(response_create_branch.json())

    else:
        st.error("Please fill out all the fields!")