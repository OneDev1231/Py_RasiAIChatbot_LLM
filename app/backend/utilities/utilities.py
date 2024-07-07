from supabase import create_client, Client
from dotenv import load_dotenv

import os

load_dotenv()

# Initialize Supabase client
SUPABASE_PROJECT_URL = os.getenv("SUPABASE_PROJECT_URL")
SUPABASE_ANON_PUBLIC_KEY = os.getenv("SUPABASE_ANON_PUBLIC_KEY")
supabase: Client = create_client(SUPABASE_PROJECT_URL, SUPABASE_ANON_PUBLIC_KEY)

def verify_token(token: str):
    response = supabase.table("business_owner").select("id").execute()
    token_db = response.data
    token_ids = {token["id"] for token in token_db}
    if token not in token_ids:
        return False
    return True