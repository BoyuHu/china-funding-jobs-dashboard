#!/usr/bin/env python3
import csv
import html
import json
import re
from pathlib import Path

SOURCE = Path("financing_over_50m.csv")
JOBS_SOURCE = Path("jobs_data.json")
OUTPUT = Path("融资公司筛选面板.html")
EXCLUDED_ROUNDS = {"IPO上市", "基石投资轮", "定向增发", "并购", "拟收购", "股权转让", "债权融资", "私有化"}
OVERSEAS = {"美国", "英国", "法国", "德国", "日本", "韩国", "新加坡", "加拿大", "澳大利亚", "印度", "以色列", "瑞士", "荷兰", "瑞典", "芬兰", "挪威", "丹麦", "阿联酋", "沙特阿拉伯", "印度尼西亚"}

MANUAL = [
  {"date":"2026-08-25","name":"想象着陆","company":"深圳想象着陆科技有限公司","industry":"AI设计","city":"深圳市","round":"天使轮","amount":"近1亿元","investors":"顺为资本、联想创投","summary":"前剪映产品负责人张琪智创办，产品为AI设计工作台OJO。金额来自媒体披露，尚未检索到公司或投资方完整公告。","source":"https://reportify.cn/social-media/863719626256064"},
  {"date":"2026-07-10","name":"灵境智源","company":"灵境智源","industry":"具身智能基础设施","city":"上海市","round":"天使及天使+轮","amount":"超1亿元","investors":"经纬创投领投、上海闵行国资战略跟投","summary":"资金用于团队建设、产品量产、具身原生芯片研发与生态建设。","source":"https://www.news.cn/shshpd/20260710/2c77553689d3463f9dc0640b7badef60/c.html"},
  {"date":"2026-07-10","name":"他山科技","company":"北京他山科技有限公司","industry":"触觉传感","city":"北京市","round":"B轮","amount":"数亿元","investors":"太平创新、均胜电子、奥克斯、洪山资本等","summary":"触觉传感与触觉原生模型。","source":"https://www.news.cn/tech/20260710/849daf41608941d28ebdb2e403127fbb/c.html"},
  {"date":"2026-06-29","name":"中科富海","company":"北京中科富海低温科技有限公司","industry":"高端低温装备","city":"北京市","round":"Pre-IPO","amount":"10亿元","investors":"国科资本领投，央国企、银行及地方产业资本参与","summary":"用于国产超低温核心产业发展。","source":"https://www.cascapital.cn/article/246.html"},
  {"date":"2026-06-16","name":"深朴智能","company":"深朴智能","industry":"具身智能","city":"北京市","round":"Pre-A轮","amount":"数亿元","investors":"滴滴领投，梅花创投、柯力传感等跟投","summary":"一年内连续完成四轮融资。","source":"https://www.36kr.com/p/3855543726691587"},
  {"date":"2026-04-20","name":"自变量机器人","company":"自变量机器人","industry":"具身智能","city":"深圳市","round":"B轮","amount":"近20亿元","investors":"小米战投、红杉中国领投","summary":"36氪独家报道；报道时公司暂无回应，证据等级为媒体披露。","source":"https://www.36kr.com/p/3774502008963841"},
  {"date":"2026-03-31","name":"玻色量子","company":"北京玻色量子科技有限公司","industry":"量子计算","city":"北京市","round":"B轮","amount":"10亿元","investors":"公开报道未完整列明","summary":"用于产品研发、芯片工艺、中试线和生态拓展。","source":"https://www.xinhuanet.com/digital/20260331/2ae0f227017e4f468f85a7beeec10f06/c.html"},
  {"date":"2026-01-22","name":"量旋科技","company":"深圳量旋科技有限公司","industry":"量子计算","city":"深圳市","round":"C轮","amount":"数亿元","investors":"隆利科技、晶凯资本、毅达资本等","summary":"用于核心技术迭代、产能扩充与全球化布局。","source":"https://www.news.cn/digital/20260123/35a8f9d943994740960a645389d8f79c/c.html"},
  {"date":"2025-12-18","name":"零点聚能","company":"零点聚能","industry":"核聚变","city":"未披露","round":"天使轮","amount":"超5000万元","investors":"公开汇总未完整列明","summary":"核聚变能源技术研发商。","source":"https://www.zhongtouhuac.com/h-nd-4141.html"},
  {"date":"2025-12-11","name":"星源智机器人","company":"星源智机器人","industry":"具身智能","city":"未披露","round":"天使+轮","amount":"超1亿元","investors":"赛富基金、凯联资本领投，三七互娱等跟投","summary":"通用具身大脑技术研发商。","source":"https://www.zhongtouhuac.com/h-nd-4141.html"},
  {"date":"2025-12-05","name":"优理奇机器人","company":"UniX AI","industry":"机器人","city":"未披露","round":"天使++++及天使+++++轮","amount":"两轮合计3亿元","investors":"川商基金、吴中金控、益华资本等","summary":"两轮合并披露。","source":"https://www.zhongtouhuac.com/h-nd-4141.html"}
]

