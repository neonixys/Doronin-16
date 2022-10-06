import json
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False
app.url_map.strict_slashes = False
db = SQLAlchemy(app)

PATH_USERS = 'data/users.json'
PATH_ORDERS = 'data/orders.json'
PATH_OFFERS = 'data/offers.json'


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    age = db.Column(db.Integer)
    email = db.Column(db.String)
    role = db.Column(db.String)
    phone = db.Column(db.String)

    def return_data(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "age": self.age,
            "email": self.email,
            "role": self.role,
            "phone": self.phone,
        }


class Order(db.Model):
    __tablename__ = "order_"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15), nullable=False)
    description = db.Column(db.String(30), nullable=False)
    start_date = db.Column(db.Integer)
    end_date = db.Column(db.Integer)
    address = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer)

    customer_id = db.Column(db.Integer, db.ForeignKey(f"{User.__tablename__}.id"))
    executor_id = db.Column(db.Integer, db.ForeignKey(f"{User.__tablename__}.id"))

    customer = db.relationship("User", foreign_keys=[customer_id])
    executor = db.relationship("User", foreign_keys=[executor_id])

    def return_data(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "address": self.address,
            "price": self.price,
            "customer_id": self.customer_id,
            "executor_id": self.executor_id,
        }


class Offer(db.Model):
    __tablename__ = "offer"
    id = db.Column(db.Integer, primary_key=True)

    order_id = db.Column(db.Integer, db.ForeignKey(f"{Order.__tablename__}.id"))
    executor_id = db.Column(db.Integer, db.ForeignKey(f"{User.__tablename__}.id"))

    order = db.relationship("Order")
    executor = db.relationship("User")

    def return_data(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "executor_id": self.executor_id,
        #     "order": self.order.return_data(),
        #     "executor": self.executor.return_data(),
        }


db.create_all()


def get_field_users(path: str, cls):
    with open(path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        for user_data in data:
            user = cls(**user_data)
            db.session.add(user)
        db.session.commit()


def get_field_offers(path: str, cls):
    with open(path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        for offer_data in data:
            offer = cls(**offer_data)
            db.session.add(offer)
        db.session.commit()


def get_field_orders(path: str, cls):
    with open(path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        for order_data in data:
            order = cls(**order_data)
            db.session.add(order)
        db.session.commit()


get_field_users(PATH_USERS, User)
get_field_offers(PATH_OFFERS, Offer)
get_field_orders(PATH_ORDERS, Order)


@app.route("/users", methods=['GET', 'POST'])
def page_users():
    if request.method == 'GET':
        result = []
        for user in User.query.all():
            result.append(user.return_data())

        return app.response_class(json.dumps(result),
                                  mimetype="application/json", status=200)

    if request.method == 'POST':
        data = request.json
        db.session.add(User(**data))
        db.session.commit()

        return app.response_class(json.dumps("User has been added"),
                                  mimetype="application/json", status=200)


@app.route("/users/<int:bid>", methods=['GET', 'PUT', 'DELETE'])
def page_user(bid):
    if request.method == 'GET':
        result = []
        for user in User.query.filter(User.id == bid).all():
            result.append(user.return_data())

        return app.response_class(json.dumps(result),
                                  mimetype="application/json", status=200)

    if request.method == 'PUT':
        data = request.json
        try:
            user = db.session.query(User).get(bid)
            user.id = data.get("id")
            user.first_name = data.get("first_name")
            user.last_name = data.get("last_name")
            user.age = data.get("age")
            user.email = data.get("email")
            user.role = data.get("role")
            user.phone = data.get("phone")

            db.session.commit()
        except Exception as e:
            print(e)

        return app.response_class(json.dumps("Users info has been updated"),
                                  mimetype="application/json", status=200)

    if request.method == 'DELETE':
        try:
            db.session.query(User).filter(User.id == bid).delete()
            db.session.commit()

        except Exception as e:
            print(e)

        return app.response_class(json.dumps("User has been deleted"),
                                  mimetype="application/json",
                                  status=200)


@app.route("/orders", methods=['GET', 'POST'])
def page_orders():
    if request.method == 'GET':
        result = []
        for order in Order.query.all():
            result.append(order.return_data())

        return app.response_class(json.dumps(result,
                                             ensure_ascii=False),
                                  mimetype="application/json",
                                  status=200)

    if request.method == 'POST':
        data = request.json
        db.session.add(Order(**data))
        db.session.commit()
        return app.response_class(json.dumps("Order has been added"),
                                  mimetype="application/json",
                                  status=200)


@app.route("/orders/<int:bid>", methods=['GET', 'PUT', 'DELETE'])
def page_order(bid):
    if request.method == 'GET':
        result = []
        for order in Order.query.filter(Order.id == bid).all():
            result.append(order.return_data())

        return app.response_class(json.dumps(result, ensure_ascii=False),
                                  mimetype="application/json",
                                  status=200)

    if request.method == 'PUT':
        data = request.json
        try:
            order = db.session.query(Order).get(bid)
            order.id = data.get("id")
            order.name = data.get("name")
            order.description = data.get("description")
            order.start_date = data.get("start_date")
            order.end_date = data.get("end_date")
            order.address = data.get("address")
            order.price = data.get("price")
            order.customer_id = data.get("customer_id")
            order.executor_id = data.get("executor_id")

            db.session.commit()
        except Exception as e:
            print(e)

        return app.response_class(json.dumps("Order has been updated"),
                                  mimetype="application/json", status=200)

    if request.method == 'DELETE':
        try:
            db.session.query(Order).filter(Order.id == bid).delete()
            db.session.commit()

        except Exception as e:
            print(e)

        return app.response_class(json.dumps("Order has been deleted"),
                                  mimetype="application/json",
                                  status=200)


@app.route("/offers", methods=['GET', 'POST'])
def page_offers():
    if request.method == 'GET':
        result = []
        for offer in Offer.query.all():
            result.append(offer.return_data())

        return app.response_class(json.dumps(result, ensure_ascii=False),
                                  mimetype="application/json",
                                  status=200)

    if request.method == 'POST':
        data = request.json
        db.session.add(Offer(**data))
        db.session.commit()

        return app.response_class(json.dumps("Offer has been added"),
                                  mimetype="application/json",
                                  status=200)


@app.route("/offers/<int:bid>", methods=['GET', 'PUT', 'DELETE'])
def page_offer(bid):
    if request.method == 'GET':
        result = []
        for offer in Offer.query.filter(Offer.id == bid).all():
            result.append(offer.return_data())

        return app.response_class(json.dumps(result, ensure_ascii=False),
                                  mimetype="application/json",
                                  status=200)

    if request.method == 'PUT':
        data = request.json
        try:
            offer = db.session.query(Offer).get(bid)
            offer.id = data.get("id")
            offer.order_id = data.get("order_id")
            offer.executor_id = data.get("executor_id")
            db.session.commit()

        except Exception as e:
            print(e)

        return app.response_class(json.dumps("Offer has benn updated"),
                                  mimetype="application/json", status=200)

    if request.method == 'DELETE':
        try:
            db.session.query(Offer).filter(Offer.id == bid).delete()
            db.session.commit()

        except Exception as e:
            print(e)

        return app.response_class(json.dumps("Offer has been deleted"),
                                  mimetype="application/json",
                                  status=200)

if __name__ == "__main__":
    app.run(debug=True)
