"""
東京23区スクレイパー一覧（正式URL版）
各区の区営・区立住宅募集ページの実URLを設定。
"""
from .shinjuku import ShinjukuScraper
from .setagaya import SetagayaScraper
from .generic import GenericWardScraper

WARD_SCRAPERS = {
    "chiyoda":    lambda: GenericWardScraper("chiyoda",    "千代田区", "https://www.city.chiyoda.lg.jp/koho/machizukuri/sumai/koejutaku/boshu/index.html"),
    "chuo":       lambda: GenericWardScraper("chuo",       "中央区",   "https://www.city.chuo.lg.jp/a0042/kurashi/sumai/koutekijuutaku/kuritujutaku.html"),
    "minato":     lambda: GenericWardScraper("minato",     "港区",     "https://www.city.minato.tokyo.jp/jutakukanri/kankyo-machi/sumai/kotekijutaku.html"),
    "shinjuku":   ShinjukuScraper,
    "bunkyo":     lambda: GenericWardScraper("bunkyo",     "文京区",   "https://www.city.bunkyo.lg.jp/b016/p000738.html"),
    "taito":      lambda: GenericWardScraper("taito",      "台東区",   "https://www.city.taito.lg.jp/kenchiku/jutaku/sumai/koukyoujuutaku/index.html"),
    "sumida":     lambda: GenericWardScraper("sumida",     "墨田区",   "https://www.city.sumida.lg.jp/kurashi/zyuutaku/sumai_osagasi/jyutaku_bosyu/index.html"),
    "koto":       lambda: GenericWardScraper("koto",       "江東区",   "https://www.city.koto.lg.jp/kurashi/sumai/moshikomi/kue/index.html"),
    "shinagawa":  lambda: GenericWardScraper("shinagawa",  "品川区",   "https://www.city.shinagawa.tokyo.jp/PC/kankyo/kankyo-kenchiku/kankyo-kenchiku-koutekizyutaku/index.html"),
    "meguro":     lambda: GenericWardScraper("meguro",     "目黒区",   "https://www.city.meguro.tokyo.jp/juutaku/kurashi/sumai/kueijyutaku.html"),
    "ota":        lambda: GenericWardScraper("ota",        "大田区",   "https://www.city.ota.tokyo.jp/seikatsu/sumaimachinami/sumai/kuei/index.html"),
    "setagaya":   SetagayaScraper,
    "shibuya":    lambda: GenericWardScraper("shibuya",    "渋谷区",   "https://www.city.shibuya.tokyo.jp/kurashi/jutaku/jutaku-info/info.html"),
    "nakano":     lambda: GenericWardScraper("nakano",     "中野区",   "https://www.city.tokyo-nakano.lg.jp/machizukuri/jyutaku/kotekichintai/kueijyutaku.html"),
    "suginami":   lambda: GenericWardScraper("suginami",   "杉並区",   "https://www.city.suginami.tokyo.jp/s093/1852.html"),
    "toshima":    lambda: GenericWardScraper("toshima",    "豊島区",   "https://www.city.toshima.lg.jp/machizukuri/sumai/koe/boshu/index.html"),
    "kita":       lambda: GenericWardScraper("kita",       "北区",     "https://www.city.kita.tokyo.jp/jutaku/jutaku/jutaku/kue/index.html"),
    "arakawa":    lambda: GenericWardScraper("arakawa",    "荒川区",   "https://www.city.arakawa.tokyo.jp/kurashi/sumai/index.html"),
    "itabashi":   lambda: GenericWardScraper("itabashi",   "板橋区",   "https://www.city.itabashi.tokyo.jp/tetsuduki/sumai/moushikomi/1002086.html"),
    "nerima":     lambda: GenericWardScraper("nerima",     "練馬区",   "https://www.city.nerima.tokyo.jp/kurashi/sumai/jutakufukushi/boshu/index.html"),
    "adachi":     lambda: GenericWardScraper("adachi",     "足立区",   "https://www.city.adachi.tokyo.jp/juutaku/machi/jutaku/kuejutaku.html"),
    "katsushika": lambda: GenericWardScraper("katsushika", "葛飾区",   "https://www.city.katsushika.lg.jp/kurashi/1003399/1030172/1003425.html"),
    "edogawa":    lambda: GenericWardScraper("edogawa",    "江戸川区", "https://www.city.edogawa.tokyo.jp/kurashi/sumai/kotekijutaku/index.html"),
}

# 新宿区専用スクレイパーのURL更新
ShinjukuScraper.listing_path = "/seikatsu/jutaku01_002117.html"

__all__ = ["WARD_SCRAPERS", "ShinjukuScraper", "SetagayaScraper", "GenericWardScraper"]
