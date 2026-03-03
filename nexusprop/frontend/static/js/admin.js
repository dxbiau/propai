/**
 * Australian Property Associates — Admin Control Panel JS
 *
 * Admin-only operations: Pipeline, QA Engine, Health, Scout Log.
 * Protected by simple password gate with session token.
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
    // Attach admin token if available
    const token = sessionStorage.getItem('apa_admin_token');
    if (token) opts.headers['Authorization'] = `Bearer ${token}`;

    if (body && method !== 'GET') opts.body = JSON.stringify(body);

    let url = `${BASE}${path}`;
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
   HELPERS
   ───────────────────────────────────────────────────────────────── */

function $(id) { return document.getElementById(id); }
function fmtPrice(v) { return v ? `$${Number(v).toLocaleString('en-AU', {maximumFractionDigits:0})}` : '—'; }
function fmtPct(v, d=1) { return v != null ? `${Number(v).toFixed(d)}%` : '—'; }

/* ─────────────────────────────────────────────────────────────────
   TAB SWITCHING
   ───────────────────────────────────────────────────────────────── */

const TAB_IDS = ['pipeline','qa','health','scout-log'];

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

    // Auto-load data on tab switch
    if (name === 'health') loadHealth();
    if (name === 'scout-log') loadScoutLog();
    if (name === 'qa') runQAHealthCheck();
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

/* ─────────────────────────────────────────────────────────────────
   AUTH — Login / Verify / Logout
   ───────────────────────────────────────────────────────────────── */

