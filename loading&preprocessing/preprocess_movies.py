import pandas as pd
import ast
import json

def clean_list_column(fake_list_str):
    """Convert a string that looks like a Python list into a JSON array string."""
    if pd.isna(fake_list_str):
        return "[]"
    try:
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
    engine="python",             
    quotechar='"',               
    escapechar='\\',             
    on_bad_lines='skip'          
)

    # Clean both list-like columns
    df["production_companies"] = df["production_companies"].apply(clean_list_column)
    df["genres"] = df["genres"].apply(clean_list_column)

    # Save cleaned CSV
    df.to_csv(output_path, index=False, quoting=1)  
    print(f"Cleaned CSV written to {output_path}")

if __name__ == "__main__":
    preprocess_csv(
        "/Users/kpapa/Downloads/DBProject-main/karlo_work/top_1000_popular_movies_tmdb.csv",
        "/Users/kpapa/Downloads/DBProject-main/karlo_work/movies_cleaned.csv"
    )
