import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# Domains and user types
domains = ['YouTube','Coursera','Udemy','KhanAcademy','Netflix','Spotify','Medium']
user_types = ['Free','Premium','Student','Teacher']

# Generate dataset
data = []

start_date = datetime(2025, 8, 1)
end_date = datetime(2025, 8, 31)
date_range = (end_date - start_date).days + 1

for i in range(1, 501):  # 500 rows
    user_id = random.randint(1, 100)  # simulate multiple sessions per user
    domain = random.choice(domains)
    user_type = random.choice(user_types)

    # Engagement score depends on domain and user type
    base_score = random.randint(10, 100)
    if domain in ['Coursera','Udemy','KhanAcademy']:
        if user_type in ['Premium','Student']:
            engagement_score = min(base_score + random.randint(20,30), 100)
        else:
            engagement_score = base_score
    elif domain in ['YouTube','Netflix','Spotify']:
        engagement_score = base_score + random.randint(0,10)
    else:
        engagement_score = base_score

    # Random date within month
    date = (start_date + timedelta(days=random.randint(0,date_range-1))).strftime('%Y-%m-%d')

    # Extra features
    session_duration = random.randint(5,120)  # minutes
    clicks = random.randint(1,50)
    completed_lessons = random.randint(0,10) if domain in ['Coursera','Udemy','KhanAcademy'] else 0

    data.append([user_id, domain, engagement_score, date, user_type, session_duration, clicks, completed_lessons])

# Create DataFrame
df = pd.DataFrame(data, columns=[
    'user_id','domain','engagement_score','date','user_type','session_duration','clicks','completed_lessons'
])

# Save to CSV
df.to_csv('user_data.csv', index=False)
print("✅ Complex dataset created: user_data.csv")

