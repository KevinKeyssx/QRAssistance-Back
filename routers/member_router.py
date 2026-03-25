# Python
from typing import List

# Services
import services.member_service as member_services

# Model
from entities.member import Member

# FastApi
from fastapi import Body, status, APIRouter, Path, HTTPException

# DTOs
from dtos.member_dto import MemberCreateDTO, MemberReadDTO, MemberUpdateDTO

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
    tags            = [tags]
)
async def register_member(member_in: MemberCreateDTO):
    # Convertimos DTO a Entity
    new_member = Member(**member_in.model_dump())
    # Guardamos en la DB
    return await new_member.insert()

# READ ALL
@member_router.get(
    path            = endpoint,
    response_model  = List[MemberReadDTO],
    status_code     = status.HTTP_200_OK,
    tags            = [tags]
)
async def get_members():
    return await member_services.get_all_members()

# READ ONE
@member_router.get(
    path            = f"{endpoint}{{member_id}}",
    response_model  = MemberReadDTO,
    tags            = [tags]
)
async def get_member(member_id: str = Path(...)):
    member = await member_services.get_member_by_id(member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Miembro no encontrado")
    return member

# UPDATE
@member_router.put(
    path            = f"{endpoint}{{member_id}}",
    response_model  = MemberReadDTO,
    tags            = [tags]
)
async def update_member(member_id: str, member_data: MemberUpdateDTO):
    updated = await member_services.update_member(member_id, member_data)
    if not updated:
        raise HTTPException(status_code=404, detail="No se pudo actualizar el miembro")
    return updated

# DELETE
@member_router.delete(
    path            = f"{endpoint}{{member_id}}",
    status_code     = status.HTTP_204_NO_CONTENT,
    tags            = [tags]
)
async def delete_member(member_id: str):
    success = await member_services.delete_member(member_id)
    if not success:
        raise HTTPException(status_code=404, detail="Miembro no encontrado")
    return None