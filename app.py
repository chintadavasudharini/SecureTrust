from flask import Flask, request, redirect, url_for, render_template, session, flash
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # For session encryption
app.permanent_session_lifetime = timedelta(minutes=10)

data = {}

@app.before_request
def make_session_permanent():
    session.permanent = True

# =========================================================
# ADMIN DATA
# =========================================================

admin_data = {

    'super_admin': {

        'fullname': 'Vasudharini',

        'password': 'superadmin@ST',

        'email': 'superadmin@securetrust.com',

        'role': 'super_admin',

        'role_display': 'Supreme Administrator',

        'status': 'active',

        'last_login': 'N/A'

    }

}

# =========================================================
# ADMIN HOME
# =========================================================

@app.route('/admin')
def admin():
    return render_template('auth/admin_home.html')



# =========================================================
# ADMIN LOGIN
# =========================================================

@app.route('/admin/login', methods=['GET', 'POST'])
def adminlogin():

    if request.method == 'POST':

        uname = request.form.get('uname')
        password = request.form.get('password')

        if uname in admin_data:

            admin = admin_data[uname]

            if admin['password'] == password:

                if admin.get('status') != 'active':
                    return 'Admin account disabled'

                session['admin'] = uname
                session['role'] = admin.get('role')
                session['admin_name'] = admin.get('fullname')
                session['role_display'] = admin.get('role_display', admin.get('role').replace('_', ' '))

                # Update Last Login
                admin_data[uname]['last_login'] = datetime.now().strftime('%Y-%m-%d %H:%M')

                return redirect(url_for('sadmin_dashboard'))

        flash('Invalid admin credentials')

    return render_template('auth/admin_login.html')

# =========================================================
# ADMIN LOGOUT
# =========================================================

@app.route('/admin/logout')
def admin_logout():

    session.clear()

    return redirect(url_for('adminlogin'))

# =========================================================
# ADMIN DASHBOARD
# =========================================================

@app.route('/admin/dashboard')
def sadmin_dashboard():

    if 'admin' not in session:
        return redirect(url_for('adminlogin'))

    total_users = len(data)
    total_admins = len(admin_data)

    total_balance = 0

    for user in data.values():
        total_balance += user.get('amount', 0)

    return render_template(
        'super_admin/sadmin_dashboard.html',
        admin=session['admin'],
        admin_name=session['admin_name'],
        role=session['role'],
        total_users=total_users,
        total_admins=total_admins,
        total_balance=total_balance
    )

# =========================================================
# ADMIN PROFILE
# =========================================================

@app.route('/admin/profile')
def sadmin_profile():

    if 'admin' not in session:
        return redirect(url_for('adminlogin'))

    current_admin = admin_data[session['admin']]
    role = current_admin.get('role')

    # Department Logic
    if role == 'super_admin':
        dept = 'SecureTrust Administrative Superior'
    elif role in ['customer_onboarding_admin', 'account_closure_admin', 'customer_support_admin']:
        dept = 'Support & Relations Department'
    elif role in ['card_manager', 'loan_manager', 'fd_manager', 'transaction_manager']:
        dept = 'Banking Operations Department'
    elif role == 'auditor':
        dept = 'Compliance & Audit Department'
    else:
        dept = 'General Administration'

    return render_template(
        'super_admin/sadmin_profile.html',
        admin=session['admin'],
        fullname=current_admin.get('fullname'),
        role=role,
        role_display=current_admin.get('role_display', role.replace('_', ' ').title()),
        email=current_admin.get('email'),
        status=current_admin.get('status', 'active').title(),
        last_login=current_admin.get('last_login', 'N/A'),
        department=dept
    )

