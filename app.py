from flask import Flask, request, redirect, url_for, render_template, session, flash
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # For session encryption
app.permanent_session_lifetime = timedelta(minutes=10)

data = {}

@app.before_request
def make_session_permanent():
    session.permanent = True


@app.route('/')
def welcome():
    return render_template('welcome.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('uname')
        password = request.form.get('password')
        name = request.form.get('name')
        accountno = request.form.get('accno')
        cardno = request.form.get('cardno')
        pinno = request.form.get('pin')
        mobile = request.form.get('mobileno')
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
