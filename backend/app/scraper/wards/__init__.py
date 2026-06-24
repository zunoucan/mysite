"""
東京23区スクレイパー一覧
各区の区立住宅情報ページ構造に合わせたスクレイパーを実装。
"""
from .shinjuku import ShinjukuScraper
from .setagaya import SetagayaScraper
from .generic import GenericWardScraper

# 全23区のスクレイパーマッピング
# 専用スクレイパーがない区はGenericWardScraperにURLと区コードを渡す
WARD_SCRAPERS = {
    "chiyoda":    lambda: GenericWardScraper("chiyoda",  "千代田区", "https://www.city.chiyoda.lg.jp/koho/machizukuri/sumai/kokyojutaku/index.html"),
    "chuo":       lambda: GenericWardScraper("chuo",     "中央区",   "https://www.city.chuo.lg.jp/a_seikatsu/sumu/kueijigyodan/index.html"),
    "minato":     lambda: GenericWardScraper("minato",   "港区",     "https://www.city.minato.tokyo.jp/jutaku/index.html"),
    "shinjuku":   ShinjukuScraper,
    "bunkyo":     lambda: GenericWardScraper("bunkyo",   "文京区",   "https://www.city.bunkyo.lg.jp/bosai/sumai/jutaku/kuei住宅.html"),
    "taito":      lambda: GenericWardScraper("taito",    "台東区",   "https://www.city.taito.lg.jp/jutaku/index.html"),
    "sumida":     lambda: GenericWardScraper("sumida",   "墨田区",   "https://www.city.sumida.lg.jp/seikatsu_guide/sumai/jutaku/index.html"),
    "koto":       lambda: GenericWardScraper("koto",     "江東区",   "https://www.city.koto.lg.jp/390202/index.html"),
    "shinagawa":  lambda: GenericWardScraper("shinagawa","品川区",   "https://www.city.shinagawa.tokyo.jp/PC/seikatsu/seikatsu-jyutaku/index.html"),
    "meguro":     lambda: GenericWardScraper("meguro",   "目黒区",   "https://www.city.meguro.tokyo.jp/kurashi/sumai/jutaku/kueijutaku/index.html"),
    "ota":        lambda: GenericWardScraper("ota",      "大田区",   "https://www.city.ota.tokyo.jp/seikatsu/sumai/housing/index.html"),
    "setagaya":   SetagayaScraper,
    "shibuya":    lambda: GenericWardScraper("shibuya",  "渋谷区",   "https://www.city.shibuya.tokyo.jp/kurashi/sumai/jutaku/index.html"),
    "nakano":     lambda: GenericWardScraper("nakano",   "中野区",   "https://www.city.tokyo-nakano.lg.jp/dept/211000/d027246.html"),
    "suginami":   lambda: GenericWardScraper("suginami", "杉並区",   "https://www.city.suginami.tokyo.jp/guide/sumai/jutaku/index.html"),
    "toshima":    lambda: GenericWardScraper("toshima",  "豊島区",   "https://www.city.toshima.lg.jp/245/1002975.html"),
    "kita":       lambda: GenericWardScraper("kita",     "北区",     "https://www.city.kita.tokyo.jp/machi/sumai/kuei/index.html"),
    "arakawa":    lambda: GenericWardScraper("arakawa",  "荒川区",   "https://www.city.arakawa.tokyo.jp/a/sumai/jutaku/index.html"),
    "itabashi":   lambda: GenericWardScraper("itabashi", "板橋区",   "https://www.city.itabashi.tokyo.jp/kenko/sumai/jutaku/1000613.html"),
    "nerima":     lambda: GenericWardScraper("nerima",   "練馬区",   "https://www.city.nerima.tokyo.jp/kurashi/sumai/koeijutaku/index.html"),
    "adachi":     lambda: GenericWardScraper("adachi",   "足立区",   "https://www.city.adachi.tokyo.jp/jutaku/index.html"),
    "katsushika": lambda: GenericWardScraper("katsushika","葛飾区",  "https://www.city.katsushika.lg.jp/kurashi/1000070/1002743/index.html"),
    "edogawa":    lambda: GenericWardScraper("edogawa",  "江戸川区", "https://www.city.edogawa.tokyo.jp/e005/kurashi/sumai/housing/index.html"),
}

__all__ = ["WARD_SCRAPERS", "ShinjukuScraper", "SetagayaScraper", "GenericWardScraper"]
