import enum
import datetime
from flask_sqlalchemy import model
from pytz import timezone
from sqlalchemy.orm import relationship, session, aliased
from marshmallow import fields
from IPython import embed
from sqlalchemy.sql.elements import or_

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
    self = Account("SELF")
    self.user = target
    cash = Account("CASH")
    cash.user = target
    bank = Account("BANK")
    bank.user = target
    db.session.add_all([self, cash, bank])


class Account(db.Model):
    __tablename__ = "accounts"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    user = relationship("User", back_populates="accounts")
    name = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
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

    def check_and_delete(self, db) -> bool:
        total_entries = self.get_entries()
        print(f"total count {total_entries}")
        if total_entries == 0:
            db.session.delete(self)
            db.session.commit()
            return True
        else:
            return False

    def get_entries(self):
        query = Entry.query.filter(
            or_(Entry.from_account_id == self.id, Entry.to_account_id == self.id)
        )
        return query.count()


class Entry(db.Model):
    __tablename__ = "entries"
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column("type", db.Enum(TxnType))
    amount = db.Column(db.Numeric, nullable=False)
    description = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    user: User = relationship("User", back_populates="entries")
    from_account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"))
    to_account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"))
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow())

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

    @property
    def created_date_localized(self):
        utc_tz = timezone("UTC")
        user_tz = timezone(self.user.timezone)

        print(f"user timezone {self.user.timezone}")

        utc_time = utc_tz.localize(self.created_date)
        return utc_time.astimezone(user_tz)


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
            "created_date_localized",
        )
        include_fk = True

    created_date = fields.DateTime()
    user = fields.Nested(UserSchema)
    type = fields.Method("get_type")
    from_account = fields.Nested(AccountSchema)
    to_account = fields.Nested(AccountSchema)
    amount = fields.Method("get_amount")
    created_date_localized = fields.Method("get_created_date_localized")

    def get_type(self, obj):
        return obj.type.name

    def get_amount(self, obj):
        return "%.2f" % obj.amount

    def get_created_date_localized(self, obj: Entry):
        return str(obj.created_date_localized)

    def on_bind_field(self, field_name, field_obj):
        field_obj.data_key = utils.camelcase(field_obj.data_key or field_name)

    pass
