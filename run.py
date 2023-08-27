if __name__ == "__main__":
    # do not exec on production environment
    from app.application import app

    app.run()
