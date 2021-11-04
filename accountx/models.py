import enum
import datetime
from flask_sqlalchemy import model
from sqlalchemy.orm import relationship
from marshmallow import fields
from IPython import embed

from accountx import db, ma, utils

# Models
class TxnType(enum.Enum):
    debit = 1
    credit = 2

    def __str__(self):
        return self.value


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    password_hash = db.Column(db.Text(), nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    entries = relationship("Entry", back_populates="user", cascade="delete")
    accounts = relationship("Account", cascade="delete")
    currency_symbol = db.Column(db.String(255))
    timezone = db.Column(db.String(255))
    onboarded = db.Column(db.Boolean, default=False)

    def __init__(self, name, email):
        self.email = email
        self.name = name

    def __repr__(self):
        return f"<User : {self.id} - {self.name}>"

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


@db.event.listens_for(User, "after_insert")
def after_insert(mapper, connection, target):
    account = Account("SELF")
    account.user = target
    db.session.add(account)


class Account(db.Model):
    __tablename__ = "accounts"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    user = relationship("User", back_populates="accounts")
    name = db.Column(db.String(255), nullable=False)
    entries = relationship(
        "Entry",
        primaryjoin="and_(Account.id==Entry.from_account_id, "
        "Account.id==Entry.to_account_id)",
    )

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"<Account {self.id} : {self.name}>"

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Entry(db.Model):
    __tablename__ = "entries"
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column("type", db.Enum(TxnType))
    amount = db.Column(db.Numeric, nullable=False)
    description = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    user = relationship("User", back_populates="entries")
    from_account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"))
    to_account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"))
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    from_account = relationship(
        "Account", foreign_keys=[from_account_id], overlaps="from_account, entries"
    )
    to_account = relationship(
        "Account", foreign_keys=[to_account_id], overlaps="to_account, entries"
    )

    def __repr__(self):
        return f"<Txn : {self.id} : {str(self.type.name)} : {self.amount}>"

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model: User
        fields = ("name", "email", "id")

    pass


class AccountSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model: Account
        include_fk = True
        fields = ("id", "name")

    pass


class EntrySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Entry
        fields = (
            "id",
            "created_date",
            "user",
            "from_account",
            "to_account",
            "type",
            "amount",
            "description",
        )
        include_fk = True

    created_date = fields.DateTime()
    user = fields.Nested(UserSchema)
    type = fields.Method("get_type")
    from_account = fields.Nested(AccountSchema)
    to_account = fields.Nested(AccountSchema)
    amount = fields.Method("get_amount")

    def get_type(self, obj):
        return obj.type.name

    def get_amount(self, obj):
        return "%.2f" % obj.amount

    def on_bind_field(self, field_name, field_obj):
        field_obj.data_key = utils.camelcase(field_obj.data_key or field_name)

    pass
