#!/usr/bin/env python3
"""One-time template assembly: Asaak shell -> Loads app/template.html.

Keeps the Addem design system, shell, workspace and settings machinery; replaces
every data-dependent renderer with the Loads data contract."""
from pathlib import Path

SRC = Path("/home/claude/work/Asaak_Reporting_Platform/app/template.html")
DST = Path("/home/claude/work/Loads_Reporting_Platform/app/template.html")

t = SRC.read_text(encoding="utf-8")


def rep(old, new, count=1):
    global t
    assert t.count(old) >= 1, f"anchor missing: {old[:80]!r}"
    t = t.replace(old, new, count)


def rep_between(start, end, new):
    """Replace text from `start` (inclusive) to `end` (exclusive) with new+end."""
    global t
    i = t.index(start)
    j = t.index(end, i)
    t = t[:i] + new + t[j:]


# ---------- shell & login ----------
rep("<title>Asaak · Institutional Reporting — Addem Capital</title>",
    "<title>Loads · Institutional Reporting — Addem Capital</title>")
rep("Institutional reporting for <em>Asaak</em> — portfolio, financials and legal in one place.",
    "Institutional reporting for <em>Loads</em> — portfolio, financials and legal in one place.")
rep("Private credit portfolio monitoring · Goldberg-Zogovic, S.A.P.I. de C.V., SOFOM, E.N.R. Confidential — authorized users only.",
    "Private credit portfolio monitoring · cross-border trade receivables. Confidential — authorized users only.")
rep("<p>Access the Asaak reporting platform.</p>", "<p>Access the Loads reporting platform.</p>")
rep("<b>Asaak · Addem Capital</b>", "<b>Loads · Addem Capital</b>")
rep('<div class="t">Addem Capital</div><div class="s">Asaak · Reporting</div>',
    '<div class="t">Addem Capital</div><div class="s">Loads · Reporting</div>')
rep('<div class="crumb">Asaak / <b id="crumbPage">Overview</b></div>',
    '<div class="crumb">Loads / <b id="crumbPage">Overview</b></div>')

# ---------- helpers: period label for annual financials ----------
rep("const monLab=m=>{const [y,mm]=m.split('-');return ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][+mm-1]+' '+y.slice(2)};",
    "const monLab=m=>{if(!m.includes('-'))return 'FY '+m;const [y,mm]=m.split('-');return ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][+mm-1]+' '+y.slice(2)};\n"
    "const fK=v=>{if(v==null)return '—';const a=Math.abs(v);return (v<0?'−$':'$')+(a>=1e6?(a/1e6).toFixed(2)+'M':(a/1e3).toFixed(0)+'k');};")

# ---------- derived series ----------
rep_between("/* ==================== derived series ==================== */",
            "/* ==================== auth & router ==================== */", """/* ==================== derived series ==================== */
const FIN=DATA.financials, LT=DATA.loan_tape, POL=DATA.policy, CT=DATA.contracts, CONC=DATA.concentration;
const PERIODS=FIN.map(f=>f.period);
const S={
 assets:FIN.map(f=>f.bs.total_assets??null),
 liabilities:FIN.map(f=>f.bs.total_liabilities??null),
 equity:FIN.map(f=>f.bs.total_equity??null),
 cash:FIN.map(f=>f.bs.cash??null),
 revM:FIN.map(f=>f.is_monthly.totals.revenue),
 niM:FIN.map(f=>f.is_monthly.totals.net_income),
 oiM:FIN.map(f=>f.is_monthly.totals.operating_income),
};
const LATEST=FIN[FIN.length-1], PREVF=FIN.length>1?FIN[FIN.length-2]:FIN[0];
const seg=(sc,sg)=>LT[sc+(sg==='all'?'':'_'+sg)]||null;
const collectionsTot=LT.total.collections.total;
const financedTot=LT.total.origination.amount;

""")

# ---------- asof pill ----------
rep("$('#asofPill').textContent='Portfolio as of '+DATA.meta.as_of_date+' · Financials through '+monLab(DATA.meta.financials_through)+' · MXN';",
    "$('#asofPill').textContent='Portfolio as of '+DATA.meta.as_of_date+' · Financials through FY '+DATA.meta.financials_through+' · USD';")

