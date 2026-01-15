from fastapi import Header, HTTPException
from typing import Optional
from src.auth.models import User

# Mock DB of users
MOCK_USERS = {
    "alice": User(id="1", username="alice", groups=["admin", "engineering"]),
    "bob": User(id="2", username="bob", groups=["sales"]),
}

async def get_current_user(
    x_user_id: Optional[str] = Header(None),
    authorization: Optional[str] = Header(None)
) -> User:
    """
    Simulates authentication by reading X-User-ID header OR Bearer token.
    In prod, this would validate JWT tokens.
    """
    user_id_to_lookup = x_user_id

    # Try mapping Bearer token if X-User-ID is missing
    if not user_id_to_lookup and authorization:
        if authorization.startswith("Bearer "):
            token = authorization.split(" ")[1]
            if token == "sk-admin":
                user_id_to_lookup = "alice"  # Map admin token to Alice
            else:
                user_id_to_lookup = "bob"    # Map any other token to Bob
    
    if not user_id_to_lookup:
        # Default public/guest user or raise error
        # raising error to enforce auth in this demo
        raise HTTPException(status_code=401, detail="Authentication missing (X-User-ID or Bearer Token)")
        
    user = MOCK_USERS.get(user_id_to_lookup)
    if not user:
        # Fallback if mapped ID doesn't exist (shouldn't happen with hardcoded logic above, but good practice)
        raise HTTPException(status_code=403, detail="User not found")
        
    return user
