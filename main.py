from flask import Flask, request, redirect, render_template, send_from_directory, url_for, jsonify, flash
from secrets import token_urlsafe
from flask_login import LoginManager, UserMixin, login_user, current_user, login_required, logout_user
import csv
import socket
import os

from datetime import datetime, timedelta
from fileio import *

os.makedirs('data', exist_ok=True)

try:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.settimeout(0)
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]

except:
    IP = "140.113.121.146"
    IP = "127.0.0.1"

PORT = 5000
ourIP = f"http://{IP}:{PORT}/"

app = Flask(__name__)
app.jinja_env.variable_start_string = '[[['
app.jinja_env.variable_end_string = ']]]'

app.secret_key = 'handsomeKuo'
login_manager = LoginManager(app)


class User(UserMixin):
    """  
    設置一： 只是假裝一下，所以單純的繼承一下而以 如果我們希望可以做更多判斷，
    如is_administrator也可以從這邊來加入 
    """
    pass


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(ourIP+request.path[1:]+'/login')


@app.route("/", methods=["GET"])
def get_homepage():
    return render_template("startup.html")


@app.route("/", methods=["POST"])
def send_selection_in_homepage():
    print(request.form)
    eventTitle = request.form["eventTitle"]
    selected_dates = request.form["selected_dates"]

    days = []
    for day in selected_dates.split(","):
        day = datetime.strptime(day, "%Y-%m-%d").date()
        days.append(str(day))

    customCandidates = []
    if request.form['voteCat'] and ('設定其他選項' in request.form):
        voteCat = request.form['voteCat']
        for key, value in request.form.items():
            if value == 'cv':
                customCandidates.append(key)
    else:
        voteCat = ""

    selected_times = []
    if '自訂時間選項' in request.form:
        for key, value in request.form.items():
            if value == 'st':
                selected_times.append(key)

    if len(selected_times) == 0:
        selected_times = ["whole-day"]

    keys = []
    for day in days:
        for option in selected_times:
            keys.append(day+' : '+option)

    while True:
        urlToken = token_urlsafe(16)
        if not os.path.isdir(f'data/{urlToken}'):
            break
    os.mkdir(f'data/{urlToken}')

    init_users_file(urlToken)
    init_selections_file(urlToken, len(keys))
    init_config_file(urlToken, eventTitle, keys, voteCat, customCandidates)
    if voteCat:
        init_custom_selections_file(urlToken, len(customCandidates))

    return redirect(ourIP+urlToken+'/login')


@app.route("/<token>/login", methods=["GET"])
def get_login_interface(token):
    usr = current_user.get_id()
    if usr is None:
        return render_voting_page(token)
    else:
        return redirect(ourIP+token)


def check_password(usernames, passwords, name, pswd):
    for usr_index in range(len(usernames)):
        username = usernames[usr_index]
        password = passwords[usr_index]
        if name == username:
            return password == pswd
    raise KeyError(f"No {name} in usernames")


@app.route("/<token>/login", methods=["POST"])
def send_id_passwd(token):
    email = request.form['email']
    usernames, passwords = get_users_file(token)
    is_new_guy = email not in usernames
    if is_new_guy:
        append_users_file(token, email, request.form['password'])
        append_selections_file(token)
        append_custom_selections_file(token)

    if is_new_guy or check_password(usernames, passwords, email, request.form['password']):
        # 實作User類別
        user = User()
        # 設置id就是email
        user.id = token + email
        # 這邊，透過login_user來記錄user_id，如下了解程式碼的login_user說明。
        login_user(user)
        # 登入成功，轉址
        return redirect(url_for("voting", token=token))

    # need to implement reinputting id/passwd
    return render_voting_page(token, wrong_password=True)


@app.route("/<token>", methods=["POST"])
@login_required
def voting(token):
    post_data = request.get_json()
    print('voting', post_data)
    if post_data['data'] == 'logout':
        logout_user()
        msg = jsonify({'success': 200})
        return msg
    elif post_data['data'] == 'pressed':
        option = post_data['option']

        usr = current_user.get_id()[22:]
        usernames, _ = get_users_file(token)
        for i, usrname in enumerate(usernames):
            if usrname == usr:
                usr_index = i

        _, keys, voteCat, customCandidates = get_config_file(token)

        if option[:10] == "customVote":
            for i, key in enumerate(customCandidates):
                if key == option[10:]:
                    key_index = i

            edit_custom_selections_file(token, usr_index, key_index)

        else:
            for i, key in enumerate(keys):
                if key == option:
                    key_index = i

            edit_selections_file(token, usr_index, key_index)

        msg = jsonify({'success': 200, 'user': usr, 'option': option})
        return msg


@app.route("/<token>", methods=["GET"])
@login_required
def get_voting_page(token):
    last_token = current_user.get_id()[:22]
    if token != last_token:
        logout_user()
        return redirect(url_for("get_login_interface", token=token))

    return render_voting_page(token)


def get_days_and_times(keys):
    days = []
    times = []
    for key in keys:
        day, time = key.split(" : ")
        if day not in days:
            days.append(day)
        if time not in times:
            times.append(time)
    return days, times


def render_voting_page(token, wrong_password=False):
    eventTitle, keys, voteCat, customCandidates = get_config_file(token)
    usernames, _ = get_users_file(token)

    options = get_available(token, keys, usernames)
    if voteCat != "":
        custom_options = get_custom_available(
            token, customCandidates, usernames)
    else:
        custom_options = {}

    days, times = get_days_and_times(keys)
    usr = current_user.get_id()
    if usr is None:
        did_login = False
        usr = ""
    else:
        usr = usr[22:]
        did_login = True

    return render_template(
        "voting.html",
        did_login=str(did_login).lower(),
        eventTitle=eventTitle,
        days=days,
        times=times,
        usr=usr,
        values=options,
        custom_options=custom_options,
        usernames=usernames,
        wrong_password=str(wrong_password).lower(),
        voteCat=voteCat,
        customCandidates=customCandidates,
    )


@login_manager.user_loader
def user_loader(email):
    """
    設置二： 透過這邊的設置讓flask_login可以隨時取到目前的使用者id   
    :param email:官網此例將email當id使用，賦值給予user.id    
    """
    user = User()
    user.id = email
    return user


''' search for how to write shorter here later '''


@app.route("/favicon.ico")
def show_ricardo1():
    return show_ricardo()


@app.route("/<token>/favicon.ico")
def show_ricardo2(token):
    return show_ricardo()


def show_ricardo():
    return send_from_directory('./static', 'ricardo.ico', mimetype='image/vnd.microsoft.icon')


@app.route("/index.css")
def send_index_css1():
    return send_index_css()


@app.route("/<token>/index.css")
def send_index_css2(token):
    return send_index_css()


def send_index_css():
    return send_from_directory("static", "template.css")


if __name__ == '__main__':
    app.run('0.0.0.0', port=PORT, debug=True)