# ---------- OVERVIEW ----------
rep_between("/* ==================== OVERVIEW ==================== */",
            "/* ==================== PORTFOLIO ==================== */", """/* ==================== OVERVIEW ==================== */
function rOverview(){
 const ta=LT.total_active, q=ta.credit_quality, fq=(seg('fin','active')||LT.fin).credit_quality;
 const eq=LATEST.bs.total_equity, eqPrev=PREVF.bs.total_equity;
 const fin=seg('fin','active')||LT.fin;
 $('#view').innerHTML=`
 <div class="pagehead"><span class="eyebrow">Borrower profile</span><h1>Loads — Overview</h1>
 <p>Loads (Loads USA, Inc., consolidated) is a tech-enabled B2B platform for cross-border food trade built on three pillars — Trade (a digital marketplace connecting verified buyers and suppliers across 25+ countries), Move (embedded end-to-end logistics with freight insurance on every shipment) and Finance (embedded working capital deployed through a ring-fenced SPV, with trade credit insurance of up to 90% per qualified operation). Addem Capital monitors the trade-receivables book as prospective senior lender to the Loads Finance SPV; every order in the tape is a short-cycle, milestone-linked receivable against an end importer.</p></div>

 <section><div class="hero-strip">
  <span class="eyebrow">Portfolio position · ${DATA.meta.as_of_date}</span>
  <h2>${fK(ta.outstanding.active_ob)} open receivable across ${ta.outstanding.active_count} orders — ${fM(financedTot)} financed to date</h2>
  <p>The tape covers ${LT.total.origination.count} trade orders issued ${LT.total.origination.first} → ${LT.total.origination.last} across six business units, all USD. ${fP(LT.total.collections.collection_rate,1)} of financed exposure has already been collected in cash; the expected-loss provision under the Manual de Crédito 2026 grid is ${fK(POL.expected_loss)} (${fP(POL.provision_coverage,1)} of the open receivable). No executed Addem facility is in the data room — the SPV facility fact sheet is indicative.</p>
  <div class="hero-kpis">
   <div class="k"><div class="lab">Financed to date</div><div class="v num">${fM(financedTot)}</div><div class="d">${LT.total.origination.count} orders</div></div>
   <div class="k"><div class="lab">Open receivable</div><div class="v num"><em>${fK(ta.outstanding.active_ob)}</em></div><div class="d">${ta.outstanding.active_count} open orders</div></div>
   <div class="k"><div class="lab">Collected in cash</div><div class="v num">${fM(collectionsTot)}</div><div class="d">${fP(LT.total.collections.collection_rate,1)} of financed</div></div>
   <div class="k"><div class="lab">Expected-loss provision</div><div class="v num">${fK(POL.expected_loss)}</div><div class="d">${fP(POL.provision_coverage,1)} coverage</div></div>
   <div class="k"><div class="lab">WA credit cycle</div><div class="v num">${LT.total.weighted_averages.wa_tenor_days} d</div><div class="d">memo avg 33 d · WAL 30–45 d</div></div>
  </div></div></section>

 <section><div class="shead"><h2>Portfolio &amp; credit</h2><span class="note">Loan tape &amp; settled payments as of ${DATA.meta.as_of_date}</span></div>
 <div class="grid g4">
  ${statCard('Open receivable',fK(ta.outstanding.active_ob),ta.outstanding.active_count+' orders · avg '+f$(ta.outstanding.avg_balance),DATA.outstanding_series.slice(-10).map(p=>p.value),'')}
  ${statCard('PAR 30 (share of receivable)',fP(q.par30.pct),f$(q.par30.amount)+' · '+q.par30.count+' orders',null,q.par30.pct>0.35?'neg':(q.par30.pct>0.15?'warn':'pos'))}
  ${statCard('&gt; 90 DPD',fP(q.par90.pct),q.par90.count+' orders in judicial bucket · NPL (&gt;180d) '+fP(q.npl.pct),null,q.par90.pct>0.10?'neg':(q.par90.pct>0?'warn':'pos'))}
  ${statCard('Collections to date',fM(collectionsTot),'Regular '+fM(LT.total.collections.by_type.regular)+' · advances '+fK(LT.total.collections.by_type.advance),LT.total.collections.monthly.slice(-10).map(p=>p.value),'')}
 </div></section>

 <section><div class="shead"><h2>Borrower financial position</h2><span class="note">Loads USA, Inc. consolidated · FY${LATEST.period} vs FY${PREVF.period} (pre-audit)</span></div>
 <div class="grid g4">
  ${statCard('Revenue · FY'+LATEST.period,fM(LATEST.is_monthly.totals.revenue),'+'+fP(LATEST.ratios.revenue_growth,1)+' vs FY'+PREVF.period,S.revM,'')}
  ${statCard('Total assets',fM(LATEST.bs.total_assets),'Cash '+fK(LATEST.bs.cash)+' · receivables '+fK(LATEST.bs.trade_receivables),S.assets,'')}
  ${statCard('Stockholders’ equity',fM(eq),'Δ '+fM(eq-eqPrev)+' YoY · D/E '+fX(LATEST.ratios.debt_to_equity),S.equity,eq<0?'neg':'pos')}
  ${statCard('Net result · FY'+LATEST.period,fM(LATEST.is_monthly.totals.net_income),'FY'+PREVF.period+': '+fK(PREVF.is_monthly.totals.net_income),S.niM,LATEST.is_monthly.totals.net_income<0?'neg':'pos')}
 </div>
 <p class="footnote">Attention items: FY2025 swung to a ${fM(LATEST.is_monthly.totals.net_income)} net loss as administrative expenses nearly doubled (${fM(LATEST.is_monthly.totals.opex)} vs ${fM(PREVF.is_monthly.totals.opex)}) against a ${fP(LATEST.ratios.revenue_growth,0)} revenue expansion — the growth investment thesis in the memo. Liquidity tightened (current ratio ${fX(LATEST.ratios.current_ratio)} vs ${fX(PREVF.ratios.current_ratio)}; quick ratio ${fX(LATEST.ratios.quick_ratio)}). On the book, PAR ratios are measured against the small residual receivable — ${f$(q.par90.amount)} sits past 90 DPD in the judicial bucket, still provisioned at only ${fK(POL.expected_loss)} under the manual's grid. The FY2025 close is pre-audit (“PRE ESTADO”).</p></section>

 <section><div class="shead"><h2>Relationship timeline</h2></div>
 <div class="card pad"><div class="timeline">
  ${tl('4Q 2022','First revenue','MVP launched with first verified cross-border trades; long-term Comex / Logistics / Finance vision defined.')}
  ${tl('2023','Seed round — USD $2.0M','Nazca, Alaya and Canary; expansion into Colombia and Mexico; Loads Logistics launched.')}
  ${tl('2024','Loads Finance institutionalized','USD $2M+ originations, SPV model implemented; quoting + logistics coordination stack developed.')}
  ${tl('1Q 2025','Seed extension — USD $3.5M','FEMSA joins; Spain expansion and import department; USD 11M+ financed with NPL below 2%.')}
  ${tl('2Q 2025','Investment Memorandum','USD 11.2M financed · 86.9% collected · NPL (>180d) 1.83% · avg 33-day cycle; institutional SPV debt facility under negotiation.')}
  ${tl('Sep 2025','Current tape begins','First order in the monitored tape (issued 2025-09-17); six business units originating in USD.')}
  ${tl(DATA.meta.as_of_date.slice(0,7),'Current position',fK(ta.outstanding.active_ob)+' open receivable · '+fP(LT.total.collections.collection_rate,1)+' collected · provision '+fK(POL.expected_loss)+'.')}
 </div></div></section>`;
}
const tl=(d,t,p)=>`<div class="tl-item"><div class="d">${d}</div><div class="t">${t}</div><p>${p}</p></div>`;
function statCard(lab,val,sub,sparkVals,tone){
 return `<div class="card stat"><div class="lab">${lab}</div><div class="v num ${tone}">${val}</div><div class="d num">${sub}</div>${sparkVals?spark(sparkVals):''}</div>`;}

""")

