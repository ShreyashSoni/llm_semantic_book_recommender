"""Gradio web application for the book recommender with enhanced UI."""

import logging
from typing import List, Tuple, Optional
from datetime import datetime

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


# Global state for current search results
current_search_results: List[Book] = []


def format_book_for_gallery(book: Book, include_favorite_btn: bool = True) -> Tuple[str, str]:
    """Format a book for display in the gallery.
    
    Args:
        book: Book object
        include_favorite_btn: Whether to include favorite icon in caption
    
    Returns:
        Tuple of (image_url, caption)
    """
    truncated_desc = book.truncate_description(max_words=25)
    formatted_authors = book.format_authors()
    
    # Check if book is favorited
    is_fav = user_service.is_favorite(default_user_id, book.isbn13)
    fav_icon = "⭐" if is_fav else "☆"
    
    caption = f"**{book.title}**\n_{formatted_authors}_\n\n{truncated_desc}"
    
    if include_favorite_btn:
        caption = f"{fav_icon} {caption}"
    
    return (book.thumbnail, caption)


def format_book_details(book: Book) -> str:
    """Format detailed book information.
    
    Args:
        book: Book object
    
    Returns:
        Formatted HTML string with book details
    """
    is_fav = user_service.is_favorite(default_user_id, book.isbn13)
    fav_status = "⭐ Favorited" if is_fav else "Not favorited"
    
    # Emotion scores
    emotions = {
        "Joy": book.joy,
        "Surprise": book.surprise,
        "Anger": book.anger,
        "Fear": book.fear,
        "Sadness": book.sadness
    }
    emotion_str = ", ".join([f"{k}: {v:.2f}" for k, v in emotions.items()])
    
    html = f"""
    <div style="padding: 20px; border: 1px solid #ddd; border-radius: 10px; background-color: #f9f9f9;">
        <h2 style="margin-top: 0; color: #333;">{book.title}</h2>
        <p style="color: #555;"><strong>Authors:</strong> {book.format_authors()}</p>
        <p style="color: #555;"><strong>Category:</strong> {book.category}</p>
        <p style="color: #555;"><strong>ISBN-13:</strong> {book.isbn13}</p>
        <p style="color: #555;"><strong>Emotion Scores:</strong> {emotion_str}</p>
        <p style="color: #555;"><strong>Status:</strong> {fav_status}</p>
        <hr>
        <p style="color: #555;"><strong>Description:</strong></p>
        <p style="color: #333;">{book.description}</p>
    </div>
    """
    return html


def recommend_books(
    query: str,
    category: str = "All",
    tone: str = "All",
    progress=gr.Progress()
) -> Tuple[List[Tuple[str, str]], str]:
    """Get book recommendations based on query and filters.
    
    Args:
        query: Search query
        category: Category filter
        tone: Emotional tone filter
        progress: Gradio progress tracker
    
    Returns:
        Tuple of (gallery items, status message)
    """
    global current_search_results
    
    try:
        # Validate query
        if not query or not query.strip():
            return [], "⚠️ Please enter a search query"
        
        progress(0.2, desc="Generating embedding...")
        logger.info(f"Search request: query='{query}', category={category}, tone={tone}")
        
        # Get recommendations
        progress(0.5, desc="Searching books...")
        recommendations = recommendation_service.search(
            query=query.strip(),
            category=category,
            tone=tone
        )
        
        # Store results globally for other functions
        current_search_results = recommendations
        
        # Save to search history
        progress(0.8, desc="Saving history...")
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
        progress(0.9, desc="Formatting results...")
        if not recommendations:
            return [], "❌ No books found. Try a different query or filters."
        
        results = [format_book_for_gallery(book) for book in recommendations]
        
        logger.info(f"Returning {len(results)} recommendations")
        status = f"✅ Found {len(results)} books!"
        
        progress(1.0, desc="Complete!")
        return results, status
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return [], f"❌ Error: {str(e)}"


