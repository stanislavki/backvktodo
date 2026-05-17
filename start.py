import os
import sys
import uvicorn

if __name__ == "__main__":
    # Настраиваем правильные пути к папке backend
    backend_dir = os.path.abspath("backend")
    sys.path.insert(0, backend_dir)
    os.chdir(backend_dir)
    
    # СЕКРЕТНЫЙ ХАК: импортируем само приложение как объект прямо здесь.
    # Чистый Python на 100% увидит main.py благодаря sys.path, 
    # а внутри main.py без проблем подтянется config.py.
    from app import main
    
    # Передаем Увикорну уже готовый объект приложения, а не строку
    uvicorn.run(app, host="0.0.0.0", port=80)