# ---------- PORTFOLIO ----------
rep_between("/* ==================== PORTFOLIO ==================== */",
            "/* ==================== METRICS ==================== */", """/* ==================== PORTFOLIO ==================== */
let pScope=store.get('lScope','total'), pSeg=store.get('lSeg','active');
function rPortfolio(){
 if(!seg(pScope,pSeg)){pSeg='all';}
 const s=seg(pScope,pSeg), tt=seg('total',pSeg)||LT.total, f=seg('fin',pSeg)||seg('fin','all');
 const share=tt.outstanding.active_ob&&f?f.outstanding.active_ob/tt.outstanding.active_ob:0;
 const q=s.credit_quality,o=s.outstanding,w=s.weighted_averages;
 $('#view').innerHTML=`
 <div class="pagehead"><span class="eyebrow">Loan tape · ${DATA.meta.as_of_date}</span><h1>Portfolio</h1>
 <p>Order-level view of the Loads trade-receivables book. Each row of the tape is a cross-border food shipment financed against an end importer: financed exposure is the order value net of credit/debit notes, the open receivable is the amount currently due, and days past due are measured net of the 30-day commercial grace period standard to Loads’ payment terms (servicer overdue days less 30 — the first 30 days are not arrears). The Loads Finance BU is the pure financing business unit; the trading BUs (Mexico, Chile, USA, Fynsa, Logistics) originate the rest. Switch scope and lifecycle segment below — every figure follows.</p></div>

 <section class="card pad" style="display:flex;flex-wrap:wrap;gap:20px;align-items:flex-end">
  <div><span class="eyebrow" style="display:block;margin-bottom:7px">Portfolio scope</span>
   <div class="segctl" id="scopeCtl"><button data-v="total" class="${pScope==='total'?'on':''}">Total Portfolio</button><button data-v="fin" class="${pScope==='fin'?'on':''}">Loads Finance BU</button></div></div>
  <div><span class="eyebrow" style="display:block;margin-bottom:7px">Lifecycle segment</span>
   <div class="segctl" id="segCtl"><button data-v="all" class="${pSeg==='all'?'on':''}">All</button><button data-v="active" class="${pSeg==='active'?'on':''}">Open</button><button data-v="closed" class="${pSeg==='closed'?'on':''}" ${seg(pScope,'closed')?'':'disabled'}>Closed</button></div></div>
  <div style="flex:1;min-width:280px">
   <div style="display:flex;justify-content:space-between;font-size:12px;color:var(--muted);margin-bottom:6px"><span><b style="color:var(--ink)">Loads Finance BU</b> within ${tt.label}</span><span class="num">${f?fK(f.outstanding.active_ob):'—'} / ${fK(tt.outstanding.active_ob)}</span></div>
   <div class="covbar"><div class="covfill" style="width:${(share*100).toFixed(1)}%"></div><div class="covlabel num">${fP(share,1)}${f?' · '+f.outstanding.active_count+' orders':''}</div><div class="covrest num">${fK(Math.max(0,tt.outstanding.active_ob-(f?f.outstanding.active_ob:0)))} trading BUs</div></div></div>
 </section>

 <section><div class="grid g4">
  ${statCard('Open receivable',fK(o.active_ob),(o.active_count||0)+' orders'+(o.avg_balance?' · avg '+f$(o.avg_balance):''),null,'')}
  ${statCard('Gross trade margin (WA)',fP(w.gross_trade_margin,1),'Net adjustments '+fK(-Math.abs(w.net_adjustments||0))+' in credit/debit notes',null,w.gross_trade_margin<0?'neg':'')}
  ${statCard('PAR 30',fP(q.par30.pct),f$(q.par30.amount)+' · '+q.par30.count+' orders',null,q.par30.pct===0?'pos':(q.par30.pct>0.35?'neg':'warn'))}
  ${statCard('&gt; 90 DPD',fP(q.par90.pct),q.par90.count+' orders · '+f$(q.par90.amount)+' · NPL (&gt;180d) '+fP(q.npl.pct),null,q.par90.pct===0?'pos':'neg')}
  ${statCard('Financed to date',fM(s.origination.amount),s.origination.count+' orders since '+s.origination.first,null,'')}
  ${statCard('Collections to date',fM(s.collections.total),fP(s.collections.collection_rate,1)+' of financed · advances '+fK(s.collections.by_type.advance||0),null,'')}
  ${statCard('Avg ticket',f$(s.origination.avg_ticket),'Order tenor '+s.origination.tenor_days.min+'–'+s.origination.tenor_days.max+' d · WA '+w.wa_tenor_days+' d',null,'')}
  ${statCard('WA credit score',w.wa_credit_score==null?'—':w.wa_credit_score,'Loads Score 0–1000 · tier A boundary at 546',null,'')}
 </div></section>

 <section><div class="grid g2">
  <div class="card"><div class="pad"><h3>Delinquency distribution (DPD)</h3><div class="sub">Servicer overdue-days field · Manual de Crédito buckets · ${s.label}</div></div>
   <table>${dpdTable(s)}</table></div>
  <div class="card"><div class="pad"><h3>PAR ladder — Loads Finance vs total book</h3><div class="sub">Share of open receivable with DPD above threshold</div></div>
   <div class="chartbox"><canvas id="chPar"></canvas></div></div>
 </div></section>

 <section><div class="grid g2">
  <div class="card"><div class="pad"><h3>Monthly origination</h3><div class="sub">Financed exposure by issue month · Loads Finance BU overlaid on the total segment</div></div>
   <div class="chartbox"><canvas id="chOrig"></canvas></div></div>
  <div class="card"><div class="pad"><h3>Monthly collections</h3><div class="sub">Settled payments (advance + regular) · ${s.label}</div></div>
   <div class="chartbox"><canvas id="chColl"></canvas></div></div>
 </div></section>

 <section><div class="grid g21">
  <div class="card"><div class="pad" style="display:flex;justify-content:space-between;align-items:baseline"><div><h3>Cohort collection performance</h3><div class="sub">Cumulative settled cash ÷ financed exposure by issue-month cohort</div></div>
   <button class="btn ghost sm" id="expCohorts">Export CSV</button></div>
   <div class="chartbox"><canvas id="chMoic"></canvas></div></div>
  <div class="card"><div class="pad"><h3>Order status</h3><div class="sub">${s.origination.count} orders in segment</div></div>
   <div class="chartbox"><canvas id="chStatus"></canvas></div></div>
 </div></section>

 <section><div class="shead"><h2>Concentration</h2><span class="note">Counterparty, geography and score mix</span></div>
 <div class="grid g21">
  <div class="card"><div class="pad"><h3>Top importers — open receivable</h3><div class="sub">Largest obligors on the active book</div></div>
   <table><tr><th style="text-align:left;padding-left:20px">Importer</th><th>Open</th><th style="text-align:left;padding-left:0">% receivable</th><th>Orders</th></tr>
   ${CONC.importers_active_ob.map(r=>`<tr><td style="text-align:left;padding-left:20px;font-weight:600;color:var(--ink)">${r.name}</td><td class="num">${f$(r.amount)}</td>
    <td style="text-align:left" class="num">${fP(r.pct,1)}<span class="inbar"><i style="width:${Math.min(100,r.pct*100)}%"></i></span></td><td class="num">${r.count}</td></tr>`).join('')}</table></div>
  <div class="card"><div class="pad"><h3>Credit-score tiers</h3><div class="sub">Financed exposure by Loads Score tier (Manual §3.2)</div></div>
   <div class="chartbox"><canvas id="chTiers"></canvas></div></div>
 </div></section>`;

 $('#scopeCtl').onclick=e=>{const b=e.target.closest('button');if(!b)return;pScope=b.dataset.v;store.set('lScope',pScope);killCharts();rPortfolio();};
 $('#segCtl').onclick=e=>{const b=e.target.closest('button');if(!b||b.disabled)return;pSeg=b.dataset.v;store.set('lSeg',pSeg);killCharts();rPortfolio();};
 $('#expCohorts').onclick=()=>csvDownload(`loads_cohorts_${pScope}_${pSeg}.csv`,[['Cohort','Financed','Collected','Orders','Collection rate'],...s.cohorts.map(c=>[c.cohort,c.disbursed,c.collected,c.count,c.collection_rate])]);

 const pv=k=>['par30','par60','par90','npl'].map(p=>k.credit_quality[p].pct*100);
 const finForPar=seg('fin',pSeg)||seg('fin','all');
 mkChart('chPar',{type:'bar',data:{labels:['PAR 30','PAR 60','PAR 90','NPL (>180d)'],datasets:[
  {label:tt.label,data:pv(tt),backgroundColor:css('--chart-a'),borderRadius:6,barPercentage:.55},
  ...(finForPar?[{label:finForPar.label,data:pv(finForPar),backgroundColor:css('--chart-b'),borderRadius:6,barPercentage:.55}]:[])]},
  options:axis(v=>(+v).toFixed(1)+'%')});
 const fo=finForPar?finForPar.origination_monthly:[];
 const mm=[...new Set([...tt.origination_monthly,...fo].map(p=>p.month))].sort();
 const map=s2=>Object.fromEntries(s2.map(p=>[p.month,p.value]));
 const tm=map(tt.origination_monthly),am=map(fo);
 mkChart('chOrig',{type:'bar',data:{labels:mm.map(monLab),datasets:[
  {label:tt.label,data:mm.map(m=>(tm[m]||0)/1e3),backgroundColor:css('--chart-c'),borderRadius:3},
  ...(finForPar?[{label:finForPar.label,data:mm.map(m=>(am[m]||0)/1e3),backgroundColor:css('--chart-a'),borderRadius:3}]:[])]},
  options:axis(v=>'$'+(+v).toFixed(0)+'k')});
 mkChart('chColl',{type:'line',data:{labels:s.collections.monthly.map(p=>monLab(p.month)),datasets:[
  {label:s.label,data:s.collections.monthly.map(p=>p.value/1e3),borderColor:css('--chart-a'),backgroundColor:css('--chart-a')+'26',fill:true,tension:.3,pointRadius:0,borderWidth:2}]},
  options:axis(v=>'$'+(+v).toFixed(0)+'k',{legend:false,xTicks:12})});
 const fc=finForPar?finForPar.cohorts:[];
 const mo=[...new Set([...tt.cohorts,...fc].map(c=>c.cohort))].sort();
 const tmo=Object.fromEntries(tt.cohorts.map(c=>[c.cohort,c.collection_rate])),amo=Object.fromEntries(fc.map(c=>[c.cohort,c.collection_rate]));
 mkChart('chMoic',{type:'line',data:{labels:mo.map(monLab),datasets:[
  {label:tt.label,data:mo.map(m=>tmo[m]==null?null:tmo[m]*100),borderColor:css('--chart-a'),pointRadius:2,borderWidth:2,tension:.25},
  ...(finForPar?[{label:finForPar.label,data:mo.map(m=>amo[m]==null?null:amo[m]*100),borderColor:css('--chart-b'),pointRadius:2,borderWidth:2,tension:.25,borderDash:[5,4]}]:[])]},
  options:axis(v=>(+v).toFixed(0)+'%')});
 const st=s.status_distribution,keys=Object.keys(st);
 const pal=[css('--chart-a'),css('--chart-b'),css('--chart-c'),'#c9e7d6',css('--warn'),css('--neg'),'#9ab0a8','#7d968c'];
 mkChart('chStatus',{type:'doughnut',data:{labels:keys,datasets:[{data:keys.map(k=>st[k]),backgroundColor:keys.map((_,i)=>pal[i%pal.length]),borderColor:css('--surface'),borderWidth:2}]},
  options:{responsive:true,maintainAspectRatio:false,cutout:'64%',plugins:{legend:{position:'right',labels:{color:css('--muted'),font:{family:'Inter Tight',size:11.5},boxWidth:9,boxHeight:9}},tooltip:{callbacks:{label:c=>' '+c.label+': '+c.parsed+' orders'}}}}});
 const tiers=CONC.score_tiers;
 mkChart('chTiers',{type:'bar',data:{labels:tiers.map(x=>x.tier),datasets:[{label:'Financed',data:tiers.map(x=>x.amount/1e3),backgroundColor:tiers.map((x,i)=>['#0d473d','#1a6f5f','#4fb08c','#9bdcc1','#d9a84e','#c98a3e','#a8443a'][i]||css('--chart-c')),borderRadius:6,barPercentage:.6}]},
  options:{...axis(v=>'$'+(+v).toFixed(0)+'k',{legend:false})}});
}
function dpdTable(s){
 const ob=s.outstanding.active_ob;
 let h='<tr><th>Bucket</th><th>Open receivable</th><th style="text-align:left;padding-left:0">% receivable</th><th>Orders</th></tr>';
 s.credit_quality.dpd_distribution.forEach(r=>{
  const tone=r.bucket==='Current'?'ok':(r.bucket.startsWith('1–')?'warn':'bad');
  h+=`<tr><td><span class="chip ${tone}">${r.bucket}</span></td><td class="num">${f$(r.outstanding)}</td>
  <td style="text-align:left" class="num">${fP(r.pct_opb)}<span class="inbar"><i style="width:${Math.min(100,r.pct_opb*100)}%"></i></span></td><td class="num">${r.count}</td></tr>`;});
 h+=`<tr class="tot"><td>Total open</td><td class="num">${f$(ob)}</td><td style="text-align:left">${ob?'100.00%':'—'}</td><td class="num">${s.outstanding.active_count}</td></tr>`;
 return h;}

""")

