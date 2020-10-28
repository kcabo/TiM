
if __name__ == '__main__':
    # read environment variable
    from os.path import join, dirname
    from dotenv import load_dotenv
    dotenv_path = join(dirname(__file__), 'safe', '.env')
    load_dotenv(dotenv_path)

    # run flask locally
    # WARNING: do not exec in a product environment
    from app.application import app
    app.run()
