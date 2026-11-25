(function(){
  const $ = s => document.querySelector(s);
  const read = id => { try { return JSON.parse(document.getElementById(id).textContent); } catch(e){ return []; } };
  const WORLDS = read('data-worlds');
  const SPELLS = read('data-spells').filter(s => s.public !== false);
  const UPDATES = read('data-updates');
  const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const no = s => 'NO. ' + String(SPELLS.indexOf(s)+1).padStart(3,'0');
  const SITE = new URL('./', document.baseURI);   // 網站根目錄（小咒語頁有 <base href="../">）
  const spellUrl = id => new URL('spells/' + encodeURIComponent(id) + '.html', SITE).href;
  const fmtDate = d => (d||'').replace(/-/g,'.');
  const reduce = matchMedia('(prefers-reduced-motion: reduce)');

  /* ---------- toast & copy ---------- */
  let tt;
  function toast(msg){ const t=$('#toast'); t.textContent=msg; t.classList.add('show'); clearTimeout(tt); tt=setTimeout(()=>t.classList.remove('show'),1800); }
  function copyText(text, okMsg){
    const fallback = () => {
      const ta=document.createElement('textarea'); ta.value=text; ta.setAttribute('readonly','');
      ta.style.position='fixed'; ta.style.opacity='0'; document.body.appendChild(ta); ta.select();
      let ok=false; try{ ok=document.execCommand('copy'); }catch(e){}
      ta.remove(); toast(ok ? okMsg : '複製沒有成功，請手動選取文字');
    };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(()=>toast(okMsg), fallback);
    } else fallback();
  }


  /* 複製咒語後，輕輕問一次要不要留紙條（每次造訪最多一次） */
  let nudged=false, nt;
  function nudge(){
    try{ if(sessionStorage.getItem('offpage-nudged')) nudged=true; }catch(e){}
    if(nudged) return; nudged=true;
    try{ sessionStorage.setItem('offpage-nudged','1'); }catch(e){}
    const n=$('#nudge'); if(!n) return;
    setTimeout(()=>{ n.classList.add('show'); nt=setTimeout(()=>n.classList.remove('show'),8000); },2000);
  }
  document.addEventListener('click', e=>{ if(e.target.closest('#nudge-x')||e.target.closest('#nudge a')){ clearTimeout(nt); $('#nudge').classList.remove('show'); } });

  /* ---------- worlds ---------- */
  function cover(w){
    if (w.cover==='null') return `<div class="cover-in c-null"><span class="no">${esc(w.no)}</span><span class="bar"></span><span class="t">NULL</span><span class="s">PREDICT · 分類失敗</span></div>`;
    if (w.cover==='qichuan') return `<div class="cover-in c-qichuan"><span class="no">${esc(w.no)}</span><span class="moon"></span><span class="t">棲川市</span><span class="s">Qichuan City</span></div>`;
    if (w.cover==='seventh') return `<div class="cover-in c-seventh"><span class="frame"></span><span class="no">${esc(w.no)}</span><span class="seal">契</span><span class="t">第七<br>婚籍管理處</span></div>`;
    if (w.cover==='unfinished') return `<div class="cover-in c-unfinished"><span class="no">${esc(w.no)}</span><span class="t">愛的未完成式</span><span class="s">THE UNFINISHED LOVE</span><svg viewBox="0 0 200 92" fill="none" stroke-linecap="round"><path d="M10 88H190" stroke="#D9CFC6"/><path d="M34 14V88M34 56H74V88" stroke="#7A5A4F" stroke-width="1.4"/><path d="M166 14V88M166 56H126V88" stroke="#7A5A4F" stroke-width="1.4"/><path d="M74 52C84 38 92 60 97 46" stroke="#9B3B33" stroke-width="1.4"/><path d="M126 52C116 66 108 40 103 50" stroke="#9B3B33" stroke-width="1.4"/></svg></div>`;
    return `<div class="cover-in" style="background:var(--mist)"><span class="no">${esc(w.no)}</span></div>`;
  }
  function worldCard(w){
    const live = !!w.url;
    const link = live
      ? `<a class="enter" href="${esc(w.url)}" target="_blank" rel="noopener">${esc(w.cta)} ↗<span class="sr" style="position:absolute;left:-9999px">（另開新分頁，前往外部作品網站）</span></a>`
      : `<span class="enter off" aria-disabled="true">入口準備中</span>`;
    return `<article class="wcard">
      <div class="cover" aria-hidden="true">${cover(w)}</div>
      <div class="wbody">
        <h3>${esc(w.title)}<small>${esc(w.en)}</small></h3>
        <div class="genres">${w.genres.map(g=>`<span>${esc(g)}</span>`).join('')}</div>
        <p class="line">「${esc(w.line)}」</p>
        <div class="wfoot"><span class="status${live?'':' soon'}">${esc(w.status)}</span><span class="links-w">${link}${w.play?`<a class="play" href="${esc(w.play)}" target="_blank" rel="noopener">點此遊玩 ↗<span style="position:absolute;left:-9999px">（另開新分頁，前往 cheliz 遊玩）</span></a>`:''}</span></div>
      </div>
    </article>`;
  }
  $('#home-worlds').innerHTML = WORLDS.slice(0,4).map(worldCard).join('');
  $('#all-worlds').innerHTML = WORLDS.map(worldCard).join('');
  $('#random-world').addEventListener('click', ()=>{
    const live = WORLDS.filter(w=>w.url);
    if(!live.length) return;
    const w = live[Math.floor(Math.random()*live.length)];
    const a = document.createElement('a'); a.href=w.url; a.target='_blank'; a.rel='noopener'; document.body.appendChild(a); a.click(); a.remove();
    toast('翻開了：' + w.title);
  });

  /* ---------- recent ---------- */
  $('#recent').innerHTML = UPDATES.slice().sort((a,b)=>b.date.localeCompare(a.date)).map(u=>{
    const ext = /^https?:/.test(u.link);
    return `<li><time datetime="${esc(u.date)}">${fmtDate(u.date)}</time><span class="kind">${esc(u.kind)}</span>
      <span class="ttl">${esc(u.title)}<small>${esc(u.note||'')}</small></span>
      ${u.link?`<a href="${esc(u.link)}"${ext?' target="_blank" rel="noopener"':''}>${ext?'前往 ↗':'翻到這頁 →'}</a>`:'<span></span>'}</li>`;
  }).join('');
  (function(){   // 首頁只先攤開最近 6 筆，其餘收在「展開全部」裡（紀錄不刪）
    const items = [...document.querySelectorAll('#recent > li')], btn = $('#recent-more'), N = 6;
    if (items.length <= N) return;
    items.slice(N).forEach(li=>li.hidden = true);
    btn.hidden = false;
    btn.addEventListener('click', ()=>{ items.forEach(li=>li.hidden = false); btn.hidden = true; });
  })();


  /* ---------- 公告橫幅＋小鈴鐺 ---------- */
  (function(){
    const list = UPDATES.slice().sort((a,b)=>b.date.localeCompare(a.date));
    const top = list[0]; if(!top) return;
    const uid = u => u.date+'|'+u.title;
    const get = k => { try{ return localStorage.getItem(k); }catch(e){ return null; } };
    const set = (k,v) => { try{ localStorage.setItem(k,v); }catch(e){} };
    const ext = u => /^https?:/.test(u.link||'');
    const attrs = u => `href="${esc(u.link||'./')}"${ext(u)?' target="_blank" rel="noopener"':''}`;

    // 橫幅：打叉後記住這一則；發新公告就會再出現
    const box = $('#notice');
    if (get('offpage-notice-closed') !== uid(top)) {
      const a = $('#notice-link');
      a.href = top.link || './';
      if (ext(top)) { a.target='_blank'; a.rel='noopener'; }
      $('#notice-date').textContent = fmtDate(top.date).slice(5);
      $('#notice-title').textContent = top.title;
      box.hidden = false;
    }
    $('#notice-close').addEventListener('click', ()=>{ box.hidden = true; set('offpage-notice-closed', uid(top)); });

    // 小鈴鐺：有沒看過的新公告就亮小紅點
    const bell = $('#bell'), panel = $('#bell-panel'), dot = $('#bell-dot');
    if (get('offpage-bell-seen') !== uid(top)) dot.hidden = false;
    $('#bell-list').innerHTML = list.slice(0,6).map(u=>`<li><a ${attrs(u)}><time>${fmtDate(u.date)}</time><span class="k">${esc(u.kind)}</span><span class="t">${esc(u.title)}${ext(u)?' ↗':''}</span></a></li>`).join('');
    const place = ()=>{ const r = bell.getBoundingClientRect(); panel.style.top = (r.bottom+8)+'px'; const w = panel.offsetWidth; panel.style.left = Math.min(Math.max(12, r.right - w), innerWidth - w - 12)+'px'; };
    const open = v => { panel.hidden = !v; bell.setAttribute('aria-expanded', v); if(v){ place(); dot.hidden = true; set('offpage-bell-seen', uid(top)); } };
    bell.addEventListener('click', e=>{ e.stopPropagation(); open(panel.hidden); });
    panel.addEventListener('click', e=>{ if(e.target.closest('a')) open(false); });
    document.addEventListener('click', e=>{ if(!panel.hidden && !panel.contains(e.target)) open(false); });
    addEventListener('keydown', e=>{ if(e.key==='Escape' && !panel.hidden){ open(false); bell.focus(); } });
    addEventListener('resize', ()=>{ if(!panel.hidden) place(); });
  })();

  /* ---------- random draw ---------- */
  let lastId = null;
  function pick(){
    if(!SPELLS.length) return null;
    if(SPELLS.length===1) return SPELLS[0];
    let s; do { s = SPELLS[Math.floor(Math.random()*SPELLS.length)]; } while (s.id===lastId);
    lastId = s.id; return s;
  }
  const tagsHtml = s => s.tags.map(t=>`<span class="tag">${esc(t)}</span>`).join('') + (s.parts?`<span class="tag">共 ${s.parts.length} 回</span>`:'');
  const partsOf = s => s.parts || [{label:'',text:s.text}];
  const copyFirst = s => { copyText(partsOf(s)[0].text, s.parts ? '已複製第 1 回 ♡' : '已複製 ♡'); nudge(); };
  const sampleHtml = s => s.sample ? '<span class="sample">範例</span>' : '';
  let current = null;
  function fillCard(s){
    current = s;
    const c = $('#scard');
    c.classList.remove('blank');
    c.innerHTML = `<span class="pg">${no(s)}</span>
      <h3>${esc(s.title)}${sampleHtml(s)}</h3>
      <p class="intro">${esc(s.intro)}</p>
      <div class="tags">${tagsHtml(s)}</div>
      <div class="row">
        <a class="btn quiet" href="spells/${esc(s.id)}.html">閱讀完整咒語</a>
        <button class="btn quiet" type="button" data-copy>${s.parts?'複製第 1 回':'複製咒語'}</button>
        <button class="btn quiet" type="button" data-again>再抽一次</button>
      </div>`;
  }
  function draw(){
    const s = pick(); if(!s) return;
    const c = $('#scard');
    if (reduce.matches) { fillCard(s); return; }
    c.classList.remove('turning'); void c.offsetWidth; c.classList.add('turning');
    setTimeout(()=>fillCard(s), 190);
    setTimeout(()=>c.classList.remove('turning'), 440);
  }
  $('#draw-btn').addEventListener('click', draw);
  $('#scard').addEventListener('click', e=>{
    if (e.target.closest('[data-copy]') && current) copyFirst(current);
    if (e.target.closest('[data-again]')) draw();
  });
  $('#draw-count').textContent = `收藏室裡目前有 ${SPELLS.length} 則咒語`;
  $('#hero-draw').addEventListener('click', ()=>{ setTimeout(draw, 350); });

  /* ---------- library ---------- */
  const ALL_TAGS = ['戀愛日常','吃醋與曖昧','關係試探','衝突與和解','劇情事件','平行世界','隨機挑戰'];
  SPELLS.forEach(s=>s.tags.forEach(t=>{ if(!ALL_TAGS.includes(t)) ALL_TAGS.push(t); }));
  const chosen = new Set();
  $('#chips').innerHTML = ALL_TAGS.map(t=>{
    const n = SPELLS.filter(s=>s.tags.includes(t)).length;
    return `<button class="chip" type="button" aria-pressed="false" data-tag="${esc(t)}">${esc(t)}<span class="n">${n}</span></button>`;
  }).join('');
  $('#chips').addEventListener('click', e=>{
    const b = e.target.closest('.chip'); if(!b) return;
    const t = b.dataset.tag;
    chosen.has(t) ? chosen.delete(t) : chosen.add(t);
    b.setAttribute('aria-pressed', chosen.has(t));
    renderLib();
  });
  $('#q').addEventListener('input', renderLib);
  $('#clear').addEventListener('click', ()=>{
    chosen.clear(); $('#q').value='';
    document.querySelectorAll('.chip').forEach(c=>c.setAttribute('aria-pressed','false'));
    renderLib();
  });
  function renderLib(){
    const q = $('#q').value.trim().toLowerCase();
    const list = SPELLS.filter(s=>{
      const tagOk = !chosen.size || [...chosen].some(t=>s.tags.includes(t));
      const hay = [s.title, s.intro, s.note||'', ...s.tags, ...(s.keywords||[]), ...(s.parts||[]).map(p=>p.label)].join(' ').toLowerCase();
      return tagOk && (!q || hay.includes(q));
    });
    $('#clear').hidden = !(chosen.size || q);
    $('#result-n').textContent = (chosen.size || q) ? `找到 ${list.length} 則` : `共 ${list.length} 則`;
    $('#sgrid').innerHTML = list.length ? list.map(s=>`
      <a class="sitem" href="spells/${esc(s.id)}.html">
        <span class="pg">${no(s)}</span>
        <h3>${esc(s.title)}${sampleHtml(s)}</h3>
        <p>${esc(s.intro)}</p>
        <div class="tags">${tagsHtml(s)}</div>
      </a>`).join('')
      : `<div class="empty" style="grid-column:1/-1"><b>這一頁還是空白的。</b>換個關鍵字，或清除篩選再翻翻看。</div>`;
  }
  renderLib();

  /* ---------- 首頁：收藏室目錄（分類捷徑＋最新收錄） ---------- */
  function pickTag(t){
    chosen.clear(); chosen.add(t); $('#q').value='';
    document.querySelectorAll('#chips .chip').forEach(c=>c.setAttribute('aria-pressed', c.dataset.tag===t));
    renderLib();
  }
  $('#room-chips').innerHTML = ALL_TAGS.map(t=>{
    const n = SPELLS.filter(s=>s.tags.includes(t)).length;
    return n ? `<a class="chip" href="spells.html" data-room-tag="${esc(t)}">${esc(t)}<span class="n">${n}</span></a>` : '';
  }).join('');
  $('#room-chips').addEventListener('click', e=>{   // 先選好分類，再由全站路由切到收藏室
    const a = e.target.closest('[data-room-tag]'); if(a) pickTag(a.dataset.roomTag);
  });
  const byNew = SPELLS.slice().sort((a,b)=>String(b.created||'').localeCompare(String(a.created||'')));
  $('#room-new').innerHTML = byNew.slice(0,4).map(s=>`<li><a href="spells/${esc(s.id)}.html"><span class="pg">${no(s)}</span><span class="t">${esc(s.title)}</span><span class="i">${esc(s.intro)}</span></a></li>`).join('');

  const goRandom = ()=>{ const s=pick(); if(s) location.assign(spellUrl(s.id)); };
  $('#lib-random').addEventListener('click', goRandom);

  /* ---------- detail ---------- */
  let detail = null;
  function showDetail(s){
    detail = s;
    $('#d-pg').textContent = 'PAGE 002 / ' + no(s);
    $('#d-title').innerHTML = esc(s.title) + sampleHtml(s);
    $('#d-intro').textContent = s.intro;
    $('#d-tags').innerHTML = tagsHtml(s);
    const parts = partsOf(s);
    $('#d-note').hidden = !s.note; $('#d-note').textContent = s.note || '';
    $('#d-parts').innerHTML = parts.length > 1
      ? parts.map((p,i)=>`<section class="part"><div class="part-head"><b><span class="no">PART ${String(i+1).padStart(2,'0')} / ${String(parts.length).padStart(2,'0')}</span>${esc(p.label)}</b><button class="btn quiet sm" type="button" data-part="${i}">複製這一回</button></div><div class="incant">${esc(p.text)}</div></section>`).join('')
      : `<div class="incant">${esc(parts[0].text)}</div>`;
    $('#d-copy').hidden = parts.length > 1;
    $('#d-dates').innerHTML = `建立　${fmtDate(s.created)}<br>更新　${fmtDate(s.updated)}`;
    document.title = s.title + '｜小咒語｜岔頁 OFF PAGE';
  }
  document.addEventListener('click', e=>{ const b=e.target.closest('[data-copy]'); if(b){ const el=document.getElementById(b.dataset.copy); if(el) copyText(el.textContent, '已複製 ♡'); } });
  $('#d-copy').addEventListener('click', ()=>{ if(detail){ copyText(partsOf(detail)[0].text, '已複製 ♡'); nudge(); } });
  $('#d-parts').addEventListener('click', e=>{ const b=e.target.closest('[data-part]'); if(b && detail){ copyText(partsOf(detail)[+b.dataset.part].text, `已複製第 ${+b.dataset.part+1} 回 ♡`); nudge(); } });
  $('#d-next').addEventListener('click', ()=>{ lastId = detail ? detail.id : lastId; goRandom(); });
  $('#d-share').addEventListener('click', ()=>{
    const url = detail ? spellUrl(detail.id) : location.href;
    copyText(url, '分享連結已複製 ♡');
  });


  /* ---------- tools：小工具試玩 ---------- */
  const WIMG = {normal:'normal',smile:'smile',blush:'blush',closed:'closed',sleepy:'sleepy',photo:'photo',stand:'stand'};
  const LOOKS = [['normal','平常'],['smile','微笑'],['blush','臉紅'],['closed','閉眼'],['sleepy','打哈欠'],['photo','舉相機'],['stand','站著']];
  $('#sheet').innerHTML = LOOKS.map(([k,n])=>`<figure><div class="fr"><img src="assets/wen/${k}.webp" alt="聞止水・${n}" loading="lazy"></div><figcaption>${n}</figcaption></figure>`).join('');
  const TOUCH = {
    ear:[['戴很多年了。','normal'],['那個不能拔。','closed'],['……耳朵不要。','blush']],
    hand:[['嗯。','smile'],['手怎麼這麼冰。','normal'],['走吧。','stand'],['……沒要放。','blush'],['握著就好，不用講話。','closed']],
    cam:[['要拍嗎。站好。','photo'],['別動。……好了。','photo'],['光很好。','photo'],['妳剛剛笑了。拍到了。','photo'],['等洗出來再給妳。','photo']],
    body:[['怎麼了。','normal'],['我在。','normal'],['……要。','blush'],['妳今天很黏。','smile'],['沒有要走。','closed']]
  };
  const pad = n => String(n).padStart(2,'0');
  function timeLine(d){
    const m = d.getHours()*60 + d.getMinutes(), mon = d.getMonth()+1;
    if (m >= 90 && m < 510) return ['……睡了。','sleepy'];
    if (m < 90) return ['嗯。','closed'];
    if (m < 660) return d.getDay()===1 ? ['星期一。撐住。','normal'] : ['醒了？','normal'];
    if (m < 840) return ['吃。','normal'];
    if (m >= 1020 && m < 1230) return ['我在樓下。','stand'];
    if (mon===12 || mon<=2) return ['很冷。手給我。','normal'];
    return ['嗯。','normal'];
  }
  let holdUntil = 0, lastLine = {};
  function setWidget(line, look){
    const img = $('#w-img');
    if (!img) return;
    img.src = 'assets/wen/' + (WIMG[look]||'normal') + '.webp';
    $('#w-line').textContent = line;
  }
  function tick(){
    const d = new Date();
    $('#w-meta').textContent = `現在 ${pad(d.getHours())}:${pad(d.getMinutes())}`;
    if (Date.now() > holdUntil) { const [l,f] = timeLine(d); setWidget(l,f); }
  }
  tick(); setInterval(tick, 20000);
  let pokes = [];
  document.querySelectorAll('.touches [data-z]').forEach(b=>b.addEventListener('click', ()=>{
    const n = Date.now(); pokes = pokes.filter(t=>n-t<4000); pokes.push(n);
    holdUntil = n + 3200; setTimeout(tick, 3300);
    if (pokes.length >= 7) { pokes = []; setWidget(Math.random()<.5 ? '妳到底要戳幾下。' : '……講完了？','normal'); return; }
    const arr = TOUCH[b.dataset.z]; let p;
    do { p = arr[Math.floor(Math.random()*arr.length)]; } while (arr.length>1 && p[0]===lastLine[b.dataset.z]);
    lastLine[b.dataset.z] = p[0]; setWidget(p[0], p[1]);
  }));

  /* ---------- 戀人入住申請單 ---------- */
  (function(){
    const f = document.getElementById('of'); if (!f) return;
    const KEY = 'offpage-residency-draft';
    const $id = id => document.getElementById(id);
    const v = id => ($id(id) && $id(id).value || '').trim();
    const fields = [...f.querySelectorAll('input:not([type=checkbox]),textarea,select')];
    const boxes = [...f.querySelectorAll('input[type=checkbox]:not([disabled])')];
    const addons = [...f.querySelectorAll('#o-feats input:not([disabled])')];
    const shown = el => !el.closest('[hidden]');
    function syncCond(){
      const show = new Set(addons.filter(b=>b.checked && b.dataset.show).map(b=>b.dataset.show));
      f.querySelectorAll('[data-for]').forEach(l=>{
        if (l.dataset.for==='o-own') l.hidden = v('o-imgs') !== '我自己準備';
        else l.hidden = !show.has(l.dataset.for);
      });
      const rights = f.querySelector('[data-for2="o-rights"]'); rights.hidden = v('o-imgs') !== '我自己準備';
    }
    // 額外 Q 版表情的張數：價格和申請單都用同一個數字（1–20 張）
    const extraN = () => Math.max(1, Math.min(20, parseInt(v('o-extra')) || 1));
    function price(){
      let lo = 300, hi = 300;
      addons.forEach(b=>{ if(!b.checked || b.dataset.rush) return; let p=+b.dataset.price, m=+(b.dataset.max||b.dataset.price);
        if (b.value==='額外 Q 版表情'){ const n=extraN(); p*=n; m*=n; }
        lo+=p; hi+=m; });
      if (v('o-imgs').includes('6 張')){ lo+=300; hi+=300; }
      if (v('o-imgs').includes('12 張')){ lo+=500; hi+=500; }
      if (f.querySelector('[data-rush]').checked){ lo=Math.round(lo*1.5); hi=Math.round(hi*1.5); }
      return lo===hi ? `NT$${lo}` : `NT$${lo}–${hi}`;
    }
    function build(){
      const sec = (t, rows) => { rows = rows.filter(Boolean); return rows.length ? '■ '+t+'\n'+rows.join('\n') : ''; };
      const picked = addons.filter(b=>b.checked).map(b=> b.value==='額外 Q 版表情' ? `☑ 額外 Q 版表情 × ${extraN()}` : '☑ '+b.value);
      const own = v('o-imgs')==='我自己準備';
      return ['【戀人入住申請單】',
        sec('聯絡', [`稱呼：${v('o-name')||'（未填）'}`, `聯絡方式：${v('o-contact')||'（未填）'}`]),
        sec('角色', [`角色名：${v('o-char')||'（未填）'}`, v('o-source')&&`出處：${v('o-source')}`, v('o-basic')&&`性別／年齡／職業：${v('o-basic')}`,
          `個性與說話方式：${v('o-persona')||'（未填）'}`, v('o-rel')&&`關係：${v('o-rel')}`, v('o-callme')&&`她怎麼叫我：${v('o-callme')}`,
          `確認是角色、不是真人：${$id('o-real').checked?'是':'（未確認）'}`, $id('o-oc').checked&&'別人家的角色：已取得親媽同意']),
        sec('圖片', [`準備方式：${v('o-imgs')}`, own&&`去背 PNG：${v('o-own')}`, own&&`使用權：${$id('o-rights').checked?'已確認':'（未確認）'}`]),
        sec('方案', ['☑ 基本入住費 NT$300', ...picked]),
        sec('設定', [shown($id('o-city'))&&v('o-city')&&`天氣城市：${v('o-city')}`, shown($id('o-diary'))&&v('o-diary')&&`角色日記：${v('o-diary')}`,
          v('o-bday')&&`我的生日：${v('o-bday')}`, v('o-met')&&`相遇日：${v('o-met')}`, `配色：${v('o-pal')}`, `聊天入口：${v('o-chat')}`]),
        sec('其他', [`可放作品集：${$id('o-folio').checked?'可以':'不要'}`, v('o-more')]),
        `預估金額：${price()}（以確認後報價為準）`,
      ].filter(Boolean).join('\n\n');
    }
    function save(){ const d={}; fields.forEach(el=>d[el.id]=el.value); boxes.forEach(b=>d['ck:'+(b.id||b.value)]=b.checked);
      try{ localStorage.setItem(KEY, JSON.stringify(d)); }catch(e){} }
    function load(){ let d=null; try{ d=JSON.parse(localStorage.getItem(KEY)||'null'); }catch(e){} if(!d) return;
      fields.forEach(el=>{ if(d[el.id]!=null) el.value=d[el.id]; }); boxes.forEach(b=>{ const k='ck:'+(b.id||b.value); if(k in d) b.checked=d[k]; }); }
    function render(){ syncCond(); $id('o-total').textContent = price(); $id('o-preview').textContent = build(); }
    f.addEventListener('input', ()=>{ render(); save(); });
    f.addEventListener('change', ()=>{ render(); save(); });
    f.addEventListener('submit', e=>{
      e.preventDefault();
      const err = $id('o-err');
      const miss = [['o-name','怎麼稱呼你'],['o-contact','聯絡方式'],['o-char','角色名'],['o-persona','個性與說話方式']].filter(([id])=>!v(id)).map(x=>x[1]);
      if (!$id('o-real').checked) miss.push('確認是角色不是真人');
      if (v('o-imgs')==='我自己準備' && !$id('o-rights').checked) miss.push('圖片使用權確認');
      if (miss.length){ err.textContent='還差：'+miss.join('、')+'。'; err.hidden=false; return; }
      err.hidden=true; copyText(build(), '已複製申請單 ♡ 到 Threads 私訊貼給我');
    });
    $id('o-reset').addEventListener('click', ()=>{ f.reset(); try{ localStorage.removeItem(KEY); }catch(e){} $id('o-err').hidden=true; render(); });
    document.querySelectorAll('[data-jump]').forEach(a=>a.addEventListener('click', e=>{ e.preventDefault(); $id(a.dataset.jump).scrollIntoView({behavior:'smooth'}); }));
    load(); render();
  })();

  /* ---------- tools：小工具分頁，一次只顯示一個工具 ---------- */
  function selectTool(anchor){
    const panels = [...document.querySelectorAll('.tool-panel')];
    if (!panels.length) return;
    const target = anchor && document.getElementById(anchor);
    const inPanel = target && target.closest('.tool-panel');
    // 錨點在某個工具裡就切到那個工具；沒有指定錨點時回到第一個
    const key = inPanel ? inPanel.dataset.tool : (anchor ? null : panels[0].dataset.tool);
    if (!key) return;
    panels.forEach(p => { p.hidden = p.dataset.tool !== key; });
    document.querySelectorAll('.shelf a[data-tool]').forEach(a => a.setAttribute('aria-selected', a.dataset.tool === key ? 'true' : 'false'));
  }

  /* ---------- router：每一頁都有自己的網址（舊的 #tools、#spell-xxx 連結也照樣能用） ---------- */
  const views = [...document.querySelectorAll('.view')];
  const PAGES = {home:'./', worlds:'worlds.html', spells:'spells.html', tools:'tools.html', order:'order.html', about:'about.html'};
  const TITLES = {home:'岔頁 OFF PAGE｜原創互動敘事、角色故事與小咒語', worlds:'世界觀收藏｜岔頁 OFF PAGE', spells:'小咒語收藏室｜岔頁 OFF PAGE', tools:'小工具｜角色主畫面小工具・上次什麼時候？｜岔頁 OFF PAGE', order:'戀人入住申請所｜岔頁 OFF PAGE', about:'關於岔頁｜岔頁 OFF PAGE', lost:'找不到這一頁｜岔頁 OFF PAGE'};
  const ON_SPELL_PAGE = document.documentElement.dataset.route === 'spell';
  const isRouteHash = h => !!PAGES[h] || h==='draw' || h==='lost' || h.startsWith('spell-');
  function resolve(href){
    const u = new URL(href, document.baseURI);
    if (u.origin !== SITE.origin || !u.pathname.startsWith(SITE.pathname)) return null;
    let rel, h;
    try { rel = decodeURIComponent(u.pathname.slice(SITE.pathname.length)); h = decodeURIComponent(u.hash.slice(1)); } catch(e){ return null; }
    const m = rel.match(/^spells\/(.+)\.html$/);
    if (m) return {name:'spell', spell:m[1]};
    if (rel === '' || rel === 'index.html') {
      if (h.startsWith('spell-')) return {name:'spell', spell:h.slice(6)};
      if (h === 'draw') return {name:'home', anchor:'draw'};
      if (PAGES[h] || h === 'lost') return {name:h};
      return {name:'home', anchor:h};
    }
    for (const k in PAGES) if (PAGES[k] === rel) return {name:k, anchor:h};
    return null;
  }
  const urlOf = r => r.name==='spell' ? spellUrl(r.spell)
    : r.name==='lost' ? location.href
    : new URL(PAGES[r.name], SITE).href + (r.anchor ? '#'+r.anchor : '');
  function scrollToAnchor(id, smooth){
    const el = id && document.getElementById(id);
    if (!el) return false;
    requestAnimationFrame(()=>el.scrollIntoView({behavior: smooth && !reduce.matches ? 'smooth' : 'auto'}));
    return true;
  }
  function show(r, smooth){
    let name = r.name;
    if (name === 'spell') {
      const s = SPELLS.find(x=>x.id===r.spell);
      if (s) showDetail(s); else name = 'lost';
    }
    if (!views.some(v=>v.dataset.view===name)) name = 'lost';
    if (name !== 'spell') document.title = TITLES[name] || TITLES.home;
    views.forEach(v=>{ v.hidden = v.dataset.view !== name; });
    const navKey = name==='spell' ? 'spells' : name==='order' ? 'tools' : name;
    document.querySelectorAll('[data-nav]').forEach(a=>{
      a.dataset.nav===navKey ? a.setAttribute('aria-current','page') : a.removeAttribute('aria-current');
    });
    if (name === 'tools') selectTool(r.anchor);
    // 切換工具時停在小工具架，讓切換的卡片和內容開頭一起出現
    const anchor = name === 'tools' && (r.anchor === 'tool-widget' || r.anchor === 'little-days') ? 'toolbox' : r.anchor;
    if (!scrollToAnchor(anchor, smooth)) window.scrollTo(0,0);
  }
  function go(r){
    // 小咒語頁是獨立的檔案，進出都整頁載入；其他頁面之間不重新載入
    if (r.name === 'spell' || ON_SPELL_PAGE) {
      const cur = resolve(location.href);
      if (cur && cur.name==='spell' && r.name==='spell' && cur.spell===r.spell) { window.scrollTo(0,0); return; }
      if (!(r.name==='spell' && !SPELLS.some(x=>x.id===r.spell))) { location.assign(urlOf(r)); return; }
    }
    const u = urlOf(r);
    if (u !== location.href) history.pushState(null, '', u);
    show(r, true);
  }
  document.addEventListener('click', e=>{
    if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    const a = e.target.closest('a[href]');
    if (!a || (a.target && a.target !== '_self') || a.hasAttribute('download')) return;
    const raw = a.getAttribute('href');
    if (raw.startsWith('#') && !isRouteHash(raw.slice(1))) {      // 頁內錨點，例如「跳到主要內容」
      const el = document.getElementById(raw.slice(1));
      if (el) { e.preventDefault(); scrollToAnchor(el.id, true); if (el.tabIndex >= 0 || el.hasAttribute('tabindex')) el.focus({preventScroll:true}); }
      return;
    }
    const r = resolve(a.href);
    if (!r) return;
    e.preventDefault();
    go(r);
  });
  addEventListener('popstate', ()=> show(resolve(location.href) || {name:'lost'}));
  addEventListener('hashchange', ()=>{
    const h = location.hash.slice(1);
    if (!isRouteHash(h)) { scrollToAnchor(h, true); return; }
    const r = resolve(location.href);
    if (r) { if (r.name==='spell' && !ON_SPELL_PAGE) { location.replace(spellUrl(r.spell)); return; } if (r.name!=='lost') history.replaceState(null,'',urlOf(r)); show(r); }
  });
  (function start(){
    const r = resolve(location.href) || {name: document.documentElement.dataset.route || 'home'};
    if (r.name === 'spell' && !ON_SPELL_PAGE && SPELLS.some(x=>x.id===r.spell)) { location.replace(spellUrl(r.spell)); return; }
    if (r.name !== 'lost' && r.name !== 'spell' && urlOf(r) !== location.href) history.replaceState(null, '', urlOf(r));
    show(r);
  })();
})();
