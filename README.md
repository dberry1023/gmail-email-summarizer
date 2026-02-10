# Gmail Email Summarizer

An AI-powered email summarization tool that connects to Gmail, fetches unread emails, and generates concise summaries using OpenAI's GPT models.

## Features

- 📧 Fetches unread Gmail messages
- 🤖 Uses OpenAI GPT-4o-mini for intelligent summaries
- 💾 Automatically saves reports with timestamps
- 🎨 Clean Streamlit web interface with custom styling
- 📊 Easy-to-read formatted reports

## Prerequisites

- Python 3.8+
- Gmail API credentials
- OpenAI API key

## Installation

1. Clone this repository:
```bash
git clone https://github.com/dberry1023/gmail-email-summarizer.git
cd gmail-email-summarizer
```

2. Install required packages:
```bash
pip install python-dotenv openai google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client streamlit
```

3. Set up your credentials:
   - Create a `.env` file with your OpenAI API key:
```
     OPENAI_API_KEY=your_api_key_here
```
   - Download your Gmail API credentials and save as `credentials.json`

## Usage

Run the Streamlit application:
```bash
streamlit run real_email_agent_vs_5.py
```

## How It Works

1. Authenticates with Gmail using OAuth 2.0
2. Fetches up to 10 unread emails from your inbox
3. Sends each email to OpenAI for summarization
4. Displays summaries in a web interface
5. Saves report as timestamped text file

## Security Notes

⚠️ This repository does not include:
- Gmail API credentials (`credentials.json`, `token.json`)
- OpenAI API keys (`.env` file)
- Generated email reports

These files are excluded via `.gitignore` for security.

## Author

**Daryl Berry**
- GitHub: [@dberry1023](https://github.com/dberry1023)
- LinkedIn: [dberry1023](https://linkedin.com/in/dberry1023)

## License

MIT License
```

