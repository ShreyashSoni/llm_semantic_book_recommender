import numpy as np
import pandas as pd
import gradio as gr

from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

from dotenv import load_dotenv
load_dotenv()

books = pd.read_csv("data/books_with_emotions.csv")
books["large_thumbnail"] = books["thumbnail"] + "&fife=w800"
books["large_thumbnail"] = np.where(
    books["large_thumbnail"].isna(), 
    "assets/cover-not-found.jpg",
    books["large_thumbnail"]
)

db_books = Chroma(persist_directory="vector_store",  embedding_function=OpenAIEmbeddings())

def retrieve_semantic_recommendations(
        query: str,
        category: str,
        tone: str,
        initial_top_k: int = 50,
        final_top_k: int = 16
) -> pd.DataFrame:
    
    recs = db_books.similarity_search(query=query, k=initial_top_k)
    books_list = [int(rec.page_content.strip('"').split()[0]) for rec in recs]
    books_recs = books[books["isbn13"].isin(books_list)].head(initial_top_k)

    if category != "All":
        books_recs = books_recs[books_recs["simple_categories"]==category].head(final_top_k)
    else:
        books_recs = books_recs.head(final_top_k)

    match tone:
        case "Happy":
            books_recs.sort_values(by="joy", ascending=False, inplace=True)
        case "Surprising":
            books_recs.sort_values(by="surprise", ascending=False, inplace=True)
        case "Angry":
            books_recs.sort_values(by="anger", ascending=False, inplace=True)
        case "Suspenseful":
            books_recs.sort_values(by="fear", ascending=False, inplace=True)
        case "Sad":
            books_recs.sort_values(by="sadness", ascending=False, inplace=True)
    
    return books_recs


def recommend_books(
        query: str,
        category: str,
        tone: str
):
    recommendations = retrieve_semantic_recommendations(query, category, tone)
    results = []

    for _, row in recommendations.iterrows():
        description = row["description"]
        truncated_desc_split = description.split()
        truncated_description = " ".join(truncated_desc_split[:30]) + "..."

        authors_split = row["authors"].split(";")
        if len(authors_split) == 2:
            author_str = f"{authors_split[0]} and {authors_split[1]}"
        elif len(authors_split) > 2:
            author_str = f"{', '.join(authors_split[:-1])} and {authors_split[-1]}"
        else:
            author_str = row["authors"]

        caption = f"{row["title"]} by {author_str}: {truncated_description}"
        results.append((row["large_thumbnail"], caption))
    
    return results


categories = ["All"] + sorted(books["simple_categories"].unique())
tone = ["All"] + ["Happy", "Surprising", "Angry", "Suspenseful", "Sad"]


with gr.Blocks(theme=gr.themes.Glass()) as dashboard:
    gr.Markdown("# Semantic Book Recommender")

    with gr.Row():
        user_query = gr.Textbox(label="Please enter a description of a book:", 
                                placeholder="e.g., A story about forgiveness")
        category_dropdown = gr.Dropdown(choices=categories, 
                                        label="Select a catgeory:", 
                                        value="All")
        tone_dropdown = gr.Dropdown(choices=tone, 
                                    label="Select an emotional tone:", 
                                    value="All")
        submit_button = gr.Button("Find recommendations")

    gr.Markdown("# Recommendations")
    output = gr.Gallery(label= "Recommended books", columns=8, rows=2)

    submit_button.click(fn=recommend_books, 
                        inputs=[user_query, category_dropdown, tone_dropdown], 
                        outputs=output)


if __name__ == "__main__":
    dashboard.launch()
