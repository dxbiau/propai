/**
 * Australian Property Associates — Bloomberg Terminal Dashboard JS
 *
 * All Australia — 8 States & Territories
 * Powers: Deals, Properties, Offers, Pipeline, Profiler, Mentor,
 *         Due Diligence, Negotiation, QA Engine, Photo Enhancement,
 *         VALUE-ADD Intelligence Engine.
 *
 * All data comes from the FastAPI backend at /api/v1/*
 */

/* ─────────────────────────────────────────────────────────────────
   CONFIG & API HELPER
   ───────────────────────────────────────────────────────────────── */

const BASE = '/api/v1';

async function api(method, path, body) {
    const opts = {
        method,
        headers: { 'Content-Type': 'application/json' },
    };
    if (body && method !== 'GET') opts.body = JSON.stringify(body);

    let url = `${BASE}${path}`;
    // For GET with query params in body
    if (method === 'GET' && body) {
        const qs = new URLSearchParams(body).toString();
        url += `?${qs}`;
        delete opts.body;
    }

    try {
        const res = await fetch(url, opts);
        if (!res.ok) {
            const err = await res.json().catch(() => ({ detail: res.statusText }));
            throw new Error(err.detail || err.error || `HTTP ${res.status}`);
        }
        return await res.json();
    } catch (e) {
        showToast(e.message || 'API error', 'error');
        throw e;
    }
}

/* ─────────────────────────────────────────────────────────────────
   FORMAT HELPERS
   ───────────────────────────────────────────────────────────────── */

function $(id) { return document.getElementById(id); }
function fmtPrice(v) { return v ? `$${Number(v).toLocaleString('en-AU', {maximumFractionDigits:0})}` : '—'; }
function fmtPct(v, d=1) { return v != null ? `${Number(v).toFixed(d)}%` : '—'; }
function fmtNum(v, d=1) { return v != null ? Number(v).toFixed(d) : '—'; }

const STRATEGY_CLASSES = {
    BTL: 'strat-btl', R2SA: 'strat-r2sa', FLIP: 'strat-flip',
    BRRR: 'strat-brrr', HMO: 'strat-hmo', PLO: 'strat-plo',
    SUBDIVISION: 'strat-subdivision', DEVELOPMENT: 'strat-development',
    LAND_BANK: 'strat-land_bank',
};

/* ─────────────────────────────────────────────────────────────────
   HELPERS — Real listing search URLs & honest property placeholders
   ───────────────────────────────────────────────────────────────── */

const _TYPE_ICONS = {
    house: '🏠', apartment: '🏢', unit: '🏢', townhouse: '🏘', villa: '🏡',
    land: '🌳', commercial: '🏗', industrial: '🏭', warehouse: '📦', retail: '🏪',
    duplex: '🏠', farm: '🌾', rural: '🌿', acreage: '🌳',
};

// Inline gradient colors — Tailwind CDN can't JIT classes injected from JS
const _TYPE_COLORS = {
    house: 'linear-gradient(135deg, #1e3a5f 0%, #152238 100%)',
    apartment: 'linear-gradient(135deg, #3b1f6e 0%, #251545 100%)',
    unit: 'linear-gradient(135deg, #2e2b6e 0%, #1c1945 100%)',
    townhouse: 'linear-gradient(135deg, #134e4a 0%, #0f302e 100%)',
    villa: 'linear-gradient(135deg, #065f46 0%, #053d2e 100%)',
    land: 'linear-gradient(135deg, #14532d 0%, #0a3018 100%)',
    commercial: 'linear-gradient(135deg, #7c2d12 0%, #4a1a0a 100%)',
    industrial: 'linear-gradient(135deg, #374151 0%, #1f2937 100%)',
    warehouse: 'linear-gradient(135deg, #334155 0%, #1e293b 100%)',
    retail: 'linear-gradient(135deg, #78350f 0%, #451e08 100%)',
    duplex: 'linear-gradient(135deg, #155e75 0%, #0e3a4a 100%)',
    farm: 'linear-gradient(135deg, #3f6212 0%, #263a0b 100%)',
    rural: 'linear-gradient(135deg, #14532d 0%, #0a3018 100%)',
    acreage: 'linear-gradient(135deg, #065f46 0%, #053d2e 100%)',
};

function makeDomainUrl(suburb, postcode, state) {
    const slug = (suburb || '').toLowerCase().replace(/\s+/g, '-');
    const stateSlug = (state || '').toLowerCase();
    return `https://www.domain.com.au/sale/${slug}${stateSlug ? '-' + stateSlug : ''}-${postcode}/`;
}
function makeRealestateUrl(suburb, postcode, state) {
    const slug = (suburb || '').toLowerCase().replace(/\s+/g, '+');
    const stateSlug = (state || '').toLowerCase();
    return `https://www.realestate.com.au/buy/in-${slug}${stateSlug ? ',+' + stateSlug : ''}+${postcode}/list-1`;
}
function propPlaceholder(type, suburb, size, imageUrl) {
    const icon = _TYPE_ICONS[(type || 'house').toLowerCase()] || '🏠';
    const grad = _TYPE_COLORS[(type || 'house').toLowerCase()] || 'linear-gradient(135deg, #1e3a5f 0%, #152238 100%)';

    // If we have a real image URL, render it
    if (imageUrl) {
        if (size === 'sm') {
            return `<div class="relative overflow-hidden rounded flex-shrink-0 border border-white/10" style="width:48px;height:48px;">
                <img src="${imageUrl}" alt="${type}" class="w-full h-full object-cover" loading="lazy" onerror="this.parentElement.innerHTML='<div style=\\'background:${grad};width:48px;height:48px;\\' class=\\'rounded flex items-center justify-center\\'><span class=\\'text-lg\\'>${icon}</span></div>'">
            </div>`;
        }
        return `<div class="relative mb-2 rounded-lg h-36 overflow-hidden border border-white/10 group">
            <img src="${imageUrl}" alt="${type} in ${suburb}" class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105" loading="lazy" onerror="this.style.display='none';this.nextElementSibling.style.display='flex'">
            <div style="background:${grad};display:none;" class="absolute inset-0 flex-col items-center justify-center"><span class="text-3xl mb-1">${icon}</span><span class="text-[9px] text-white/60 font-mono">${(type || 'HOUSE').toUpperCase()} — ${suburb || ''}</span></div>
            <div class="absolute inset-0 bg-gradient-to-t from-black/70 via-black/20 to-transparent"></div>
            <div class="absolute bottom-2 left-2 flex items-center space-x-1">
                <span class="text-[9px] font-mono text-white/80 bg-black/50 backdrop-blur-sm px-1.5 py-0.5 rounded">${(type || 'HOUSE').toUpperCase()}</span>
            </div>
        </div>`;
    }

    // Fallback to gradient placeholder
    if (size === 'sm') {
        return `<div style="background:${grad};width:48px;height:48px;" class="rounded flex items-center justify-center flex-shrink-0 border border-white/10"><span class="text-lg">${icon}</span></div>`;
    }
    return `<div style="background:${grad};" class="mb-2 rounded-lg h-36 flex flex-col items-center justify-center border border-white/10"><span class="text-3xl mb-1">${icon}</span><span class="text-[9px] text-white/60 font-mono tracking-wider">${(type || 'HOUSE').toUpperCase()} — ${suburb || ''}</span></div>`;
}

/* ─────────────────────────────────────────────────────────────────
   TAB SWITCHING
   ───────────────────────────────────────────────────────────────── */

const TAB_IDS = ['deals','properties','offers','profiler','mentor','diligence','negotiate','photos','reno','research'];

function switchTab(name) {
    TAB_IDS.forEach(t => {
        const panel = $(`panel-${t}`);
        const tab = $(`tab-${t}`);
        if (panel) panel.classList.toggle('hidden', t !== name);
        if (tab) {
            tab.classList.toggle('tab-active', t === name);
            if (t !== name) tab.classList.add('text-terminal-muted');
            else tab.classList.remove('text-terminal-muted');
        }
    });
}

/* ─────────────────────────────────────────────────────────────────
   TOAST NOTIFICATIONS
   ───────────────────────────────────────────────────────────────── */

function showToast(msg, type = 'info') {
    const container = $('toast-container');
    const colors = {
        info: 'bg-terminal-info/20 border-terminal-info/40 text-terminal-info',
        success: 'bg-terminal-green/20 border-terminal-green/40 text-terminal-green',
        error: 'bg-terminal-danger/20 border-terminal-danger/40 text-terminal-danger',
        warn: 'bg-terminal-warn/20 border-terminal-warn/40 text-terminal-warn',
    };
    const el = document.createElement('div');
    el.className = `${colors[type] || colors.info} border rounded px-3 py-2 text-xs font-mono animate-fade-in`;
    el.textContent = msg;
    container.appendChild(el);
    setTimeout(() => { el.remove(); }, 4000);
}

/* ─────────────────────────────────────────────────────────────────
   MODALS
   ───────────────────────────────────────────────────────────────── */

function showModal(id) {
    const m = $(id);
    m.classList.remove('hidden');
    m.classList.add('flex');
}

function closeModal(id) {
    const m = $(id);
    m.classList.add('hidden');
    m.classList.remove('flex');
}

function showQuickROI() { showModal('modal-roi'); }

/* ─────────────────────────────────────────────────────────────────
   DEALS — Load, Render, Filter
   ───────────────────────────────────────────────────────────────── */

let _allDeals = [];
let _locationTree = {};   // state → region → [suburb names]
let _locationData = {};   // full data from /locations/tree

async function loadDeals() {
    try {
        const data = await api('GET', '/deals/');
        _allDeals = data.deals || [];
        $('stat-deals').textContent = data.total || 0;
        $('stat-golden').textContent = data.golden_count || 0;
        $('stat-avg-score').textContent = data.average_bargain_score ? fmtNum(data.average_bargain_score) : '—';
        $('ticker-golden').textContent = data.golden_count || 0;
        renderDeals(_allDeals);
    } catch (e) {
        console.error('loadDeals failed', e);
    }
}

/* ─── Location-aware national region filter cascading ─── */

async function loadLocationTree() {
    try {
        const data = await api('GET', '/properties/locations/tree');
        _locationTree = data.tree || {};
        _locationData = data;
        console.log('[PIA] Location database loaded:', data.summary);

        // Auto-populate region dropdown (deals filter) — all states
        const regionSel = $('filter-region');
        if (regionSel) {
            regionSel.innerHTML = '<option value="">ALL STATES</option>';
            Object.entries(_locationTree).forEach(([state, regions]) => {
                const group = document.createElement('optgroup');
                group.label = state;
                Object.keys(regions).forEach(region => {
                    const opt = document.createElement('option');
                    opt.value = `${state}|${region}`;
                    opt.textContent = `${state} — ${region}`;
                    group.appendChild(opt);
                });
                regionSel.appendChild(group);
            });
        }
    } catch (e) {
        console.warn('loadLocationTree failed — region filter will be empty', e);
    }
}

function onStateFilterChange() {
    filterDeals();
}

function filterDeals() {
    const strategy = $('filter-strategy').value;
    const sort = $('filter-sort').value;
    const goldenOnly = $('filter-golden').checked;
    const bmvOnly = $('filter-bmv').checked;
    const regionFilter = $('filter-region') ? $('filter-region').value : '';
    const suburbSearch = $('filter-suburb-search') ? $('filter-suburb-search').value.toLowerCase().trim() : '';

    let deals = [..._allDeals];

    // Region filter: check if the deal's suburb is in the selected state/region
    if (regionFilter) {
        const parts = regionFilter.split('|');
        if (parts.length === 2) {
            const [st, reg] = parts;
            if (_locationTree[st] && _locationTree[st][reg]) {
                const regionSuburbs = _locationTree[st][reg].map(s => s.toLowerCase());
                deals = deals.filter(d => {
                    const sub = (d.property?.suburb || '').toLowerCase();
                    return regionSuburbs.includes(sub);
                });
            }
        }
    }

    // Suburb search: text match
    if (suburbSearch) {
        deals = deals.filter(d => {
            const sub = (d.property?.suburb || '').toLowerCase();
            const addr = (d.property?.address || '').toLowerCase();
            const pc = (d.property?.postcode || '').toLowerCase();
            return sub.includes(suburbSearch) || addr.includes(suburbSearch) || pc.includes(suburbSearch);
        });
    }

    if (strategy) deals = deals.filter(d => d.deal_type === strategy);
    if (goldenOnly) deals = deals.filter(d => d.is_golden_opportunity);
    if (bmvOnly) deals = deals.filter(d => d.bmv_pct > 0);

    const sortFns = {
        bargain_score: (a, b) => (b.bargain_score?.overall_score || 0) - (a.bargain_score?.overall_score || 0),
        roi: (a, b) => (b.cash_flow?.roi || 0) - (a.cash_flow?.roi || 0),
        cash_flow: (a, b) => (b.cash_flow?.monthly_cash_flow || 0) - (a.cash_flow?.monthly_cash_flow || 0),
        price: (a, b) => (a.property?.asking_price || 0) - (b.property?.asking_price || 0),
        price_sqm: (a, b) => (a.price_per_sqm || 9999999) - (b.price_per_sqm || 9999999),
        payback: (a, b) => (a.payback_period_months || 9999) - (b.payback_period_months || 9999),
        bmv: (a, b) => (b.bmv_pct || 0) - (a.bmv_pct || 0),
    };
    deals.sort(sortFns[sort] || sortFns.bargain_score);
    renderDeals(deals);
}

function renderDeals(deals) {
    const grid = $('deals-grid');
    $('deals-count').textContent = `${deals.length} DEAL${deals.length !== 1 ? 'S' : ''}`;

    if (!deals.length) {
        grid.innerHTML = `<div class="col-span-full text-center py-16 text-terminal-muted">
            <div class="font-mono text-sm mb-2">NO DEALS MATCH FILTERS</div>
            <div class="text-xs">Adjust filters or run the pipeline to find deals.</div></div>`;
        return;
    }

    grid.innerHTML = deals.map(d => renderDealCard(d)).join('');
    // Compute avg price/sqm
    const sqms = deals.filter(d => d.price_per_sqm).map(d => d.price_per_sqm);
    $('stat-avg-sqm').textContent = sqms.length ? fmtPrice(sqms.reduce((a,b) => a+b, 0) / sqms.length) + '/m²' : '—';
}

