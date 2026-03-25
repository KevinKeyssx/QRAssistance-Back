from ulid           import ULID
from mongoengine    import Document, StringField, DateTimeField, EnumField
from datetime       import datetime
from enum           import Enum


class QRType( Enum ):
    QUORUM      = "quorum-elders"
    SOCIETY     = "relief-society"
    YOUNG       = "sunday-school-young"
    ADULTS      = "sunday-school-adults"
    MEN         = 'young-men'
    WOMEN       = 'young-women'
    JAS         = 'jas'
    FRIENDS     = 'friends'
    PRIMARY     = 'primary'
    # Specials
    FAMILY_HOME = 'family-home'
    SHOW        = 'show'
    EVENT       = 'event'


class QR( Document ):
    meta = {'collection': 'qrs'}

    id          : str       = StringField( primary_key = True, default = lambda: str( ULID() ))
    type        : QRType    = EnumField( QRType, required = True )
    date        : datetime  = DateTimeField( required = True )
    start_hour  : str       = StringField( required = True )
    end_hour    : str       = StringField( required = True )

    created_at  : datetime  = DateTimeField( default = datetime.utcnow )
    updated_at  : datetime  = DateTimeField( default = datetime.utcnow )
