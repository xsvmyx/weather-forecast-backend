from supabase import  create_client, Client
import os
import dotenv

dotenv.load_dotenv()

SUPABASE_URL: str = os.getenv("SUPABASE_URL")
SUPABASE_KEY: str = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

if Client is None:
    raise ValueError("Supabase client could not be created. Check your SUPABASE_URL and SUPABASE_KEY.")
else:
    print("Supabase client created successfully.")