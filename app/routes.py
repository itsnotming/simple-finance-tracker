from flask import Blueprint, redirect, render_template, request, url_for

from app import db
from app.models import Transaction

main = Blueprint("main", __name__)


@main.route("/")
def home():
    transactions = Transaction.query.all()
    total_income = sum(
        transaction.amount
        for transaction in transactions
        if transaction.transaction_type == "income"
    )
    total_expense = sum(
        transaction.amount
        for transaction in transactions
        if transaction.transaction_type == "expense"
    )
    balance = total_income - total_expense

    return render_template(
        "index.html",
        transactions=transactions,
        balance=balance,
        total_income=total_income,
        total_expense=total_expense,
    )


@main.route("/add", methods=["GET", "POST"])
def add_transaction():
    if request.method == "POST":
        description = request.form["description"]
        amount = float(request.form["amount"])
        transaction_type = request.form["type"]
        category = request.form["category"]

        transaction = Transaction(
            description=description,
            amount=amount,
            transaction_type=transaction_type,
            category=category,
        )

        db.session.add(transaction)
        db.session.commit()

        return redirect(url_for("main.home"))

    return render_template("add.html")

@main.route("/edit/<int:transaction_id>", methods=["GET", "POST"])
def edit_transaction(transaction_id):
    transaction = db.get_or_404(Transaction, transaction_id)
    
    if request.method == "POST":
        transaction.description = request.form["description"]
        transaction.amount = float(request.form["amount"])
        transaction.transaction_type = request.form["type"]
        transaction.category = request.form["category"]
        
        db.session.commit()
        
        return redirect(url_for("main.home"))
    
    return render_template("edit.html", transaction=transaction)


@main.route("/delete/<int:transaction_id>", methods=["POST"])
def delete_transaction(transaction_id):
    transaction = db.get_or_404(Transaction, transaction_id)

    db.session.delete(transaction)
    db.session.commit()

    return redirect(url_for("main.home"))
