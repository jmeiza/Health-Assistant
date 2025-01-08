import streamlit as st
import sqlite3
import bcrypt
from ai import get_diet
from profiles import create_profile, get_notes, get_profile
from form_submit import update_personal_info, add_note, delete_note


# Setting up the database
conn = sqlite3.connect('users.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users
            (username TEXT, password TEXT)''')
conn.commit()

#Database setup for additional user info
info_conn = sqlite3.connect('user_info.db')
info_c = info_conn.cursor()
info_c.execute('''CREATE TABLE IF NOT EXISTS user_info
                  (username TEXT, name TEXT, age INTEGER, weight REAL, height REAL, gender TEXT)''')
info_conn.commit()

# Hashing Function
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

# Function to add a new user
def add_user(username, password):
    hashed_password = hash_password(password)
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
    conn.commit()

# Adding user's information
def add_user_info(username,name,age,weight,height,gender):
    info_c.execute("INSERT INTO user_info (username, name, age, weight, height, gender) VALUES (?, ?, ?, ?, ?, ?)", (username,name,age,weight,height,gender))
    info_conn.commit()

# Function to validate login
def login_user(username, password):
    c.execute("SELECT password FROM users WHERE username = ?", (username,))
    stored_password = c.fetchone()
    if stored_password and bcrypt.checkpw(password.encode(), stored_password[0]):
        return True
    return False

# Navigate function
def navigate_to(page):
    st.session_state["page"] = page
    st.rerun()

# Data Form
@st.fragment
def personal_data_form():
    with st.form("personal_data"):
        st.header("Personal Data")

        profile = st.session_state.profile

        name = st.text_input("Name", value=profile["general"]["name"])
        age = st.number_input("Age", min_value=1, max_value=120, step=1, value=profile["general"]["age"])
        weight = st.number_input("Weight (kg)", min_value=0.0, max_value=300.0, step=0.1, value=float(profile["general"]["weight"]))
        height = st.number_input("Height (cm)", min_value=0.0, max_value=250.0, step=0.1, value=float(profile["general"]["height"]))
        
        genders = ["Male", "Female", "Other"]
        gender = st.radio('Gender', genders, genders.index(profile["general"].get("gender", "Male")))
        
        #Remeber to create a separate page for username and password
        username = st.text_input("Username")
        password = st.text_input("Password")

        personal_data_submit = st.form_submit_button("Save")
        if personal_data_submit:
            if all([name,age,weight,height,gender]):
                with st.spinner():
                    st.ssession_state.profile = update_personal_info(profile, "general", name=name, age=age, weight=weight, height=height, gender=gender)
                    st.success('Information saved')
            else:
                st.warning("Please fill in all of the data")
    return name,age,weight,height,gender,username,password


@st.fragment
def goals_form():
    profile = st.session_state.profile
    with st.form("goals form"):
        st.header("Goals")
        goals = st.multiselect(
            "Select your Goals", ["Muscle Gain", "Fat Loss", "Stay Active"],
            default=profile.get("goals", ["Stay Active"])
        )

        goals_submit = st.form_submit_button('Save')
        if goals_submit:
            if goals:
                with st.spinner():
                    st.session_state.profile = update_personal_info(profile, "goals", goals=goals)
                    st.success('Goals Updated')
            else:
                st.warning("Please select at least one goal")

@st.fragment
def diet():
    profile = st.session_state.profile
    nutrition = st.container(border=True)
    nutrition.header("Diet")
    if nutrition.button("Generate with AI"):
        result = get_diet(profile.get("general"), profile.get("goals"))
        profile["nutrition"] = result
        nutrition.success("AI has generated the results.")
    
    with nutrition.form("nutrition_form", border=False):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            calories = st.number_input("Calories", min_value=0,step=1,value=profile["nutrition"].get("calories"))
        with col2:
            protein = st.number_input("Protein", min_value=0,step=1,value=profile["nutrition"].get("protein"))
        with col3:
            fat = st.number_input("Fat", min_value=0,step=1,value=profile["nutrition"].get("fat"))
        with col4:
            carbs = st.number_input("Carbs", min_value=0,step=1,value=profile["nutrition"].get("carbs"))
        
        if st.form_submit_button("Save"):
            with st.spinner():
                st.session_state.profile = update_personal_info(profile, "nutrition", protein=protein, calories=calories, fat=fat, carbs=carbs)
                st.success("Information saved")

@st.fragment
def notes():
    st.subheader("Notes: ")
    for i, note in enumerate(st.session_state.notes):
        cols = st.columns([5, 1])
        with cols[0]:
            st.text(note.get("text"))
        with cols[1]:
            if st.button("Delete", key=i):
                delete_note(note.get("_id"))
                st.session_state.notes.pop(i)
                st.rerun()
    new_note = st.text_input("Add a new note: ")
    if st.button("Add note"):
        if new_note:
            note = add_note(new_note, st.session_state.profile_id)
            st.session_state.notes.append(note)
            st.rerun()

# @st.fragment
# def ask_ai():
#     st.subheader("Ask AI")
#     user_question = st.text_input("Ask AI a question: ")
#     if st.button("Ask AI"):
#         with st.spinner():


def forms():
    if "profile" not in st.session_state:
        profile_id = 1
        profile = get_profile(profile_id)
        if not profile:
            profile_id, profile = create_profile(profile_id)
        
        st.session_state.profile = profile
        st.session_state.profile_id = profile_id

    if "notes" not in st.session_state:
        st.session_state.notes = get_notes(st.session_state.profile_id)

    personal_data_form()
    goals_form()
    diet()
    notes()



# Session State Variables
if "page" not in st.session_state:
    st.session_state.page = "Welcome"

if "show_login_form" not in st.session_state: 
    st.session_state.show_login_form = False

if "username" not in st.session_state:
    st.session_state.username = ""



# Displaying the Welcome Page
if st.session_state.page == "Welcome":
    st.write("\n")
    st.write("\n")
    st.write("\n")
    st.title("Welcome to Health Assistant")
    st.subheader("Mission: To help you stay healthy!")
    st.write("\n")
    st.write("\n")
    st.write("\n")

    col1, col2 =  st.columns(2)

    with col1:
        st.subheader("Have an account?")
        if st.button("Sign in!"):
            st.session_state.show_login_form = True
          
    with col2:
        st.subheader("Don't have an account?")
        if st.button("Create Account"):
            navigate_to("SignUp")
    with col1:
        if st.session_state.show_login_form:
            with st.form(key="sign_in"):
                st.session_state.username = st.text_input("Username")
                password = st.text_input("Password", type= 'password')
                if st.form_submit_button("Submit"):
                    if login_user(st.session_state.username, password): 
                        st.success("Logged in as {}".format(st.session_state.username)) 
                        navigate_to("Profile")
                    else:
                        st.warning("Incorrect Username/Password")

# Displaying the Sign Up Page
elif st.session_state.page == "SignUp":
    st.header("Sign Up")
    name,age,weight,height,gender,st.session_state.username,password = personal_data_form()
    add_user(st.session_state.username,password)
    add_user_info(st.session_state.username,name,age,weight,height,gender)
    navigate_to("Profile")

# Displaying the User's profile page
elif st.session_state.page == "Profile":
    info_c.execute("SELECT name, age, weight, height, gender FROM user_info WHERE username = ?", (st.session_state.username,))
    result = info_c.fetchone()

    if result:
        name, age, weight, height, gender = result

    tab1, tab2, tab3 = st.tabs(["Profile", "Workout", "Diet"])

    with tab1:
        st.header(f"{name}'s Profile")
        st.write("\n")
        st.write("\n")
        st.subheader(f"Name: {name}")
        st.subheader(f"Name: {age}")
        st.subheader(f"Weight: {weight}lbs")
        st.subheader(f"Height: {height}cm")
        st.subheader(f"Weight Loss Plan: {gender}")
    
    with tab2:
        st.header(f"{name}'s Workout Plan")
    
    