# ---------- METRICS ----------
rep_between("/* ==================== METRICS ==================== */",
            "</script>\n<script>\n/* ==================== FINANCIAL STATEMENTS", """/* ==================== METRICS ==================== */
function rMetrics(){
 const r=LATEST.ratios;
 const tact=LT.total_active, q=tact.credit_quality;
 const covRows=[
  ['NPL — receivables > 180 DPD','Loads underwriting benchmark: NPL below 2%',fP(POL.npl_pct,2),'≤ 2.00%',POL.npl_pct<=0.02?'ok':'bad','Open receivable past 180 days ÷ total open receivable — memo book ran 1.83%'],
  ['Judicial bucket — > 90 DPD','Manual §5: legal process with external counsel',fP(q.par90.pct,1),'Action plan per account',q.par90.pct===0?'ok':'warn',q.par90.count+' orders · '+f$(q.par90.amount)+' — weekly Judicial Committee tracking required'],
  ['Expected-loss provision coverage','Manual §6.2 grid applied to the open receivable',fP(POL.provision_coverage,1),'Per aging grid','ok','Provision '+fK(POL.expected_loss)+' → net receivable '+fK(POL.net_receivable)],
  ['Collection rate — financed to date','Memo reference: 86.9% collected on the USD 11.2M book',fP(POL.collection_rate,1),'≥ 86.9% at maturity',POL.collection_rate>=POL.collection_benchmark?'ok':'warn','Settled cash ÷ financed exposure — current tape is young; open orders are still inside their cycle'],
  ['WA credit cycle','Structured-facility WAL band 30–45 days',POL.wa_tenor_days+' d','30 – 45 d',(POL.wa_tenor_days>=30&&POL.wa_tenor_days<=45)?'ok':'warn','Financed-weighted order tenor (issue → due) — memo average 33 days'],
  ['Minimum retention (advance rate)','Structured facility: advance ≤ 80% of assigned invoice',fP(POL.min_advance_rate,0)+' min retention','≥ 20%','ok','Tier-driven payment structures (Manual §3.2) keep 20–100% of each order milestone-linked'],
  ['Single-importer concentration','Largest obligor on the open receivable',fP(POL.importer_top1.pct,1),'Monitored — no hard limit',POL.importer_top1.pct<=0.20?'warn':'bad',POL.importer_top1.name+' · '+f$(POL.importer_top1.amount)+' across '+POL.importer_top1.count+' orders'],
  ['Borrower Debt / Equity','Consolidated leverage pending facility covenants',fX(POL.servicer_debt_to_equity),'Covenant TBD',POL.servicer_debt_to_equity<=3?'ok':'warn','Total liabilities ÷ equity per FY'+LATEST.period+' consolidated balance sheet'],
  ['Borrower equity','Going-concern floor',fM(POL.servicer_equity),'&gt; $0',POL.servicer_equity>0?'ok':'bad','Loads USA, Inc. consolidated stockholders’ equity (pre-audit FY'+LATEST.period+')'],
 ];
 const ratioDefs=[
  ['Collection rate (financed to date)',POL.collection_rate,'pct1',null],
  ['WA credit cycle',POL.wa_tenor_days,'d',null],
  ['Gross trade margin (WA)',LT.total.weighted_averages.gross_trade_margin,'pct1',null],
  ['Revenue growth (FY)',r.revenue_growth,'pct1',null],
  ['Debt / Equity',r.debt_to_equity,'x',FIN.map(f=>f.ratios.debt_to_equity)],
  ['Debt / Assets',r.debt_to_assets,'pct1',FIN.map(f=>f.ratios.debt_to_assets)],
  ['Equity ratio',r.equity_ratio,'pct1',FIN.map(f=>f.ratios.equity_ratio)],
  ['Current ratio',r.current_ratio,'x',FIN.map(f=>f.ratios.current_ratio)],
  ['Quick ratio',r.quick_ratio,'x',FIN.map(f=>f.ratios.quick_ratio)],
  ['Gross margin',r.gross_margin,'pct1',FIN.map(f=>f.ratios.gross_margin)],
  ['Operating margin',r.operating_margin,'pct1',FIN.map(f=>f.ratios.operating_margin)],
  ['Net margin',r.net_margin,'pct1',FIN.map(f=>f.ratios.net_margin)],
  ['ROA (FY)',r.roa_annualized,'pct1',FIN.map(f=>f.ratios.roa_annualized)],
  ['ROE (FY)',r.roe_annualized,'pct1',FIN.map(f=>f.ratios.roe_annualized)],
 ];
 const fmt=(v,k)=>k==='pct1'?fP(v,1):k==='x'?fX(v):k==='d'?(v==null?'—':v+' d'):v;
 $('#view').innerHTML=`
 <div class="pagehead"><span class="eyebrow">Policy compliance &amp; ratios</span><h1>Metrics</h1>
 <p>Credit-policy compliance computed from the loan tape and settled payments against the Manual de Crédito 2026 and the underwriting benchmarks in the 2Q2025 Investment Memorandum, followed by the financial ratio suite on the consolidated statements. No Addem facility covenants are executed yet — thresholds shown are policy and structuring references.</p></div>

 <section><div class="shead"><h2>Credit-policy board</h2><span class="note">As of ${DATA.meta.as_of_date} · traffic-light status</span></div>
 <div class="card">
  <div class="covhead"><span>Test</span><span>Current</span><span>Reference</span><span>Basis</span><span>Status</span></div>
  ${covRows.map(([n,s2,v,th,st,basis])=>`<div class="covrow"><div><div class="n">${n}</div><div class="s">${s2}</div></div>
   <div class="val num">${v}</div><div class="num" style="color:var(--muted)">${th}</div><div class="s">${basis}</div>
   <div><span class="chip ${st}">${st==='ok'?'Compliant':st==='warn'?'Watch':'Breach'}</span></div></div>`).join('')}
 </div>
 <p class="footnote">The provision grid (Manual §6.2): 0% through 60 DPD · 0.5% at 61–90 · 10% at 91–120 · 25% at 121–150 · 65% at 151–180 · 100% past 180 — rates derive from Loads’ historical loss behavior and are reviewed annually. The collection-rate reading is mechanically depressed while orders remain inside their 30–45 day cycle; cohort-level rates on the Portfolio page show seasoned months near or at full collection. Facility covenants (advance rate, borrowing base, concentration limits, interest reserve) will replace the reference tests once the Addem credit agreement is executed.</p></section>

 <section><div class="shead"><h2>Financial &amp; portfolio ratios</h2><span class="note">Consolidated annual closes FY${PREVF.period}–FY${LATEST.period}; sparklines show the two-year path</span></div>
 <div class="grid g4">${ratioDefs.map(([n,v,k,hist])=>{
   const tone=(n.includes('Equity')||n.includes('margin')||n.startsWith('RO'))&&v!=null&&v<0?'neg':'';
   return `<div class="card stat"><div class="lab">${n}</div><div class="v num ${tone}">${fmt(v,k)}</div>${hist&&hist.filter(x=>x!=null).length>1?spark(hist):'<div class="d">point-in-time</div>'}</div>`;}).join('')}
 </div>
 <p class="footnote">Interest coverage is not meaningful on the FY2025 close (operating loss against ${fK(23043.9)} of net financial costs). Margins and returns are computed on the annual result; the FY2025 statements are the pre-audit consolidated close of Loads USA, Inc. Portfolio ratios are cash-realized figures from the tape, not accrual yields.</p></section>

 <section><div class="grid g2">
  <div class="card"><div class="pad"><h3>Receivable, provision and financed base</h3><div class="sub">Expected-loss grid applied to the open receivable</div></div>
   <div class="chartbox"><canvas id="chCov"></canvas></div></div>
  <div class="card"><div class="pad"><h3>Leverage &amp; equity</h3><div class="sub">Consolidated balance-sheet evolution</div></div>
   <div class="chartbox"><canvas id="chLev"></canvas></div></div>
 </div></section>`;
 mkChart('chCov',{type:'bar',data:{labels:['Open receivable','Expected-loss provision','Net receivable','Financed to date'],datasets:[{label:'USD',data:[LT.total_active.outstanding.active_ob/1e3,POL.expected_loss/1e3,POL.net_receivable/1e3,financedTot/1e3],backgroundColor:[css('--chart-a'),css('--neg'),css('--chart-b'),css('--chart-c')],borderRadius:8,barPercentage:.55}]},
  options:{...axis(v=>'$'+(+v).toFixed(0)+'k',{legend:false}),indexAxis:'y'}});
 mkChart('chLev',{type:'bar',data:{labels:PERIODS.map(monLab),datasets:[
  {label:'Total assets',data:S.assets.map(v=>v&&v/1e6),backgroundColor:css('--chart-b'),borderRadius:5},
  {label:'Total liabilities',data:S.liabilities.map(v=>v&&v/1e6),backgroundColor:css('--chart-a'),borderRadius:5},
  {label:'Equity',data:S.equity.map(v=>v&&v/1e6),backgroundColor:css('--chart-c'),borderRadius:5}]},
  options:axis(v=>'$'+(+v).toFixed(1)+'M')});
}
""")

