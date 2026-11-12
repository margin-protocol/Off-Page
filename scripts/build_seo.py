#!/usr/bin/env python3
"""岔頁的 SEO／AEO 產生器。

index.html 是唯一的原稿（首頁＋所有資料）。這支腳本會：
  1. 更新 index.html 裡自動產生的區塊（結構化資料、常見問題、小咒語清單、noscript）
  2. 從 index.html 複製出各分頁：worlds.html、spells.html、tools.html、order.html、about.html
  3. 每則公開的小咒語產生一頁：spells/<id>.html
  4. 產生 sitemap.xml 和 llms.txt

新增或修改咒語、作品、常見問題之後，在 repo 根目錄執行：
    python3 scripts/build_seo.py
（推到 GitHub 後，GitHub Actions 也會自動幫你跑。）
"""
import json, re, html, datetime, pathlib, shutil

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = "https://xia-mumu.github.io/Off-Page/"
TODAY = datetime.date.today().isoformat()
esc = lambda s: html.escape(str(s), quote=True)
jsesc = lambda s: esc(s).replace("&#x27;", "&#39;")   # 跟網頁裡 JS 的 esc() 輸出一致

src = (ROOT / "index.html").read_text(encoding="utf-8")

def data(i):
    m = re.search(r'<script type="application/json" id="data-%s">(.*?)</script>' % i, src, re.S)
    return json.loads(m.group(1))

worlds = data("worlds")
spells = [s for s in data("spells") if s.get("public", True)]
spell_url = lambda s: BASE + "spells/%s.html" % s["id"]
no = lambda s: "NO. %03d" % (spells.index(s) + 1)
fmt = lambda d: (d or "").replace("-", ".")

# 常見問題：(分組, 問題, 答案)。答案可以用 <a href="tools.html">連結</a> 或 <b>粗體</b>。
# 分組 "site" 顯示在「關於」頁，"order" 顯示在「戀人入住申請所」頁；也會進結構化資料和 llms.txt。
THREADS = '<a href="https://www.threads.com/@xiaxia_7575" target="_blank" rel="noopener">Threads @xiaxia_7575</a>'
FAQ = [
 ("site", "岔頁 OFF PAGE 是什麼？",
  "岔頁是 Xia mumu 的個人創作收藏室。這裡收錄原創互動敘事世界觀<b>《NULL》《棲川市》《第七婚籍管理處》</b>、<a href=\"./stories.html\">角色故事</a>、<a href=\"spells.html\">小咒語收藏室</a>，以及讓角色住進 iPhone 主畫面的<a href=\"tools.html\">小工具</a>。"),
 ("site", "小咒語是什麼？怎麼用？",
  "小咒語是寫給 AI 角色扮演用的情境提示，每一則都設定一個會讓故事轉向的狀況。到<a href=\"spells.html\">小咒語收藏室</a>挑一則、按複製，貼進你和角色的對話裡就能用；連載型的咒語可以一回一回分開複製。"),
 ("site", "角色故事在哪裡看？",
  "在<a href=\"./stories.html\">角色故事館</a>。目前有《棲川市》與《NULL》兩本刊物，翻開刊物、選一個角色，就能讀到他們各自的故事。"),
 ("site", "可以自己做角色主畫面小工具嗎？要花錢嗎？",
  "可以。<a href=\"tools.html\">小工具頁</a>有一步一步的教學和可以直接複製的指令，用自己的 Claude 帳號請 Claude 幫你做，不用寫程式，也不用申請 API 金鑰。如果只要小工具、不需要和她聊天，用事先寫好的台詞就能<b>完全免費</b>。"),
 ("site", "Android 可以用嗎？",
  "目前只支援 iPhone。小工具是用 Scriptable 做的，而 Scriptable 沒有 Android 版。"),
 ("order", "委託費用是多少？",
  "基本入住費 <b>NT$300</b>：固定模板客製化，含角色名稱、對你的稱呼、重要日期、配色，以及完整 Scriptable JS 檔與圖文安裝教學。另外可以加購完整台詞包（+NT$400–600）、進階互動功能包（+NT$300）、Q 版角色素材（6 張 +NT$300、12 張 +NT$500）等項目。"),
 ("order", "多久可以拿到？怎麼付款？",
  "資料齊全後，基本方案 <b>7 個工作天</b>，有加購為 10–14 個工作天；急件加收 50%。付款方式為 LINE Pay 或銀行轉帳，全額預付，NT$1,000 以上可以先付五成。每月限 10 位。"),
 ("order", "可以委託真人，或是別人家的角色嗎？",
  "只接角色，<b>不接真人</b>（包含真人照片與以真人為原型的改畫）。原創或二創角色都可以；如果是別人家的角色，請先取得親媽同意，並確認對方可以接受的二創範圍。"),
 ("order", "我沒有角色圖，或想用繪師畫的圖可以嗎？",
  "沒有圖可以加購 Q 版角色素材（AI 生成，我會整理去背、統一大小與位置）。想用繪師的圖也歡迎，請先跟繪師確認圖可以交給第三方裁切、去背、放進小工具，最好請繪師提供去背 PNG。"),
 ("order", "小工具裡可以跟角色聊天嗎？",
  "觸摸互動和預設台詞不需要 AI。想和角色自由聊天，需要自己準備聊天頁（例如用自己的 Claude 帳號做一個），我再幫你把小工具的聊天入口連過去。點聊天按鈕會開啟那個頁面，不是在小工具裡直接對話。"),
 ("order", "裝好之後出問題怎麼辦？",
  "交付後 7 天內，可重現的程式錯誤免費修。不過本服務不提供遠端操作、一對一安裝指導或手機設定協助，安裝需要依照教學自己完成。"),
 ("order", "要怎麼委託？",
  "在下面填好入住申請單，再到 " + THREADS + " 私訊給我。我確認內容、回覆報價，付款後開始排單；完成後先給你預覽截圖，確認後交付 JS 檔、素材與安裝教學。"),
]
plain = lambda h: html.unescape(re.sub(r"<[^>]+>", "", h))

