from fastapi import APIRouter
from database import db 

router = APIRouter(prefix="/task", tags=["task"])

# Умная функция перевода vk_id во внутренний ID
async def get_internal_id(vk_id: int):
    user = await db.get_user_by_vk_id(vk_id)
    return user['id'] if user else None

# Создание задачи
@router.post("/add_task")
async def add_task(from_id: int, to_id: int, title: str, description: str = ""):
    # Фронт присылает vk_id (from_id и to_id), переводим их во внутренние ID
    internal_from = await get_internal_id(from_id)
    if not internal_from:
        return {"status": "ERR: user not found"}

    from_user = await db.check_membership_by_user_id(internal_from)
    if not from_user:
        return {"status": "ERR: user not in family"}

    family_id = from_user['family_id']

    if len(title) > 255:
        return {"status": "ERR: title too long"}
    if len(description) > 255:
        return {"status": "ERR: description too long"}

    # create_task использует внутренние ID для базы
    new_task_id = await db.create_task(family_id, internal_from, title, description)

    # Назначаем исполнителя
    if to_id and to_id != 0:
        internal_to = await get_internal_id(to_id)
        if internal_to:
            await db.assign_task(new_task_id, internal_to)

    return {
        "status": "task_assigned",
        "task_id": new_task_id
    }

# Удаление задачи
@router.post("/delete_task")
async def delete_task(task_id: int):
    await db.delete_task(task_id)
    return {"status": "task_deleted", "task_id": task_id}

# Получение задач
@router.get("/get_family_tasks")
async def get_family_tasks(user_id: int): # Сюда прилетает vk_id с фронтенда!
    # Перехватываем vk_id и достаем реальный внутренний ID
    internal_id = await get_internal_id(user_id)
    if not internal_id:
        return {"status": "ERR: user not in family"}

    user = await db.check_membership_by_user_id(internal_id)
    if not user:
        return {"status": "ERR: user not in family"}

    family_id = user['family_id']
    
    tasks = await db.get_family_tasks(family_id)
    members = await db.get_family_members(family_id)
    
    # Словари для перевода ID:
    # name_map -> для красивых имен
    # vk_map -> для возврата vk_id обратно на фронтенд
    name_map = {m['user_id']: m['name'] for m in members}
    vk_map = {m['user_id']: m['vk_id'] for m in members}

    enriched_tasks = []
    for t in tasks:
        enriched_tasks.append({
            "task_id": t['id'],
            "title": t['title'],
            "description": t['description'],
            "status": t['status'],
            "creator_name": name_map.get(t['creator_id'], 'Неизвестный'),
            "assignee_name": name_map.get(t['assigned_to'], 'Не назначено') if t['assigned_to'] else 'Не назначено',
            # Возвращаем vk_id исполнителя, чтобы вкладка "Мои задачи" работала чётко
            "assigned_to_id": vk_map.get(t['assigned_to']) if t['assigned_to'] else None
        })

    return {"tasks": enriched_tasks}
