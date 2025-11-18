import pandas as pd
# pandas used because its the simplest and most effective for dealing with CSVs

# Loading data from CSV files
try:
    df_results = pd.read_csv('results.csv')
    df_shootouts = pd.read_csv('shootouts.csv')
    df_goalscorers = pd.read_csv('goalscorers.csv')
except FileNotFoundError:
    print("Error: CSV files not found in current directory.")
    exit()

# Convert date to datetime objects- done for accurate filtering and merging
df_results['date'] = pd.to_datetime(df_results['date'])
df_shootouts['date'] = pd.to_datetime(df_shootouts['date'])
df_goalscorers['date'] = pd.to_datetime(df_goalscorers['date'])

print("----- Q1: Avg Goals per Game (1900-2000) ---")

# Filter 20th century
mask = (df_results['date'].dt.year >= 1900) & (df_results['date'].dt.year <= 2000)
filtered_games = df_results[mask]

# Calculate average goals each game
avg_goals = (filtered_games['home_score'] + filtered_games['away_score']).mean()
print(f"{avg_goals:.2f}")


print("\n----- Q2: Shootout Wins by Country ---")

# Count frequency of winners
# Sort by alphabet
print(df_shootouts['winner'].value_counts().sort_index())

# The next line is only used if i wanna see the full list of all countries
#// print(df_shootouts['winner'].value_counts().sort_index().to_string())


print("\n----- Q3: Reliable Key Strategy ---")

# This will be used in question 4
# My reliable key is a combination of date, home_team, and away_team to avoid duplicate matches
print("Answer: I created a Composite Key using [Date] + [Home_Team] + [Away_Team].")


print("\n----- Q4: Shootout winners after 1-1 draw ---")

# Find all 1-1 draws
draws = df_results[(df_results['home_score'] == 1) & (df_results['away_score'] == 1)]

# Join results with shootouts using the composite key
# The part on=['date', 'home_team', 'away_team'] is the reliable key asked for in question 3
merged_q4 = pd.merge(draws, df_shootouts, on=['date', 'home_team', 'away_team'])
print(merged_q4['winner'].unique())


print("\n----- Q5: Top Scorer % by Tournament ---")

# strategy is to split this one into multiple parts solving one query at a time then joining them

# 1. Left Join Goalscorers with Results to retrieve Tournament info
cols_needed = ['date', 'home_team', 'away_team', 'tournament']
full_data = pd.merge(df_goalscorers, df_results[cols_needed], on=['date', 'home_team', 'away_team'], how='left')

# 2. Total tournament goals vs. Player goals
tourn_totals = full_data.groupby('tournament').size().reset_index(name='total_goals')
player_totals = full_data.groupby(['tournament', 'scorer']).size().reset_index(name='player_goals')

# 3. Calculate Percentage
stats = pd.merge(player_totals, tourn_totals, on='tournament')
stats['percent'] = (stats['player_goals'] / stats['total_goals']) * 100

# 4. Rank then filter top scorer per tournament
top_scorers = stats.sort_values('player_goals', ascending=False).groupby('tournament').head(1)

print(top_scorers[['tournament', 'scorer', 'percent']].sort_values('tournament').to_string(index=False))



# ----- Additional Tasks: Data Quality Check and Resolution ---
print("\n----- ADDITIONAL TASK: DATA QUALITY CHECK & RESOLUTION -----")

# Task A: Create DQ Flag for Missing Goalscorers
# I checked the most critical column for missing data
df_goalscorers['DQ_flag'] = df_goalscorers['scorer'].apply(
    lambda x: 'Missing_Scorer_Name' if pd.isna(x) else 'OK'
)

# Display count of flagged records to show issue was identified
flagged_count = df_goalscorers['DQ_flag'].value_counts()
print("\nDQ Flagged Records Identified:")
print(flagged_count)

# Task B: Resolve the DQ Issues
# Fill the missing values with a placeholder to maintain the record count as the .
df_goalscorers['scorer'] = df_goalscorers['scorer'].fillna('Unknown Scorer')