WORLD_DESC = {w["id"]: "、".join(w["genres"]) + "。" + w["line"] for w in worlds}

# ---------- 各分頁的標題與描述（標題要跟 index.html 裡 router 的 TITLES 一致） ----------
PAGES = {
 "home":   ("",            "岔頁 OFF PAGE｜Xia mumu 的原創互動敘事、角色故事與小咒語",
            "岔頁 OFF PAGE 是 Xia mumu 的創作入口：原創互動敘事世界觀《NULL》《棲川市》《第七婚籍管理處》、角色故事、可直接複製的 AI 角色扮演小咒語，以及 iPhone Scriptable 角色主畫面小工具教學與客製委託。"),
 "worlds": ("worlds.html", "世界觀收藏｜岔頁 OFF PAGE",
            "Xia mumu 的原創互動敘事世界觀：" + "、".join("%s《%s》" % (w["genres"][0], w["title"]) for w in worlds) + "。每個世界都有自己的入口。"),
 "spells": ("spells.html", "小咒語收藏室｜岔頁 OFF PAGE",
            "小咒語收藏室：%d 則可以直接複製、貼給角色的 AI 角色扮演情境提示，依戀愛日常、吃醋與曖昧、衝突與和解等標籤分類，也能隨機抽一則。" % len(spells)),
 "tools":  ("tools.html",  "角色主畫面小工具｜岔頁 OFF PAGE",
            "讓角色住進 iPhone 主畫面：Scriptable 角色小工具介紹與自製教學。不用寫程式，用自己的 Claude 帳號就能做，附可以直接複製的指令。範例角色聞止水。"),
 "order":  ("order.html",  "戀人入住申請所｜岔頁 OFF PAGE",
            "岔頁｜戀人入住申請所：iPhone Scriptable 角色主畫面小工具客製委託。基本入住費 NT$300 起，12 組配色可選，可加購台詞包與 Q 版素材；只接角色，不接真人。"),
 "about":  ("about.html",  "關於 Xia mumu｜岔頁 OFF PAGE",
            "關於 Xia mumu：寫角色、建立世界、設計互動敘事的創作者。岔頁 OFF PAGE 的常見問題也在這裡。"),
}

