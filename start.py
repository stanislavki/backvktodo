import os
import uvicorn

if __name__ == "__main__":
    # Переходим прямо в папку backend, чтобы Python видел config, database и т.д.
    os.chdir("backend")
    
    # Теперь запускаем main:app напрямую, так как мы уже находимся внутри папки
    uvicorn.run("main:app", host="0.0.0.0", port=80)
