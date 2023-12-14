from uuid import uuid4
from datetime import datetime

from flask_login import login_user

from app.factory import db


def rand_id():
    return str(uuid4())


class User(db.Model):
    """
    Mission booth staff who will be creating raffle entries and prizes, managing the backend.
    """
    __tablename__ = 'users'

    id = db.Column(db.String(50), primary_key=True)
    register_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_login_date = db.Column(db.DateTime, nullable=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(50), unique=True, nullable=False)
    profile_pic = db.Column(db.String(150))

    def __repr__(self):
        return str(self.id)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def login(self):
        self.last_login_date = datetime.utcnow()
        login_user(self)
        db.session.commit()


class Entry(db.Model):
    """
    Raffle ticket for visitors to the booth who wish to enter a raffle.
    """
    __tablename__ = 'entries'

    id = db.Column(db.Integer, primary_key=True, unique=True)
    uuid = db.Column(db.String(100), default=rand_id, unique=True)
    create_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.ForeignKey('users.id'))
    confirmed = db.Column(db.Boolean, default=False)
    has_won = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return str(self.uuid)


class Prize(db.Model):
    """
    Prizes that can be won by raffle entrants. Can be used by multiple drawings.
    """
    __tablename__ = 'prizes'

    id = db.Column(db.Integer, primary_key=True, unique=True)
    name = db.Column(db.String(150))
    image_url = db.Column(db.String(300))
    description = db.Column(db.String(1200))
    ship_to_winner = db.Column(db.Boolean)
    create_date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return str(self.name)


class Drawing(db.Model):
    """
    Drawing events are held at the booth and pick a random winner for a series of prizes.
    """
    __tablename__ = 'drawings'

    id = db.Column(db.Integer, primary_key=True, unique=True)
    name = db.Column(db.String(50))
    date_started = db.Column(db.DateTime, nullable=True)
    date_ended = db.Column(db.DateTime, nullable=True)
    create_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=False)
    has_concluded = db.Column(db.Boolean, default=False)

    def get_next_prize(self):
        drawing_prizes = DrawingPrize.query.filter(
            DrawingPrize.drawing_id == self.id,
            DrawingPrize.confirmed_winner == None
        ).order_by(DrawingPrize.create_date.asc())
        return drawing_prizes.first()
    
    def end(self):
        self.date_ended = datetime.utcnow()
        self.is_active = False
        self.has_concluded = True
        db.session.commit()
    
    def start(self):
        self.date_started = datetime.utcnow()
        self.is_active = True
        db.session.commit()

    def __repr__(self):
        return str(self.name)


class DrawingPrize(db.Model):
    """
    Association objects for drawings and prizes; includes winner.
    """
    __tablename__ = 'drawingprizes'

    id = db.Column(db.Integer, primary_key=True, unique=True)
    prize_id = db.Column(db.ForeignKey('prizes.id', ondelete='CASCADE'))
    prize = db.relationship('Prize')
    drawing_id = db.Column(db.ForeignKey('drawings.id', ondelete='CASCADE'))
    drawing = db.relationship('Drawing')
    confirmed_winner_id = db.Column(db.ForeignKey('entries.id'))
    confirmed_winner = db.relationship('Entry', foreign_keys=[confirmed_winner_id])
    selected_entry_id = db.Column(db.ForeignKey('entries.id'))
    selected_entry = db.relationship('Entry', foreign_keys=[selected_entry_id])
    create_date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return str(self.id)