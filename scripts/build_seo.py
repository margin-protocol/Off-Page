#!/usr/bin/env python3
"""重新產生 SEO／AEO 用的檔案。新增作品、咒語或故事後，在 repo 根目錄執行：
    python3 scripts/build_seo.py
會更新：index.html 裡的 <noscript> 備用內容與 JSON-LD、sitemap.xml、llms.txt。
"""
import json, re, html, datetime, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = "https://xia-mumu.github.io/off-page/"
TODAY = datetime.date.today().isoformat()
esc = lambda s: html.escape(str(s), quote=True)

src = (ROOT / "index.html").read_text(encoding="utf-8")

def data(i):
    m = re.search(r'<script type="application/json" id="data-%s">(.*?)</script>' % i, src, re.S)
    return json.loads(m.group(1))

worlds = data("worlds")
spells = [s for s in data("spells") if s.get("public", True)]

stories_src = (ROOT / "stories.html").read_text(encoding="utf-8")

FAQ = [
 ("岔頁 OFF PAGE 是什麼？",
  "岔頁 OFF PAGE 是創作者 Xia mumu 的個人創作入口網站，收錄原創互動敘事世界觀《NULL》《棲川市》《第七婚籍管理處》、角色故事、小咒語收藏室，以及 iPhone 角色主畫面小工具的教學與客製委託。"),
 ("小咒語是什麼？怎麼用？",
  "小咒語是寫給 AI 角色扮演用的情境提示，每一則設定一個會讓故事轉向的狀況。在岔頁的小咒語收藏室挑一則、按複製，貼進你和角色的對話裡就能使用；連載型的咒語可以一回一回分開複製。"),
 ("角色主畫面小工具是什麼？Android 可以用嗎？",
  "它是用 Scriptable 做的 iPhone 主畫面小工具：角色會待在主畫面上，依時間、天氣、電量和紀念日換台詞，點進去還能和她互動。目前只支援 iPhone，因為 Scriptable 沒有 Android 版。"),
 ("可以自己做角色小工具嗎？需要花錢嗎？",
  "可以。岔頁的小工具頁有一步一步的教學和可以直接複製的指令，用自己的 Claude 帳號請 Claude 幫你做，不用寫程式也不用申請 API 金鑰。如果只要小工具、不需要 AI 聊天，用事先寫好的台詞就能完全免費。"),
 ("戀人入住申請所的委託費用是多少？",
  "基本入住費是 NT$300（固定模板客製化，含角色名稱、稱呼、重要日期、配色、Scriptable JS 檔與圖文安裝教學）。可加購完整台詞包（+NT$400–600）、進階互動功能包（+NT$300）、Q 版角色素材（6 張 +NT$300、12 張 +NT$500）等項目。"),
 ("委託的交期和付款方式？",
  "基本方案在資料齊全後 7 個工作天交付，有加購為 10–14 個工作天；急件加收 50%。付款方式為 LINE Pay 或銀行轉帳，全額預付，NT$1,000 以上可先付五成。每月限 10 位。"),
 ("可以委託真人或別人的角色嗎？",
  "只接角色，不接真人（包含真人照片與以真人為原型的改畫）。原創或二創角色都可以；如果是別人家的角色，需要先取得原作者同意，並確認對方能接受的二創範圍。"),
 ("要怎麼委託？",
  "在岔頁的戀人入住申請所填寫入住申請單，再到 Threads 私訊 @xiaxia_7575。確認內容與報價後付款排單，完成後會先給預覽截圖，確認後交付 JS 檔、素材與安裝教學。"),
]

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
                  "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]},
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
ns += ['</ul>', '<h2>常見問題</h2>', '<dl>']
for q, a in FAQ:
    ns.append('<dt>%s</dt><dd>%s</dd>' % (esc(q), esc(a)))
ns += ['</dl>', '</section>', '</noscript>', '<!-- SEO:NOSCRIPT:END -->']
ns_block = "\n".join(ns)

def put(text, name, block, anchor, before=True):
    pat = re.compile(r'<!-- SEO:%s:START -->.*?<!-- SEO:%s:END -->' % (name, name), re.S)
    if pat.search(text):
        return pat.sub(lambda m: block, text)
    i = text.index(anchor)
    return text[:i] + block + "\n" + text[i:] if before else text[:i + len(anchor)] + "\n" + block + text[i + len(anchor):]

out = put(src, "LD", ld_block, "</head>")
out = put(out, "NOSCRIPT", ns_block, "</main>")
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
for q, a in FAQ:
    L += ["### " + q, a, ""]
(ROOT / "llms.txt").write_text("\n".join(L), encoding="utf-8")
print("worlds", len(worlds), "spells", len(spells), "ok")