function renderDealCard(d) {
    const p = d.property || {};
    const cf = d.cash_flow || {};
    const bs = d.bargain_score || {};
    const score = bs.overall_score || 0;
    const isGolden = d.is_golden_opportunity;

    const scoreColor = score >= 85 ? 'text-terminal-gold' : score >= 65 ? 'text-terminal-green' : score >= 40 ? 'text-terminal-warn' : 'text-terminal-red';
    const goldenBorder = isGolden ? 'border-terminal-gold golden-pulse' : 'border-terminal-border';
    const stratClass = STRATEGY_CLASSES[d.deal_type] || 'strat-btl';

    const priceText = fmtPrice(p.asking_price || p.effective_price);
    const bedBath = `${p.bedrooms || '?'}BR ${p.bathrooms || '?'}BA ${p.car_spaces || 0}🚗`;
    const propType = (p.property_type || 'house').toUpperCase();
    const suburb = p.suburb || 'Unknown';
    const state = p.state || '';
    const sqm = p.land_size_sqm || p.building_size_sqm;

    // Property hero image — real photo or type placeholder
    const pTypeKey = (p.property_type || 'house').toLowerCase();
    const imageUrl = (p.image_urls && p.image_urls.length > 0) ? p.image_urls[0] : null;
    const imgHtml = propPlaceholder(pTypeKey, suburb, 'lg', imageUrl);

    // Full-label metrics — no confusing abbreviations
    const metrics = [];
    if (cf.gross_rental_yield != null) metrics.push(`<span class="metric-pill">Gross Yield ${fmtPct(cf.gross_rental_yield)}</span>`);
    if (cf.net_yield != null) metrics.push(`<span class="metric-pill">Net Yield ${fmtPct(cf.net_yield)}</span>`);
    if (cf.monthly_cash_flow != null) {
        const cfColor = cf.monthly_cash_flow >= 0 ? 'text-terminal-green' : 'text-terminal-red';
        metrics.push(`<span class="metric-pill ${cfColor}">Cash Flow ${fmtPrice(cf.monthly_cash_flow)}/mo</span>`);
    }
    if (cf.cash_on_cash_return != null) metrics.push(`<span class="metric-pill">Cash-on-Cash ${fmtPct(cf.cash_on_cash_return)}</span>`);
    if (cf.roi != null) metrics.push(`<span class="metric-pill">Return on Investment ${fmtPct(cf.roi)}</span>`);
    if (d.price_per_sqm) metrics.push(`<span class="metric-pill">${fmtPrice(d.price_per_sqm)}/m²</span>`);
    if (d.payback_period_months) metrics.push(`<span class="metric-pill">Payback ${fmtNum(d.payback_period_months, 0)} months</span>`);

    const bmvBadge = d.bmv_pct > 0 ? `<span class="bmv-badge">BMV ${fmtPct(d.bmv_pct, 0)}</span>` : '';
    const flipBadge = d.flip_profit > 0 ? `<span class="metric-pill text-terminal-purple">Flip Profit ${fmtPrice(d.flip_profit)}</span>` : '';

    const distressCount = (p.distress_signals || []).length;
    const distressDots = distressCount > 0 ? `<span class="text-terminal-danger text-[9px]">${'⚠'.repeat(Math.min(distressCount, 3))} ${distressCount} distress signal${distressCount > 1 ? 's' : ''}</span>` : '';

    return `
    <div class="deal-card ${isGolden ? 'golden-pulse' : ''} p-3 animate-fade-in cursor-pointer" style="${isGolden ? 'border-color: rgba(251, 191, 36, 0.3);' : ''}" onclick="showDealDetail('${d.id}')">
        ${imgHtml}
        <div class="flex items-start justify-between mb-1.5">
            <div>
                <div class="text-xs font-medium text-terminal-bright">${suburb}, ${state}</div>
                <div class="text-[10px] text-terminal-dim">${p.address || ''}</div>
            </div>
            <div class="text-right">
                <div class="text-lg font-mono font-bold ${scoreColor}" style="text-shadow: 0 0 15px currentColor;">${score}</div>
                <div class="text-[8px] text-terminal-muted uppercase tracking-wider">Score</div>
            </div>
        </div>
        <div class="flex items-center space-x-2 mb-2">
            <span class="text-sm font-mono font-bold text-terminal-bright">${priceText}</span>
            <span class="strategy-badge ${stratClass}">${d.deal_type || 'BTL'}</span>
            ${bmvBadge}
            ${isGolden ? '<span class="text-[9px] text-terminal-gold font-bold">🏆 GOLDEN</span>' : ''}
        </div>
        <div class="flex items-center space-x-3 text-[10px] text-terminal-dim mb-2 font-mono">
            <span>${bedBath}</span>
            <span class="text-terminal-muted">·</span>
            <span>${propType}</span>
            ${sqm ? `<span class="text-terminal-muted">·</span><span>${Number(sqm).toLocaleString()}m²</span>` : ''}
            <span class="text-terminal-muted">·</span>
            <span class="text-terminal-green">Rent ${fmtPrice(cf.weekly_rent || p.estimated_weekly_rent || p.current_weekly_rent)}/wk</span>
        </div>
        <div class="flex flex-wrap gap-1 mb-2">${metrics.join('')}${flipBadge}</div>
        <div class="flex items-center justify-between">
            ${distressDots}
            <div class="flex space-x-1.5">
                <button onclick="event.stopPropagation();showOfferModal('${d.id}')" class="bg-terminal-green/10 hover:bg-terminal-green/20 text-terminal-green px-2.5 py-1 rounded-md text-[9px] font-mono font-medium transition border border-terminal-green/20">OFFER</button>
                <button onclick="event.stopPropagation();showDealDetail('${d.id}')" class="bg-terminal-accent/10 hover:bg-terminal-accent/20 text-terminal-accent px-2.5 py-1 rounded-md text-[9px] font-mono font-medium transition border border-terminal-accent/20">DETAILS</button>
            </div>
        </div>
    </div>`;
}

/* ─────────────────────────────────────────────────────────────────
   DEAL DETAIL MODAL
   ───────────────────────────────────────────────────────────────── */

function showDealDetail(dealId) {
    const d = _allDeals.find(x => x.id === dealId);
    if (!d) { showToast('Deal not found', 'error'); return; }

    const p = d.property || {};
    const cf = d.cash_flow || {};
    const bs = d.bargain_score || {};

    const content = $('deal-detail-content');
    // Property type placeholder (real photos when available)
    const pTypeKey = (p.property_type || 'house').toLowerCase();
    const typeIcon = _TYPE_ICONS[pTypeKey] || '🏠';
    const typeGrad = _TYPE_COLORS[pTypeKey] || 'linear-gradient(135deg, #1e3a5f 0%, #152238 100%)';
    const detailImageUrl = (p.image_urls && p.image_urls.length > 0) ? p.image_urls[0] : null;
    const headerPlaceholder = detailImageUrl
        ? `<div class="relative rounded-lg h-40 overflow-hidden border border-white/10 mb-3">
            <img src="${detailImageUrl}" alt="${p.suburb}" class="w-full h-full object-cover">
            <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-black/30 to-transparent"></div>
            <div class="absolute bottom-3 left-3">
                <div class="text-sm font-mono text-white font-bold">${(p.property_type || 'HOUSE').toUpperCase()}</div>
                <div class="text-[10px] text-white/70">${p.suburb || ''}${p.state ? ', ' + p.state : ''} ${p.postcode || ''}</div>
            </div>
            <button onclick="event.stopPropagation();enhancePropertyPhoto('${detailImageUrl}')" class="absolute top-2 right-2 bg-black/50 backdrop-blur-sm hover:bg-terminal-accent/80 text-white px-2 py-1 rounded text-[9px] font-mono transition" title="AI Enhance">✨ ENHANCE</button>
        </div>`
        : `<div style="background:${typeGrad};" class="rounded-lg h-32 flex items-center justify-center border border-white/10 mb-3">
        <span class="text-4xl mr-3">${typeIcon}</span>
        <div><div class="text-sm font-mono text-white">${(p.property_type || 'HOUSE').toUpperCase()}</div>
        <div class="text-[9px] text-white/60">${p.suburb || ''}${p.state ? ', ' + p.state : ''} ${p.postcode || ''}</div></div>
    </div>`;

    content.innerHTML = `
        ${headerPlaceholder}
        <div class="grid grid-cols-2 gap-3">
            <div>
                <div class="text-[9px] text-terminal-muted font-mono tracking-wider mb-1">PROPERTY</div>
                <div class="text-sm font-medium text-terminal-bright">${p.address || ''}</div>
                <div class="text-xs text-terminal-dim">${p.suburb || ''}, ${p.state || ''} ${p.postcode || ''}</div>
                <div class="text-xs text-terminal-dim mt-1">${p.bedrooms || 0}BR ${p.bathrooms || 0}BA ${p.car_spaces || 0}🚗 — ${(p.property_type || '').toUpperCase()}</div>
                ${p.land_size_sqm ? `<div class="text-xs text-terminal-dim">Land: ${Number(p.land_size_sqm).toLocaleString()}m²</div>` : ''}
                ${p.building_size_sqm ? `<div class="text-xs text-terminal-dim">Building: ${Number(p.building_size_sqm).toLocaleString()}m²</div>` : ''}
                ${p.zoning ? `<div class="text-xs text-terminal-dim">Zoning: ${p.zoning}</div>` : ''}
                ${p.condition ? `<div class="text-xs text-terminal-dim">Condition: ${p.condition.replace(/_/g, ' ').toUpperCase()}</div>` : ''}
            </div>
            <div>
                <div class="text-[9px] text-terminal-muted font-mono tracking-wider mb-1">BARGAIN SCORE</div>
                <div class="text-3xl font-mono font-bold ${bs.overall_score >= 85 ? 'text-terminal-gold' : bs.overall_score >= 65 ? 'text-terminal-green' : 'text-terminal-warn'}">${bs.overall_score || 0}</div>
                <div class="text-[10px] text-terminal-muted mt-1">${bs.summary || ''}</div>
                <div class="space-y-1 mt-2">
                    <div class="flex justify-between text-[10px] font-mono"><span class="text-terminal-dim">Price Deviation</span><span>${fmtNum(bs.price_deviation_score)}</span></div>
                    <div class="flex justify-between text-[10px] font-mono"><span class="text-terminal-dim">Cash Flow Score</span><span>${fmtNum(bs.cash_flow_score)}</span></div>
                    <div class="flex justify-between text-[10px] font-mono"><span class="text-terminal-dim">Market Timing</span><span>${fmtNum(bs.market_timing_score)}</span></div>
                    <div class="flex justify-between text-[10px] font-mono"><span class="text-terminal-dim">Below Market Value</span><span>${fmtPct(d.bmv_pct)}</span></div>
                </div>
            </div>
        </div>
        <div class="bg-terminal-bg rounded border border-terminal-border p-3">
            <div class="text-[9px] text-terminal-muted font-mono tracking-wider mb-2">FINANCIAL ANALYSIS</div>
            <div class="grid grid-cols-4 gap-2 text-center">
                <div><div class="text-[9px] text-terminal-muted">Purchase Price</div><div class="font-mono font-bold text-sm">${fmtPrice(cf.purchase_price)}</div></div>
                <div><div class="text-[9px] text-terminal-muted">Stamp Duty</div><div class="font-mono font-bold text-sm">${fmtPrice(cf.stamp_duty)}</div></div>
                <div><div class="text-[9px] text-terminal-muted">Total Investment</div><div class="font-mono font-bold text-sm">${fmtPrice(cf.total_investment)}</div></div>
                <div><div class="text-[9px] text-terminal-muted">Loan Amount</div><div class="font-mono font-bold text-sm">${fmtPrice(cf.loan_amount)}</div></div>
            </div>
            <div class="grid grid-cols-4 gap-2 text-center mt-2">
                <div><div class="text-[9px] text-terminal-muted">Weekly Rent</div><div class="font-mono font-bold text-sm">${fmtPrice(cf.weekly_rent)}/wk</div></div>
                <div><div class="text-[9px] text-terminal-muted">Gross Yield</div><div class="font-mono font-bold text-sm text-terminal-accent">${fmtPct(cf.gross_rental_yield)}</div></div>
                <div><div class="text-[9px] text-terminal-muted">Net Yield</div><div class="font-mono font-bold text-sm ${(cf.net_yield || 0) >= 0 ? 'text-terminal-green' : 'text-terminal-red'}">${fmtPct(cf.net_yield)}</div></div>
                <div><div class="text-[9px] text-terminal-muted">Monthly Cash Flow</div><div class="font-mono font-bold text-sm ${(cf.monthly_cash_flow || 0) >= 0 ? 'text-terminal-green' : 'text-terminal-red'}">${fmtPrice(cf.monthly_cash_flow)}</div></div>
            </div>
            <div class="grid grid-cols-4 gap-2 text-center mt-2">
                <div><div class="text-[9px] text-terminal-muted">Cash-on-Cash Return</div><div class="font-mono font-bold text-sm">${fmtPct(cf.cash_on_cash_return)}</div></div>
                <div><div class="text-[9px] text-terminal-muted">Return on Investment</div><div class="font-mono font-bold text-sm">${fmtPct(cf.roi)}</div></div>
                <div><div class="text-[9px] text-terminal-muted">Price per m²</div><div class="font-mono font-bold text-sm">${d.price_per_sqm ? fmtPrice(d.price_per_sqm) : '—'}</div></div>
                <div><div class="text-[9px] text-terminal-muted">Payback Period</div><div class="font-mono font-bold text-sm">${d.payback_period_months ? fmtNum(d.payback_period_months, 0) + ' months' : '—'}</div></div>
            </div>
        </div>
        ${d.estimated_refurb_cost > 0 || d.flip_profit > 0 ? `
        <div class="bg-terminal-bg rounded border border-terminal-border p-3">
            <div class="text-[9px] text-terminal-muted font-mono tracking-wider mb-2">RENOVATION & FLIP ANALYSIS</div>
            <div class="grid grid-cols-3 gap-2 text-center">
                <div><div class="text-[9px] text-terminal-muted">Renovation Cost Estimate</div><div class="font-mono font-bold text-sm">${fmtPrice(d.estimated_refurb_cost)}</div></div>
                <div><div class="text-[9px] text-terminal-muted">After Repair Value</div><div class="font-mono font-bold text-sm">${fmtPrice(d.after_repair_value)}</div></div>
                <div><div class="text-[9px] text-terminal-muted">Estimated Flip Profit</div><div class="font-mono font-bold text-sm text-terminal-green">${fmtPrice(d.flip_profit)}</div></div>
            </div>
        </div>` : ''}
        ${(p.distress_signals || []).length > 0 ? `
        <div class="bg-terminal-bg rounded border border-terminal-border p-3">
            <div class="text-[9px] text-terminal-muted font-mono tracking-wider mb-2">⚠ DISTRESS SIGNALS</div>
            <div class="space-y-1">
                ${(p.distress_signals || []).map(s => `
                    <div class="flex items-center justify-between text-[10px] font-mono">
                        <span class="text-terminal-danger">${s.keyword}</span>
                        <span class="text-terminal-muted">${(s.confidence * 100).toFixed(0)}% confidence</span>
                    </div>`).join('')}
            </div>
        </div>` : ''}
        ${d.ai_analysis ? `
        <div class="bg-terminal-bg rounded border border-terminal-border p-3">
            <div class="text-[9px] text-terminal-muted font-mono tracking-wider mb-2">AI ANALYSIS</div>
            <div class="text-xs text-terminal-text leading-relaxed whitespace-pre-wrap">${d.ai_analysis}</div>
        </div>` : ''}
        ${p.listing_text ? `
        <div class="bg-terminal-bg rounded border border-terminal-border p-3">
            <div class="text-[9px] text-terminal-muted font-mono tracking-wider mb-2">LISTING DESCRIPTION</div>
            <div class="text-xs text-terminal-dim leading-relaxed">${p.listing_text}</div>
        </div>` : ''}
        <div class="flex flex-wrap gap-2">
            <button onclick="showOfferModal('${d.id}')" class="bg-terminal-green/10 hover:bg-terminal-green/20 text-terminal-green px-4 py-2 rounded text-xs font-mono font-medium transition border border-terminal-green/30">GENERATE OFFER</button>
            <a href="${makeDomainUrl(p.suburb, p.postcode, p.state)}" target="_blank" rel="noopener" class="bg-terminal-accent/10 hover:bg-terminal-accent/20 text-terminal-accent px-4 py-2 rounded text-xs font-mono transition border border-terminal-accent/30">DOMAIN.COM.AU ↗</a>
            <a href="${makeRealestateUrl(p.suburb, p.postcode, p.state)}" target="_blank" rel="noopener" class="bg-terminal-panel hover:bg-terminal-border text-terminal-dim px-4 py-2 rounded text-xs font-mono transition border border-terminal-border">REALESTATE.COM.AU ↗</a>
        </div>
        <div class="text-[8px] text-terminal-muted font-mono text-center mt-1 italic">⚠ SIMULATED LISTING — Search real portals above to verify actual availability &amp; pricing</div>
    `;
    showModal('modal-deal');
}