def load_search_history() -> str:
    """Load and format search history.
    
    Returns:
        HTML with search history
    """
    try:
        history = user_service.get_search_history(default_user_id, limit=20)
        
        if not history:
            return """
            <div style="padding: 40px; text-align: center; color: #999;">
                <h3 style="color: #666;">No search history yet</h3>
                <p style="color: #888;">Your recent searches will appear here</p>
            </div>
            """
        
        html = "<div style='padding: 10px;'>"
        html += "<h3 style='color: #333;'>Recent Searches</h3>"
        html += "<table style='width: 100%; border-collapse: collapse;'>"
        html += "<tr style='background-color: #f0f0f0;'>"
        html += "<th style='padding: 10px; text-align: left; color: #333;'>Query</th>"
        html += "<th style='padding: 10px; text-align: left; color: #333;'>Filters</th>"
        html += "<th style='padding: 10px; text-align: left; color: #333;'>Results</th>"
        html += "<th style='padding: 10px; text-align: left; color: #333;'>Time</th>"
        html += "</tr>"
        
        for search in history:
            # Format timestamp
            time_str = search['created_at'].strftime("%Y-%m-%d %H:%M")
            
            # Format filters
            filters = []
            category_val = search.get('category')
            tone_val = search.get('tone')
            
            if category_val:
                filters.append(f"Category: {category_val}")
            if tone_val:
                filters.append(f"Tone: {tone_val}")
            filter_str = ", ".join(filters) if filters else "None"
            
            html += f"<tr style='border-bottom: 1px solid #ddd;'>"
            html += f"<td style='padding: 10px; color: #333;'><strong>{search['query']}</strong></td>"
            html += f"<td style='padding: 10px; color: #555;'>{filter_str}</td>"
            html += f"<td style='padding: 10px; color: #555;'>{search['results_count']}</td>"
            html += f"<td style='padding: 10px; color: #555;'>{time_str}</td>"
            html += "</tr>"
        
        html += "</table></div>"
        return html
        
    except Exception as e:
        logger.error(f"Error loading search history: {e}")
        return f"<p style='color: #d00;'>Error loading history: {e}</p>"


def load_favorites() -> Tuple[List[Tuple[str, str]], str]:
    """Load favorite books.
    
    Returns:
        Tuple of (gallery items, count message)
    """
    global current_search_results
    
    try:
        favorites = user_service.get_favorites(default_user_id, limit=50)
        
        if not favorites:
            return [], "No favorites yet. Add books from the Search tab!"
        
        # Get book details from the books dataframe
        books_df = recommendation_service.books
        
        # Get ISBNs from favorites
        favorite_isbns = [int(fav['book_isbn13']) for fav in favorites]
        
        # Filter books by ISBNs
        favorite_books_df = books_df[books_df['isbn13'].isin(favorite_isbns)]
        
        if favorite_books_df.empty:
            return [], f"Could not load favorite books ({len(favorites)} saved)"
        
        # Convert to Book objects
        books = [Book(row) for _, row in favorite_books_df.iterrows()]
        
        # Store in global state for detail viewing and removal
        current_search_results = books
        
        # Format for gallery
        results = [format_book_for_gallery(book, include_favorite_btn=True) for book in books]
        message = f"Showing {len(books)} favorite books"
        
        return results, message
        
    except Exception as e:
        logger.error(f"Error loading favorites: {e}")
        return [], f"Error loading favorites: {e}"


def get_cache_stats() -> str:
    """Get cache statistics as formatted string."""
    try:
        stats = recommendation_service.get_cache_stats()
        return (
            f"📊 **Cache Statistics**\n\n"
            f"- Entries: {stats['entries']}\n"
            f"- Hits: {stats['hits']}\n"
            f"- Misses: {stats['misses']}\n"
            f"- Hit Rate: {stats['hit_rate_percent']}%\n"
            f"- TTL: {stats['ttl_seconds']}s"
        )
    except Exception as e:
        return f"Error: {e}"


def get_user_stats_text() -> str:
    """Get user statistics as formatted string."""
    try:
        stats = user_service.get_user_stats(default_user_id)
        member_since = stats['member_since'][:10] if stats['member_since'] else 'N/A'
        
        return (
            f"👤 **User Statistics**\n\n"
            f"- Username: {stats['username']}\n"
            f"- Total Searches: {stats['total_searches']}\n"
            f"- Favorites: {stats['total_favorites']}\n"
            f"- Member Since: {member_since}"
        )
    except Exception as e:
        return f"Error: {e}"


def clear_cache_action() -> str:
    """Clear the cache."""
    try:
        recommendation_service.clear_cache()
        return "✅ Cache cleared successfully!"
    except Exception as e:
        return f"❌ Error: {e}"