# ---------- 結構化資料 ----------
AUTHOR = {"@id": BASE + "#xia-mumu"}
PERSON = {"@type": "Person", "@id": BASE + "#xia-mumu", "name": "Xia mumu", "url": BASE + "about.html",
          "description": "原創角色、世界觀與互動敘事創作者。",
          "sameAs": ["https://www.threads.com/@xiaxia_7575", "https://github.com/xia-mumu"]}
WEBSITE = {"@type": "WebSite", "@id": BASE + "#website", "url": BASE, "name": "岔頁 OFF PAGE",
           "alternateName": ["岔頁", "OFF PAGE", "Off Page by Xia mumu"], "inLanguage": "zh-Hant",
           "description": "Xia mumu 的原創互動敘事作品入口、角色故事與小咒語收藏室。", "publisher": AUTHOR}

def faq_ld(group):
    return {"@type": "FAQPage", "inLanguage": "zh-Hant",
            "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": plain(a)}}
                           for g, q, a in FAQ if g == group]}

def crumbs(*items):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i, "name": n, "item": u} for i, (n, u) in enumerate(items, 1)]}

def world_parts():
    return [{"@type": "CreativeWork", "name": w["title"], "alternateName": w["en"], "url": w["url"], "genre": w["genres"],
             "description": w["line"], "inLanguage": "zh-Hant", "author": AUTHOR} for w in worlds]

def page_ld(key):
    path, title, desc = PAGES[key]
    url = BASE + path
    def web(t="WebPage", **kw):
        d = {"@type": t, "@id": url + "#page", "url": url, "name": title, "description": desc,
             "inLanguage": "zh-Hant", "isPartOf": {"@id": BASE + "#website"}}
        d.update(kw)
        return d
    home = ("岔頁 OFF PAGE", BASE)
    if key == "home":
        return [WEBSITE, PERSON, web("CollectionPage", about=AUTHOR, dateModified=TODAY,
                                     primaryImageOfPage=BASE + "images/og.jpg", hasPart=world_parts())]
    if key == "worlds":
        return [web("CollectionPage", hasPart=world_parts()), crumbs(home, ("世界觀收藏", url))]
    if key == "spells":
        return [web("CollectionPage", mainEntity={"@type": "ItemList", "numberOfItems": len(spells), "itemListElement": [
                    {"@type": "ListItem", "position": i, "url": spell_url(s), "name": s["title"]} for i, s in enumerate(spells, 1)]}),
                crumbs(home, ("小咒語收藏室", url))]
    if key == "tools":
        return [web(about={"@type": "Thing", "name": "iPhone Scriptable 角色主畫面小工具"}), crumbs(home, ("角色主畫面小工具", url))]
    if key == "order":
        return [web(), {"@type": "Service", "@id": url + "#service", "name": "岔頁｜戀人入住申請所",
                        "serviceType": "iPhone Scriptable 角色主畫面小工具客製化", "url": url, "provider": PERSON,
                        "description": "把喜歡的角色做成 iPhone 主畫面小工具：含客製化 Scriptable JS 檔與圖文安裝教學。只接角色，不接真人。",
                        "offers": {"@type": "Offer", "price": "300", "priceCurrency": "TWD", "name": "基本入住費・固定模板客製化", "url": url}},
                faq_ld("order"), crumbs(home, ("角色主畫面小工具", BASE + "tools.html"), ("戀人入住申請所", url))]
    if key == "about":
        return [web("ProfilePage", mainEntity=PERSON), faq_ld("site"), crumbs(home, ("關於 Xia mumu", url))]

def spell_ld(s):
    url = spell_url(s)
    return [{"@type": "CreativeWork", "@id": url + "#spell", "url": url, "name": s["title"], "headline": s["title"],
             "description": s["intro"], "keywords": "、".join(s["tags"] + s.get("keywords", [])), "genre": "AI 角色扮演情境提示",
             "inLanguage": "zh-Hant", "dateCreated": s.get("created"), "dateModified": s.get("updated") or s.get("created"),
             "author": PERSON, "image": BASE + "images/og.jpg",
             "isPartOf": {"@type": "CollectionPage", "name": "小咒語收藏室", "url": BASE + "spells.html"}},
            crumbs(("岔頁 OFF PAGE", BASE), ("小咒語收藏室", BASE + "spells.html"), (s["title"], url))]

