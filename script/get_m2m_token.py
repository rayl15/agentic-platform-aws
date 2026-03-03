# script/get_m2m_token.py
import os
import argparse
import sys
import requests
import json
import boto3
from botocore.exceptions import ClientError

def get_secret_from_arn(secret_arn):
    """Get secret value from AWS Secrets Manager using secret ARN"""
    try:
        session = boto3.session.Session()
        client = session.client('secretsmanager')
        response = client.get_secret_value(SecretId=secret_arn)
        secret_string = response['SecretString']
        return json.loads(secret_string)
    except ClientError as e:
        print(f"Error retrieving secret: {str(e)}")
        sys.exit(1)

def get_m2m_token(client_id=None, client_secret=None, scopes=None, token_url=None, secret_arn=None, export_env=False):
    """Get Cognito M2M token using OAuth 2.0 client credentials flow"""
    # If secret ARN is provided, get values from Secrets Manager
    if secret_arn:
        print(f"Retrieving credentials from secret: {secret_arn}")
        secret_data = get_secret_from_arn(secret_arn)
        client_id = client_id or secret_data.get('client_id')
        client_secret = client_secret or secret_data.get('client_secret')
        token_url = token_url or secret_data.get('token_url')
        scopes = scopes or secret_data.get('scopes')
        
        # Export to environment variables if requested
        if export_env:
            os.environ["COGNITO_M2M_CLIENT_ID"] = client_id
            os.environ["COGNITO_M2M_CLIENT_SECRET"] = client_secret
            os.environ["COGNITO_TOKEN_URL"] = token_url
            os.environ["COGNITO_M2M_SCOPES"] = scopes
            print("Credentials exported to environment variables:")
            print("  COGNITO_M2M_CLIENT_ID")
            print("  COGNITO_M2M_CLIENT_SECRET")
            print("  COGNITO_TOKEN_URL")
            print("  COGNITO_M2M_SCOPES")
    
    # Use environment variables as fallback
    client_id = client_id or os.environ.get("COGNITO_M2M_CLIENT_ID")
    client_secret = client_secret or os.environ.get("COGNITO_M2M_CLIENT_SECRET")
    token_url = token_url or os.environ.get("COGNITO_TOKEN_URL")
    
    # If no scopes provided, get from env or use defaults
    if not scopes:
        scope_env = os.environ.get("COGNITO_M2M_SCOPES")
        if scope_env:
            scopes = scope_env
        else:
            # Default scope (this should be configured in your Cognito resource server)
            scopes = "api/read api/write"
    
    # Check if we have all required values
    if not all([client_id, client_secret, token_url]):
        missing = []
        if not client_id: missing.append("--client-id or COGNITO_M2M_CLIENT_ID")
        if not client_secret: missing.append("--client-secret or COGNITO_M2M_CLIENT_SECRET")
        if not token_url: missing.append("--token-url or COGNITO_TOKEN_URL")
        
        print(f"Error: Missing required credentials: {', '.join(missing)}")
        print("Please provide them as arguments, environment variables, or via --secret-arn")
        sys.exit(1)
    
    try:
        # Debug info
        print(f"Making request to: {token_url}")
        print(f"Client ID: {client_id}")
        print(f"Scopes: {scopes}")
        
        # Debug the actual request details
        print("\n--- DETAILED REQUEST INFORMATION ---")
        print(f"Token URL: {token_url}")
        print(f"Headers: {{'Content-Type': 'application/x-www-form-urlencoded'}}")
        print("Request Body:")
        print(f"  grant_type: client_credentials")
        print(f"  client_id: {client_id}")
        print(f"  client_secret: {client_secret[:4]}...{client_secret[-4:] if len(client_secret) > 8 else '****'}")
        print(f"  scope: {scopes}")
        print("--- END REQUEST INFORMATION ---\n")
        
        # Make the token request using OAuth 2.0 client credentials flow
        response = requests.post(
            token_url,
            data={
                'grant_type': 'client_credentials',
                'client_id': client_id,
                'client_secret': client_secret,
                'scope': scopes
            },
            headers={
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            timeout=10.0  # Add a reasonable timeout (in seconds)
        )
        
        # Check for errors
        if response.status_code != 200:
            print(f"\n--- ERROR DETAILS ---")
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            print(f"Response Body: {response.text}")
            print("--- END ERROR DETAILS ---\n")
            sys.exit(1)
            
        token_data = response.json()
        
        # Extract the access token
        token = token_data['access_token']
        
        # Print info
        print("\nM2M Access Token (for Authorization: Bearer):")
        print(f"Bearer {token}")
        
        print("\nToken Details:")
        print(f"Expires in: {token_data.get('expires_in', 'unknown')} seconds")
        print(f"Scopes: {token_data.get('scope', 'unknown')}")
        
        print("\nCurl example:")
        print(f'curl -H "Authorization: Bearer {token}" https://your-api-endpoint/resource')
        
        return token
        
    except Exception as e:
        print(f"Error getting M2M token: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    # Add command line arguments
    parser = argparse.ArgumentParser(description='Get Cognito M2M token using OAuth 2.0 client credentials flow')
    parser.add_argument('--client-id', help='Cognito app client ID')
    parser.add_argument('--client-secret', help='Cognito app client secret')
    parser.add_argument('--scopes', help='Space-separated list of scopes to request (e.g., "api/read api/write")')
    parser.add_argument('--token-url', help='Complete OAuth2 token endpoint URL')
    parser.add_argument('--secret-arn', help='ARN of the AWS Secrets Manager secret containing M2M credentials')
    parser.add_argument('--export-env', action='store_true', help='Export credentials to environment variables')
    parser.add_argument('--quiet', action='store_true', help='Only output the token')
    
    args = parser.parse_args()
    
    # Get token
    token = get_m2m_token(
        args.client_id, 
        args.client_secret, 
        args.scopes,
        args.token_url,
        args.secret_arn,
        args.export_env
    )
    
    # If quiet mode, just print the token
    if args.quiet:
        print(token)