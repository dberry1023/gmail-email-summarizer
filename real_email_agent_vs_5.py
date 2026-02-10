# ===============================================================
# To run this code, type the following command in your terminal:
#
# streamlit run real_email_agent_vs_5.py
#
#----------------------------------------------------------------


from dotenv import load_dotenv
from openai import OpenAI
import datetime
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
import streamlit as st


# Load environment variables from .env
load_dotenv()

# Initialize the OpenAI client
client = OpenAI()

# Gmail API scope
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def get_gmail_service():
    """Authenticate and return Gmail API service."""
    creds = None
    
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    token_path = os.path.join(script_dir, 'token.json')
    credentials_path = os.path.join(script_dir, 'credentials.json')
    
    # Token file stores user's access and refresh tokens
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    # If no valid credentials, let user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, SCOPES)  # Use full path
            creds = flow.run_local_server(port=0)
        # Save credentials for next run
        with open(token_path, 'w') as token:  # Use full path
            token.write(creds.to_json())
    
    return build('gmail', 'v1', credentials=creds)

def get_unread_emails(service, max_results=10):
    """Fetch unread emails from Gmail."""
    try:
        # Get unread messages from inbox
        results = service.users().messages().list(
            userId='me',
            q='is:unread',
            maxResults=max_results
        ).execute()
        
        messages = results.get('messages', [])
        emails = []
        
        for msg in messages:
            # Get full message details
            message = service.users().messages().get(
                userId='me',
                id=msg['id'],
                format='full'
            ).execute()
            
            # Extract headers
            headers = message['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
            
            # Extract body
            body = ''
            if 'parts' in message['payload']:
                for part in message['payload']['parts']:
                    if part['mimeType'] == 'text/plain':
                        body_data = part['body'].get('data', '')
                        if body_data:
                            body = base64.urlsafe_b64decode(body_data).decode('utf-8')
                            break
            else:
                body_data = message['payload']['body'].get('data', '')
                if body_data:
                    body = base64.urlsafe_b64decode(body_data).decode('utf-8')
            
            # Truncate long bodies
            if len(body) > 500:
                body = body[:500] + "..."
            
            emails.append({
                "from": sender,
                "subject": subject,
                "body": body if body else "No text content available"
            })
        
        return emails
    
    except HttpError as error:
        print(f'An error occurred: {error}')
        return []

def summarize_email(email):
    """Summarize a single email using OpenAI."""
    prompt = f"""
    Summarize this email briefly for a daily report:
    From: {email['from']}
    Subject: {email['subject']}
    Body: {email['body']}
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

def generate_daily_summary(emails):
    """Generate a summary report of all emails."""
    if not emails:
        return "No unread emails found."
    
    summaries = [summarize_email(e) for e in emails]
    date = datetime.date.today().strftime("%B %d, %Y")
    report = f"Email Summary Report — {date}\n\n"
    for i, summary in enumerate(summaries, 1):
        report += f"{i}. {summary}\n\n"
    return report


# Streamlit UI that allows users to click a button to generate the email summary report

st.title("Gmail Summary Dashboard")

# Create two columns for buttons
# Custom CSS for styling
st.markdown("""
    <style>
    /* Change app background to gray */
    .stApp {
        background-color: #D3D3D3;
    }
    
    /* Style all buttons to be navy blue with white text */
    .stButton > button {
        background-color: #000080;
        color: white;
        font-weight: bold;
        border: none;
        padding: 10px 24px;
        border-radius: 4px;
    }
    
    /* Hover effect for buttons */
    .stButton > button:hover {
        background-color: #000066;
        color: white;
    }
    
    /* Active/clicked state */
    .stButton > button:active {
        background-color: #00004d;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# ===========================================

st.info("""
📌 **How it works:**  
This application connects to your Gmail account, fetches unread emails, 
and uses AI to generate concise summaries. The report is automatically
saved as a text file with a timestamp.
        
Click the button below to create your personalized email summary report.
""")

# ==========================================


# Create two columns for buttons
col1, col2 = st.columns(2)

with col1:
    if st.button("Click Here to Generate Summary"):
        with st.spinner("Fetching emails..."):
            service = get_gmail_service()
            emails = get_unread_emails(service)
            report = generate_daily_summary(emails)
            
            # Save to file
            date_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"email_report_{date_str}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(report)
            
            # Display in Streamlit
            st.markdown(report)
            st.success(f"Report saved to {filename}")

with col2:
    if st.button("Exit Application"):
        st.markdown("""
        <script>
        window.close();
        </script>
        """, unsafe_allow_html=True)
        st.info("You can now close this browser tab or press Ctrl+C in the terminal to stop the server.")
        st.stop()