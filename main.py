from flask import Flask, render_template, redirect, url_for, flash, get_flashed_messages
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import DataRequired, NumberRange, InputRequired

# create the extension
db = SQLAlchemy()


# Define Models
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    rating = db.Column(db.Float, nullable=False)

    # Optional: this will allow each book object to be identified by its title when printed.
    def __repr__(self):
        return f'<Book {self.title}>'


# create the app
app = Flask(__name__)
app.config['SECRET_KEY'] = '8Bhkdlgldrgtl23'
Bootstrap(app)

# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///../new-books-collection.db"

# initialize the app with the extension
db.init_app(app)

# Create db with all columns
with app.app_context():
    db.create_all()


# FlaskForm to add items
class BookForm(FlaskForm):
    title = StringField("Tilte", validators=[DataRequired(message="Enter a Book Tilte")])
    book_author = StringField("Author", validators=[DataRequired(message="Missing Author's name")])
    rating = FloatField("Rating", validators=[DataRequired("Add a valid rating"),
                                              NumberRange(min=1, max=10, message='Rating must be between 1 and 10')])
    submit = SubmitField(label="Add Book")


# New rating FlaskForm for the update rating
class NewRatingForm(FlaskForm):
    new_rating = FloatField("New Rating", validators=[InputRequired(), NumberRange(min=0, max=10)])
    change_rating = SubmitField("Update Rating")


@app.route('/')
def home():
    # READ ALL RECORDS
    all_books = db.session.query(Book).all()
    print(all_books)
    return render_template("index.html", all_books=all_books, len=len)


# Add items
@app.route("/add", methods=["GET", "POST"])
def add():
    form = BookForm()
    if form.validate_on_submit():
        # Read A Particular Record By Query in the db
        existing_book = Book.query.filter_by(title=form.title.data).first()
        # if the book is not in the db
        if existing_book is None:
            new_book = Book(title=form.title.data, author=form.book_author.data, rating=form.rating.data)
            db.session.add(new_book)
            db.session.commit()
            print(f"New book added!{new_book}")

        # if the book already in the db
        else:
            print("Book already exists in the database.")

        return redirect(url_for("home"))

    return render_template("add.html", form=form)


# Update rating
@app.route("/edit/<int:book_id>", methods=["GET", "POST"])
def edit_rating(book_id):
    form = NewRatingForm()
    book = Book.query.get(book_id)
    print(book)
    if form.validate_on_submit():
        book.rating = form.new_rating.data
        db.session.commit()
        print(f"Book {book} Rating updated successfully!")
        flash("Rating updated successfully!", "success")
        return redirect(url_for("home"))
    return render_template("edit-rating.html", book=book, form=form)


# Delete items
@app.route("/delete/id=<int:book_id>")
def delete(book_id):
    book = Book.query.get(book_id)
    db.session.delete(book)
    db.session.commit()
    flash("Book deleted successfully!", "success")
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
