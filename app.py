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

#############################
# Routes for Flask
# HOME
@app.route("/")
def home():

    search_query = request.args.get('q', '').strip()
    sort_param = request.args.get('sort', 'title')

    stmt = db.select(Book).join(Author)

    if search_query:
        stmt = stmt.where(
            db.or_(
                Book.title.icontains(search_query),
                Author.name.icontains(search_query)
            )
        )

    if sort_param == 'author':
        stmt = stmt.order_by(Author.name)
    else:
        stmt = stmt.order_by(Book.title)

    query = db.select(Book).join(Author)

    if sort_param == 'author':
        query = query.order_by(Author.name)
    elif sort_param == 'year':
        query = query.order_by(Book.publication_year.desc())
    else:
        query = query.order_by(Book.title)

    books = db.session.execute(stmt).scalars().all()

    return render_template('home.html',
                            books=books,
                            search_query=search_query,
                            current_sort=sort_param)

# ADD_author
@app.route("/add_author", methods=["GET", "POST"])
def add_author():
    if request.method == "POST":

        name = request.form.get("name")
        birth_date = request.form.get("birthdate")
        year_of_death = request.form.get("date_of_death")

        if not name or not birth_date:
            flash("Name und Geburtsdatum sind erforderlich!", "error")
            return redirect(url_for('add_author'))

        new_author = Author()
        new_author.name = name
        new_author.birth_date = birth_date
        new_author.year_of_death = year_of_death if year_of_death else None


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

    return render_template("add_author.html")

# ADD_BOOK
@app.route("/add_book", methods=("GET", "POST"))
def add_book():

    if request.method == "POST":
        title = request.form.get("title")
        author_id = request.form.get("author_id")
        isbn = request.form.get("isbn")
        publication_year = request.form.get("publication_year")

        if not title or not author_id or not isbn or not publication_year:
            flash("Bitte fülle alle Felder aus!", "error")
            return redirect(url_for('add_book'))

        try:
            new_book = Book()
            new_book.title = title
            new_book.author_id = int(author_id)
            new_book.isbn = isbn
            new_book.publication_year = publication_year

            db.session.add(new_book)
            db.session.commit()
            flash(f"Buch mit ISBN {isbn} wurde erfolgreich hinzugefügt!", "success")
            return redirect(url_for('add_book'))
        except Exception as e:
            db.session.rollback()
            flash(f"Fehler beim Speichern: {str(e)}", "error")

        return redirect(url_for('add_book'))

    authors = db.session.execute(db.select(Author).order_by(Author.name)).scalars().all()
    return render_template("add_book.html", authors=authors)

# DELET EBOOK
@app.route("/book/<int:book_id>/delete", methods=["POST"])
def delete_book(book_id):
    book = db.session.get(Book, book_id)
    if book:
        title = book.title
        db.session.delete(book)
        db.session.commit()
        flash(f"Das Buch '{title}' wurde gelöscht.", "success")
    return redirect(url_for('home'))

# DELETE AUTHOR
@app.route("/author/<int:author_id>/delete", methods=["POST"])
def delete_author(author_id):
    author = db.session.get(Author, author_id)
    if author:
        # Prüfung: Hat der Autor noch Bücher?
        if author.books:
            flash(f"Fehler: '{author.name}' kann nicht gelöscht werden, da noch Bücher von ihm existieren.", "error")
        else:
            name = author.name
            db.session.delete(author)
            db.session.commit()
            flash(f"Autor '{name}' wurde gelöscht.", "success")
    return redirect(url_for('home'))

#############################
# Python
def get_book_details(isbn):
    url = f"https://googleapis.com:{isbn}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if "items" in data:
            # Holt den Link zum Vorschaubild (thumbnail)
            image_links = data["items"][0]["volumeInfo"].get("imageLinks", {})
            return image_links.get("thumbnail")
    return None

def main():
    app.run(debug=True, use_reloader=True)


if __name__ == '__main__':
    main()