def ld_block(graph):
    j = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=1).replace("</", "<\\/")
    return '<!-- SEO:LD:START -->\n<script type="application/ld+json">\n%s\n</script>\n<!-- SEO:LD:END -->' % j

# ---------- 預先寫進 HTML 的內容（不跑 JavaScript 也看得到） ----------
def tags_html(s):
    return "".join('<span class="tag">%s</span>' % jsesc(t) for t in s["tags"]) + \
           ('<span class="tag">共 %d 回</span>' % len(s["parts"]) if s.get("parts") else "")

def sample_html(s):
    return '<span class="sample">範例</span>' if s.get("sample") else ""

SITEM = """
      <a class="sitem" href="spells/%s.html">
        <span class="pg">%s</span>
        <h3>%s%s</h3>
        <p>%s</p>
        <div class="tags">%s</div>
      </a>"""

def sgrid_html():
    return "".join(SITEM % (jsesc(s["id"]), no(s), jsesc(s["title"]), sample_html(s), jsesc(s["intro"]), tags_html(s))
                   for s in spells)

def faq_section(group, sid, title, lead):
    items = [(q, a) for g, q, a in FAQ if g == group]
    h = ['<!-- SEO:FAQ-%s:START -->' % group.upper(),
         '    <section class="wrap sec faq" aria-labelledby="%s">' % sid,
         '      <div class="sec-head"><span class="label">QUESTIONS</span><div><h2 id="%s">%s<em>FAQ</em></h2><p>%s</p></div></div>' % (sid, title, lead),
         '      <div class="faq-list">']
    for i, (q, a) in enumerate(items, 1):
        h += ['        <details class="faq-item"%s>' % (' open' if i == 1 else ''),
              '          <summary><span class="faq-no">Q.%02d</span><span class="faq-q">%s</span><span class="faq-ic" aria-hidden="true"></span></summary>' % (i, esc(q)),
              '          <div class="faq-a"><p>%s</p></div>' % a,
              '        </details>']
    h += ['      </div>', '    </section>', '<!-- SEO:FAQ-%s:END -->' % group.upper()]
    return "\n".join(h)

ns = ['<!-- SEO:NOSCRIPT:START -->', '<noscript>', '<section class="wrap sec">', '<h2>世界觀收藏</h2>', '<ul>']
for w in worlds:
    ns.append('<li><a href="%s">%s（%s）</a>：%s</li>' % (esc(w["url"]), esc(w["title"]), esc(w["en"]), esc(WORLD_DESC[w["id"]])))
ns += ['</ul>', '<h2>更多頁面</h2>', '<ul>',
       '<li><a href="spells.html">小咒語收藏室</a>：可以直接複製、貼給角色的 AI 角色扮演情境提示。</li>',
       '<li><a href="./stories.html">角色故事館</a>：《棲川市》與《NULL》的角色短篇。</li>',
       '<li><a href="tools.html">角色主畫面小工具</a>：讓角色住進 iPhone 主畫面的教學。</li>',
       '<li><a href="order.html">戀人入住申請所</a>：角色小工具客製委託。</li>',
       '<li><a href="about.html">關於 Xia mumu</a>與常見問題。</li>',
       '</ul>', '</section>', '</noscript>', '<!-- SEO:NOSCRIPT:END -->']

def put(text, name, block, anchor):
    pat = re.compile(r'<!-- SEO:%s:START -->.*?<!-- SEO:%s:END -->' % (name, name), re.S)
    if pat.search(text):
        return pat.sub(lambda m: block, text)
    i = text.index(anchor)
    return text[:i] + block + "\n" + text[i:]

out = put(src, "LD", ld_block(page_ld("home")), "</head>")
out = put(out, "NOSCRIPT", "\n".join(ns), "</main>")
out = put(out, "FAQ-ORDER", faq_section("order", "h-faq-order", "委託常見問題", "還有其他想問的，歡迎直接到 Threads 私訊。"),
          '    <section class="wrap sec order" id="rs-form"')
out = put(out, "FAQ-SITE", faq_section("site", "h-faq-site", "常見問題", "第一次翻開岔頁？先從這裡開始。"),
          '  </div>\n\n  <!-- ===== 404 ===== -->')