async function adminLogin() {
    const key = $('admin-key-input').value.trim();
    if (!key) { showToast('Enter admin key', 'error'); return; }

    const btn = $('btn-admin-login');
    btn.disabled = true;
    btn.textContent = '⏳ VERIFYING...';
    $('login-error').classList.add('hidden');

    try {
        const result = await fetch(`${BASE}/admin/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ key }),
        });

        if (!result.ok) {
            const err = await result.json().catch(() => ({ detail: 'Invalid key' }));
            throw new Error(err.detail || 'Access denied');
        }

        const data = await result.json();
        sessionStorage.setItem('apa_admin_token', data.token);
        showAdminDashboard();
        showToast('Admin access granted', 'success');
    } catch (e) {
        $('login-error').textContent = e.message || 'Authentication failed';
        $('login-error').classList.remove('hidden');
    } finally {
        btn.disabled = false;
        btn.textContent = '🔐 AUTHENTICATE';
    }
}

async function verifyAdmin() {
    const token = sessionStorage.getItem('apa_admin_token');
    if (!token) return false;

    try {
        const res = await fetch(`${BASE}/admin/verify`, {
            headers: { 'Authorization': `Bearer ${token}` },
        });
        return res.ok;
    } catch (e) {
        return false;
    }
}

function adminLogout() {
    sessionStorage.removeItem('apa_admin_token');
    $('admin-dashboard').classList.add('hidden');
    $('login-gate').classList.remove('hidden');
    $('admin-key-input').value = '';
    showToast('Logged out', 'info');
}

function showAdminDashboard() {
    $('login-gate').classList.add('hidden');
    $('admin-dashboard').classList.remove('hidden');
    $('admin-dashboard').classList.add('flex');
    initAdminData();
}

/* ─────────────────────────────────────────────────────────────────
   LOCATION TREE & SCOUT
   ───────────────────────────────────────────────────────────────── */

let _locationTree = {};
let _scoutScope = 'all';
let _scoutSelectedStates = [];
let _scoutSelectedRegion = '';
let _scoutSelectedSuburbs = [];

async function loadLocationTree() {
    try {
        const data = await api('GET', '/properties/locations');
        if (data && typeof data === 'object') _locationTree = data;
    } catch (e) { /* fail silently */ }
}

function showLocationScout() {
    showModal('modal-scout');
    loadScoutData();
    setScoutScope('all');
}

async function loadScoutData() {
    if (!Object.keys(_locationTree).length) await loadLocationTree();
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
    _scoutSelectedStates = Object.keys(_locationTree);
    _scoutSelectedRegion = '';
    _scoutSelectedSuburbs = [];

    ['all', 'region', 'suburb'].forEach(s => {
        const btn = $(`scout-scope-${s}`);
        if (!btn) return;
        if (s === scope) {
            btn.className = 'bg-terminal-accent/20 text-terminal-accent px-3 py-1.5 rounded text-xs font-mono font-medium border border-terminal-accent/30 transition';
        } else {
            btn.className = 'bg-terminal-panel text-terminal-dim px-3 py-1.5 rounded text-xs font-mono font-medium border border-terminal-border transition hover:text-terminal-text';
        }
    });

    $('scout-region-row').classList.toggle('hidden', scope === 'all');
    $('scout-suburb-row').classList.toggle('hidden', scope !== 'suburb');
    const mp = $('scout-market-preview');
    if (mp) mp.classList.add('hidden');
    $('scout-suburb-results').innerHTML = '';
    $('scout-selected-suburbs').innerHTML = '';

    if (scope === 'region' || scope === 'suburb') populateScoutRegions();
    updateScoutSummary();
}

function onScoutStateChange() {
    const val = $('scout-state-select').value;
    if (val) {
        _scoutSelectedStates = [val];
    } else {
        _scoutSelectedStates = Object.keys(_locationTree);
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
    const mp = $('scout-market-preview');
    if (!suburbs.length) { if (mp) mp.classList.add('hidden'); return; }
    if (mp) mp.classList.remove('hidden');
    const show = suburbs.slice(0, 12);
    $('scout-market-grid').innerHTML = show.map(s =>
        `<div class="bg-terminal-bg rounded border border-terminal-border p-2">
            <div class="text-[10px] font-mono font-bold text-terminal-bright">${s.name}</div>
            <div class="text-[9px] text-terminal-dim">${s.state} · ${s.region}</div>
        </div>`
    ).join('');
}

function updateScoutSummary() {
    let target = '', regionCount = '—', suburbCount = '—';
    if (_scoutScope === 'all') {
        target = 'All Australia — 6 States';
        const totalRegions = Object.values(_locationTree).reduce((sum, r) => sum + Object.keys(r).length, 0);
        const totalSuburbs = Object.values(_locationTree).reduce((sum, r) => sum + Object.values(r).reduce((s2, subs) => s2 + subs.length, 0), 0);
        regionCount = `${totalRegions} Regions`;
        suburbCount = `${totalSuburbs} Suburbs`;
    } else if (_scoutScope === 'state') {
        const states = _scoutSelectedStates.length ? _scoutSelectedStates.join(', ') : 'None selected';
        target = states;
        let rC = 0, sC = 0;
        _scoutSelectedStates.forEach(st => {
            if (_locationTree[st]) {
                rC += Object.keys(_locationTree[st]).length;
                sC += Object.values(_locationTree[st]).reduce((s, a) => s + a.length, 0);
            }
        });
        regionCount = `${rC} Regions`;
        suburbCount = `${sC} Suburbs`;
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
    $('scout-property-count').textContent = '—';
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
    $('stat-pipeline').textContent = 'SCOUTING';
    $('stat-pipeline').className = 'text-base font-mono font-bold text-terminal-warn kpi-value';

    try {
        const result = await api('POST', '/properties/scout', { states, suburbs, max_agencies: 10 });
        showToast(`Scout complete: ${result.properties_found} properties found`, 'success');
        $('stat-pipeline').textContent = 'DONE';
        $('stat-pipeline').className = 'text-base font-mono font-bold text-terminal-green kpi-value';
        loadScoutLog();
    } catch (e) {
        $('stat-pipeline').textContent = 'ERROR';
        $('stat-pipeline').className = 'text-base font-mono font-bold text-terminal-red kpi-value';
    }
}

/* ─────────────────────────────────────────────────────────────────
   PIPELINE
   ───────────────────────────────────────────────────────────────── */

async function runPipeline() {
    const btn = $('btn-run-pipeline');
    btn.disabled = true;
    btn.textContent = '⏳ EXECUTING...';
    $('stat-pipeline').textContent = 'RUNNING';
    $('stat-pipeline').className = 'text-base font-mono font-bold text-terminal-warn kpi-value';
    showToast('Pipeline executing — Scout → Analyst → Stacker...', 'info');

    try {
        await executeLocationScout();
        await bulkAnalyze();
        $('stat-pipeline').textContent = 'COMPLETE';
        $('stat-pipeline').className = 'text-base font-mono font-bold text-terminal-green kpi-value';
        showToast('Pipeline complete!', 'success');
    } catch (e) {
        $('stat-pipeline').textContent = 'ERROR';
        $('stat-pipeline').className = 'text-base font-mono font-bold text-terminal-red kpi-value';
    } finally {
        btn.disabled = false;
        btn.textContent = '▶ EXECUTE PIPELINE';
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

                // Update KPI
                const scores = Object.values(agents).map(v => typeof v === 'number' ? v : (v?.score || v?.health || 0));
                if (scores.length) {
                    const avg = scores.reduce((a, b) => a + b, 0) / scores.length;
                    $('stat-qa').textContent = avg >= 80 ? 'HEALTHY' : avg >= 50 ? 'FAIR' : 'DEGRADED';
                    $('stat-qa').className = `text-base font-mono font-bold kpi-value ${avg >= 80 ? 'text-terminal-green' : avg >= 50 ? 'text-terminal-warn' : 'text-terminal-red'}`;
                }
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
            pipeline_results: { note: 'Manual governance trigger from admin' },
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
   HEALTH PANEL
   ───────────────────────────────────────────────────────────────── */

async function loadHealth() {
    try {
        const res = await fetch('/health');
        if (!res.ok) throw new Error('Health endpoint unavailable');
        const data = await res.json();

        // System Status
        const statusEl = $('health-status');
        const uptimeSec = data.uptime_seconds || 0;
        const uptimeStr = uptimeSec > 3600
            ? `${(uptimeSec / 3600).toFixed(1)}h`
            : uptimeSec > 60 ? `${(uptimeSec / 60).toFixed(0)}m` : `${uptimeSec.toFixed(0)}s`;

        statusEl.innerHTML = `
            <div class="flex items-center justify-between text-[10px] font-mono">
                <span class="text-terminal-dim">Status</span>
                <span class="text-terminal-green font-bold">${(data.status || 'unknown').toUpperCase()}</span>
            </div>
            <div class="flex items-center justify-between text-[10px] font-mono">
                <span class="text-terminal-dim">Environment</span>
                <span class="text-terminal-text">${data.environment || '—'}</span>
            </div>
            <div class="flex items-center justify-between text-[10px] font-mono">
                <span class="text-terminal-dim">Uptime</span>
                <span class="text-terminal-text">${uptimeStr}</span>
            </div>
            <div class="flex items-center justify-between text-[10px] font-mono">
                <span class="text-terminal-dim">Auto-Scout Active</span>
                <span class="${data.auto_scout?.active ? 'text-terminal-green' : 'text-terminal-warn'}">${data.auto_scout?.active ? 'YES' : 'NO'}</span>
            </div>
            <div class="flex items-center justify-between text-[10px] font-mono">
                <span class="text-terminal-dim">Scout Interval</span>
                <span class="text-terminal-text">${data.auto_scout?.interval_minutes || '—'}min</span>
            </div>`;

        // Update KPIs
        $('stat-uptime').textContent = uptimeStr;
        $('stat-api').textContent = '● UP';
        $('stat-api').className = 'text-base font-mono font-bold text-terminal-green kpi-value';

        if (data.auto_scout) {
            $('stat-scout').textContent = data.auto_scout.active ? `q${data.auto_scout.interval_minutes}m` : 'PAUSED';
            $('stat-scout').className = `text-base font-mono font-bold kpi-value ${data.auto_scout.active ? 'text-terminal-green' : 'text-terminal-warn'}`;
            $('scout-status').innerHTML = data.auto_scout.active ? `● SCOUT q${data.auto_scout.interval_minutes}m` : '○ SCOUT PAUSED';
            $('scout-status').className = data.auto_scout.active ? 'text-terminal-green' : 'text-terminal-warn';
        }

        // Services
        const servicesEl = $('health-services');
        const services = data.services || {};
        servicesEl.innerHTML = Object.entries(services).map(([name, active]) => `
            <div class="flex items-center justify-between text-[10px] font-mono">
                <span class="text-terminal-dim">${name.charAt(0).toUpperCase() + name.slice(1)}</span>
                <span class="${active ? 'text-terminal-green' : 'text-terminal-muted'}">${active ? '● ACTIVE' : '○ INACTIVE'}</span>
            </div>`).join('');

        // DB
        const dbEl = $('health-db');
        const p = data.persistence || {};
        $('stat-db-size').textContent = p.db_size_kb ? `${p.db_size_kb}KB` : '—';
        $('db-status').innerHTML = `● SQLite ${p.db_size_kb || 0}KB`;

        dbEl.innerHTML = `
            <div class="grid grid-cols-4 gap-3">
                <div class="flex flex-col items-center text-[10px] font-mono">
                    <span class="text-terminal-dim mb-1">Size</span>
                    <span class="text-terminal-bright font-bold text-sm">${p.db_size_kb || 0}KB</span>
                </div>
                <div class="flex flex-col items-center text-[10px] font-mono">
                    <span class="text-terminal-dim mb-1">Properties</span>
                    <span class="text-terminal-bright font-bold text-sm">${p.properties || 0}</span>
                </div>
                <div class="flex flex-col items-center text-[10px] font-mono">
                    <span class="text-terminal-dim mb-1">Deals</span>
                    <span class="text-terminal-bright font-bold text-sm">${p.deals || 0}</span>
                </div>
                <div class="flex flex-col items-center text-[10px] font-mono">
                    <span class="text-terminal-dim mb-1">Offers</span>
                    <span class="text-terminal-bright font-bold text-sm">${p.offers || 0}</span>
                </div>
            </div>`;

    } catch (e) {
        $('health-status').innerHTML = `<div class="text-center py-4 text-terminal-danger font-mono text-[10px]">Failed to load health data: ${e.message}</div>`;
        $('stat-api').textContent = '● DOWN';
        $('stat-api').className = 'text-base font-mono font-bold text-terminal-red kpi-value';
    }
}

/* ─────────────────────────────────────────────────────────────────
   SCOUT LOG
   ───────────────────────────────────────────────────────────────── */

async function loadScoutLog() {
    try {
        const res = await fetch('/health');
        if (!res.ok) throw new Error('Health endpoint unavailable');
        const data = await res.json();
        const runs = data.auto_scout?.recent_runs || [];

        const container = $('scout-log-list');
        if (!runs.length) {
            container.innerHTML = '<div class="text-center py-8 text-terminal-muted font-mono text-[10px]">No scout runs recorded yet. Run a Location Scout to start.</div>';
            return;
        }

        container.innerHTML = runs.map((run, i) => `
            <div class="bg-terminal-bg rounded border border-terminal-border p-3 flex items-center justify-between">
                <div class="flex items-center space-x-4">
                    <span class="text-[10px] font-mono text-terminal-muted">#${i + 1}</span>
                    <span class="text-[10px] font-mono text-terminal-dim">${run.timestamp || '—'}</span>
                </div>
                <div class="flex items-center space-x-4 text-[10px] font-mono">
                    <span class="text-terminal-accent">${run.new_properties || 0} properties</span>
                    <span class="text-terminal-green">${run.new_deals || 0} deals</span>
                    <span class="text-terminal-dim">${run.suburbs_searched || '—'} suburbs</span>
                </div>
            </div>`).join('');

    } catch (e) {
        $('scout-log-list').innerHTML = `<div class="text-center py-4 text-terminal-danger font-mono text-[10px]">${e.message}</div>`;
    }
}

/* ─────────────────────────────────────────────────────────────────
   INIT
   ───────────────────────────────────────────────────────────────── */

async function initAdminData() {
    console.log('[APA ADMIN] Initialising admin dashboard...');
    await loadLocationTree();
    loadHealth();
    loadScoutLog();
    runQAHealthCheck();
}

document.addEventListener('DOMContentLoaded', async () => {
    console.log('[APA ADMIN] Control Panel loading...');

    const isValid = await verifyAdmin();
    if (isValid) {
        showAdminDashboard();
    } else {
        sessionStorage.removeItem('apa_admin_token');
        // Focus the input
        setTimeout(() => $('admin-key-input')?.focus(), 100);
    }
});
