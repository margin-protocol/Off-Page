#!/usr/bin/env python3
"""重新產生 SEO／AEO 用的檔案。新增作品、咒語或故事後，在 repo 根目錄執行：
    python3 scripts/build_seo.py
會更新：index.html 裡的 <noscript> 備用內容與 JSON-LD、sitemap.xml、llms.txt。
"""
import json, re, html, datetime, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = "https://xia-mumu.github.io/Off-Page/"
TODAY = datetime.date.today().isoformat()
esc = lambda s: html.escape(str(s), quote=True)

src = (ROOT / "index.html").read_text(encoding="utf-8")

def data(i):
    m = re.search(r'<script type="application/json" id="data-%s">(.*?)</script>' % i, src, re.S)
    return json.loads(m.group(1))

worlds = data("worlds")
spells = [s for s in data("spells") if s.get("public", True)]

stories_src = (ROOT / "stories.html").read_text(encoding="utf-8")

# 常見問題：(分組, 問題, 答案)。答案可以用 <a href="#tools">連結</a> 或 <b>粗體</b>。
# 分組 "site" 顯示在「關於」頁，"order" 顯示在「戀人入住申請所」頁；全部都會進結構化資料和 llms.txt。
THREADS = '<a href="https://www.threads.com/@xiaxia_7575" target="_blank" rel="noopener">Threads @xiaxia_7575</a>'
FAQ = [
 ("site", "岔頁 OFF PAGE 是什麼？",
  "岔頁是 Xia mumu 的個人創作收藏室。這裡收錄原創互動敘事世界觀<b>《NULL》《棲川市》《第七婚籍管理處》</b>、<a href=\"./stories.html\">角色故事</a>、<a href=\"#spells\">小咒語收藏室</a>，以及讓角色住進 iPhone 主畫面的<a href=\"#tools\">小工具</a>。"),
 ("site", "小咒語是什麼？怎麼用？",
  "小咒語是寫給 AI 角色扮演用的情境提示，每一則都設定一個會讓故事轉向的狀況。到<a href=\"#spells\">小咒語收藏室</a>挑一則、按複製，貼進你和角色的對話裡就能用；連載型的咒語可以一回一回分開複製。"),
 ("site", "角色故事在哪裡看？",
  "在<a href=\"./stories.html\">角色故事館</a>。目前有《棲川市》與《NULL》兩本刊物，翻開刊物、選一個角色，就能讀到他們各自的故事。"),
 ("site", "可以自己做角色主畫面小工具嗎？要花錢嗎？",
  "可以。<a href=\"#tools\">小工具頁</a>有一步一步的教學和可以直接複製的指令，用自己的 Claude 帳號請 Claude 幫你做，不用寫程式，也不用申請 API 金鑰。如果只要小工具、不需要和她聊天，用事先寫好的台詞就能<b>完全免費</b>。"),
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

# ---------- JSON-LD ----------
person = {"@type": "Person", "@id": BASE + "#xia-mumu", "name": "Xia mumu",
          "url": BASE + "#about",
          "description": "原創角色、世界觀與互動敘事創作者。",
          "sameAs": ["https://www.threads.com/@xiaxia_7575", "https://github.com/xia-mumu"]}
graph = [
 {"@type": "WebSite", "@id": BASE + "#website", "url": BASE, "name": "岔頁 OFF PAGE",
  "alternateName": ["岔頁", "OFF PAGE", "Off Page by Xia mumu"], "inLanguage": "zh-Hant",
  "description": "Xia mumu 的原創互動敘事作品入口、角色故事與小咒語收藏室。",
  "publisher": {"@id": BASE + "#xia-mumu"}},
 person,
 {"@type": "CollectionPage", "@id": BASE + "#page", "url": BASE, "name": "岔頁 OFF PAGE",
  "isPartOf": {"@id": BASE + "#website"}, "about": {"@id": BASE + "#xia-mumu"},
  "inLanguage": "zh-Hant", "dateModified": TODAY,
  "primaryImageOfPage": BASE + "images/og.jpg",
  "hasPart": [{"@type": "CreativeWork", "name": w["title"], "alternateName": w["en"], "url": w["url"],
               "genre": w["genres"], "description": w["line"], "inLanguage": "zh-Hant",
               "author": {"@id": BASE + "#xia-mumu"}} for w in worlds]
           + [{"@type": "CreativeWork", "name": "小咒語收藏室", "url": BASE + "#spells",
               "description": "可直接複製使用的 AI 角色扮演情境提示，目前公開 %d 則。" % len(spells),
               "author": {"@id": BASE + "#xia-mumu"}},
              {"@type": "CreativeWork", "name": "角色故事", "url": BASE + "stories.html",
               "description": "《棲川市》與《NULL》的角色短篇故事。",
               "author": {"@id": BASE + "#xia-mumu"}}]},
 {"@type": "Service", "@id": BASE + "#order", "name": "岔頁｜戀人入住申請所",
  "serviceType": "iPhone Scriptable 角色主畫面小工具客製化", "url": BASE + "#order",
  "provider": {"@id": BASE + "#xia-mumu"},
  "description": "把喜歡的角色做成 iPhone 主畫面小工具：含客製化 Scriptable JS 檔與圖文安裝教學。只接角色，不接真人。",
  "offers": {"@type": "Offer", "price": "300", "priceCurrency": "TWD",
             "name": "基本入住費・固定模板客製化", "url": BASE + "#order"}},
 {"@type": "FAQPage", "@id": BASE + "#faq", "inLanguage": "zh-Hant",
  "mainEntity": [{"@type": "Question", "name": q,
                  "acceptedAnswer": {"@type": "Answer", "text": plain(a)}} for _, q, a in FAQ]},
]
ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=1).replace("</", "<\\/")
ld_block = '<!-- SEO:LD:START -->\n<script type="application/ld+json">\n%s\n</script>\n<!-- SEO:LD:END -->' % ld

