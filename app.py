import streamlit as st
import requests
import time
import base64

# Title of the Streamlit App
st.title("MLOps Flow")

# Group inputs in a form for better organization
with st.form("mlops_form"):
    st.subheader("GitHub Configuration")
    # user_name = st.text_input("Git User Name")
    # user_email = st.text_input("Git Email")
    repo_owner = st.text_input("Repository Owner", placeholder="e.g., your-username")
    repo_name = st.text_input("Repository Name", placeholder="e.g., your-repo")
    branch_name = st.text_input("Branch Name", placeholder="e.g., feature_<your-branch-name>")
    github_token = st.text_input("GitHub Token", type="password", help="Personal Access Token (PAT) for GitHub")
    
    st.subheader("Upload Files")
    uploaded_model = st.file_uploader("Upload Model (.pkl format)", type=["pkl"])
    uploaded_dataset = st.file_uploader("Upload Dataset (.csv format)", type=["csv"])
    
    # Form submission button
    submit_button = st.form_submit_button("Submit & Upload")
    
    if submit_button:
        if not (repo_owner and repo_name and branch_name and github_token and uploaded_model and uploaded_dataset):
            st.error("Please fill in all required fields and upload both files.")
        else:
            st.success("All details provided. Ready to upload!")
            create_branch_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/actions/workflows/create-branch.yml/dispatches"

            # Prepare headers for GitHub API request
            headers = {
                "Authorization": f"token {github_token}",
                "Accept": "application/vnd.github.v3+json"
            }

            # First, trigger the create branch workflow
            create_branch_payload = {
                "ref": "main", # Reference branch to create the new branch from
                "inputs":{
                    "branch_name": branch_name
                }
            }

            # Send the POST request to trigger the create branch workflow
            response_create_branch = requests.post(create_branch_url, headers=headers, json=create_branch_payload)

            if response_create_branch.status_code == 204:
                st.success(f"Branch '{branch_name} creation triggered. Waiting for branch creation to complete.")

                max_retries = 5
                retry_delay = 5 #seconds
                branch_exists = False

                for attempt in range(max_retries):

                    # Verify that the branch was created by checking the repo for the new branch
                    branch_check_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/git/refs/heads/{branch_name}"
                    branch_check_response = requests.get(branch_check_url, headers=headers)

                    if branch_check_response == 200:
                        branch_exists = True
                        st.stuccess(f"Branch '{branch_name}' was successfully created!")
                        break
                    else:
                        time.sleep(retry_delay)
                    
                if branch_exists:

                    # Encode model and dataset to base64 for the upload workflow
                    model_content_base64 = base64.b64encode(uploaded_model.read()).decode("utf-8")
                    dataset_content_base64 = base64.b64encode(uploaded_dataset.read()).decode("utf-8")

                    # GitHub API URL for triggering the upload files workflow
                    upload_files_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/actions/workflows/upload-files.yml/dispatches"

                    # Get model and dataset name
                    model_name = uploaded_model.name
                    dataset_name = uploaded_dataset.name

                    # Prepare payload for the upload files workflow
                    upload_files_payload = {
                        "ref": branch_name,
                        "inputs": {
                            "branch_name": branch_name,
                            "model_file": model_content_base64,
                            "dataset_file": dataset_content_base64,
                            "model_name": model_name,
                            "dataset_name": dataset_name
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
                    st.error(f"Failed to create branch! Status code: {response_create_branch.status_code}")
                    st.write(response_create_branch.json())
            else:
                st.error("Please fill out all the fields!")

