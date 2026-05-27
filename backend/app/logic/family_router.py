from fastapi import APIRouter, HTTPException

from database import db
import random
import string

router = APIRouter(prefix="/family", tags=["family"])


async def code_generator():
    chars = string.ascii_letters + string.digits
    while True:
        code = ''.join(random.choice(chars) for _ in range(10))
        existing = await db.get_family_by_invite_code(code)
        if not existing:
            return code


# Вспомогательная функция: переводит vk_id во внутренний id (и регистрирует при необходимости)
async def get_or_create_user(vk_id: int) -> int:
    user = await db.get_user_by_vk_id(vk_id)
    if user:
        return user['id'] # Возвращаем внутренний ID существующего пользователя
    
    # Если пользователя нет, создаем его и возвращаем его новый внутренний ID
    return await db.create_user(vk_id, f"Пользователь {vk_id}")


# создание семьи
@router.post("/create")
async def create_family(name: str, user_id: int): # user_id здесь = vk_id
    # ограничение на длину имени
    if len(name) > 45:
        return {"error": "name too long"}

    # Получаем внутренний ID (и спасаем от ошибки 500)
    internal_id = await get_or_create_user(user_id)

    invite_code = await code_generator()
    await db.create_family(name, invite_code)
    
    family = await db.get_family_by_code(invite_code)
    family_id = family['id']

    # Передаем внутренний ID в таблицу family_members
    await db.add_member(internal_id, family_id, 'owner')

    return {
        "status": "family created",
        "invite_code": family['invite_code'],
        "family_id": family_id,
        "name": family['name'],
    }


# присоединение к семье по коду
@router.post("/join")
async def join_family(invite_code: str, user_id: int):
    family = await db.get_family_by_invite_code(invite_code)
    if family:
        # Получаем внутренний ID
        internal_id = await get_or_create_user(user_id)

        user = await db.check_membership_by_user_id(internal_id)
        if user and user['family_id'] == family['id']:
            return {
                "status": "ERR: user is already in this family",
            }
        elif user and user['family_id'] != family['id']:
            return {
                "status": "ERR: user is in another family",
            }
        else:
            await db.add_member(internal_id, family['id'], 'child')
            return {
                "status": "member added",
                "family_id": family['id'],
                "invite_code": family['invite_code'],
            }
    else:
        return {
            "status": "ERR: wrong invite code",
        }


# выход из семьи
@router.post("/leave")
async def leave_family(user_id: int):
    internal_id = await get_or_create_user(user_id)
    await db.delete_member(internal_id)
    return {
        "status": "member deleted",
        "user_id": user_id,
    }


# получение данных семьи по коду
@router.get("/get-by-code")
async def get_family_by_code(invite_code: str):
    family = await db.get_family_by_code(invite_code)
    if family:
        return {
            "id": family['id'],
            "name": family['name'],
            "invite_code": family['invite_code']
        }
    raise HTTPException(status_code=404, detail="Family not found")


# поменять роль
@router.post("/change-role")
async def change_role(user_id: int, new_role: str):
    if new_role not in ['owner', 'parent', 'child']:
        return {"status": "ERR: invalid role. Must be 'owner', 'parent', or 'child'"}
    
    internal_id = await get_or_create_user(user_id)
    await db.change_user_role(internal_id, new_role)
    
    return {
        "status": "role changed",
        "user_id": user_id, # В ответе можно оставить vk_id для удобства фронтенда
        "new_role": new_role
    }
