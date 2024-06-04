import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.api:app", host="192.168.86.157.", port=8000, reload=True)