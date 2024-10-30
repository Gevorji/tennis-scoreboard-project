def load_test_env():
    from dotenv import dotenv_values
    import os
    import os.path
    dotenv_path = os.path.abspath(os.path.join(__file__, r'..\..\.env'))
    os.environ.update(dotenv_values(dotenv_path))