# ---------- FINANCIAL STATEMENTS (label-level edits) ----------
rep('<div class="pagehead"><span class="eyebrow">Servicer financials · Asaak FSL MX, S. de R.L. de C.V.</span><h1>Financial Statements</h1>\n <p>Interactive monthly financials parsed from the accountant\'s closes — QuickBooks (April 2026) and CONTPAQ i (May 2026). Sections expand into full account detail. Statements are monthly-period figures; the fiscal-year-to-date result is carried on the balance sheet.</p></div>',
    '<div class="pagehead"><span class="eyebrow">Borrower financials · Loads USA, Inc. (consolidated)</span><h1>Financial Statements</h1>\n <p>Interactive consolidated statements parsed from the statutory close — statement of financial position and income statement by function for the years ended 31 December 2025 and 2024, in US dollars. Sections expand into full line detail. The FY2025 figures are the pre-audit close (“PRE ESTADO”); the audited statements govern.</p></div>')
rep("${statCard('Revenue · month',fM(tot.revenue),'',null,'')}",
    "${statCard('Revenue · '+monLab(fsMonth),fM(tot.revenue),f.ratios.revenue_growth!=null?'+'+fP(f.ratios.revenue_growth,1)+' YoY':'',null,'')}")
rep("${statCard('Net result',fM(tot.net_income),'FY-to-date '+fM(f.ytd_net_income),null,tot.net_income<0?'neg':'pos')}",
    "${statCard('Net result',fM(tot.net_income),'Full fiscal year',null,tot.net_income<0?'neg':'pos')}")
