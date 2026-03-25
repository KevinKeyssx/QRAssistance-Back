from ulid           import ULID
from mongoengine    import Document, StringField, DateTimeField, ListField, BooleanField
from datetime       import datetime
from typing         import List


class Assistance( Document ):
    meta = {'collection': 'assistances'}

    id          : str   = StringField( primary_key = True, default = lambda: str( ULID() ))
    member_id   : str   = StringField( required = True )
    qr_id       : str   = StringField( required = True )

    created_at  : datetime  = DateTimeField( default = datetime.utcnow )
    updated_at  : datetime  = DateTimeField( default = datetime.utcnow )