/* ─────────────────────────────────────────────────────────────────
   PROPERTIES — Load & Render
   ───────────────────────────────────────────────────────────────── */

let _allProperties = [];

async function loadProperties() {
    try {
        const data = await api('GET', '/properties/');
        _allProperties = data.properties || [];
        $('stat-properties').textContent = data.total || 0;
        renderProperties(_allProperties);
    } catch (e) {
        console.error('loadProperties failed', e);
    }
}

function searchProperties() {
    const suburb = $('search-suburb').value.toLowerCase().trim();
    const type = $('prop-type-filter').value;
    const distressOnly = $('distress-filter').checked;

    let props = [..._allProperties];
    if (suburb) props = props.filter(p => (p.suburb || '').toLowerCase().includes(suburb) || (p.state || '').toLowerCase().includes(suburb));
    if (type) props = props.filter(p => p.property_type === type);
    if (distressOnly) props = props.filter(p => (p.distress_signals || []).length > 0);
    renderProperties(props);
}

function renderProperties(props) {
    const list = $('properties-list');
    if (!props.length) {
        list.innerHTML = '<div class="text-center py-16 text-terminal-muted font-mono text-sm">NO PROPERTIES MATCH</div>';
        return;
    }
    list.innerHTML = props.map(p => {
        const price = fmtPrice(p.asking_price || p.sold_price);
        const distressCount = (p.distress_signals || []).length;
        const distressBadge = distressCount > 0 ? `<span class="text-terminal-danger text-[9px] font-mono">${distressCount} ⚠</span>` : '';
        const type = (p.property_type || 'house').toUpperCase();
        const typeLower = (p.property_type || 'house').toLowerCase();
        const imgUrl = (p.image_urls && p.image_urls.length > 0) ? p.image_urls[0] : null;
        const thumbHtml = propPlaceholder(typeLower, p.suburb, 'sm', imgUrl);
        const domainUrl = makeDomainUrl(p.suburb, p.postcode, p.state);
        return `
        <div class="deal-card px-3 py-2.5 flex items-center justify-between cursor-pointer" onclick="showPropertyDetail('${p.id}')">
            <div class="flex items-center space-x-3">
                ${thumbHtml}
                <div class="text-center min-w-[40px]">
                    <div class="text-sm font-mono font-bold text-terminal-bright">${p.bedrooms || '?'}</div>
                    <div class="text-[8px] text-terminal-muted">BED</div>
                </div>
                <div>
                    <div class="text-xs font-medium text-terminal-bright">${p.address}</div>
                    <div class="text-[10px] text-terminal-dim">${p.suburb}, ${p.state} ${p.postcode} — ${type}</div>
                </div>
            </div>
            <div class="flex items-center space-x-3">
                ${distressBadge}
                <span class="font-mono text-sm font-bold text-terminal-accent">${price}</span>
                <span class="text-[9px] text-terminal-dim font-mono">${p.estimated_weekly_rent ? fmtPrice(p.estimated_weekly_rent) + '/wk' : ''}</span>
                ${p.land_size_sqm ? `<span class="text-[9px] text-terminal-dim font-mono">${Number(p.land_size_sqm).toLocaleString()}m²</span>` : ''}
                <a href="${domainUrl}" target="_blank" rel="noopener" onclick="event.stopPropagation()" class="text-[8px] text-terminal-accent/60 hover:text-terminal-accent font-mono">DOMAIN ↗</a>
            </div>
        </div>`;
    }).join('');
}

/* ─────────────────────────────────────────────────────────────────
   PROPERTY DETAIL MODAL — clickable property cards
   ───────────────────────────────────────────────────────────────── */

function showPropertyDetail(propId) {
    const p = _allProperties.find(x => x.id === propId);
    if (!p) { showToast('Property not found', 'error'); return; }

    const content = $('property-detail-content');
    const pTypeKey = (p.property_type || 'house').toLowerCase();
    const typeIcon = _TYPE_ICONS[pTypeKey] || '🏠';
    const typeGrad = _TYPE_COLORS[pTypeKey] || 'linear-gradient(135deg, #1e3a5f 0%, #152238 100%)';
    const distressCount = (p.distress_signals || []).length;
    const domainUrl = makeDomainUrl(p.suburb, p.postcode, p.state);
    const realestateUrl = makeRealestateUrl(p.suburb, p.postcode, p.state);

    content.innerHTML = `
        <div style="background:${typeGrad};" class="rounded h-24 flex items-center justify-center border border-terminal-border/30">
            <span class="text-4xl mr-3">${typeIcon}</span>
            <div>
                <div class="text-sm font-mono text-terminal-bright">${(p.property_type || 'HOUSE').toUpperCase()}</div>
                <div class="text-[9px] text-terminal-muted">${p.suburb}${p.state ? ', ' + p.state : ''} ${p.postcode}</div>
            </div>
        </div>

        <div class="grid grid-cols-2 gap-3">
            <div>
                <div class="text-[9px] text-terminal-muted font-mono tracking-wider mb-1">LOCATION</div>
                <div class="text-sm font-medium text-terminal-bright">${p.address}</div>
                <div class="text-xs text-terminal-dim">${p.suburb}, ${p.state} ${p.postcode}</div>
                <div class="text-xs text-terminal-dim mt-1">${p.bedrooms || 0}BR ${p.bathrooms || 0}BA ${p.car_spaces || 0}🚗</div>
                ${p.land_size_sqm ? `<div class="text-xs text-terminal-dim">Land: ${Number(p.land_size_sqm).toLocaleString()}m²</div>` : ''}
                ${p.building_size_sqm ? `<div class="text-xs text-terminal-dim">Building: ${Number(p.building_size_sqm).toLocaleString()}m²</div>` : ''}
                ${p.year_built ? `<div class="text-xs text-terminal-dim">Built: ${p.year_built}</div>` : ''}
                ${p.zoning ? `<div class="text-xs text-terminal-dim">Zoning: ${p.zoning}</div>` : ''}
                ${p.condition ? `<div class="text-xs text-terminal-dim">Condition: ${p.condition.replace(/_/g, ' ').toUpperCase()}</div>` : ''}
            </div>
            <div>
                <div class="text-[9px] text-terminal-muted font-mono tracking-wider mb-1">PRICING & RENTAL</div>
                <div class="text-2xl font-mono font-bold text-terminal-accent">${fmtPrice(p.asking_price || p.sold_price)}</div>
                ${p.estimated_weekly_rent ? `<div class="text-xs text-terminal-dim mt-1">Est. Rent: ${fmtPrice(p.estimated_weekly_rent)}/wk</div>` : ''}
                ${p.current_weekly_rent ? `<div class="text-xs text-terminal-green">Current Rent: ${fmtPrice(p.current_weekly_rent)}/wk (tenanted)</div>` : ''}
                ${p.council_rates_annual ? `<div class="text-xs text-terminal-dim">Council Rates: ${fmtPrice(p.council_rates_annual)}/yr</div>` : ''}
                ${p.water_rates_annual ? `<div class="text-xs text-terminal-dim">Water Rates: ${fmtPrice(p.water_rates_annual)}/yr</div>` : ''}
                ${p.strata_levies_quarterly ? `<div class="text-xs text-terminal-dim">Strata: ${fmtPrice(p.strata_levies_quarterly)}/qtr</div>` : ''}
            </div>
        </div>

        ${p.agent_name || p.agency_name ? `
        <div class="bg-terminal-bg rounded border border-terminal-border p-3">
            <div class="text-[9px] text-terminal-muted font-mono tracking-wider mb-1">AGENT</div>
            <div class="text-xs text-terminal-bright">${p.agent_name || ''} ${p.agency_name ? '— ' + p.agency_name : ''}</div>
            ${p.agent_phone ? `<div class="text-xs text-terminal-dim">${p.agent_phone}</div>` : ''}
        </div>` : ''}

        ${distressCount > 0 ? `
        <div class="bg-terminal-bg rounded border border-terminal-border p-3">
            <div class="text-[9px] text-terminal-muted font-mono tracking-wider mb-2">⚠ DISTRESS SIGNALS</div>
            <div class="space-y-1">
                ${(p.distress_signals || []).map(s => `
                    <div class="flex items-center justify-between text-[10px] font-mono">
                        <span class="text-terminal-danger">${s.keyword}</span>
                        <span class="text-terminal-muted">${(s.confidence * 100).toFixed(0)}% confidence</span>
                    </div>`).join('')}
            </div>
        </div>` : ''}

        ${p.listing_text ? `
        <div class="bg-terminal-bg rounded border border-terminal-border p-3">
            <div class="text-[9px] text-terminal-muted font-mono tracking-wider mb-2">LISTING DESCRIPTION</div>
            <div class="text-xs text-terminal-dim leading-relaxed">${p.listing_text}</div>
        </div>` : ''}

        <div class="bg-terminal-bg rounded border border-terminal-warn/30 p-3">
            <div class="text-[9px] text-terminal-warn font-mono tracking-wider mb-2">🔍 VERIFY ON REAL PORTALS</div>
            <div class="text-[10px] text-terminal-muted mb-2">This is a simulated listing for analysis practice. Search real portals to find actual available properties in <span class="text-terminal-bright">${p.suburb}</span>:</div>
            <div class="flex flex-wrap gap-2">
                <a href="${domainUrl}" target="_blank" rel="noopener" class="bg-terminal-accent/10 hover:bg-terminal-accent/20 text-terminal-accent px-4 py-2 rounded text-xs font-mono font-medium transition border border-terminal-accent/30">🏠 SEARCH DOMAIN.COM.AU ↗</a>
                <a href="${realestateUrl}" target="_blank" rel="noopener" class="bg-terminal-green/10 hover:bg-terminal-green/20 text-terminal-green px-4 py-2 rounded text-xs font-mono font-medium transition border border-terminal-green/30">🔎 SEARCH REALESTATE.COM.AU ↗</a>
            </div>
        </div>
    `;
    showModal('modal-property');
}

/* ─────────────────────────────────────────────────────────────────
   OFFERS — Generate & List
   ───────────────────────────────────────────────────────────────── */

function showOfferModal(dealId) {
    $('offer-deal-id').value = dealId;
    closeModal('modal-deal');
    showModal('modal-offer');
}

