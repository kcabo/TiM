from os.path import join, dirname
from dotenv import load_dotenv

# run flask locally
if __name__ == '__main__':
    # read environment variables from local file
    dotenv_path = join(dirname(__file__), 'safe', '.env')
    load_dotenv(dotenv_path)

    # do not exec on production environment
    from app.application import app
    app.run()
