from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates, relationship
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)


class Hero(db.Model, SerializerMixin):
    __tablename__ = 'heroes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    super_name = db.Column(db.String)

    hero_powers = relationship('HeroPower', backref='hero', cascade='all, delete-orphan')
    powers = association_proxy('hero_powers', 'power')

    serialize_rules = ('-hero_powers.hero',)

    def __repr__(self):
        return f'<Hero {self.id}>'


class Power(db.Model, SerializerMixin):
    __tablename__ = 'powers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)

    hero_powers = relationship('HeroPower', backref='power', cascade='all, delete-orphan')
    heroes = association_proxy('hero_powers', 'hero')

    serialize_rules = ('-hero_powers.power',)

    @validates('description')
    def validate_description(self, key, value):
        if not value or len(value) < 20:
            raise ValueError("Description must be at least 20 characters.")
        return value

    def __repr__(self):
        return f'<Power {self.id}>'


class HeroPower(db.Model, SerializerMixin):
    __tablename__ = 'hero_powers'

    id = db.Column(db.Integer, primary_key=True)
    strength = db.Column(db.String, nullable=False)

    hero_id = db.Column(db.Integer, db.ForeignKey('heroes.id'))
    power_id = db.Column(db.Integer, db.ForeignKey('powers.id'))

    serialize_rules = ('-hero.hero_powers', '-power.hero_powers')

    @validates('strength')
    def validate_strength(self, key, value):
        if value not in ['Strong', 'Weak', 'Average']:
            raise ValueError("Strength must be 'Strong', 'Weak', or 'Average'.")
        return value

    def __repr__(self):
        return f'<HeroPower {self.id}>'