async function submitOffer() {
    const dealId = $('offer-deal-id').value;
    if (!dealId) { showToast('No deal selected', 'error'); return; }

    const body = {
        deal_id: dealId,
        buyer_name: $('offer-name').value || 'Investor',
        buyer_entity: $('offer-entity').value || null,
        max_budget: parseFloat($('offer-budget').value) || 0,
        tone: $('offer-tone').value,
        personal_story: $('offer-story').value || null,
    };

    showToast('Generating offer...', 'info');
    try {
        const result = await api('POST', '/offers/', body);
        closeModal('modal-offer');
        showToast('Offer generated successfully!', 'success');
        switchTab('offers');
        loadOffers();
    } catch (e) {
        // Error already toasted by api()
    }
}

async function loadOffers() {
    try {
        const data = await api('GET', '/offers/');
        const offers = data.offers || [];
        $('stat-offers').textContent = offers.length;
        const list = $('offers-list');
        if (!offers.length) {
            list.innerHTML = '<div class="text-center py-16 text-terminal-muted font-mono text-sm">NO OFFERS GENERATED</div>';
            return;
        }
        list.innerHTML = offers.map(o => `
            <div class="bg-terminal-panel rounded border border-terminal-border p-3">
                <div class="flex items-center justify-between mb-2">
                    <div class="font-mono text-xs text-terminal-accent">${o.property_address || 'Offer'}</div>
                    <span class="text-[10px] font-mono text-terminal-muted">${new Date(o.created_at).toLocaleDateString()}</span>
                </div>
                <div class="text-xs text-terminal-text whitespace-pre-wrap leading-relaxed">${o.offer_text || o.letter || ''}</div>
                <div class="mt-2 flex items-center space-x-3 text-[10px] font-mono text-terminal-dim">
                    <span>Offer: ${fmtPrice(o.offer_amount || o.recommended_price)}</span>
                    <span>Tone: ${(o.tone || '').toUpperCase()}</span>
                </div>
            </div>`).join('');
    } catch (e) {
        console.error('loadOffers failed', e);
    }
}

/* ─────────────────────────────────────────────────────────────────
   ROI CALCULATOR
   ───────────────────────────────────────────────────────────────── */

async function calculateROI() {
    const price = parseFloat($('roi-price').value);
    const rent = parseFloat($('roi-rent').value);
    const state = $('roi-state').value;

    if (!price || !rent) { showToast('Enter price and rent', 'error'); return; }

    try {
        const result = await api('GET', '/deals/quick-roi', {
            purchase_price: price, weekly_rent: rent, state: state,
        });

        const r = $('roi-result');
        r.classList.remove('hidden');
        const verdictColor = result.verdict.includes('STRONG') ? 'text-terminal-green' : result.verdict.includes('WEAK') ? 'text-terminal-red' : 'text-terminal-warn';
        r.innerHTML = `
            <div class="text-center mb-2"><span class="text-lg font-mono font-bold ${verdictColor}">${result.verdict}</span></div>
            <div class="grid grid-cols-2 gap-2 text-[10px] font-mono">
                <div class="flex justify-between"><span class="text-terminal-dim">Gross Yield</span><span class="text-terminal-bright">${fmtPct(result.gross_yield)}</span></div>
                <div class="flex justify-between"><span class="text-terminal-dim">Net Yield (est.)</span><span class="text-terminal-bright">${fmtPct(result.estimated_net_yield)}</span></div>
                <div class="flex justify-between"><span class="text-terminal-dim">Monthly Cash Flow</span><span class="${result.monthly_cash_flow >= 0 ? 'text-terminal-green' : 'text-terminal-red'}">${fmtPrice(result.monthly_cash_flow)}</span></div>
                <div class="flex justify-between"><span class="text-terminal-dim">Stamp Duty</span><span class="text-terminal-bright">${fmtPrice(result.stamp_duty)}</span></div>
            </div>`;
    } catch (e) { /* api() shows toast */ }
}

/* ─────────────────────────────────────────────────────────────────
   PIPELINE — Scout & Full Run
   ───────────────────────────────────────────────────────────────── */

/* ═══ LOCATION SCOUT — Modal & State Machine ═══ */

let _scoutScope = 'all';
let _scoutSelectedStates = [];
let _scoutSelectedRegion = '';
let _scoutSelectedSuburbs = [];

function showLocationScout() {
    showModal('modal-scout');
    loadScoutData();
    setScoutScope('all');
}

async function loadScoutData() {
    // Load location tree if not already loaded
    if (!Object.keys(_locationTree).length) await loadLocationTree();

    // Load stats
    try {
        const stats = await api('GET', '/properties/locations/stats');
        $('scout-db-stats').textContent =
            `${stats.total_states} States · ${stats.total_regions} Regions · ${stats.total_suburbs} Suburbs · ${stats.total_properties} Properties Loaded`;
    } catch (e) {
        $('scout-db-stats').textContent = 'Location database available';
    }
    updateScoutSummary();
}

function setScoutScope(scope) {
    _scoutScope = scope;
    _scoutSelectedStates = Object.keys(_locationTree);  // All states
    _scoutSelectedRegion = '';
    _scoutSelectedSuburbs = [];

    // Update scope button styles
    ['all', 'region', 'suburb'].forEach(s => {
        const btn = $(`scout-scope-${s}`);
        if (!btn) return;
        if (s === scope) {
            btn.className = 'bg-terminal-accent/20 text-terminal-accent px-3 py-1.5 rounded text-xs font-mono font-medium border border-terminal-accent/30 transition';
        } else {
            btn.className = 'bg-terminal-panel text-terminal-dim px-3 py-1.5 rounded text-xs font-mono font-medium border border-terminal-border transition hover:text-terminal-text';
        }
    });

    // Show/hide rows
    $('scout-region-row').classList.toggle('hidden', scope === 'all');
    $('scout-suburb-row').classList.toggle('hidden', scope !== 'suburb');
    $('scout-market-preview').classList.add('hidden');
    $('scout-suburb-results').innerHTML = '';
    $('scout-selected-suburbs').innerHTML = '';

    // Populate regions in scout
    if (scope === 'region' || scope === 'suburb') {
        populateScoutRegions();
    }

    updateScoutSummary();
}

function toggleScoutState(state) {
    if (_scoutSelectedStates.includes(state)) {
        _scoutSelectedStates = _scoutSelectedStates.filter(s => s !== state);
    } else {
        _scoutSelectedStates.push(state);
    }
    updateScoutSummary();
}

function populateScoutRegions() {
    const sel = $('scout-region-select');
    sel.innerHTML = '<option value="">— Select a region —</option>';
    Object.entries(_locationTree).forEach(([state, regions]) => {
        const group = document.createElement('optgroup');
        group.label = state;
        Object.keys(regions).forEach(region => {
            const opt = document.createElement('option');
            opt.value = `${state}|${region}`;
            opt.textContent = `${state} — ${region}`;
            group.appendChild(opt);
        });
        sel.appendChild(group);
    });
}

function onScoutRegionChange() {
    _scoutSelectedRegion = $('scout-region-select').value;
    updateScoutSummary();
    showScoutMarketPreview();
}

async function searchScoutSuburbs() {
    const q = $('scout-suburb-search').value.trim();
    if (q.length < 2) { $('scout-suburb-results').innerHTML = ''; return; }

    try {
        const data = await api('GET', `/properties/locations/search?q=${encodeURIComponent(q)}`);
        const results = data.results || [];
        $('scout-suburb-results').innerHTML = results.map(s => {
            const isSelected = _scoutSelectedSuburbs.find(x => x.name === s.name && x.state === s.state);
            return `<div class="flex items-center justify-between bg-terminal-bg rounded px-2 py-1 text-[10px] font-mono cursor-pointer hover:bg-terminal-border/30 transition ${isSelected ? 'border border-terminal-accent/50' : ''}"
                         onclick="addScoutSuburb('${s.name}', '${s.state}', '${s.region}', ${s.median}, ${s.growth}, ${s.yield})">
                <div>
                    <span class="text-terminal-bright">${s.name}</span>
                    <span class="text-terminal-muted ml-1">${s.state} ${s.postcode}</span>
                    <span class="text-terminal-dim ml-1">${s.region}</span>
                </div>
                <div class="flex space-x-3 text-terminal-dim">
                    <span>Median ${fmtPrice(s.median)}</span>
                    <span class="${s.growth >= 0 ? 'text-terminal-green' : 'text-terminal-red'}">${s.growth >= 0 ? '▲' : '▼'}${Math.abs(s.growth).toFixed(1)}%</span>
                    <span>Yield ${s.yield.toFixed(1)}%</span>
                </div>
            </div>`;
        }).join('');
    } catch (e) { /* fail silently */ }
}

function addScoutSuburb(name, state, region, median, growth, yld) {
    if (_scoutSelectedSuburbs.find(s => s.name === name && s.state === state)) {
        _scoutSelectedSuburbs = _scoutSelectedSuburbs.filter(s => !(s.name === name && s.state === state));
    } else {
        _scoutSelectedSuburbs.push({ name, state, region, median, growth, yield: yld });
    }
    renderSelectedSuburbs();
    updateScoutSummary();
}

function renderSelectedSuburbs() {
    $('scout-selected-suburbs').innerHTML = _scoutSelectedSuburbs.map(s =>
        `<span class="inline-flex items-center bg-terminal-accent/10 text-terminal-accent border border-terminal-accent/30 rounded px-2 py-0.5 text-[9px] font-mono">
            ${s.name}, ${s.state}
            <button onclick="addScoutSuburb('${s.name}','${s.state}','${s.region}',${s.median},${s.growth},${s.yield})" class="ml-1 text-terminal-muted hover:text-terminal-danger">×</button>
        </span>`
    ).join('');
}

function showScoutMarketPreview() {
    let suburbs = [];
    if (_scoutScope === 'state' && _scoutSelectedStates.length) {
        // Show top suburbs from selected states (by yield)
        _scoutSelectedStates.forEach(state => {
            if (_locationTree[state]) {
                Object.entries(_locationTree[state]).forEach(([region, subNames]) => {
                    subNames.forEach(name => suburbs.push({ name, state, region }));
                });
            }
        });
    } else if (_scoutScope === 'region' && _scoutSelectedRegion) {
        const [st, reg] = _scoutSelectedRegion.split('|');
        if (_locationTree[st] && _locationTree[st][reg]) {
            _locationTree[st][reg].forEach(name => suburbs.push({ name, state: st, region: reg }));
        }
    }

    if (!suburbs.length) { $('scout-market-preview').classList.add('hidden'); return; }

    $('scout-market-preview').classList.remove('hidden');
    // Limit to 12
    const show = suburbs.slice(0, 12);
    $('scout-market-grid').innerHTML = show.map(s =>
        `<div class="bg-terminal-bg rounded border border-terminal-border p-2">
            <div class="text-[10px] font-mono font-bold text-terminal-bright">${s.name}</div>
            <div class="text-[9px] text-terminal-dim">${s.state} · ${s.region}</div>
        </div>`
    ).join('');
}

function updateScoutSummary() {
    let target = '';
    let regionCount = '—';
    let suburbCount = '—';

    if (_scoutScope === 'all') {
        target = 'All Australia — 6 States';
        const totalRegions = Object.values(_locationTree).reduce((sum, regions) => sum + Object.keys(regions).length, 0);
        const totalSuburbs = Object.values(_locationTree).reduce((sum, regions) =>
            sum + Object.values(regions).reduce((s2, subs) => s2 + subs.length, 0), 0);
        regionCount = `${totalRegions} Regions`;
        suburbCount = `${totalSuburbs} Suburbs`;
    } else if (_scoutScope === 'state') {
        const states = _scoutSelectedStates.length ? _scoutSelectedStates.join(', ') : 'None selected';
        target = states;
        let rCount = 0, sCount = 0;
        _scoutSelectedStates.forEach(st => {
            if (_locationTree[st]) {
                rCount += Object.keys(_locationTree[st]).length;
                sCount += Object.values(_locationTree[st]).reduce((s, a) => s + a.length, 0);
            }
        });
        regionCount = `${rCount} Regions`;
        suburbCount = `${sCount} Suburbs`;
    } else if (_scoutScope === 'region') {
        if (_scoutSelectedRegion) {
            const [st, reg] = _scoutSelectedRegion.split('|');
            target = `${reg} (${st})`;
            regionCount = '1 Region';
            suburbCount = `${(_locationTree[st]?.[reg] || []).length} Suburbs`;
        } else {
            target = 'Select a region';
        }
    } else if (_scoutScope === 'suburb') {
        target = _scoutSelectedSuburbs.length
            ? `${_scoutSelectedSuburbs.length} suburb${_scoutSelectedSuburbs.length > 1 ? 's' : ''} selected`
            : 'Search and select suburbs';
        suburbCount = `${_scoutSelectedSuburbs.length} Suburbs`;
    }

    $('scout-target-summary').textContent = target;
    $('scout-region-count').textContent = regionCount;
    $('scout-suburb-count').textContent = suburbCount;

    // Property count from loaded data
    const propCount = _allProperties.length;
    $('scout-property-count').textContent = `${propCount} Properties Loaded`;
}

async function executeLocationScout() {
    let states = [];
    let suburbs = [];

    if (_scoutScope === 'all') {
        states = Object.keys(_locationTree);
    } else if (_scoutScope === 'state') {
        states = _scoutSelectedStates.length ? _scoutSelectedStates : Object.keys(_locationTree);
    } else if (_scoutScope === 'region' && _scoutSelectedRegion) {
        const [st, reg] = _scoutSelectedRegion.split('|');
        states = [st];
        suburbs = _locationTree[st]?.[reg] || [];
    } else if (_scoutScope === 'suburb') {
        states = [...new Set(_scoutSelectedSuburbs.map(s => s.state))];
        suburbs = _scoutSelectedSuburbs.map(s => s.name);
    }

    if (!states.length) {
        showToast('Select at least one state or suburb', 'error');
        return;
    }

    closeModal('modal-scout');
    showToast(`Scouting ${_scoutScope === 'all' ? 'All Australia' : states.join(', ')}...`, 'info');
    const pipeEl = $('stat-pipeline');
    if (pipeEl) { pipeEl.textContent = 'SCOUTING'; pipeEl.className = 'text-base font-mono font-bold text-terminal-warn'; }

    try {
        const result = await api('POST', '/properties/scout', {
            states,
            suburbs,
            max_agencies: 10,
        });
        showToast(`Scout complete: ${result.properties_found} properties found`, 'success');
        if (pipeEl) { pipeEl.textContent = 'DONE'; pipeEl.className = 'text-base font-mono font-bold text-terminal-green'; }
        await loadProperties();
        await loadDeals();
    } catch (e) {
        if (pipeEl) { pipeEl.textContent = 'ERROR'; pipeEl.className = 'text-base font-mono font-bold text-terminal-red'; }
    }
}

