import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

def load_and_process(file_list, condition_name):
    combined_data = []
    for file_name in file_list:
        if not os.path.exists(file_name):
            print(f"❌ ERROR: Could not find '{file_name}'")
            continue
            
        print(f"✅ Successfully loaded '{file_name}'")
        
        # Load the CSV without assuming headers
        df = pd.read_csv(file_name, header=None, names=["Trial_in_Set", "ID", "Time", "Hit"])
        
        # SMART HEADER DETECTION: Drop first row if it contains text
        if pd.to_numeric(df['Time'], errors='coerce').isna().iloc[0]:
            df = df.iloc[1:].reset_index(drop=True)
            
        df['Trial_in_Set'] = pd.to_numeric(df['Trial_in_Set'])
        df['ID'] = pd.to_numeric(df['ID'])
        df['Time'] = pd.to_numeric(df['Time'])
        
        # ---> FORCE EVERY TRIAL TO BE A HIT (1) <---
        # This ignores any misses for all subsequent analysis and plots
        df['Hit'] = 1 
        
        df['Condition'] = condition_name
        df['Participant'] = file_name.replace(condition_name.lower(), "").replace(".csv", "").replace(condition_name, "")
        
        df['Set'] = (df.index // 20) + 1
        df['Continuous_Trial'] = np.arange(1, len(df) + 1)
        combined_data.append(df)
        
    return pd.concat(combined_data, ignore_index=True) if combined_data else pd.DataFrame()

# ==========================================
# EXACT FILE NAMES
# ==========================================
pulling_files = ["PullingDook.csv", "PullingPieter.csv", "PullingTimo.csv"]
pushing_files = ["PushingAdriaan.csv", "PushingBarthold.csv", "PushingFriso.csv", "PushingJulius.csv"]

print("--- LOADING DATA ---")
df_pull = load_and_process(pulling_files, "Pulling")
df_push = load_and_process(pushing_files, "Pushing")
df_all = pd.concat([df_pull, df_push], ignore_index=True)

if df_all.empty:
    print("\n🚨 CRITICAL ERROR: No data found at all!")
    exit()

# Global visual settings
sns.set_theme(style="ticks", context="talk")
palette_main = {"Pushing": "red", "Pulling": "blue"}

# =====================================================================
# FIGURE 1: Trials vs Completion Time (Smooth Curves, No Dots)
# =====================================================================
plt.figure(figsize=(12, 6))

# Removed marker='o' to create smooth curves
sns.lineplot(
    data=df_all, 
    x='Continuous_Trial', 
    y='Time', 
    hue='Condition', 
    palette=palette_main, 
    linewidth=2.5, 
    errorbar=('ci', 95), 
    alpha=0.8
)

plt.axvline(x=60.5, color='black', linestyle='--', linewidth=1.5)
plt.text(61, df_all['Time'].max() * 0.9, ' Feedback Removed', fontsize=12)

plt.title("Figure 1. Completion Time across All Trials")
plt.xlabel("Trial Number")
plt.ylabel("Completion Time (s)")
sns.despine()
plt.tight_layout()
plt.savefig("Figure1_Trials_vs_Time_Smooth.png", dpi=300)
plt.close()
print("Saved Figure 1: Figure1_Trials_vs_Time_Smooth.png")


# =====================================================================
# FIGURE 2: Push vs Pull - Change in Completion Time (Set 4 vs Set 3)
# =====================================================================
# Calculate mean time per participant per set
set_means = df_all.groupby(['Participant', 'Condition', 'Set'])['Time'].mean().reset_index()

# Extract Set 3 (Final Training) and Set 4 (Transfer)
set3 = set_means[set_means['Set'] == 3].set_index('Participant')['Time']
set4 = set_means[set_means['Set'] == 4].set_index('Participant')['Time']

# Calculate the Change (Transfer minus Final Training)
change_df = pd.DataFrame({
    'Condition': set_means[set_means['Set'] == 3].set_index('Participant')['Condition'],
    'Time_Change': set4 - set3
}).reset_index()

plt.figure(figsize=(7, 6))

sns.pointplot(
    data=change_df, 
    x='Condition', 
    y='Time_Change', 
    hue='Condition', 
    order=['Pushing', 'Pulling'], 
    palette=palette_main, 
    capsize=0.1, 
    errorbar=('ci', 95), 
    join=False,      # Removes the line connecting the two condition dots
    markers='o', 
    legend=False
)

plt.axhline(y=0, color='black', linestyle='--', linewidth=1)
plt.title("Figure 2. Change in Completion Time\n(Without vs. Without Feedback)")
plt.ylabel("Time Difference (s)")
plt.xlabel("Condition")
sns.despine()
plt.tight_layout()
plt.savefig("Figure2_Change_in_Time.png", dpi=300)
plt.close()
print("Saved Figure 2: Figure2_Change_in_Time.png")


# =====================================================================
# FIGURE 3: Phase Comparison (First 3 Sets vs Last Set)
# =====================================================================
def create_phase_label(row):
    phase = '1-3' if row['Set'] <= 3 else '4'
    return f"{row['Condition']}\n(Set {phase})"

df_all['Phase_Group'] = df_all.apply(create_phase_label, axis=1)

# Define the Left-to-Right order for the 4 categories
order_4 = [
    "Pushing\n(Set 1-3)",
    "Pushing\n(Set 4)",
    "Pulling\n(Set 1-3)",
    "Pulling\n(Set 4)"
]

# Color palette maintaining the Red/Blue theme (lighter for training, darker for transfer)
palette_4 = {
    "Pushing\n(Set 1-3)": "#ff6666",  # Light Red
    "Pushing\n(Set 4)": "#cc0000",    # Dark Red
    "Pulling\n(Set 1-3)": "#66b3ff",  # Light Blue
    "Pulling\n(Set 4)": "#005ce6"     # Dark Blue
}

plt.figure(figsize=(10, 7))

sns.pointplot(
    data=df_all, 
    x='Phase_Group', 
    y='Time', 
    hue='Phase_Group',
    order=order_4, 
    palette=palette_4, 
    capsize=0.1, 
    errorbar=('ci', 95), 
    markers='o',
    legend=False
)

plt.title("Figure 3. Completion Time: Training vs Transfer (All Trials)")
plt.ylabel("Average Completion Time (s)")
plt.xlabel("") 
plt.xticks(fontsize=12)
sns.despine()
plt.tight_layout()
plt.savefig("Figure3_Phase_Comparison.png", dpi=300)
plt.close()
print("Saved Figure 3: Figure3_Phase_Comparison.png")

print("\n All 3 figures generated successfully!")