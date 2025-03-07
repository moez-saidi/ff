from app.worker.celery import app


@app.task
def post_registration():
    print("User created successfully")