def amount_cny(text):
    s = text.replace(",", "")
    m = re.search(r"([0-9.]+)亿美元", s)
    if m: return float(m.group(1)) * 7.1 * 100_000_000
    m = re.search(r"([0-9.]+)万美元", s)
    if m: return float(m.group(1)) * 7.1 * 10_000
    m = re.search(r"([0-9.]+)亿", s)
    if m: return float(m.group(1)) * 100_000_000
    m = re.search(r"([0-9.]+)万", s)
    if m: return float(m.group(1)) * 10_000
    if "数十亿" in s: return 3_000_000_000
    if "数亿" in s: return 300_000_000
    if "两亿" in s: return 200_000_000
    if "近亿" in s or "近1亿" in s: return 90_000_000
    if any(x in s for x in ("超亿", "过亿", "亿级")): return 110_000_000
    return 50_000_000

def confidence(row):
    if row["name"] == "想象着陆" or "暂无回应" in row.get("summary", ""):
        return "媒体披露"
    if any(x in row["amount"] for x in ("数", "近", "超", "约")):
        return "金额模糊"
    return "金额明确"

def load_rows():
    with SOURCE.open(encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    rows = [r for r in rows if r["round"] not in EXCLUDED_ROUNDS and r["city"] not in OVERSEAS]
    existing = {(r["date"], r["name"]) for r in rows}
    rows.extend(r for r in MANUAL if (r["date"], r["name"]) not in existing)
    for i, row in enumerate(rows):
        row["id"] = i + 1
        row["amountValue"] = amount_cny(row["amount"])
        row["confidence"] = confidence(row)
    rows.sort(key=lambda r: (r["date"], r["amountValue"]), reverse=True)
    return rows

TEMPLATE = r'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>国内大额融资公司筛选面板</title>
<style>
:root{--ink:#17211d;--paper:#f5f2e9;--panel:#ece8dc;--copper:#c8673b;--moss:#5e725f;--line:#d6d1c5;--muted:#6c726d;--white:#fffdf8;--danger:#9b493b}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--paper);color:var(--ink);font-family:"Avenir Next","PingFang SC","Microsoft YaHei",sans-serif;font-size:14px}
button,input,select{font:inherit}.shell{display:grid;grid-template-columns:286px minmax(0,1fr);min-height:100vh}.sidebar{position:sticky;top:0;height:100vh;padding:30px 22px;background:var(--ink);color:#f8f4e8;overflow:auto}.eyebrow{font-family:"IBM Plex Mono","Menlo",monospace;font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:#c7d1c8}.brand{margin:10px 0 8px;font-family:"Songti SC","Noto Serif CJK SC",serif;font-size:27px;line-height:1.2}.brand-note{margin:0 0 28px;color:#b9c0ba;line-height:1.6}.filter-group{margin:0 0 19px}.filter-group label{display:block;margin-bottom:7px;font-size:12px;color:#d7ddd7}.control{width:100%;height:40px;border:1px solid #49554e;border-radius:2px;background:#202c26;color:#fff;padding:0 11px;outline:none}.control:focus{border-color:#d88a62;box-shadow:0 0 0 2px rgba(200,103,59,.18)}.date-row{display:grid;grid-template-columns:1fr 1fr;gap:8px}.actions{display:flex;gap:8px;margin-top:24px}.btn{border:1px solid transparent;border-radius:2px;padding:10px 12px;cursor:pointer;transition:.16s ease}.btn-primary{background:var(--copper);color:#fff}.btn-secondary{border-color:#526158;background:transparent;color:#e6ebe6}.btn:hover{transform:translateY(-1px);filter:brightness(1.06)}.main{padding:34px 42px 50px;min-width:0}.masthead{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:26px;align-items:end;border-bottom:1px solid var(--ink);padding-bottom:21px}.masthead h1{margin:0;font-family:"Songti SC","Noto Serif CJK SC",serif;font-size:36px;font-weight:600;letter-spacing:-.03em}.masthead p{max-width:760px;margin:11px 0 0;color:var(--muted);line-height:1.7}.stamp{font-family:"IBM Plex Mono","Menlo",monospace;color:var(--muted);text-align:right;font-size:12px}.metrics{display:grid;grid-template-columns:1.2fr 1fr 1fr 1fr;gap:1px;margin:24px 0;background:var(--line);border:1px solid var(--line)}.metric{background:var(--white);padding:18px 20px;min-height:102px}.metric strong{display:block;font-family:"IBM Plex Mono","Menlo",monospace;font-size:28px;line-height:1;margin-bottom:10px}.metric span{color:var(--muted);font-size:12px}.metric.primary{background:var(--moss);color:#fff}.metric.primary span{color:#dbe4dc}.toolbar{display:flex;align-items:center;justify-content:space-between;gap:14px;margin:0 0 13px}.result-note{color:var(--muted)}.toolbar-right{display:flex;align-items:center;gap:8px}.sort{height:36px;border:1px solid var(--line);background:var(--white);padding:0 9px;color:var(--ink)}.export{height:36px;border:1px solid var(--ink);background:transparent;color:var(--ink);padding:0 12px;cursor:pointer}.table-wrap{overflow:auto;border:1px solid var(--line);background:var(--white)}table{width:100%;min-width:1080px;border-collapse:collapse;table-layout:fixed}th{position:sticky;top:0;z-index:2;background:var(--ink);color:#fff;text-align:left;font-size:11px;letter-spacing:.08em;padding:13px 12px}td{border-bottom:1px solid var(--line);padding:13px 12px;vertical-align:top;line-height:1.55}tbody tr{transition:.12s}tbody tr:hover{background:#f0ede4}.company{font-weight:700;font-size:15px}.legal{display:block;color:var(--muted);font-size:11px;margin-top:3px}.tag{display:inline-block;border:1px solid var(--line);padding:2px 7px;margin:0 4px 4px 0;font-size:11px;background:#faf8f2}.amount{font-family:"IBM Plex Mono","Menlo",monospace;font-weight:700;color:var(--copper)}.date{font-family:"IBM Plex Mono","Menlo",monospace;font-size:12px}.investors{color:#38413d}.source{display:inline-flex;align-items:center;gap:5px;color:#27553d;text-decoration:none;border-bottom:1px solid #8ba291}.source:hover{color:var(--copper);border-color:var(--copper)}.status{font-size:11px}.status.exact{color:#315f45}.status.vague{color:#8a5b24}.status.media{color:var(--danger)}.pager{display:flex;justify-content:space-between;align-items:center;margin-top:14px;color:var(--muted)}.pager-buttons{display:flex;gap:8px}.pager button{border:1px solid var(--line);background:var(--white);padding:8px 12px;color:var(--ink);cursor:pointer}.pager button:disabled{opacity:.35;cursor:not-allowed}.empty{padding:70px 24px;text-align:center;color:var(--muted)}.notice{margin-top:24px;padding-top:17px;border-top:1px solid var(--line);color:var(--muted);font-size:12px;line-height:1.7}
.tabs{display:flex;gap:0;margin:24px 0 0;border-bottom:1px solid var(--ink)}.tab{border:0;background:transparent;color:var(--muted);padding:12px 18px;cursor:pointer;font-weight:700}.tab.active{background:var(--ink);color:#fff}.view[hidden]{display:none}.job-controls{display:grid;grid-template-columns:1.2fr 1fr 1fr auto;gap:10px;margin:20px 0}.job-groups{display:grid;gap:18px}.job-group{border-top:3px solid var(--ink);background:var(--white)}.job-group h2{display:flex;justify-content:space-between;margin:0;padding:16px 18px;border-bottom:1px solid var(--line);font-family:"Songti SC","Noto Serif CJK SC",serif;font-size:22px}.job-count{font-family:"IBM Plex Mono","Menlo",monospace;color:var(--copper);font-size:14px}.job-list{display:grid;grid-template-columns:repeat(2,minmax(0,1fr))}.job-item{padding:16px 18px;border-bottom:1px solid var(--line);border-right:1px solid var(--line)}.job-item h3{margin:0 0 7px;font-size:15px}.job-meta{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:10px;color:var(--muted);font-size:11px}.job-company{color:var(--moss);font-weight:700}.job-link{color:#27553d;text-decoration:none;border-bottom:1px solid #8ba291}.coverage{margin-top:24px;padding:18px;background:var(--panel);line-height:1.7}.coverage strong{font-family:"IBM Plex Mono","Menlo",monospace}.pending-list{margin-top:12px;max-height:180px;overflow:auto;font-size:12px;color:var(--muted)}
@media(max-width:900px){.shell{display:block}.sidebar{position:relative;height:auto}.main{padding:25px 18px}.masthead{display:block}.stamp{text-align:left;margin-top:14px}.metrics{grid-template-columns:1fr 1fr}.toolbar{align-items:flex-start;flex-direction:column}.sidebar .filters{display:grid;grid-template-columns:1fr 1fr;gap:0 14px}.actions{grid-column:1/-1}.job-controls{grid-template-columns:1fr 1fr}.job-list{grid-template-columns:1fr}}
@media(max-width:560px){.sidebar .filters{display:block}.metrics{grid-template-columns:1fr}.masthead h1{font-size:29px}.main{padding:20px 12px}}
</style>
</head>
<body>
<div class="shell">
<aside class="sidebar">
  <div class="eyebrow">Capital Signal Desk</div><div class="brand">大额融资<br>公开信息面板</div>
  <p class="brand-note">筛选近一年国内单笔融资5000万元以上的公开披露事件。</p>
  <div class="filters">
    <div class="filter-group"><label for="search">公司或投资方关键词</label><input id="search" class="control" type="search" placeholder="例如 想象着陆 或 红杉"></div>
    <div class="filter-group"><label for="city">城市</label><select id="city" class="control"><option value="">全部城市</option></select></div>
    <div class="filter-group"><label for="industry">行业</label><select id="industry" class="control"><option value="">全部行业</option></select></div>
    <div class="filter-group"><label for="round">融资轮次</label><select id="round" class="control"><option value="">全部轮次</option></select></div>
    <div class="filter-group"><label for="amountBand">融资金额</label><select id="amountBand" class="control"><option value="">全部金额</option><option value="0.5-1">5000万至1亿元</option><option value="1-5">1亿至5亿元</option><option value="5-10">5亿至10亿元</option><option value="10+">10亿元以上</option></select></div>
    <div class="filter-group"><label for="confidence">信息口径</label><select id="confidence" class="control"><option value="">全部口径</option><option>金额明确</option><option>金额模糊</option><option>媒体披露</option></select></div>
    <div class="filter-group"><label>披露日期</label><div class="date-row"><input id="startDate" class="control" type="date" value="2025-11-07"><input id="endDate" class="control" type="date" value="2026-11-07"></div></div>
    <div class="actions"><button id="reset" class="btn btn-secondary">清空筛选</button><button id="focusOjo" class="btn btn-primary">查看想象着陆</button></div>
  </div>
</aside>
<main class="main">
  <header class="masthead"><div><h1>国内高额融资公司雷达</h1><p>将公开披露的股权融资事件按公司、城市、行业和轮次集中呈现。金额模糊项目保留原始表述，并单独标记证据口径。</p></div><div class="stamp">DATA CUT<br>2026.11.07</div></header>
  <div class="tabs" role="tablist"><button class="tab active" id="financeTab" role="tab">融资公司</button><button class="tab" id="jobsTab" role="tab">招聘岗位</button></div>
  <section id="financeView" class="view">
  <section class="metrics"><div class="metric primary"><strong id="metricCount">0</strong><span>当前融资事件</span></div><div class="metric"><strong id="metricCompanies">0</strong><span>公司</span></div><div class="metric"><strong id="metricCities">0</strong><span>城市</span></div><div class="metric"><strong id="metricIndustries">0</strong><span>行业</span></div></section>
  <div class="toolbar"><div id="resultNote" class="result-note"></div><div class="toolbar-right"><select id="sort" class="sort"><option value="date-desc">日期从新到旧</option><option value="amount-desc">金额从高到低</option><option value="amount-asc">金额从低到高</option><option value="company-asc">公司名称</option></select><button id="export" class="export">导出筛选结果</button></div></div>
  <div class="table-wrap"><table><colgroup><col style="width:110px"><col style="width:200px"><col style="width:145px"><col style="width:150px"><col style="width:360px"><col style="width:115px"></colgroup><thead><tr><th>日期</th><th>公司与地区</th><th>轮次与金额</th><th>行业与口径</th><th>投资方与说明</th><th>资料来源</th></tr></thead><tbody id="tbody"></tbody></table><div id="empty" class="empty" hidden>没有符合条件的记录，请减少筛选条件。</div></div>
  <div class="pager"><div id="pageInfo"></div><div class="pager-buttons"><button id="prev">上一页</button><button id="next">下一页</button></div></div>
  <div class="notice">说明：面板排除了IPO募资、基石投资、上市公司定向增发、债权融资、并购和单纯股权转让。公开数据库存在分页及企业未披露限制，本面板适合线索发现和初筛，不替代正式尽调。</div></section>
  <section id="jobsView" class="view" hidden>
    <section class="metrics"><div class="metric primary"><strong id="jobMetricCount">0</strong><span>已核验岗位</span></div><div class="metric"><strong id="jobMetricCompanies">0</strong><span>已覆盖公司</span></div><div class="metric"><strong id="jobMetricFamilies">0</strong><span>工种分类</span></div><div class="metric"><strong id="jobMetricPending">0</strong><span>待继续核验公司</span></div></section>
    <div class="job-controls"><input id="jobSearch" class="sort" type="search" placeholder="搜索岗位或公司"><select id="jobFamily" class="sort"><option value="">全部工种</option></select><select id="jobCity" class="sort"><option value="">全部城市</option></select><button id="jobReset" class="export">清空岗位筛选</button></div>
    <div id="jobResultNote" class="result-note"></div><div id="jobGroups" class="job-groups"></div>
    <div class="coverage"><strong>覆盖说明</strong><br>本页目前只展示已找到具体岗位名称和有效投递入口的公开招聘信息。没有公开招聘页、岗位已下线或尚未完成核验的公司不会被冒充为“正在招聘”。<div id="pendingList" class="pending-list"></div></div>
  </section>
</main></div>
<script id="dataset" type="application/json">__DATA__</script>
<script id="jobsDataset" type="application/json">__JOBS__</script>
<script>
const DATA=JSON.parse(document.getElementById('dataset').textContent);const JOBS=JSON.parse(document.getElementById('jobsDataset').textContent);const PAGE_SIZE=50;let page=1,filtered=[];
const $=id=>document.getElementById(id);const controls=['search','city','industry','round','amountBand','confidence','startDate','endDate','sort'];
const esc=s=>String(s??'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
function fillSelect(id,values){const s=$(id);[...new Set(values.filter(Boolean))].sort((a,b)=>a.localeCompare(b,'zh-CN')).forEach(v=>s.add(new Option(v,v)))}
fillSelect('city',DATA.map(x=>x.city));fillSelect('industry',DATA.map(x=>x.industry));fillSelect('round',DATA.map(x=>x.round));
function inBand(v,b){if(!b)return true;const yi=v/1e8;if(b==='0.5-1')return yi>=.5&&yi<1;if(b==='1-5')return yi>=1&&yi<5;if(b==='5-10')return yi>=5&&yi<10;return yi>=10}
function apply(){const q=$('search').value.trim().toLowerCase();filtered=DATA.filter(x=>(!q||[x.name,x.company,x.investors,x.summary].join(' ').toLowerCase().includes(q))&&(!$('city').value||x.city===$('city').value)&&(!$('industry').value||x.industry===$('industry').value)&&(!$('round').value||x.round===$('round').value)&&inBand(x.amountValue,$('amountBand').value)&&(!$('confidence').value||x.confidence===$('confidence').value)&&(!$('startDate').value||x.date>=$('startDate').value)&&(!$('endDate').value||x.date<=$('endDate').value));
const sort=$('sort').value;filtered.sort((a,b)=>sort==='amount-desc'?b.amountValue-a.amountValue:sort==='amount-asc'?a.amountValue-b.amountValue:sort==='company-asc'?a.name.localeCompare(b.name,'zh-CN'):b.date.localeCompare(a.date));page=Math.min(page,Math.max(1,Math.ceil(filtered.length/PAGE_SIZE)));render()}
function statusClass(c){return c==='金额明确'?'exact':c==='金额模糊'?'vague':'media'}
function render(){const start=(page-1)*PAGE_SIZE,rows=filtered.slice(start,start+PAGE_SIZE);$('tbody').innerHTML=rows.map(x=>`<tr><td class="date">${esc(x.date)}</td><td><span class="company">${esc(x.name)}</span><span class="legal">${esc(x.company!==x.name?x.company:'')}${x.city?' · '+esc(x.city):''}</span></td><td><span class="tag">${esc(x.round)}</span><div class="amount">${esc(x.amount)}</div></td><td><span class="tag">${esc(x.industry)}</span><div class="status ${statusClass(x.confidence)}">${esc(x.confidence)}</div></td><td class="investors">${esc(x.investors)}${x.summary?'<span class="legal">'+esc(x.summary)+'</span>':''}</td><td><a class="source" href="${esc(x.source)}" target="_blank" rel="noopener">打开来源 ↗</a></td></tr>`).join('');$('empty').hidden=rows.length>0;$('metricCount').textContent=filtered.length.toLocaleString('zh-CN');$('metricCompanies').textContent=new Set(filtered.map(x=>x.name)).size.toLocaleString('zh-CN');$('metricCities').textContent=new Set(filtered.map(x=>x.city).filter(Boolean)).size;$('metricIndustries').textContent=new Set(filtered.map(x=>x.industry).filter(Boolean)).size;$('resultNote').textContent=`从 ${DATA.length} 条公开记录中筛出 ${filtered.length} 条`;$('pageInfo').textContent=filtered.length?`第 ${page} / ${Math.ceil(filtered.length/PAGE_SIZE)} 页`:'无结果';$('prev').disabled=page<=1;$('next').disabled=page>=Math.ceil(filtered.length/PAGE_SIZE)}
controls.forEach(id=>$(id).addEventListener(id==='search'?'input':'change',()=>{page=1;apply()}));$('reset').onclick=()=>{controls.forEach(id=>{if(id==='startDate')$(id).value='2025-11-07';else if(id==='endDate')$(id).value='2026-11-07';else if(id==='sort')$(id).value='date-desc';else $(id).value=''});page=1;apply()};$('focusOjo').onclick=()=>{$('search').value='想象着陆';page=1;apply()};$('prev').onclick=()=>{if(page>1){page--;render();scrollTo({top:0,behavior:'smooth'})}};$('next').onclick=()=>{if(page<Math.ceil(filtered.length/PAGE_SIZE)){page++;render();scrollTo({top:0,behavior:'smooth'})}};
$('export').onclick=()=>{const cols=['date','name','company','city','industry','round','amount','confidence','investors','source'];const csv=[cols.join(','),...filtered.map(r=>cols.map(c=>'"'+String(r[c]??'').replaceAll('"','""')+'"').join(','))].join('\n');const blob=new Blob(['\ufeff'+csv],{type:'text/csv;charset=utf-8'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='融资筛选结果.csv';a.click();URL.revokeObjectURL(a.href)};
function switchTab(name){const jobs=name==='jobs';$('financeView').hidden=jobs;$('jobsView').hidden=!jobs;document.querySelector('.filters').hidden=jobs;$('financeTab').classList.toggle('active',!jobs);$('jobsTab').classList.toggle('active',jobs)}$('financeTab').onclick=()=>switchTab('finance');$('jobsTab').onclick=()=>switchTab('jobs');
fillSelect('jobFamily',JOBS.map(x=>x.family));const jobCities=JOBS.flatMap(x=>x.city.split(/[、 ，]/).filter(Boolean));fillSelect('jobCity',jobCities);
const fundedNames=new Set(DATA.map(x=>x.name));const hiredNames=new Set(JOBS.map(x=>x.company));const pending=[...fundedNames].filter(x=>!hiredNames.has(x)).sort((a,b)=>a.localeCompare(b,'zh-CN'));
function renderJobs(){const q=$('jobSearch').value.trim().toLowerCase(),family=$('jobFamily').value,city=$('jobCity').value;const rows=JOBS.filter(x=>(!q||[x.company,x.title,x.family].join(' ').toLowerCase().includes(q))&&(!family||x.family===family)&&(!city||x.city.includes(city)));const groups=Object.groupBy?Object.groupBy(rows,x=>x.family):rows.reduce((a,x)=>((a[x.family]??=[]).push(x),a),{});$('jobGroups').innerHTML=Object.entries(groups).sort((a,b)=>b[1].length-a[1].length).map(([name,list])=>`<section class="job-group"><h2>${esc(name)}<span class="job-count">${list.length} 个岗位</span></h2><div class="job-list">${list.map(x=>`<article class="job-item"><h3>${esc(x.title)}</h3><div class="job-meta"><span class="job-company">${esc(x.company)}</span><span>${esc(x.city)}</span><span>${esc(x.type)}</span></div><a class="job-link" href="${esc(x.apply)}" target="_blank" rel="noopener">查看岗位并申请 ↗</a><span class="legal">${esc(x.source)} · 核验 ${esc(x.verified)}${x.published&&x.published!=='未披露'?' · 发布 '+esc(x.published):''}</span></article>`).join('')}</div></section>`).join('')||'<div class="empty">没有符合条件的岗位。</div>';$('jobMetricCount').textContent=rows.length;$('jobMetricCompanies').textContent=new Set(rows.map(x=>x.company)).size;$('jobMetricFamilies').textContent=new Set(rows.map(x=>x.family)).size;$('jobMetricPending').textContent=pending.length;$('jobResultNote').textContent=`已核验 ${JOBS.length} 个岗位，当前显示 ${rows.length} 个`;$('pendingList').textContent=`待继续核验 ${pending.length} 家：${pending.join('、')}`}
['jobSearch','jobFamily','jobCity'].forEach(id=>$(id).addEventListener(id==='jobSearch'?'input':'change',renderJobs));$('jobReset').onclick=()=>{$('jobSearch').value='';$('jobFamily').value='';$('jobCity').value='';renderJobs()};apply();renderJobs();
</script></body></html>'''

def main():
    rows = load_rows()
    jobs = json.loads(JOBS_SOURCE.read_text(encoding="utf-8"))
    payload = json.dumps(rows, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    jobs_payload = json.dumps(jobs, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    OUTPUT.write_text(TEMPLATE.replace("__DATA__", payload).replace("__JOBS__", jobs_payload), encoding="utf-8")
    print(f"saved {OUTPUT} rows={len(rows)} jobs={len(jobs)} bytes={OUTPUT.stat().st_size}")

if __name__ == "__main__":
    main()
