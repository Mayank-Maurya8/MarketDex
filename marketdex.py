# Modules
from stocknews import StockNews
import pyrebase
import streamlit as st
from datetime import date
import yfinance as yf
from prophet import Prophet
from prophet.plot import plot_plotly
from plotly import graph_objs as go
import datetime
from PIL import Image

# Marketdex page1

# style
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# ui
st.title("Welcome to MarketDex")
st.header("Get stock market data, news and share your thoughts to the world with your own blog space. This website will not just provide you the historical data about a company but also provide stock price prediction powered by Facebook Prophet. ")
image = Image.open('banner.png')
st.image(image)


# Configuration key
firebaseConfig = {
    'apiKey': "AIzaSyBEnplVdSyEGpQJr-cnZH5ZZmNkqZ-JsXo",
    'authDomain': "market-dex.firebaseapp.com",
    'projectId': "market-dex",
    'databaseURL': "https://market-dex-default-rtdb.asia-southeast1.firebasedatabase.app/",
    'storageBucket': "market-dex.appspot.com",
    'messagingSenderId': "1000870451994",
    'appId': "1:1000870451994:web:5d20af35b54f36a9692aa3",
    'measurementId': "G-5Y7QVZY6N5"
}

# Firebase Authentication
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

# Database
db = firebase.database()
storage = firebase.storage()

image = Image.open('logo.png')
st.sidebar.image(image)
st.sidebar.title(
    "Start using the features of marketdex and get all the information and future predictions of your favourite stocks. ")


# Authentication
choice = st.sidebar.selectbox('login/Signup', ['Login', 'Sign up'])

# Obtain User Input for email and password
email = st.sidebar.text_input('Please enter your email address')
password = st.sidebar.text_input('Please enter your password', type='password')


# Sign up Block

if choice == 'Sign up':
    handle = st.sidebar.text_input(
        'Please input your app handle name', value='Default')
    submit = st.sidebar.button('Create my account')

    if submit:
        user = auth.create_user_with_email_and_password(email, password)
        st.success('Your account is created suceesfully!')
        st.balloons()
        # Sign in
        user = auth.sign_in_with_email_and_password(email, password)
        db.child(user['localId']).child("Handle").set(handle)
        db.child(user['localId']).child("ID").set(user['localId'])
        st.title('Welcome' + handle)
        st.info('Login via login drop down selection')


