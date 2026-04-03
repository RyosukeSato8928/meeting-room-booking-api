import datetime
from pydantic import BaseModel, Field

class BookingCreate(BaseModel):
    user_id: int
    room_id: int
    booked_num: int
    start_datetime: datetime.datetime
    end_datetime: datetime.datetime

class Booking(BookingCreate):
    booking_id: int

    class Config:
        orm_mode = True

# ユーザー登録の際に必要な情報を定義するためのクラス（入力値のスキーマ）
class UserCreate(BaseModel):
    user_name: str = Field(max_length=12)

# class Userは、ユーザーデータの構造を定義するためのクラスで、UserCreateを継承している（登録する際のデータとしてのスキーマ）
class User(UserCreate):
    user_id: int
    # orm_mode = Trueは、SQLAlchemyのモデルをPydanticのモデルに変換するための設定
    class Config:
        orm_mode = True

class  RoomCreate(BaseModel):
    room_name: str = Field(max_length=12)
    capacity: int

class  Room(RoomCreate):
    room_id: int

    class Config:
        orm_mode = True