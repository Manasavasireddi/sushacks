import streamlit as st
from datetime import date
import random
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access the Gemini API key
gemini_api_key = os.getenv("GEMINI_API_KEY")

# Example usage of the API key
if gemini_api_key:
    st.write("Gemini API key loaded successfully!")
else:
    st.error("Gemini API key not found. Please check your .env file.")

# --- Session State Initialization ---
if 'last_checkin' not in st.session_state:
    st.session_state.last_checkin = None
if 'streak' not in st.session_state:
    st.session_state.streak = 0
if 'xp' not in st.session_state:
    st.session_state.xp = 0
if 'badges' not in st.session_state:
    st.session_state.badges = []
if 'goals' not in st.session_state:
    st.session_state.goals = ['Machine Learning']
if 'goal_progress' not in st.session_state:
    st.session_state.goal_progress = {goal: 0 for goal in st.session_state.goals}
if 'weekly_tasks' not in st.session_state:
    st.session_state.weekly_tasks = {"Submit Resume": False, "Complete 3 lessons": False, "Take 1 quiz": False}
if 'user_rank' not in st.session_state:
    st.session_state.user_rank = random.randint(1, 50)
if 'leaderboard' not in st.session_state:
    st.session_state.leaderboard = {"You": st.session_state.xp, "UserA": 120, "UserB": 90, "UserC": 70}

# --- Title ---
st.title("🚀 PathPilot - Your Career Launch Dashboard")

# --- Daily Check-In ---
st.header("📅 Daily Check-In")
if st.button("✅ Mark Today’s Learning Done"):
    today = date.today()
    if st.session_state.last_checkin != today:
        if st.session_state.last_checkin == today.fromordinal(today.toordinal() - 1):
            st.session_state.streak += 1
        else:
            st.session_state.streak = 1
        st.session_state.last_checkin = today
        st.session_state.xp += 10

        if st.session_state.streak in [3, 7, 14, 30]:
            badge = f"{st.session_state.streak}-Day Streak 🔥"
            if badge not in st.session_state.badges:
                st.session_state.badges.append(badge)
                st.success(f"🏅 New badge earned: {badge}")
    else:
        st.warning("✅ Already checked in today!")

st.markdown("---")

# --- Key Stats ---
st.subheader("📊 Your Progress Overview")
col1, col2, col3 = st.columns(3)
col1.metric("🔥 Streak", f"{st.session_state.streak} days")
col2.metric("⭐ XP", f"{st.session_state.xp} XP")
col3.metric("🏅 Badges", f"{len(st.session_state.badges)} earned")

st.markdown("---")

# --- Learning Path Management ---
st.header("📚 Your Learning Paths")
new_goals = st.multiselect("🎯 Add/Remove Learning Goals", 
                           ["Machine Learning", "Cloud Computing", "Data Science", "DevOps", "AI Ethics"],
                           default=st.session_state.goals)
st.session_state.goals = new_goals
for goal in new_goals:
    if goal not in st.session_state.goal_progress:
        st.session_state.goal_progress[goal] = 0

for goal in st.session_state.goals:
    progress = st.slider(f"{goal} Progress", 0, 100, key=f"prog_{goal}", value=st.session_state.goal_progress[goal])
    if progress > st.session_state.goal_progress[goal]:
        st.session_state.xp += (progress - st.session_state.goal_progress[goal]) // 10 * 5
    st.session_state.goal_progress[goal] = progress
    if progress >= 100 and f"{goal} Mastery 🧠" not in st.session_state.badges:
        st.session_state.badges.append(f"{goal} Mastery 🧠")
        st.session_state.xp += 50
        st.balloons()
        st.success(f"🏆 Mastered {goal}! +50 XP and badge unlocked!")

st.markdown("---")

# --- Weekly Challenge To-Do List ---
st.header("⚔️ Weekly Challenge")
st.caption("Complete at least 2 out of 3 tasks this week to earn a reward! 💪")

# Editable Weekly Tasks
new_task = st.text_input("Add a new weekly challenge:")
if st.button("➕ Add Task") and new_task:
    st.session_state.weekly_tasks[new_task] = False

to_remove = st.multiselect("🗑️ Remove completed/old tasks:", list(st.session_state.weekly_tasks.keys()))
for task in to_remove:
    st.session_state.weekly_tasks.pop(task, None)

# Display and track weekly tasks
completed = 0
for task in list(st.session_state.weekly_tasks.keys()):
    st.session_state.weekly_tasks[task] = st.checkbox(task, value=st.session_state.weekly_tasks[task])
    if st.session_state.weekly_tasks[task]:
        completed += 1

if completed >= 2:
    st.success("🎉 Weekly Goal Achieved! +30 XP")
    st.session_state.xp += 30

# Badges Info
st.markdown("### 🏅 Available Badges")
st.markdown("""
- **3-Day Streak 🔥** – Stay consistent for 3 days  
- **7-Day Streak 🔥** – Keep the momentum going for a week  
- **{Skill} Mastery 🧠** – Reach 100% in any learning goal  
- **Weekly Warrior 💥** – Complete 2+ weekly challenges  
""")

if completed >= 2 and "Weekly Warrior 💥" not in st.session_state.badges:
    st.session_state.badges.append("Weekly Warrior 💥")
    st.success("🏅 Badge unlocked: Weekly Warrior 💥")

st.markdown("---")

# --- Leaderboard ---
st.header("🏆 Global Leaderboard")
st.caption("Compare your XP with peers!")

leaderboard = st.session_state.leaderboard
leaderboard["You"] = st.session_state.xp
sorted_leaderboard = dict(sorted(leaderboard.items(), key=lambda x: x[1], reverse=True))
for rank, (user, xp) in enumerate(sorted_leaderboard.items(), start=1):
    if user == "You":
        st.markdown(f"**{rank}. {user} - {xp} XP 🫵**")
    else:
        st.markdown(f"{rank}. {user} - {xp} XP")

st.markdown("---")

# --- Badge Showcase ---
if st.session_state.badges:
    st.header("🎖️ Your Badge Collection")
    st.markdown(" | ".join(st.session_state.badges))

# --- Motivation Quote ---
st.header("💬 Daily Motivation")
quotes = [
    "You're doing amazing! Keep showing up.",
    "One step at a time gets you there faster than you think.",
    "Stay consistent and the results will follow.",
    "You're building momentum. Keep pushing!",
    "Learning is a superpower — and you’ve got it!"
]
st.info(random.choice(quotes))

st.markdown("---")
st.markdown("🚀 _Stay focused. Every click is one step closer to your dream role!_")
