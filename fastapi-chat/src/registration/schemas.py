from fastapi import File, Form, UploadFile
from pydantic import EmailStr


class UserRegisterSchema:
    def __init__(
        self,
        email: EmailStr = Form(...),
        username: str = Form(max_length=150),
        password: str = Form(min_length=6, max_length=72),
        first_name: str = Form(max_length=150),
        last_name: str = Form(max_length=150),
        uploaded_image: UploadFile = File(None, media_type="image/jpeg"),
    ):
        self.email = email
        self.username = username
        # Truncate password to 72 bytes for bcrypt compatibility
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
            while len(password_bytes) > 0:
                try:
                    password = password_bytes.decode('utf-8')
                    break
                except UnicodeDecodeError:
                    password_bytes = password_bytes[:-1]
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.uploaded_image = uploaded_image
