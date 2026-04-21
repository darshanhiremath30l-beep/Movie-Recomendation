def authenticate_user(email, password):
    """
    Placeholder service for checking passwords and producing a JWT token.
    Return None if invalid, or a dict containing token and user if valid.
    """
    if email and password:
        return {"token": "fake-jwt-token-from-service", "user_id": "u123"}
    return None

def register_user(name, email, password):
    """
    Placeholder service to insert a new user to DB.
    """
    # password_hash = hash(password)
    # db.session.add(User(name=name, email=email...))
    return True
