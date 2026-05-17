import uvicorn

if __name__ == "__main__":
    # Запускаем uvicorn программно, указывая правильный путь к приложению
    uvicorn.run("backend.main:app", host="0.0.0.0", port=80)