# ---------- noscript 備用內容（給不執行 JavaScript 的搜尋引擎與 AI 爬蟲） ----------
ns = ['<!-- SEO:NOSCRIPT:START -->', '<noscript>', '<section class="wrap sec">',
      '<h2>世界觀收藏</h2>', '<ul>']
for w in worlds:
    ns.append('<li><a href="%s">%s（%s）</a>：%s</li>' % (esc(w["url"]), esc(w["title"]), esc(w["en"]), esc(WORLD_DESC[w["id"]])))
ns += ['</ul>', '<h2>角色故事</h2>',
       '<p><a href="./stories.html">角色故事館</a>：《棲川市》與《NULL》的角色短篇。</p>',
       '<h2>小咒語收藏室</h2>', '<p>可以直接複製、貼給角色的 AI 角色扮演情境提示。</p>', '<ul>']
for s in spells:
    ns.append('<li><a href="#spell-%s">%s</a>：%s（%s）</li>' % (esc(s["id"]), esc(s["title"]), esc(s["intro"]), esc("、".join(s["tags"]))))
ns += ['</ul>']
ns += ['</dl>', '</section>', '</noscript>', '<!-- SEO:NOSCRIPT:END -->']
ns_block = "\n".join(ns)

def faq_section(group, sid, label, title, lead):
    items = [(q, a) for g, q, a in FAQ if g == group]
    h = ['<!-- SEO:FAQ-%s:START -->' % group.upper(),
         '    <section class="wrap sec faq" aria-labelledby="%s">' % sid,
         '      <div class="sec-head"><span class="label">%s</span><div><h2 id="%s">%s<em>FAQ</em></h2><p>%s</p></div></div>' % (label, sid, title, lead),
         '      <div class="faq-list">']
    for i, (q, a) in enumerate(items, 1):
        h += ['        <details class="faq-item"%s>' % (' open' if i == 1 else ''),
              '          <summary><span class="faq-no">Q.%02d</span><span class="faq-q">%s</span><span class="faq-ic" aria-hidden="true"></span></summary>' % (i, esc(q)),
              '          <div class="faq-a"><p>%s</p></div>' % a,
              '        </details>']
    h += ['      </div>', '    </section>', '<!-- SEO:FAQ-%s:END -->' % group.upper()]
    return "\n".join(h)

