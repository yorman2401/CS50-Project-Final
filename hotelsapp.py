# Modules and frameworks
import requests
import sqlite3
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Recommended places for query in the API
places = ['miami', 'madrid', 'paris', 'london', 'dubai', 'new york']

# The API query list
queries = list()

# Type of alerts
alerts = {
    'info': {'class': 'alert-info', 'icon': 'info_outline', 'title': 'Info Alert: '},
    'success': {'class': 'alert-success', 'icon': 'check', 'title': 'Success Alert: '},
    'warning': {'class': 'alert-warning', 'icon': 'warning', 'title': 'Warning Alert: '},
    'error': {'class': 'alert-danger', 'icon': 'error_outline', 'title': 'Error Alert: '},
    'delete': {'class': 'alert-danger', 'icon': 'delete', 'title': 'Delete: '}
}

# Recommended places
cards = [
    {'image': 'https://media-cdn.tripadvisor.com/media/photo-s/12/f7/4e/c3/miami-beach.jpg', 'city': 'Miami', 'country': 'United States', 'description': "Miami is hot hot hot! And it’s not just the sultry weather. Here, the nightlife is scorching, thanks to a strong Latin influence and spicy salsa culture. Dance the noche away in a nightclub, or indulge in a fancy meal at one of the city’s celebrity-owned restaurants. By day, hit the beach of course, or have yourself a walkabout, taking in Miami’s colorful art deco architecture. Grab a Cuban sandwich in Little Havana, then ride the vintage carousel at Virginia Key Beach Park."},
    {'image': 'https://media-cdn.tripadvisor.com/media/photo-s/1b/33/e6/bf/caption.jpg', 'city': 'Madrid', 'country': 'Spain', 'description': "So many of Madrid’s buildings look like castles, you’ll think you’ve stumbled into a fairytale. Even City Hall is astounding, with its white pinnacles and neo-Gothic features. A self-guided architecture tour can begin by the great bear statue in the central Puerta del Sol. Wander by the fanciful Royal Palace before absorbing the natural beauty of Retiro Park, then visit one of the city’s many museums. You could happily cap off each day by nibbling on forkfuls of paella while sipping Spanish rioja."},
    {'image': 'https://media-cdn.tripadvisor.com/media/photo-s/1b/33/ca/c8/caption.jpg', 'city': 'Paris', 'country': 'France', 'description': "Lingering over pain au chocolat in a sidewalk café, relaxing after a day of strolling along the Seine and marveling at icons like the Eiffel Tower and the Arc de Triomphe… the perfect Paris experience combines leisure and liveliness with enough time to savor both an exquisite meal and exhibits at the Louvre. Awaken your spirit at Notre Dame, bargain hunt at the Marché aux Puces de Montreuil or for goodies at the Marché Biologique Raspail, then cap it all off with a risqué show at the Moulin Rouge."},
    {'image': 'https://media-cdn.tripadvisor.com/media/photo-s/1b/4b/5a/98/caption.jpg', 'city': 'London', 'country': 'United Kingdom', 'description': "From Shoreditch’s swaggering style to Camden’s punky vibe and chic Portobello Road, London is many worlds in one. The city’s energy means that no two days are the same. Explore royal or historic sites, tick off landmarks from your bucket list, eat and drink in exclusive Michelin-starred restaurants, enjoy a pint in a traditional pub, or get lost down winding cobbled streets and see what you stumble across – when it comes to London, the possibilities are endless."},
    {'image': 'https://media-cdn.tripadvisor.com/media/photo-s/1b/51/ca/8d/caption.jpg', 'city': 'Dubai', 'country': 'United Arab Emirates', 'description': "Dubai is a destination that mixes modern culture with history, adventure with world-class shopping and entertainment. Catch a show at the Dubai Opera, see downtown from atop the Burj Khalifa and spend an afternoon along Dubai Creek exploring the gold, textile and spice souks. If you’re looking for thrills, you can float above the desert dunes in a hot air balloon, climb aboard a high-speed ride at IMG Worlds of Adventure or skydive over the Palm Jumeirah."},
    {'image': 'https://media-cdn.tripadvisor.com/media/photo-s/1b/43/e5/f4/caption.jpg', 'city': 'New York City', 'country': 'United States', 'description': "Conquering New York in one visit is impossible. Instead, hit the must-sees – the Empire State Building, the Statue of Liberty, Central Park, the Metropolitan Museum of Art – and then explore off the beaten path with visits to The Cloisters or one of the city’s libraries. Indulge in the bohemian shops of the West Village or the fine dining of the Upper West Side. The bustling marketplace inside of Grand Central Station gives you a literal taste of the best the city has to offer."}
]

