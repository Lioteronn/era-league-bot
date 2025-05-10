import os
from dotenv import load_dotenv

load_dotenv()

# Supabase Configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# Database Configuration
DATABASE_URL = os.getenv('DATABASE_URL')

# Discord Bot Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Logo download path
LOGO_PATH = os.getenv('LOGO_PATH')
