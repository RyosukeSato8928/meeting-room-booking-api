import streamlit as st
import datetime
import requests
import json
import pandas as pd

from sql_app import constants

page = st.sidebar.selectbox('画面を選択してください', [constants.ADD_USER, constants.ADD_ROOM, constants.ADD_BOOKING])

if page == constants.ADD_USER:
    st.title("ユーザー登録画面")
    with st.form(key="user"):
        username: str = st.text_input('ユーザー名', max_chars=12)
        data = {
            'user_name': username
        }

        submit_button = st.form_submit_button(label="ユーザー登録")

    if submit_button:
        url = 'http://127.0.0.1:8000/users'
        res = requests.post(
            url,
            data=json.dumps(data)
        )
        if res.status_code == 200:
            st.success('ユーザー登録完了')

elif page == constants.ADD_ROOM:
    st.title("会議室登録画面")

    with st.form(key="room"):
        room_name: str = st.text_input('会議室名', max_chars=12)
        capacity: int = st.number_input('定員', step=1)
        data = {
            'room_name': room_name,
            'capacity': capacity
        }

        submit_button = st.form_submit_button(label="会議室登録")

    if submit_button:
        url = 'http://127.0.0.1:8000/rooms'
        res = requests.post(
            url,
            data=json.dumps(data)
        )
        if res.status_code == 200:
            st.success('会議室登録完了')

elif page == constants.ADD_BOOKING:
    st.title("会議室予約画面")

    # ユーザー一覧取得
    url_users = 'http://127.0.0.1:8000/users'
    res = requests.get(url_users)
    users = res.json()
    users_name = {}
    # リストで取得したユーザー一覧から、ユーザー名をKey、ユーザーIDをValueとした辞書を作成
    for user in users:
        users_name[user['user_name']] = user['user_id']

    # 会議室一覧取得
    url_rooms = 'http://127.0.0.1:8000/rooms'
    res = requests.get(url_rooms)
    rooms = res.json()
    rooms_name = {}
    # リストで取得した会議室一覧から、会議室名をKey、会議室IDと定員をValueとした辞書を作成
    for room in rooms:
        rooms_name[room['room_name']] = {
            'room_id': room['room_id'],
            'capacity': room['capacity']
        }

    st.write('### 会議室一覧')
    # 会議室一覧が表に変換される
    df_rooms = pd.DataFrame(rooms)
    # カラム名を変換する
    df_rooms.columns = ['会議室名', '定員', '会議室ID']
    st.write(df_rooms)

    url_bookings = 'http://127.0.0.1:8000/bookings'
    res = requests.get(url_bookings)
    bookings = res.json()
    df_bookings = pd.DataFrame(bookings)

    # ユーザーIDをKeyに、ユーザー名を取得する
    users_id = {}
    for user in users:
        users_id[user['user_id']] = user['user_name']

    # 会議室IDをKeyに、会議室名と定員を取得する
    rooms_id = {}
    for room in rooms:
        rooms_id[room['room_id']] = {
            'room_name': room['room_name'],
            'capacity': room['capacity']
        }

    # 予約一覧のカラム名を変換する(xにはデータが入る)
    to_username = lambda x: users_id[x] # ユーザーIDをKeyに、ユーザー名を取得する関数
    to_roomname = lambda x: rooms_id[x]['room_name'] # 会議室IDをKeyに、会議室名を取得する関数
    to_datetime = lambda x: datetime.datetime.fromisoformat(x).strftime('%Y/%m/%d %H:%M') # 予約日時を見やすい形式に変換する関数

    # mapメソッドで各要素に関数を適用させ、データを上書きする（1→'かんた'のように）
    df_bookings['user_id'] = df_bookings['user_id'].map(to_username)
    df_bookings['room_id'] = df_bookings['room_id'].map(to_roomname)
    df_bookings['start_datetime'] = df_bookings['start_datetime'].map(to_datetime)
    df_bookings['end_datetime'] = df_bookings['end_datetime'].map(to_datetime)

    df_bookings = df_bookings.rename(columns={
        'user_id': '予約者名',
        'room_id': '会議室名',
        'booked_num': '予約人数',
        'start_datetime': '開始日時',
        'end_datetime': '終了日時',
        'booking_id': '予約番号'
    })

    st.write('### 予約一覧')
    st.table(df_bookings)

    with st.form(key="booking"):
        username: str = st.selectbox('予約者名', users_name.keys())
        roomname: str = st.selectbox('会議室名', rooms_name.keys())
        booked_num: str = st.number_input('予約人数', step=1, min_value=1)
        date = st.date_input('日付を入力', min_value=datetime.date.today())
        start_time = st.time_input('開始時刻', value=datetime.time(hour=9, minute=0))
        end_time = st.time_input('終了時刻', value=datetime.time(hour=20, minute=0))

        submit_button = st.form_submit_button(label="予約登録")

    if submit_button:
        # users_nameのKeyを指定してユーザーIDと会議室IDを取得する
        user_id: int = users_name[username]
        # rooms_nameの中のKeyを指定して会議室IDと定員を取得する（辞書in辞書になっているときはさらに指定する）
        room_id: int = rooms_name[roomname]['room_id']
        capacity: int = rooms_name[roomname]['capacity']

        data = {
            'user_id': user_id,
            'room_id': room_id,
            'booked_num': booked_num,
            'start_datetime': datetime.datetime(
                year=date.year,
                month=date.month,
                day=date.day,
                hour=start_time.hour,
                minute=start_time.minute
            ).isoformat(),
            'end_datetime': datetime.datetime(
                year=date.year,
                month=date.month,
                day=date.day,
                hour=end_time.hour,
                minute=end_time.minute
            ).isoformat()
        }

        # 定員より多い予約人数の場合
        if booked_num > capacity:
            st.error(f'{roomname}の定員は{capacity}人です。予約人数を確認してください。')
        # 開始日時が終了日時より前でない場合
        elif start_time>= end_time:
            st.error('開始日時は終了日時より前にしてください。')
        elif start_time < datetime.time(hour=9, minute=0, second=0) or end_time > datetime.time(hour=20, minute=0, second=0):
            st.error('予約可能時間は9:00~20:00です。予約日時を確認してください。')
        else:
            # 会議室予約
            url = 'http://127.0.0.1:8000/bookings'
            res = requests.post(
                url,
                data=json.dumps(data)
            )
            if res.status_code == 200:
                st.success('予約完了しました')
            elif res.status_code == 404:
                st.error('予約が重複しています。予約日時を確認してください。')