import streamlit as st

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
        if not (user_name and user_email and repo_owner and repo_name and branch_name and github_token and uploaded_model and uploaded_dataset):
            st.error("Please fill in all required fields and upload both files.")
        else:
            st.success("All details provided. Ready to upload!")
            create_branch_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/actions/workflows/create-branch.yml/dispatches"
