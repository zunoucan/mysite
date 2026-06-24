"""23区のマスターデータ初期投入"""
from sqlmodel import Session, select
from .db import engine
from .models import Ward

WARDS = [
    ("chiyoda",    "千代田区", "https://www.city.chiyoda.lg.jp"),
    ("chuo",       "中央区",   "https://www.city.chuo.lg.jp"),
    ("minato",     "港区",     "https://www.city.minato.tokyo.jp"),
    ("shinjuku",   "新宿区",   "https://www.city.shinjuku.lg.jp"),
    ("bunkyo",     "文京区",   "https://www.city.bunkyo.lg.jp"),
    ("taito",      "台東区",   "https://www.city.taito.lg.jp"),
    ("sumida",     "墨田区",   "https://www.city.sumida.lg.jp"),
    ("koto",       "江東区",   "https://www.city.koto.lg.jp"),
    ("shinagawa",  "品川区",   "https://www.city.shinagawa.tokyo.jp"),
    ("meguro",     "目黒区",   "https://www.city.meguro.tokyo.jp"),
    ("ota",        "大田区",   "https://www.city.ota.tokyo.jp"),
    ("setagaya",   "世田谷区", "https://www.city.setagaya.lg.jp"),
    ("shibuya",    "渋谷区",   "https://www.city.shibuya.tokyo.jp"),
    ("nakano",     "中野区",   "https://www.city.tokyo-nakano.lg.jp"),
    ("suginami",   "杉並区",   "https://www.city.suginami.tokyo.jp"),
    ("toshima",    "豊島区",   "https://www.city.toshima.lg.jp"),
    ("kita",       "北区",     "https://www.city.kita.tokyo.jp"),
    ("arakawa",    "荒川区",   "https://www.city.arakawa.tokyo.jp"),
    ("itabashi",   "板橋区",   "https://www.city.itabashi.tokyo.jp"),
    ("nerima",     "練馬区",   "https://www.city.nerima.tokyo.jp"),
    ("adachi",     "足立区",   "https://www.city.adachi.tokyo.jp"),
    ("katsushika", "葛飾区",   "https://www.city.katsushika.lg.jp"),
    ("edogawa",    "江戸川区", "https://www.city.edogawa.tokyo.jp"),
]


def seed_wards():
    with Session(engine) as session:
        for code, name_ja, url in WARDS:
            existing = session.exec(select(Ward).where(Ward.code == code)).first()
            if not existing:
                session.add(Ward(code=code, name_ja=name_ja, website_url=url))
        session.commit()
