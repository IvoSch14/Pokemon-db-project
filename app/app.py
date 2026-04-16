from flask import Flask, jsonify, request
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from db import get_db, close_db

app = Flask(__name__)

@app.teardown_appcontext
def teardown_db(exception):
    close_db(exception)

@app.route("/test")
def test():
    return jsonify({"message" : "Flask is working"})

@app.route("/")
def home():
    return "Pokemon Card Price Tracker Home Page"

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password_hash = request.form["password"]

        db = get_db()
        db.execute("""
            INSERT INTO users (username, email, password_hash, created_at)
            VALUES (?, ?, ?, ?)
        """, (username, email, password_hash, datetime.now().isoformat()))
        db.commit()

        return "User registered successfully."

    return """
    <form method="post">
        Username: <input name="username"><br>
        Email: <input name="email"><br>
        Password: <input name="password"><br>
        <button type="submit">Register</button>
    </form>
    """

@app.route("/add_set", methods=["GET", "POST"])
def add_set():
    if request.method == "POST":
        set_name = request.form["set_name"]
        release_date = request.form["release_date"]
        series = request.form["series"]

        db = get_db()
        db.execute("""
            INSERT INTO sets (set_name, release_date, series)
            VALUES (?, ?, ?)
        """, (set_name, release_date, series))
        db.commit()

        return "Set added successfully."

    return """
    <form method="post">
        Set Name: <input name="set_name"><br>
        Release Date: <input name="release_date"><br>
        Series: <input name="series"><br>
        <button type="submit">Add Set</button>
    </form>
    """

@app.route("/add_card", methods=["GET", "POST"])
def add_card():
    if request.method == "POST":
        card_name = request.form["card_name"]
        card_number = request.form["card_number"]
        rarity = request.form["rarity"]
        card_type = request.form["type"]
        set_id = request.form["set_id"]
        image_url = request.form["image_url"]

        db = get_db()
        db.execute("""
            INSERT INTO cards (card_name, card_number, rarity, type, set_id, image_url)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (card_name, card_number, rarity, card_type, set_id, image_url))
        db.commit()

        return "Card added successfully."

    return """
    <form method="post">
        Card Name: <input name="card_name"><br>
        Card Number: <input name="card_number"><br>
        Rarity: <input name="rarity"><br>
        Type: <input name="type"><br>
        Set ID: <input name="set_id"><br>
        Image URL: <input name="image_url"><br>
        <button type="submit">Add Card</button>
    </form>
    """

@app.route("/add_card_from_api", methods=["POST"])
def add_card_from_api():
    data = request.get_json()

    card_name = data.get("name")
    rarity = data.get("rarity")

    db = get_db()
    db.execute("""
        INSERT INTO cards (card_name, rarity)
        VALUES (?, ?)
    """, (card_name, rarity))
    db.commit()

    return jsonify({"message": "Card added from API"})

@app.route("/search_cards")
def search_cards():
    search_term = request.args.get("q", "")

    db = get_db()
    cards = db.execute("""
        SELECT * FROM cards
        WHERE card_name LIKE ?
    """, ('%' + search_term + '%',)).fetchall()

    output = "<h1>Search Results</h1>"
    for card in cards:
        output += f"<p>{card['card_name']} - {card['rarity']}</p>"

    return output

@app.route("/update_email", methods=["GET", "POST"])
def update_email():
    if request.method == "POST":
        user_id = request.form["user_id"]
        new_email = request.form["new_email"]

        db = get_db()
        db.execute("""
            UPDATE users
            SET email = ?
            WHERE user_id = ?
        """, (new_email, user_id))
        db.commit()

        return "Email updated."

    return """
    <form method="post">
        User ID: <input name="user_id"><br>
        New Email: <input name="new_email"><br>
        <button type="submit">Update</button>
    </form>
    """

@app.route("/delete_card/<int:card_id>")
def delete_card(card_id):
    db = get_db()
    db.execute("""
        DELETE FROM cards
        WHERE card_id = ?
    """, (card_id,))
    db.commit()

    return "Card deleted."

@app.route("/user_watchlist/<int:user_id>")
def user_watchlist(user_id):
    db = get_db()
    rows = db.execute("""
        SELECT watchlist.watchlist_id,
               users.username,
               cards.card_name,
               cards.rarity,
               watchlist.target_price,
               watchlist.alert_direction
        FROM watchlist
        JOIN users ON watchlist.user_id = users.user_id
        JOIN cards ON watchlist.card_id = cards.card_id
        WHERE users.user_id = ?
    """, (user_id,)).fetchall()

    output = "<h1>User Watchlist</h1>"
    for row in rows:
        output += f"""
        <p>
            {row['username']} is tracking {row['card_name']}
            ({row['rarity']}) -
            Target: {row['alert_direction']} ${row['target_price']}
        </p>
        """

    return output

@app.route("/average_price/<int:card_id>")
def average_price(card_id):
    db = get_db()
    row = db.execute("""
        SELECT AVG(price_value) AS avg_price
        FROM price_history
        WHERE card_id = ?
    """, (card_id,)).fetchone()

    if row["avg_price"] is None:
        return "No price history found."

    return f"Average price: ${row['avg_price']:.2f}"


if __name__ == "__main__":
    app.run(debug=True)