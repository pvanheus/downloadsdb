from downloadsdb import db
from math import log2

_suffixes = ['bytes', 'KiB', 'MiB', 'GiB', 'TiB', 'EiB', 'ZiB']

# from http://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
def file_size(size):
    # determine binary order in steps of size 10
    # (coerce to int, // still returns a float)
    order = int(log2(size) / 10) if size else 0
    # format file size
    # (.4g results in rounded numbers for exact matches and max 3 decimals,
    # should never resort to exponent values)

    return '{:.4g} {}'.format(size / (1 << (order * 10)), _suffixes[order])


class Collection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    display_name = db.Column(db.String, unique=True, index=True, nullable=True)
    path = db.Column(db.String, unique=True, nullable=False)
    series_id = db.Column(db.Integer, db.ForeignKey('series.id'), nullable=True)
    season = db.Column(db.Integer, nullable=True, unique=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('collection.id'), nullable=True)
    children = db.relationship('Collection', backref=db.backref('parent', remote_side=[id]))

    series = db.relationship('Series', backref=db.backref('collections'))

    @property
    def name(self) -> str:
        return self.path if self.display_name is None else self.path

    @property
    def size(self) -> int:
        return sum((item.size for item in self.items)) + sum((child.size for child in self.children))

    def __repr__(self):
        num_children = len(self.children)
        return 'Collection({}, {}, {}, {} child{}, {} items)'.format(self.id, self.name,
                                                                     file_size(self.size),
                                                                     num_children,
                                                                     '' if num_children == 1 else 'ren',
                                                                     len(self.items))


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