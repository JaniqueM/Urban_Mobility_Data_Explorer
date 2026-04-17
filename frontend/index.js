const API = 'http://localhost:5000/api';
const $ = id => document.getElementById(id);
const C = { ink:'#0a0a0a', ink3:'#767676', accent:'#e5241c', rule:'#ebebeb' };
const DAYS = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'];

// State
let state = { page:1, perPage:20, hour:'', day:'', passengers:'', sortBy:'pickup_datetime', sortDir:'desc', search:'' };
let charts = {};

// Populate hour filter
(function(){
    const sel = $('fHour');
    for(let h=0;h<24;h++){
        const o=document.createElement('option');
        o.value=h; o.textContent=`${String(h).padStart(2,'0')}:00`; sel.appendChild(o);
    }
})();

// Utilities
function fmt(n,d=0){ return n==null||isNaN(n)?'—':Number(n).toLocaleString('en-US',{minimumFractionDigits:d,maximumFractionDigits:d}); }
function fmtCompact(n){ const x=Number(n); return x>=1e6?(x/1e6).toFixed(2).replace(/\.?0+$/,'')+'M':x>=1e3?(x/1e3).toFixed(1).replace(/\.?0+$/,'')+'K':fmt(x); }
function fmtTime(s){ try{return new Date(s).toLocaleString('en-US',{month:'short',day:'numeric',hour:'2-digit',minute:'2-digit',hour12:false})}catch{return s||'—'} }
function escH(s){ return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])) }
function toast(msg,err){
    const t=$('toast'); t.textContent=msg; t.className='toast show'+(err?' err':'');
    clearTimeout(t._t); t._t=setTimeout(()=>t.classList.remove('show'),2800);
}
function setStatus(on,txt){ $('statusDot').className='status-dot '+(on?'online':'offline'); $('statusText').textContent=txt; }

// Chart setup
if(window.Chart){
    Chart.defaults.font.family="'Hanken Grotesk',sans-serif";
    Chart.defaults.font.size=11;
    Chart.defaults.color=C.ink3;
    Chart.defaults.plugins.tooltip.backgroundColor=C.ink;
    Chart.defaults.plugins.tooltip.titleColor='#fff';
    Chart.defaults.plugins.tooltip.bodyColor=C.accent;
    Chart.defaults.plugins.tooltip.padding=10;
    Chart.defaults.plugins.tooltip.cornerRadius=0;
    Chart.defaults.plugins.tooltip.displayColors=false;
    Chart.defaults.plugins.tooltip.titleFont={family:"'JetBrains Mono',monospace",size:9,weight:'600'};
    Chart.defaults.plugins.tooltip.bodyFont={family:"'Hanken Grotesk',sans-serif",size:13,weight:'700'};
}

function co(yTitle){
    return {
        responsive:true,maintainAspectRatio:false,animation:{duration:600,easing:'easeOutQuad'},
        plugins:{legend:{display:false}},
        scales:{
            x:{grid:{display:false},border:{color:C.ink,width:1},ticks:{color:C.ink3,font:{family:"'JetBrains Mono',monospace",size:9,weight:'500'}}},
            y:{beginAtZero:true,grid:{color:C.rule,drawBorder:false,lineWidth:1},border:{display:false},ticks:{color:C.ink3,font:{family:"'JetBrains Mono',monospace",size:9,weight:'500'}},title:yTitle?{display:true,text:yTitle,color:C.ink3,font:{family:"'JetBrains Mono',monospace",size:9}}:undefined}
        }
    };
}

function mkChart(id, cfg){
    if(charts[id]) charts[id].destroy();
    charts[id] = new Chart($(id).getContext('2d'), cfg);
}

// API fetch
async function api(path){
    const r = await fetch(API+path);
    if(!r.ok) throw new Error(r.status);
    return r.json();
}

// ── Stats / KPIs ──────────────────────────────────────────────────────────────
async function loadStats(){
    try{
        const d = await api('/stats');
        $('heroTrips').textContent = fmtCompact(d.total_trips);
        $('kpiTrips').innerHTML = '<span style="font-size:0.65em;letter-spacing:-0.01em">'+fmtCompact(d.total_trips)+'</span>';
        $('kpiDuration').innerHTML = fmt(d.avg_duration_min,1)+'<span class="sub">min</span>';
        $('kpiSpeed').innerHTML = fmt(d.avg_speed_kmh,1)+'<span class="sub">km/h</span>';
        $('kpiPassengers').innerHTML = fmt(d.avg_passengers,2)+'<span class="sub">avg</span>';
        // Date range
        const e=d.earliest?.slice(0,7),l=d.latest?.slice(0,7);
        $('kpiDateRange').innerHTML='<span style="font-size:0.5em;letter-spacing:-0.01em">'+(e||'—')+'<br>→ '+(l||'—')+'</span>';
        setStatus(true,'Live');
    } catch(e){
        setStatus(false,'Offline');
        toast('Backend offline — start Flask: python app.py',true);
    }
}

