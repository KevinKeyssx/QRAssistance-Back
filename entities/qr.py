from ulid       import ULID
from pydantic   import Field
from beanie     import Document
from datetime   import datetime
from enum       import Enum


class QRType( str, Enum ):
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
	id          : str       = Field( default_factory = lambda: str( ULID() ), alias = "_id" )
	type        : QRType
	date        : datetime
	start_hour  : str
	end_hour    : str

	created_at  : datetime  = Field( default_factory = datetime.utcnow )
	updated_at  : datetime  = Field( default_factory = datetime.utcnow )

	class Settings:
		name = "qrs"
