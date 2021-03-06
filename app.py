from flask import Flask, render_template, request, redirect, url_for, flash, make_response, jsonify
from scraper import run, get_student_course, get_student_progress, get_graduate_info, get_course_table
import requests
import json


app = Flask(__name__)
app.config['SECRET_KEY'] = '3c178af81e8f023e05fc72c56757417158aaeff46e23263df647d9fdc4ad2452'
app.config['JSON_AS_ASCII'] = False

# get course data from API server
url = 'https://4129db66-df60-48ee-a1d1-daf67fe23ce3.mock.pstmn.io'
response = requests.get(url)
courseData = json.loads(response.text)


@app.route('/')
def index():
    return render_template('terms_of_service.html')


@app.route('/home')
def home():
    cookieAccount = request.cookies.get('Account')
    cookiePassword = request.cookies.get('Password')
    cookieName = request.cookies.get('Name')

    userName = '訪客'
    userId = 'A0000000'
    hasLoggedIn = 'False'

    if cookieAccount != None and cookiePassword != None:
        hasLoggedIn = 'True'
        userName = cookieName
        userId = cookieAccount
    return render_template('home.html',
                           userName=userName,
                           userId=userId,
                           hasLoggedIn=hasLoggedIn,
                           courseData=courseData)


@app.route('/profile')
def profile():
    cookieAccount = request.cookies.get('Account')
    cookiePassword = request.cookies.get('Password')
    cookieName = request.cookies.get('Name')

    if cookieAccount == None or cookiePassword == None:
        return redirect(url_for('login'))

    userName = cookieName
    studentCourseData = get_student_course(run(cookieAccount, cookiePassword))
    studentCourseCredits = get_student_progress(
        run(cookieAccount, cookiePassword))
    studentGraduateInfo = get_graduate_info(cookieAccount, cookiePassword)

    userPicUrl = '/static/img/user.png'
    r = requests.get(
        'http://elearning.nuk.edu.tw/_uploadfiles/stuphoto/' + cookieAccount.lower() + '.jpg')
    if r.status_code == 200:
        userPicUrl = 'http://elearning.nuk.edu.tw/_uploadfiles/stuphoto/' + \
            cookieAccount.lower() + '.jpg'

    return render_template('profile.html',
                           userName=userName,
                           userId=cookieAccount,
                           userPicUrl=userPicUrl,
                           studentGraduateInfo=studentGraduateInfo,
                           studentCourseData=studentCourseData,
                           studentCourseCredits=studentCourseCredits)


@app.route('/guide')
def guide():
    cookieAccount = request.cookies.get('Account')
    cookiePassword = request.cookies.get('Password')
    cookieName = request.cookies.get('Name')

    userName = '訪客'
    userId = 'A0000000'
    hasLoggedIn = 'False'

    if cookieAccount != None and cookiePassword != None:
        hasLoggedIn = 'True'
        userName = cookieName
        userId = cookieAccount

    return render_template('how_to_use.html',
                           userName=userName,
                           userId=userId,
                           hasLoggedIn=hasLoggedIn)


@app.route('/login', methods=['GET', 'POST'])
def login():
    cookieAccount = request.cookies.get('Account')
    cookiePassword = request.cookies.get('Password')
    if cookieAccount != None and cookiePassword != None:
        return redirect(url_for('profile'))

    if request.method == 'GET':
        return render_template('login.html')

    account = request.form['account']
    password = request.form['password']

    res = requests.post(
        'https://aca.nuk.edu.tw/Student2/Menu1.asp',
        {
            'Account': account,
            'Password': password
        })
    res.encoding = 'big5'

    if res.headers['Content-Length'] != '992':
        studentGraduateInfo = get_graduate_info(account, password)  # 取得學生基本資料
        response = make_response(redirect(url_for('profile')))
        response.set_cookie('Name', studentGraduateInfo['student_name'])
        response.set_cookie('Account', account)
        response.set_cookie('Password', password)
        return response
    else:
        flash('教務系統說登入錯誤', 'danger')
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    if request.cookies.get('Account') != None:
        res = make_response(redirect(url_for('home')))
        res.delete_cookie('Account')
        res.delete_cookie('Password')
        res.delete_cookie('Name')
        return res
    else:
        return redirect(url_for('home'))


