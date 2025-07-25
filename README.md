📥 Data Ingestion — Project Raseed
1. Gmail API Setup
    To enable data ingestion via Gmail, follow these steps:
    
    Create a Google Cloud Project
    Visit Google Cloud Console and create a new project.
    
    Enable Gmail API
    In the APIs & Services > Library, search for and enable the Gmail API.
    
    Configure OAuth Consent Screen
    
    Go to APIs & Services > OAuth consent screen
    
    Choose "External" or "Internal" based on your use case
    
    Add the following scope:
      https://www.googleapis.com/auth/gmail.readonly
      
    Create OAuth 2.0 Credentials
      Navigate to APIs & Services > Credentials
      Click Create Credentials > OAuth client ID
      Choose Web Application
      Add redirect URIs
      
    Download credentials.json
    Place it in your project root directory