// ── Vendor compare ────────────────────────────────────────────────────────────
async function loadVendors(){
    try{
        const rows = await api('/trips/vendor-comparison');
        rows.forEach(v=>{
            const n = v.vendor_id;
            $(`v${n}Trips`).textContent = fmtCompact(v.total_trips);
            $(`v${n}Dur`).textContent = fmt(v.avg_duration,1)+'m';
            $(`v${n}Speed`).textContent = fmt(v.avg_speed,1)+'km/h';
            $(`v${n}Pax`).textContent = fmt(v.avg_passengers,2);
        });
        // Chart
        const ph=$('phVendor'); if(ph) ph.style.display='none';
        mkChart('chartVendor',{
            type:'bar', data:{
                labels:rows.map(r=>'Vendor '+r.vendor_id+' · '+fmtCompact(r.total_trips)+' trips'),
                datasets:[{data:rows.map(r=>r.total_trips),backgroundColor:[C.ink,C.accent],borderRadius:0,maxBarThickness:80}]
            },
            options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,animation:{duration:600},plugins:{legend:{display:false}},scales:{
                    x:{beginAtZero:true,grid:{color:C.rule,drawBorder:false},ticks:{color:C.ink3,font:{family:"'JetBrains Mono',monospace",size:9,weight:'500'}}},
                    y:{grid:{display:false},border:{color:C.ink},ticks:{color:C.ink,font:{family:"'Hanken Grotesk',sans-serif",size:13,weight:'600'}}}
                }}
        });
    } catch{}
}

// ── Hourly chart ──────────────────────────────────────────────────────────────
async function loadHourly(){
    try{
        const rows = await api('/trips/by-hour');
        const ph=$('phHourly'); if(ph) ph.style.display='none';
        mkChart('chartHourly',{
            type:'bar', data:{
                labels:rows.map(r=>String(r.hour).padStart(2,'0')),
                datasets:[{data:rows.map(r=>r.trip_count),backgroundColor:rows.map(r=>r.hour>=17&&r.hour<=20?C.accent:C.ink),borderRadius:0,maxBarThickness:14}]
            },
            options:{...co('TRIPS'),plugins:{...co('TRIPS').plugins,tooltip:{...Chart.defaults.plugins.tooltip,callbacks:{title:i=>`${String(i[0].label).padStart(2,'0')}:00`,body:i=>fmt(i[0].raw)+' trips'}}}}
        });
    } catch{ const ph=$('phHourly'); if(ph){ph.style.display='grid';ph.textContent='Unavailable';} }
}

// ── Daily chart ───────────────────────────────────────────────────────────────
async function loadDaily(){
    try{
        const rows = await api('/trips/by-day');
        const ph=$('phDaily'); if(ph) ph.style.display='none';
        mkChart('chartDaily',{
            type:'bar', data:{
                labels:rows.map(r=>DAYS[r.day_of_week]),
                datasets:[{data:rows.map(r=>r.trip_count),backgroundColor:rows.map(r=>r.day_of_week>=3&&r.day_of_week<=4?C.accent:C.ink),borderRadius:0,maxBarThickness:40}]
            },
            options:co('TRIPS')
        });
    } catch{ const ph=$('phDaily'); if(ph){ph.style.display='grid';ph.textContent='Unavailable';} }
}

// ── Monthly chart ─────────────────────────────────────────────────────────────
async function loadMonthly(){
    try{
        const rows = await api('/trips/monthly-trend');
        const ph=$('phMonthly'); if(ph) ph.style.display='none';
        mkChart('chartMonthly',{
            type:'line', data:{
                labels:rows.map(r=>r.month),
                datasets:[{data:rows.map(r=>r.trip_count),borderColor:C.ink,backgroundColor:'rgba(10,10,10,0.06)',borderWidth:2,tension:0.25,fill:true,pointRadius:5,pointBackgroundColor:C.accent,pointBorderColor:C.ink,pointBorderWidth:1.5,pointHoverRadius:7}]
            },
            options:co('TRIPS')
        });
    } catch{ const ph=$('phMonthly'); if(ph){ph.style.display='grid';ph.textContent='Unavailable';} }
}

