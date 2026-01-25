"""Gradio web application for the book recommender."""

import logging
from typing import List, Tuple

import gradio as gr

from src.config import get_settings
from src.services import (
    get_recommendation_service,
    get_user_service,
    Book
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize services
try:
    settings = get_settings()
    recommendation_service = get_recommendation_service()
    user_service = get_user_service()
    
    # Get or create default user (returns user_id)
    default_user_id = user_service.get_or_create_user("default")
    logger.info(f"Initialized services with user_id: {default_user_id}")
    
except Exception as e:
    logger.error(f"Failed to initialize services: {e}")
    raise


def format_book_result(book: Book) -> Tuple[str, str]:
    """Format a book for display in the gallery.
    
    Args:
        book: Book object
    
    Returns:
        Tuple of (image_url, caption)
    """
    truncated_desc = book.truncate_description(max_words=30)
    formatted_authors = book.format_authors()
    caption = f"{book.title} by {formatted_authors}: {truncated_desc}"
    return (book.thumbnail, caption)


def recommend_books(
    query: str,
    category: str = "All",
    tone: str = "All"
) -> List[Tuple[str, str]]:
    """Get book recommendations based on query and filters.
    
    Args:
        query: Search query
        category: Category filter
        tone: Emotional tone filter
    
    Returns:
        List of (image_url, caption) tuples for gallery
    """
    try:
        logger.info(f"Search request: query='{query}', category={category}, tone={tone}")
        
        # Validate query
        if not query or not query.strip():
            logger.warning("Empty query received")
            return []
        
        # Get recommendations
        recommendations = recommendation_service.search(
            query=query.strip(),
            category=category,
            tone=tone
        )
        
        # Save to search history
        try:
            user_service.save_search(
                user_id=default_user_id,
                query=query.strip(),
                category=category,
                tone=tone,
                results_count=len(recommendations)
            )
        except Exception as e:
            logger.warning(f"Failed to save search history: {e}")
        
        # Format results for display
        results = [format_book_result(book) for book in recommendations]
        
        logger.info(f"Returning {len(results)} recommendations")
        return results
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        # Return empty list on error (Gradio will show empty gallery)
        return []


def get_cache_stats() -> str:
    """Get cache statistics as formatted string.
    
    Returns:
        Formatted cache stats
    """
    try:
        stats = recommendation_service.get_cache_stats()
        return (
            f"Cache Stats:\n"
            f"- Entries: {stats['entries']}\n"
            f"- Hits: {stats['hits']}\n"
            f"- Misses: {stats['misses']}\n"
            f"- Hit Rate: {stats['hit_rate_percent']}%\n"
            f"- TTL: {stats['ttl_seconds']}s"
        )
    except Exception as e:
        return f"Error getting cache stats: {e}"


def get_user_stats_text() -> str:
    """Get user statistics as formatted string.
    
    Returns:
        Formatted user stats
    """
    try:
        stats = user_service.get_user_stats(default_user_id)
        return (
            f"User Stats:\n"
            f"- Username: {stats['username']}\n"
            f"- Total Searches: {stats['total_searches']}\n"
            f"- Favorites: {stats['total_favorites']}\n"
            f"- Member Since: {stats['member_since'][:10] if stats['member_since'] else 'N/A'}"
        )
    except Exception as e:
        return f"Error getting user stats: {e}"


def clear_cache_action() -> str:
    """Clear the cache.
    
    Returns:
        Status message
    """
    try:
        recommendation_service.clear_cache()
        return "✅ Cache cleared successfully!"
    except Exception as e:
        return f"❌ Error clearing cache: {e}"


# Build Gradio interface
def create_app() -> gr.Blocks:
    """Create the Gradio application.
    
    Returns:
        Gradio Blocks app
    """
    # Get available categories and tones
    categories = recommendation_service.get_categories()
    tones = recommendation_service.get_tones()
    
    with gr.Blocks(theme=gr.themes.Glass(), title="Semantic Book Recommender") as app:
        gr.Markdown("# 📚 Semantic Book Recommender")
        gr.Markdown(
            "Find your next great read using AI-powered semantic search. "
            "Describe what you're looking for, and we'll recommend books that match!"
        )
        
        with gr.Row():
            with gr.Column(scale=3):
                user_query = gr.Textbox(
                    label="What kind of book are you looking for?",
                    placeholder="e.g., A thrilling mystery with unexpected twists",
                    lines=2
                )
            
            with gr.Column(scale=1):
                category_dropdown = gr.Dropdown(
                    choices=categories,
                    label="Category",
                    value="All"
                )
            
            with gr.Column(scale=1):
                tone_dropdown = gr.Dropdown(
                    choices=tones,
                    label="Emotional Tone",
                    value="All"
                )
        
        with gr.Row():
            submit_button = gr.Button("🔍 Find Recommendations", variant="primary", scale=2)
            clear_button = gr.Button("🗑️ Clear Cache", scale=1)
        
        gr.Markdown("## 📖 Recommended Books")
        output = gr.Gallery(
            label="",
            columns=4,
            rows=4,
            height="auto",
            object_fit="contain"
        )
        
        # Info section
        with gr.Accordion("ℹ️ System Information", open=False):
            with gr.Row():
                with gr.Column():
                    cache_stats = gr.Textbox(
                        label="Cache Statistics",
                        value=get_cache_stats(),
                        interactive=False,
                        lines=5
                    )
                
                with gr.Column():
                    user_stats = gr.Textbox(
                        label="User Statistics",
                        value=get_user_stats_text(),
                        interactive=False,
                        lines=5
                    )
            
            refresh_stats = gr.Button("🔄 Refresh Stats")
            clear_result = gr.Textbox(label="Action Result", interactive=False)
        
        # Event handlers
        submit_button.click(
            fn=recommend_books,
            inputs=[user_query, category_dropdown, tone_dropdown],
            outputs=output
        )
        
        clear_button.click(
            fn=clear_cache_action,
            outputs=clear_result
        )
        
        refresh_stats.click(
            fn=get_cache_stats,
            outputs=cache_stats
        ).then(
            fn=get_user_stats_text,
            outputs=user_stats
        )
        
        # Footer
        gr.Markdown(
            "---\n"
            "💡 **Tips:**\n"
            "- Be specific in your descriptions for better results\n"
            "- Use filters to narrow down by category or emotional tone\n"
            "- Try different phrasings if you don't find what you're looking for\n"
        )
    
    return app


# Create the app
dashboard = create_app()


if __name__ == "__main__":
    logger.info("Starting Semantic Book Recommender...")
    dashboard.launch(
        server_name=settings.gradio_server_name,
        server_port=settings.gradio_server_port,
        share=settings.gradio_share
    )