rep('<h3>Income statement — month</h3><div class="sub">${monLab(fsMonth)} · click a section to expand detail</div>',
    '<h3>Income statement — fiscal year</h3><div class="sub">${monLab(fsMonth)} · by function · click a section to expand detail</div>')
rep('<h3>Balance sheet</h3><div class="sub">Statement of financial position as of ${monLab(fsMonth)} · click to expand</div>',
    '<h3>Balance sheet</h3><div class="sub">Statement of financial position · 31 Dec ${fsMonth} · click to expand</div>')
rep('<h3>Revenue vs net result</h3><div class="sub">Monthly closes available to the platform</div>',
    '<h3>Revenue vs net result</h3><div class="sub">Annual closes available to the platform</div>')
rep('<h3>Balance sheet structure</h3><div class="sub">Assets, liabilities and equity by close</div>',
    '<h3>Balance sheet structure</h3><div class="sub">Assets, liabilities and equity by fiscal year</div>')
rep("<p class=\"footnote\">April is reported from the QuickBooks close of Asaak MX; May from the CONTPAQ i close of Asaak FSL MX S de RL de CV. FY-to-date reconciliation holds across systems (YTD May = YTD April + May result, drift &lt; MXN $1). ASAAK facility debt sits at the Mifel trust, not on the servicer balance sheet; long-term funding shown is intercompany (Asaak Financial Services Ltd), the FlexClub absorption note and Untapped.</p>",
    "<p class=\"footnote\">Both years are consolidated statutory closes of Loads USA, Inc. in USD; statement articulation is validated in the ETL (current assets tie, balance sheet balances, pre-tax + tax = net result, drift &lt; $1). FY2025 shows the growth investment: revenue +${fP(LATEST.ratios.revenue_growth,0)} with administrative expenses at ${fM(LATEST.is_monthly.totals.opex)}, a ${fM(LATEST.is_monthly.totals.net_income)} net loss, and paid-in capital reduced $200k to ${fM(LATEST.bs.paid_in_capital)}. SPV facility debt would sit at the ring-fenced vehicle, not on this consolidated balance sheet.</p>")
rep("csvDownload(`asaak_is_${fsMonth}.csv`,rows);",
    "csvDownload(`loads_is_fy${fsMonth}.csv`,rows);")
rep("[['income','Revenue'],['cost','Cost of sales'],['opex','Operating expenses'],['other','Financial result & other']]",
    "[['income','Revenue'],['cost','Cost of operations'],['opex','Administrative expenses'],['other','Financial result, indexation & tax']]")
rep("  +sec('cost','Cost of sales & fleet',tot.cost)",
    "  +sec('cost','Cost of operations',tot.cost)")
rep("  +sec('opex','Operating expenses',tot.opex)",
    "  +sec('opex','Administrative expenses',tot.opex)")
rep("  +sec('other','Financial result & other',tot.other)",
    "  +sec('other','Financial result, indexation & tax',tot.other)")
rep("`<div class=\"fs-grand\"><span>Gross profit</span>", "`<div class=\"fs-grand\"><span>Operating profit (Utilidad en operaciones)</span>")

