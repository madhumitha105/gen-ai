session_store = {}

def get_session(session_id: str):
    """
    Returns the message list for a session.
    Creates a new one if it doesn't exist.
    """
    if session_id not in session_store:
        session_store[session_id] = []
    return session_store[session_id]