def create_app() -> gr.Blocks:
    """Create the Gradio application with tabbed interface.
    
    Returns:
        Gradio Blocks app
    """
    # Get available categories and tones
    categories = recommendation_service.get_categories()
    tones = recommendation_service.get_tones()
    
    with gr.Blocks(title="Semantic Book Recommender") as app:
        gr.Markdown("# 📚 Semantic Book Recommender")
        gr.Markdown(
            "Find your next great read using AI-powered semantic search. "
            "Search, save favorites, and track your reading journey!"
        )
        
        # Main tabbed interface
        with gr.Tabs() as tabs:
            # TAB 1: Search
            with gr.Tab("🔍 Search", id=0):
                gr.Markdown("### Find Books")
                
                with gr.Row():
                    with gr.Column(scale=3):
                        search_query = gr.Textbox(
                            label="What kind of book are you looking for?",
                            placeholder="e.g., A thrilling mystery with unexpected twists",
                            lines=2
                        )
                    
                    with gr.Column(scale=1):
                        search_category = gr.Dropdown(
                            choices=categories,
                            label="Category",
                            value="All"
                        )
                    
                    with gr.Column(scale=1):
                        search_tone = gr.Dropdown(
                            choices=tones,
                            label="Emotional Tone",
                            value="All"
                        )
                
                search_button = gr.Button("🔍 Search Books", variant="primary", size="lg")
                search_status = gr.Markdown("")
                
                gr.Markdown("### Results")
                search_gallery = gr.Gallery(
                    label="Click a book to see details",
                    columns=4,
                    rows=2,
                    height=600,
                    object_fit="contain",
                    show_label=True
                )
                
                with gr.Row():
                    with gr.Column(scale=4):
                        gr.Markdown("### Book Details")
                        book_details = gr.HTML(
                            value="<p style='text-align: center; color: #999; padding: 40px;'>Click a book above to see details</p>"
                        )
                    
                    with gr.Column(scale=1):
                        gr.Markdown("### Add to Favorites")
                        gr.Markdown("_Click a book, then:_")
                        selected_search_idx = gr.State(value=-1)
                        add_fav_btn = gr.Button("⭐ Add to Favorites", variant="primary", interactive=False)
                        add_fav_status = gr.Markdown("")
                
                # Search button handler
                search_button.click(
                    fn=recommend_books,
                    inputs=[search_query, search_category, search_tone],
                    outputs=[search_gallery, search_status],
                    show_progress="full"
                )
                
                # Book selection handler for search tab
                def on_search_book_select(evt: gr.SelectData) -> Tuple[str, int, gr.Button]:
                    """Show details and enable add button."""
                    global current_search_results
                    
                    if not current_search_results or evt.index >= len(current_search_results):
                        return "<p style='color: #999;'>No book selected</p>", -1, gr.Button(interactive=False)
                    
                    book = current_search_results[evt.index]
                    details = format_book_details(book)
                    
                    # Check if already favorited
                    is_fav = user_service.is_favorite(default_user_id, book.isbn13)
                    btn = gr.Button(interactive=not is_fav)
                    
                    return details, evt.index, btn
                
                # Add to favorites handler
                def add_to_favorites(selected_idx: int) -> Tuple[List[Tuple[str, str]], str, gr.Button]:
                    """Add book to favorites."""
                    global current_search_results
                    
                    if selected_idx < 0 or not current_search_results or selected_idx >= len(current_search_results):
                        return [], "⚠️ No book selected", gr.Button(interactive=False)
                    
                    try:
                        book = current_search_results[selected_idx]
                        user_service.add_favorite(default_user_id, book.isbn13)
                        
                        # Refresh gallery
                        results = [format_book_for_gallery(b) for b in current_search_results]
                        btn = gr.Button(interactive=False)
                        
                        return results, f"⭐ Added '{book.title}' to favorites!", btn
                    except Exception as e:
                        logger.error(f"Error adding favorite: {e}")
                        return [], f"❌ Error: {e}", gr.Button(interactive=True)
                
                # Connect events
                search_gallery.select(
                    fn=on_search_book_select,
                    outputs=[book_details, selected_search_idx, add_fav_btn]
                )
                
                add_fav_btn.click(
                    fn=add_to_favorites,
                    inputs=[selected_search_idx],
                    outputs=[search_gallery, add_fav_status, add_fav_btn]
                )
            
            # TAB 2: History
            with gr.Tab("📜 History", id=1):
                gr.Markdown("### Your Search History")
                
                history_display = gr.HTML()
                refresh_history_btn = gr.Button("🔄 Refresh History")
                
                refresh_history_btn.click(
                    fn=load_search_history,
                    outputs=history_display
                )
                
                # Initial load
                app.load(
                    fn=load_search_history,
                    outputs=history_display
                )
            
            # TAB 3: Favorites
            with gr.Tab("⭐ Favorites", id=2):
                gr.Markdown("### Your Favorite Books")
                
                favorites_status = gr.Markdown("")
                favorites_gallery = gr.Gallery(
                    label="Click a book to see details",
                    columns=8,
                    rows=2,
                )
                
                with gr.Row():
                    with gr.Column(scale=4):
                        gr.Markdown("### Book Details")
                        fav_book_details = gr.HTML(
                            value="<p style='text-align: center; color: #999; padding: 40px;'>Click a book above to see details</p>"
                        )
                    
                    with gr.Column(scale=1):
                        gr.Markdown("### Remove from Favorites")
                        gr.Markdown("_Click a book, then:_")
                        selected_fav_idx = gr.State(value=-1)
                        remove_fav_btn = gr.Button("💔 Remove from Favorites", variant="secondary", interactive=False)
                        remove_fav_status = gr.Markdown("")
                
                refresh_favorites_btn = gr.Button("🔄 Refresh Favorites", variant="primary")
                
                # Book selection handler for favorites tab
                def on_favorite_book_select(evt: gr.SelectData) -> Tuple[str, int, gr.Button]:
                    """Show details and enable remove button."""
                    global current_search_results
                    
                    if not current_search_results or evt.index >= len(current_search_results):
                        return "<p style='color: #999;'>No book selected</p>", -1, gr.Button(interactive=False)
                    
                    book = current_search_results[evt.index]
                    details = format_book_details(book)
                    btn = gr.Button(interactive=True)
                    
                    return details, evt.index, btn
                
                # Remove from favorites handler
                def remove_from_favorites(selected_idx: int) -> Tuple[List[Tuple[str, str]], str, str, str, gr.Button]:
                    """Remove book from favorites."""
                    global current_search_results
                    
                    if selected_idx < 0 or not current_search_results or selected_idx >= len(current_search_results):
                        return [], "⚠️ No book selected", "", "<p style='color: #999;'>Click a book above to see details</p>", gr.Button(interactive=False)
                    
                    try:
                        book = current_search_results[selected_idx]
                        user_service.remove_favorite(default_user_id, book.isbn13)
                        
                        # Reload favorites
                        gallery, status = load_favorites()
                        clear_details = "<p style='text-align: center; color: #999; padding: 40px;'>Click a book above to see details</p>"
                        btn = gr.Button(interactive=False)
                        
                        return gallery, status, f"💔 Removed '{book.title}' from favorites!", clear_details, btn
                    except Exception as e:
                        logger.error(f"Error removing favorite: {e}")
                        return [], f"❌ Error: {e}", "", "<p style='color: #999;'>Error occurred</p>", gr.Button(interactive=False)
                
                # Connect events
                favorites_gallery.select(
                    fn=on_favorite_book_select,
                    outputs=[fav_book_details, selected_fav_idx, remove_fav_btn]
                )
                
                remove_fav_btn.click(
                    fn=remove_from_favorites,
                    inputs=[selected_fav_idx],
                    outputs=[favorites_gallery, favorites_status, remove_fav_status, fav_book_details, remove_fav_btn]
                )
                
                refresh_favorites_btn.click(
                    fn=load_favorites,
                    outputs=[favorites_gallery, favorites_status]
                )
                
                # Initial load
                app.load(
                    fn=load_favorites,
                    outputs=[favorites_gallery, favorites_status]
                )
            
            # TAB 4: Settings & Stats
            with gr.Tab("⚙️ Settings", id=3):
                gr.Markdown("### System Information")
                
                with gr.Row():
                    with gr.Column():
                        user_stats = gr.Markdown(value=get_user_stats_text())
                    
                    with gr.Column():
                        cache_stats = gr.Markdown(value=get_cache_stats())
                
                with gr.Row():
                    refresh_stats_btn = gr.Button("🔄 Refresh Stats", variant="secondary")
                    clear_cache_btn = gr.Button("🗑️ Clear Cache", variant="stop")
                
                action_result = gr.Markdown("")
                
                # Event handlers
                refresh_stats_btn.click(
                    fn=get_user_stats_text,
                    outputs=user_stats
                ).then(
                    fn=get_cache_stats,
                    outputs=cache_stats
                )
                
                clear_cache_btn.click(
                    fn=clear_cache_action,
                    outputs=action_result
                )
        
        # Footer
        gr.Markdown(
            "---\n"
            "💡 **Tips:**\n"
            "- **Search tab**: Click a book → Click 'Add to Favorites' button\n"
            "- **Favorites tab**: Click a book → Click 'Remove from Favorites' button\n"
            "- Be specific in your descriptions for better results\n"
            "- Use filters to narrow down by category or emotional tone\n"
            "- Stars (⭐/☆) on book covers show favorite status\n"
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