def login_required(f):
    """Decorate routes to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_id') is None:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function


def logout_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_id') is not None:
            return redirect('/')
        return f(*args, **kwargs)
    return decorated_function


def place_finder(search):

    url = "https://tripadvisor1.p.rapidapi.com/locations/search"

    querystring = {"location_id":"1","limit":"5","sort":"relevance","offset":"0","lang":"en_US","currency":"USD","units":"km","query":search}

    headers = {
        'x-rapidapi-host': "tripadvisor1.p.rapidapi.com",
        'x-rapidapi-key': "01f417be64msh6294ab946d9f1dfp1ff778jsn7a4add4e1bce"
    }

    try:
        response = requests.request("GET", url, headers=headers, params=querystring).json()
    except requests.RequestException:
        return None

    i = 0
    while i < 5:
        try:
            return {'place_id': response['data'][i]['result_object']['location_id']}
        except (KeyError, TypeError, ValueError, IndexError):
            i += 1
            continue
        except:
            i += 1
    return None


def hotel_finder(search):

    try:
        search['place_id'] = place_finder(search['place'])['place_id']
    except:
        return None

    url = "https://tripadvisor1.p.rapidapi.com/hotels/list"

    querystring = {"offset":"0","currency":"USD","limit":"10","order":"asc","lang":"en_US","sort":"recommended","location_id":search['place_id'],"adults":search['adults'],"checkin":search['checkin'],"rooms":"1","nights":search['nights']}

    headers = {
        'x-rapidapi-host': "tripadvisor1.p.rapidapi.com",
        'x-rapidapi-key': "01f417be64msh6294ab946d9f1dfp1ff778jsn7a4add4e1bce"
    }

    try:
        response = requests.request("GET", url, headers=headers, params=querystring).json()
    except requests.RequestException:
        return None

    try:
        return response['data']
    except:
        return None

def badge():

    # Connect with SQLite databse
    db = sqlite3.connect('project/hotels.db')

    # Query to get the number hotels in the wishlist
    try:
        rows = db.execute("SELECT wishes FROM users WHERE id = ?", (session['user_id'],)).fetchall()
    except KeyError:
        return None

    # Close database
    db.close()

    # Return number of wishes
    return rows[0][0]


@app.route('/', methods=["GET", "POST"])
def index():
    """Home page"""

    # Display home page
    return render_template('index.html', cards=cards, alerts=alerts, badge=badge())


@app.route('/query', methods=["GET", "POST"])
def show_query():
    """Display hotels"""

    # Check search is alphabet
    place = request.form.get('place')
    for c in place:
        if not c.isalpha() and not c.isspace():
            flash("Enter only names of cities, states or countries", 'warning')
            return redirect('/')

    # Request parameters
    search = {
            'place': place,
            'checkin': request.form.get('checkin'),
            'nights': request.form.get('nights'),
            'adults': request.form.get('adults')
            }

    # Query the search in the API
    queries = hotel_finder(search)
    if queries is None:
        flash("Invalid search or the place has no availability", 'error')
        return redirect('/')

    # Display query page
    return render_template('query.html', queries=queries, adults=search['adults'], badge=badge())


@app.route('/wishlist', methods=["GET", "POST"])
@login_required
def wishlist():
    """ Hotel wishlist"""

    # Check request method
    if request.method == "GET":

        # Connect with SQLite database
        db = sqlite3.connect('project/hotels.db')

        # Query to get the wishlist
        rows = db.execute("SELECT * FROM wishlist WHERE user_id = ?", (session['user_id'],)).fetchall() 

        # Close database
        db.close()

        # Display wishlist page
        return render_template('wishlist.html', rows=rows, alerts=alerts, badge=badge())
    else:

        # Check add or delete action
        if request.form.get('wishlist') == 'add':

            # Request parameters
            hotel_id = request.form.get('hotel_id')
            photo = request.form.get('photo')
            name = request.form.get('name')
            stars = request.form.get('stars')
            reviews = request.form.get('reviews')
            location = request.form.get('location')
            price = request.form.get('price')

            # Connect with SQLite database
            db = sqlite3.connect('project/hotels.db')

            # Query to get the number hotels in the wishlist
            rows = db.execute("SELECT wishes FROM users WHERE id = ?", (session['user_id'],)).fetchall()
            if not len(rows) == 1:
                flash("Error adding the hotel to the wishlist", 'error')
                return redirect('/wishlist')

            # Query to insert hotels in the wishlist
            db.execute("""INSERT INTO wishlist (user_id, hotel_id, photo, name, stars, reviews, location, price) 
                        VALUES(:user_id, :hotel_id, :photo, :name, :stars, :reviews, :location, :price)""",
                        {'user_id': session['user_id'], 'hotel_id': hotel_id, 'photo': photo, 'name': name,
                        'stars': stars, 'reviews': reviews,'location': location, 'price': price})

            # Update user number of wishes
            db.execute("UPDATE users SET wishes = :wishes WHERE id = :id",
                        {'wishes': rows[0][0] + 1, 'id': session['user_id']})

            # Save changes
            db.commit()

            # Close database
            db.close()

            # Redirect user to wishlist page
            flash('Hotel has been added to wishlist', 'success')
            return redirect('/wishlist')
        else:

            # Request parameter
            hotel_id = request.form.get('hotel_id')

            # Connect with SQLite database
            db = sqlite3.connect('project/hotels.db')

            # Query to get the number hotels in the wishlist
            rows = db.execute("SELECT wishes FROM users WHERE id = ?", (session['user_id'],)).fetchall()
            if not len(rows) == 1:
                flash("Error adding the hotel to the wishlist", 'error')
                return redirect('/wishlist')

            # Query to delete hotels of the wishlist
            db.execute("DELETE FROM wishlist WHERE hotel_id = ?", (hotel_id,))

            # Update user number of wishes
            db.execute("UPDATE users SET wishes = :wishes WHERE id = :id",
                        {'wishes': rows[0][0] - 1, 'id': session['user_id']})

            # Save the changes
            db.commit()

            # Close database
            db.close()

            # Redirect user to wishlist page
            flash('Hotel has been removed', 'delete')
            return redirect('/wishlist')

@app.route('/register', methods=["GET", "POST"])
@logout_required
def register():
    """Register new users"""

    # Check request method
    if request.method == "GET":

        # Display register page
        return render_template("register.html", alerts=alerts)
    else:

        # Request parameters
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirm")

        # Check the passwords match
        if not password == confirm:
            flash("Passwords don't match", 'info')
            return redirect("/register")

        # Connect with the SQLite database
        db = sqlite3.connect('project/hotels.db')

        # Check username don't exists
        rows = db.execute("SELECT username FROM users WHERE username = ? COLLATE NOCASE", (username,))
        if not len(rows.fetchall()) == 0:
            flash("Username already exists", 'info')
            return redirect("/register")

        # Insert the new user in the database
        db.execute("INSERT INTO users(username, hash) VALUES(:username, :hash)",
                    {'username': username, 'hash': generate_password_hash(password)})

        # Save the changes
        db.commit()

        # Close database
        db.close()

        # Redirect user to home
        flash("You have successfully registered", 'success')
        return redirect("/")


@app.route("/login", methods=["GET", "POST"])
@logout_required
def login():
    """Log in users"""

    # Forget any user_id
    session.clear()

    # Check request method
    if request.method == "GET":

        # Display login web page
        return render_template("login.html", alerts=alerts)
    else:

        # Request parameters
        username = request.form.get("username")
        password = request.form.get("password")

        # Connect with the SQLite database
        db = sqlite3.connect('project/hotels.db')

        # Check username and password
        rows = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchall()
        if not len(rows) == 1 or not check_password_hash(rows[0][2], password):
            flash("Invalid username or/and password", 'warning')
            return redirect("/")

        # Remember which user has logged in
        session["user_id"] = rows[0][0]

        # Close database
        db.close()

        # Redirect user to home
        flash(f"Welcome '{username}'", 'success')
        return redirect("/")


@app.route("/logout")
def logout():
    """Log out users"""

    # Forget any user_id
    session.clear()

    # Redirect user to index
    return redirect("/")


@app.route("/change_username", methods=["GET", "POST"])
@login_required
def username():
    """Change username"""

    # Check reuest method
    if request.method == "GET":

        # Display change usename web page
        return render_template("username.html", alerts=alerts, badge=badge())
    else:

        # Request parameters
        current = request.form.get("current")
        username = request.form.get("username")
        password = request.form.get("password")

        # Connect with the SQLite database
        db = sqlite3.connect('project/hotels.db')

        # Ensure current username and password are corrects
        rows = db.execute("SELECT username, hash FROM users WHERE id = ?", (session["user_id"],)).fetchall()
        if not len(rows) == 1 or not rows[0][0] == current or not check_password_hash(rows[0][1], password):
            flash("Invalid current username and/or password", 'warning')
            return redirect("/change_username")

        # Check usernames are differents
        if not current != username:
            flash("Usernames aren't different", 'info')
            return redirect("/change_username")

        # Ensure username doesn't exists
        rows = db.execute("SELECT username FROM users WHERE username = ?", (username,)).fetchall()
        if not len(rows) == 0:
            flash("New username already exists", 'info')
            return redirect("/change_username")

        # Update the account username
        db.execute("Update users SET username = :username WHERE id = :id", 
                    {'username': username, 'id': session['user_id']})

        # Save the changes
        db.commit()

        # Close database
        db.close()

        # Redirect user to home page
        flash("Change username success", 'success')
        return redirect("/")


@app.route("/change_password", methods=["GET", "POST"])
@login_required
def password():
    """Change password"""

    # Check request method
    if request.method == "GET":

        # Display change password web page
        return render_template("password.html", alerts=alerts, badge=badge())
    else:

        # Request parameters
        current = request.form.get("current")
        password = request.form.get("password")
        confirm = request.form.get("confirm")

        # Connect with the SQLite database
        db = sqlite3.connect('project/hotels.db')

        # Ensure current password is correct
        rows = db.execute("SELECT hash FROM users WHERE id = ?", (session['user_id'],)).fetchall()
        if not len(rows) == 1 or not check_password_hash(rows[0][0], current):
            flash("Invalid current password", 'warning')
            return redirect("/change_password")

        # Ensure current and new password are different
        if not current != password:
            flash("Current and new password aren't different", 'warning')
            return redirect("change_password")

        # Ensure passwords match
        if not password == confirm:
            flash("Passwords don't match", 'info')
            return redirect("change_password")

        # Update the account password
        db.execute("UPDATE users SET hash = :hash WHERE id = :id", 
                    {'hash': generate_password_hash(password), 'id': session['user_id']})

        # Save the changes
        db.commit()

        # Close database
        db.close()

        # Redirect use to home page
        flash("Change password success", 'success')
        return redirect("/")


@app.route("/delete_account", methods=["GET", "POST"])
@login_required
def delete():
    """Delete account"""

    # Check request method
    if request.method == "GET":

        # Display delete web page
        return render_template("delete.html", alerts=alerts, badge=badge())
    else:

        # Request parameters
        username = request.form.get("username")
        password = request.form.get("password")

        # Connect with SQLite database
        db = sqlite3.connect('project/hotels.db')

        # Ensure username and password is correct
        rows = db.execute("SELECT username, hash FROM users WHERE id = ?", (session['user_id'],)).fetchall()
        if not len(rows) == 1 or not rows[0][0] == username or not check_password_hash(rows[0][1], password):
            flash("Invalid username and/or password", 'warning')
            return redirect("/delete_account")

        # Database query to delete account
        db.execute("DELETE FROM wishlist WHERE user_id = ?", (session['user_id'],))
        db.execute("DELETE FROM users WHERE id = ?", (session['user_id'],))

        # Save the changes
        db.commit()

        # Close database
        db.close()

        # Log out of deleted user
        session.clear()

        # Redirect user to home page
        flash("Your account has been deleted", 'delete')
        return redirect("/")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return f"{e.name}, {e.code}"


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)