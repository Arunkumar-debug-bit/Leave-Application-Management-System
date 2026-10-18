LEAVE APPLICATION MANAGEMENT SYSTEM - LOCAL PROTOTYPE

RUN ON WINDOWS
1. Install Python 3 if it is not already installed.
2. Open Command Prompt in this folder.
3. Run:
   python -m venv venv
   venv\Scripts\activate
   pip install flask
   python app.py
4. Open http://127.0.0.1:5000

DEMO FLOW
1. Sign in as Student with a name and student ID (example: Arunkumar Prabhu / 44110932).
2. Apply for leave and submit.
3. Sign out.
4. Sign in as Faculty / Admin with any name and choose that role.
5. Approve or reject the request.
6. Sign out and sign in again as the same student ID to see status.

IMPORTANT
This is a local demonstration prototype using SQLite. Role selection is for demo only and is not secure production authentication. It is not deployed to AWS. Do not claim AWS deployment is complete until it has actually been deployed.
