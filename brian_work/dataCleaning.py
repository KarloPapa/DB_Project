import pandas as pd

df = pd.read_csv(
    'top_1000_popular_movies_tmdb.csv',
    engine='python',
    on_bad_lines='skip'
)

# Drop rows with any missing values
df_clean = df.dropna()

# Save cleaned CSV
df_clean.to_csv('top_1000_popular_movies_tmdb_clean.csv', index=False)
print("Cleaned CSV saved as 'top_1000_popular_movies_tmdb_clean.csv'")
