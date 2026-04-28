from flask import Flask, request, redirect, url_for, render_template, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Required for session

data = {}         # User data
admin_data = {}   # Admin data


# -------------------- Common Routes --------------------

@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('welcome'))


# -------------------- User Routes --------------------

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('uname')
        if username not in data:
            data[username] = {
                'name': request.form.get('name'),
                'account_number': request.form.get('accno'),
                'password': request.form.get('password'),
                'card_number': request.form.get('cardno'),
                'pin_no': request.form.get('pin'),
                'mobile_number': request.form.get('mobileno'),
                'email_id': request.form.get('emailid'),
                'amount': 500,
                'transactions': []
            }
            return redirect(url_for('login'))
        else:
            return 'User already exists'
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('uname')
        password = request.form.get('password')
        if username in data and data[username]['password'] == password:
            return redirect(url_for('dashboard', pusername=username))
        return 'Invalid credentials'
    return render_template('login.html')


@app.route('/dashboard/<pusername>')
def dashboard(pusername):
    return render_template('dashboard.html',
                           ausername=pusername,
                           wbalanceamount=int(data[pusername]['amount']))


@app.route('/balance/<busername>')
def balance(busername):
    return render_template('balance.html',
                           abalance_amount=data[busername]['amount'],
                           ausername=busername)


@app.route('/transactions/<username>')
def transaction(username):
    return render_template('transaction.html', ausername=username, username=username)


@app.route('/deposit/<dusername>', methods=['GET', 'POST'])
def deposit(dusername):
    if request.method == 'POST':
        udamount = int(request.form.get('damount'))
        if udamount <= 0 or udamount > 100000:
            return 'Invalid amount'
        previous_balance = data[dusername]['amount']
        data[dusername]['amount'] += udamount
        data[dusername]['transactions'].append({
            'type': 'Deposit',
            'amount': udamount,
            'balance': data[dusername]['amount'],
            'time': datetime.now().strftime('%Y-%m-%d %H:%M')
        })
        return render_template('balance.html',
                               abalance_amount=data[dusername]['amount'],
                               prev_balance=previous_balance,
                               amount=udamount,
                               action='deposit',
                               ausername=dusername)
    return render_template('deposit.html', ausername=dusername)


@app.route('/withdraw/<wusername>', methods=['GET', 'POST'])
def withdraw(wusername):
    if request.method == 'POST':
        uwamount = int(request.form.get('wamount'))
        current_balance = data[wusername]['amount']
        if uwamount <= 0 or uwamount > current_balance or current_balance - uwamount < 500:
            return 'Invalid or insufficient funds'
        data[wusername]['amount'] -= uwamount
        data[wusername]['transactions'].append({
            'type': 'Withdraw',
            'amount': uwamount,
            'balance': data[wusername]['amount'],
            'time': datetime.now().strftime('%Y-%m-%d %H:%M')
        })
        return render_template('balance.html',
                               abalance_amount=data[wusername]['amount'],
                               prev_balance=current_balance,
                               amount=uwamount,
                               action='withdraw',
                               ausername=wusername)
    return render_template('withdraw.html', ausername=wusername)


@app.route('/transfer/<username>', methods=['GET', 'POST'])
def transfer(username):
    sender_acc = data[username]['account_number']
    if request.method == 'POST':
        receiver_acc = request.form.get('receiver_accno')
        amount = int(request.form.get('amount'))
        if amount <= 0 or receiver_acc == sender_acc:
            return 'Invalid transfer'
        receiver = next((u for u, v in data.items() if v['account_number'] == receiver_acc), None)
        if not receiver or data[username]['amount'] - amount < 500:
            return 'Transfer failed'
        data[username]['amount'] -= amount
        data[receiver]['amount'] += amount
        now = datetime.now().strftime('%Y-%m-%d %H:%M')
        data[username]['transactions'].append({
            'type': 'Transfer Sent', 'amount': amount, 'balance': data[username]['amount'], 'time': now, 'to': receiver_acc
        })
        data[receiver]['transactions'].append({
            'type': 'Transfer Received', 'amount': amount, 'balance': data[receiver]['amount'], 'time': now, 'from': sender_acc
        })
        return f"₹{amount} transferred to {receiver_acc}"
    return render_template('transfer.html', ausername=username, sender_accno=sender_acc)


@app.route('/accountstatement/<username>')
def accountstatement(username):
    return render_template('statement.html',
                           username=username,
                           ausername=username,
                           transactions=reversed(data[username]['transactions']))


@app.route('/pin/<username>')
def pinchange(username):
    return render_template('changepin.html', ausername=username)


@app.route('/profile/<username>')
def profile(username):
    return render_template('profile.html', ausername=username, user=data[username])


@app.route('/accountdeletion/<pusername>')
def deleteaccount(pusername):
    data.pop(pusername, None)
    return redirect(url_for('welcome'))


# -------------------- Admin Routes --------------------

@app.route('/admin/register', methods=['GET', 'POST'])
def adminregister():
    if request.method == 'POST':
        uname = request.form.get('uname')
        if uname not in admin_data:
            admin_data[uname] = {
                'password': request.form.get('password'),
                'email': request.form.get('email')
            }
            return redirect(url_for('adminlogin'))
        return 'Admin already exists'
    return render_template('admin_registration.html')


@app.route('/admin/login', methods=['GET', 'POST'])
def adminlogin():
    if request.method == 'POST':
        uname = request.form.get('uname')
        password = request.form.get('password')
        if uname in admin_data and admin_data[uname]['password'] == password:
            session['admin'] = uname
            return redirect(url_for('admin_dashboard'))
        return 'Invalid admin credentials'
    return render_template('admin_login.html')


@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin' not in session:
        return redirect(url_for('adminlogin'))
    return render_template('admin_dashboard.html', admin=session['admin'])


@app.route('/admin/viewallusers')
def admin_view_users():
    if 'admin' not in session:
        return redirect(url_for('adminlogin'))
    return render_template('admin_viewallusers.html', admin=session['admin'], users=[
        {'username': uname, 'fullname': details['name'], 'account_number': details['account_number']}
        for uname, details in data.items()
    ])


@app.route('/admin/user/<username>/info')
def admin_user_info(username):
    if 'admin' not in session:
        return redirect(url_for('adminlogin'))
    return render_template('profile.html', user=data[username], ausername=username)


@app.route('/admin/user/<username>/transactions')
def admin_user_transactions(username):
    if 'admin' not in session:
        return redirect(url_for('adminlogin'))
    return render_template('statement.html', username=username, ausername=username,
                           transactions=reversed(data[username]['transactions']))


@app.route('/admin/profile/<admin>')
def admin_profile(admin):
    return f"Admin Profile for {admin} (add template if needed)"


@app.route('/admin/settings/<admin>')
def admin_settings(admin):
    return f"Admin Settings for {admin} (add template if needed)"


# -------------------- Run App --------------------

if __name__ == '__main__':
    app.run(debug=True)