@app.route('/admin/add-admin', methods=['GET', 'POST'])
def admin_addadmin():
    if 'admin' not in session:
        return redirect(url_for('adminlogin'))

    # Strict Super Admin Check
    if session.get('role') != 'super_admin':
        flash("Unauthorized: Only Super Admins can add new administrators.")
        return redirect(url_for('sadmin_dashboard'))

    if request.method == 'POST':
        fullname = request.form.get('fullname')
        uname = request.form.get('uname')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')

        # Prevent Multiple Super Admins
        if role == 'super_admin' and any(a.get('role') == 'super_admin' for a in admin_data.values()):
            flash('A Super Admin already exists. There can only be one system authority.')
            return redirect(url_for('admin_addadmin'))

        if uname not in admin_data:
            admin_data[uname] = {
                'fullname': fullname,
                'password': password,
                'email': email,
                'role': role,
                'status': 'active',
                'last_login': 'N/A'
            }
            flash(f'Administrator {uname} created successfully!')
            return redirect(url_for('admin_viewadmins'))

        flash('Admin username already exists!')

    # Count admins per role for auto-generation
    role_counts = {}
    for admin in admin_data.values():
        r = admin.get('role')
        role_counts[r] = role_counts.get(r, 0) + 1

    return render_template(
        'super_admin/sadmin_addadmin.html',
        admin=session['admin'],
        role=session['role'],
        role_counts=role_counts
    )


@app.route('/admin/view-admins')
def admin_viewadmins():
    if 'admin' not in session:
        return redirect(url_for('adminlogin'))

    # Only Super Admin or Auditor Allowed
    if session.get('role') not in ['super_admin', 'auditor']:
        flash("Unauthorized access to admin directory.")
        return redirect(url_for('sadmin_dashboard'))

    admins_list = []
    for uname, details in admin_data.items():
        role = details.get('role', 'admin')
        
        # Skip Super Admin in the directory
        if role == 'super_admin':
            continue

        # Determine Department
        if role in ['customer_onboarding_admin', 'account_closure_admin', 'customer_support_admin']:
            dept = 'Support & Relations'
        elif role in ['card_manager', 'loan_manager', 'fd_manager', 'transaction_manager']:
            dept = 'Banking Operations'
        elif role == 'auditor':
            dept = 'Compliance & Audit'
        else:
            dept = 'General Staff'

        admins_list.append({
            'username': uname,
            'fullname': details.get('fullname', 'N/A'),
            'email': details.get('email', 'N/A'),
            'role': role,
            'status': details.get('status', 'active'),
            'last_login': details.get('last_login', 'N/A'),
            'department': dept
        })

    # Calculate Department-wise counts
    dept_counts = {}
    for admin in admins_list:
        d = admin.get('department')
        dept_counts[d] = dept_counts.get(d, 0) + 1

    return render_template(
        'super_admin/sadmin_viewalladmins.html',
        admin=session['admin'],
        role=session['role'],
        admins_list=admins_list,
        total_admins=len(admins_list),
        dept_counts=dept_counts
    )


@app.route('/admin/view-admin/<username>')
def admin_view_specific_admin(username):

    if 'admin' not in session:
        return redirect(url_for('adminlogin'))

    if username not in admin_data:
        flash("Administrator not found.")
        return redirect(url_for('admin_viewadmins'))

    details = admin_data[username]
    role = details.get('role', 'admin')

    # Department Logic
    if role == 'super_admin':
        dept = 'SecureTrust Administrative Superior'
    elif role in ['customer_onboarding_admin', 'account_closure_admin', 'customer_support_admin']:
        dept = 'Support & Relations Department'
    elif role in ['card_manager', 'loan_manager', 'fd_manager', 'transaction_manager']:
        dept = 'Banking Operations Department'
    elif role == 'auditor':
        dept = 'Compliance & Audit Department'
    else:
        dept = 'General Administration'

    return render_template(
        'super_admin/sadmin_viewadmin.html',
        admin=session['admin'],
        target_admin_uname=username,
        fullname=details.get('fullname', 'N/A'),
        role_display=details.get('role_display', role.replace('_', ' ').title()),
        email=details.get('email', 'N/A'),
        status=details.get('status', 'active').title(),
        last_login=details.get('last_login', 'N/A'),
        department=dept
    )