out, n = re.subn(r'<div class="sgrid" id="sgrid">.*?</div><!-- /sgrid -->|<div class="sgrid" id="sgrid"></div>',
                 lambda m: '<div class="sgrid" id="sgrid">' + sgrid_html() + '\n      </div><!-- /sgrid -->', out, count=1, flags=re.S)
assert n == 1, "sgrid"
(ROOT / "index.html").write_text(out, encoding="utf-8")

# ---------- 從 index.html 複製出各分頁 ----------
def set_meta(page, title, desc, url, og_type="website"):
    subs = [(r'<title>.*?</title>', '<title>%s</title>' % esc(title)),
            (r'<meta name="description" content="[^"]*"', '<meta name="description" content="%s"' % esc(desc)),
            (r'<link rel="canonical" href="[^"]*"', '<link rel="canonical" href="%s"' % url),
            (r'<meta property="og:url" content="[^"]*"', '<meta property="og:url" content="%s"' % url),
            (r'<meta property="og:title" content="[^"]*"', '<meta property="og:title" content="%s"' % esc(title)),
            (r'<meta property="og:description" content="[^"]*"', '<meta property="og:description" content="%s"' % esc(desc)),
            (r'<meta property="og:type" content="[^"]*"', '<meta property="og:type" content="%s"' % og_type)]
    for pat, rep in subs:
        page, k = re.subn(pat, lambda m, rep=rep: rep, page, count=1, flags=re.S)
        assert k == 1, pat
    return page

def show_view(page, view):
    return re.sub(r'<div class="view" id="v-(\w+)" data-view="\w+"(?: hidden)?>',
                  lambda m: '<div class="view" id="v-%s" data-view="%s"%s>' % (m.group(1), m.group(1), "" if m.group(1) == view else " hidden"),
                  page)

def fill_spell(page, s):
    parts = s.get("parts") or [{"label": "", "text": s.get("text", "")}]
    if len(parts) > 1:
        body = "".join('<section class="part"><div class="part-head"><b><span class="no">PART %02d / %02d</span>%s</b>'
                       '<button class="btn quiet sm" type="button" data-part="%d">複製這一回</button></div>'
                       '<div class="incant">%s</div></section>' % (i + 1, len(parts), jsesc(p["label"]), i, jsesc(p["text"]))
                       for i, p in enumerate(parts))
    else:
        body = '<div class="incant">%s</div>' % jsesc(parts[0]["text"])
    fills = [('<span class="label" id="d-pg">PAGE 002 / SPELL</span>', '<span class="label" id="d-pg">PAGE 002 / %s</span>' % no(s)),
             ('<div class="dates" id="d-dates"></div>', '<div class="dates" id="d-dates">建立　%s<br>更新　%s</div>' % (fmt(s.get("created")), fmt(s.get("updated")))),
             ('<h1 id="d-title"></h1>', '<h1 id="d-title">%s%s</h1>' % (jsesc(s["title"]), sample_html(s))),
             ('<p class="intro" id="d-intro"></p>', '<p class="intro" id="d-intro">%s</p>' % jsesc(s["intro"])),
             ('<div class="tags" id="d-tags"></div>', '<div class="tags" id="d-tags">%s</div>' % tags_html(s)),
             ('<p class="note" id="d-note" hidden></p>', '<p class="note" id="d-note"%s>%s</p>' % ("" if s.get("note") else " hidden", jsesc(s.get("note", "")))),
             ('<div id="d-parts"></div>', '<div id="d-parts">%s</div>' % body)]
    if len(parts) > 1:
        fills.append(('<button class="btn" type="button" id="d-copy">', '<button class="btn" type="button" id="d-copy" hidden>'))
    for a, b in fills:
        assert page.count(a) == 1, a
        page = page.replace(a, b, 1)
    return page