def put(text, name, block, anchor, before=True):
    pat = re.compile(r'<!-- SEO:%s:START -->.*?<!-- SEO:%s:END -->' % (name, name), re.S)
    if pat.search(text):
        return pat.sub(lambda m: block, text)
    i = text.index(anchor)
    return text[:i] + block + "\n" + text[i:] if before else text[:i + len(anchor)] + "\n" + block + text[i + len(anchor):]

out = put(src, "LD", ld_block, "</head>")
out = put(out, "NOSCRIPT", ns_block, "</main>")
out = put(out, "FAQ-ORDER", faq_section("order", "h-faq-order", "QUESTIONS", "委託常見問題", "還有其他想問的，歡迎直接到 Threads 私訊。"), '    <section class="wrap sec order" id="rs-form"')
out = put(out, "FAQ-SITE", faq_section("site", "h-faq-site", "QUESTIONS", "常見問題", "第一次翻開岔頁？先從這裡開始。"), '  </div>\n\n  <!-- ===== 404 ===== -->')
(ROOT / "index.html").write_text(out, encoding="utf-8")

# ---------- sitemap.xml ----------
(ROOT / "sitemap.xml").write_text(
 '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
 + "".join('  <url><loc>%s</loc><lastmod>%s</lastmod></url>\n' % (u, TODAY) for u in (BASE, BASE + "stories.html"))
 + '</urlset>\n', encoding="utf-8")

# ---------- llms.txt ----------
L = ["# 岔頁 OFF PAGE", "",
     "> 岔頁 OFF PAGE 是創作者 Xia mumu 的個人創作入口網站（繁體中文）：收錄原創互動敘事世界觀、角色故事、可直接複製的 AI 角色扮演「小咒語」，以及 iPhone Scriptable 角色主畫面小工具的教學與客製委託服務「戀人入住申請所」。",
     "", "- 網址：" + BASE, "- 作者：Xia mumu（Threads：@xiaxia_7575，GitHub：xia-mumu）",
     "- 語言：繁體中文（台灣）", "- 最後更新：" + TODAY, "",
     "## 世界觀", ""]
for w in worlds:
    L.append("- [%s（%s）](%s)：%s" % (w["title"], w["en"], w["url"], WORLD_DESC[w["id"]]))
L += ["", "## 角色故事", "", "- [角色故事館](%sstories.html)：《棲川市》與《NULL》兩本刊物，點開角色閱讀各自的短篇故事。" % BASE,
      "", "## 小咒語收藏室", "",
      "小咒語是寫給 AI 角色扮演用的情境提示，複製後貼進和角色的對話即可使用。目前公開 %d 則：" % len(spells), ""]
for s in spells:
    L.append("- [%s](%s#spell-%s)：%s（%s）" % (s["title"], BASE, s["id"], s["intro"], "、".join(s["tags"])))
L += ["", "## 角色主畫面小工具", "",
      "- [小工具介紹與自製教學](%s#tools)：用 Scriptable 讓角色住進 iPhone 主畫面，範例角色為聞止水。附可直接複製給 Claude、ChatGPT 或 Gemini 的指令；只支援 iPhone。" % BASE,
      "- [戀人入住申請所（客製委託）](%s#order)：基本入住費 NT$300，可加購台詞包、進階互動與 Q 版素材；LINE Pay 或銀行轉帳；每月限 10 位；只接角色、不接真人。" % BASE,
      "", "## 常見問題", ""]
for _, q, a in FAQ:
    L += ["### " + q, plain(a), ""]
(ROOT / "llms.txt").write_text("\n".join(L), encoding="utf-8")
print("worlds", len(worlds), "spells", len(spells), "ok")