@app.route('/admin/delete-admin/<username>')
def delete_admin(username):
    if 'admin' not in session:
        return redirect(url_for('adminlogin'))

    if session.get('role') != 'super_admin':
        flash("Unauthorized action.")
        return redirect(url_for('sadmin_dashboard'))

    if username == 'super_admin': # Protect the root admin
        flash('Root Super Admin cannot be deleted')
        return redirect(url_for('admin_viewadmins'))

    if username in admin_data:
        del admin_data[username]
        flash('Admin deleted successfully')
    return redirect(url_for('admin_viewadmins'))


@app.route('/admin/disable-admin/<username>')
def disable_admin(username):
    if 'admin' not in session:
        return redirect(url_for('adminlogin'))

    if session.get('role') != 'super_admin':
        flash("Unauthorized action.")
        return redirect(url_for('sadmin_dashboard'))

    if username == 'super_admin':
        flash('Root Super Admin cannot be disabled')
        return redirect(url_for('admin_viewadmins'))

    if username in admin_data:
        current_status = admin_data[username].get('status')
        admin_data[username]['status'] = 'disabled' if current_status == 'active' else 'active'
        flash(f"Admin {admin_data[username]['status']} successfully")

    return redirect(url_for('admin_viewadmins'))


@app.route('/admin/viewallusers')
def admin_view_users():
    if 'admin' not in session:
        return redirect(url_for('adminlogin'))
    
    # Restricted roles for user viewing
    allowed_roles = ['super_admin', 'customer_onboarding_admin', 'account_closure_admin', 'customer_support_admin', 'transaction_manager', 'auditor']
    if session.get('role') not in allowed_roles:
        flash("Access Denied to User Directory.")
        return redirect(url_for('sadmin_dashboard'))

    return render_template('onboarding/admin_viewallusers.html', admin=session['admin'], role=session.get('role'), users=[
        {
            'username': uname, 
            'fullname': details.get('name', 'N/A'), 
            'account_number': details.get('account_number', 'N/A'),
            'status': details.get('status', 'active')
        }
        for uname, details in data.items()
    ])


@app.route('/admin/user/<username>/info', methods=['GET', 'POST'])
def admin_user_info(username):
    if 'admin' not in session:
        return redirect(url_for('adminlogin'))

    if request.method == 'POST':
        # Update logic
        data[username].update({
            'name': request.form.get('name'),
            'dob': request.form.get('dob'),
            'mobile_number': request.form.get('mobileno'),
            'email_id': request.form.get('emailid'),
            'city': request.form.get('city'),
            'state': request.form.get('state'),
            'account_number': request.form.get('accno'),
            'card_number': request.form.get('cardno'),
            'pin_no': request.form.get('pin'),
            'amount': int(request.form.get('amount')),
            'aadharno': request.form.get('aadharno'),
            'panno': request.form.get('panno')
        })
        flash(f"Records for {username} updated successfully.")
        return redirect(url_for('admin_view_users'))

    return render_template(
        'onboarding/admin_viewuserinfo.html', 
        user=data[username], 
        ausername=username,
        admin=session['admin'],
        role=session.get('role')
    )


@app.route('/admin/user/<username>/transactions')
def admin_user_transactions(username):
    if 'admin' not in session:
        return redirect(url_for('adminlogin'))
    return render_template('audit/admin_userstament.html', 
                           username=username, 
                           admin=session['admin'],
                           transactions=reversed(data[username]['transactions']))