// ── Duration chart ────────────────────────────────────────────────────────────
async function loadDuration(){
    try{
        const rows = await api('/trips/by-duration');
        const ph=$('phDuration'); if(ph) ph.style.display='none';
        mkChart('chartDuration',{
            type:'bar', data:{
                labels:rows.map(r=>r.bucket+'m'),
                datasets:[{data:rows.map(r=>r.trip_count),backgroundColor:C.ink,borderRadius:0,maxBarThickness:22}]
            },
            options:co('TRIPS')
        });
    } catch{ const ph=$('phDuration'); if(ph){ph.style.display='grid';ph.textContent='Unavailable';} }
}

// ── Speed chart ───────────────────────────────────────────────────────────────
async function loadSpeed(){
    try{
        const rows = await api('/trips/speed-distribution');
        const ph=$('phSpeed'); if(ph) ph.style.display='none';
        mkChart('chartSpeed',{
            type:'bar', data:{
                labels:rows.map(r=>r.bucket+'km'),
                datasets:[{data:rows.map(r=>r.count),backgroundColor:C.accent,borderRadius:0,maxBarThickness:22}]
            },
            options:co('TRIPS')
        });
    } catch{ const ph=$('phSpeed'); if(ph){ph.style.display='grid';ph.textContent='Unavailable';} }
}

// ── Passengers chart ──────────────────────────────────────────────────────────
async function loadPassengers(){
    try{
        const rows = await api('/trips/by-passenger');
        const ph=$('phPassengers'); if(ph) ph.style.display='none';
        mkChart('chartPassengers',{
            type:'bar', data:{
                labels:rows.map(r=>r.passenger_count+' pax'),
                datasets:[{data:rows.map(r=>r.trip_count),backgroundColor:rows.map((_,i)=>i===0?C.ink:C.accent),borderRadius:0,maxBarThickness:32}]
            },
            options:co('TRIPS')
        });
    } catch{ const ph=$('phPassengers'); if(ph){ph.style.display='grid';ph.textContent='Unavailable';} }
}

// ── DSA Quicksort Rankings ────────────────────────────────────────────────────
async function loadRankings(){
    try{
        const d = await api('/trips/peak-hours-ranked');
        const ranked = d.ranked || [];
        const top = ranked[0], bot = ranked[ranked.length-1];
        const maxCount = top?.trip_count || 1;

        // Insights
        $('ins1Val').textContent = top ? String(top.hour).padStart(2,'0')+':00' : '—';
        $('ins1Label').textContent = top ? `${fmt(top.trip_count)} trips · ${fmt(top.avg_duration,1)} min avg duration` : '—';
        $('ins2Val').textContent = bot ? String(bot.hour).padStart(2,'0')+':00' : '—';
        $('ins2Label').textContent = bot ? `${fmt(bot.trip_count)} trips — the city's quietest hour by demand.` : '—';
        if(top && bot){
            const ratio = (top.trip_count/bot.trip_count).toFixed(1);
            $('ins3Val').textContent = ratio+'×';
        }

        // DSA visual (top 8 hours)
        const top8 = ranked.slice(0,8);
        $('dsaRanking').innerHTML = top8.map((r,i)=>{
            const pct = Math.round((r.trip_count/maxCount)*100);
            return `<div class="rank-item">
        <div class="rank-badge">#${i+1}</div>
        <div class="rank-hour">${String(r.hour).padStart(2,'0')}:00</div>
        <div class="rank-count">${fmtCompact(r.trip_count)} trips</div>
        <div class="rank-bar" style="width:${pct}%"></div>
      </div>`;
        }).join('');
    } catch(e){ $('dsaRanking').innerHTML='<div style="padding:20px;font-family:var(--mono);font-size:11px;color:var(--ink-3);">Rankings unavailable</div>'; }
}

// ── Map ────────────────────────────────────────────────────────────────────────
let lmap=null, heatLayer=null;
function initMap(){
    if(lmap) return;
    lmap = L.map('pickupMap',{zoomControl:true,scrollWheelZoom:false}).setView([40.758,-73.9855],12);
    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png',{maxZoom:18,attribution:'&copy; OSM &copy; CARTO'}).addTo(lmap);
    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_only_labels/{z}/{x}/{y}{r}.png',{maxZoom:18,opacity:0.9}).addTo(lmap);
}