# ===== 手機頁面路由 ===== #

@app.route('/m/home')
def mobile_home():
    cookieAccount = request.cookies.get('Account')
    cookiePassword = request.cookies.get('Password')
    cookieName = request.cookies.get('Name')

    userName = '訪客'
    userId = 'A0000000'
    hasLoggedIn = 'False'

    if cookieAccount != None and cookiePassword != None:
        hasLoggedIn = 'True'
        userName = cookieName
        userId = cookieAccount
    return render_template('mobile_home.html',
                           userName=userName,
                           userId=userId,
                           hasLoggedIn=hasLoggedIn,
                           courseData=courseData)


@app.route('/m/profile')
def mobile_profile():
    cookieAccount = request.cookies.get('Account')
    cookiePassword = request.cookies.get('Password')
    cookieName = request.cookies.get('Name')

    if cookieAccount == None or cookiePassword == None:
        return redirect(url_for('mobile_login'))

    userName = cookieName
    studentCourseData = get_student_course(run(cookieAccount, cookiePassword))
    studentCourseCredits = get_student_progress(
        run(cookieAccount, cookiePassword))
    studentGraduateInfo = get_graduate_info(cookieAccount, cookiePassword)

    userPicUrl = '/static/img/user.png'
    r = requests.get(
        'http://elearning.nuk.edu.tw/_uploadfiles/stuphoto/' + cookieAccount.lower() + '.jpg')
    if r.status_code == 200:
        userPicUrl = 'http://elearning.nuk.edu.tw/_uploadfiles/stuphoto/' + \
            cookieAccount.lower() + '.jpg'

    return render_template('mobile_profile.html',
                           userName=userName,
                           userId=cookieAccount,
                           userPicUrl=userPicUrl,
                           studentGraduateInfo=studentGraduateInfo,
                           studentCourseData=studentCourseData,
                           studentCourseCredits=studentCourseCredits)


@app.route('/m/login', methods=['GET', 'POST'])
def mobile_login():
    cookieAccount = request.cookies.get('Account')
    cookiePassword = request.cookies.get('Password')
    if cookieAccount != None and cookiePassword != None:
        return redirect(url_for('mobile_profile'))

    if request.method == 'GET':
        return render_template('login.html')

    account = request.form['account']
    password = request.form['password']

    res = requests.post(
        'https://aca.nuk.edu.tw/Student2/Menu1.asp',
        {
            'Account': account,
            'Password': password
        })
    res.encoding = 'big5'

    if res.headers['Content-Length'] != '992':
        studentGraduateInfo = get_graduate_info(account, password)  # 取得學生基本資料
        response = make_response(redirect(url_for('mobile_profile')))
        response.set_cookie('Name', studentGraduateInfo['student_name'])
        response.set_cookie('Account', account)
        response.set_cookie('Password', password)
        return response
    else:
        flash('教務系統說登入錯誤', 'danger')
        return redirect(url_for('mobile_login'))


@app.route('/m/logout')
def mobile_logout():
    if request.cookies.get('Account') != None:
        res = make_response(redirect(url_for('mobile_home')))
        res.delete_cookie('Account')
        res.delete_cookie('Password')
        res.delete_cookie('Name')
        return res
    else:
        return redirect(url_for('mobile_home'))


# ===== API ===== #

@app.route('/getInfo/<id>&<password>')
def getInfo(id, password):
    return jsonify(get_graduate_info(id, password))


@app.route('/getCourse/<id>&<password>')
def getCourse(id, password):
    return jsonify(get_student_course(run(id, password)))


@app.route('/getProgress/<id>&<password>')
def getProgress(id, password):
    return jsonify(get_student_progress(run(id, password)))


@app.route('/getTable/<id>&<password>')
def getTable(id, password):
    return jsonify(get_course_table(id, password))


if __name__ == "__main__":
    app.run(debug=True)
