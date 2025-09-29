#!/usr/bin/env python3
"""
Setup script for AI Commerce Search Engine
Panora AI Take-Home Exercise
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version.split()[0]} detected")
    return True

def create_directory_structure():
    """Create necessary directories."""
    directories = [
        "data",
        "src",
        "baml_src",
        "baml_client",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"📁 Created directory: {directory}")
    
    return True

def check_env_file():
    """Check if .env file exists and has required variables."""
    env_file = Path(".env")
    
    if not env_file.exists():
        print("⚠️  .env file not found. Please create it with your API keys:")
        print("   GEMINI_API_KEY=your_gemini_api_key")
        print("   PINECONE_API_KEY=your_pinecone_api_key")
        return False
    
    # Check for required environment variables
    with open(env_file, 'r') as f:
        content = f.read()
    
    required_vars = ['GEMINI_API_KEY', 'PINECONE_API_KEY']
    
    missing_vars = []
    for var in required_vars:
        if var not in content or f"{var}=your_" in content:
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Missing or incomplete environment variables: {', '.join(missing_vars)}")
        print("Please update your .env file with actual API keys")
        return False
    
    print("✅ Environment variables configured")
    return True

def install_dependencies():
    """Install Python dependencies."""
    print("\n📦 Installing dependencies...")
    
    # Install requirements
    success = run_command(
        "pip install -r requirements.txt",
        "Installing Python packages"
    )
    
    if not success:
        print("❌ Failed to install dependencies")
        return False
    
    return True

def initialize_baml():
    """Initialize BAML client."""
    print("\n🧠 Initializing BAML...")
    
    # Check if BAML is properly installed
    try:
        import baml_py
        print("✅ BAML Python package found")
    except ImportError:
        print("❌ BAML not found, installing...")
        success = run_command("pip install baml-py", "Installing BAML")
        if not success:
            return False
    
    # Check if BAML client already exists and works
    try:
        from baml_client import b
        print("✅ BAML client already exists and working")
        return True
    except ImportError:
        print("⚠️  BAML client not found, need to generate...")
    
    # Check if BAML CLI is available
    cli_available = run_command(
        "baml-cli --version",
        "Checking BAML CLI"
    )
    
    # Generate BAML client only if it doesn't exist
    if cli_available:
        print("🔄 Generating BAML client...")
        success = run_command(
            "baml-cli generate --from baml_src",
            "Generating BAML client with CLI"
        )
        
        # Fix the nested directory structure
        if success:
            print("🔧 Fixing directory structure...")
            run_command(
                "mkdir -p baml_client && mv baml_src/baml_client/baml_client/* baml_client/ 2>/dev/null || true && rm -rf baml_src/baml_client",
                "Moving BAML files to correct location"
            )
    else:
        print("⚠️  BAML CLI not found, trying Python module...")
        success = run_command(
            "python -c \"import baml_py; baml_py.generate_from_directory('baml_src')\"",
            "Generating BAML client with Python"
        )
    
    # Test if BAML client works now
    try:
        from baml_client import b
        print("✅ BAML client generated and working")
        return True
    except ImportError:
        print("❌ BAML client generation failed")
        return False

def test_connections():
    """Test API connections."""
    print("\n🔗 Testing API connections...")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Test Gemini API
    try:
        import google.generativeai as genai
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key and not api_key.startswith('your_'):
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            response = model.generate_content("Hello")
            print("✅ Gemini API connection successful")
        else:
            print("⚠️  Gemini API key not properly configured")
            return False
    except Exception as e:
        print(f"❌ Gemini API connection failed: {e}")
        return False
    
    # Test Pinecone API
    try:
        from pinecone import Pinecone
        api_key = os.getenv('PINECONE_API_KEY')
        if api_key and not api_key.startswith('your_'):
            pc = Pinecone(api_key=api_key)
            pc.list_indexes()
            print("✅ Pinecone API connection successful")
        else:
            print("⚠️  Pinecone API key not properly configured")
            return False
    except Exception as e:
        print(f"❌ Pinecone API connection failed: {e}")
        return False
    
    return True

def run_data_processing():
    """Run initial data processing."""
    print("\n📊 Processing Amazon dataset...")
    
    try:
        from src.data_processor import AmazonDataProcessor
        
        processor = AmazonDataProcessor(target_size=800)
        products = processor.load_and_filter_data()
        
        if products:
            success = processor.save_processed_data("data/processed_products.json")
            if success:
                print(f"✅ Processed {len(products)} products successfully")
                return True
        
        print("❌ Data processing failed")
        return False
        
    except Exception as e:
        print(f"❌ Data processing error: {e}")
        return False

def setup_vector_store():
    """Initialize vector store."""
    print("\n🔍 Setting up vector store...")
    
    try:
        from src.vector_store import setup_vector_store_from_data
        
        vector_store = setup_vector_store_from_data()
        stats = vector_store.get_index_stats()
        
        if stats.get('total_vector_count', 0) > 0:
            print(f"✅ Vector store setup with {stats['total_vector_count']} products")
            return True
        else:
            print("❌ Vector store setup failed")
            return False
            
    except Exception as e:
        print(f"❌ Vector store error: {e}")
        return False

def main():
    """Main setup function."""
    print("🚀 AI Commerce Search Engine Setup")
    print("=" * 50)
    
    # Step 1: Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Step 2: Create directory structure
    if not create_directory_structure():
        sys.exit(1)
    
    # Step 3: Check environment file
    if not check_env_file():
        print("\n⚠️  Please configure your .env file before continuing")
        sys.exit(1)
    
    # Step 4: Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Step 5: Initialize BAML
    if not initialize_baml():
        print("⚠️  BAML initialization failed, but continuing...")
    
    # Step 6: Test API connections
    if not test_connections():
        print("⚠️  API connections failed. Please check your API keys.")
        sys.exit(1)
    
    # Step 7: Process data
    process_data = input("\n🤔 Process Amazon dataset now? This may take a few minutes (y/n): ").lower() == 'y'
    
    if process_data:
        if not run_data_processing():
            print("⚠️  Data processing failed, but you can run it later from the Streamlit app")
        else:
            # Step 8: Setup vector store
            setup_vectors = input("\n🤔 Setup vector store now? (y/n): ").lower() == 'y'
            if setup_vectors:
                if not setup_vector_store():
                    print("⚠️  Vector store setup failed, but you can run it later from the Streamlit app")
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed!")
    print("\nNext steps:")
    print("1. Ensure your .env file has valid API keys")
    print("2. Run the application: streamlit run streamlit_app.py")
    print("3. If you skipped data processing, use the app's setup buttons")
    print("\n📚 For questions, refer to the README or documentation")

if __name__ == "__main__":
    main()