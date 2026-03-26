import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Arc, Circle
import random

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
st.set_page_config(layout="wide")

# iPad-friendly button styling
st.markdown(
    """
    <style>
    button {
        padding: 0.8rem 1.2rem;
        font-size: 1.1rem;
        border-radius: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

LOSS_TYPES = ["Bad Pass", "Tackle", "Dribble Lost", "Poor Touch", "Intercepted"]
LOSS_COLOURS = {
    "Bad Pass": "red",
    "Tackle": "blue",
    "Dribble Lost": "orange",
    "Poor Touch": "purple",
    "Intercepted": "yellow"
}

PLAYER_COLOURS = [
    "#e53935",  # red
    "#1e88e5",  # blue
    "#43a047",  # green
    "#fdd835",  # yellow
    "#8e24aa",  # purple
    "#fb8c00",  # orange
    "#00897b",  # teal
]

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------
for key, default in {
    "players": [],
    "started": False,
    "selected_player": None,
    "selected_loss": None,
    "events": []
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# --------------------------------------------------
# HELPERS
# --------------------------------------------------
def get_third(x):
    if x < 33.3:
        return "Build-up 3rd"
    elif x < 66.6:
        return "Middle 3rd"
    else:
        return "Attacking 3rd"

def get_channel(y):
    if y < 33.3:
        return "Left"
    elif y < 66.6:
        return "Central"
    else:
        return "Right"

def draw_pitch(ax):
    ax.set_facecolor("#2e7d32")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_xticks([])
    ax.set_yticks([])

    # Outline
    ax.plot([0, 100], [0, 0], color="white", lw=2)
    ax.plot([0, 100], [100, 100], color="white", lw=2)
    ax.plot([0, 0], [0, 100], color="white", lw=2)
    ax.plot([100, 100], [0, 100], color="white", lw=2)

    # Halfway
    ax.plot([50, 50], [0, 100], color="white", lw=2)

    # Centre
    ax.add_patch(Circle((50, 50), 9.15, fill=False, color="white", lw=2))
    ax.scatter(50, 50, color="white", s=30)

    # Penalty areas
    ax.plot([16.5, 16.5], [21.1, 78.9], color="white", lw=2)
    ax.plot([0, 16.5], [21.1, 21.1], color="white", lw=2)
    ax.plot([0, 16.5], [78.9, 78.9], color="white", lw=2)
    ax.plot([83.5, 83.5], [21.1, 78.9], color="white", lw=2)
    ax.plot([83.5, 100], [21.1, 21.1], color="white", lw=2)
    ax.plot([83.5, 100], [78.9, 78.9], color="white", lw=2)

    # 6-yard boxes
    ax.plot([5.5, 5.5], [36.8, 63.2], color="white", lw=2)
    ax.plot([0, 5.5], [36.8, 36.8], color="white", lw=2)
    ax.plot([0, 5.5], [63.2, 63.2], color="white", lw=2)
    ax.plot([94.5, 94.5], [36.8, 63.2], color="white", lw=2)
    ax.plot([94.5, 100], [36.8, 36.8], color="white", lw=2)
    ax.plot([94.5, 100], [63.2, 63.2], color="white", lw=2)

    # Spots + arcs
    ax.scatter(11, 50, color="white", s=30)
    ax.scatter(89, 50, color="white", s=30)
    ax.add_patch(Arc((11, 50), 18.3, 18.3, theta1=310, theta2=50, color="white", lw=2))
    ax.add_patch(Arc((89, 50), 18.3, 18.3, theta1=130, theta2=230, color="white", lw=2))

    # Analysis overlays
    ax.plot([33.33, 33.33], [0, 100], color="white", lw=1, ls="--")
    ax.plot([66.66, 66.66], [0, 100], color="white", lw=1, ls="--")
    ax.plot([0, 100], [33.33, 33.33], color="white", lw=1, ls="--")
    ax.plot([0, 100], [66.66, 66.66], color="white", lw=1, ls="--")

# --------------------------------------------------
# SETUP SCREEN
# --------------------------------------------------
st.title("⚽ Touchscreen Soccer Analysis")
st.caption("Version 1.0 – Match Day Analysis")
if not st.session_state.started:
    names = st.text_input("Enter players (comma separated)")
    if st.button("Start"):
        players = [n.strip() for n in names.split(",") if n.strip()]
        if players:
            st.session_state.players = players
            st.session_state.started = True
            st.rerun()
    st.stop()

# --------------------------------------------------
# PLAYERS
# --------------------------------------------------
st.subheader("Players")
cols = st.columns(len(st.session_state.players))
for i, p in enumerate(st.session_state.players):
    if cols[i].button(p, key=f"player_{i}"):
        st.session_state.selected_player = p

if st.session_state.selected_player:
    st.info(f"Selected player: **{st.session_state.selected_player}**")

# --------------------------------------------------
# LOSS TYPE
# --------------------------------------------------
st.subheader("Loss Type")
loss_cols = st.columns(len(LOSS_TYPES))
for i, loss in enumerate(LOSS_TYPES):
    if loss_cols[i].button(loss, key=f"loss_{i}"):
        st.session_state.selected_loss = loss

if st.session_state.selected_loss:
    st.info(f"Selected loss type: **{st.session_state.selected_loss}**")

# --------------------------------------------------
# TAP PITCH
# --------------------------------------------------
st.subheader("Tap Pitch")
fig, ax = plt.subplots(figsize=(10, 6))
draw_pitch(ax)
st.pyplot(fig)

if st.button("📍 Register location"):
    if st.session_state.selected_player and st.session_state.selected_loss:
        x = round(random.uniform(0, 100), 1)
        y = round(random.uniform(0, 100), 1)
        st.session_state.events.append({
            "player": st.session_state.selected_player,
            "loss": st.session_state.selected_loss,
            "third": get_third(x),
            "channel": get_channel(y),
            "x": x,
            "y": y
        })

# --------------------------------------------------
# RECORDED EVENTS
# --------------------------------------------------
st.subheader("Recorded Events")
if st.session_state.events:
    st.dataframe(pd.DataFrame(st.session_state.events))

# --------------------------------------------------
# LIVE LOSS MAP (TOGGLE)
# --------------------------------------------------
st.markdown("### Map Colour Mode")
colour_mode = st.radio(
    "",
    ["Loss Type", "Player"],
    horizontal=True
)

if st.session_state.events:
    fig, ax = plt.subplots(figsize=(10, 6))
    draw_pitch(ax)

    for e in st.session_state.events:
        if colour_mode == "Loss Type":
            colour = LOSS_COLOURS[e["loss"]]
        else:
            idx = st.session_state.players.index(e["player"])
            colour = PLAYER_COLOURS[idx % len(PLAYER_COLOURS)]

        ax.scatter(
            e["x"], e["y"],
            color=colour,
            s=110,
            edgecolors="black",
            zorder=5
        )

    st.pyplot(fig)

# --------------------------------------------------
# UNDO (SAFE PLACEMENT)
# --------------------------------------------------
st.markdown("---")
if st.button("↩️ Undo Last Event", help="Remove the most recent recorded event"):
    if st.session_state.events:
        st.session_state.events.pop()