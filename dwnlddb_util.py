#!/usr/bin/env python

import sys
import os
import hashlib
import os.path
from operator import attrgetter
import click
from downloadsdb import db
import model
from sqlalchemy.orm.exc import NoResultFound
import asciitree

def add_item(db, path, collection, name=None, compute_md5=False) -> None:
    size = os.stat(path).st_size
    if compute_md5:
        md5sum = hashlib.md5(open(path,'rb').read()).hexdigest()
    else:
        md5sum = None
    item = model.Item(path=os.path.basename(path), size=size, md5sum=md5sum, collection=collection)
    db.session.add(item)

def add_collection(db, path, name=None, compute_md5=False) -> None:
    collection_by_path = { path: model.Collection(path='/', parent=None)}
    for dirname, subdirs, files in os.walk(path):
        if 'Coursera' in dirname or '/.' in dirname:
            continue
        collection = collection_by_path.get(dirname, model.Collection(path=os.path.basename(dirname)))
        for filename in files:
            if filename.startswith('.'):
                continue
            add_item(db, os.path.join(dirname, filename), collection, compute_md5=compute_md5)
        for subdirname in subdirs:
            if subdirname.startswith('.'):
                continue
            child_collection = model.Collection(path=subdirname)
            collection.children.append(child_collection)
            collection_by_path[os.path.join(dirname, subdirname)] = child_collection

def find_root(db) -> model.Collection:
    try:
        collection = model.Collection.query.filter_by(path='/').one()
    except NoResultFound as e:
        return None
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
        add_item(db, root_collection, compute_md5=compute_md5)
    elif os.path.isdir(path):
        add_collection(db, path, compute_md5=compute_md5)
    db.session.commit()

@cli.command()
def initdb():
    db.drop_all()
    db.session.commit()
    db.create_all()
    print("created DB at {}.".format(db.app.config['SQLALCHEMY_DATABASE_URI']))

@cli.command()
def drawtree():
    root = find_root(db)
    if root is  None:
        print("No root for the tree, cannot draw it.")
    else:
        tree = asciitree.draw_tree(root)
        print(tree)

if __name__ == '__main__':
    cli()