# ---------- CREDIT FACILITY ----------
rep_between("/* ==================== CREDIT FACILITY ==================== */",
            "/* ==================== PERFORMANCE ==================== */", """/* ==================== CREDIT FACILITY ==================== */
let facTab=store.get('lFacTab','FACILITY');
const fact=(k,v)=>v?`<div class="f"><div class="k">${k}</div><div class="v">${v}</div></div>`:'';
const dotlist=(items,tone)=>items.map(x=>`<div style="display:flex;gap:10px;padding:8px 0;border-bottom:1px dashed var(--border);font-size:13px"><span class="dot ${tone}" style="margin-top:6px;flex-shrink:0"></span><span>${x}</span></div>`).join('');
function rFacility(){
 const c=CT[facTab];
 $('#view').innerHTML=`
 <div class="pagehead"><span class="eyebrow">Legal · facility &amp; credit policy</span><h1>Credit Facility</h1>
 <p>Fact sheets for the Loads relationship. The SPV structured facility reflects the profile in the 2Q2025 Investment Memorandum — indicative until an Addem credit agreement is executed. The Manual de Crédito, Recuperación y Cobranza 2026 is the borrower's operating credit policy: scoring, tier-based payment structures, collections cadence and expected-loss provisioning.</p></div>

 <section style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-bottom:14px">
  <div class="segctl" id="facCtl"><button data-v="FACILITY" class="${facTab==='FACILITY'?'on':''}">SPV Structured Facility</button><button data-v="MANUAL" class="${facTab==='MANUAL'?'on':''}">Credit Manual 2026</button></div>
  <span class="chip ${facTab==='FACILITY'?'warn':'ok'}">${c.status}</span>
 </section>

 ${facTab==='FACILITY'?facilityHTML(c):manualHTML(c)}`;
 $('#facCtl').onclick=e=>{const b=e.target.closest('button');if(!b)return;facTab=b.dataset.v;store.set('lFacTab',facTab);rFacility();};
}
function facilityHTML(c){
 return `
 <section><div class="hero-strip">
  <span class="eyebrow">${c.name}</span>
  <h2>Short-duration, insured trade receivables at ${c.annualized_yield.replace('≈ ','~')}</h2>
  <p>${c.structure}. ${c.equity_contribution}.</p>
  <div class="hero-kpis">
   <div class="k"><div class="lab">Discount per cycle</div><div class="v num"><em>~4%</em></div><div class="d">${c.annualized_yield} annualized</div></div>
   <div class="k"><div class="lab">Minimum retention</div><div class="v num">20%</div><div class="d">advance ≤ 80% of invoice</div></div>
   <div class="k"><div class="lab">WAL</div><div class="v num">30–45 d</div><div class="d">1–4 milestone payments</div></div>
   <div class="k"><div class="lab">First-loss equity</div><div class="v num">10–30%</div><div class="d">per SPV structure</div></div>
   <div class="k"><div class="lab">Credit insurance</div><div class="v num">≤ 90%</div><div class="d">per qualified operation</div></div>
  </div></div></section>

 <section><div class="shead"><h2>Key terms</h2></div><div class="fact">
  ${fact('Lender',c.lender)}${fact('Borrower',c.borrower)}
  ${fact('Obligor',c.obligor)}${fact('Structure',c.structure)}
  ${fact('Coupon structure',c.coupon_structure)}${fact('Advance / retention',c.advance_rate)}
  ${fact('Pricing',c.discount_rate+' · '+c.annualized_yield)}${fact('Typical ticket',c.typical_ticket)}
  ${fact('Weighted average life',c.wal)}${fact('Collateral',c.collateral)}
  ${fact('Insurance',c.insurance)}${fact('Assignment mechanism',c.assignment)}
  ${fact('Funding process',c.funding_process)}${fact('First-loss equity',c.equity_contribution)}
 </div></section>

 <section><div class="grid g2">
  <div class="card pad"><h3>Eligibility criteria</h3><div class="sub" style="margin-bottom:10px">Underwriting gates per the Credit Manual and memo</div>
   ${dotlist(c.eligibility,'ok')}</div>
  <div class="card pad"><h3>Concentration &amp; structural limits</h3><div class="sub" style="margin-bottom:10px">Structuring references — hard limits to be set in the credit agreement</div>
   <table><tr><th style="text-align:left">Limit</th><th>Reference</th></tr>
   ${c.concentration_limits.map(x=>`<tr><td style="text-align:left;color:var(--muted)">${x.limit}</td><td class="num" style="font-weight:600;color:var(--ink)">${x.threshold}</td></tr>`).join('')}</table></div>
 </div></section>

 <section><div class="grid g2">
  <div class="card pad"><h3>Default &amp; recovery mechanics</h3><div class="sub" style="margin-bottom:10px">Per the Manual de Crédito collections framework</div>
   ${dotlist(c.key_defaults,'bad')}</div>
  <div class="card pad"><h3>Reporting &amp; monitoring</h3><div class="sub" style="margin-bottom:10px">Operating cadence available to the lender</div>
   ${dotlist(c.reporting,'ok')}</div>
 </div></section>

 <section><div class="card pad"><h3>Legal timeline</h3><div class="sub" style="margin-bottom:14px">Financing documentation history</div>
   <div class="timeline">
    ${tl('2024','SPV model implemented','Loads Finance institutionalized: invoice assignment into a ring-fenced SPV; USD 2M+ originated.')}
    ${tl('1Q 2025','Seed extension (USD 3.5M)','FEMSA joins the cap table; insurance programme migrated post-Coface with up to 90% coverage per operation.')}
    ${tl('2Q 2025','Investment Memorandum','Structured-facility profile circulated: min 20% retention, ~4% discount per cycle, 30–45d WAL, milestone-linked payments.')}
    ${tl('2026','Manual de Crédito 2026 in force','Unified credit, recovery and collections policy signed; provisioning grid and committee cadence formalized.')}
    ${tl('H2 2026','Addem structuring','Term sheet in progress — borrowing base, concentration limits and reporting covenants to be executed in the credit agreement.')}
   </div></div></section>`;
}
function manualHTML(c){
 return `
 <section><div class="hero-strip">
  <span class="eyebrow">${c.name}</span>
  <h2>One operating standard from origination to recovery</h2>
  <p>${c.scope}. ${c.origination}.</p>
  <div class="hero-kpis">
   <div class="k"><div class="lab">Score range</div><div class="v num">0–1000</div><div class="d">7 tiers AAA → E</div></div>
   <div class="k"><div class="lab">New client SLA</div><div class="v num">72 h</div><div class="d">new order 24 h</div></div>
   <div class="k"><div class="lab">Collections buckets</div><div class="v num">4</div><div class="d">preventive → judicial</div></div>
   <div class="k"><div class="lab">Write-off provision</div><div class="v num">100%</div><div class="d">past 180 DPD</div></div>
  </div></div></section>

 <section><div class="grid g2">
  <div class="card pad"><h3>Credit Scoring — four weighted blocks</h3><div class="sub" style="margin-bottom:10px">§3.1 — sources behind the 0–1000 score</div>
   ${c.scoring_blocks.map(b=>`<div style="padding:9px 0;border-bottom:1px dashed var(--border)"><div style="display:flex;justify-content:space-between;font-weight:600;color:var(--ink);font-size:13px"><span>Block ${b.block}</span><span class="num">${b.weight}</span></div><div style="font-size:12.5px;color:var(--muted)">${b.detail}</div></div>`).join('')}</div>
  <div class="card pad"><h3>Risk mitigation &amp; documents</h3><div class="sub" style="margin-bottom:10px">§4 &amp; §6.1</div>
   ${fact('Mitigation',c.mitigation)}${fact('Decision SLAs',c.sla)}${fact('Documentary set',c.documents)}</div>
 </div></section>

 <section><div class="card"><div class="pad"><h3>Score tiers &amp; recommended financing structure</h3><div class="sub">§3.2 — the tier drives the payment structure offered on every order</div></div>
  <div class="scrolly"><table>
  <thead><tr><th>Tier</th><th>Range</th><th style="text-align:left">Client profile</th><th style="text-align:left">Recommended structure</th></tr></thead><tbody>
  ${c.tiers.map(x=>`<tr><td><span class="chip ${['AAA','AA','A'].includes(x.tier)?'ok':(['B','C'].includes(x.tier)?'warn':'bad')}">${x.tier}</span></td><td class="num">${x.range}</td><td style="text-align:left;color:var(--muted)">${x.profile}</td><td style="text-align:left;font-weight:600;color:var(--ink)">${x.structure}</td></tr>`).join('')}
  </tbody></table></div></section>

 <section><div class="grid g2">
  <div class="card"><div class="pad"><h3>Collections cadence</h3><div class="sub">§5 — buckets by days past due with weekly committees</div></div>
   <div class="pad" style="padding-top:0">${c.collections.map(x=>`<div style="padding:9px 0;border-bottom:1px dashed var(--border)"><div style="font-weight:600;color:var(--ink);font-size:13px">${x.bucket}</div><div style="font-size:12.5px;color:var(--muted)">${x.plan}</div></div>`).join('')}</div></div>
  <div class="card"><div class="pad"><h3>Expected-loss provisioning grid</h3><div class="sub">§6.2 — applied by aging bucket; reviewed annually</div></div>
   <table><tr><th style="text-align:left;padding-left:20px">Receivable aging</th><th>Provision rate</th></tr>
   ${POL.provision_grid.map(x=>`<tr><td style="text-align:left;padding-left:20px;color:var(--muted)">${x.bucket}</td><td class="num" style="font-weight:600;color:${x.rate>=0.5?'var(--neg)':x.rate>0?'var(--warn)':'var(--ink)'}">${fP(x.rate,1)}</td></tr>`).join('')}</table></div>
 </div></section>`;
}

""")

