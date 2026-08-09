from app import create_app


def test_create_app():
    app = create_app()

    assert app is not None



def test_home_filters_transactions_by_category():
    from app import db
    from app.models import Transaction

    app = create_app()
    app.config.update(TESTING=True)

    descriptions = [
        "Filter test grocery income",
        "Filter test book expense",
    ]

    with app.app_context():
        Transaction.query.filter(
            Transaction.description.in_(descriptions)
        ).delete(synchronize_session=False)
        db.session.add(
            Transaction(
                description="Filter test grocery income",
                amount=100.00,
                transaction_type="income",
                category="Groceries Filter Test",
            )
        )
        db.session.add(
            Transaction(
                description="Filter test book expense",
                amount=30.00,
                transaction_type="expense",
                category="Books Filter Test",
            )
        )
        db.session.commit()

        all_transactions = Transaction.query.all()
        total_income = sum(
            transaction.amount
            for transaction in all_transactions
            if transaction.transaction_type == "income"
        )
        total_expense = sum(
            transaction.amount
            for transaction in all_transactions
            if transaction.transaction_type == "expense"
        )
        balance = total_income - total_expense

        response = app.test_client().get(
            "/", query_string={"category": "Groceries Filter Test"}
        )
        html = response.get_data(as_text=True)

        assert response.status_code == 200
        assert "Filter test grocery income" in html
        assert "Filter test book expense" not in html
        assert "Groceries Filter Test" in html
        assert "Books Filter Test" in html
        assert f"Total Income: ${total_income:.2f}" in html
        assert f"Total Expense: ${total_expense:.2f}" in html
        assert f"Balance: ${balance:.2f}" in html

        Transaction.query.filter(
            Transaction.description.in_(descriptions)
        ).delete(synchronize_session=False)
        db.session.commit()
