"""
Kod muharriri (CodeMirror) shabloni
"""

EDITOR_TMPL = """<!DOCTYPE html>
<html lang="uz"><head><meta charset="UTF-8">
<title>Muharrir — NAME</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/codemirror.min.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/theme/dracula.min.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/addon/hint/show-hint.min.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/addon/lint/lint.min.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/addon/dialog/dialog.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/codemirror.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/mode/htmlmixed/htmlmixed.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/mode/xml/xml.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/mode/css/css.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/mode/javascript/javascript.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/addon/edit/matchbrackets.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/addon/edit/closebrackets.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/addon/selection/active-line.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/addon/comment/comment.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/addon/hint/show-hint.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/addon/search/searchcursor.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/addon/dialog/dialog.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/addon/lint/lint.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jshint/2.13.6/jshint.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/addon/lint/javascript-lint.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/js-beautify/1.15.1/beautify.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/js-beautify/1.15.1/beautify-css.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/js-beautify/1.15.1/beautify-html.min.js"></script>
<style>
INSERTCSS
body{overflow:hidden;height:100vh;display:flex;flex-direction:column}
.eh{background:var(--surf);border-bottom:1px solid var(--brd);padding:9px 14px;
  display:flex;align-items:center;gap:9px;flex-shrink:0;flex-wrap:wrap}
.eh h1{font-size:.9rem;font-weight:700;color:#fff;margin-right:auto}
.crumb{font-size:.72rem;color:var(--mt);background:var(--surf);border-bottom:1px solid var(--brd);
  padding:5px 14px;flex-shrink:0}
.crumb b{color:var(--ac);font-weight:600}
.ebMain{display:flex;flex:1;overflow:hidden}
#sidebar{width:210px;flex-shrink:0;background:var(--surf);border-right:1px solid var(--brd);
  display:flex;flex-direction:column;overflow:hidden}
.sbhead{padding:8px 10px;display:flex;gap:6px;border-bottom:1px solid var(--brd);flex-wrap:wrap}
.sbhead button{flex:1;background:transparent;border:1px solid var(--brd);color:var(--mt);
  border-radius:6px;padding:4px;cursor:pointer;font-size:.72rem}
.sbhead button:hover{border-color:var(--ac);color:var(--ac)}
#fileTree{flex:1;overflow-y:auto;padding:6px 0}
.frow{display:flex;align-items:center;gap:6px;padding:5px 10px;font-size:.78rem;
  color:var(--tx);cursor:pointer;white-space:nowrap;border-left:2px solid transparent}
.frow:hover{background:rgba(124,111,255,.08)}
.frow.act{background:rgba(124,111,255,.14);border-left-color:var(--ac);color:#fff}
.frow.dragover{outline:1px dashed var(--ac);background:rgba(124,111,255,.18)}
.fic{font-size:.85rem}
#codePane{display:flex;flex-direction:column;flex:0 0 45%;border-right:1px solid var(--brd);min-width:220px}
.tabsBar{display:flex;background:var(--surf);border-bottom:1px solid var(--brd);overflow-x:auto;flex-shrink:0}
.ftab{display:flex;align-items:center;gap:8px;padding:7px 10px;font-size:.78rem;color:var(--mt);
  cursor:pointer;border-right:1px solid var(--brd);white-space:nowrap}
.ftab.act{color:#fff;background:rgba(124,111,255,.08);border-bottom:2px solid var(--ac)}
.ftabx{opacity:.6;padding:0 2px}
.ftabx:hover{opacity:1;color:var(--rd)}
.editWrap{flex:1;display:flex;overflow:hidden}
#cmHost{flex:1;overflow:hidden}
#cmHost2{flex:1;overflow:hidden;border-left:1px solid var(--brd);display:none}
#minimap{width:56px;flex-shrink:0;background:#0a0c14;border-left:1px solid var(--brd);cursor:pointer}
#cmHost .CodeMirror,#cmHost2 .CodeMirror{height:100%;font-size:13px;background:#0d0f18}
.CodeMirror-matchingbracket{color:#22d3a0 !important;font-weight:700;text-decoration:underline;text-decoration-color:#22d3a0}
.CodeMirror-nonmatchingbracket{color:#f05d5d !important;font-weight:700}
.CodeMirror-activeline-background{background:rgba(124,111,255,.06)}
.CodeMirror-hints{background:#161929;border:1px solid #252d45;color:#d4daf0;
  font-family:'Consolas',monospace;font-size:12.5px;box-shadow:0 8px 24px rgba(0,0,0,.45);
  border-radius:8px;padding:4px 0;z-index:99999}
.CodeMirror-hint{padding:5px 12px;border-radius:0}
li.CodeMirror-hint-active{background:#7c6fff !important;color:#fff !important}
.cm-hint-snip{color:#22d3a0;font-size:10px;margin-left:10px;opacity:.85}
.CodeMirror-dialog{background:var(--surf);color:var(--tx);border-bottom:1px solid var(--brd)}
.CodeMirror-lint-marker-error{color:var(--rd)} .CodeMirror-lint-marker-warning{color:var(--yl)}
.CodeMirror-lint-tooltip{background:#161929;border:1px solid #252d45;color:var(--tx);
  border-radius:6px;font-size:12px;padding:4px 8px;z-index:999999}
#resizer{width:6px;cursor:col-resize;background:var(--brd);flex-shrink:0}
#resizer:hover{background:var(--ac)}
.pvcol{flex:1;display:flex;flex-direction:column;min-width:220px}
.devbar{display:flex;align-items:center;gap:6px;padding:7px 12px;background:var(--surf);
  border-bottom:1px solid var(--brd);font-size:.76rem;flex-shrink:0;flex-wrap:wrap}
.devbar button{background:transparent;border:1px solid var(--brd);color:var(--mt);
  border-radius:6px;padding:4px 9px;cursor:pointer;font-size:.74rem}
.devbar button:hover,.devbar button.on{border-color:var(--ac);color:var(--ac)}
.pvwrap{flex:1;display:flex;align-items:center;justify-content:center;overflow:auto;background:#05060a}
.pvwrap iframe{border:none}
.pvwrap.desktop iframe{width:100%;height:100%}
.pvwrap.tablet iframe{width:768px;height:1024px;max-width:94%;max-height:94%;
  border:10px solid #2b2f3a;border-radius:16px;background:#fff}
.pvwrap.mobile iframe{width:375px;height:667px;max-width:90%;max-height:94%;
  border:10px solid #2b2f3a;border-radius:26px;background:#fff}
.khint{font-size:.68rem;color:var(--mt);cursor:help}
#ctxMenu{position:fixed;display:none;background:#161929;border:1px solid #252d45;border-radius:8px;
  padding:4px 0;z-index:999999;min-width:180px;box-shadow:0 8px 24px rgba(0,0,0,.5)}
#ctxMenu div{padding:7px 14px;font-size:.8rem;color:var(--tx);cursor:pointer}
#ctxMenu div:hover{background:rgba(124,111,255,.15)}
.modalBg{position:fixed;inset:0;background:rgba(0,0,0,.55);display:none;
  align-items:flex-start;justify-content:center;z-index:9999999;padding-top:8vh}
.modalBox{background:var(--card);border:1px solid var(--brd);border-radius:12px;
  width:92%;max-width:560px;max-height:78vh;display:flex;flex-direction:column;overflow:hidden}
.modalBox input[type=text]{width:100%;padding:10px 14px;background:var(--bg);border:none;
  border-bottom:1px solid var(--brd);color:var(--tx);font-size:.9rem;outline:none}
.modalList{overflow-y:auto;flex:1}
.modalRow{padding:9px 14px;font-size:.82rem;color:var(--tx);cursor:pointer;
  display:flex;justify-content:space-between;gap:8px}
.modalRow:hover,.modalRow.sel{background:rgba(124,111,255,.14)}
.modalRow small{color:var(--mt)}
#consolePanel{height:130px;flex-shrink:0;background:#05060a;border-top:1px solid var(--brd);
  overflow-y:auto;font-family:monospace;font-size:.74rem;display:none}
#consolePanel .cline{padding:3px 10px;border-bottom:1px solid #12141f;white-space:pre-wrap;word-break:break-all}
#consolePanel .clog{color:var(--tx)} #consolePanel .cerr{color:var(--rd)} #consolePanel .cwarn{color:var(--yl)}
.histItem{padding:8px 12px;font-size:.78rem;border-bottom:1px solid var(--brd);display:flex;justify-content:space-between;gap:8px}
.histItem button{flex-shrink:0}
@media(max-width:768px){.layout{flex-direction:column}.sb{width:100%;height:auto;position:static}}
</style></head><body>
<div class="eh">
  <h1>✏️ NAME</h1>
  <span class="khint" id="autosaveInd" title="Avtosaqlash holati">💾 —</span>
  <button class="btn bp bsm" onclick="runCode()" title="Ctrl+Enter">▶ Run</button>
  <button class="btn bg bsm" onclick="saveActive()" title="Ctrl+S">💾 Saqlash</button>
  <button class="btn bgh bsm" onclick="formatActive()" title="Shift+Alt+F">🧹 Formatlash</button>
  <label class="khint" style="cursor:pointer"><input type="checkbox" id="fmtOnSave" style="width:auto;vertical-align:middle"> Saqlashda formatlash</label>
  <button class="btn bgh bsm" onclick="openQuickOpen()" title="Ctrl+P">📂 Quick Open</button>
  <button class="btn bgh bsm" onclick="openGlobalSearch()" title="Ctrl+Shift+F">🔍 Global qidiruv</button>
  <button class="btn bgh bsm" onclick="toggleSplit()">⊞ Split</button>
  <button class="btn bgh bsm" onclick="toggleConsole()">🖥 Konsol</button>
  <button class="btn bgh bsm" onclick="openSnippets()">✨ Snippetlar</button>
  <button class="btn bgh bsm" onclick="openHistory()">🕘 Tarix</button>
  <button class="btn bgh bsm" onclick="openBackendPanel()">🐍 Backend</button>
  <button class="btn bgh bsm" onclick="openHelpPanel()">❓ Yordam</button>
  <button class="btn bgh bsm" onclick="openChatPanel()">💬 Chat</button>
  <button class="btn bgh bsm" onclick="openTodoPanel()">🎯 TODO</button>
  <button class="btn bgh bsm" onclick="openComponentsPanel()">🧩 Komponent</button>
  <button class="btn bgh bsm" onclick="openColorPicker()">📐 Rang</button>
  <button class="btn bgh bsm" onclick="openTerminal()">💻 Terminal</button>
  <button class="btn bgh bsm" onclick="generatePWA()">📱 PWA</button>
  <button class="btn bgh bsm" onclick="generateReadme()">📑 README</button>
  <a href="/projects/download/UUID" class="btn bgh bsm">⬇ ZIP</a>
  <span class="khint" title="Emmet: div.foo#bar, ul>li*3, div+p, (div>p)*2, a{Matn} kabi qisqartmalarni yozib Tab yoki Enter bosing&#10;CSS: w100%, h50vh, m10-20, p0, df, jcc, aic, fxd, tac kabi qisqartmalar ham qo'llab-quvvatlanadi&#10;Ctrl+Space — takliflar ro'yxati&#10;Ctrl+P — Quick Open&#10;Ctrl+Shift+F — global qidiruv&#10;Ctrl+S — saqlash&#10;Ctrl+Enter — ishga tushirish&#10;Ctrl+/ — izohga olish&#10;Shift+Alt+F — formatlash&#10;Alt+Click — qo'shimcha kursor (multi-cursor)&#10;O'ng tugma — fayl daraxtida yangi fayl/papka/nomini o'zgartirish/o'chirish&#10;Sudrab tashlash — faylni boshqa papkaga ko'chirish">⌨ Tugmalar</span>
  <a href="/projects" class="btn bgh bsm">← Loyihalar</a>
  <a href="/preview/UUID" target="_blank" class="btn bgh bsm">👁 To'liq</a>
</div>
<div class="crumb" id="breadcrumb">—</div>
<div class="ebMain" id="ebMain">
  <aside id="sidebar" oncontextmenu="event.preventDefault();contextTargetPath=null;openCtxMenu(event,null);">
    <div class="sbhead">
      <button onclick="contextTargetPath=null;ctxNewFile()">+📄 Fayl</button>
      <button onclick="contextTargetPath=null;ctxNewFolder()">+📁 Papka</button>
    </div>
    <div id="fileTree"></div>
  </aside>
  <div id="codePane">
    <div class="tabsBar" id="tabsBar"></div>
    <div class="editWrap">
      <div id="cmHost"></div>
      <div id="cmHost2"></div>
      <canvas id="minimap" width="56" height="600"></canvas>
    </div>
  </div>
  <div id="resizer"></div>
  <div class="pvcol">
    <div class="devbar">
      <button onclick="setDevice('desktop')" id="devDesktop">🖥 Desktop</button>
      <button onclick="setDevice('tablet')" id="devTablet">📱 Planshet</button>
      <button onclick="setDevice('mobile')" id="devMobile">📱 Telefon</button>
      <button onclick="toggleFullscreen()">⛶ Kattalashtirish</button>
      <span id="ps" style="margin-left:auto;color:var(--gr)">✓ Tayyor</span>
    </div>
    <div class="pvwrap desktop" id="pvwrap">
      <iframe id="pf" sandbox="allow-scripts allow-same-origin allow-forms allow-popups"></iframe>
    </div>
    <div id="consolePanel"></div>
  </div>
</div>
<div id="ctxMenu">
  <div onclick="ctxNewFile()">📄 Yangi fayl</div>
  <div onclick="ctxNewFolder()">📁 Yangi papka</div>
  <div onclick="ctxRename()">✏️ Nomini o'zgartirish</div>
  <div onclick="ctxDelete()">🗑 O'chirish</div>
</div>

<div class="modalBg" id="quickOpenBg"><div class="modalBox">
  <input type="text" id="quickOpenInput" placeholder="Fayl qidirish... (Ctrl+P)">
  <div class="modalList" id="quickOpenList"></div>
</div></div>

<div class="modalBg" id="globalSearchBg"><div class="modalBox" style="max-width:680px">
  <input type="text" id="gsQuery" placeholder="Barcha fayllarda qidirish...">
  <input type="text" id="gsReplace" placeholder="Almashtirish matni (ixtiyoriy)">
  <div class="fl" style="padding:8px 14px">
    <button class="btn bp bsm" onclick="runGlobalSearch()">🔍 Qidirish</button>
    <button class="btn br bsm" onclick="runGlobalReplace()">🔁 Barchasini almashtirish</button>
    <button class="btn bgh bsm mla" onclick="closeModal('globalSearchBg')">Yopish</button>
  </div>
  <div class="modalList" id="gsResults"></div>
</div></div>

<div class="modalBg" id="helpBg"><div class="modalBox" style="max-width:720px;max-height:85vh">
  <div style="padding:12px 14px;border-bottom:1px solid var(--brd);display:flex;align-items:center;justify-content:space-between">
    <b style="color:#fff">❓ Emmet qisqartmalari va klaviatura tugmalari</b>
    <button class="btn bgh bsm" onclick="closeModal('helpBg')">✕</button>
  </div>
  <div class="modalList" style="padding:14px;overflow-y:auto;font-size:.82rem;line-height:1.7">

    <h3 style="color:var(--ac);margin-bottom:8px">⌨️ Klaviatura tugmalari</h3>
    <table style="width:100%;margin-bottom:18px"><tbody>
      <tr><td style="color:var(--gr);width:180px"><kbd>Tab</kbd></td><td>Emmet/Snippet kengaytirish</td></tr>
      <tr><td style="color:var(--gr)"><kbd>Ctrl+S</kbd></td><td>Saqlash</td></tr>
      <tr><td style="color:var(--gr)"><kbd>Ctrl+Enter</kbd></td><td>Ishga tushirish (Run)</td></tr>
      <tr><td style="color:var(--gr)"><kbd>Ctrl+Space</kbd></td><td>Takliflar ro'yxati (Autocomplete)</td></tr>
      <tr><td style="color:var(--gr)"><kbd>Ctrl+P</kbd></td><td>Quick Open — fayl qidirish</td></tr>
      <tr><td style="color:var(--gr)"><kbd>Ctrl+Shift+F</kbd></td><td>Global qidiruv / almashtirish</td></tr>
      <tr><td style="color:var(--gr)"><kbd>Ctrl+/</kbd></td><td>Izohga olish / izohdan chiqarish</td></tr>
      <tr><td style="color:var(--gr)"><kbd>Shift+Alt+F</kbd></td><td>Kodni formatlash (beautify)</td></tr>
      <tr><td style="color:var(--gr)"><kbd>Alt+Click</kbd></td><td>Ko'p kursor (multi-cursor)</td></tr>
    </tbody></table>

    <h3 style="color:var(--ac);margin-bottom:8px">🌐 HTML Emmet qisqartmalari</h3>
    <p style="color:var(--mt);margin-bottom:8px">Qisqartmani yozib <kbd>Tab</kbd> yoki <kbd>Enter</kbd> bosing:</p>
    <table style="width:100%;margin-bottom:18px"><tbody>
      <tr><td style="color:var(--yl);width:200px"><code>!</code></td><td>HTML5 to'liq shablon (boilerplate)</td></tr>
      <tr><td style="color:var(--yl)"><code>div.box#main</code></td><td>&lt;div class="box" id="main"&gt;&lt;/div&gt;</td></tr>
      <tr><td style="color:var(--yl)"><code>ul>li*5</code></td><td>ul ichida 5 ta li elementi</td></tr>
      <tr><td style="color:var(--yl)"><code>nav>ul>li*4>a</code></td><td>Navigatsiya tuzilmasi</td></tr>
      <tr><td style="color:var(--yl)"><code>div+p+span</code></td><td>Bir xil darajada 3 ta element</td></tr>
      <tr><td style="color:var(--yl)"><code>(div>p)*3</code></td><td>Guruhni 3 marta takrorlash</td></tr>
      <tr><td style="color:var(--yl)"><code>a[href=#]{Havola}</code></td><td>Atributli va matnli element</td></tr>
      <tr><td style="color:var(--yl)"><code>div.item$*4</code></td><td>item1, item2, item3, item4 klasslar</td></tr>
      <tr><td style="color:var(--yl)"><code>lorem</code> / <code>lorem30</code></td><td>Lorem ipsum matn (30 so'z)</td></tr>
      <tr><td style="color:var(--yl)"><code>img</code></td><td>&lt;img src="" alt=""&gt;</td></tr>
      <tr><td style="color:var(--yl)"><code>input</code></td><td>&lt;input type="text"&gt;</td></tr>
      <tr><td style="color:var(--yl)"><code>link</code></td><td>&lt;link rel="stylesheet" href=""&gt;</td></tr>
      <tr><td style="color:var(--yl)"><code>html5</code> / <code>com</code></td><td>HTML5 shablon / izoh bloki</td></tr>
    </tbody></table>

    <h3 style="color:var(--ac);margin-bottom:8px">🎨 CSS Emmet qisqartmalari</h3>
    <p style="color:var(--mt);margin-bottom:8px">CSS faylda qisqartmani yozib <kbd>Tab</kbd> bosing:</p>
    <table style="width:100%;margin-bottom:18px"><tbody>
      <tr><td style="color:var(--yl);width:200px"><code>w100%</code></td><td>width: 100%;</td></tr>
      <tr><td style="color:var(--yl)"><code>h50vh</code></td><td>height: 50vh;</td></tr>
      <tr><td style="color:var(--yl)"><code>m10</code> / <code>m10-20</code></td><td>margin: 10px; / margin: 10px 20px;</td></tr>
      <tr><td style="color:var(--yl)"><code>p0</code></td><td>padding: 0;</td></tr>
      <tr><td style="color:var(--yl)"><code>mt15</code> / <code>mb20</code></td><td>margin-top: 15px; / margin-bottom: 20px;</td></tr>
      <tr><td style="color:var(--yl)"><code>fs16</code></td><td>font-size: 16px;</td></tr>
      <tr><td style="color:var(--yl)"><code>fw700</code></td><td>font-weight: 700;</td></tr>
      <tr><td style="color:var(--yl)"><code>lh1.5</code></td><td>line-height: 1.5;</td></tr>
      <tr><td style="color:var(--yl)"><code>df</code> / <code>flex</code></td><td>display: flex;</td></tr>
      <tr><td style="color:var(--yl)"><code>dg</code> / <code>grid</code></td><td>display: grid;</td></tr>
      <tr><td style="color:var(--yl)"><code>jcc</code></td><td>justify-content: center;</td></tr>
      <tr><td style="color:var(--yl)"><code>aic</code></td><td>align-items: center;</td></tr>
      <tr><td style="color:var(--yl)"><code>fxd</code> / <code>fxdc</code></td><td>flex-direction: column;</td></tr>
      <tr><td style="color:var(--yl)"><code>fxww</code></td><td>flex-wrap: wrap;</td></tr>
      <tr><td style="color:var(--yl)"><code>center</code></td><td>display:flex; align-items:center; justify-content:center;</td></tr>
      <tr><td style="color:var(--yl)"><code>tac</code></td><td>text-align: center;</td></tr>
      <tr><td style="color:var(--yl)"><code>brr</code></td><td>border-radius:;</td></tr>
      <tr><td style="color:var(--yl)"><code>op</code></td><td>opacity:;</td></tr>
      <tr><td style="color:var(--yl)"><code>cur</code></td><td>cursor: pointer;</td></tr>
      <tr><td style="color:var(--yl)"><code>trs</code></td><td>transition:;</td></tr>
    </tbody></table>

    <h3 style="color:var(--ac);margin-bottom:8px">📜 JavaScript Snippet qisqartmalari</h3>
    <table style="width:100%;margin-bottom:18px"><tbody>
      <tr><td style="color:var(--yl);width:200px"><code>fn</code></td><td>function nomi() { }</td></tr>
      <tr><td style="color:var(--yl)"><code>af</code> / <code>anfn</code></td><td>() => { } (arrow function)</td></tr>
      <tr><td style="color:var(--yl)"><code>cl</code> / <code>clg</code></td><td>console.log();</td></tr>
      <tr><td style="color:var(--yl)"><code>ce</code></td><td>console.error();</td></tr>
      <tr><td style="color:var(--yl)"><code>fori</code></td><td>for (let i = 0; i < .length; i++)</td></tr>
      <tr><td style="color:var(--yl)"><code>forof</code></td><td>for (const item of ...)</td></tr>
      <tr><td style="color:var(--yl)"><code>fe</code></td><td>.forEach(item => { })</td></tr>
      <tr><td style="color:var(--yl)"><code>asf</code></td><td>async function() { }</td></tr>
      <tr><td style="color:var(--yl)"><code>awt</code></td><td>await ...;</td></tr>
      <tr><td style="color:var(--yl)"><code>qs</code></td><td>document.querySelector('');</td></tr>
      <tr><td style="color:var(--yl)"><code>qsa</code></td><td>document.querySelectorAll('');</td></tr>
      <tr><td style="color:var(--yl)"><code>addE</code></td><td>addEventListener('', () => { });</td></tr>
      <tr><td style="color:var(--yl)"><code>setT</code> / <code>sto</code></td><td>setTimeout(() => { }, 1000);</td></tr>
      <tr><td style="color:var(--yl)"><code>imp</code></td><td>import ... from '';</td></tr>
      <tr><td style="color:var(--yl)"><code>exp</code></td><td>export default ...;</td></tr>
      <tr><td style="color:var(--yl)"><code>ifj</code></td><td>if (...) { }</td></tr>
    </tbody></table>

    <h3 style="color:var(--ac);margin-bottom:8px">🖱️ Muharrir imkoniyatlari</h3>
    <table style="width:100%"><tbody>
      <tr><td style="color:var(--gr);width:200px">Fayl daraxti</td><td>O'ng tugma — yangi fayl/papka, nom o'zgartirish, o'chirish</td></tr>
      <tr><td style="color:var(--gr)">Sudrab tashlash</td><td>Faylni boshqa papkaga ko'chirish (drag & drop)</td></tr>
      <tr><td style="color:var(--gr)">Split view</td><td>⊞ Split tugmasi — ikki panelda bir vaqtda ishlash</td></tr>
      <tr><td style="color:var(--gr)">Konsol</td><td>console.log() natijalarini ko'rish (🖥 Konsol)</td></tr>
      <tr><td style="color:var(--gr)">Snippetlar</td><td>Shaxsiy qisqartmalar yaratish (✨ Snippetlar)</td></tr>
      <tr><td style="color:var(--gr)">Tarix</td><td>Har saqlashda avtomatik snapshot — eski holatni tiklash</td></tr>
      <tr><td style="color:var(--gr)">Formatlash</td><td>Shift+Alt+F yoki "Saqlashda formatlash" checkbox</td></tr>
      <tr><td style="color:var(--gr)">Backend</td><td>Loyiha ichidagi Python serverless funksiyalar</td></tr>
    </tbody></table>

  </div>
</div></div>

<div class="modalBg" id="chatBg"><div class="modalBox" style="max-width:480px;height:70vh">
  <div style="padding:10px 14px;border-bottom:1px solid var(--brd);display:flex;align-items:center;justify-content:space-between">
    <b style="color:#fff">💬 Loyiha chati</b>
    <button class="btn bgh bsm" onclick="closeModal('chatBg')">✕</button></div>
  <div id="chatMessages" style="flex:1;overflow-y:auto;padding:10px;font-size:.82rem"></div>
  <div style="padding:8px 14px;border-top:1px solid var(--brd);display:flex;gap:6px">
    <input type="text" id="chatInput" placeholder="Xabar yozing..." style="flex:1;padding:7px 10px;background:var(--bg);border:1px solid var(--brd);border-radius:6px;color:var(--tx);font-size:.82rem" onkeydown="if(event.key==='Enter')sendChat()">
    <button class="btn bp bsm" onclick="sendChat()">↑</button>
  </div>
</div></div>

<div class="modalBg" id="todoBg"><div class="modalBox" style="max-width:500px">
  <div style="padding:10px 14px;border-bottom:1px solid var(--brd);display:flex;align-items:center;justify-content:space-between">
    <b style="color:#fff">🎯 TODO / Vazifalar</b>
    <button class="btn bgh bsm" onclick="closeModal('todoBg')">✕</button></div>
  <div style="padding:10px 14px;display:flex;gap:6px">
    <input type="text" id="todoInput" placeholder="Yangi vazifa..." style="flex:1;padding:7px 10px;background:var(--bg);border:1px solid var(--brd);border-radius:6px;color:var(--tx);font-size:.82rem" onkeydown="if(event.key==='Enter')addTodo()">
    <select id="todoPriority" style="padding:5px;background:var(--bg);border:1px solid var(--brd);border-radius:6px;color:var(--tx);font-size:.78rem"><option value="normal">Normal</option><option value="high">Yuqori</option><option value="low">Past</option></select>
    <button class="btn bp bsm" onclick="addTodo()">+</button>
  </div>
  <div class="modalList" id="todoList" style="max-height:50vh;overflow-y:auto"></div>
</div></div>

<div class="modalBg" id="compBg"><div class="modalBox" style="max-width:700px;max-height:80vh">
  <div style="padding:10px 14px;border-bottom:1px solid var(--brd);display:flex;align-items:center;justify-content:space-between">
    <b style="color:#fff">🧩 Komponent kutubxonasi</b>
    <button class="btn bgh bsm" onclick="closeModal('compBg')">✕</button></div>
  <div class="modalList" id="compList" style="overflow-y:auto"></div>
</div></div>

<div class="modalBg" id="colorBg"><div class="modalBox" style="max-width:420px">
  <div style="padding:10px 14px;border-bottom:1px solid var(--brd);display:flex;align-items:center;justify-content:space-between">
    <b style="color:#fff">📐 Color Picker</b>
    <button class="btn bgh bsm" onclick="closeModal('colorBg')">✕</button></div>
  <div style="padding:14px">
    <input type="color" id="colorPickerInput" value="#7c6fff" style="width:100%;height:40px;border:none;cursor:pointer;border-radius:6px">
    <div style="margin-top:8px;display:flex;gap:6px;align-items:center">
      <input type="text" id="colorHexVal" value="#7c6fff" style="flex:1;padding:6px 10px;background:var(--bg);border:1px solid var(--brd);border-radius:6px;color:var(--tx);font-family:monospace;font-size:.85rem">
      <button class="btn bp bsm" onclick="insertColor()">Qo'shish</button>
    </div>
    <div id="colorPalettes" style="margin-top:12px"></div>
  </div>
</div></div>

<div class="modalBg" id="termBg"><div class="modalBox" style="max-width:700px;height:70vh">
  <div style="padding:10px 14px;border-bottom:1px solid var(--brd);display:flex;align-items:center;justify-content:space-between">
    <b style="color:#fff">💻 Terminal</b>
    <button class="btn bgh bsm" onclick="closeModal('termBg')">✕</button></div>
  <div id="termOutput" style="flex:1;overflow-y:auto;padding:10px;font-family:monospace;font-size:.78rem;background:#05060a;color:var(--gr);white-space:pre-wrap"></div>
  <div style="padding:8px 14px;border-top:1px solid var(--brd);display:flex;gap:6px">
    <span style="color:var(--gr);font-family:monospace;font-size:.82rem">$</span>
    <input type="text" id="termInput" placeholder="Buyruq kiriting..." style="flex:1;padding:7px 10px;background:var(--bg);border:1px solid var(--brd);border-radius:6px;color:var(--tx);font-family:monospace;font-size:.82rem" onkeydown="if(event.key==='Enter')runTermCmd()">
    <button class="btn bp bsm" onclick="runTermCmd()">▶</button>
  </div>
</div></div>

<div class="modalBg" id="snippetsBg"><div class="modalBox">
  <div style="padding:12px 14px;border-bottom:1px solid var(--brd)"><b style="color:#fff">✨ Mening snippetlarim</b></div>
  <div style="padding:12px 14px">
    <div class="g g3">
      <select id="snpLang"><option value="h">HTML</option><option value="c">CSS</option><option value="j">JS</option></select>
      <input type="text" id="snpTrigger" placeholder="Trigger (masalan: mycard)">
      <button class="btn bp bsm" onclick="addSnippet()">+ Qo'shish</button>
    </div>
    <textarea id="snpBody" placeholder="Kod (kursor o'rni uchun § belgisidan foydalaning)" style="width:100%;min-height:70px;margin-top:8px;background:var(--bg);border:1px solid var(--brd);color:var(--tx);border-radius:7px;padding:8px"></textarea>
  </div>
  <div class="modalList" id="snpList"></div>
  <div style="padding:10px 14px"><button class="btn bgh bsm" onclick="closeModal('snippetsBg')">Yopish</button></div>
</div></div>

<div class="modalBg" id="backendBg"><div class="modalBox" style="max-width:640px">
  <div style="padding:12px 14px;border-bottom:1px solid var(--brd)"><b style="color:#fff">🐍 Backend route'lari</b></div>
  <div style="padding:12px 14px">
    <div class="g g3">
      <select id="beMethod"><option>GET</option><option>POST</option><option>PUT</option><option>DELETE</option></select>
      <input type="text" id="bePath" placeholder="Yo'l (masalan: hello)">
      <button class="btn bp bsm" onclick="addBackendRoute()">+ Qo'shish</button>
    </div>
    <textarea id="beCode" placeholder="Python kod. Kirish: request, query, body. Natija: result = ..." style="width:100%;min-height:90px;margin-top:8px;background:var(--bg);border:1px solid var(--brd);color:var(--tx);border-radius:7px;padding:8px;font-family:monospace"></textarea>
    <p class="khint mt">Chaqiruv manzili: <code>/api/run/UUID/&lt;yo'l&gt;</code> — kirish: <code>request</code>, <code>query</code>, <code>body</code>; natijani <code>result</code> o'zgaruvchisiga yozing.</p>
  </div>
  <div class="modalList" id="beList"></div>
  <div style="padding:10px 14px"><button class="btn bgh bsm" onclick="closeModal('backendBg')">Yopish</button></div>
</div></div>

<div class="modalBg" id="historyBg"><div class="modalBox">
  <div style="padding:12px 14px;border-bottom:1px solid var(--brd)"><b style="color:#fff" id="histTitle">🕘 Versiya tarixi</b></div>
  <div class="modalList" id="histList"></div>
  <div style="padding:10px 14px"><button class="btn bgh bsm" onclick="closeModal('historyBg')">Yopish</button></div>
</div></div>

<script>
function debounce(fn,ms){var t;return function(){clearTimeout(t);t=setTimeout(fn,ms);};}
function flash(msg,color){
  var el=document.getElementById('ps'); if(!el) return;
  el.textContent=msg; el.style.color='var(--'+color+')';
}
function closeModal(id){ document.getElementById(id).style.display='none'; }
var CSRF_TOKEN = "CSRFTOKEN";
function authFetch(url, opts){
  opts = opts || {};
  opts.headers = Object.assign({'X-CSRF-Token': CSRF_TOKEN}, opts.headers||{});
  return fetch(url, opts);
}

/* ══════════════════════════════════════════════════════════════════════
   EMMET MOTORI — HTML va CSS qisqartmalarini to'liq kodga aylantiradi
   ══════════════════════════════════════════════════════════════════════ */
var activeTab='h';
var CURSOR_MARK = '\\u0001';

var HTML_VOID_TAGS = ['area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'];
var HTML_TAG_WHITELIST = ['div','span','p','a','ul','ol','li','table','tr','td','th','thead','tbody','tfoot',
  'form','input','button','img','nav','section','article','header','footer','aside','h1','h2','h3','h4','h5','h6',
  'label','textarea','select','option','optgroup','i','b','strong','em','small','br','hr','iframe','video','audio',
  'canvas','svg','path','script','link','meta','style','title','head','body','html','main','figure','figcaption',
  'blockquote','code','pre','strike','u','sub','sup','dl','dt','dd','fieldset','legend','address','time','mark'];
var HTML_DEFAULT_ATTRS = {
  a: [['href','']],
  img: [['src',''],['alt','']],
  link: [['rel','stylesheet'],['href','']],
  input: [['type','text']],
  script: [['src','']]
};
var IMPLICIT_CHILD_TAG = {ul:'li', ol:'li', table:'tr', tbody:'tr', thead:'tr', tfoot:'tr', tr:'td', select:'option', optgroup:'option'};
var LOREM_WORDS = ('lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut '+
  'labore et dolore magna aliqua ut enim ad minim veniam quis nostrud exercitation ullamco laboris nisi ut '+
  'aliquip ex ea commodo consequat duis aute irure dolor in reprehenderit voluptate velit esse cillum '+
  'dolore eu fugiat nulla pariatur excepteur sint occaecat cupidatat non proident sunt culpa qui officia '+
  'deserunt mollit anim id est laborum').split(' ');

function generateLorem(n){
  var out = [];
  for (var i=0;i<n;i++) out.push(LOREM_WORDS[i % LOREM_WORDS.length]);
  var s = out.join(' ');
  return s.charAt(0).toUpperCase() + s.slice(1) + '.';
}

function substDollar(s, index){
  if (s == null) return s;
  return s.replace(/\$+/g, function(m){ return String(index).padStart(m.length,'0'); });
}

function EmmetState(str){ return { s: str, i: 0, len: str.length }; }
function emParseTop(st){ return emParseSiblings(st); }

function emParseSiblings(st){
  var nodes = [emParseChain(st)];
  while (st.s[st.i] === '+') {
    st.i++;
    nodes.push(emParseChain(st));
  }
  while (st.s[st.i] === '^') {
    while (st.s[st.i] === '^') st.i++;
    if (st.i < st.len && st.s[st.i] !== ')') {
      nodes.push(emParseChain(st));
      while (st.s[st.i] === '+') { st.i++; nodes.push(emParseChain(st)); }
    }
  }
  return nodes;
}

function emParseChain(st){
  var node = emParsePrimary(st);
  if (st.s[st.i] === '>') {
    st.i++;
    node.children = emParseSiblings(st);
  }
  return node;
}

function emParsePrimary(st){
  if (st.s[st.i] === '(') {
    st.i++;
    var items = emParseSiblings(st);
    if (st.s[st.i] === ')') st.i++;
    var mult = emParseMultiplier(st);
    return {type:'group', items: items, mult: mult};
  }
  return emParseElement(st);
}

function emParseMultiplier(st){
  if (st.s[st.i] === '*') {
    st.i++;
    var n = '';
    while (st.i<st.len && /[0-9]/.test(st.s[st.i])) { n += st.s[st.i]; st.i++; }
    return parseInt(n||'1',10);
  }
  return 1;
}

function emParseElement(st){
  var s = st.s, len = st.len;
  var name = '';
  while (st.i<len && /[a-zA-Z0-9:_-]/.test(s[st.i])) { name += s[st.i]; st.i++; }
  var implicitName = false;
  if (!name) { name = 'div'; implicitName = true; }
  var classes = [], id = '', attrs = [], text = null;
  while (st.i < len) {
    var c = s[st.i];
    if (c === '.') {
      st.i++; var cls='';
      while (st.i<len && /[a-zA-Z0-9_-]/.test(s[st.i])) { cls+=s[st.i]; st.i++; }
      classes.push(cls);
    } else if (c === '#') {
      st.i++; var idv='';
      while (st.i<len && /[a-zA-Z0-9_-]/.test(s[st.i])) { idv+=s[st.i]; st.i++; }
      id = idv;
    } else if (c === '[') {
      st.i++; var inner='';
      while (st.i<len && s[st.i] !== ']') { inner+=s[st.i]; st.i++; }
      st.i++;
      var parts = inner.match(/[^\s"']+|"[^"]*"|'[^']*'/g) || [];
      for (var k=0;k<parts.length;k++){
        var p = parts[k], eq = p.indexOf('=');
        if (eq === -1) attrs.push({key:p, val:'', hasEq:false});
        else {
          var val = p.slice(eq+1).replace(/^["']|["']$/g,'');
          attrs.push({key:p.slice(0,eq), val: val, hasEq:true});
        }
      }
    } else if (c === '{') {
      st.i++; var t=''; var depth=1;
      while (st.i<len && depth>0) {
        if (s[st.i]==='{') depth++;
        else if (s[st.i]==='}') { depth--; if(depth===0){st.i++;break;} }
        t += s[st.i]; st.i++;
      }
      text = t;
    } else break;
  }
  var mult = emParseMultiplier(st);
  return {type:'element', name:name, implicitName:implicitName, classes:classes, id:id, attrs:attrs, text:text, mult:mult, children:null};
}

function emRenderNodes(nodes, indent, index, ctx, parentName){
  var lines = [];
  for (var n=0;n<nodes.length;n++){
    lines = lines.concat(emRenderNode(nodes[n], indent, index, ctx, parentName));
  }
  return lines;
}

function emRenderNode(node, indent, inheritedIndex, ctx, parentName){
  var mult = node.mult || 1;
  var lines = [];
  for (var i=1;i<=mult;i++){
    var idx = mult>1 ? i : inheritedIndex;
    if (node.type === 'group') {
      lines = lines.concat(emRenderNodes(node.items, indent, idx, ctx, parentName));
    } else {
      lines = lines.concat(emRenderElement(node, indent, idx, ctx, parentName));
    }
  }
  return lines;
}

function emRenderElement(node, indent, index, ctx, parentName){
  var pad = '  '.repeat(indent);
  if (/^lorem[0-9]*$/i.test(node.name)) {
    var n = parseInt(node.name.replace(/^lorem/i,''),10) || 30;
    return [pad + generateLorem(n)];
  }
  var tagName = node.name;
  if (node.implicitName && parentName && IMPLICIT_CHILD_TAG[parentName]) {
    tagName = IMPLICIT_CHILD_TAG[parentName];
  }
  var classes = node.classes.map(function(c){ return substDollar(c,index); });
  var id = node.id ? substDollar(node.id,index) : '';
  var attrsOut = '';
  if (classes.length) attrsOut += ' class="'+classes.join(' ')+'"';
  if (id) attrsOut += ' id="'+id+'"';
  var defaults = HTML_DEFAULT_ATTRS[tagName] || [];
  var explicitKeys = {};
  for (var a=0;a<node.attrs.length;a++) explicitKeys[node.attrs[a].key]=1;
  for (var d=0;d<defaults.length;d++){
    var dk=defaults[d][0], dv=defaults[d][1];
    if (!explicitKeys[dk]) attrsOut += ' '+dk+'="'+dv+'"';
  }
  for (var a2=0;a2<node.attrs.length;a2++){
    var at = node.attrs[a2];
    if (!at.hasEq) attrsOut += ' '+at.key;
    else attrsOut += ' '+at.key+'="'+substDollar(at.val,index)+'"';
  }
  var isVoid = HTML_VOID_TAGS.indexOf(tagName.toLowerCase()) !== -1;
  if (isVoid) return [pad+'<'+tagName+attrsOut+'>'];
  var text = node.text != null ? substDollar(node.text,index) : null;
  var children = node.children;
  if (children && children.length) {
    var out = [pad+'<'+tagName+attrsOut+'>'];
    out = out.concat(emRenderNodes(children, indent+1, index, ctx, tagName));
    out.push(pad+'</'+tagName+'>');
    return out;
  }
  if (text != null) {
    return [pad+'<'+tagName+attrsOut+'>'+text+'</'+tagName+'>'];
  }
  if (!ctx.placed) {
    ctx.placed = true;
    return [pad+'<'+tagName+attrsOut+'>'+CURSOR_MARK+'</'+tagName+'>'];
  }
  return [pad+'<'+tagName+attrsOut+'></'+tagName+'>'];
}

var HTML5_BOILERPLATE = '<!DOCTYPE html>\\n<html lang="uz">\\n<head>\\n  <meta charset="UTF-8">\\n  <title>'+CURSOR_MARK+'</title>\\n</head>\\n<body>\\n  \\n</body>\\n</html>';

function finalizeEmmetText(text){
  var idx = text.indexOf(CURSOR_MARK);
  if (idx>=0) return {text: text.slice(0,idx)+text.slice(idx+CURSOR_MARK.length), cursorOffset: idx};
  return {text:text, cursorOffset:text.length};
}

function expandEmmetHTML(abbr){
  abbr = (abbr||'').trim();
  if (!abbr) return null;
  if (abbr === '!') return finalizeEmmetText(HTML5_BOILERPLATE);
  if (/^lorem[0-9]*$/i.test(abbr)) {
    var nn = parseInt(abbr.replace(/^lorem/i,''),10) || 30;
    var txt = generateLorem(nn);
    return {text: txt, cursorOffset: txt.length};
  }
  var hasSpecial = /[.#\[\]{}*+>^()]/.test(abbr);
  var bareWord = /^[a-zA-Z][a-zA-Z0-9]*$/.test(abbr);
  if (!hasSpecial && bareWord && HTML_TAG_WHITELIST.indexOf(abbr.toLowerCase())===-1) return null;
  try {
    var st = EmmetState(abbr);
    var nodes = emParseTop(st);
    if (st.i < st.len) return null;
    var ctx = {placed:false};
    var lines = emRenderNodes(nodes, 0, 1, ctx, null);
    var text = lines.join('\\n');
    return finalizeEmmetText(text);
  } catch(e){ return null; }
}

/* Emmet naqshi ekanini tez aniqlash — hintni yopish qarorlari uchun */
function looksLikeEmmet(word){
  return /[.#\[\]{}*+>^()]/.test(word) || word === '!' || /^lorem[0-9]*$/i.test(word);
}

var CSS_PROP_PREFIXES = {
  minw:'min-width', minh:'min-height', maxw:'max-width', maxh:'max-height',
  mw:'max-width', mh:'max-height',
  mt:'margin-top', mb:'margin-bottom', ml:'margin-left', mr:'margin-right',
  pt:'padding-top', pb:'padding-bottom', pl:'padding-left', pr:'padding-right',
  m:'margin', p:'padding', w:'width', h:'height',
  fs:'font-size', fw:'font-weight', lh:'line-height', z:'z-index',
  brr:'border-radius', op:'opacity', top:'top', left:'left', right:'right', bottom:'bottom'
};
var CSS_VALUE_KEYWORDS = {a:'auto', n:'none', i:'inherit', s:'solid', h:'hidden', b:'both'};
var CSS_UNITS = ['px','%','em','rem','vh','vw','vmin','vmax','pt','pc','in','cm','mm','ex','ch','fr','deg','s','ms'];

function emSplitCssToken(tok){
  var m = tok.match(/^(-?[0-9]*\.?[0-9]+)([a-zA-Z%]*)$/);
  if (!m) return tok;
  var num = m[1], unit = m[2];
  if (unit === '') return num + (num === '0' ? '' : 'px');
  if (CSS_UNITS.indexOf(unit) !== -1) return num + unit;
  var numPart = num + (num === '0' ? '' : 'px');
  var kw = CSS_VALUE_KEYWORDS[unit] || unit;
  return numPart + ' ' + kw;
}

function expandCssFuzzy(word){
  var keys = Object.keys(CSS_PROP_PREFIXES).sort(function(a,b){return b.length-a.length;});
  for (var k=0;k<keys.length;k++){
    var pre = keys[k];
    if (word.length > pre.length && word.indexOf(pre) === 0 && /^[0-9]/.test(word.slice(pre.length))) {
      var valuePart = word.slice(pre.length);
      var tokens = valuePart.split('-').map(emSplitCssToken);
      return CSS_PROP_PREFIXES[pre] + ': ' + tokens.join(' ') + ';';
    }
  }
  return null;
}

function emApplyResult(cmi, from, to, res){
  var line = cmi.getLine(from.line);
  var indentMatch = line.match(/^\s*/);
  var baseIndent = indentMatch ? indentMatch[0] : '';
  var parts = res.text.split('\\n');
  var text = parts.map(function(l,idx){ return idx===0 ? l : baseIndent+l; }).join('\\n');
  var before2 = res.text.slice(0, res.cursorOffset);
  var nlCount = (before2.match(/\\n/g)||[]).length;
  var newOffset = res.cursorOffset + baseIndent.length*nlCount;
  cmi.replaceRange(text, from, to);
  var startIdx = cmi.indexFromPos(from);
  var pos = cmi.posFromIndex(startIdx + newOffset);
  cmi.setCursor(pos);
}

function emExtractAbbrev(line, endCh){
  var i = endCh, braceDepth = 0, bracketDepth = 0;
  var allowed = /[a-zA-Z0-9._#\[\]{}*+>^()$=:"'%,!\/-]/;
  while (i > 0) {
    var ch = line[i-1];
    var stop = false;
    if (ch === '}') braceDepth++;
    else if (ch === '{') { if (braceDepth>0) braceDepth--; else stop = true; }
    else if (ch === ']') bracketDepth++;
    else if (ch === '[') { if (bracketDepth>0) bracketDepth--; else stop = true; }
    else if (braceDepth===0 && bracketDepth===0) {
      if (ch === ' ' || !allowed.test(ch)) stop = true;
    }
    if (stop) break;
    i--;
  }
  return line.slice(i, endCh);
}

var SNIPPETS = {
  h: { 'html5': '<!DOCTYPE html>\\n<html lang="uz">\\n<head>\\n  <meta charset="UTF-8">\\n  <title>§</title>\\n</head>\\n<body>\\n  §\\n</body>\\n</html>', 'com': '<!-- § -->' },
  c: {
    'col': 'color: §;', 'bg': 'background: §;', 'bgc': 'background-color: §;',
    'bgi': 'background-image: url(§);', 'w': 'width: §;', 'h': 'height: §;',
    'mw': 'max-width: §;', 'mh': 'max-height: §;', 'm': 'margin: §;', 'mt': 'margin-top: §;',
    'mb': 'margin-bottom: §;', 'ml': 'margin-left: §;', 'mr': 'margin-right: §;',
    'p': 'padding: §;', 'pt': 'padding-top: §;', 'pb': 'padding-bottom: §;',
    'd': 'display: §;', 'db': 'display: block;', 'di': 'display: inline-block;',
    'pos': 'position: §;', 'posa': 'position: absolute;', 'posr': 'position: relative;',
    'fs': 'font-size: §;', 'fw': 'font-weight: §;', 'ff': 'font-family: §;',
    'ta': 'text-align: §;', 'tac': 'text-align: center;', 'td': 'text-decoration: §;',
    'brd': 'border: §;', 'br': 'border-radius: §;', 'bs': 'box-shadow: §;',
    'bxsd': 'box-shadow: inset 0 0 10px §;',
    'op': 'opacity: §;', 'ov': 'overflow: §;', 'z': 'z-index: §;',
    'flex': 'display: flex;', 'df': 'display: flex;', 'dg': 'display: grid;',
    'center': 'display: flex;\\n  align-items: center;\\n  justify-content: center;',
    'jcc': 'justify-content: center;', 'aic': 'align-items: center;',
    'fxd': 'flex-direction: column;', 'fxdr': 'flex-direction: row;',
    'fxdc': 'flex-direction: column;', 'fxdw': 'flex-flow: row wrap;',
    'fxww': 'flex-wrap: wrap;',
    'grid': 'display: grid;', 'trs': 'transition: §;', 'cur': 'cursor: pointer;',
    'bg+': 'background: #fff url(§) 0 0 no-repeat;'
  },
  j: {
    'fn': 'function §() {\\n  \\n}', 'af': '(§) => {\\n  \\n}', 'anfn': '(§) => {\\n  \\n}',
    'cl': 'console.log(§);', 'clg': 'console.log(§);', 'ce': 'console.error(§);',
    'fori': 'for (let i = 0; i < §.length; i++) {\\n  \\n}',
    'forof': 'for (const item of §) {\\n  \\n}',
    'fe': '§.forEach(item => {\\n  \\n});',
    'imp': "import § from '';", 'exp': 'export default §;',
    'asf': 'async function §() {\\n  \\n}', 'awt': 'await §;',
    'setT': 'setTimeout(() => {\\n  §\\n}, 1000);', 'sto': 'setTimeout(() => {\\n  §\\n}, 1000);',
    'addE': "addEventListener('§', () => {\\n  \\n});",
    'qs': "document.querySelector('§');", 'qsa': "document.querySelectorAll('§');",
    'ifj': 'if (§) {\\n  \\n}'
  }
};

function insertSnippet(cmi, from, to, snip){
  var idx = snip.indexOf('§');
  var text = idx>=0 ? (snip.slice(0,idx)+snip.slice(idx+1)) : snip;
  cmi.replaceRange(text, from, to);
  if (idx>=0){
    var pre = text.slice(0, idx);
    var lines = pre.split('\\n');
    var line = from.line + lines.length - 1;
    var ch = lines.length===1 ? (from.ch + lines[0].length) : lines[lines.length-1].length;
    cmi.setCursor({line: line, ch: ch});
  }
}

function trySnippetExpand(cmi){
  var cur = cmi.getCursor();
  var line = cmi.getLine(cur.line);
  var before = line.slice(0, cur.ch);
  if (activeTab === 'h') {
    var abbr = emExtractAbbrev(line, cur.ch);
    if (abbr) {
      var res = expandEmmetHTML(abbr);
      if (res) {
        var from = {line: cur.line, ch: cur.ch - abbr.length};
        emApplyResult(cmi, from, cur, res);
        return true;
      }
    }
    var mh = before.match(/[a-zA-Z0-9-]+$/);
    if (mh && SNIPPETS.h[mh[0]]) {
      var fh = {line: cur.line, ch: cur.ch - mh[0].length};
      insertSnippet(cmi, fh, cur, SNIPPETS.h[mh[0]]);
      return true;
    }
    return false;
  }
  if (activeTab === 'c') {
    var mc = before.match(/[a-zA-Z0-9%.+-]+$/);
    if (mc) {
      var word = mc[0];
      var fc = {line: cur.line, ch: cur.ch - word.length};
      if (SNIPPETS.c[word]) { insertSnippet(cmi, fc, cur, SNIPPETS.c[word]); return true; }
      var fz = expandCssFuzzy(word);
      if (fz) {
        cmi.replaceRange(fz, fc, cur);
        cmi.setCursor({line: fc.line, ch: fc.ch + fz.length});
        return true;
      }
    }
    return false;
  }
  var dict = SNIPPETS[activeTab];
  if (!dict) return false;
  var m = before.match(/[a-zA-Z0-9-]+$/);
  if (!m) return false;
  var word2 = m[0];
  var snip = dict[word2];
  if (!snip) return false;
  var from2 = {line: cur.line, ch: cur.ch - word2.length};
  insertSnippet(cmi, from2, cur, snip);
  return true;
}

function customHint(cmi){
  var dict = SNIPPETS[activeTab] || {};
  var cur = cmi.getCursor();
  var line = cmi.getLine(cur.line);
  var before = line.slice(0, cur.ch);
  var m = before.match(/[a-zA-Z0-9-]+$/);
  var word = m ? m[0] : '';
  if (!word) return null;
  var from = {line: cur.line, ch: cur.ch - word.length};
  var to = cur;
  var list = [];
  Object.keys(dict).forEach(function(k){
    if (k.indexOf(word) === 0){
      (function(key){
        list.push({
          text: key,
          render: function(el){
            var preview = dict[key].replace('§','').split('\\n')[0];
            el.innerHTML = '<b>'+key+'</b><span class="cm-hint-snip">'+preview+'</span>';
          },
          hint: function(cx, data){ insertSnippet(cx, data.from, data.to, dict[key]); }
        });
      })(k);
    }
  });
  if (!list.length) return null;
  return {list: list, from: from, to: to};
}

/* ══════════════════════════════════════════════════════════════════════
   KO'P FAYLLI LOYIHA: fayl daraxti, tablar, resizer, qurilma preview,
   autosave, quick-open, global qidiruv, drag&drop, split, konsol, tarix
   ══════════════════════════════════════════════════════════════════════ */
var cm, cm2;
var docsCache = {};
var fileList = [];
var openTabs = [];
var activePath = null;
var activePath2 = null;
var expandedFolders = {};
var contextTargetPath = null;
var dirty = {};
var scheduleRun, scheduleAutosave;
var splitOn = false;
var consoleOn = false;
var userSnippets = [];
var draggedPath = null;

var IMAGE_EXT = /\.(png|jpe?g|gif|ico|webp)$/i;
var SVG_EXT = /\.svg$/i;

function modeForPath(path){
  if (SVG_EXT.test(path)) return 'xml';
  if (/\.html?$/i.test(path)) return 'htmlmixed';
  if (/\.css$/i.test(path)) return 'css';
  if (/\.js$/i.test(path)) return 'javascript';
  if (/\.json$/i.test(path)) return 'application/json';
  return 'htmlmixed';
}
function kindForPath(path){
  if (/\.html?$/i.test(path)) return 'h';
  if (/\.css$/i.test(path)) return 'c';
  return 'j';
}
function lintForPath(path){
  if (/\.js$/i.test(path)) return {options:{esversion:11, asi:true, browser:true}};
  return false;
}
function fileIcon(path){
  if (/\.html?$/i.test(path)) return '🌐';
  if (/\.css$/i.test(path)) return '🎨';
  if (/\.js$/i.test(path)) return '📜';
  if (/\.json$/i.test(path)) return '🔧';
  if (IMAGE_EXT.test(path) || SVG_EXT.test(path)) return '🖼';
  return '📄';
}
function getFileRecord(path){
  for (var i=0;i<fileList.length;i++) if (fileList[i].path===path) return fileList[i];
  return null;
}
function currentContent(path){
  if (docsCache[path]) return docsCache[path].getValue();
  var rec = getFileRecord(path);
  return rec ? (rec.content||'') : null;
}

function loadAll(){
  authFetch('/editor/fs/all/UUID').then(function(r){return r.json();}).then(function(d){
    fileList = d.files;
    renderTree();
    var entry = getFileRecord('index.html') || fileList.find(function(f){return !f.is_folder;});
    if (entry) openFile(entry.path);
  });
  authFetch('/editor/snippets').then(function(r){return r.json();}).then(function(d){
    userSnippets = d.snippets || [];
    userSnippets.forEach(function(s){
      if (!SNIPPETS[s.lang]) SNIPPETS[s.lang] = {};
      SNIPPETS[s.lang][s.trigger_key] = s.body;
    });
    renderSnippetList();
  }).catch(function(){});
}

function updateBreadcrumb(path){
  var el = document.getElementById('breadcrumb');
  if (!path){ el.innerHTML = '—'; return; }
  var parts = path.split('/');
  el.innerHTML = 'UUID_NAME &nbsp;›&nbsp; ' + parts.map(function(p,i){
    return i===parts.length-1 ? '<b>'+p+'</b>' : p;
  }).join(' / ');
}

function openFile(path, pane){
  var rec = getFileRecord(path);
  if (!rec || rec.is_folder) return;
  if (!docsCache[path]) docsCache[path] = new CodeMirror.Doc(rec.content||'', modeForPath(path));
  if (openTabs.indexOf(path)===-1) openTabs.push(path);
  if (pane === 2){
    activePath2 = path;
    if (cm2) cm2.swapDoc(docsCache[path]);
  } else {
    activePath = path;
    activeTab = kindForPath(path);
    cm.swapDoc(docsCache[path]);
    cm.setOption('mode', modeForPath(path));
    var lo = lintForPath(path);
    cm.setOption('lint', lo);
    updateBreadcrumb(path);
    scheduleRun();
    drawMinimap();
  }
  renderTabs();
  renderTree();
}

function closeTab(path){
  var idx = openTabs.indexOf(path);
  if (idx===-1) return;
  openTabs.splice(idx,1);
  if (activePath===path){
    var next = openTabs[idx] || openTabs[idx-1];
    if (next) openFile(next);
    else { activePath=null; cm.swapDoc(new CodeMirror.Doc('','htmlmixed')); updateBreadcrumb(null); }
  }
  renderTabs();
}

function renderTabs(){
  var bar = document.getElementById('tabsBar');
  bar.innerHTML = '';
  openTabs.forEach(function(p){
    var el = document.createElement('div');
    el.className = 'ftab' + (p===activePath?' act':'');
    el.onclick = function(){ openFile(p); };
    var label = document.createElement('span');
    label.textContent = fileIcon(p)+' '+p.split('/').pop()+(dirty[p]?' •':'');
    var xBtn = document.createElement('span');
    xBtn.className = 'ftabx'; xBtn.textContent = '×';
    xBtn.onclick = function(ev){ ev.stopPropagation(); closeTab(p); };
    el.appendChild(label); el.appendChild(xBtn);
    if (splitOn){
      var sp = document.createElement('span');
      sp.textContent = '⊞'; sp.title = 'O\\'ng panelda ochish';
      sp.style.marginLeft='4px'; sp.style.opacity='.6';
      sp.onclick = function(ev){ ev.stopPropagation(); openFile(p, 2); };
      el.appendChild(sp);
    }
    bar.appendChild(el);
  });
}

function doSave(path, silent){
  if (!path || !docsCache[path]) return;
  var content = docsCache[path].getValue();
  if (document.getElementById('fmtOnSave') && document.getElementById('fmtOnSave').checked){
    content = beautifyText(content, kindForPath(path));
    docsCache[path].setValue(content);
  }
  authFetch('/editor/fs/write',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({uuid:'UUID',path:path,content:content})
  }).then(function(r){return r.json();}).then(function(d){
    if (d.ok){
      var rec = getFileRecord(path); if(rec) rec.content=content;
      dirty[path]=false; renderTabs();
      var ind = document.getElementById('autosaveInd');
      var now = new Date(); var hh=('0'+now.getHours()).slice(-2), mm=('0'+now.getMinutes()).slice(-2), ss=('0'+now.getSeconds()).slice(-2);
      if (ind) ind.textContent = '💾 Saqlandi ' + hh+':'+mm+':'+ss;
      if (!silent) flash('✓ Saqlandi: '+path,'gr');
    } else if (!silent) flash('✗ Saqlashda xato','rd');
  }).catch(function(){ if(!silent) flash('✗ Tarmoq xatosi','rd'); });
}
function saveActive(){ doSave(activePath, false); }

function beautifyText(v, kind){
  try{
    if (kind==='h' && window.html_beautify) return html_beautify(v,{indent_size:2, wrap_line_length:0});
    if (kind==='c' && window.css_beautify) return css_beautify(v,{indent_size:2});
    if (window.js_beautify) return js_beautify(v,{indent_size:2});
  }catch(e){}
  return v;
}
function formatActive(){
  if (!activePath) return;
  var v = docsCache[activePath].getValue();
  var nv = beautifyText(v, activeTab);
  if (nv === v){ flash('⚠ Formatlash kutubxonasi yuklanmadi','yl'); return; }
  docsCache[activePath].setValue(nv);
  flash('🧹 Tartiblandi','gr'); scheduleRun();
}

function resolveRel(base, rel){
  if (/^https?:/i.test(rel)) return null;
  rel = rel.replace(/^\//,'');
  var baseDir = base.indexOf('/')>=0 ? base.slice(0,base.lastIndexOf('/')+1) : '';
  var parts = (baseDir+rel).split('/'); var out=[];
  parts.forEach(function(p){ if(p==='..') out.pop(); else if(p!=='.'&&p!=='') out.push(p); });
  return out.join('/');
}
function findEntry(){
  if (getFileRecord('index.html')) return 'index.html';
  var htmlFile = fileList.find(function(f){ return !f.is_folder && /\.html?$/i.test(f.path); });
  return htmlFile ? htmlFile.path : null;
}

var CONSOLE_BRIDGE = "<script>(function(){var _o=console.log,_e=console.error,_w=console.warn;"+
  "function fwd(type,args){try{parent.postMessage({__consoleFwd:true,ctype:type,msg:Array.prototype.slice.call(args).map(function(a){"+
  "try{return typeof a==='object'?JSON.stringify(a):String(a);}catch(e){return String(a);}}).join(' ')},'*');}catch(e){}}"+
  "console.log=function(){fwd('log',arguments);_o.apply(console,arguments);};"+
  "console.error=function(){fwd('error',arguments);_e.apply(console,arguments);};"+
  "console.warn=function(){fwd('warn',arguments);_w.apply(console,arguments);};"+
  "window.onerror=function(m){fwd('error',[m]);};})();<\/script>";

function buildPreviewHtml(){
  var entry = findEntry();
  if (!entry) return '<html><body style="font-family:sans-serif;padding:24px;color:#888">index.html topilmadi. Fayl daraxtida yarating.</body></html>';
  var html = currentContent(entry) || '';
  html = html.replace(/<link[^>]+href=["']([^"'>]+\.css)["'][^>]*>/gi, function(m, href){
    var rp = resolveRel(entry, href); if(!rp) return m;
    var c = currentContent(rp);
    return c!=null ? '<style>'+c+'</style>' : m;
  });
  html = html.replace(/<script[^>]+src=["']([^"'>]+\.js)["'][^>]*><\/script>/gi, function(m, src){
    var rp = resolveRel(entry, src); if(!rp) return m;
    var c = currentContent(rp);
    return c!=null ? '<script>'+c+'<\/script>' : m;
  });
  if (/<head[^>]*>/i.test(html)) html = html.replace(/<head([^>]*)>/i, '<head$1>'+CONSOLE_BRIDGE);
  else html = CONSOLE_BRIDGE + html;
  return html;
}
function runCode(){
  try{
    document.getElementById('pf').srcdoc = buildPreviewHtml();
    flash('✓ Yangilandi','gr');
  }catch(e){ flash('✗ Xato','rd'); }
}
window.addEventListener('message', function(ev){
  var d = ev.data;
  if (!d || !d.__consoleFwd) return;
  if (!consoleOn) return;
  var panel = document.getElementById('consolePanel');
  var line = document.createElement('div');
  line.className = 'cline c'+(d.ctype==='error'?'err':(d.ctype==='warn'?'warn':'log'));
  line.textContent = '['+d.ctype+'] '+d.msg;
  panel.appendChild(line);
  panel.scrollTop = panel.scrollHeight;
});
function toggleConsole(){
  consoleOn = !consoleOn;
  document.getElementById('consolePanel').style.display = consoleOn ? 'block':'none';
}

function buildTree(){
  var root = {name:'',path:'',is_folder:1,children:{}};
  fileList.slice().sort(function(a,b){return a.path.localeCompare(b.path);}).forEach(function(item){
    var parts = item.path.split('/');
    var node = root;
    for (var i=0;i<parts.length;i++){
      var name = parts[i]; var isLast = i===parts.length-1;
      var p = parts.slice(0,i+1).join('/');
      if (!node.children[p]) node.children[p] = {name:name, path:p, is_folder: isLast? item.is_folder:1, children:{}};
      node = node.children[p];
    }
  });
  return root;
}
function renderTree(){
  var root = buildTree();
  var host = document.getElementById('fileTree');
  host.innerHTML='';
  renderTreeNode(root, host, 0);
}
function moveFile(oldp, newp){
  if (oldp===newp) return;
  authFetch('/editor/fs/rename',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({uuid:'UUID',old_path:oldp,new_path:newp})
  }).then(function(r){return r.json();}).then(function(d){ if(d.ok) loadAll(); else flash('✗ Ko\\'chirishda xato','rd'); });
}
function renderTreeNode(node, host, depth){
  var keys = Object.keys(node.children).sort(function(a,b){
    var na=node.children[a], nb=node.children[b];
    if (na.is_folder!==nb.is_folder) return nb.is_folder-na.is_folder;
    return na.name.localeCompare(nb.name);
  });
  keys.forEach(function(k){
    var n = node.children[k];
    var row = document.createElement('div');
    row.className = 'frow'+(n.path===activePath?' act':'');
    row.style.paddingLeft = (10+depth*14)+'px';
    row.draggable = true;
    row.oncontextmenu = (function(nn){ return function(e){ e.preventDefault(); e.stopPropagation(); contextTargetPath=nn; openCtxMenu(e,nn); }; })(n);
    row.ondragstart = (function(nn){ return function(e){ draggedPath = nn.path; e.dataTransfer.effectAllowed='move'; }; })(n);
    row.ondragover = (function(nn){ return function(e){ if(nn.is_folder){ e.preventDefault(); row.classList.add('dragover'); } }; })(n);
    row.ondragleave = function(){ row.classList.remove('dragover'); };
    row.ondrop = (function(nn){ return function(e){
      e.preventDefault(); row.classList.remove('dragover');
      if (!draggedPath || !nn.is_folder) return;
      var name = draggedPath.split('/').pop();
      moveFile(draggedPath, (nn.path+'/'+name).replace(/\/+/g,'/'));
      draggedPath = null;
    }; })(n);
    if (n.is_folder){
      var expanded = !!expandedFolders[n.path];
      row.innerHTML = '<span class="fic">'+(expanded?'📂':'📁')+'</span><span>'+n.name+'</span>';
      row.onclick = (function(nn,exp){ return function(){ expandedFolders[nn.path]=!exp; renderTree(); }; })(n,expanded);
      host.appendChild(row);
      if (expanded) renderTreeNode(n, host, depth+1);
    } else {
      var isImg = IMAGE_EXT.test(n.path) || SVG_EXT.test(n.path);
      row.innerHTML = '<span class="fic">'+fileIcon(n.path)+'</span><span>'+n.name+(dirty[n.path]?' •':'')+'</span>';
      row.onclick = (function(nn){ return function(){ openFile(nn.path); }; })(n);
      host.appendChild(row);
    }
  });
}

function openCtxMenu(e, node){
  contextTargetPath = node;
  var menu = document.getElementById('ctxMenu');
  menu.style.left = e.pageX+'px'; menu.style.top = e.pageY+'px';
  menu.style.display='block';
}
document.addEventListener('click', function(){ document.getElementById('ctxMenu').style.display='none'; });

function ctxBaseDir(){
  if (!contextTargetPath) return '';
  if (contextTargetPath.is_folder) return contextTargetPath.path+'/';
  var idx = contextTargetPath.path.lastIndexOf('/');
  return idx>=0 ? contextTargetPath.path.slice(0,idx+1) : '';
}
function maybeAutoImport(path){
  var idx = getFileRecord('index.html');
  if (!idx) return;
  var isCss = /\.css$/i.test(path), isJs = /\.js$/i.test(path);
  if (!isCss && !isJs) return;
  if (!confirm((isCss?'CSS':'JS')+" faylini index.html ga avtomatik ulaymi? ("+path+")")) return;
  var html = idx.content || '';
  if (isCss){
    if (html.indexOf(path) === -1 && /<\/head>/i.test(html))
      html = html.replace(/<\/head>/i, '  <link rel="stylesheet" href="'+path+'">\\n</head>');
  } else {
    if (html.indexOf(path) === -1 && /<\/body>/i.test(html))
      html = html.replace(/<\/body>/i, '  <script src="'+path+'"><\/script>\\n</body>');
  }
  idx.content = html;
  if (docsCache['index.html']) docsCache['index.html'].setValue(html);
  authFetch('/editor/fs/write',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({uuid:'UUID',path:'index.html',content:html})}).then(function(){ scheduleRun(); });
}
function ctxNewFile(){
  var base = ctxBaseDir();
  var name = prompt('Yangi fayl nomi:', 'yangi.html');
  if (!name) return;
  var path = (base+name).replace(/\/+/g,'/').replace(/^\//,'');
  authFetch('/editor/fs/mkfile',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({uuid:'UUID',path:path,content:''})
  }).then(function(r){return r.json();}).then(function(d){
    if (d.ok){ fileList.push({path:path,is_folder:false,content:''}); renderTree(); openFile(path); maybeAutoImport(path); }
    else alert("Xato: fayl allaqachon mavjud bo'lishi mumkin");
  });
}
function ctxNewFolder(){
  var base = ctxBaseDir();
  var name = prompt('Yangi papka nomi:', 'papka');
  if (!name) return;
  var path = (base+name).replace(/\/+/g,'/').replace(/^\//,'');
  authFetch('/editor/fs/mkdir',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({uuid:'UUID',path:path})
  }).then(function(r){return r.json();}).then(function(d){
    if (d.ok){ fileList.push({path:path,is_folder:true,content:null}); expandedFolders[path]=true; renderTree(); }
    else alert("Xato: papka allaqachon mavjud bo'lishi mumkin");
  });
}
function ctxRename(){
  if (!contextTargetPath) return;
  var oldp = contextTargetPath.path;
  var name = prompt('Yangi nom:', oldp.split('/').pop());
  if (!name) return;
  var idx = oldp.lastIndexOf('/');
  var parent = idx>=0 ? oldp.slice(0,idx+1) : '';
  var newp = parent+name;
  moveFile(oldp, newp);
}
function ctxDelete(){
  if (!contextTargetPath) return;
  if (!confirm("O'chirishni tasdiqlaysizmi? "+contextTargetPath.path)) return;
  var p = contextTargetPath.path;
  authFetch('/editor/fs/delete',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({uuid:'UUID',path:p})
  }).then(function(r){return r.json();}).then(function(d){
    if (d.ok){ if (openTabs.indexOf(p)>=0) closeTab(p); loadAll(); }
  });
}

function setupResizer(){
  var resizer = document.getElementById('resizer');
  var codePane = document.getElementById('codePane');
  var dragging=false;
  resizer.addEventListener('mousedown', function(e){ dragging=true; document.body.style.cursor='col-resize'; e.preventDefault(); });
  window.addEventListener('mousemove', function(e){
    if (!dragging) return;
    var wrap = document.getElementById('ebMain').getBoundingClientRect();
    var sidebarW = document.getElementById('sidebar').offsetWidth;
    var x = e.clientX - wrap.left - sidebarW;
    var totalW = wrap.width - sidebarW - 6;
    var pct = Math.min(78, Math.max(18, (x/totalW)*100));
    codePane.style.flex = '0 0 '+pct+'%';
    cm.refresh(); if(cm2) cm2.refresh();
  });
  window.addEventListener('mouseup', function(){ if(dragging){dragging=false; document.body.style.cursor='';} });
}

function setDevice(mode){
  document.getElementById('pvwrap').className = 'pvwrap '+mode;
  ['devDesktop','devTablet','devMobile'].forEach(function(id){document.getElementById(id).classList.remove('on');});
  document.getElementById('dev'+mode.charAt(0).toUpperCase()+mode.slice(1)).classList.add('on');
}
function toggleFullscreen(){
  var wrap = document.getElementById('pvwrap');
  if (!document.fullscreenElement) { if (wrap.requestFullscreen) wrap.requestFullscreen(); }
  else { if (document.exitFullscreen) document.exitFullscreen(); }
}

/* ── Split-view: ikkinchi CodeMirror panel ────────────────────────────── */
function toggleSplit(){
  splitOn = !splitOn;
  var host2 = document.getElementById('cmHost2');
  host2.style.display = splitOn ? 'block' : 'none';
  if (splitOn && !cm2){
    cm2 = CodeMirror(host2, {value:'', mode:'htmlmixed', theme:'dracula', lineNumbers:true,
      lineWrapping:true, tabSize:2, indentUnit:2, matchBrackets:true, autoCloseBrackets:true, styleActiveLine:true,
      gutters:['CodeMirror-linenumbers','CodeMirror-lint-markers'],
      extraKeys: {
        'Ctrl-Space': function(cx){ CodeMirror.showHint(cx, customHint, {completeSingle:false}); },
        'Tab': function(cx){
          if (cx.state.completionActive){
            var w = cx.getRange({line:cx.getCursor().line,ch:0}, cx.getCursor());
            var m = w.match(/[a-zA-Z0-9._#\\[\\]{}*+>^()$=:"'%,!\\/-]+$/);
            if (m && looksLikeEmmet(m[0])){ cx.closeHint(); if (trySnippetExpand(cx)) return; }
            return CodeMirror.Pass;
          }
          if (trySnippetExpand(cx)) return;
          if (cx.somethingSelected()){ cx.execCommand('indentMore'); return; }
          cx.replaceSelection('  ');
        },
        'Enter': function(cx){
          if (cx.state.completionActive) return CodeMirror.Pass;
          if ((activeTab==='h'||activeTab==='c') && trySnippetExpand(cx)) return;
          return CodeMirror.Pass;
        },
        'Ctrl-S': function(){ saveActive(); return false; },
        'Cmd-S': function(){ saveActive(); return false; },
        'Ctrl-Enter': function(){ runCode(); },
        'Cmd-Enter': function(){ runCode(); },
        'Shift-Alt-F': function(){ formatActive(); },
        'Ctrl-/': 'toggleComment',
        'Cmd-/': 'toggleComment'
      }
    });
    cm2.on('inputRead', function(cx, change){
      if (change.text.length===1 && /[a-zA-Z]/.test(change.text[0])){
        var cur = cx.getCursor();
        var before = cx.getLine(cur.line).slice(0, cur.ch);
        var m = before.match(/[a-zA-Z0-9._#\\[\\]{}*+>^()$=:"'%,!\\/-]+$/);
        if (m && looksLikeEmmet(m[0])) return;
        CodeMirror.showHint(cx, customHint, {completeSingle:false});
      }
    });
  }
  renderTabs();
  setTimeout(function(){ cm.refresh(); if(cm2) cm2.refresh(); }, 50);
}

/* ── Mini-xarita (soddalashtirilgan kod xaritasi) ─────────────────────── */
function drawMinimap(){
  var canvas = document.getElementById('minimap');
  var ctx = canvas.getContext('2d');
  var h = document.getElementById('cmHost').clientHeight || 600;
  canvas.height = h;
  ctx.clearRect(0,0,canvas.width,canvas.height);
  ctx.fillStyle = '#0a0c14'; ctx.fillRect(0,0,canvas.width,canvas.height);
  if (!activePath || !docsCache[activePath]) return;
  var doc = docsCache[activePath];
  var lines = doc.getValue().split('\\n');
  var scale = Math.min(2, h / Math.max(1,lines.length));
  ctx.fillStyle = '#7c6fff88';
  lines.forEach(function(l,i){
    var y = i*scale;
    if (y>h) return;
    var w = Math.min(canvas.width-6, (l.length||0)*0.9);
    ctx.fillRect(3, y, w, Math.max(1,scale-0.4));
  });
  canvas.onclick = function(e){
    var rect = canvas.getBoundingClientRect();
    var frac = (e.clientY-rect.top)/rect.height;
    var target = Math.floor(frac*lines.length);
    cm.setCursor({line:target, ch:0});
    cm.scrollIntoView({line:target,ch:0}, 100);
  };
}

/* ══════════════════════════════════════════════════════════════════════
   QUICK OPEN (Ctrl+P) — fayllar orasida tez qidirib ochish
   ══════════════════════════════════════════════════════════════════════ */
var qoSelIndex = 0, qoFiltered = [];

function openQuickOpen(){
  var bg = document.getElementById('quickOpenBg');
  var inp = document.getElementById('quickOpenInput');
  bg.style.display = 'flex';
  inp.value = '';
  inp.focus();
  renderQuickOpenList('');
}
function renderQuickOpenList(q){
  var list = document.getElementById('quickOpenList');
  qoFiltered = fileList.filter(function(f){
    return !f.is_folder && (!q || f.path.toLowerCase().indexOf(q.toLowerCase())!==-1);
  }).sort(function(a,b){ return a.path.length - b.path.length; });
  qoSelIndex = 0;
  list.innerHTML = '';
  qoFiltered.forEach(function(f, i){
    var row = document.createElement('div');
    row.className = 'modalRow' + (i===0 ? ' sel' : '');
    row.innerHTML = '<span>'+fileIcon(f.path)+' '+f.path+'</span><small>'+(dirty[f.path]?'●':'')+'</small>';
    row.onclick = function(){ openFile(f.path); closeModal('quickOpenBg'); };
    list.appendChild(row);
  });
  if (!qoFiltered.length) list.innerHTML = '<div class="modalRow"><small>Hech narsa topilmadi</small></div>';
}
document.addEventListener('DOMContentLoaded', function(){
  var inp = document.getElementById('quickOpenInput');
  inp.addEventListener('input', function(){ renderQuickOpenList(inp.value); });
  inp.addEventListener('keydown', function(e){
    var rows = document.querySelectorAll('#quickOpenList .modalRow');
    if (e.key === 'ArrowDown'){ e.preventDefault(); qoSelIndex = Math.min(rows.length-1, qoSelIndex+1); }
    else if (e.key === 'ArrowUp'){ e.preventDefault(); qoSelIndex = Math.max(0, qoSelIndex-1); }
    else if (e.key === 'Enter'){ if (qoFiltered[qoSelIndex]){ openFile(qoFiltered[qoSelIndex].path); closeModal('quickOpenBg'); } return; }
    else if (e.key === 'Escape'){ closeModal('quickOpenBg'); return; }
    else return;
    rows.forEach(function(r,i){ r.classList.toggle('sel', i===qoSelIndex); });
    if (rows[qoSelIndex]) rows[qoSelIndex].scrollIntoView({block:'nearest'});
  });
  document.getElementById('quickOpenBg').addEventListener('click', function(e){
    if (e.target.id === 'quickOpenBg') closeModal('quickOpenBg');
  });
});

/* ══════════════════════════════════════════════════════════════════════
   GLOBAL QIDIRUV / ALMASHTIRISH — barcha loyiha fayllari ichidan
   ══════════════════════════════════════════════════════════════════════ */
function openGlobalSearch(){
  document.getElementById('globalSearchBg').style.display = 'flex';
  document.getElementById('gsQuery').focus();
  document.getElementById('gsResults').innerHTML = '';
}
function allFileContents(){
  var map = {};
  fileList.forEach(function(f){
    if (!f.is_folder) map[f.path] = docsCache[f.path] ? docsCache[f.path].getValue() : (f.content||'');
  });
  return map;
}
function runGlobalSearch(){
  var q = document.getElementById('gsQuery').value;
  var results = document.getElementById('gsResults');
  results.innerHTML = '';
  if (!q){ results.innerHTML = '<div class="modalRow"><small>So\\'z kiriting</small></div>'; return; }
  var contents = allFileContents();
  var totalHits = 0;
  Object.keys(contents).forEach(function(path){
    var lines = contents[path].split('\\n');
    lines.forEach(function(line, li){
      if (line.toLowerCase().indexOf(q.toLowerCase()) !== -1){
        totalHits++;
        var row = document.createElement('div');
        row.className = 'modalRow';
        row.innerHTML = '<span>'+fileIcon(path)+' '+path+':'+(li+1)+' — '+
          line.trim().slice(0,70).replace(/</g,'&lt;')+'</span>';
        row.onclick = (function(p,ln){ return function(){
          openFile(p); closeModal('globalSearchBg');
          setTimeout(function(){ cm.setCursor({line:ln,ch:0}); cm.scrollIntoView({line:ln,ch:0},100); }, 60);
        }; })(path, li);
        results.appendChild(row);
      }
    });
  });
  if (!totalHits) results.innerHTML = '<div class="modalRow"><small>Hech narsa topilmadi</small></div>';
}
function runGlobalReplace(){
  var q = document.getElementById('gsQuery').value;
  var rep = document.getElementById('gsReplace').value;
  if (!q) { flash('⚠ Qidiruv so\\'zi bosh','yl'); return; }
  if (!confirm("Barcha fayllarda \\""+q+"\\" ni \\""+rep+"\\" ga almashtirasizmi? Bekor qilib bo'lmaydi.")) return;
  var changed = 0;
  fileList.forEach(function(f){
    if (f.is_folder) return;
    var cur = docsCache[f.path] ? docsCache[f.path].getValue() : (f.content||'');
    if (cur.indexOf(q) === -1) return;
    var next = cur.split(q).join(rep);
    changed++;
    if (docsCache[f.path]) docsCache[f.path].setValue(next);
    f.content = next;
    authFetch('/editor/fs/write',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({uuid:'UUID',path:f.path,content:next})});
  });
  flash('✓ '+changed+' faylda almashtirildi','gr');
  closeModal('globalSearchBg');
  scheduleRun();
}

/* ══════════════════════════════════════════════════════════════════════
   FOYDALANUVCHI SNIPPETLARI (bazada saqlanadi)
   ══════════════════════════════════════════════════════════════════════ */
function openSnippets(){
  document.getElementById('snippetsBg').style.display = 'flex';
  renderSnippetList();
}
function renderSnippetList(){
  var list = document.getElementById('snpList');
  list.innerHTML = '';
  userSnippets.forEach(function(s){
    var row = document.createElement('div');
    row.className = 'modalRow';
    row.innerHTML = '<span>['+s.lang.toUpperCase()+'] '+s.trigger_key+'</span>'+
      '<button class="btn br bsm" data-id="'+s.id+'">🗑</button>';
    row.querySelector('button').onclick = function(){ delSnippet(s.id); };
    list.appendChild(row);
  });
  if (!userSnippets.length) list.innerHTML = '<div class="modalRow"><small>Hali snippet yoq</small></div>';
}
function addSnippet(){
  var lang = document.getElementById('snpLang').value;
  var trig = document.getElementById('snpTrigger').value.trim();
  var body = document.getElementById('snpBody').value;
  if (!trig || !body){ flash('⚠ Trigger va kod kiriting','yl'); return; }
  authFetch('/editor/snippets',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({lang:lang,trigger:trig,body:body})
  }).then(function(r){return r.json();}).then(function(d){
    if (d.ok){
      userSnippets.push({id:d.id, lang:lang, trigger_key:trig, body:body});
      if (!SNIPPETS[lang]) SNIPPETS[lang]={};
      SNIPPETS[lang][trig] = body;
      document.getElementById('snpTrigger').value=''; document.getElementById('snpBody').value='';
      renderSnippetList(); flash('✓ Snippet qo\\'shildi','gr');
    } else flash('✗ Xato: trigger allaqachon mavjud','rd');
  });
}
function delSnippet(id){
  authFetch('/editor/snippets/'+id, {method:'DELETE'}).then(function(r){return r.json();}).then(function(d){
    if (d.ok){
      var s = userSnippets.find(function(x){return x.id===id;});
      if (s && SNIPPETS[s.lang]) delete SNIPPETS[s.lang][s.trigger_key];
      userSnippets = userSnippets.filter(function(x){return x.id!==id;});
      renderSnippetList();
    }
  });
}

/* ══════════════════════════════════════════════════════════════════════
   VERSIYA TARIXI (har saqlashda avtomatik saqlanadigan snapshot)
   ══════════════════════════════════════════════════════════════════════ */
function openHistory(){
  if (!activePath){ flash('⚠ Avval fayl oching','yl'); return; }
  document.getElementById('historyBg').style.display = 'flex';
  document.getElementById('histTitle').textContent = '🕘 Tarix — '+activePath;
  var list = document.getElementById('histList');
  list.innerHTML = '<div class="modalRow"><small>Yuklanmoqda...</small></div>';
  authFetch('/editor/fs/history?uuid=UUID&path='+encodeURIComponent(activePath))
    .then(function(r){return r.json();}).then(function(d){
      list.innerHTML = '';
      (d.history||[]).forEach(function(h){
        var row = document.createElement('div');
        row.className = 'histItem';
        row.innerHTML = '<span>'+h.saved_at+'</span><button class="btn bgh bsm">↩ Tiklash</button>';
        row.querySelector('button').onclick = function(){
          if (!confirm('Joriy tarkib almashtiriladi. Davom etasizmi?')) return;
          docsCache[activePath].setValue(h.content);
          doSave(activePath, false);
          closeModal('historyBg');
        };
        list.appendChild(row);
      });
      if (!(d.history||[]).length) list.innerHTML = '<div class="modalRow"><small>Tarix bosh</small></div>';
    });
}

/* ══════════════════════════════════════════════════════════════════════
   YORDAM PANELI (Emmet qisqartmalari va tugmalar haqida)
   ══════════════════════════════════════════════════════════════════════ */
function openHelpPanel(){
  document.getElementById('helpBg').style.display = 'flex';
}
document.addEventListener('DOMContentLoaded', function(){
  var hbg = document.getElementById('helpBg');
  if (hbg) hbg.addEventListener('click', function(e){
    if (e.target.id === 'helpBg') closeModal('helpBg');
  });
});

/* ══════════════════════════════════════════════════════════════════════
   CHAT — Loyiha ichidagi jonli chat
   ══════════════════════════════════════════════════════════════════════ */
var chatInterval=null;
function openChatPanel(){
  document.getElementById('chatBg').style.display='flex';
  loadChat();
  if(chatInterval) clearInterval(chatInterval);
  chatInterval=setInterval(loadChat,3000);
}
function loadChat(){
  authFetch('/api/chat/UUID/messages').then(function(r){return r.json();}).then(function(d){
    var box=document.getElementById('chatMessages');
    box.innerHTML=(d.messages||[]).map(function(m){
      return '<div style="margin-bottom:6px"><b style="color:var(--ac);font-size:.75rem">'+m.username+'</b> <span class="tm" style="font-size:.65rem">'+m.created_at.slice(11,16)+'</span><br><span>'+m.message+'</span></div>';
    }).join('') || '<p class="tm" style="text-align:center;margin-top:20px">Hali xabar yoq</p>';
    box.scrollTop=box.scrollHeight;
  });
}
function sendChat(){
  var inp=document.getElementById('chatInput');
  var msg=inp.value.trim();
  if(!msg) return;
  authFetch('/api/chat/UUID/send',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:msg})}).then(function(){inp.value='';loadChat();});
}
document.addEventListener('DOMContentLoaded',function(){
  document.getElementById('chatBg').addEventListener('click',function(e){if(e.target.id==='chatBg'){closeModal('chatBg');if(chatInterval)clearInterval(chatInterval);}});
});

/* ══════════════════════════════════════════════════════════════════════
   TODO — Loyiha vazifalar ro'yxati
   ══════════════════════════════════════════════════════════════════════ */
function openTodoPanel(){
  document.getElementById('todoBg').style.display='flex';
  loadTodos();
}
function loadTodos(){
  authFetch('/api/todos/UUID').then(function(r){return r.json();}).then(function(d){
    var list=document.getElementById('todoList');
    list.innerHTML=(d.todos||[]).map(function(t){
      var pri={'high':'🔴','normal':'🟡','low':'🟢'}[t.priority]||'🟡';
      return '<div class="modalRow" style="'+(t.is_done?'opacity:.5;text-decoration:line-through':'')+'"><span>'+pri+' '+t.title+'</span><span class="fl"><button class="btn bgh bsm" onclick="toggleTodo('+t.id+','+(!t.is_done)+')">✓</button><button class="btn br bsm" onclick="delTodo('+t.id+')">🗑</button></span></div>';
    }).join('') || '<div class="modalRow"><small>Vazifa yoq</small></div>';
  });
}
function addTodo(){
  var inp=document.getElementById('todoInput');var title=inp.value.trim();
  var pri=document.getElementById('todoPriority').value;
  if(!title){flash('⚠ Vazifa kiriting','yl');return;}
  authFetch('/api/todos/UUID',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({title:title,priority:pri})}).then(function(r){return r.json();}).then(function(d){if(d.ok){inp.value='';loadTodos();flash('✓ Qo\\'shildi','gr');}});
}
function toggleTodo(id,done){
  authFetch('/api/todos/UUID/'+id,{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify({is_done:done})}).then(function(){loadTodos();});
}
function delTodo(id){
  authFetch('/api/todos/UUID/'+id,{method:'DELETE'}).then(function(){loadTodos();});
}
document.addEventListener('DOMContentLoaded',function(){document.getElementById('todoBg').addEventListener('click',function(e){if(e.target.id==='todoBg')closeModal('todoBg');});});

/* ══════════════════════════════════════════════════════════════════════
   KOMPONENT KUTUBXONASI
   ══════════════════════════════════════════════════════════════════════ */
function openComponentsPanel(){
  document.getElementById('compBg').style.display='flex';
  authFetch('/api/components').then(function(r){return r.json();}).then(function(d){
    var list=document.getElementById('compList');
    list.innerHTML=(d.components||[]).map(function(c){
      return '<div class="modalRow" style="flex-direction:column;align-items:flex-start"><div class="fl" style="width:100%"><b style="color:#fff;font-size:.82rem">'+c.name+'</b><span class="bx xp mla">'+c.category+'</span><button class="btn bp bsm" onclick="insertComponent('+JSON.stringify(JSON.stringify(c.code))+')">+ Qo\\'shish</button></div></div>';
    }).join('');
  });
}
function insertComponent(code){
  if(!cm||!activePath) return;
  var cur=cm.getCursor();
  cm.replaceRange(JSON.parse(code)+'\\n',cur);
  closeModal('compBg');
  flash('✓ Komponent qo\\'shildi','gr');
  scheduleRun();
}
document.addEventListener('DOMContentLoaded',function(){document.getElementById('compBg').addEventListener('click',function(e){if(e.target.id==='compBg')closeModal('compBg');});});

/* ══════════════════════════════════════════════════════════════════════
   COLOR PICKER
   ══════════════════════════════════════════════════════════════════════ */
function openColorPicker(){
  document.getElementById('colorBg').style.display='flex';
  loadPalettes();
  document.getElementById('colorPickerInput').oninput=function(){document.getElementById('colorHexVal').value=this.value;};
}
function loadPalettes(){
  authFetch('/api/color/palette').then(function(r){return r.json();}).then(function(d){
    var box=document.getElementById('colorPalettes');
    var html='';
    Object.keys(d.palettes||{}).forEach(function(name){
      html+='<p style="color:var(--mt);font-size:.72rem;margin:8px 0 4px">'+name+'</p><div style="display:flex;flex-wrap:wrap;gap:4px">';
      d.palettes[name].forEach(function(c){
        html+='<div onclick="pickColor(\\''+c+'\\')" style="width:24px;height:24px;border-radius:4px;cursor:pointer;background:'+c+';border:1px solid var(--brd)" title="'+c+'"></div>';
      });
      html+='</div>';
    });
    box.innerHTML=html;
  });
}
function pickColor(c){document.getElementById('colorHexVal').value=c;document.getElementById('colorPickerInput').value=c;}
function insertColor(){
  var c=document.getElementById('colorHexVal').value;
  if(!cm||!activePath) return;
  var cur=cm.getCursor();
  cm.replaceRange(c,cur);
  closeModal('colorBg');
  flash('✓ Rang qo\\'shildi: '+c,'gr');
}
document.addEventListener('DOMContentLoaded',function(){document.getElementById('colorBg').addEventListener('click',function(e){if(e.target.id==='colorBg')closeModal('colorBg');});});

/* ══════════════════════════════════════════════════════════════════════
   TERMINAL
   ══════════════════════════════════════════════════════════════════════ */
function openTerminal(){document.getElementById('termBg').style.display='flex';document.getElementById('termInput').focus();}
function runTermCmd(){
  var inp=document.getElementById('termInput');var cmd=inp.value.trim();
  if(!cmd) return;
  var out=document.getElementById('termOutput');
  out.innerHTML+='<span style="color:var(--ac)">$ '+cmd+'</span>\\n';
  inp.value='';
  authFetch('/api/terminal/exec',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({command:cmd})}).then(function(r){return r.json();}).then(function(d){
    if(d.ok) out.innerHTML+='<span>'+((d.output||'').replace(/</g,'&lt;'))+'</span>\\n';
    else out.innerHTML+='<span style="color:var(--rd)">Xato: '+(d.error||'')+'</span>\\n';
    out.scrollTop=out.scrollHeight;
  }).catch(function(){out.innerHTML+='<span style="color:var(--rd)">Tarmoq xatosi</span>\\n';});
}
document.addEventListener('DOMContentLoaded',function(){document.getElementById('termBg').addEventListener('click',function(e){if(e.target.id==='termBg')closeModal('termBg');});});

/* ══════════════════════════════════════════════════════════════════════
   PWA GENERATOR
   ══════════════════════════════════════════════════════════════════════ */
function generatePWA(){
  if(!confirm('Loyihaga PWA fayllarni (manifest.json, sw.js) qo\\'shish va index.html ni yangilashni xohlaysizmi?')) return;
  authFetch('/api/pwa/generate/UUID',{method:'POST'}).then(function(r){return r.json();}).then(function(d){
    if(d.ok){flash('✓ PWA yaratildi: '+d.files.join(', '),'gr');loadAll();}
    else flash('✗ Xato','rd');
  });
}

/* ══════════════════════════════════════════════════════════════════════
   README GENERATOR
   ══════════════════════════════════════════════════════════════════════ */
function generateReadme(){
  if(!confirm('README.md faylni avtomatik yaratish/yangilashni xohlaysizmi?')) return;
  authFetch('/api/readme/generate/UUID',{method:'POST'}).then(function(r){return r.json();}).then(function(d){
    if(d.ok){flash('✓ README.md yaratildi','gr');loadAll();}
    else flash('✗ Xato','rd');
  });
}

/* ══════════════════════════════════════════════════════════════════════
   RASM DRAG&DROP YUKLASH
   ══════════════════════════════════════════════════════════════════════ */
document.addEventListener('DOMContentLoaded',function(){
  var cmHost=document.getElementById('cmHost');
  if(!cmHost) return;
  cmHost.addEventListener('dragover',function(e){e.preventDefault();e.dataTransfer.dropEffect='copy';cmHost.style.outline='2px dashed var(--ac)';});
  cmHost.addEventListener('dragleave',function(){cmHost.style.outline='';});
  cmHost.addEventListener('drop',function(e){
    e.preventDefault();cmHost.style.outline='';
    var files=e.dataTransfer.files;
    if(!files.length) return;
    var file=files[0];
    if(!file.type.startsWith('image/')){flash('⚠ Faqat rasm fayllar','yl');return;}
    var fd=new FormData();fd.append('image',file);
    authFetch('/editor/upload-image/UUID',{method:'POST',body:fd}).then(function(r){return r.json();}).then(function(d){
      if(d.ok){
        var tag='<img src="'+d.url+'" alt="'+d.filename+'">';
        if(cm&&activePath) cm.replaceRange(tag+'\\n',cm.getCursor());
        flash('✓ Rasm yuklandi va qo\\'shildi','gr');
        scheduleRun();
      } else flash('✗ '+(d.error||'Xato'),'rd');
    });
  });
});

/* ══════════════════════════════════════════════════════════════════════
   BACKEND ROUTE'LAR (loyiha ichidagi mini-serverless funksiyalar)
   ══════════════════════════════════════════════════════════════════════ */
var beRoutes = [];

function openBackendPanel(){
  document.getElementById('backendBg').style.display = 'flex';
  beRefresh();
}
function beRefresh(){
  authFetch('/editor/backend/UUID').then(function(r){return r.json();}).then(function(d){
    beRoutes = d.routes || [];
    renderBackendList();
  });
}
function renderBackendList(){
  var list = document.getElementById('beList');
  list.innerHTML = '';
  beRoutes.forEach(function(r){
    var row = document.createElement('div');
    row.className = 'modalRow';
    row.innerHTML = '<span>['+r.method+'] /'+r.path+' '+(r.is_enabled?'':'<small>(o\\'chirilgan)</small>')+'</span>'+
      '<span class="fl"><button class="btn bgh bsm" data-t="tog">'+(r.is_enabled?'⏸':'▶️')+'</button>'+
      '<button class="btn br bsm" data-t="del">🗑</button></span>';
    row.querySelectorAll('button')[0].onclick = function(){ toggleBackendRoute(r.id, !r.is_enabled); };
    row.querySelectorAll('button')[1].onclick = function(){ deleteBackendRoute(r.id); };
    list.appendChild(row);
  });
  if (!beRoutes.length) list.innerHTML = '<div class="modalRow"><small>Hali backend route yoq</small></div>';
}
function addBackendRoute(){
  var method = document.getElementById('beMethod').value;
  var path = document.getElementById('bePath').value.trim();
  var code = document.getElementById('beCode').value;
  if (!path){ flash('⚠ Yo\\'l kiriting','yl'); return; }
  authFetch('/editor/backend/UUID',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({path:path,method:method,code:code})
  }).then(function(r){return r.json();}).then(function(d){
    if (d.ok){
      document.getElementById('bePath').value=''; document.getElementById('beCode').value='';
      beRefresh(); flash('✓ Route qo\\'shildi','gr');
    } else flash('✗ '+(d.error||'Xato'),'rd');
  });
}
function toggleBackendRoute(id, enabled){
  authFetch('/editor/backend/UUID/'+id,{method:'PUT',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({is_enabled:enabled})
  }).then(function(r){return r.json();}).then(function(){ beRefresh(); });
}
function deleteBackendRoute(id){
  if (!confirm('Route o\\'chirilsinmi?')) return;
  authFetch('/editor/backend/UUID/'+id,{method:'DELETE'}).then(function(r){return r.json();}).then(function(){ beRefresh(); });
}
document.addEventListener('DOMContentLoaded', function(){
  var bg = document.getElementById('backendBg');
  if (bg) bg.addEventListener('click', function(e){
    if (e.target.id === 'backendBg') closeModal('backendBg');
  });
});

/* ══════════════════════════════════════════════════════════════════════
   INITSIALIZATSIYA
   ══════════════════════════════════════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', function(){
  cm = new CodeMirror(document.getElementById('cmHost'), {
    value:'', mode:'htmlmixed', theme:'dracula', lineNumbers:true, lineWrapping:true, tabSize:2, indentUnit:2,
    matchBrackets:true, autoCloseBrackets:true, styleActiveLine:true, gutters:['CodeMirror-linenumbers','CodeMirror-lint-markers'],
    extraKeys: {
      'Ctrl-Space': function(cx){ CodeMirror.showHint(cx, customHint, {completeSingle:false}); },
      'Tab': function(cx){
        if (cx.state.completionActive){
          var w = cx.getRange({line:cx.getCursor().line,ch:0}, cx.getCursor());
          var m = w.match(/[a-zA-Z0-9._#\[\]{}*+>^()$=:"'%,!\/-]+$/);
          if (m && looksLikeEmmet(m[0])){ cx.closeHint(); if (trySnippetExpand(cx)) return; }
          return CodeMirror.Pass;
        }
        if (trySnippetExpand(cx)) return;
        if (cx.somethingSelected()){ cx.execCommand('indentMore'); return; }
        cx.replaceSelection('  ');
      },
      'Enter': function(cx){
        if (cx.state.completionActive) return CodeMirror.Pass;
        if ((activeTab==='h'||activeTab==='c') && trySnippetExpand(cx)) return;
        return CodeMirror.Pass;
      },
      'Ctrl-S': function(){ saveActive(); return false; },
      'Cmd-S': function(){ saveActive(); return false; },
      'Ctrl-P': function(){ openQuickOpen(); return false; },
      'Cmd-P': function(){ openQuickOpen(); return false; },
      'Ctrl-Shift-F': function(){ openGlobalSearch(); return false; },
      'Ctrl-Enter': function(){ runCode(); },
      'Cmd-Enter': function(){ runCode(); },
      'Shift-Alt-F': function(){ formatActive(); },
      'Ctrl-/': 'toggleComment',
      'Cmd-/': 'toggleComment'
    }
  });
  scheduleRun = debounce(runCode, 600);
  scheduleAutosave = debounce(function(){ if (activePath) doSave(activePath, true); }, 1500);
  cm.on('change', function(){
    if (activePath){ dirty[activePath]=true; renderTabs(); }
    scheduleRun();
    scheduleAutosave();
    drawMinimap();
  });
  cm.on('inputRead', function(cx, change){
    if (change.text.length===1 && /[a-zA-Z]/.test(change.text[0])){
      var cur = cx.getCursor();
      var before = cx.getLine(cur.line).slice(0, cur.ch);
      var m = before.match(/[a-zA-Z0-9._#\[\]{}*+>^()$=:"'%,!\/-]+$/);
      // Emmet naqshiga o'xshasa hintni ochmaymiz — Tab birinchi bosishdayoq kengaysin
      if (m && looksLikeEmmet(m[0])) return;
      CodeMirror.showHint(cx, customHint, {completeSingle:false});
    }
  });
  document.getElementById('globalSearchBg').addEventListener('click', function(e){
    if (e.target.id === 'globalSearchBg') closeModal('globalSearchBg');
  });
  document.getElementById('snippetsBg').addEventListener('click', function(e){
    if (e.target.id === 'snippetsBg') closeModal('snippetsBg');
  });
  document.getElementById('historyBg').addEventListener('click', function(e){
    if (e.target.id === 'historyBg') closeModal('historyBg');
  });
  document.addEventListener('keydown', function(e){
    if ((e.ctrlKey||e.metaKey) && e.key.toLowerCase()==='p'){ e.preventDefault(); openQuickOpen(); }
    if ((e.ctrlKey||e.metaKey) && e.shiftKey && e.key.toLowerCase()==='f'){ e.preventDefault(); openGlobalSearch(); }
  });
  setupResizer();
  loadAll();
  window.addEventListener('resize', drawMinimap);
});
</script></body></html>"""
