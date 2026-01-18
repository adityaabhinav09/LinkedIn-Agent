"""
Setup script for LinkedIn AI Posting Agent.
Run this to initialize the project and verify configuration.
"""

import os
import sys
import shutil
from pathlib import Path

def setup():
    """Run project setup."""
    project_root = Path(__file__).parent
    
    print("=" * 60)
    print("🚀 LinkedIn AI Posting Agent - Setup")
    print("=" * 60)
    
    # 1. Check Python version
    print("\n📌 Checking Python version...")
    if sys.version_info < (3, 9):
        print(f"❌ Python 3.9+ required. You have {sys.version}")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
    
    # 2. Create .env file if not exists
    env_file = project_root / ".env"
    env_example = project_root / ".env.example"
    
    if not env_file.exists():
        print("\n📌 Creating .env file...")
        if env_example.exists():
            shutil.copy(env_example, env_file)
            print("✅ Created .env from .env.example")
            print("⚠️  Please edit .env and add your API keys!")
        else:
            print("❌ .env.example not found")
    else:
        print("\n✅ .env file exists")
    
    # 3. Create data directory
    data_dir = project_root / "data"
    print("\n📌 Checking data directory...")
    data_dir.mkdir(exist_ok=True)
    print(f"✅ Data directory: {data_dir}")
    
    # 4. Check for required files
    print("\n📌 Checking required files...")
    required_files = [
        "data/curriculum.json",
        "data/posted_history.json",
        "data/agent_state.json",
        "config/settings.py",
        "src/agent.py",
        "main.py"
    ]
    
    all_present = True
    for file in required_files:
        path = project_root / file
        if path.exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - MISSING")
            all_present = False
    
    # 5. Install dependencies prompt
    print("\n" + "=" * 60)
    print("📦 NEXT STEPS:")
    print("=" * 60)
    print("""
1. Install dependencies:
   pip install -r requirements.txt

2. Configure your .env file with:
   - OPENAI_API_KEY: Get from https://platform.openai.com/api-keys
   - LINKEDIN_ACCESS_TOKEN: Get from LinkedIn Developer Portal
   - LINKEDIN_PERSON_ID: Your LinkedIn URN

3. Run the agent:
   python main.py

4. Available commands:
   - generate: Preview today's post
   - post: Generate and post with approval
   - schedule: Start daily 10 AM posting
   - status: Check progress
   - help: See all commands
    """)
    
    return all_present


if __name__ == "__main__":
    success = setup()
    sys.exit(0 if success else 1)
