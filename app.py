from flask import Flask, request, redirect, url_for, render_template, session, flash
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # For session encryption
app.permanent_session_lifetime = timedelta(minutes=10)

data = {}
admin_data = {}

@app.before_request
def make_session_permanent():
    session.permanent = True

    # -------------------- Admin Routes --------------------

@app.route('/admin')
def admin():
    return render_template('admin_home.html')    

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
    return render_template('admin_register.html')


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
    return render_template('admin_viewuserinfo.html', user=data[username], ausername=username)


@app.route('/admin/user/<username>/transactions')
def admin_user_transactions(username):
    if 'admin' not in session:
        return redirect(url_for('adminlogin'))
    return render_template('admin_userstament.html', 
                           username=username, 
                           admin=session['admin'],
                           transactions=reversed(data[username]['transactions']))


@app.route('/admin/adduser', methods=['GET', 'POST'])
def admin_add_user():
    if 'admin' not in session:
        return redirect(url_for('adminlogin'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        accno = request.form.get('accno')
        mobile = request.form.get('mobileno')
        email = request.form.get('emailid')
        initial_deposit = int(request.form.get('initial_deposit', 500))
        
        # Use name as username for simplicity or generate one
        username = name.lower().replace(" ", "")
        
        if username not in data:
            data[username] = {
                'name': name,
                'account_number': accno,
                'password': 'password123', # Default password for new users
                'card_number': 'ST' + accno[-4:], 
                'pin_no': '1234',
                'mobile_number': mobile,
                'email_id': email,
                'amount': initial_deposit,
                'transactions': [{
                    'type': 'Initial Deposit',
                    'amount': initial_deposit,
                    'balance': initial_deposit,
                    'time': datetime.now().strftime('%Y-%m-%d %H:%M')
                }]
            }
            flash(f'User {name} enrolled successfully!')
            return redirect(url_for('admin_view_users'))
        else:
            flash('User already exists.')
            
    return render_template('admin_adduser.html', admin=session['admin'])


@app.route('/admin/profile/<admin>')
def admin_profile(admin):
    return f"Admin Profile for {admin} (add template if needed)"


@app.route('/admin/settings/<admin>')
def admin_settings(admin):
    return f"Admin Settings for {admin} (add template if needed)"

# -------------------- User Routes --------------------

@app.route('/')
def welcome():
    return render_template('welcome.html')
    
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('uname')
        password = request.form.get('password')
        name = request.form.get('name', username) # Fallback to username if name is missing
        accountno = request.form.get('accno', 'ST-' + str(datetime.now().timestamp())[:10])
        cardno = request.form.get('cardno', 'XXXX-XXXX-XXXX-' + str(datetime.now().timestamp())[-4:])
        pinno = request.form.get('pin', '1234')
        mobile = request.form.get('mobileno', '0000000000')
        email = request.form.get('emailid')

        if username not in data:
            data[username] = {
                'name': name,
                'account_number': accountno,
                'password': password,
                'card_number': cardno,
                'pin_no': pinno,
                'mobile_number': mobile,
                'email_id': email,
                'amount': 500,
                'transactions': []
            }
            flash('Registration successful! Please login.')
            return redirect(url_for('login'))
        else:
            flash('Username already exists. Try a different one.')
            return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('uname')
        password = request.form.get('password')

        if username not in data:
            flash('User does not exist. Please register first.')
            return redirect(url_for('register'))
        elif data[username]['password'] != password:
            flash('Invalid password. Please try again.')
            return redirect(url_for('login'))
        session['user'] = username
        flash('Login successful!')
        return redirect(url_for('dashboard', pusername=username))

    return render_template('login.html')


@app.route('/dashboard/<pusername>')
def dashboard(pusername):
    if 'user' not in session or session['user'] != pusername:
        flash("Please login to continue.")
        return redirect(url_for('login'))

    return render_template('dashboard.html',
                           ausername=pusername,
                           wbalanceamount=int(data[pusername]['amount']))


@app.route('/balance/<busername>')
def balance(busername):
    if 'user' not in session or session['user'] != busername:
        return redirect(url_for('login'))

    return render_template('balance.html',
                           abalance_amount=data[busername]['amount'],
                           ausername=busername)


@app.route('/transactions/<username>')
def transaction(username):
    if 'user' not in session or session['user'] != username:
        return redirect(url_for('login'))

    return render_template('transaction.html', ausername=username, username=username)


@app.route('/deposit/<dusername>', methods=['GET', 'POST'])
def deposit(dusername):
    if 'user' not in session or session['user'] != dusername:
        return redirect(url_for('login'))

    if request.method == 'POST':
        udamount = int(request.form.get('damount'))
        if udamount <= 0:
            flash("Invalid Amount")
        elif udamount > 100000:
            flash("Deposit Limit Exceeded (₹1,00,000 max)")
        else:
            previous_balance = data[dusername]['amount']
            data[dusername]['amount'] += udamount
            data[dusername]['transactions'].append({
                'type': 'Deposit',
                'amount': udamount,
                'balance': data[dusername]['amount'],
                'time': datetime.now().strftime('%Y-%m-%d %H:%M')
            })
            flash(f"₹{udamount} deposited successfully!")
            return render_template('balance.html',
                                   abalance_amount=data[dusername]['amount'],
                                   prev_balance=previous_balance,
                                   amount=udamount,
                                   action='deposit',
                                   ausername=dusername)

    return render_template('deposit.html', ausername=dusername)


@app.route('/withdraw/<wusername>', methods=['GET', 'POST'])
def withdraw(wusername):
    if 'user' not in session or session['user'] != wusername:
        return redirect(url_for('login'))

    current_balance = data[wusername]['amount']

    if request.method == 'POST':
        uwamount = int(request.form.get('wamount'))
        if uwamount <= 0:
            flash("Amount must be greater than 0")
        elif uwamount > current_balance:
            flash(f'Insufficient Balance: ₹{current_balance}')
        elif current_balance - uwamount < 500:
            flash(f'Minimum ₹500 balance must be maintained after withdrawal.')
        else:
            data[wusername]['amount'] -= uwamount
            data[wusername]['transactions'].append({
                'type': 'Withdraw',
                'amount': uwamount,
                'balance': data[wusername]['amount'],
                'time': datetime.now().strftime('%Y-%m-%d %H:%M')
            })
            flash(f"₹{uwamount} withdrawn successfully!")
            return render_template('balance.html',
                                   abalance_amount=data[wusername]['amount'],
                                   prev_balance=current_balance,
                                   amount=uwamount,
                                   action='withdraw',
                                   ausername=wusername)

    return render_template('withdraw.html', ausername=wusername)


@app.route('/transfer/<username>', methods=['GET', 'POST'])
def transfer(username):
    if 'user' not in session or session['user'] != username:
        return redirect(url_for('login'))

    sender_acc = data[username]['account_number']

    if request.method == 'POST':
        receiver_acc = request.form.get('receiver_accno')
        amount = int(request.form.get('amount'))

        if amount <= 0:
            flash("Invalid transfer amount.")
        elif receiver_acc == sender_acc:
            flash("Cannot transfer to your own account.")
        else:
            receiver = None
            for uname, details in data.items():
                if details['account_number'] == receiver_acc:
                    receiver = uname
                    break

            if receiver is None:
                flash("Receiver account not found.")
            elif data[username]['amount'] - amount < 500:
                flash("Transfer denied. Minimum ₹500 balance must remain.")
            else:
                data[username]['amount'] -= amount
                data[receiver]['amount'] += amount

                now = datetime.now().strftime('%Y-%m-%d %H:%M')

                data[username]['transactions'].append({
                    'type': 'Transfer Sent',
                    'amount': amount,
                    'balance': data[username]['amount'],
                    'time': now,
                    'to': receiver_acc
                })

                data[receiver]['transactions'].append({
                    'type': 'Transfer Received',
                    'amount': amount,
                    'balance': data[receiver]['amount'],
                    'time': now,
                    'from': sender_acc
                })

                flash(f"Success: ₹{amount} transferred to account {receiver_acc}")
                return redirect(url_for('dashboard', pusername=username))

    return render_template('transfer.html', ausername=username, sender_accno=sender_acc)


@app.route('/accountstatement/<username>')
def accountstatement(username):
    if 'user' not in session or session['user'] != username:
        return redirect(url_for('login'))

    user_txns = data[username].get('transactions', [])
    return render_template('statement.html', username=username, ausername=username, transactions=reversed(user_txns))


@app.route('/pin/<username>', methods=['GET', 'POST'])
def pinchange(username):
    if 'user' not in session or session['user'] != username:
        return redirect(url_for('login'))

    if request.method == 'POST':
        newpin = request.form.get('newpin')
        data[username]['pin_no'] = newpin
        flash("PIN changed successfully!")
        return redirect(url_for('dashboard', pusername=username))

    return render_template('changepin.html', ausername=username)


@app.route('/profile/<username>')
def profile(username):
    if 'user' not in session or session['user'] != username:
        return redirect(url_for('login'))

    return render_template('profile.html', ausername=username, user=data[username])


@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for('welcome'))


@app.route('/accountdeletion/<pusername>')
def deleteaccount(pusername):
    if 'user' not in session or session['user'] != pusername:
        return redirect(url_for('login'))

    data.pop(pusername)
    session.clear()
    flash("Account deleted successfully.")
    return redirect(url_for('welcome'))


if __name__ == '__main__':
    app.run(debug=True,use_reloader=True)
