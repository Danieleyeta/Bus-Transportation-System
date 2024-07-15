from flask import Flask, render_template, request, redirect, session, flash, send_file, url_for
from datetime import datetime, timedelta
from flask_mysqldb import MySQL
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

app = Flask(__name__, template_folder="template", static_folder="static")
app.secret_key = 'your_secret_key'  # Set a secret key for session management

# Configure db
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Kester@9498'
app.config['MYSQL_DB'] = 'bus_transportation_system'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)  # Session expires after 30 minutes of inactivity

mysql = MySQL(app)

# Helper function for console logging
def log_to_console(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")

@app.route('/')
def home():
    try:
        log_to_console("Home page accessed")
        return render_template('index.html')
    except Exception as e:
        log_to_console(f"Error loading home page: {str(e)}")
        return render_template('error.html', error_msg='An error occurred while loading the page')

@app.route('/about')
def about():
    try:
        log_to_console("About page accessed")
        return render_template('about.html')
    except Exception as e:
        log_to_console(f"Error loading about page: {str(e)}")
        return render_template('error.html', error_msg='An error occurred while loading the page')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        try:
            # Retrieve form data
            userDetails = request.form
            name = userDetails.get('name', '')
            email = userDetails.get('email', '')
            phone = userDetails.get('phone', '')
            message = userDetails.get('message', '')

            # Validate form data
            if not name:
                return render_template("invalid.html", error_msg="No Name", error_msg2="You did not enter the name")
            if not email:
                return render_template("invalid.html", error_msg="No Email", error_msg2="You did not enter the Email")
            if not phone:
                return render_template("invalid.html", error_msg="No Number", error_msg2="You did not enter the Phone Number")
            if not message:
                return render_template("invalid.html", error_msg="No Message", error_msg2="You did not enter the Message")

            # Insert into database
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO contact(name, email, phone, msg) VALUES(%s, %s, %s, %s)", (name, email, phone, message))
            mysql.connection.commit()
            cur.close()

            log_to_console("Contact form submitted and saved to database")
            return redirect('/')
        
        except Exception as e:
            log_to_console(f"Error processing contact form: {str(e)}")
            return render_template('error.html', error_msg='An error occurred while processing your request')

    return render_template('contact.html')

@app.route('/post', methods=['GET', 'POST'])
def post():
    try:
        log_to_console("Post page accessed")
        fromDetails = []
        toDetails = []
        userDetails = []
        not_found = ""

        # Initialize variables to retain form data
        departure = ""
        fromm = ""
        too = ""
        name = ""

        if request.method == 'POST':
            # Fetch form data
            departure = request.form.get("departure")
            fromm = request.form.get("from")
            too = request.form.get("to")
            name = request.form.get("name")
            
            log_to_console(f"Form data received - Departure: {departure}, From: {fromm}, To: {too}, Name: {name}")

            # Validate and process form data
            if departure and fromm and too:
                try:
                    # Convert departure date to datetime object
                    format_str = '%Y-%m-%d'
                    get_date = datetime.strptime(departure, format_str)
                    log_to_console(f"Parsed departure date: {get_date}")
                except ValueError:
                    log_to_console("Invalid date format")
                    return render_template('error.html', error_msg='Invalid date format')

                # Fetch buses based on 'from' and 'to' locations
                cur = mysql.connection.cursor()
                cur.execute("SELECT * FROM buses WHERE b_from = %s AND b_to = %s", (fromm, too))
                userDetails = cur.fetchall()
                log_to_console(f"Buses fetched: {userDetails}")

                if not userDetails:
                    not_found = "Oops! Buses aren't available"
                    log_to_console("Buses aren't available")
                cur.close()

                # If a bus is selected for booking
                if name:
                    cur = mysql.connection.cursor()
                    cur.execute("SELECT bus_id, seats FROM buses WHERE b_from = %s AND b_to = %s AND bus_name = %s", (fromm, too, name))
                    bus_data = cur.fetchone()
                    log_to_console(f"Bus data fetched: {bus_data}")

                    if bus_data:
                        bus_id = bus_data[0]
                        total_seats = bus_data[1]

                        # Fetch user_id from session
                        user_id = session.get('user_id')
                        log_to_console(f"User id from session: {user_id}")

                        if not user_id:
                            log_to_console("User not logged in")
                            return redirect('/signin')

                        # Check how many seats are already booked
                        cur.execute("SELECT COUNT(*) FROM bookings WHERE bus_id = %s AND depart = %s", (bus_id, get_date))
                        booked_seats = cur.fetchone()[0]
                        log_to_console(f"Booked seats: {booked_seats}, Total seats: {total_seats}")

                        if booked_seats >= total_seats:
                            not_found = "Oops! This bus is fully booked"
                            log_to_console("Bus is fully booked")
                        else:
                            # Assign the next available seat number
                            seat_no = booked_seats + 1
                            log_to_console(f"Assigning seat number: {seat_no}")

                            # Insert booking into 'bookings' table
                            cur.execute("INSERT INTO bookings(user_id, bus_id, depart, bk_from, bk_to, seat_no) VALUES (%s, %s, %s, %s, %s, %s)",
                                        (user_id, bus_id, get_date, fromm, too, seat_no))
                            mysql.connection.commit()
                            cur.close()
                            log_to_console("Booking successful, redirecting to /payment")

                            # log_to_console("Booking successful, redirecting to /mybookings")

                            # Redirect to 'mybookings' page after successful booking
                            # return redirect("/mybookings")

                            # Store booking details in session for payment
                            session['booking_details'] = {
                                'user_id': user_id,
                                'bus_id': bus_id,
                                'depart': get_date,
                                'bk_from': fromm,
                                'bk_to': too,
                                'seat_no': seat_no
                            }

                            # Redirect to payment page after successful booking
                            return redirect("/payment")
                    else:
                        log_to_console("Bus data not found for the selected name")
                        not_found = "Bus not found"

        # Fetch distinct 'from' and 'to' values from database
        cur = mysql.connection.cursor()
        cur.execute("SELECT DISTINCT(b_from) FROM buses")
        fromDetails = cur.fetchall()
        log_to_console(f"Distinct 'from' locations fetched: {fromDetails}")

        cur.execute("SELECT DISTINCT(b_to) FROM buses")
        toDetails = cur.fetchall()
        log_to_console(f"Distinct 'to' locations fetched: {toDetails}")
        cur.close()

        return render_template('post.html', fromDetails=fromDetails, toDetails=toDetails, userDetails=userDetails, not_found=not_found, departure=departure, fromm=fromm, too=too, name=name)

    except Exception as e:
        log_to_console(f"Error in post route: {str(e)}")
        return render_template('error.html', error_msg='An error occurred while processing your request')


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    try:
        log_to_console("Signin page accessed")

        if request.method == 'POST':
            userDetails = request.form
            email = userDetails['email']
            password = userDetails['password']

            if not email:
                log_to_console("No Email entered")
                return render_template('invalid.html', error_msg='No Email', error_msg2='You cannot leave email blank!')

            if not password:
                log_to_console("No Password entered")
                return render_template('invalid.html', error_msg='No Password', error_msg2='You did not enter your password!')

            cur = mysql.connection.cursor()

            # Check if the user is in the admin table
            cur.execute("SELECT user_id FROM admin WHERE user_id IN (SELECT user_id FROM users WHERE email = %s AND password = %s)", (email, password))
            admin_id = cur.fetchone()

            if admin_id:
                admin_id = admin_id[0]

            # Check if the user exists and retrieve their user_id
            cur.execute("SELECT user_id FROM users WHERE email = %s AND password = %s", (email, password))
            user_id = cur.fetchone()

            if user_id:
                user_id = user_id[0]

            if not user_id:
                log_to_console("Incorrect Email or Password")
                return render_template('invalid.html', error_msg='Incorrect Email or Password', error_msg2='Please check your credentials!')

            session['user_id'] = user_id  # Store user_id in session
            session.permanent = True  # Make session permanent to apply the expiration

            if admin_id == user_id:
                cur.execute("INSERT INTO signin(user_id, email) VALUES (%s, %s)", (user_id, email))
                mysql.connection.commit()

                # Fetch user's name
                cur.execute("SELECT name FROM users WHERE email = %s", (email,))
                name1 = cur.fetchone()
                display_name = name1[0] if name1 else 'User'

                cur.close()
                log_to_console(f"Admin signed in: user_id {user_id}")
                session['user_type'] = "admin"
                return render_template('admin.html', welcome='Welcome', user=display_name, exc='!')

            else:
                cur.execute("INSERT INTO signin(user_id, email) VALUES (%s, %s)", (user_id, email))
                mysql.connection.commit()

                # Fetch user's name
                cur.execute("SELECT name FROM users WHERE email = %s", (email,))
                name1 = cur.fetchone()
                display_name = name1[0] if name1 else 'User'

                cur.close()
                log_to_console(f"User signed in: user_id {user_id}")
                session['user_type'] = "user"
                return render_template('index.html', welcome='Welcome', user=display_name, exc='!')

        return render_template('login.html')

    except Exception as e:
        log_to_console(f"Error processing signin form: {str(e)}")
        return render_template('error.html', error_msg='An error occurred while processing your request')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    try:
        log_to_console("Signup page accessed")

        if request.method == 'POST':
            userDetails = request.form
            name = userDetails['name']
            email = userDetails['email']
            password = userDetails['password']

            if not name:
                log_to_console("No Name entered")
                return render_template('invalid.html', error_msg='No Name', error_msg2='Name cannot be empty')

            if not email:
                log_to_console("No Email entered")
                return render_template('invalid.html', error_msg='No Email', error_msg2='Email cannot be empty')

            if not password:
                log_to_console("No Password entered")
                return render_template('invalid.html', error_msg='No Password', error_msg2='Password cannot be empty')

            cur = mysql.connection.cursor()
            cur.execute("SELECT MAX(user_id) FROM users")
            id = cur.fetchone()[0] or 0
            user_id = id + 1

            cur.execute("INSERT INTO users(user_id, name, email, password) VALUES(%s, %s, %s, %s)", (user_id, name, email, password))
            cur.execute("INSERT INTO signin(user_id, email)  VALUES(%s, %s)", (user_id, email))
            mysql.connection.commit()

            cur.execute("SELECT name FROM users WHERE email = (SELECT email FROM signin WHERE time = (SELECT MAX(time) FROM signin))")
            name2 = cur.fetchone()
            display_name = name2[0] if name2 else 'User'

            cur.close()
            # session['user_id'] = user_id  # Store user_id in session
            # session.permanent = True  # Make session permanent to apply the expiration
            log_to_console(f"User signed up successfully: user_id {user_id}")
            # return render_template('index.html', welcome='Welcome', user=display_name, exc='!')
            return render_template('login.html', welcome='User signed up successfully')

        return render_template('signup.html')

    except Exception as e:
        log_to_console(f"Error processing signup form: {str(e)}")
        return render_template('error.html', error_msg='An error occurred while processing your request')

@app.route('/logout')
def logout():
    session.clear()  # Clear all session data
    log_to_console("User logged out")
    return redirect('/')

@app.route('/mybookings')
def bookings():
    try:
        log_to_console("My Bookings page accessed")

        user_id = session.get('user_id')

        if not user_id:
            log_to_console("User not logged in")
            return render_template('login.html')

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM bookings WHERE user_id = %s", (user_id,))
        userDetails = cur.fetchall()
        cur.close()

        log_to_console(f"User bookings retrieved: user_id {user_id}")
        return render_template('bookings.html', userDetails=userDetails)

    except Exception as e:
        log_to_console(f"Error retrieving user bookings: {str(e)}")
        return render_template('error.html', error_msg='An error occurred while processing your request')

@app.route('/booking')
def booking():
    try:
        log_to_console("My Booking page accessed")
        # Retrieve booking details from session
        booking_details = session.get('booking_details')
        
        log_to_console(f"Booking details retrieved: {booking_details}")
        return render_template('booking.html', booking_details=booking_details)
        # session.pop('booking_details', None)

    except Exception as e:
        log_to_console(f"Error retrieving user bookings: {str(e)}")
        return render_template('error.html', error_msg='An error occurred while processing your request')

@app.route('/details')
def info():
    try:
        log_to_console("Details page accessed")

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM buses")
        busDetails = cur.fetchall()

        cur.execute("SELECT * FROM users")
        userDetails = cur.fetchall()

        cur.execute("SELECT * FROM bookings")
        bookDetails = cur.fetchall()

        cur.close()

        log_to_console("Database details retrieved")
        return render_template('users.html', userDetails=userDetails, busDetails=busDetails, bookDetails=bookDetails)

    except Exception as e:
        log_to_console(f"Error retrieving database details: {str(e)}")
        return render_template('error.html', error_msg='An error occurred while processing your request')

@app.route('/edit', methods=['GET', 'POST'])
def edit():
    try:
        log_to_console("Edit page accessed")

        if request.method == 'POST':
            cur = mysql.connection.cursor()
            name = request.form.get('name')
            bustype = request.form.get('bustype')
            bfrom = request.form.get('bfrom')
            to = request.form.get('place')
            fare = request.form.get('fare')
            busid = request.form.get('busid')
            seats = request.form.get('seats')

            if name and bustype and bfrom and to and fare:
                cur.execute("INSERT INTO buses(bus_name, bus_type, b_from, b_to, fare, seats) VALUES(%s, %s, %s, %s, %s, %s)", (name, bustype, bfrom, to, fare, seats))
                mysql.connection.commit()
                cur.close()
                log_to_console("Bus details updated")
                return render_template('admin.html')

            if busid:
                cur.execute("DELETE FROM buses WHERE bus_id = %s", (busid,))
                mysql.connection.commit()
                cur.close()
                log_to_console(f"Bus deleted: bus_id {busid}")
                return render_template('admin.html')

            cur.close()
            return render_template('admin.html')

        return render_template('edit.html')

    except Exception as e:
        log_to_console(f"Error processing edit form: {str(e)}")
        return render_template('error.html', error_msg='An error occurred while processing your request')

@app.route('/admin')
def admin():
    log_to_console("Admin page accessed")
    return render_template('admin.html')

@app.route('/payment')
def payment():
    try:
        log_to_console("Payment page accessed")
        
        # Retrieve booking details from session
        booking_details = session.get('booking_details')
        if not booking_details:
            log_to_console("No booking details found in session")
            return redirect('/post')
        
        log_to_console(f"Payment page accessed for booking details: {booking_details}")
        return render_template('payment.html', booking_details=booking_details)

    except Exception as e:
        log_to_console(f"Error loading payment page: {str(e)}")
        return render_template('error.html', error_msg='An error occurred while processing your request')

@app.route('/process_payment', methods=['POST'])
def payment_confirmation():
    try:
        # log_to_console("Payment confirmation page accessed")
        
        # Clear booking details from session
        payment_method = request.form['paymentMethod']
        booking_details = session.get('booking_details')
        # booking_details = session.pop('booking_details', None)
        if not booking_details:
            log_to_console("No booking details found in session")
            return redirect('/post')
        
        user_id = booking_details['user_id']
        bus_id = booking_details['bus_id']
        depart = booking_details['depart']
        bk_from = booking_details['bk_from']
        bk_to = booking_details['bk_to']
        seat_no = booking_details['seat_no']
        
        log_to_console(f"Processing payment for booking details: {booking_details}, Payment Method: {payment_method}")
    
        # Simulate payment processing
        payment_success = True
        paymentStatus = "SUCCESSFUL"
        
        if payment_success:
            log_to_console("Payment successful")
            # Store payment details in database
            cur = mysql.connection.cursor()
            cur.execute("UPDATE bookings SET payment = %s, payment_status = %s WHERE user_id = %s AND bus_id = %s AND depart = %s",
                        (payment_method, paymentStatus , user_id, bus_id, depart))
            mysql.connection.commit()
            cur.close()
            
            # Clear booking details from session
            # session.pop('booking_details', None)
            return redirect('/booking')
            
            # return render_template('bookings', message="Payment Successful! Your booking is confirmed.")

    except Exception as e:
        log_to_console(f"Error displaying payment confirmation: {str(e)}")
        return render_template('error.html', error_msg='An error occurred while processing your request')
    
@app.route('/ticket/download')
def download_ticket():
    # Example booking details
    booking_details = session.get("booking_details")

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Title
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width / 2.0, height - 100, "Booking Confirmation")

    # Subtitle
    c.setFont("Helvetica", 14)
    c.drawCentredString(width / 2.0, height - 130, "Your booking details")

    # Booking details
    c.setFont("Helvetica", 12)
    c.drawString(100, height - 180, f"Departure Date: {booking_details['depart']}")
    c.drawString(100, height - 200, f"From: {booking_details['bk_from']}")
    c.drawString(100, height - 220, f"To: {booking_details['bk_to']}")
    c.drawString(100, height - 240, f"Seat Number: {booking_details['seat_no']}")

    # Thank you note
    c.drawString(100, height - 280, "Thank you for booking with us!")

    c.showPage()
    c.save()

    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name='ticket.pdf',
        mimetype='application/pdf'
    )

if __name__ == '__main__':
    app.run(debug=True)