def derive(key=None, spell=None):
    page = out
    if spell:
        s = spell
        title = "%s｜小咒語｜岔頁 OFF PAGE" % s["title"]
        desc = "%s——AI 角色扮演小咒語，標籤：%s。可以直接複製，貼進你和角色的對話。" % (s["intro"], "、".join(s["tags"]))
        page = set_meta(page, title, desc, spell_url(s), "article")
        page = page.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n<base href="../">', 1)
        page = page.replace('<html lang="zh-Hant">', '<html lang="zh-Hant" data-route="spell">', 1)
        page = show_view(page, "spell")
        page = put(page, "LD", ld_block(spell_ld(s)), "</head>")
        page = fill_spell(page, s)
    else:
        path, title, desc = PAGES[key]
        page = set_meta(page, title, desc, BASE + path)
        page = page.replace('<html lang="zh-Hant">', '<html lang="zh-Hant" data-route="%s">' % key, 1)
        page = show_view(page, key)
        page = put(page, "LD", ld_block(page_ld(key)), "</head>")
    page = re.sub(r'<!-- SEO:NOSCRIPT:START -->.*?<!-- SEO:NOSCRIPT:END -->\n?', "", page, flags=re.S)
    page = page.replace("<body>", "<body>\n<!-- 這個檔案是 scripts/build_seo.py 從 index.html 自動產生的：請改 index.html，不要改這裡。 -->", 1)
    return page

for key in PAGES:
    if key != "home":
        (ROOT / PAGES[key][0]).write_text(derive(key), encoding="utf-8")
sdir = ROOT / "spells"
if sdir.exists():
    shutil.rmtree(sdir)      # 下架或改名的咒語，舊頁面會一起清掉
sdir.mkdir()
for s in spells:
    (sdir / ("%s.html" % s["id"])).write_text(derive(spell=s), encoding="utf-8")

# ---------- sitemap.xml ----------
urls = [(BASE + PAGES[k][0], TODAY) for k in PAGES] + [(BASE + "stories.html", TODAY)] + \
       [(spell_url(s), s.get("updated") or s.get("created") or TODAY) for s in spells]
(ROOT / "sitemap.xml").write_text(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + "".join('  <url><loc>%s</loc><lastmod>%s</lastmod></url>\n' % (esc(u), d) for u, d in urls)
    + '</urlset>\n', encoding="utf-8")

# ---------- llms.txt ----------
L = ["# 岔頁 OFF PAGE", "",
     "> 岔頁 OFF PAGE 是創作者 Xia mumu 的個人創作入口網站（繁體中文）：收錄原創互動敘事世界觀、角色故事、可直接複製的 AI 角色扮演「小咒語」，以及 iPhone Scriptable 角色主畫面小工具的教學與客製委託服務「戀人入住申請所」。",
     "", "- 網址：" + BASE, "- 作者：[Xia mumu](%sabout.html)（Threads：@xiaxia_7575，GitHub：xia-mumu）" % BASE,
     "- 語言：繁體中文（台灣）", "- 最後更新：" + TODAY, "",
     "## 世界觀", "", "總覽：[世界觀收藏](%sworlds.html)" % BASE, ""]
for w in worlds:
    L.append("- [%s（%s）](%s)：%s" % (w["title"], w["en"], w["url"], WORLD_DESC[w["id"]]))
L += ["", "## 角色故事", "", "- [角色故事館](%sstories.html)：《棲川市》與《NULL》兩本刊物，點開角色閱讀各自的短篇故事。" % BASE,
      "", "## 小咒語收藏室", "",
      "小咒語是寫給 AI 角色扮演用的情境提示，複製後貼進和角色的對話即可使用。[收藏室總覽](%sspells.html)，目前公開 %d 則，每則都有自己的頁面：" % (BASE, len(spells)), ""]
for s in spells:
    L.append("- [%s](%s)：%s（%s）" % (s["title"], spell_url(s), s["intro"], "、".join(s["tags"])))
L += ["", "## 角色主畫面小工具", "",
      "- [小工具介紹與自製教學](%stools.html)：用 Scriptable 讓角色住進 iPhone 主畫面，範例角色為聞止水。附可直接複製給 Claude、ChatGPT 或 Gemini 的指令；只支援 iPhone。" % BASE,
      "- [戀人入住申請所（客製委託）](%sorder.html)：基本入住費 NT$300，可加購台詞包、進階互動與 Q 版素材；LINE Pay 或銀行轉帳；每月限 10 位；只接角色、不接真人。" % BASE,
      "", "## 常見問題", ""]
for _, q, a in FAQ:
    L += ["### " + q, plain(a), ""]
(ROOT / "llms.txt").write_text("\n".join(L), encoding="utf-8")
print("pages %d, spells %d, sitemap %d urls" % (len(PAGES), len(spells), len(urls)))
