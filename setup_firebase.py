"""
Script untuk setup Firebase credentials
Jalankan script ini untuk membantu setup Firebase
"""
import os
import json

def setup_firebase():
    print("🔥 Firebase Setup Helper")
    print("=" * 50)
    
    config_dir = "config"
    credentials_path = os.path.join(config_dir, "firebase-credentials.json")
    
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
        print(f"✅ Created {config_dir} directory")
    
    if os.path.exists(credentials_path):
        print(f"✅ Firebase credentials already exist at {credentials_path}")
        
        # Validate credentials file
        try:
            with open(credentials_path, 'r') as f:
                creds = json.load(f)
                
            required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email']
            missing_fields = [field for field in required_fields if field not in creds]
            
            if missing_fields:
                print(f"❌ Missing required fields in credentials: {missing_fields}")
                return False
            
            print(f"✅ Credentials file is valid")
            print(f"📋 Project ID: {creds.get('project_id')}")
            
            # Update .env file with project ID
            update_env_file(creds.get('project_id'))
            
            return True
            
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON in credentials file")
            return False
    else:
        print(f"❌ Firebase credentials not found at {credentials_path}")
        print("\n📝 To setup Firebase:")
        print("1. Go to Firebase Console (https://console.firebase.google.com/)")
        print("2. Select your project")
        print("3. Go to Project Settings > Service Accounts")
        print("4. Click 'Generate new private key'")
        print("5. Download the JSON file")
        print(f"6. Save it as {credentials_path}")
        print("7. Run this script again")
        return False

def update_env_file(project_id):
    """Update .env file with Firebase project ID"""
    env_path = ".env"
    
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            lines = f.readlines()
        
        # Update FIREBASE_PROJECT_ID
        updated = False
        for i, line in enumerate(lines):
            if line.startswith('FIREBASE_PROJECT_ID='):
                lines[i] = f'FIREBASE_PROJECT_ID={project_id}\n'
                updated = True
                break
        
        if updated:
            with open(env_path, 'w') as f:
                f.writelines(lines)
            print(f"✅ Updated .env file with project ID: {project_id}")
        else:
            print(f"⚠️ FIREBASE_PROJECT_ID not found in .env file")
    else:
        print(f"⚠️ .env file not found")

if __name__ == "__main__":
    setup_firebase()