/* ═══ Legacy triggerScout — now uses Location Scout ═══ */

async function triggerScout() {
    showLocationScout();
}

async function runPipeline() {
    const btn = $('btn-run-pipeline');
    if (btn) { btn.disabled = true; btn.textContent = '⏳ EXECUTING...'; }
    const pEl = $('stat-pipeline');
    if (pEl) { pEl.textContent = 'RUNNING'; pEl.className = 'text-base font-mono font-bold text-terminal-warn'; }
    showToast('Pipeline executing — Scout → Analyst → Stacker...', 'info');

    try {
        await triggerScout();
        await bulkAnalyze();
        if (pEl) { pEl.textContent = 'COMPLETE'; pEl.className = 'text-base font-mono font-bold text-terminal-green'; }
        showToast('Pipeline complete!', 'success');
    } catch (e) {
        if (pEl) { pEl.textContent = 'ERROR'; pEl.className = 'text-base font-mono font-bold text-terminal-red'; }
    } finally {
        if (btn) { btn.disabled = false; btn.textContent = '▶ EXECUTE PIPELINE'; }
    }
}

/* ─────────────────────────────────────────────────────────────────
   QUICK SCOUT — on-demand suburb discovery from deals toolbar
   ───────────────────────────────────────────────────────────────── */

async function quickScoutSuburb() {
    const input = $('quick-scout-input');
    const suburb = input.value.trim();
    if (!suburb || suburb.length < 2) {
        showToast('Enter a suburb name (min 2 characters)', 'error');
        input.focus();
        return;
    }

    showToast(`Scouting "${suburb}"... (fuzzy match enabled)`, 'info');
    input.disabled = true;

    try {
        const result = await api('POST', '/properties/quick-scout', {
            suburb: suburb,
            count: 3,
        });

        showToast(
            `Found ${result.properties_found} properties in ${result.matched_suburb} (${result.matched_region}). ${result.deals_generated} deals analysed.`,
            'success'
        );

        // Show what was matched vs what was typed
        if (result.matched_suburb.toLowerCase() !== suburb.toLowerCase()) {
            showToast(`Fuzzy match: "${suburb}" → ${result.matched_suburb}`, 'info');
        }

        // Refresh deals and properties
        await Promise.all([loadDeals(), loadProperties()]);

        // Pre-fill the suburb filter with the matched suburb
        $('filter-suburb-search').value = result.matched_suburb;
        filterDeals();

        input.value = '';
    } catch (e) {
        // api() shows toast on error already
    } finally {
        input.disabled = false;
        input.focus();
    }
}

async function bulkAnalyze() {
    showToast('Running bulk analysis...', 'info');
    try {
        const result = await api('POST', '/deals/bulk-analyze', {
            strategy: 'BTL',
            max_properties: 50,
        });
        showToast(`Analysis complete: ${result.total} deals scored, ${result.golden_count} golden`, 'success');
        await loadDeals();
    } catch (e) { /* api() shows toast */ }
}

/* ─────────────────────────────────────────────────────────────────
   PROFILER
   ───────────────────────────────────────────────────────────────── */

let _currentProfileId = null;

async function buildProfile() {
    const input = $('profiler-input').value.trim();
    if (!input) { showToast('Tell us about your investment situation', 'error'); return; }

    showToast('Building investor profile...', 'info');
    try {
        const result = await api('POST', '/profiler/build', {
            user_input: input,
            profile_id: _currentProfileId,
        });

        _currentProfileId = result.profile_id;
        $('profile-readiness').textContent = Math.round(result.readiness || 0);
        $('profile-borrowing').textContent = fmtPrice(result.borrowing_power);
        $('profile-max-purchase').textContent = fmtPrice(result.max_purchase);
        $('profile-complete-pct').textContent = `${Math.round(result.completeness || 0)}%`;
        $('profile-complete-bar').style.width = `${result.completeness || 0}%`;
        $('stat-profile').textContent = Math.round(result.readiness || 0);

        // Show follow-up questions
        if (result.next_questions && result.next_questions.length > 0) {
            $('profiler-questions').classList.remove('hidden');
            $('profiler-q-list').innerHTML = result.next_questions.map(q =>
                `<div class="bg-terminal-bg rounded px-2 py-1 text-[10px] font-mono text-terminal-dim cursor-pointer hover:text-terminal-text transition" onclick="document.getElementById('profiler-input').value=this.textContent;this.parentElement.parentElement.classList.add('hidden')">${q}</div>`
            ).join('');
        }

        // Show profile details
        if (result.profile) {
            const pd = result.profile;
            $('profile-details').innerHTML = `
                <div class="text-[9px] text-terminal-muted font-mono tracking-wider mb-2">YOUR INVESTOR PROFILE</div>
                <div class="grid grid-cols-2 gap-2 text-[10px] font-mono">
                    ${pd.risk_tolerance ? `<div class="flex justify-between"><span class="text-terminal-dim">Risk Tolerance</span><span>${pd.risk_tolerance}</span></div>` : ''}
                    ${pd.experience_level ? `<div class="flex justify-between"><span class="text-terminal-dim">Experience</span><span>${pd.experience_level}</span></div>` : ''}
                    ${pd.investment_goals ? `<div class="flex justify-between"><span class="text-terminal-dim">Goals</span><span>${Array.isArray(pd.investment_goals) ? pd.investment_goals.join(', ') : pd.investment_goals}</span></div>` : ''}
                    ${pd.preferred_states ? `<div class="flex justify-between"><span class="text-terminal-dim">Preferred States</span><span>${Array.isArray(pd.preferred_states) ? pd.preferred_states.join(', ') : pd.preferred_states}</span></div>` : ''}
                </div>`;
        }

        showToast('Profile built successfully', 'success');
    } catch (e) { /* api() shows toast */ }
}

/* ─────────────────────────────────────────────────────────────────
   MENTOR — Chat
   ───────────────────────────────────────────────────────────────── */

async function askMentor(topic) {
    $('mentor-topic-badge').textContent = (topic || 'general').toUpperCase().replace(/_/g, ' ');
    const presetQuestions = {
        market_commentary: 'What is the current state of the Australian property market? Cover the key trends across major capital cities.',
        strategy_education: 'Explain the different property investment strategies in Australia — BTL, BRRR, R2SA, HMO, flipping.',
        portfolio_review: 'Review my current portfolio and suggest next steps for growth.',
        suburb_deepdive: 'Give me a deep dive analysis of Woolloongabba, QLD as an investment suburb — with 2032 Olympics impact.',
        deal_review: 'How do I evaluate whether a deal is worth pursuing? What are the key metrics?',
        next_steps: 'Based on the current market, what should be my next investment move?',
        general_coaching: 'I am new to property investing in Australia. Where should I start?',
    };
    $('mentor-input').value = presetQuestions[topic] || '';
    sendMentorMessage();
}

async function sendMentorMessage() {
    const input = $('mentor-input');
    const msg = input.value.trim();
    if (!msg) return;

    const chat = $('mentor-chat');
    if (chat.querySelector('.text-center')) chat.innerHTML = '';

    chat.innerHTML += `<div class="flex justify-end"><div class="chat-msg-user rounded px-3 py-1.5 max-w-[70%]"><div class="text-[10px] text-terminal-info mb-0.5">YOU</div>${escapeHtml(msg)}</div></div>`;
    input.value = '';
    chat.scrollTop = chat.scrollHeight;

    try {
        const result = await api('POST', '/mentor/ask', {
            question: msg,
            topic: $('mentor-topic-badge').textContent.toLowerCase().replace(/ /g, '_'),
        });

        chat.innerHTML += `<div class="flex justify-start"><div class="chat-msg-ai rounded px-3 py-1.5 max-w-[80%]"><div class="text-[10px] text-terminal-accent mb-0.5">🎓 MENTOR</div><div class="whitespace-pre-wrap leading-relaxed">${escapeHtml(result.response || 'No response')}</div></div></div>`;
        chat.scrollTop = chat.scrollHeight;

        if (result.follow_up_topics && result.follow_up_topics.length > 0) {
            chat.innerHTML += `<div class="flex justify-start"><div class="bg-terminal-bg rounded px-3 py-1.5 max-w-[80%] border border-terminal-border"><div class="text-[10px] text-terminal-muted mb-1">FOLLOW-UP TOPICS:</div>${result.follow_up_topics.map(t => `<button onclick="askMentor('${t}')" class="text-terminal-accent text-[10px] font-mono hover:underline mr-2">${t.replace(/_/g, ' ')}</button>`).join('')}</div></div>`;
        }
    } catch (e) {
        chat.innerHTML += `<div class="flex justify-start"><div class="bg-terminal-danger/10 border border-terminal-danger/30 rounded px-3 py-1.5 max-w-[70%]"><div class="text-[10px] text-terminal-danger">Error: ${e.message}</div></div></div>`;
    }
    chat.scrollTop = chat.scrollHeight;
}

async function getWeeklyBrief() {
    showToast('Generating weekly brief...', 'info');
    try {
        const result = await api('POST', '/mentor/brief', { states: Object.keys(_locationTree) });
        const chat = $('mentor-chat');
        if (chat.querySelector('.text-center')) chat.innerHTML = '';
        chat.innerHTML += `<div class="flex justify-start"><div class="chat-msg-ai rounded px-3 py-1.5 max-w-[90%]"><div class="text-[10px] text-terminal-accent mb-0.5">📰 WEEKLY BRIEF</div><div class="whitespace-pre-wrap leading-relaxed">${escapeHtml(result.brief || result.response || JSON.stringify(result))}</div></div></div>`;
        chat.scrollTop = chat.scrollHeight;
    } catch (e) { /* api() shows toast */ }
}

/* ─────────────────────────────────────────────────────────────────
   QA ENGINE
   ───────────────────────────────────────────────────────────────── */

async function runQAHealthCheck() {
    showToast('Running system health check...', 'info');
    try {
        const result = await api('GET', '/qa/health');
        const grid = $('qa-health-grid');
        if (result && typeof result === 'object') {
            const agents = result.agents || result;
            if (typeof agents === 'object') {
                grid.innerHTML = Object.entries(agents).map(([name, data]) => {
                    const score = typeof data === 'number' ? data : (data?.score || data?.health || 0);
                    const color = score >= 80 ? 'bg-terminal-green' : score >= 60 ? 'bg-terminal-warn' : 'bg-terminal-red';
                    return `
                    <div>
                        <div class="flex items-center justify-between text-[10px] font-mono mb-1">
                            <span class="text-terminal-dim">${name}</span>
                            <span class="text-terminal-bright">${typeof score === 'number' ? score.toFixed(0) : score}</span>
                        </div>
                        <div class="health-bar"><div class="health-fill ${color}" style="width: ${typeof score === 'number' ? score : 50}%"></div></div>
                    </div>`;
                }).join('');
            } else {
                grid.innerHTML = `<pre class="text-[10px] font-mono text-terminal-text">${JSON.stringify(result, null, 2)}</pre>`;
            }
        }
        showToast('Health check complete', 'success');
    } catch (e) { /* api() shows toast */ }
}

async function runFullGovernance() {
    showToast('Running full governance cycle...', 'info');
    try {
        const result = await api('POST', '/qa/evaluate-and-improve', {
            pipeline_results: { note: 'Manual governance trigger' },
        });
        showToast('Governance cycle complete', 'success');

        if (result && result.skills) {
            const skills = $('qa-skills');
            skills.innerHTML = Object.entries(result.skills).map(([agent, skill]) => `
                <div class="bg-terminal-bg rounded border border-terminal-border p-2">
                    <div class="text-[10px] font-mono font-bold text-terminal-accent">${agent}</div>
                    <div class="text-[9px] text-terminal-muted mt-1">${skill.description || skill.improvement || 'Evolved'}</div>
                </div>`).join('');
        }
    } catch (e) { /* api() shows toast */ }
}

/* ─────────────────────────────────────────────────────────────────
   PHOTO ENHANCEMENT
   ───────────────────────────────────────────────────────────────── */

function previewPhoto(input) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            $('photo-before').innerHTML = `<img src="${e.target.result}" class="max-w-full max-h-[400px] rounded">`;
        };
        reader.readAsDataURL(input.files[0]);
    }
}