# Login Block
if choice == 'Login':
    login = st.sidebar.checkbox('Login')
    if login:
        bio = st.radio('Jump to', ['Stock Dashboard', 'Blog', 'Settings'])
        user = auth.sign_in_with_email_and_password(email, password)
        st.write(
            '<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)

        if bio == 'Settings':
            # Defining the size of image
            def resize_fun(img, new_width):
                width, height = img.size
                ratio = height/width
                new_height = int(ratio*new_width)
                resized_image = img.resize((new_height, new_width))
                return resized_image

            # CHECK FOR IMAGE
            nImage = db.child(user['localId']).child("Image").get().val()
            # IMAGE FOUND
            if nImage is not None:
                # We plan to store all our image under the child image
                Image = db.child(user['localId']).child("Image").get()
                for img in Image.each():
                    img_choice = img.val()
                    # st.write(img_choice)
                st.image(img_choice)
                exp = st.expander('Change Bio and Image')
                # User plan to change profile picture
                with exp:
                    newImgPath = st.text_input(
                        'Enter full path of your profile imgae')
                    upload_new = st.button('Upload')
                    if upload_new:
                        uid = user['localId']
                        fireb_upload = storage.child(uid).put(
                            newImgPath, user['idToken'])
                        a_imgdata_url = storage.child(uid).get_url(
                            fireb_upload['downloadTokens'])
                        db.child(user['localId']).child(
                            "Image").push(a_imgdata_url)
                        st.success('Success!')
            # IF THERE IS NO IMAGE
            else:
                st.info("No profile picture yet")
                newImgPath = st.text_input(
                    'Enter full path of your profile image')
                upload_new = st.button('Upload')
                if upload_new:
                    uid = user['localId']
                    # Stored Initated Bucket in Firebase
                    fireb_upload = storage.child(uid).put(
                        newImgPath, user['idToken'])
                    # Get the url for easy access
                    a_imgdata_url = storage.child(uid).get_url(
                        fireb_upload['downloadTokens'])
                    # Put it in our real time database
                    db.child(user['localId']).child(
                        "Image").push(a_imgdata_url)

   # WORKPLACE FEED PAGE
        elif bio == 'Stock Dashboard':
            # Marketdex page2
            user_input = st.text_input('Enter the stock ticker', 'AAPL')
            retrInfo = yf.Ticker(user_input)
            info = retrInfo.info

            info_company, current, prediction, news = st.tabs(
                ["Information about "+user_input, "Historical data for "+user_input, "Stock price prediction for "+user_input, "Top news of " + user_input])

            # Following companies
            userdata = {}

            key, value = user_input, info['currentPrice']
            userdata[key] = value

            st.sidebar.write("Recently used tickers:"+str(userdata))

            # Information about the company
            with info_company:
                st.write(info['longBusinessSummary'])
                st.write("Sector - "+info['sector'])
                st.write("Website - "+info['website'])
                st.write("Gross Profits - "+str(info['grossProfits']))
                st.write("Market Cap- "+str(info['marketCap']))

            # Historical data
            with current:
                START = "2012-01-01"
                TODAY = date.today().strftime("%Y-%m-%d")

                st.subheader('Here is the information related to '+user_input)

                df = yf.download(user_input, START, TODAY)

                st.subheader("Current Price - "+str(info['currentPrice']))

                # @st.cache_data
                def load_data(ticker):
                    data = yf.download(ticker, START, TODAY)
                    data.reset_index(inplace=True)
                    return data

                data = load_data(user_input)
                col1, col2 = st.columns(2)

                with col1:
                    st.subheader('Historical data')
                    st.write(data.tail())

                with col2:
                    def plot_raw_data():
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(x=data['Date'],
                                                 y=data['Open'], name='stock_open'))
                        fig.add_trace(go.Scatter(x=data['Date'],
                                                 y=data['Close'], name='stock_close'))
                        fig.layout.update(title_text="Time series Data",
                                          xaxis_rangeslider_visible=True)
                        st.plotly_chart(fig)

                    plot_raw_data()

            # Predict forecast with Prophet.
            with prediction:
                n_years = st.slider('Years of prediction:', 1, 4)
                period = n_years * 365
                df_train = data[['Date', 'Close']]
                df_train = df_train.rename(
                    columns={"Date": "ds", "Close": "y"})

                m = Prophet()
                m.fit(df_train)
                future = m.make_future_dataframe(periods=period)
                forecast = m.predict(future)

                # Show and plot forecast
                st.subheader('Forecast data')
                st.write(forecast.tail())

                st.subheader(f'Forecast plot for {n_years} years')
                fig1 = plot_plotly(m, forecast)
                st.plotly_chart(fig1)
                st.write(
                    "The plot visualization - Historical Values (Black dot) , Blue Shaded area (High-confidence area) , Blue Line (Forecast)")

                st.subheader("Forecast components")
                fig2 = m.plot_components(forecast)
                st.write(fig2)

            with news:
                st.header(f'News of {user_input}')
                sn = StockNews(user_input, save_news=False)
                df_news = sn.read_rss()
                for i in range(15):
                    st.subheader(f'News {i+1}')
                    st.write(df_news['published'][i])
                    st.write(df_news['title'][i])
                    st.write(df_news['summary'][i])
                    title_sentiment = df_news['sentiment_title'][i]
                    st.write(f'Title Sentiment {title_sentiment}')
                    news_sentiment = df_news['sentiment_summary'][i]
                    st.write(f'News Sentiment {news_sentiment}')

        elif bio == 'Blog':
            col1, col2 = st.columns(2)

            # col for Profile picture
            with col1:
                nImage = db.child(user['localId']).child("Image").get().val()
                if nImage is not None:
                    val = db.child(user['localId']).child("Image").get()
                    for img in val.each():
                        img_choice = img.val()
                    st.image(img_choice, use_column_width=True)
                else:
                    st.info(
                        "No profile picture yet. Go to Edit Profile and choose one!")

                post = st.text_input(
                    "Let's share my current mood as a post!", max_chars=100)
                add_post = st.button('Share Posts')
            if add_post:
                now = datetime.date.today()
                dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
                post = {'Post:': post,
                        'Timestamp': dt_string}
                results = db.child(user['localId']).child("Posts").push(post)
                st.balloons()

            # This coloumn for the post Display
            with col2:

                all_posts = db.child(user['localId']).child("Posts").get()
                if all_posts.val() is not None:
                    for Posts in reversed(all_posts.each()):
                        # st.write(Posts.key()) # Morty
                        st.code(Posts.val(), language='')

            all_users = db.get()
            res = []
            # Store all the users handle name
            for users_handle in all_users.each():
                k = users_handle.val()
                k = k.get("Handle")
                res.append(k)
            # Total users
            nl = len(res)
            st.write('Total users here: ' + str(nl))

            # Allow the user to choose which other user he/she wants to see
            choice = st.selectbox('My Collegues', res)
            push = st.button('Show Profile')

            # Show the choosen Profile
            if push:
                for users_handle in all_users.each():
                    k = users_handle.val()
                    k = k.get("Handle")
                    #
                    if k == choice:
                        lid = users_handle.val()
                        lid = lid.get("ID")

                        handlename = db.child(lid).child("Handle").get().val()

                        st.markdown(handlename, unsafe_allow_html=True)

                        col1, col2 = st.columns(2)

                        with col1:
                            nImage = db.child(lid).child("Image").get().val()
                            if nImage is not None:
                                val = db.child(lid).child("Image").get()
                                for img in val.each():
                                    img_choice = img.val()
                                    st.image(img_choice)
                            else:
                                st.info(
                                    "No profile picture yet. Go to Edit Profile and choose one!")

                        with col2:

                            # All posts
                            all_posts = db.child(lid).child("Posts").get()
                            if all_posts.val() is not None:
                                for Posts in reversed(all_posts.each()):
                                    st.code(Posts.val(), language='')
