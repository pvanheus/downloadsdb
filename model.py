from downloadsdb import db


class Collection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    display_name = db.Column(db.String, unique=True, index=True, nullable=True)
    path = db.Column(db.String, unique=True, nullable=False)
    series_id = db.Column(db.Integer, db.ForeignKey('series.id'), nullable=True)
    season = db.Column(db.Integer, nullable=True, unique=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('collection.id'), nullable=True)
    parent = db.relationship('Collection', backref=db.backref('children'))

    series = db.relationship('Series', backref=db.backref('collections'))

    @property
    def name(self) -> str:
        return self.path if self.display_name.is_(None) else self.path

    @property
    def size(self) -> int:
        return sum((item.size for item in self.items))


class Series(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, index=True)


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    display_name = db.Column(db.String, unique=True, nullable=True)
    path = db.Column(db.String, nullable=False)
    size = db.Column(db.Integer, nullable=False)
    md5sum = db.Column(db.String, nullable=True)
    collection_id = db.Column(db.Integer, db.ForeignKey('collection.id'), nullable=True)

    collection = db.relationship('Collection', backref=db.backref('items'))

    @property
    def name(self):
        return self.path if self.display_name.is_(None) else self.path