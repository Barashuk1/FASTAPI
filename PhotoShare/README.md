# PhotoShare API

PhotoShare API is a web service built with FastAPI for managing image uploads, tagging, user profiles, and more.

## Features

- **User Authentication:** Secure user registration and login using JWT (JSON Web Tokens).
- **Image Uploading and Management:** Users can upload images from their local devices, add descriptions, and associate tags with their images.
- **Image Rating:** Users can rate images with likes and dislikes, and the platform displays the rating of each image.
- **Commenting System:** Users can add comments to images, fostering engagement and discussion around shared content.
- **Image Searching:** Users can search for images based on descriptions, tags, or usernames.
- **User Profiles:** Users have profiles that display their uploaded images and relevant information.
- **Admin Panel:** Administrative users have access to features for managing users, roles, and banning users if necessary.
- **Image Transformations:** Users can apply transformations to their images, such as cropping, resizing, and applying filters.
- **QR Code Generation:** Users can generate QR codes for their images, allowing for easy sharing and access.

## Installation

1. Clone the repository:

```bash
git clone https://github.com/Barashuk1/FASTAPI.git
cd photoshare
```

2. Create a virtual environment (recommended) and activate it:

```bash
pip install poetry
poetry shell
```

3. Install dependencies using Poetry:

```bash
poetry install --no-root
```

4. Set up the database:

```bash
alembic upgrade head
```

5. Run the application:

```bash
docker compose up
python3 main.py
```
or
```bash
docker compose up
uvicorn main:app --reload
```

## API Endpoints

### Authentication

- **Signup**
    ```http
    POST /photoshare/auth/signup
    ```
    **Request Body**:
    - `username`: String
    - `email`: String
    - `password`: String

- **Login**
    ```http
    POST /photoshare/auth/login
    ```
    **Request Body**:
    - `username`: String (email in this case)
    - `password`: String

- **Refresh Token**
    ```http
    GET /photoshare/auth/refresh_token
    ```
    **Headers**:
    - `Authorization`: Bearer <refresh_token>

### Images

- **Add Image from PC**
    ```http
    POST /photoshare/images/add_from_pc
    ```
    **Request Body**:
    - `description`: String
    - `file`: UploadFile
    - `tags`: Optional string (comma-separated)
    **Headers**:
    - `Authorization`: Bearer <access_token>

- **Get Image by URL**
    ```http
    GET /photoshare/images/url/{url_view}
    ```

- **Rate Images**
    ```http
    GET /photoshare/images/rate
    ```
    **Query Parameters**:
    - `order`: asc or desc

- **Delete Image**
    ```http
    DELETE /photoshare/images/{image_id}
    ```
    **Headers**:
    - `Authorization`: Bearer <access_token>

- **Update Image**
    ```http
    PUT /photoshare/images/{image_id}
    ```
    **Request Body**:
    - `description`: String

    **Headers**:
    - `Authorization`: Bearer <access_token>

- **Get Image by ID**
    ```http
    GET /photoshare/images/{image_id}
    ```

- **Transform Image**
    ```http
    POST /photoshare/images/{image_id}
    ```
    **Request Body**:
    - `choice`: Integer (1, 2, or 3)

    **Headers**:
    - `Authorization`: Bearer <access_token>

- **Search Images by Description**
    ```http
    GET /photoshare/images/search/{description}
    ```

- **Search Images by Tags**
    ```http
    GET /photoshare/images/search/tags/{tags}
    ```
    **Path Parameters**:
    - `tags`: Comma-separated string of tags

- **Search Images by User**
    ```http
    GET /photoshare/images/search/user/{username}
    ```

### Comments

- **Add Comment**
    ```http
    POST /photoshare/images/{image_id}/add_comment/
    ```
    **Request Body**:
    - `text`: String

    **Headers**:
    - `Authorization`: Bearer <access_token>

- **Get Comments for Image**
    ```http
    GET /photoshare/images/{image_id}/comments/
    ```

- **Edit Comment**
    ```http
    PUT /photoshare/images/{image_id}/comments/{comment_id}/
    ```
    **Request Body**:
    - `text`: String

    **Headers**:
    - `Authorization`: Bearer <access_token>

- **Delete Comment**
    ```http
    DELETE /photoshare/images/{image_id}/comments/{comment_id}/
    ```
    **Headers**:
    - `Authorization`: Bearer <access_token>

### Tags

- **Get All Tags**
    ```http
    GET /photoshare/tags/
    ```

- **Get Tag by ID**
    ```http
    GET /photoshare/tags/{tag_id}
    ```

- **Create Tag**
    ```http
    POST /photoshare/tags/
    ```
    **Request Body**:
    - `name`: String

- **Update Tag**
    ```http
    PUT /photoshare/tags/{tag_id}
    ```
    **Request Body**:
    - `name`: String

- **Delete Tag**
    ```http
    DELETE /photoshare/tags/{tag_id}
    ```

### Users

- **Get User Profile**
    ```http
    GET /photoshare/user/{username}
    ```

- **Update User Settings**
    ```http
    PUT /photoshare/user/{username}/settings
    ```
    **Request Body**:
    - `username`: Optional string
    - `email`: Optional string
    - `password`: Optional string

    **Headers**:
    - `Authorization`: Bearer <access_token>

- **Set User Role (Admin Only)**
    ```http
    PUT /photoshare/user/admin/{user_id}/role
    ```
    **Request Body**:
    - `role`: String ("user" or "moderator")

    **Headers**:
    - `Authorization`: Bearer <access_token>

- **Ban User (Admin Only)**
    ```http
    PUT /photoshare/user/admin/{user_id}/ban
    ```
    **Headers**:
    - `Authorization`: Bearer <access_token>

- **Unban User (Admin Only)**
    ```http
    PUT /photoshare/user/admin/{user_id}/unban
    ```
    **Headers**:
    - `Authorization`: Bearer <access_token>