# ---------- PERFORMANCE ----------
rep_between("/* ==================== PERFORMANCE ==================== */",
            "/* ==================== DOCUMENTS ==================== */", """/* ==================== PERFORMANCE ==================== */
function rPerformance(){
 const coll=LT.total.collections.monthly,orig=LT.total.origination_monthly;
 const months=[...new Set([...coll,...orig].map(p=>p.month))].sort();
 const cmap=Object.fromEntries(coll.map(p=>[p.month,p.value])),omap=Object.fromEntries(orig.map(p=>[p.month,p.value]));
 let c1=0,c2=0;const cumColl=months.map(m=>(c1+=cmap[m]||0)/1e6),cumOrig=months.map(m=>(c2+=omap[m]||0)/1e6);
 const os=DATA.outstanding_series;
 $('#view').innerHTML=`
 <div class="pagehead"><span class="eyebrow">Executive review</span><h1>Portfolio Performance</h1>
 <p>The Loads trade-receivables book in four movements: how financed exposure deployed since the tape opens in September 2025, what the open receivable did underneath as milestone payments settled, where the book concentrates by destination market, and the credit picture that results under the Manual de Crédito aging.</p></div>

 <section><div class="card"><div class="pad"><h3>1 · Deployment vs cash back</h3><div class="sub">Cumulative financed exposure against cumulative settled collections — the gap is capital at work in transit</div></div>
  <div class="chartbox tall"><canvas id="chDeploy"></canvas></div></div></section>

 <section><div class="grid g2">
  <div class="card"><div class="pad"><h3>2 · Open receivable balance</h3><div class="sub">Reconstructed month-end receivable: financed exposure less settled payments and closing adjustments</div></div>
   <div class="chartbox"><canvas id="chGrow"></canvas></div></div>
  <div class="card"><div class="pad"><h3>3 · Destination markets</h3><div class="sub">Financed exposure by importer country — the demand side of the book</div></div>
   <div class="chartbox"><canvas id="chStack"></canvas></div></div>
 </div></section>

 <section><div class="grid g2">
  <div class="card"><div class="pad"><h3>4 · Credit quality</h3><div class="sub">DPD distribution of the open receivable — total book vs Loads Finance BU</div></div>
   <div class="chartbox"><canvas id="chQual"></canvas></div></div>
  <div class="card"><div class="pad"><h3>Borrower result &amp; equity</h3><div class="sub">Consolidated annual net result with the equity path underneath</div></div>
   <div class="chartbox"><canvas id="chEq"></canvas></div></div>
 </div>
 <p class="footnote">PAR evolution over time requires historical tape snapshots; this dataset carries one tape (as of ${DATA.meta.as_of_date}), so credit quality is shown as the latest aged distribution. Feeding weekly Back Office cuts into the ETL unlocks the PAR time series automatically. Supply side of the book: ${CONC.supplier_countries_financed.slice(0,3).map(x=>x.name+' '+fP(x.pct,0)).join(' · ')} of financed exposure by supplier country.</p></section>`;
 mkChart('chDeploy',{type:'line',data:{labels:months.map(monLab),datasets:[
  {label:'Cumulative financed',data:cumOrig,borderColor:css('--chart-a'),backgroundColor:css('--chart-a')+'18',fill:true,pointRadius:0,borderWidth:2,tension:.25},
  {label:'Cumulative collections',data:cumColl,borderColor:css('--chart-b'),backgroundColor:css('--chart-b')+'22',fill:true,pointRadius:0,borderWidth:2,tension:.25}]},
  options:axis(v=>'$'+(+v).toFixed(1)+'M',{xTicks:12})});
 mkChart('chGrow',{type:'line',data:{labels:os.map(p=>monLab(p.month)),datasets:[
  {label:'Open receivable',data:os.map(p=>p.value/1e6),borderColor:css('--chart-a'),backgroundColor:css('--chart-a')+'15',fill:true,pointRadius:0,borderWidth:2,tension:.25}]},
  options:axis(v=>'$'+(+v).toFixed(1)+'M',{legend:false,xTicks:12})});
 const dc=CONC.importer_countries_financed;
 mkChart('chStack',{type:'bar',data:{labels:dc.map(x=>x.name),datasets:[{label:'Financed',data:dc.map(x=>x.amount/1e3),backgroundColor:css('--chart-a'),borderRadius:6,barPercentage:.6}]},
  options:{...axis(v=>'$'+(+v).toFixed(0)+'k',{legend:false}),indexAxis:'y'}});
 const dT=LT.total_active.credit_quality.dpd_distribution,fseg=seg('fin','active')||LT.fin,dA=fseg.credit_quality.dpd_distribution;
 mkChart('chQual',{type:'bar',data:{labels:dT.map(d=>d.bucket),datasets:[
  {label:'Total open book',data:dT.map(d=>d.pct_opb*100),backgroundColor:css('--chart-c'),borderRadius:4},
  {label:'Loads Finance BU',data:dA.map(d=>d.pct_opb*100),backgroundColor:css('--chart-a'),borderRadius:4}]},
  options:axis(v=>(+v).toFixed(1)+'%')});
 mkChart('chEq',{type:'bar',data:{labels:PERIODS.map(monLab),datasets:[
  {label:'Annual net result',data:S.niM.map(v=>v==null?null:v/1e6),backgroundColor:S.niM.map(v=>v!=null&&v>=0?css('--pos'):css('--neg')),borderRadius:4,order:2},
  {label:'Equity (EoY)',type:'line',data:S.equity.map(v=>v&&v/1e6),borderColor:css('--chart-a'),pointRadius:3,borderWidth:2,tension:.25,order:1}]},
  options:axis(v=>'$'+(+v).toFixed(1)+'M')});
}

""")

# ---------- WORKSPACE & SETTINGS text ----------
rep("let tasks=store.get('asaakTasks',null)||seedTasks();", "let tasks=store.get('loadsTasks',null)||seedTasks();")
rep("const saveTasks=()=>store.set('asaakTasks',tasks);", "const saveTasks=()=>store.set('loadsTasks',tasks);")
rep("let wsView=store.get('aWsView','kanban')", "let wsView=store.get('lWsView','kanban')")
rep("store.set('aWsView',wsView);", "store.set('lWsView',wsView);")
rep("<p>Deal-team task tracking for the Asaak relationship, seeded from the team's Asana history plus the facility's forward monitoring calendar. Tasks persist locally in this browser.</p>",
    "<p>Deal-team task tracking for the Loads relationship, seeded with the diligence and forward monitoring calendar of the SPV facility structuring. Tasks persist locally in this browser.</p>")

rep_between('<tr><td style="text-align:left">Loan tape</td>',
            '<tr><td style="text-align:left">Google Drive sync</td>', """<tr><td style="text-align:left">Loan tape</td><td class="num">as of ${DATA.meta.as_of_date} · ${LT.total.origination.count} orders · 6 business units</td></tr>
    <tr><td style="text-align:left">Payment detail</td><td class="num">172 settled rows + 160 expected milestones · 2025–2026</td></tr>
    <tr><td style="text-align:left">Financial statements</td><td class="num">${PERIODS.length} consolidated annual closes (FY2024 · FY2025 pre-audit)</td></tr>
    <tr><td style="text-align:left">Credit policy</td><td class="num">Manual de Crédito 2026 (in force) · SPV facility (indicative)</td></tr>
    """)
rep("<tr><td style=\"text-align:left\">Application</td><td class=\"num\">Asaak Institutional Reporting · v1.0</td></tr>",
    "<tr><td style=\"text-align:left\">Application</td><td class=\"num\">Loads Institutional Reporting · v1.0</td></tr>")
rep("<tr><td style=\"text-align:left\">Owner</td><td class=\"num\">Addem Capital (Goldberg-Zogovic SOFOM ENR)</td></tr>",
    "<tr><td style=\"text-align:left\">Owner</td><td class=\"num\">Addem Capital</td></tr>")
rep("<tr><td style=\"text-align:left\">Currency</td><td class=\"num\">MXN</td></tr>",
    "<tr><td style=\"text-align:left\">Currency</td><td class=\"num\">USD</td></tr>")

assert "Asaak" not in t and "ASAAK" not in t and "asaak" not in t, "leftover Asaak refs: " + \
    "; ".join(sorted({ln.strip()[:90] for ln in t.splitlines() if 'saak' in ln.lower()}))
DST.write_text(t, encoding="utf-8")
print("template written:", len(t)//1024, "KB")
