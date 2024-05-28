from unittest.mock import patch
from main import app 
import pytest
from photoshare.services.auth import auth_service
from photoshare.repository.users import create_user, get_user_by_email
from photoshare.schemas import UserModel


@pytest.mark.asyncio
async def test_get_user_profile(client, session, test_user_data):
    user_model_data = UserModel(
        username=test_user_data["username"],
        email=test_user_data["email"],
        password=test_user_data["password"]
    )
    user = await create_user(user_model_data, session)
    response = client.get(f"/photoshare/user/{user.username}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["username"] == user.username
    assert data["email"] == user.email
    assert "created_at" in data
    assert "images_count" in data

# @pytest.mark.asyncio
# async def test_update_user(client, session, test_user_data, access_token):
#     token = access_token(client, test_user_data)
#     new_data = {
#         "username": test_user_data["username"],
#         "email": "newemail@example.com",
#         "password": "newpasswo"
#     }
#     token = await token
#     print(token)
#     response = client.put(
#         f"/photoshare/user/{user.username}/settings",
#         json=new_data,
#         headers={"Authorization": f"Bearer {token}"}
#     )
#     assert response.status_code == 200, response.text
#     data = response.json()
#     assert data["email"] == new_data["email"]



# @pytest.mark.asyncio
# async def test_set_user_role(client, session, test_user_data, token):
#     response = client.put(f"/photoshare/user/admin/{test_user_data['id']}/role", json={"role": "moderator"}, headers={"Authorization": f"Bearer {token}"})
#     assert response.status_code == 200, response.text
#     data = response.json()
#     assert data["user"]["role"] == "moderator"


# @pytest.mark.asyncio
# async def test_ban_user(client, session, test_user_data, token):
#     response = client.put(f"/photoshare/user/admin/{test_user_data['id']}/ban", headers={"Authorization": f"Bearer {token}"})
#     assert response.status_code == 200, response.text
#     data = response.json()
#     assert data["user"]["is_active"] == False


# @pytest.mark.asyncio
# async def test_unban_user(client, session, test_user_data, token):
#     response = client.put(f"/photoshare/user/admin/{test_user_data['id']}/unban", headers={"Authorization": f"Bearer {token}"})
#     assert response.status_code == 200, response.text
#     data = response.json()
#     assert data["user"]["is_active"] == True