import os
import sys
import uvicorn

if __name__ == "__main__":
    # Получаем абсолютный путь к папке backend
    backend_dir = os.path.abspath("backend")
    
    # СЕКРЕТНЫЙ ИНГРЕДИЕНТ: принудительно добавляем backend в пути поиска модулей Python
    sys.path.insert(0, backend_dir)
    
    # Меняем рабочую директорию
    os.chdir(backend_dir)
    
    # Теперь Python на 100% увидит и main.py, и config.py, и всё остальное
    uvicorn.run("main:app", host="0.0.0.0", port=80)
