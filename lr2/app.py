from flask import Flask, render_template, request, make_response
import re

app = Flask(__name__)
application = app

def get_cookie():
    return {
        'cookie': 'This_is_cookie!'
    }

def process_phone_number(raw_number):
    digits = re.sub(r'[ ()-.+]', '', raw_number)
    if not digits:
        return digits
    if not digits.isdigit():
        return 'Недопустимый ввод. В номере телефона встречаются недопустимые символы.'
    if not (len(digits) == 10 or len(digits) == 11 and digits[0] in '78'):
        return 'Недопустимый ввод. Неверное количество цифр.'
    if (len(digits) == 11):
        digits = digits[1:]
    return f'8-{digits[0:3]}-{digits[3:6]}-{digits[6:8]}-{digits[8:10]}'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/url_params')
def url_params():
    return render_template('url_params.html', params = request.args)

@app.route('/request_headers')
def request_headers():
    return render_template('request_headers.html', headers = request.headers)

@app.route('/cookie')
def cookie():
    response = make_response(render_template('cookie.html', cookies = request.cookies))
    for key, value in get_cookie().items():
        if request.cookies.get(key):
            response.delete_cookie(key)
        else:
            response.set_cookie(key, value)
    return response

@app.route('/form_params', methods=['GET', 'POST'])
def form_params():
    return render_template('form_params.html', form = request.form)

@app.route('/error_handling_form', methods=['GET', 'POST'])
def error_handling_form():
    response = process_phone_number(request.form.get('phone_number', ''))
    is_valid = True if re.match(r'^8-\d{3}-\d{3}-\d{2}-\d{2}$', response) else False
    return render_template('error_handling_form.html', form = request.form, response = response, is_valid = is_valid)