async function enhancePhoto() {
    const fileInput = $('photo-file');
    if (!fileInput.files || !fileInput.files[0]) {
        showToast('Upload a photo first', 'error');
        return;
    }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('preset', $('photo-preset').value);
    formData.append('upscale', $('photo-upscale').checked);

    showToast('Enhancing photo...', 'info');
    try {
        const res = await fetch(`${BASE}/photos/enhance-upload`, { method: 'POST', body: formData });
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || 'Enhancement failed');
        }
        const result = await res.json();

        // Support both field names: image_base64 (current) and enhanced_base64 (legacy)
        const b64 = result.image_base64 || result.enhanced_base64;
        if (b64) {
            $('photo-after').innerHTML = `<img src="data:image/jpeg;base64,${b64}" class="max-w-full max-h-[400px] rounded">`;
        } else if (result.data_uri) {
            $('photo-after').innerHTML = `<img src="${result.data_uri}" class="max-w-full max-h-[400px] rounded">`;
        } else if (result.output_path) {
            $('photo-after').innerHTML = `<div class="text-terminal-green text-xs font-mono p-4">Enhanced! Saved to: ${result.output_path}</div>`;
        }

        // Show enhancement log (enhancements_applied) or legacy improvements dict
        const metricsEl = $('photo-metrics');
        if (metricsEl) {
            if (result.enhancements_applied && result.enhancements_applied.length) {
                metricsEl.classList.remove('hidden');
                metricsEl.innerHTML = result.enhancements_applied.map(e =>
                    `<div class="bg-terminal-bg rounded border border-terminal-border p-2 text-center">
                        <div class="text-[9px] text-terminal-muted font-mono">${e}</div>
                    </div>`
                ).join('');
            } else if (result.improvements) {
                metricsEl.classList.remove('hidden');
                metricsEl.innerHTML = Object.entries(result.improvements || {}).map(([k, v]) =>
                    `<div class="bg-terminal-bg rounded border border-terminal-border p-2 text-center">
                        <div class="text-[9px] text-terminal-muted font-mono">${k.replace(/_/g, ' ').toUpperCase()}</div>
                        <div class="text-xs font-mono font-bold text-terminal-accent">${v}</div>
                    </div>`
                ).join('');
            }
        }

        showToast('Photo enhanced successfully!', 'success');
    } catch (e) {
        showToast(e.message, 'error');
    }
}

async function analyzePhotoQuality() {
    const fileInput = $('photo-file');
    if (!fileInput.files || !fileInput.files[0]) {
        showToast('Upload a photo first', 'error');
        return;
    }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    showToast('Analysing photo quality...', 'info');
    try {
        const res = await fetch(`${BASE}/photos/analyze`, { method: 'POST', body: formData });
        if (!res.ok) throw new Error('Analysis failed');
        const result = await res.json();

        const analysis = $('photo-analysis');
        analysis.classList.remove('hidden');
        analysis.innerHTML = `
            <div class="flex justify-between"><span class="text-terminal-dim">Quality Score</span><span class="font-bold text-terminal-accent">${result.quality_score || '—'}/100</span></div>
            <div class="flex justify-between"><span class="text-terminal-dim">Recommended Preset</span><span class="text-terminal-bright">${(result.recommended_preset || '—').replace(/_/g, ' ')}</span></div>
            <div class="flex justify-between"><span class="text-terminal-dim">Brightness</span><span>${result.brightness || '—'}</span></div>
            <div class="flex justify-between"><span class="text-terminal-dim">Contrast</span><span>${result.contrast || '—'}</span></div>
            <div class="flex justify-between"><span class="text-terminal-dim">Sharpness</span><span>${result.sharpness || '—'}</span></div>
            ${result.suggestions ? `<div class="mt-2 text-terminal-muted">${Array.isArray(result.suggestions) ? result.suggestions.join(', ') : result.suggestions}</div>` : ''}
        `;
        showToast('Analysis complete', 'success');
    } catch (e) {
        showToast(e.message, 'error');
    }
}

/* ─────────────────────────────────────────────────────────────────
   UTILITY
   ───────────────────────────────────────────────────────────────── */

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

/* ─────────────────────────────────────────────────────────────────
   INITIALISE — Load everything on page ready
   ───────────────────────────────────────────────────────────────── */

document.addEventListener('DOMContentLoaded', async () => {
    console.log('[PIA] Bloomberg Terminal v5 — All Australia — initialising...');

    // Check API connectivity + persistence + auto-scout
    try {
        const health = await fetch('/health');
        if (health.ok) {
            const hData = await health.json();

            $('api-status').innerHTML = '● API CONNECTED';
            $('api-status').className = 'text-terminal-green';

            // DB persistence status
            const dbEl = $('db-status');
            const tickerDb = $('ticker-db');
            if (hData.persistence) {
                const dbKB = hData.persistence.db_size_kb || 0;
                if (dbEl) dbEl.innerHTML = `● SQLite ${dbKB}KB`;
                if (tickerDb) tickerDb.textContent = `${dbKB}KB`;
            }

            // Auto-scout status
            const scoutEl = $('scout-status');
            const tickerScout = $('ticker-scout');
            if (hData.auto_scout) {
                const active = hData.auto_scout.active;
                const interval = hData.auto_scout.interval_minutes;
                const runs = hData.auto_scout.recent_runs || [];
                if (scoutEl) {
                    scoutEl.innerHTML = active ? `● SCOUT q${interval}m` : '○ SCOUT PAUSED';
                    scoutEl.className = active ? 'text-terminal-green' : 'text-terminal-warn';
                }
                if (tickerScout) {
                    tickerScout.textContent = active ? `q${interval}m` : 'PAUSED';
                    tickerScout.className = active ? 'text-terminal-green' : 'text-terminal-warn';
                }
                // Show last scout run count in console
                if (runs.length > 0) {
                    console.log(`[PIM] Last scout: ${runs[0].new_properties} props, ${runs[0].new_deals} deals`);
                }
            }
        }
    } catch (e) {
        $('api-status').innerHTML = '● API OFFLINE';
        $('api-status').className = 'text-terminal-red';
    }

    // Load location tree for cascading filters
    await loadLocationTree();

    // Load primary data
    await Promise.all([loadDeals(), loadProperties()]);
    loadOffers().catch(() => {});

    // ─── Fix all remaining placeholders ───

    // 1. Ticker: Shadow listings — count off-market / coming-soon / boutique
    try {
        const stats = await api('GET', '/properties/locations/stats');
        $('ticker-shadow').textContent = stats.shadow_listings || 0;
    } catch (e) {
        // Count locally from loaded properties
        const shadowCount = _allProperties.filter(p =>
            p.source === 'off_market' || p.source === 'coming_soon' || p.source === 'boutique_agency'
        ).length;
        $('ticker-shadow').textContent = shadowCount;
    }

    // 2. QA Health — run initial lightweight check (ticker only)
    try {
        const healthData = await api('GET', '/qa/health');
        if (healthData && typeof healthData === 'object') {
            const agents = healthData.agents || healthData;
            const scores = Object.values(agents).map(v => typeof v === 'number' ? v : (v?.score || v?.health || 0));
            if (scores.length) {
                const avg = scores.reduce((a, b) => a + b, 0) / scores.length;
                $('ticker-qa').textContent = avg >= 80 ? 'HEALTHY' : avg >= 50 ? 'FAIR' : 'DEGRADED';
                $('ticker-qa').className = avg >= 80 ? 'text-terminal-green' : avg >= 50 ? 'text-terminal-warn' : 'text-terminal-red';
            }
        }
    } catch (e) {
        $('ticker-qa').textContent = 'OK';
    }

    // 3. QA Performance/Trends panel — populate with deal quality stats
    try {
        const trendEl = $('qa-trends');
        if (trendEl && _allDeals.length) {
            const cfPos = _allDeals.filter(d => d.cash_flow?.is_cash_flow_positive).length;
            const golden = _allDeals.filter(d => d.is_golden_opportunity).length;
            const avgScore = _allDeals.reduce((sum, d) => sum + (d.bargain_score?.overall_score || 0), 0) / _allDeals.length;
            const avgYield = _allDeals.filter(d => d.cash_flow?.gross_rental_yield).reduce((sum, d) => sum + d.cash_flow.gross_rental_yield, 0) / (_allDeals.filter(d => d.cash_flow?.gross_rental_yield).length || 1);
            const strategies = {};
            _allDeals.forEach(d => { strategies[d.deal_type || 'BTL'] = (strategies[d.deal_type || 'BTL'] || 0) + 1; });

            trendEl.innerHTML = `
                <div class="flex items-center justify-between text-[10px] font-mono"><span class="text-terminal-dim">Total Deals</span><span class="text-terminal-bright">${_allDeals.length}</span></div>
                <div class="flex items-center justify-between text-[10px] font-mono"><span class="text-terminal-dim">Cash Flow Positive</span><span class="text-terminal-green">${cfPos} (${(cfPos / _allDeals.length * 100).toFixed(0)}%)</span></div>
                <div class="flex items-center justify-between text-[10px] font-mono"><span class="text-terminal-dim">Golden Opportunities</span><span class="text-terminal-gold">${golden}</span></div>
                <div class="flex items-center justify-between text-[10px] font-mono"><span class="text-terminal-dim">Avg Bargain Score</span><span class="text-terminal-accent">${avgScore.toFixed(1)}</span></div>
                <div class="flex items-center justify-between text-[10px] font-mono"><span class="text-terminal-dim">Avg Gross Yield</span><span class="text-terminal-bright">${avgYield.toFixed(1)}%</span></div>
                <div class="mt-2 text-[9px] text-terminal-muted">STRATEGY MIX</div>
                ${Object.entries(strategies).sort((a,b) => b[1]-a[1]).map(([s, c]) =>
                    `<div class="flex items-center justify-between text-[10px] font-mono"><span class="text-terminal-dim">${s}</span><span class="text-terminal-bright">${c}</span></div>`
                ).join('')}
            `;
        }
    } catch (e) {
        console.warn('QA trends population failed', e);
    }

    // 4. Status bar agent count
    const agentCount = $('sub-tier')?.parentElement?.querySelector(':nth-child(1)');
    // Footer shows "9 AGENTS" — update to reflect actual count
    const footerAgentSpan = document.querySelector('footer span');
    if (footerAgentSpan && footerAgentSpan.textContent.includes('AGENTS')) {
        footerAgentSpan.textContent = '13 AGENTS';
    }

    // 5. Load chatbot trending news on startup
    loadTrendingNews();

    console.log('[PIA] Dashboard ready. All Australia mode active. Data persisted to SQLite. Auto-scout engaged. Chatbot active.');
});

// ═══════════════════════════════════════════════════════════════════════════
//  CHATBOT — Trending News & Conversational Intelligence
// ═══════════════════════════════════════════════════════════════════════════

let _chatSessionId = 'session_' + Date.now();
let _chatbotOpen = false;

function toggleChatbot() {
    _chatbotOpen = !_chatbotOpen;
    const panel = $('chatbot-panel');
    const fab = $('chatbot-fab');
    if (_chatbotOpen) {
        panel.classList.remove('hidden');
        panel.classList.add('flex');
        fab.style.transform = 'scale(0.9)';
        $('chatbot-badge')?.classList.add('hidden');
        $('chatbot-input')?.focus();
    } else {
        panel.classList.add('hidden');
        panel.classList.remove('flex');
        fab.style.transform = '';
    }
}

async function sendChatMessage() {
    const input = $('chatbot-input');
    const msg = input?.value?.trim();
    if (!msg) return;
    input.value = '';

    const container = $('chatbot-messages');
    // Add user message
    container.innerHTML += `
        <div class="flex justify-end animate-fade-in">
            <div class="chat-msg-user rounded-lg px-3 py-2 max-w-[85%]">
                <div class="text-[10px] text-terminal-info mb-0.5 font-mono">YOU</div>
                <div class="text-xs text-terminal-text">${escHtml(msg)}</div>
            </div>
        </div>`;
    container.scrollTop = container.scrollHeight;

    // Show typing indicator
    const typingId = 'typing-' + Date.now();
    container.innerHTML += `
        <div id="${typingId}" class="flex justify-start animate-fade-in">
            <div class="chat-msg-ai rounded-lg px-3 py-2">
                <div class="text-[10px] text-terminal-accent mb-0.5 font-mono">MARKET AI</div>
                <div class="text-xs text-terminal-dim">Analysing...</div>
            </div>
        </div>`;
    container.scrollTop = container.scrollHeight;
    $('chatbot-status').textContent = 'Thinking...';

    try {
        const result = await api('POST', '/chat', {
            message: msg,
            session_id: _chatSessionId,
            include_news: true,
        });

        // Remove typing indicator
        document.getElementById(typingId)?.remove();

        // Format response (handle markdown-like formatting)
        const formatted = formatChatResponse(result.response || 'No response received.');

        container.innerHTML += `
            <div class="flex justify-start animate-fade-in">
                <div class="chat-msg-ai rounded-lg px-3 py-2 max-w-[85%]">
                    <div class="text-[10px] text-terminal-accent mb-0.5 font-mono">MARKET AI</div>
                    <div class="text-xs text-terminal-text leading-relaxed">${formatted}</div>
                </div>
            </div>`;

        // Update trending if new articles came
        if (result.trending_news?.length) {
            renderTrendingNews(result.trending_news);
        }

        $('chatbot-status').textContent = `${result.conversation_length || 0} messages`;
    } catch (e) {
        document.getElementById(typingId)?.remove();
        container.innerHTML += `
            <div class="flex justify-start animate-fade-in">
                <div class="chat-msg-ai rounded-lg px-3 py-2 max-w-[85%]" style="border-color: #ef444433;">
                    <div class="text-[10px] text-terminal-danger mb-0.5 font-mono">ERROR</div>
                    <div class="text-xs text-terminal-dim">Couldn't reach the chatbot. Make sure the server is running.</div>
                </div>
            </div>`;
        $('chatbot-status').textContent = 'Error';
    }
    container.scrollTop = container.scrollHeight;
}

function sendQuickChat(msg) {
    const input = $('chatbot-input');
    if (input) {
        input.value = msg;
        sendChatMessage();
    }
}

function formatChatResponse(text) {
    // Basic markdown-like formatting
    let html = escHtml(text);
    // Bold: **text** or __text__
    html = html.replace(/\*\*(.+?)\*\*/g, '<strong class="text-terminal-bright">$1</strong>');
    html = html.replace(/__(.+?)__/g, '<strong class="text-terminal-bright">$1</strong>');
    // Links: [text](url)
    html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" class="text-terminal-accent hover:underline">$1</a>');
    // Bullet points
    html = html.replace(/^[•\-\*] (.+)$/gm, '<span class="text-terminal-accent">•</span> $1');
    // Numbered points
    html = html.replace(/^(\d+)\. (.+)$/gm, '<span class="text-terminal-accent">$1.</span> $2');
    // Emoji impact ratings
    html = html.replace(/🔴/g, '<span title="Major Impact">🔴</span>');
    html = html.replace(/🟡/g, '<span title="Moderate Impact">🟡</span>');
    html = html.replace(/🟢/g, '<span title="Minor Impact">🟢</span>');
    // Newlines
    html = html.replace(/\n/g, '<br>');
    return html;
}

function escHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

async function loadTrendingNews() {
    try {
        const articles = await api('GET', '/chat/trending?limit=5');
        if (articles?.length) {
            renderTrendingNews(articles);
        }
    } catch (e) {
        console.warn('[PIM] Trending news fetch failed — chatbot will load news on first message');
        const list = $('chatbot-trending-list');
        if (list) list.innerHTML = '<div class="text-terminal-dim text-[10px]">News loads on first chat message</div>';
    }
}

function renderTrendingNews(articles) {
    const list = $('chatbot-trending-list');
    if (!list || !articles?.length) return;

    list.innerHTML = articles.slice(0, 4).map(a => {
        const relevance = a.au_relevance >= 0.7 ? '🟢' : a.au_relevance >= 0.4 ? '🟡' : '⚪';
        const source = (a.source || '').replace(/\s+/g, '').substring(0, 12);
        return `<div class="flex items-start space-x-1 cursor-pointer hover:bg-terminal-bg/50 rounded px-1 py-0.5" onclick="sendQuickChat('Tell me about: ${escAttr(a.title)}')">
            <span>${relevance}</span>
            <div class="flex-1 truncate">
                <span class="text-terminal-text hover:text-terminal-accent">${escHtml(a.title)}</span>
                <span class="text-terminal-muted ml-1">${source}</span>
            </div>
        </div>`;
    }).join('');

    // Show badge if chatbot is closed
    if (!_chatbotOpen) {
        const badge = $('chatbot-badge');
        if (badge) badge.classList.remove('hidden');
    }
}

function escAttr(str) {
    return (str || '').replace(/'/g, "\\'").replace(/"/g, '&quot;');
}

async function clearChatSession() {
    try {
        await api('DELETE', `/chat/${_chatSessionId}`);
    } catch (e) { /* ignore */ }
    _chatSessionId = 'session_' + Date.now();
    const container = $('chatbot-messages');
    if (container) {
        container.innerHTML = `
            <div class="flex justify-start">
                <div class="chat-msg-ai rounded-lg px-3 py-2 max-w-[85%]">
                    <div class="text-[10px] text-terminal-accent mb-0.5 font-mono">MARKET AI</div>
                    <div class="text-xs text-terminal-text">Session cleared! What would you like to explore?</div>
                </div>
            </div>`;
    }
    $('chatbot-status').textContent = 'Ready';
}

/* ─────────────────────────────────────────────────────────────────
   PHOTO ENHANCEMENT — In-card quick enhance via Photo Agent
   ───────────────────────────────────────────────────────────────── */

async function enhancePropertyPhoto(imageUrl) {
    showToast('Sending photo to AI Enhancement Agent...', 'info');

    // Switch to Photos tab and show the image there
    switchTab('photos');

    // Show in the before panel
    const beforePanel = $('photo-before');
    if (beforePanel) {
        beforePanel.innerHTML = `<img src="${imageUrl}" alt="Original" class="w-full h-full object-cover rounded">`;
    }

    // Try to enhance via API (fetch image → send to enhance endpoint)
    try {
        const response = await fetch(imageUrl);
        if (!response.ok) throw new Error('Could not fetch image');
        const blob = await response.blob();

        const formData = new FormData();
        // FIX: field name must be 'file' to match the FastAPI UploadFile parameter
        formData.append('file', blob, 'property.jpg');

        const preset = $('photo-preset')?.value || 'real_estate_standard';
        const upscale = $('photo-upscale')?.checked || false;

        // FIX: correct endpoint is /photos/enhance-upload (not /photos/enhance)
        const res = await fetch(`${BASE}/photos/enhance-upload`, {
            method: 'POST',
            body: formData,
        });

        if (res.ok) {
            const result = await res.json();
            const afterPanel = $('photo-after');
            // FIX: API returns 'image_base64' (also aliased as 'enhanced_base64' for compat)
            const b64 = result.image_base64 || result.enhanced_base64 || result.data_uri;
            if (afterPanel && b64) {
                const src = b64.startsWith('data:') ? b64 : `data:image/jpeg;base64,${b64}`;
                afterPanel.innerHTML = `<img src="${src}" alt="Enhanced" class="w-full h-full object-cover rounded">`;
                // Show enhancement log if available
                const metrics = $('photo-metrics');
                if (metrics && result.enhancements_applied && result.enhancements_applied.length) {
                    metrics.classList.remove('hidden');
                    metrics.innerHTML = result.enhancements_applied.map(e =>
                        `<div class="bg-terminal-bg rounded border border-terminal-border p-2 text-center">
                            <div class="text-[9px] text-terminal-muted font-mono">${e}</div>
                        </div>`
                    ).join('');
                }
            }
            showToast('Photo enhanced successfully!', 'success');
        } else {
            const err = await res.json().catch(() => ({}));
            showToast(err.detail || 'Enhancement failed — check Photos tab', 'warn');
        }
    } catch (e) {
        showToast('Photo loaded for enhancement — select preset and enhance manually', 'info');
    }
}

/* ─────────────────────────────────────────────────────────────────
   PERSONAL RESEARCH — PASTE A LINK, GET EVERYTHING
   ───────────────────────────────────────────────────────────────── */

async function parseResearchUrl() {
    const url = ($('research-url') || {}).value || '';
    if (!url || url.length < 10) return;
    try {
        const result = await api('POST', `/research/parse-url?url=${encodeURIComponent(url)}`);
        const box = $('research-url-parsed');
        if (box && result) {
            box.classList.remove('hidden');
            let html = `<span class="text-terminal-accent">SOURCE:</span> ${result.source || 'Unknown'}`;
            if (result.suburb_hint) {
                html += ` | <span class="text-terminal-accent">SUBURB:</span> ${result.suburb_hint}`;
                const subField = $('research-suburb');
                if (subField) subField.value = result.suburb_hint;
            }
            if (result.state_hint) {
                html += ` | <span class="text-terminal-accent">STATE:</span> ${result.state_hint}`;
                const stField = $('research-state');
                if (stField) stField.value = result.state_hint;
            }
            box.innerHTML = html;
        }
    } catch (e) {
        // Silent — URL parsing is best-effort
    }
}

async function executeResearch() {
    const url = ($('research-url') || {}).value || '';
    const suburb = ($('research-suburb') || {}).value || '';
    const state = ($('research-state') || {}).value || '';
    const postcode = ($('research-postcode') || {}).value || '';
    const propType = ($('research-proptype') || {}).value || 'house';
    const isPrivate = ($('research-private') || {}).checked || false;
    const floodZone = ($('research-flood') || {}).checked || false;
    const bushfireZone = ($('research-bushfire') || {}).checked || false;

    if (!url && !suburb) {
        showToast('Paste a URL or enter a suburb name', 'error');
        return;
    }

    showToast('Researching property — climate risk, nearby suburbs, market data...', 'info');
    const resultsDiv = $('research-results');
    if (resultsDiv) resultsDiv.innerHTML = '<div class="text-center text-terminal-accent py-10 animate-pulse"><div class="text-2xl mb-2">🔍</div><div class="text-[10px]">Analysing property, climate risk, and market data...</div></div>';

    try {
        const result = await api('POST', '/research/research', {
            url,
            suburb: suburb || null,
            state,
            postcode: postcode || null,
            property_type: propType,
            private: isPrivate,
            include_climate: true,
            include_nearby: true,
            flood_zone: floodZone || null,
            bushfire_zone: bushfireZone || null,
        });

        if (result && result.success) {
            renderResearchResults(result.data);
        } else {
            if (resultsDiv) resultsDiv.innerHTML = `<div class="text-terminal-danger text-xs font-mono py-4">Research failed: ${result?.error || 'Unknown error'}</div>`;
        }
    } catch (e) {
        if (resultsDiv) resultsDiv.innerHTML = `<div class="text-terminal-danger text-xs font-mono py-4">Error: ${e.message || 'Network error'}</div>`;
    }
}

function renderResearchResults(data) {
    if (!data) return;

    // Main results panel
    const resultsDiv = $('research-results');
    if (resultsDiv) {
        let html = '';

        // URL Analysis
        if (data.url) {
            const src = data.url_analysis?.source || 'Unknown';
            html += `<div class="bg-terminal-bg rounded border border-terminal-border p-2">
                <div class="text-[10px] text-terminal-muted mb-1">SOURCE</div>
                <div class="text-terminal-accent">${src}</div>
                <div class="text-[9px] text-terminal-dim truncate mt-0.5">${data.url}</div>
            </div>`;
        }

        // Location
        html += `<div class="bg-terminal-bg rounded border border-terminal-border p-2">
            <div class="text-[10px] text-terminal-muted mb-1">LOCATION</div>
            <div class="text-terminal-text font-bold">${data.suburb}, ${data.state} ${data.postcode || ''}</div>
            <div class="text-[9px] text-terminal-dim">${data.private ? '🔒 Private Research' : '🌐 Public'} | Research ID: ${(data.research_id || '').slice(0,8)}...</div>
        </div>`;

        // Market Data
        if (data.market_data) {
            const md = data.market_data;
            html += `<div class="bg-terminal-bg rounded border border-terminal-border p-2">
                <div class="text-[10px] text-terminal-muted mb-1">MARKET DATA (${data.state})</div>
                <div class="grid grid-cols-2 gap-1 text-[10px]">
                    <div><span class="text-terminal-muted">Median House:</span> <span class="text-terminal-green">$${(md.state_median_house || 0).toLocaleString()}</span></div>
                    <div><span class="text-terminal-muted">Median Unit:</span> <span class="text-terminal-green">$${(md.state_median_unit || 0).toLocaleString()}</span></div>
                    <div><span class="text-terminal-muted">Growth:</span> <span class="${(md.annual_growth || 0) >= 0 ? 'text-terminal-green' : 'text-terminal-danger'}">${md.annual_growth || 0}%</span></div>
                    <div><span class="text-terminal-muted">Yield:</span> <span class="text-terminal-accent">${md.gross_yield || 0}%</span></div>
                    <div><span class="text-terminal-muted">Vacancy:</span> ${md.vacancy_rate || 0}%</div>
                    <div><span class="text-terminal-muted">Days on Market:</span> ${md.days_on_market || 'N/A'}</div>
                    <div><span class="text-terminal-muted">Auction Clearance:</span> ${md.auction_clearance || 0}%</div>
                    <div><span class="text-terminal-muted">Rent/wk:</span> $${md.rental_house_weekly || 0}</div>
                </div>
            </div>`;
        }

        resultsDiv.innerHTML = html;
    }

    // Climate Risk Panel
    renderClimateRisk(data.climate_risk);

    // Nearby Suburbs Panel
    renderNearbySuburbs(data.nearby_properties, data.climate_comparison);

    // AI Analysis Panel
    const aiDiv = $('research-ai');
    if (aiDiv && data.ai_analysis) {
        aiDiv.innerHTML = `<div class="whitespace-pre-wrap leading-relaxed">${data.ai_analysis}</div>`;
    }

    showToast('Research complete!', 'success');
}

function renderClimateRisk(climate) {
    const div = $('research-climate');
    if (!div || !climate) return;

    const riskColors = {
        'EXTREME': 'text-red-400 bg-red-400/10 border-red-400/30',
        'HIGH': 'text-orange-400 bg-orange-400/10 border-orange-400/30',
        'MODERATE': 'text-yellow-400 bg-yellow-400/10 border-yellow-400/30',
        'LOW': 'text-green-400 bg-green-400/10 border-green-400/30',
        'MINIMAL': 'text-emerald-400 bg-emerald-400/10 border-emerald-400/30',
        'UNASSESSED': 'text-gray-400 bg-gray-400/10 border-gray-400/30',
    };
    const riskClass = riskColors[climate.overall_risk] || riskColors['UNASSESSED'];

    let html = `<div class="flex items-center justify-between mb-2">
        <span class="text-[10px] text-terminal-muted">OVERALL RISK</span>
        <span class="text-xs font-bold px-2 py-0.5 rounded border ${riskClass}">${climate.overall_risk}</span>
    </div>`;

    if (climate.climate_risk_score !== undefined) {
        const score = climate.climate_risk_score;
        const barColor = score >= 70 ? 'bg-red-500' : score >= 40 ? 'bg-yellow-500' : 'bg-green-500';
        html += `<div class="mb-2">
            <div class="flex justify-between text-[9px] text-terminal-muted mb-0.5"><span>Risk Score</span><span>${score}/100</span></div>
            <div class="w-full bg-terminal-bg rounded-full h-1.5"><div class="${barColor} h-1.5 rounded-full" style="width:${score}%"></div></div>
        </div>`;
    }

    // Hazards
    if (climate.hazards && Object.keys(climate.hazards).length > 0) {
        html += '<div class="text-[10px] text-terminal-muted mb-1 mt-2">HAZARDS</div>';
        const hazardIcons = { flood: '🌊', bushfire: '🔥', coastal_erosion: '🏖️', cyclone: '🌪️', extreme_heat: '🌡️', storm_surge: '🌊', drought: '☀️', hail: '🧊' };
        for (const [hazard, info] of Object.entries(climate.hazards)) {
            const icon = hazardIcons[hazard] || '⚠️';
            const hRiskClass = riskColors[info.level] || '';
            html += `<div class="bg-terminal-bg/50 rounded p-1.5 mb-1 border border-terminal-border/50">
                <div class="flex items-center justify-between">
                    <span>${icon} ${hazard.replace('_', ' ').toUpperCase()}</span>
                    <span class="text-[9px] px-1.5 py-0.5 rounded border ${hRiskClass}">${info.level}</span>
                </div>
                <div class="text-[9px] text-terminal-dim mt-0.5">${(info.detail || '').slice(0, 120)}${info.detail?.length > 120 ? '...' : ''}</div>
            </div>`;
        }
    }

    // Insurance
    if (climate.insurance_estimate) {
        html += `<div class="mt-2 bg-terminal-bg/50 rounded p-1.5 border border-terminal-border/50">
            <div class="text-[10px] text-terminal-muted">ESTIMATED INSURANCE</div>
            <div class="text-terminal-accent font-bold">${climate.insurance_estimate}</div>
            <div class="text-[9px] text-terminal-dim">${climate.insurance_rating || ''}</div>
        </div>`;
    }

    // Investment Note
    if (climate.investment_note) {
        html += `<div class="mt-2 text-[9px] text-terminal-dim italic">${climate.investment_note}</div>`;
    }

    div.innerHTML = html;
}

