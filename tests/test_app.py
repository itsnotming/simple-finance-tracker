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



def test_home_searches_transactions_by_description():
    from app import db
    from app.models import Transaction

    app = create_app()
    app.config.update(TESTING=True)

    descriptions = [
        "Search test Coffee",
        "Search test Sandwich",
    ]

    with app.app_context():
        Transaction.query.filter(
            Transaction.description.in_(descriptions)
        ).delete(synchronize_session=False)
        db.session.add(
            Transaction(
                description="Search test Coffee",
                amount=4.50,
                transaction_type="expense",
                category="Search Test Food",
            )
        )
        db.session.add(
            Transaction(
                description="Search test Sandwich",
                amount=9.00,
                transaction_type="expense",
                category="Search Test Food",
            )
        )
        db.session.commit()

        response = app.test_client().get("/", query_string={"search": "cof"})
        html = response.get_data(as_text=True)

        assert response.status_code == 200
        assert "Search test Coffee" in html
        assert "Search test Sandwich" not in html
        assert 'value="cof"' in html

        Transaction.query.filter(
            Transaction.description.in_(descriptions)
        ).delete(synchronize_session=False)
        db.session.commit()



def test_home_sorts_transactions_by_amount():
    from app import db
    from app.models import Transaction

    app = create_app()
    app.config.update(TESTING=True)

    descriptions = [
        "Sort test Cheap",
        "Sort test Expensive",
    ]

    with app.app_context():
        Transaction.query.filter(
            Transaction.description.in_(descriptions)
        ).delete(synchronize_session=False)
        db.session.add(
            Transaction(
                description="Sort test Cheap",
                amount=2.00,
                transaction_type="expense",
                category="Sort Test",
            )
        )
        db.session.add(
            Transaction(
                description="Sort test Expensive",
                amount=20.00,
                transaction_type="expense",
                category="Sort Test",
            )
        )
        db.session.commit()

        response = app.test_client().get(
            "/", query_string={"category": "Sort Test", "sort": "amount_desc"}
        )
        html = response.get_data(as_text=True)

        assert response.status_code == 200
        assert html.index("Sort test Expensive") < html.index("Sort test Cheap")
        assert 'value="amount_desc" selected' in html

        Transaction.query.filter(
            Transaction.description.in_(descriptions)
        ).delete(synchronize_session=False)
        db.session.commit()



def test_home_combines_category_search_and_sort():
    from app import db
    from app.models import Transaction

    app = create_app()
    app.config.update(TESTING=True)

    descriptions = [
        "Combo test Coffee Small",
        "Combo test Coffee Large",
        "Combo test Coffee Office",
        "Combo test Tea",
    ]

    with app.app_context():
        Transaction.query.filter(
            Transaction.description.in_(descriptions)
        ).delete(synchronize_session=False)
        db.session.add(
            Transaction(
                description="Combo test Coffee Small",
                amount=3.00,
                transaction_type="expense",
                category="Combo Test Food",
            )
        )
        db.session.add(
            Transaction(
                description="Combo test Coffee Large",
                amount=6.00,
                transaction_type="expense",
                category="Combo Test Food",
            )
        )
        db.session.add(
            Transaction(
                description="Combo test Coffee Office",
                amount=12.00,
                transaction_type="expense",
                category="Combo Test Work",
            )
        )
        db.session.add(
            Transaction(
                description="Combo test Tea",
                amount=2.00,
                transaction_type="expense",
                category="Combo Test Food",
            )
        )
        db.session.commit()

        all_transactions = Transaction.query.all()
        total_expense = sum(
            transaction.amount
            for transaction in all_transactions
            if transaction.transaction_type == "expense"
        )

        response = app.test_client().get(
            "/",
            query_string={
                "category": "Combo Test Food",
                "search": "coffee",
                "sort": "amount_asc",
            },
        )
        html = response.get_data(as_text=True)

        assert response.status_code == 200
        assert "Combo test Coffee Small" in html
        assert "Combo test Coffee Large" in html
        assert "Combo test Coffee Office" not in html
        assert "Combo test Tea" not in html
        assert html.index("Combo test Coffee Small") < html.index("Combo test Coffee Large")
        assert 'value="coffee"' in html
        assert 'value="amount_asc" selected' in html
        assert f"Total Expense: ${total_expense:.2f}" in html

        Transaction.query.filter(
            Transaction.description.in_(descriptions)
        ).delete(synchronize_session=False)
        db.session.commit()
