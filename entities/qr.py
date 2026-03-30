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
	session_id  : str       = Field( default_factory = lambda: str( ULID() ), min_length = 26, max_length = 26 )
	type        : QRType    = Field( ... )
	date        : datetime  = Field( ... )
	start_hour  : str       = Field( ..., min_length = 5, max_length = 5 )
	end_hour    : str       = Field( ..., min_length = 5, max_length = 5 )

	created_at  : datetime  = Field( default_factory = datetime.utcnow )
	updated_at  : datetime  = Field( default_factory = datetime.utcnow )

	class Settings:
		name = "qrs"
