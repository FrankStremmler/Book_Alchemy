from datetime import date
import os
from flask import Flask, render_template, request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Date, String, Float, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from data_models import db, Author, Book

# Constants
#SQL_DATABASE =f"sqlite:///{os.path.join(basedir, 'data/library.sqlite')}"

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/library.sqlite')}"
app.config['SECRET_KEY'] = "secret"

db.init_app(app)


# Routes for Flask
@app.route("/")
def home():
    books = db.session.execute(db.select(Book)).scalars().all()
    print(books )
    return render_template('home.html', books=books)

@app.route("/add_author", methods=["GET", "POST"])
def add_author():
    if request.method == "POST":
        # Daten aus dem Formular abrufen
        name = request.form.get("name")
        birth_date = request.form.get("birthdate")
        year_of_death = request.form.get("date_of_death")

        # Validierung (einfaches Beispiel)
        if not name or not birth_date:
            flash("Name und Geburtsdatum sind erforderlich!", "error")
            return redirect(url_for('add_author'))

        # Neuen Autor-Datensatz erstellen
        new_author = Author()
        new_author.name = name
        new_author.birth_date = birth_date
        new_author.year_of_death = year_of_death if year_of_death else str(date.min.year)

        try:
            print("Try add")
            db.session.add(new_author)
            print("Try commit")
            db.session.commit()
            print("commited")
            flash(f"Autor '{name}' wurde erfolgreich hinzugefügt!", "success")
        except Exception as e:
            print("Fehler")
            db.session.rollback()
            flash(f"Fehler beim Speichern: {str(e)}", "error")

        return redirect(url_for('add_author'))

    # Bei GET-Request: Formular anzeigen
    return render_template("add_author.html")

@app.route("/add_book")
def add_book():
    authors = db.session.execute(db.select(Author).order_by(Author.name)).scalars().all()

    if request.method == "POST":
        title = request.form.get("title")
        author_id = request.form.get("author_id")
        isbn = request.form.get("isbn")
        year = request.form.get("publication_year")

        if not author_id or not isbn or not year:
            flash("Bitte fülle alle Felder aus!", "error")
            return redirect(url_for('add_book'))

        try:
            new_book = Book()
            new_book.title = title
            new_book.author_id = int(selected_author_id)
            new_book.isbn = isbn
            new_book.publication_year = year

            db.session.add(new_book)
            db.session.commit()
            flash(f"Buch mit ISBN {isbn} wurde erfolgreich hinzugefügt!", "success")
            return redirect(url_for('add_book'))
        except Exception as e:
            db.session.rollback()
            flash(f"Fehler beim Speichern: {str(e)}", "error")

        return redirect(url_for('add_book'))

    return render_template("add_book.html", authors=authors)


def main():
    app.run(debug=True, use_reloader=True, host='127.0.0.1', port=5000)


if __name__ == '__main__':
    main()

# with app.app_context():
#     db.create_all()