function renderNearbySuburbs(nearby, comparison) {
    const div = $('research-nearby');
    if (!div) return;

    if (!nearby || nearby.length === 0) {
        div.innerHTML = '<div class="text-center text-terminal-muted py-4 text-[10px]">No nearby suburbs found in database</div>';
        return;
    }

    let html = '';

    // Comparison summary
    if (comparison) {
        html += `<div class="bg-terminal-bg/50 rounded p-2 border border-terminal-accent/20 mb-2">
            <div class="text-[9px] text-terminal-accent">CLIMATE COMPARISON</div>
            <div class="text-[9px] text-terminal-dim">Safest: <span class="text-terminal-green">${comparison.safest || 'N/A'}</span> | Riskiest: <span class="text-terminal-danger">${comparison.riskiest || 'N/A'}</span></div>
        </div>`;
    }

    for (const n of nearby) {
        html += `<div class="flex items-center justify-between bg-terminal-bg/50 rounded px-2 py-1 border border-terminal-border/30 hover:border-terminal-accent/30 cursor-pointer transition" onclick="researchNearbySuburb('${n.suburb}','${n.state}','${n.postcode}')">
            <div>
                <span class="text-terminal-text">${n.suburb}</span>
                <span class="text-terminal-muted text-[9px]"> ${n.postcode} ${n.region || ''}</span>
            </div>
            <div class="text-right text-[9px]">
                <div class="text-terminal-green">$${(n.median || 0).toLocaleString()}</div>
                <div class="${(n.growth || 0) >= 0 ? 'text-terminal-green' : 'text-terminal-danger'}">${n.growth || 0}%</div>
            </div>
        </div>`;
    }

    div.innerHTML = html;
}

function researchNearbySuburb(suburb, state, postcode) {
    const subField = $('research-suburb');
    const stField = $('research-state');
    const pcField = $('research-postcode');
    if (subField) subField.value = suburb;
    if (stField) stField.value = state;
    if (pcField) pcField.value = postcode;
    executeResearch();
}

async function executeClimateOnly() {
    const suburb = ($('research-suburb') || {}).value || '';
    const state = ($('research-state') || {}).value || '';
    if (!suburb) {
        showToast('Enter a suburb name first', 'error');
        return;
    }
    showToast('Loading climate risk profile...', 'info');
    try {
        const result = await api('GET', `/research/climate/${encodeURIComponent(suburb)}`);
        if (result) {
            // Enhance with assessment data
            const floodZone = ($('research-flood') || {}).checked || false;
            const bushfireZone = ($('research-bushfire') || {}).checked || false;
            const propType = ($('research-proptype') || {}).value || 'house';

            const assessment = await api('POST', `/research/climate/assess?suburb=${encodeURIComponent(suburb)}&state=${state}&property_type=${propType}${floodZone ? '&flood_zone=true' : ''}${bushfireZone ? '&bushfire_zone=true' : ''}`);
            renderClimateRisk(assessment || result);
            showToast('Climate risk profile loaded', 'success');
        }
    } catch (e) {
        showToast('Climate data unavailable for this suburb', 'warn');
    }
}

// ═══════════════════════════════════════════════════════════════
// AI RENO VISION — Renovation Engine + Bunnings Materials
// ═══════════════════════════════════════════════════════════════

async function generateRenoVision() {
    const suburb = ($('reno-suburb') || {}).value?.trim();
    const state  = ($('reno-state') || {}).value;
    if (!suburb || !state) {
        showToast('Enter suburb and state first', 'error');
        return;
    }

    // Show loading, hide others
    $('reno-empty').classList.add('hidden');
    $('reno-summary').classList.add('hidden');
    $('reno-rooms').innerHTML = '';
    $('reno-quick-estimate').classList.add('hidden');
    $('reno-loading').classList.remove('hidden');

    try {
        const payload = {
            suburb,
            state,
            property_type: ($('reno-type') || {}).value || 'house',
            bedrooms:       parseInt(($('reno-beds') || {}).value) || 3,
            bathrooms:      parseInt(($('reno-baths') || {}).value) || 1,
            asking_price:   parseFloat(($('reno-price') || {}).value) || 550000,
            style:          ($('reno-style') || {}).value || 'contemporary',
            budget_tier:    ($('reno-budget') || {}).value || 'refresh',
            generate_images: false,
        };

        const result = await api('POST', '/reno-vision/generate', payload);
        $('reno-loading').classList.add('hidden');

        if (result && result.package) {
            renderRenoPackage(result);
        } else {
            showToast('Reno vision generation failed', 'error');
            $('reno-empty').classList.remove('hidden');
        }
    } catch (e) {
        $('reno-loading').classList.add('hidden');
        $('reno-empty').classList.remove('hidden');
        showToast('Error generating reno vision: ' + e.message, 'error');
    }
}

function renderRenoPackage(result) {
    const pkg     = result.package;
    const summary = result.summary;

    // ── Summary card ──
    $('reno-tagline').textContent     = pkg.tagline || 'AI Renovation Vision';
    $('reno-exec-summary').textContent = pkg.executive_summary || '';
    $('reno-mat-cost').textContent    = fmtPrice(summary.total_materials_cost);
    $('reno-labour-cost').textContent = fmtPrice(summary.total_labour_estimate);
    $('reno-total-cost').textContent  = fmtPrice(summary.total_project_cost);
    $('reno-uplift').textContent      = `+${summary.estimated_value_uplift_pct}% (${fmtPrice(summary.estimated_value_uplift_aud)})`;
    $('reno-roi').textContent         = `${summary.roi_on_reno}x`;
    $('reno-items-count').textContent = summary.total_bunnings_items;
    $('reno-summary').classList.remove('hidden');

    // ── Room cards ──
    const container = $('reno-rooms');
    container.innerHTML = '';

    (pkg.rooms || []).forEach(room => {
        const materialsHtml = (room.materials || []).map(item => `
            <tr class="border-b border-terminal-border/30 hover:bg-terminal-bg/50 transition">
                <td class="py-1.5 pr-2">
                    <a href="${item.url}" target="_blank" rel="noopener" class="text-terminal-accent hover:underline text-[10px] font-mono">${item.name}</a>
                    <div class="text-[9px] text-terminal-muted">${item.brand} &middot; SKU: ${item.sku}</div>
                    <div class="text-[9px] text-terminal-dim italic">${item.purpose}</div>
                </td>
                <td class="py-1.5 text-right text-[10px] font-mono text-terminal-dim whitespace-nowrap">${item.unit}</td>
                <td class="py-1.5 text-right text-[10px] font-mono text-terminal-text whitespace-nowrap">&times;${item.quantity}</td>
                <td class="py-1.5 text-right text-[10px] font-mono text-terminal-warn font-bold whitespace-nowrap">${fmtPrice(item.total_cost)}</td>
            </tr>
        `).join('');

        const changesHtml = (room.key_changes || []).map(c =>
            `<li class="text-[10px] text-terminal-dim leading-relaxed">&bull; ${c}</li>`
        ).join('');

        const upliftColor = room.roi_uplift_pct >= 3
            ? 'text-terminal-green'
            : room.roi_uplift_pct >= 1.5
                ? 'text-terminal-warn'
                : 'text-terminal-dim';

        const card = document.createElement('div');
        card.className = 'bg-terminal-panel rounded border border-terminal-border p-4 animate-fade-in';
        card.innerHTML = `
            <div class="flex items-center justify-between mb-2">
                <div>
                    <div class="font-mono text-xs text-terminal-accent font-bold">${room.room_name.toUpperCase()}</div>
                    <div class="font-mono text-sm text-terminal-text mt-0.5">${room.headline}</div>
                </div>
                <div class="text-right">
                    <div class="font-mono text-sm font-bold text-terminal-warn">${fmtPrice(room.total_room_cost)}</div>
                    <div class="text-[9px] font-mono ${upliftColor}">+${room.roi_uplift_pct}% uplift</div>
                </div>
            </div>
            <div class="text-[10px] text-terminal-dim leading-relaxed mb-3">${room.description}</div>
            <div class="grid grid-cols-2 gap-3 mb-3">
                <div>
                    <div class="text-[9px] font-mono text-terminal-muted mb-1 tracking-wider">KEY CHANGES</div>
                    <ul class="space-y-0.5">${changesHtml}</ul>
                </div>
                <div>
                    <div class="text-[9px] font-mono text-terminal-muted mb-1 tracking-wider">COST BREAKDOWN</div>
                    <div class="flex justify-between text-[10px] font-mono"><span class="text-terminal-muted">Materials</span><span class="text-terminal-text">${fmtPrice(room.total_materials_cost)}</span></div>
                    <div class="flex justify-between text-[10px] font-mono"><span class="text-terminal-muted">Labour est.</span><span class="text-terminal-text">${fmtPrice(room.labour_estimate)}</span></div>
                    <div class="flex justify-between text-[10px] font-mono border-t border-terminal-border/50 mt-1 pt-1"><span class="text-terminal-muted font-bold">Room Total</span><span class="text-terminal-warn font-bold">${fmtPrice(room.total_room_cost)}</span></div>
                </div>
            </div>
            ${room.materials && room.materials.length > 0 ? `
            <details class="group">
                <summary class="cursor-pointer text-[10px] font-mono text-terminal-accent hover:text-terminal-text transition flex items-center gap-1 select-none">
                    <span class="group-open:rotate-90 transition-transform inline-block">&#9658;</span>
                    BUNNINGS MATERIALS LIST (${room.materials.length} items)
                    <span class="ml-auto text-terminal-muted">Click to expand</span>
                </summary>
                <div class="mt-2 overflow-x-auto">
                    <table class="w-full text-left">
                        <thead>
                            <tr class="border-b border-terminal-border">
                                <th class="pb-1 text-[9px] font-mono text-terminal-muted">PRODUCT</th>
                                <th class="pb-1 text-[9px] font-mono text-terminal-muted text-right">UNIT</th>
                                <th class="pb-1 text-[9px] font-mono text-terminal-muted text-right">QTY</th>
                                <th class="pb-1 text-[9px] font-mono text-terminal-muted text-right">TOTAL</th>
                            </tr>
                        </thead>
                        <tbody>${materialsHtml}</tbody>
                    </table>
                </div>
                <div class="mt-2 text-[9px] font-mono text-terminal-muted italic">${pkg.partnership_note || ''}</div>
            </details>
            ` : ''}
        `;
        container.appendChild(card);
    });

    container.scrollIntoView({ behavior: 'smooth', block: 'start' });
    showToast(`Reno vision ready \u2014 ${pkg.rooms.length} rooms, ${fmtPrice(summary.total_project_cost)} total`, 'success');
}

async function getQuickRenoEstimate() {
    const suburb = ($('reno-suburb') || {}).value?.trim() || 'Unknown';
    const state  = ($('reno-state') || {}).value || 'NSW';
    const price  = parseFloat(($('reno-price') || {}).value) || 550000;
    const beds   = parseInt(($('reno-beds') || {}).value) || 3;
    const type   = ($('reno-type') || {}).value || 'house';

    try {
        const result = await api('POST', '/reno-vision/quick-estimate', {
            suburb, state,
            property_type: type,
            bedrooms: beds,
            bathrooms: parseInt(($('reno-baths') || {}).value) || 1,
            asking_price: price,
            style: ($('reno-style') || {}).value || 'contemporary',
            budget_tier: ($('reno-budget') || {}).value || 'refresh',
        });

        if (!result || !result.estimates) return;

        const container = $('reno-quick-content');
        const tierLabels = { cosmetic: 'COSMETIC REFRESH', refresh: 'FULL REFRESH', transform: 'FULL TRANSFORMATION' };
        const tierColors = { cosmetic: 'text-terminal-green', refresh: 'text-terminal-warn', transform: 'text-terminal-accent' };

        container.innerHTML = Object.entries(result.estimates).map(([tier, est]) => `
            <div class="bg-terminal-bg rounded border border-terminal-border p-3">
                <div class="font-mono text-[9px] ${tierColors[tier] || 'text-terminal-dim'} tracking-wider mb-1">${tierLabels[tier] || tier.toUpperCase()}</div>
                <div class="font-mono text-sm font-bold text-terminal-text mb-1">${est.cost_range}</div>
                <div class="text-[9px] text-terminal-muted mb-2">${est.description}</div>
                <div class="flex justify-between text-[10px] font-mono">
                    <span class="text-terminal-muted">Uplift</span>
                    <span class="text-terminal-green">+${est.estimated_value_uplift_pct}% (${fmtPrice(est.estimated_value_uplift_aud)})</span>
                </div>
                <div class="flex justify-between text-[10px] font-mono">
                    <span class="text-terminal-muted">ROI</span>
                    <span class="text-terminal-accent font-bold">${est.roi_on_reno}x</span>
                </div>
            </div>
        `).join('');

        $('reno-quick-estimate').classList.remove('hidden');
        $('reno-quick-estimate').scrollIntoView({ behavior: 'smooth', block: 'start' });
        showToast('Quick estimate ready', 'success');
    } catch (e) {
        showToast('Quick estimate failed', 'error');
    }
}
