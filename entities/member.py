from ulid           import ULID
from mongoengine    import Document, StringField, DateTimeField, ListField, BooleanField
from datetime       import datetime
from typing         import List


class Member( Document ):
    meta = {'collection': 'members'}

    id          : str       = StringField( primary_key = True, default = lambda: str( ULID() ))
    name        : str       = StringField( required = True )
    last_name   : str       = StringField( required = True )
    classes     : List[str] = ListField( StringField(), required = True )
    ulid        : str       = StringField( required = True )
    saveFinger  : bool      = BooleanField( default = False )

    created_at  : datetime  = DateTimeField( default = datetime.utcnow )
    updated_at  : datetime  = DateTimeField( default = datetime.utcnow )
