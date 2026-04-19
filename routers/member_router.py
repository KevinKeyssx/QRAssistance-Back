# Python
from typing import List, Optional

# Services
import services.member_service as member_services

# Model
from entities.member import Member

# FastApi
from fastapi import Body, status, APIRouter, Path, HTTPException, Depends, Query

# DTOs
from dtos.member_dto import MemberCreateDTO, MemberReadDTO, MemberUpdateDTO, PaginatedMemberResponse
from dtos.paginated_dto import Pagination

# Services
import services.assistance_service as assistance_services

# Utils
from utils.consts import ErrorCode

# Variables
member_router   = APIRouter()
version         = "/api/v1/"
collection      = "members"
endpoint        = version + collection + "/"
tags            = "Member Services"

# CREATE
@member_router.post(
    path            = endpoint,
    response_model  = MemberReadDTO,
    status_code     = status.HTTP_201_CREATED,
    tags            = [ tags ]
)
async def register_member(
    member_in: MemberCreateDTO
) -> MemberReadDTO:
    is_duplicate = await member_services.check_duplicate_member(
        name        = member_in.name,
        last_name   = member_in.last_name,
        classes     = member_in.classes
    )

    if ( is_duplicate ):
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail      = "Miembro ya existe registrado."
        )

    new_member = Member( **member_in.model_dump() )
    await new_member.insert()

    # Si viene qr_session_id, intentamos registrar la asistencia
    if member_in.qr_session_id:
        try:
            await assistance_services.process_assistance_registration( 
                member        = new_member, 
                qr_session_id = member_in.qr_session_id 
            )
        except HTTPException:
            # Si falla la asistencia, devolvemos un error 206 con los datos del miembro (el miembro NO se borra)
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail      = {
                    "code"    : ErrorCode.ERR_206,
                    "message" : "El miembro se pudo registrar pero no su asistencia.",
                    "data"    : MemberReadDTO.from_attributes( new_member ).model_dump()
                }
            )

    return new_member

# READ ALL
@member_router.get(
    path            = endpoint,
    response_model  = PaginatedMemberResponse,
    status_code     = status.HTTP_200_OK,
    tags            = [tags]
)
async def get_members(
    pagination: Pagination = Depends(),
) -> PaginatedMemberResponse:
    members = await member_services.get_all_members( pagination )

    return PaginatedMemberResponse(
        items   = members,
        total   = len( members ),
        page    = pagination.page,
        size    = pagination.size,
        pages   = ( len( members ) + pagination.size - 1 ) // pagination.size
    )

# READ ONE
# @member_router.get(
#     path            = f"{endpoint}{{member_id}}",
#     response_model  = MemberReadDTO,
#     tags            = [tags]
# )
# async def get_member(
#     member_id: str = Path( ... )
# ) -> MemberReadDTO:
#     member = await member_services.get_member_by_id( member_id )

#     if not member:
#         raise HTTPException(
#             status_code = status.HTTP_404_NOT_FOUND,
#             detail      = "Miembro no encontrado"
#         )

#     return member

# SEARCH BY NAME
@member_router.get(
	path			= f"{endpoint}search",
	response_model	= PaginatedMemberResponse,
	status_code		= status.HTTP_200_OK,
	tags			= [ tags ]
)
async def search_members(
	query_text	: Optional[ str ] = Query( None ),
	pagination	: Pagination = Depends()
) -> PaginatedMemberResponse:
	members, total = await member_services.get_members_by_name( query_text, pagination )

	return PaginatedMemberResponse(
		items	= members,
		total	= total,
		page	= pagination.page,
		size	= pagination.size,
		pages	= ( total + pagination.size - 1 ) // pagination.size if pagination.size > 0 else 0
	)

# UPDATE
@member_router.put(
    path            = f"{endpoint}{{member_id}}",
    response_model  = MemberReadDTO,
    tags            = [tags]
)
async def update_member(
    member_id   : str = Path(...),
    member_data : MemberUpdateDTO = Body(...)
):
    updated = await member_services.update_member( member_id, member_data )

    if not updated:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "Miembro no encontrado"
        )

    return updated

# DELETE
@member_router.delete(
    path            = f"{endpoint}{{member_id}}",
    status_code     = status.HTTP_204_NO_CONTENT,
    tags            = [tags]
)
async def delete_member(
    member_id: str = Path( ... )
):
    success = await member_services.delete_member( member_id )

    if not success:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "Miembro no encontrado"
        )

    return None