@app.route('/admin/adduser', methods=['GET', 'POST'])
def admin_add_user():
    if 'admin' not in session:
        return redirect(url_for('adminlogin'))
    
    if session.get('role') not in ['super_admin', 'customer_onboarding_admin']:
        flash("Access Denied: You do not have permission to enroll new users.")
        return redirect(url_for('sadmin_dashboard'))

    if request.method == 'POST':
        # (Existing logic...)
        name = request.form.get('name')
        accno = request.form.get('accno')
        mobile = request.form.get('mobileno')
        email = request.form.get('emailid')
        dob = request.form.get('dob')
        aadharno = request.form.get('aadharno')
        panno = request.form.get('panno')
        city = request.form.get('city')
        state = request.form.get('state')
        initial_deposit = int(request.form.get('initial_deposit', 500))
        username = name.lower().replace(" ", "")
        
        if username not in data:
            data[username] = {
                'name': name,
                'account_number': accno,
                'dob': dob,
                'aadharno': aadharno,
                'panno': panno,
                'city': city,
                'state': state,
                'password': 'password123',
                'card_number': 'ST' + accno[-4:], 
                'pin_no': '1234',
                'mobile_number': mobile,
                'email_id': email,
                'amount': initial_deposit,
                'last_login': 'N/A',
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
            
    existing_accnos = [u.get('account_number') for u in data.values()]
    return render_template('onboarding/admin_adduser.html', admin=session['admin'], role=session.get('role'), existing_accnos=existing_accnos)


@app.route('/admin/profile/<admin>')
def admin_profile(admin):
    return f"Admin Profile for {admin} (add template if needed)"


@app.route('/admin/settings/<admin>')
def admin_settings(admin):
    return f"Admin Settings for {admin} (add template if needed)"

# ================= CUSTOMER SUPPORT =================
@app.route('/admin/support/tickets')
def support_tickets():
    if 'admin' not in session: return redirect(url_for('adminlogin'))
    return render_template('support/support_tickets.html', admin=session['admin'], role=session['role'])

# ================= ACCOUNT CLOSURE =================
@app.route('/admin/closure/requests')
def closure_requests():
    if 'admin' not in session: return redirect(url_for('adminlogin'))
    return render_template('account_closure/delete_requests.html', admin=session['admin'], role=session['role'])

# ================= CARD OPERATIONS =================
@app.route('/admin/cards/management')
def card_management():
    if 'admin' not in session: return redirect(url_for('adminlogin'))
    return render_template('cards/card_management.html', admin=session['admin'], role=session['role'])

# ================= LOAN OPERATIONS =================
@app.route('/admin/loans/desk')
def loan_desk():
    if 'admin' not in session: return redirect(url_for('adminlogin'))
    return render_template('loans/loan_requests.html', admin=session['admin'], role=session['role'])

# ================= FD OPERATIONS =================
@app.route('/admin/fd/management')
def fd_management_admin():
    if 'admin' not in session: return redirect(url_for('adminlogin'))
    return render_template('fd/fd_requests.html', admin=session['admin'], role=session['role'])

# ================= TRANSACTION MONITORING =================
@app.route('/admin/transactions/monitor')
def transaction_monitor():
    if 'admin' not in session: return redirect(url_for('adminlogin'))
    return render_template('transactions/transaction_monitoring.html', admin=session['admin'], role=session['role'])

# ================= AUDIT & ANALYTICS =================
@app.route('/admin/audit/reports')
def audit_reports():
    if 'admin' not in session: return redirect(url_for('adminlogin'))
    return render_template('audit/reports_dashboard.html', admin=session['admin'], role=session['role'])

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
                'last_login': 'N/A',
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
        # Update Last Login
        data[username]['last_login'] = datetime.now().strftime('%Y-%m-%d %H:%M')
        flash('Login successful!')
        return redirect(url_for('dashboard', pusername=username))

    return render_template('login.html')


@app.route('/dashboard/<pusername>')
def dashboard(pusername):
    if 'user' not in session or session['user'] != pusername:
        flash("Please login to continue.")
        return redirect(url_for('login'))

    if pusername not in data:
        flash('Session expired or user data lost. Please login again.', 'danger')
        session.clear()
        return redirect(url_for('login'))

    return render_template('dashboard.html',
                           ausername=pusername,
                           wbalanceamount=int(data[pusername]['amount']),
                           last_login=data[pusername].get('last_login', 'N/A'))


@app.route('/balance/<busername>')
def balance(busername):
    if 'user' not in session or session['user'] != busername:
        return redirect(url_for('login'))

    if busername not in data:
        flash('Session expired or user data lost. Please login again.', 'danger')
        session.clear()
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
        udamount = int(request.form.get('amount'))
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
        uwamount = int(request.form.get('amount'))
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


@app.route('/transfer2/<username>', methods=['GET', 'POST'])
def transfer2(username):
    if 'user' not in session or session['user'] != username:
        return redirect(url_for('login'))

    if username not in data:
        flash('Session expired. Please login again.', 'danger')
        return redirect(url_for('login'))

    sender_acc = data[username]['account_number']

    if request.method == 'POST':
        bank_name = request.form.get('bank_name')
        receiver_acc = request.form.get('receiver_accno')
        ifsc = request.form.get('ifsc_code')
        amount = int(request.form.get('amount'))

        if amount <= 0:
            flash("Invalid transfer amount.", "danger")
        elif data[username]['amount'] - amount < 500:
            flash("Transfer denied. Minimum ₹500 balance must remain.", "danger")
        else:
            # Simulate Other Bank Transfer
            data[username]['amount'] -= amount
            now = datetime.now().strftime('%Y-%m-%d %H:%M')

            data[username]['transactions'].append({
                'type': f'Other Bank ({bank_name})',
                'amount': amount,
                'balance': data[username]['amount'],
                'time': now,
                'to': receiver_acc
            })

            flash(f"Success: ₹{amount} transferred to {bank_name} account {receiver_acc}", "success")
            return redirect(url_for('dashboard', pusername=username))

    return render_template('transfer2.html', ausername=username, sender_accno=sender_acc)


@app.route('/upitransfer/<username>', methods=['GET', 'POST'])
def upitransfer(username):
    if 'user' not in session or session['user'] != username:
        return redirect(url_for('login'))

    if username not in data:
        flash('Session expired. Please login again.', 'danger')
        return redirect(url_for('login'))

    sender_acc = data[username]['account_number']

    if request.method == 'POST':
        upi_id = request.form.get('upi_id')
        amount = int(request.form.get('amount'))

        if amount <= 0:
            flash("Invalid amount.", "danger")
        elif data[username]['amount'] - amount < 500:
            flash("Insufficient balance. Minimum ₹500 must remain.", "danger")
        else:
            # Simulate UPI Transfer
            data[username]['amount'] -= amount
            now = datetime.now().strftime('%Y-%m-%d %H:%M')

            data[username]['transactions'].append({
                'type': 'UPI Payment',
                'amount': amount,
                'balance': data[username]['amount'],
                'time': now,
                'to': upi_id
            })

            flash(f"Success: ₹{amount} paid via UPI to {upi_id}", "success")
            return redirect(url_for('dashboard', pusername=username))

    return render_template('upitransfer.html', ausername=username, sender_accno=sender_acc)


@app.route('/accountstatement/<username>')
def accountstatement(username):
    if 'user' not in session or session['user'] != username:
        return redirect(url_for('login'))

    user_txns = data[username].get('transactions', [])
    return render_template('statement.html', username=username, ausername=username, transactions=reversed(user_txns))

# ================= LOAN PAGE =================

@app.route('/loan/<username>')
def loan(username):

    if 'user' not in session or session['user'] != username:
        return redirect(url_for('login'))

    if username not in data:
        flash('User data not found. Please log in again.', 'danger')
        return redirect(url_for('login'))

    return render_template(
        'loan.html',
        ausername=username,
        user=data[username]
    )


# ================= FIXED DEPOSIT PAGE =================

@app.route('/fd/<username>')
def fd(username):

    if 'user' not in session or session['user'] != username:
        return redirect(url_for('login'))

    if username not in data:
        flash('User data not found. Please log in again.', 'danger')
        return redirect(url_for('login'))

    return render_template(
        'fd.html',
        ausername=username,
        user=data[username]
    )


# ================= CARD CENTER PAGE =================

@app.route('/card/<username>')
def card(username):

    if 'user' not in session or session['user'] != username:
        return redirect(url_for('login'))

    return render_template(
        'card.html',
        ausername=username
    )

# ================= CARD SERVICES ROUTES =================

# ---------------- VIEW CARD ----------------

@app.route('/viewcard/<username>', methods=['GET', 'POST'])
def viewcard(username):

    if username not in data:
        flash('User not found!', 'danger')
        return redirect(url_for('login'))

    return render_template(
        'viewcard.html',
        ausername=username
    )


# ---------------- CHANGE CARD PIN ----------------

@app.route('/changecardpin/<username>', methods=['GET', 'POST'])
def changecardpin(username):

    if username not in data:
        flash('User not found!', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':

        accountnumber = request.form.get('accountnumber')
        cardtype = request.form.get('cardtype')
        cardnumber = request.form.get('cardnumber')
        cardholder = request.form.get('cardholder')
        expiry = request.form.get('expiry')
        cvv = request.form.get('cvv')

        currentpin = request.form.get('currentpin')
        newpin = request.form.get('newpin')
        confirmpin = request.form.get('confirmpin')

        # ================= VALIDATIONS =================

        if newpin != confirmpin:

            flash('New PIN and Confirm PIN do not match!', 'danger')

            return redirect(
                url_for(
                    'changecardpin',
                    username=username
                )
            )

        if len(newpin) != 4 or not newpin.isdigit():

            flash('PIN must contain exactly 4 digits!', 'danger')

            return redirect(
                url_for(
                    'changecardpin',
                    username=username
                )
            )

        flash('Card PIN updated successfully!', 'success')

        return redirect(
            url_for(
                'changecardpin',
                username=username
            )
        )

    return render_template(
        'changecardpin.html',
        ausername=username
    )


# ---------------- CHANGE PASSWORD ----------------

@app.route('/changepassword/<username>', methods=['GET', 'POST'])
def changepassword(username):

    if username not in data:
        flash('User not found!', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':

        email = request.form.get('email')
        currentpassword = request.form.get('currentpassword')
        newpassword = request.form.get('newpassword')
        confirmpassword = request.form.get('confirmpassword')

        # ================= VALIDATIONS =================

        if newpassword != confirmpassword:
            flash('New Password and Confirm Password do not match!', 'danger')
            return redirect(url_for('changepassword', username=username))

        if data[username]['password'] != currentpassword:
            flash('Current password is incorrect!', 'danger')
            return redirect(url_for('changepassword', username=username))

        if data[username].get('email_id') != email:
            flash('Email address does not match our records!', 'danger')
            return redirect(url_for('changepassword', username=username))

        # Update Password
        data[username]['password'] = newpassword
        
        flash('Password updated successfully!', 'success')

        return redirect(url_for('changepassword', username=username))

    return render_template(
        'changepassword.html',
        ausername=username
    )


# ---------------- BLOCK CARD ----------------

@app.route('/blockcard/<username>', methods=['GET', 'POST'])
def blockcard(username):

    if username not in data:
        flash('User not found!', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':

        accountnumber = request.form.get('accountnumber')
        cardtype = request.form.get('cardtype')
        cardnumber = request.form.get('cardnumber')
        cardholder = request.form.get('cardholder')
        expiry = request.form.get('expiry')
        cvv = request.form.get('cvv')
        pin = request.form.get('pin')

        # ================= VALIDATION =================

        if len(pin) != 4 or not pin.isdigit():

            flash('PIN must contain exactly 4 digits!', 'danger')

            return redirect(
                url_for(
                    'blockcard',
                    username=username
                )
            )

        flash('Your card has been blocked successfully!', 'success')

        return redirect(
            url_for(
                'blockcard',
                username=username
            )
        )

    return render_template(
        'blockcard.html',
        ausername=username
    )


# ---------------- REQUEST CARD ----------------

@app.route('/requestcard/<username>', methods=['GET', 'POST'])
def requestcard(username):

    if username not in data:
        flash('User not found!', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':

        accountnumber = request.form.get('accountnumber')
        cardtype = request.form.get('cardtype')

        flash(
            f'{cardtype} request submitted successfully!',
            'success'
        )

        return redirect(
            url_for(
                'requestcard',
                username=username
            )
        )

    return render_template(
        'requestcard.html',
        ausername=username
    )

@app.route('/profile/<username>')
def profile(username):
    if 'user' not in session or session['user'] != username:
        return redirect(url_for('login'))

    if username not in data:
        flash('Session expired or user data lost. Please login again.', 'danger')
        session.clear()
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
