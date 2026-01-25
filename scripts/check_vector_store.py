"""Check vector store and optionally migrate embeddings."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from langchain_chroma import Chroma
from src.services.embeddings import get_embedding_service
from src.config import get_settings


def check_vector_store():
    """Check if vector store exists and is accessible."""
    settings = get_settings()
    
    print("🔍 Checking vector store...")
    print(f"📁 Vector store path: {settings.vector_store_path}")
    
    # Check if directory exists
    if not settings.vector_store_dir.exists():
        print("❌ Vector store directory does not exist!")
        print(f"   Create it at: {settings.vector_store_dir}")
        return False
    
    try:
        # Initialize embedding service
        print("\n📊 Initializing embedding service...")
        embedding_service = get_embedding_service()
        print(f"✅ Embedding service ready ({embedding_service.model_name}, {embedding_service.dimensions}D)")
        
        # Try to load vector store
        print("\n📚 Loading vector store...")
        vector_store = Chroma(
            persist_directory=str(settings.vector_store_path),
            embedding_function=embedding_service.embeddings
        )
        
        # Get collection info
        collection = vector_store._collection
        count = collection.count()
        
        print(f"✅ Vector store loaded successfully")
        print(f"📖 Total documents: {count}")
        
        if count > 0:
            # Test a simple query
            print("\n🧪 Testing similarity search...")
            results = vector_store.similarity_search("book about adventure", k=3)
            print(f"✅ Search successful, found {len(results)} results")
            
            if results:
                print("\n📋 Sample result:")
                print(f"   Content preview: {results[0].page_content[:100]}...")
        else:
            print("\n⚠️  Vector store is empty!")
            print("   You need to add documents to the vector store.")
            print("   Run the notebooks to process your books data.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error checking vector store: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure OPENAI_API_KEY is set in .env")
        print("2. Run notebooks to generate vector store")
        print("3. Check vector_store/ directory has data")
        return False


def check_books_data():
    """Check if books CSV exists."""
    print("\n\n🔍 Checking books data...")
    
    books_path = Path("data/books_with_emotions.csv")
    
    if not books_path.exists():
        print(f"❌ Books data not found at: {books_path}")
        print("\nYou need to:")
        print("1. Download the dataset from Kaggle")
        print("2. Run the data processing notebooks")
        print("3. Generate books_with_emotions.csv")
        return False
    
    try:
        import pandas as pd
        books = pd.read_csv(books_path)
        print(f"✅ Books data loaded")
        print(f"📖 Total books: {len(books)}")
        print(f"📊 Columns: {', '.join(books.columns[:5])}...")
        return True
    except Exception as e:
        print(f"❌ Error loading books data: {e}")
        return False


def main():
    """Main function."""
    print("=" * 70)
    print("  Semantic Book Recommender - Vector Store Check")
    print("=" * 70)
    
    vector_store_ok = check_vector_store()
    books_data_ok = check_books_data()
    
    print("\n" + "=" * 70)
    print("  Summary")
    print("=" * 70)
    
    if vector_store_ok and books_data_ok:
        print("✅ Everything looks good!")
        print("   You can run the application with: uv run gradio_dashboard.py")
    else:
        print("⚠️  Some issues need to be resolved:")
        if not vector_store_ok:
            print("   ❌ Vector store needs attention")
        if not books_data_ok:
            print("   ❌ Books data needs to be prepared")
        
        print("\nNext steps:")
        print("1. Download dataset: https://www.kaggle.com/datasets/dylanjcastillo/7k-books-with-metadata")
        print("2. Run notebooks in order:")
        print("   - data_exploration.ipynb")
        print("   - text_classification.ipynb")
        print("   - sentiment_analysis.ipynb")
        print("   - vector_search.ipynb")


if __name__ == "__main__":
    main()