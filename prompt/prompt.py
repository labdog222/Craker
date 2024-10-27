SINGLE_FILE_PROMPT = """
User Request: {user_request}

File Details:
Filename: {filename}
Path: {path}
Relevant Information:
{file_details}
"""

MULTIPLE_FILE_PROMPT = """
User Request: {user_request}

Purpose: Extract relevant information from the following code files to address the user’s query.

Files Analyzed:
{files_report}
"""