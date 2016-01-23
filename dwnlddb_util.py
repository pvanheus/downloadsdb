#!/usr/bin/env python

import sys
import os
import hashlib
import os.path
import click
from downloadsdb import db
import model
from sqlalchemy.orm.exc import NoResultFound

def add_item(db, path, collection, name=None, compute_md5=False) -> None:
    size = os.stat(path).st_size
    if compute_md5:
        md5sum = hashlib.md5(open(path,'rb').read()).hexdigest()
    else:
        md5sum = None
    item = model.Item(path=os.path.basename(path), size=size, md5sum=md5sum, collection=collection)
    db.session.add(item)

def add_collection(db, path, parent, name=None, compute_md5=False) -> None:
    if parent is None:
        parent = find_root(db)
    collection = model.Collection(os.path.basename(path), parent=parent)
    for _, subdirs, files in os.walk(path):
        for filename in files:
            add_item(db, filename, collection, compute_md5=compute_md5)
        for subdirname in subdirs:
            add_collection(db, subdirname, collection, compute_md5=compute_md5)

def find_root(db) -> model.Collection:
    try:
        collection = model.Collection.query(path='/').one()
    except NoResultFound as e:
        print("DB error: no top level collection found.", file=sys.stderr)
        raise e
    else:
        return collection

@click.group()
def cli() -> None:
    pass

@cli.command()
@click.option('--collection_name')
@click.option('--compute_md5/--no_compute_md5', default=False)
@click.argument('path', type=click.Path(file_okay=True, dir_okay=True))
def scan(path, collection_name=None, compute_md5=False) -> None:
    if not os.path.exists(path):
        return False
    elif os.path.isfile(path):
        root_collection = find_root(db)
        add_item(db, collection, compute_md5=compute_md5)
    elif os.path.isdir(path):
        add_collection(db, os.path.basename(path), None, compute_md5=compute_md5)
    db.session.commit()

if __name__ == '__main__':
    cli()