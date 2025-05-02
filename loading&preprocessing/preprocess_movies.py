import pandas as pd
import ast
import json

def clean_list_column(fake_list_str):
    """Convert a string that looks like a Python list into a JSON array string."""
    if pd.isna(fake_list_str):
        return "[]"
    try:
        # Safely evaluate the string to a real Python list
        parsed = ast.literal_eval(fake_list_str)
        if isinstance(parsed, list):
            return json.dumps(parsed, ensure_ascii=False)
        else:
            return "[]"
    except Exception:
        return "[]"

def preprocess_csv(input_path: str, output_path: str):
    df = pd.read_csv(
    input_path,
    engine="python",              # More flexible parser
    quotechar='"',                # Handle quoted strings correctly
    escapechar='\\',              # Helps handle stray quotes
    on_bad_lines='skip'           # Replaces error_bad_lines=False
)

    # Clean both list-like columns
    df["production_companies"] = df["production_companies"].apply(clean_list_column)
    df["genres"] = df["genres"].apply(clean_list_column)

    # Save cleaned CSV
    df.to_csv(output_path, index=False, quoting=1)  # quoting=1 → quote all strings
    print(f"Cleaned CSV written to {output_path}")

if __name__ == "__main__":
    preprocess_csv(
        "/Users/kpapa/Downloads/DBProject-main/karlo_work/top_1000_popular_movies_tmdb.csv",
        "/Users/kpapa/Downloads/DBProject-main/karlo_work/movies_cleaned.csv"
    )