async function loadHeatmap(){
    initMap();
    try{
        const pts = await api('/trips/heatmap');
        if(heatLayer) lmap.removeLayer(heatLayer);
        heatLayer = L.heatLayer(pts,{radius:18,blur:22,maxZoom:15,gradient:{0.2:'#767676',0.4:'#333333',0.6:'#7a120e',0.8:'#b81a14',1.0:'#e5241c'}}).addTo(lmap);
    } catch(e){ console.error('Heatmap error',e); }
}

// ── Trips table ────────────────────────────────────────────────────────────────
async function loadTable(){
    const body = $('tripsBody');
    body.innerHTML = '<tr><td colspan="8" class="empty-row">Loading…</td></tr>';
    try{
        const p = new URLSearchParams({page:state.page, per_page:state.perPage});
        if(state.hour!=='') p.set('hour',state.hour);
        if(state.day!=='') p.set('dow',state.day);
        if(state.passengers!=='') p.set('passengers',state.passengers);

        const d = await api('/trips/recent?'+p);
        const rows = d.trips || [];
        const total = d.total || 0;
        $('archiveCount').textContent = fmt(total);

        // Client-side search filter
        const q = state.search.toLowerCase();
        const filtered = q ? rows.filter(r=>r.id?.toLowerCase().includes(q)) : rows;

        if(!filtered.length){
            body.innerHTML = '<tr><td colspan="8" class="empty-row">No records match</td></tr>';
        } else {
            body.innerHTML = filtered.map(r=>`<tr>
        <td><span class="mono-cell">${escH(r.id||'—')}</span></td>
        <td><span class="vchip v${r.vendor_id}">V${r.vendor_id}</span></td>
        <td>${fmtTime(r.pickup_datetime)}</td>
        <td>${r.passenger_count??'—'}</td>
        <td><span class="mono-cell">${fmt(r.duration_min,1)} min</span></td>
        <td><span class="mono-cell">${fmt(r.speed_kmh,1)} km/h</span></td>
        <td><span class="mono-cell">${String(r.pickup_hour??'?').padStart(2,'0')}h</span></td>
        <td>${DAYS[r.day_of_week]??'—'}</td>
      </tr>`).join('');
        }

        // Pagination
        const totalPages = Math.ceil(total/state.perPage);
        const start = total===0?0:(state.page-1)*state.perPage+1;
        const end = Math.min(state.page*state.perPage, total);
        $('paginationInfo').textContent = `${fmt(start)}–${fmt(end)} of ${fmt(total)}`;

        const ctl = $('paginationControls');
        ctl.innerHTML = '';
        const mk = (lbl,pg,disabled,active)=>{
            const b=document.createElement('button');
            b.className='page-btn'+(active?' active':'');
            b.textContent=lbl; b.disabled=!!disabled;
            if(!disabled) b.onclick=()=>{state.page=pg;loadTable();};
            return b;
        };
        ctl.appendChild(mk('‹',state.page-1,state.page<=1));
        for(let p=Math.max(1,state.page-2);p<=Math.min(totalPages,state.page+2);p++){
            ctl.appendChild(mk(p,p,false,p===state.page));
        }
        ctl.appendChild(mk('›',state.page+1,state.page>=totalPages));

    } catch(e){
        body.innerHTML='<tr><td colspan="8" class="empty-row">Records unavailable</td></tr>';
        $('paginationInfo').textContent='—';
        $('paginationControls').innerHTML='';
    }
}

// ── Event listeners ────────────────────────────────────────────────────────────
$('applyFilters').addEventListener('click',()=>{
    state.hour = $('fHour').value;
    state.day = $('fDay').value;
    state.passengers = $('fPassengers').value;
    state.page = 1;
    loadTable();
    toast('Filter applied');
});
$('resetFilters').addEventListener('click',()=>{
    $('fHour').value=''; $('fDay').value=''; $('fPassengers').value='';
    state.hour=''; state.day=''; state.passengers=''; state.page=1;
    loadTable();
    toast('Filter reset');
});
let tSearch;
$('searchInput').addEventListener('input',e=>{
    clearTimeout(tSearch);
    tSearch=setTimeout(()=>{state.search=e.target.value.trim();loadTable();},350);
});

// ── Init ────────────────────────────────────────────────────────────────────────
async function init(){
    setStatus(false,'Connecting');
    await Promise.allSettled([
        loadStats(),
        loadVendors(),
        loadHourly(),
        loadDaily(),
        loadMonthly(),
        loadDuration(),
        loadSpeed(),
        loadPassengers(),
        loadRankings(),
    ]);
    loadHeatmap();
    loadTable();
}

document.addEventListener('DOMContentLoaded', init);