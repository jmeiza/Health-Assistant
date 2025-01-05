import streamlit as st
import sqlite3
import bcrypt


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
    info_c.execute("INSERT INTO user_info (username, name, weight, height, plan) VALUES (?, ?, ?, ?, ?)", (username,name,age,weight,height,gender))
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
        name = st.text_input("Name")
        age = st.number_input("Age", min_value=1, max_value=120, step=1)
        weight = st.number_input("Weight (kg)", min_value=0.0, max_value=300.0, step=0.1)
        height = st.number_input("Height (cm)", min_value=0.0, max_value=250.0, step=0.1)
        gender = st.radio('Gender', ["Male", "Female", "Other"])
        username = st.text_input("Username")
        password = st.text_input("Password")

        personal_data_submit = st.form_submit_button("Save")
        if personal_data_submit:
            if all([name,age,weight,height,gender]):
                with st.spinner():
                    #save the data
                    st.success('Information saved')
            else:
                st.warning("Please fill in all of the data")
    return name,age,weight,height,gender,username,password


# Session State Variables
if "page" not in st.session_state:
    st.session_state.page = "Welcome"

if "show_login_form" not in st.session_state: 
    st.session_state.show_login_form = False

if "username" not in st.session_state:
    st.session_state.username = ""
##########################################


# Displaying the Welcome Page
if st.session_state.page == "Welcome":
    st.write("\n")
    st.write("\n")
    st.write("\n")
    st.title("Welcome to Food Health Tracker")
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
    
    


