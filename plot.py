import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

def load_and_process(file_list, condition_name):
    combined_data = []
    for file_name in file_list:
        if not os.path.exists(file_name):
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
        df['Hit'] = 1 
        
        df['Condition'] = condition_name
        
        # Safely extract participant name (e.g., "PullingPieter.csv" -> "pieter")
        df['Participant'] = file_name.lower().replace(condition_name.lower(), "").replace(".csv", "")
        
        df['Set'] = (df.index // 20) + 1
        df['Continuous_Trial'] = np.arange(1, len(df) + 1)
        combined_data.append(df)
        
    return pd.concat(combined_data, ignore_index=True) if combined_data else pd.DataFrame()

# ==========================================
# AUTOMATIC FILE DETECTION
# ==========================================
# Get all files in the current directory that end in .csv
all_files = [f for f in os.listdir('.') if f.endswith('.csv')]

# Automatically separate them into pulling and pushing groups (case-insensitive)
pulling_files = [f for f in all_files if f.lower().startswith('pulling')]
pushing_files = [f for f in all_files if f.lower().startswith('pushing')]

print(f"--- FOUND {len(pulling_files)} PULLING FILES AND {len(pushing_files)} PUSHING FILES ---")

df_pull = load_and_process(pulling_files, "Pulling")
df_push = load_and_process(pushing_files, "Pushing")

if df_pull.empty and df_push.empty:
    print("\n🚨 CRITICAL ERROR: No data found at all! Are the CSVs in the same folder as this script?")
    exit()

# Combine data
df_all = pd.concat([df_pull, df_push], ignore_index=True)

# ==========================================
# CALCULATE GROUP NUMBERS (N)
# ==========================================
# Count unique participants dynamically based on what was loaded
n_pull = df_all[df_all['Condition'] == 'Pulling']['Participant'].nunique() if not df_pull.empty else 0
n_push = df_all[df_all['Condition'] == 'Pushing']['Participant'].nunique() if not df_push.empty else 0

# Create new labels with the N appended
label_pull = f"Pulling (N={n_pull})"
label_push = f"Pushing (N={n_push})"

# Map the raw condition names to the new labels for the plots
df_all['Condition'] = df_all['Condition'].map({"Pulling": label_pull, "Pushing": label_push})

# ==========================================
# 🌙 DARK MODE SETTINGS
# ==========================================
plt.style.use('dark_background')
sns.set_context("talk")

# Force strictly black background and white text globally
plt.rcParams.update({
    "figure.facecolor": "black",
    "axes.facecolor": "black",
    "savefig.facecolor": "black",
    "savefig.edgecolor": "black",
    "text.color": "white",
    "axes.labelcolor": "white",
    "xtick.color": "white",
    "ytick.color": "white",
    "axes.edgecolor": "white"
})

# Dynamic palette using the new N labels
palette_main = {label_push: "#ff4d4d", label_pull: "#4d94ff"}

# =====================================================================
# FIGURE 1: Trials vs Completion Time (Smooth Curves, No Dots)
# =====================================================================
plt.figure(figsize=(12, 6))

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

plt.axvline(x=60.5, color='white', linestyle='--', linewidth=1.5)
plt.text(61, df_all['Time'].max() * 0.9, ' Feedback Removed', color='white', fontsize=12)

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
set_means = df_all.groupby(['Participant', 'Condition', 'Set'])['Time'].mean().reset_index()

# We only process Figure 2 if both Set 3 and Set 4 exist
if 3 in set_means['Set'].values and 4 in set_means['Set'].values:
    set3 = set_means[set_means['Set'] == 3].set_index('Participant')['Time']
    set4 = set_means[set_means['Set'] == 4].set_index('Participant')['Time']

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
        order=[label_push, label_pull], 
        palette=palette_main, 
        capsize=0.1, 
        errorbar=('ci', 95), 
        join=False,
        markers='o', 
        legend=False
    )

    plt.axhline(y=0, color='white', linestyle='--', linewidth=1)
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

order_4 = [
    f"{label_push}\n(Set 1-3)",
    f"{label_push}\n(Set 4)",
    f"{label_pull}\n(Set 1-3)",
    f"{label_pull}\n(Set 4)"
]

palette_4 = {
    f"{label_push}\n(Set 1-3)": "#ff6666",  
    f"{label_push}\n(Set 4)": "#cc0000",    
    f"{label_pull}\n(Set 1-3)": "#66b3ff",  
    f"{label_pull}\n(Set 4)": "#005ce6"     
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

print("\n🎉 All 3 dark-themed figures generated successfully!")