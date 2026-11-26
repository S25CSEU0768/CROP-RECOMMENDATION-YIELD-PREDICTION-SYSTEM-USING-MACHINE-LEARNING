/**
 * Precision Agriculture Decision Support & Yield Prediction System
 * Modern Client-Side JavaScript Application Logic
 * Bennett University • TEAM ROCKET (2025-2026)
 */

// Active Farmer Profile in Memory
let currentFarmer = null;
let confidenceChart = null;

// Initialize Lucide Icons Safely
function refreshIcons() {
    if (window.lucide && typeof window.lucide.createIcons === 'function') {
        window.lucide.createIcons();
    }
}

// ═══════════════════════════════════════════════
// NAVIGATION & VIEW SWITCHING
// ═══════════════════════════════════════════════
function toggleMobileMenu(forceState) {
    const menu = document.getElementById('mobile-menu');
    const icon = document.getElementById('mobile-menu-icon');
    if (!menu) return;
    const shouldOpen = (forceState !== undefined) ? forceState : menu.classList.contains('hidden');
    if (shouldOpen) {
        menu.classList.remove('hidden');
        if (icon) icon.setAttribute('data-lucide', 'x');
    } else {
        menu.classList.add('hidden');
        if (icon) icon.setAttribute('data-lucide', 'menu');
    }
    refreshIcons();
}

function showSection(sectionId) {
    toggleMobileMenu(false);
    const sections = ['landing', 'login', 'register', 'dashboard', 'history', 'benchmarks', 'about'];
    
    sections.forEach(id => {
        const el = document.getElementById('view-' + id);
        if (el) el.classList.add('hidden');
        
        const btn = document.getElementById('nav-' + id);
        if (btn) {
            btn.className = 'nav-btn px-3.5 py-1.5 rounded-lg text-sm font-medium transition-colors text-slate-600 hover:text-slate-900 hover:bg-slate-100';
        }
    });

    const activeEl = document.getElementById('view-' + sectionId);
    if (activeEl) activeEl.classList.remove('hidden');

    const activeBtn = document.getElementById('nav-' + sectionId);
    if (activeBtn) {
        activeBtn.className = 'nav-btn px-3.5 py-1.5 rounded-lg text-sm font-semibold transition-colors bg-emerald-50 text-emerald-700 shadow-sm border border-emerald-200/60';
    }
    
    if (sectionId === 'history') {
        fetchHistory();
    } else if (sectionId === 'register') {
        setStep(1);
    } else if (sectionId === 'dashboard') {
        setTimeout(() => {
            if (confidenceChart) {
                confidenceChart.resize();
            }
        }, 100);
    }

    window.scrollTo({ top: 0, behavior: 'smooth' });
    refreshIcons();
}

// ═══════════════════════════════════════════════
// REGISTRATION 3-STEP WIZARD
// ═══════════════════════════════════════════════
function clearRegErrors() {
    const err1 = document.getElementById('reg-error');
    const err3 = document.getElementById('reg-error-step3');
    if (err1) err1.classList.add('hidden');
    if (err3) err3.classList.add('hidden');
    const act1 = document.getElementById('reg-error-action');
    const act3 = document.getElementById('reg-error-step3-action');
    if (act1) act1.classList.add('hidden');
    if (act3) act3.classList.add('hidden');
}

function showRegError(msg, isDuplicatePhone = false) {
    const err1 = document.getElementById('reg-error');
    const msg1 = document.getElementById('reg-error-msg');
    const act1 = document.getElementById('reg-error-action');
    if (err1 && msg1) {
        msg1.textContent = msg;
        err1.classList.remove('hidden');
        if (isDuplicatePhone && act1) act1.classList.remove('hidden');
    }

    const err3 = document.getElementById('reg-error-step3');
    const msg3 = document.getElementById('reg-error-step3-msg');
    const act3 = document.getElementById('reg-error-step3-action');
    if (err3 && msg3) {
        msg3.textContent = msg;
        err3.classList.remove('hidden');
        if (isDuplicatePhone && act3) act3.classList.remove('hidden');
    }
    refreshIcons();
}

function setStep(step) {
    clearRegErrors();
    [1, 2, 3].forEach(s => {
        const el = document.getElementById('step-' + s);
        if (el) el.classList.add('hidden');
    });
    const target = document.getElementById('step-' + step);
    if (target) target.classList.remove('hidden');

    const bar = document.getElementById('reg-progress-bar');
    const badge = document.getElementById('reg-step-badge');
    const pct = document.getElementById('reg-step-percent');

    if (step === 1) {
        if (bar) bar.className = 'h-full bg-emerald-500 transition-all duration-300 w-1/3';
        if (badge) badge.textContent = 'Step 1 of 3: Personal Details';
        if (pct) pct.textContent = '33%';
    } else if (step === 2) {
        if (bar) bar.className = 'h-full bg-emerald-500 transition-all duration-300 w-2/3';
        if (badge) badge.textContent = 'Step 2 of 3: Land & Location';
        if (pct) pct.textContent = '66%';
    } else {
        if (bar) bar.className = 'h-full bg-emerald-500 transition-all duration-300 w-full';
        if (badge) badge.textContent = 'Step 3 of 3: Budget & Goals';
        if (pct) pct.textContent = '100%';
    }
    refreshIcons();
}

function validateStep1AndNext() {
    clearRegErrors();
    const name = document.getElementById('r-name').value.trim();
    const phone = document.getElementById('r-phone').value.trim();
    const password = document.getElementById('r-password').value;

    if (!name) {
        showRegError("Please enter your full name to proceed.");
        document.getElementById('r-name').focus();
        return;
    }
    if (!phone) {
        showRegError("Please enter your phone or WhatsApp number.");
        document.getElementById('r-phone').focus();
        return;
    }
    if (!password || password.length < 4) {
        showRegError("Please create a password of at least 4 characters.");
        document.getElementById('r-password').focus();
        return;
    }

    setStep(2);
}

function validateStep2AndNext() {
    clearRegErrors();
    const area = parseFloat(document.getElementById('r-area').value);
    if (isNaN(area) || area <= 0) {
        showRegError("Please enter a valid cultivable land area (greater than 0).");
        document.getElementById('r-area').focus();
        return;
    }

    setStep(3);
}

function fillDemoRegister() {
    const randomSuffix = Math.floor(10000000 + Math.random() * 90000000);
    document.getElementById('r-name').value = 'Vikram Patel';
    document.getElementById('r-phone').value = '+9198' + randomSuffix;
    document.getElementById('r-password').value = 'farmer123';
    document.getElementById('r-age').value = '38';
    document.getElementById('r-gender').value = 'Male';
    clearRegErrors();
}

// ═══════════════════════════════════════════════
// AUTHENTICATION HANDLERS
// ═══════════════════════════════════════════════
async function submitLogin() {
    const id = document.getElementById('login-id').value.trim();
    const pw = document.getElementById('login-pass').value;
    const errBox = document.getElementById('login-error');
    const errMsg = document.getElementById('login-error-msg');
    
    if (errBox) errBox.classList.add('hidden');

    try {
        const res = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone_or_name: id, password: pw })
        });
        const data = await res.json();
        
        if (data.status === 'success') {
            setFarmerSession(data.user);
            showSection('dashboard');
            triggerPrediction();
        } else {
            if (errMsg) errMsg.textContent = data.message || 'Login failed';
            if (errBox) errBox.classList.remove('hidden');
        }
    } catch (err) {
        if (errMsg) errMsg.textContent = 'Server connection error. Please make sure web server is running.';
        if (errBox) errBox.classList.remove('hidden');
    }
    refreshIcons();
}

async function submitRegister() {
    clearRegErrors();

    const name = document.getElementById('r-name').value.trim();
    const phone = document.getElementById('r-phone').value.trim();
    const password = document.getElementById('r-password').value;

    if (!name) {
        setStep(1);
        showRegError("Please enter your full name.");
        document.getElementById('r-name').focus();
        return;
    }
    if (!phone) {
        setStep(1);
        showRegError("Please enter your phone or WhatsApp number.");
        document.getElementById('r-phone').focus();
        return;
    }
    if (!password || password.length < 4) {
        setStep(1);
        showRegError("Please enter a password of at least 4 characters.");
        document.getElementById('r-password').focus();
        return;
    }

    const area = parseFloat(document.getElementById('r-area').value);
    if (isNaN(area) || area <= 0) {
        setStep(2);
        showRegError("Please specify a valid cultivable land area.");
        document.getElementById('r-area').focus();
        return;
    }

    const budget = parseFloat(document.getElementById('r-budget').value);
    if (isNaN(budget) || budget <= 0) {
        showRegError("Please specify a valid seasonal investment budget (e.g. ₹50,000).");
        document.getElementById('r-budget').focus();
        return;
    }

    const unitChecked = document.querySelector('input[name="r-unit"]:checked');
    const land_unit = unitChecked ? unitChecked.value : 'Acres';

    const payload = {
        full_name: name,
        phone: phone,
        password: password,
        age: parseInt(document.getElementById('r-age').value) || 35,
        gender: document.getElementById('r-gender').value,
        state: document.getElementById('r-state').value,
        district: document.getElementById('r-district').value.trim() || 'Central',
        land_area: area,
        land_unit: land_unit,
        investment_budget: budget,
        goal: document.getElementById('r-goal').value
    };

    const btn = document.getElementById('btn-create-account');
    const btnText = document.getElementById('btn-create-text');
    const btnIcon = document.getElementById('btn-create-icon');
    
    if (btn) btn.disabled = true;
    if (btnText) btnText.textContent = "Creating Account & Saving...";
    if (btnIcon) btnIcon.setAttribute('data-lucide', 'loader-2');
    refreshIcons();

    try {
        const res = await fetch('/api/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();

        if (data.status === 'success') {
            if (btnText) btnText.textContent = "Account Created! Loading...";
            setFarmerSession(data.user);
            setTimeout(() => {
                showSection('dashboard');
                triggerPrediction();
            }, 350);
        } else {
            const msg = data.message || 'Registration failed';
            const isDup = msg.toLowerCase().includes('already exists') || msg.toLowerCase().includes('phone');
            showRegError(msg, isDup);
        }
    } catch (err) {
        showRegError('Server connection error. Please make sure the app server is running.');
    } finally {
        if (btn) btn.disabled = false;
        if (btnText) btnText.textContent = "Create Account & Save";
        if (btnIcon) btnIcon.setAttribute('data-lucide', 'check');
        refreshIcons();
    }
}

function setFarmerSession(user) {
    currentFarmer = user;
    if (user && user.id) {
        localStorage.setItem('crop_farmer_session', JSON.stringify(user));
    }

    const name = user ? (user.full_name || 'Farmer') : 'Farmer';
    const area = user ? (user.land_area || 5.0) : 5.0;
    const unit = user ? (user.land_unit || 'Acres') : 'Acres';
    const state = user ? (user.state || 'Uttar Pradesh') : 'Uttar Pradesh';
    const district = user ? (user.district || 'Varanasi') : 'Varanasi';
    const budget = user ? (user.investment_budget || 50000) : 50000;

    const navName = document.getElementById('nav-user-name');
    if (navName) navName.textContent = name;
    const navFarm = document.getElementById('nav-user-farm');
    if (navFarm) navFarm.textContent = `${area} ${unit} • ${state.substring(0, 12)}`;
    
    const initials = name.split(' ').filter(n => n.length > 0).map(n => n[0]).join('').substring(0, 2).toUpperCase() || 'FM';
    const navAvatar = document.getElementById('nav-user-avatar');
    if (navAvatar) navAvatar.textContent = initials;
    const dashAvatar = document.getElementById('dash-avatar');
    if (dashAvatar) dashAvatar.textContent = initials;

    const dashName = document.getElementById('dash-farmer-name');
    if (dashName) {
        if (user && user.id) {
            dashName.textContent = `Welcome, ${name} 👋`;
        } else {
            dashName.textContent = 'Farm Simulation & AI Advisory';
        }
    }
    
    const dashMeta = document.getElementById('dash-farmer-meta');
    if (dashMeta) {
        dashMeta.innerHTML = `Location: <strong>${district}, ${state}</strong> • Cultivable Land: <strong>${area} ${unit}</strong> • Budget: <strong>₹${Number(budget).toLocaleString('en-IN')}</strong>`;
    }

    const statusBadge = document.getElementById('dash-farmer-status-badge');
    if (statusBadge) {
        if (user && user.id) {
            statusBadge.className = 'text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 flex items-center gap-1 border border-emerald-300/60';
            statusBadge.innerHTML = '<i data-lucide="shield-check" class="w-3.5 h-3.5 text-emerald-600"></i> Database Verified';
        } else {
            statusBadge.className = 'text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-700 flex items-center gap-1 border border-slate-200';
            statusBadge.innerHTML = '<i data-lucide="sparkles" class="w-3.5 h-3.5 text-emerald-600"></i> Interactive Simulator';
        }
    }

    const unloggedDiv = document.getElementById('auth-buttons-unlogged');
    const loggedDiv = document.getElementById('auth-buttons-logged');
    if (user && user.id) {
        if (unloggedDiv) unloggedDiv.classList.add('hidden');
        if (loggedDiv) loggedDiv.classList.remove('hidden');
    } else {
        if (unloggedDiv) unloggedDiv.classList.remove('hidden');
        if (loggedDiv) loggedDiv.classList.add('hidden');
    }
    refreshIcons();
}

function logoutFarmer() {
    currentFarmer = null;
    localStorage.removeItem('crop_farmer_session');
    
    const unloggedDiv = document.getElementById('auth-buttons-unlogged');
    const loggedDiv = document.getElementById('auth-buttons-logged');
    if (unloggedDiv) unloggedDiv.classList.remove('hidden');
    if (loggedDiv) loggedDiv.classList.add('hidden');

    setFarmerSession(null);
    showSection('landing');
    refreshIcons();
}

// ═══════════════════════════════════════════════
// DATABASE ADVISORY HISTORY
// ═══════════════════════════════════════════════
async function fetchHistory() {
    const emptyState = document.getElementById('history-empty');
    const historyTable = document.getElementById('history-table');
    const loader = document.getElementById('history-loading');

    if (!currentFarmer || !currentFarmer.id) {
        if (emptyState) emptyState.classList.remove('hidden');
        if (historyTable) historyTable.classList.add('hidden');
        if (loader) loader.classList.add('hidden');
        return;
    }

    if (loader) loader.classList.remove('hidden');
    if (emptyState) emptyState.classList.add('hidden');
    if (historyTable) historyTable.classList.add('hidden');

    try {
        const res = await fetch('/api/auth/history?user_id=' + currentFarmer.id);
        const data = await res.json();
        
        if (data.status === 'success' && data.history && data.history.length > 0) {
            const tbody = document.getElementById('history-tbody');
            if (tbody) {
                tbody.innerHTML = '';
                
                data.history.forEach(item => {
                    const tr = document.createElement('tr');
                    tr.className = 'hover:bg-slate-50 transition-colors';
                    const encodedData = encodeURIComponent(JSON.stringify(item));
                    tr.innerHTML = `
                        <td class="py-3 px-4 font-mono text-xs text-slate-500 tabular-nums">${item.created_at ? item.created_at.substring(0, 16) : '-'}</td>
                        <td class="py-3 px-4 font-bold text-slate-900">${item.recommended_crop}</td>
                        <td class="py-3 px-4 text-emerald-700 font-semibold tabular-nums">${item.confidence ? item.confidence.toFixed(1) : 0}%</td>
                        <td class="py-3 px-4 text-slate-700 tabular-nums">${item.yield_rate ? item.yield_rate.toFixed(2) : 0} t/ha</td>
                        <td class="py-3 px-4 font-semibold text-slate-900 tabular-nums">${item.total_harvest ? item.total_harvest.toFixed(2) : 0} Tons</td>
                        <td class="py-3 px-4 font-bold tabular-nums ${item.net_profit >= 0 ? 'text-emerald-600' : 'text-red-600'}">
                            ${item.net_profit >= 0 ? '+' : ''}₹${Math.round(item.net_profit || 0).toLocaleString('en-IN')}
                        </td>
                        <td class="py-3 px-4 text-xs font-semibold text-slate-600">${item.season || 'Kharif'}</td>
                        <td class="py-3 px-4 text-right">
                            <button onclick="loadHistoryItem('${encodedData}')" class="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg bg-emerald-50 hover:bg-emerald-100 text-emerald-700 border border-emerald-200 text-xs font-bold transition-all shadow-sm">
                                <i data-lucide="zap" class="w-3.5 h-3.5"></i> Load In AI
                            </button>
                        </td>
                    `;
                    tbody.appendChild(tr);
                });
            }

            if (historyTable) historyTable.classList.remove('hidden');
            refreshIcons();
        } else {
            if (emptyState) emptyState.classList.remove('hidden');
        }
    } catch (err) {
        console.error('History fetch error:', err);
        if (emptyState) emptyState.classList.remove('hidden');
    } finally {
        if (loader) loader.classList.add('hidden');
    }
}

function loadHistoryItem(encodedStr) {
    try {
        const item = JSON.parse(decodeURIComponent(encodedStr));
        const n = item.n_val !== undefined ? item.n_val : item.n;
        const p = item.p_val !== undefined ? item.p_val : item.p;
        const k = item.k_val !== undefined ? item.k_val : item.k;
        const temp = item.temperature;
        const hum = item.humidity;
        const ph = item.ph;
        const rain = item.rainfall;

        if (n !== undefined) { document.getElementById('n').value = n; syncVal('n', 'mg/kg'); }
        if (p !== undefined) { document.getElementById('p').value = p; syncVal('p', 'mg/kg'); }
        if (k !== undefined) { document.getElementById('k').value = k; syncVal('k', 'mg/kg'); }
        if (temp !== undefined) { document.getElementById('temperature').value = temp; syncVal('temperature', '°C'); }
        if (hum !== undefined) { document.getElementById('humidity').value = hum; syncVal('humidity', '%'); }
        if (ph !== undefined) { document.getElementById('ph').value = ph; syncVal('ph', 'pH'); }
        if (rain !== undefined) { document.getElementById('rainfall').value = rain; syncVal('rainfall', 'mm'); }
        
        if (item.season) {
            selectSeason(item.season);
        }

        showSection('dashboard');
        triggerPrediction();
    } catch (err) {
        console.error('Failed to load history item:', err);
    }
}

// ═══════════════════════════════════════════════
// SEASON SELECTOR & SLIDER CONTROLS
// ═══════════════════════════════════════════════
function selectSeason(seasonName) {
    const hidden = document.getElementById('hidden_season');
    if (hidden) hidden.value = seasonName;
    
    // Correctly matches the HTML radio input name "season_radio"
    const radio = document.querySelector(`input[name="season_radio"][value="${seasonName}"]`);
    if (radio) {
        radio.checked = true;
    }
}

function syncVal(id, unit) {
    const el = document.getElementById(id);
    if (!el) return;
    const val = el.value;
    const label = document.getElementById(id + '-val');
    if (label) {
        label.textContent = val + ' ' + unit;
    }
}

const PRESETS = {
    rice: { n: 90, p: 42, k: 43, temperature: 21.0, humidity: 82.0, ph: 6.5, rainfall: 202.0, season: 'Kharif' },
    maize: { n: 78, p: 46, k: 20, temperature: 24.0, humidity: 65.0, ph: 6.2, rainfall: 75.0, season: 'Kharif' },
    apple: { n: 24, p: 135, k: 198, temperature: 22.0, humidity: 92.0, ph: 5.9, rainfall: 110.0, season: 'Whole Year' },
    coffee: { n: 101, p: 29, k: 30, temperature: 26.0, humidity: 58.0, ph: 6.8, rainfall: 158.0, season: 'Whole Year' },
    cotton: { n: 118, p: 47, k: 19, temperature: 24.0, humidity: 80.0, ph: 6.9, rainfall: 80.0, season: 'Kharif' }
};

function applyPreset(type) {
    const p = PRESETS[type];
    if (!p) return;
    
    document.getElementById('n').value = p.n; syncVal('n', 'mg/kg');
    document.getElementById('p').value = p.p; syncVal('p', 'mg/kg');
    document.getElementById('k').value = p.k; syncVal('k', 'mg/kg');
    document.getElementById('temperature').value = p.temperature; syncVal('temperature', '°C');
    document.getElementById('humidity').value = p.humidity; syncVal('humidity', '%');
    document.getElementById('ph').value = p.ph; syncVal('ph', 'pH');
    document.getElementById('rainfall').value = p.rainfall; syncVal('rainfall', 'mm');

    if (p.season) {
        selectSeason(p.season);
    }

    // Update active preset visual indicator
    document.querySelectorAll('.preset-btn').forEach(btn => {
        if (btn.getAttribute('data-preset') === type) {
            btn.className = 'preset-btn px-3 py-1.5 rounded-lg text-xs font-bold bg-emerald-600 text-white shadow-sm border border-emerald-600 transition-all';
        } else {
            btn.className = 'preset-btn px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-100 hover:bg-emerald-50 hover:text-emerald-700 hover:border-emerald-200 border border-slate-200 transition-all text-slate-700';
        }
    });

    triggerPrediction();
}

// ═══════════════════════════════════════════════
// CONFIDENCE CHART (CHART.JS)
// ═══════════════════════════════════════════════
function initChart(labels, data) {
    const canvas = document.getElementById('chart-confidence');
    if (!canvas) return;
    if (typeof Chart === 'undefined') {
        console.warn('Chart.js is not loaded. Skipping chart render.');
        return;
    }
    const ctx = canvas.getContext('2d');
    if (confidenceChart) confidenceChart.destroy();
    
    try {
        confidenceChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Confidence (%)',
                    data: data,
                    backgroundColor: ['#059669', '#10b981', '#6ee7b7'],
                    borderRadius: 6,
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: ctx => ctx.raw.toFixed(1) + '% model confidence'
                        }
                    }
                },
                scales: {
                    x: { min: 0, max: 100, ticks: { callback: v => v + '%' }, grid: { color: '#f1f5f9' } },
                    y: { grid: { display: false }, ticks: { font: { weight: '600' } } }
                }
            }
        });
    } catch (e) {
        console.warn('Chart creation error caught gracefully:', e);
    }
}

// ═══════════════════════════════════════════════
// EDIT BUDGET & LAND MODAL
// ═══════════════════════════════════════════════
function openEditProfileModal() {
    const farmer = currentFarmer || {
        investment_budget: 50000,
        land_area: 5.0,
        land_unit: 'Acres'
    };

    const bInput = document.getElementById('edit-budget');
    const aInput = document.getElementById('edit-area');
    const prev = document.getElementById('edit-budget-preview');

    if (bInput) bInput.value = farmer.investment_budget || 50000;
    if (aInput) aInput.value = farmer.land_area || 5.0;
    if (prev) prev.textContent = '₹' + Number(farmer.investment_budget || 50000).toLocaleString('en-IN');

    const unitStr = (farmer.land_unit || 'Acres').toString().trim().toLowerCase();
    const isHect = unitStr.includes('hect');
    const targetUnit = isHect ? 'Hectares' : 'Acres';

    const rUnit = document.querySelector(`input[name="edit-unit"][value="${targetUnit}"]`);
    if (rUnit) rUnit.checked = true;
    const lUnit = document.getElementById('edit-unit-label');
    if (lUnit) lUnit.textContent = targetUnit;

    const modal = document.getElementById('modal-edit-profile');
    if (modal) modal.classList.remove('hidden');
    refreshIcons();
}

function closeEditProfileModal() {
    const modal = document.getElementById('modal-edit-profile');
    if (modal) modal.classList.add('hidden');
}

async function saveProfileEdits() {
    const budget = parseFloat(document.getElementById('edit-budget').value);
    const area = parseFloat(document.getElementById('edit-area').value);
    const unitEl = document.querySelector('input[name="edit-unit"]:checked');
    const unit = unitEl ? unitEl.value : 'Acres';

    if (isNaN(budget) || budget <= 0) {
        alert("Please enter a valid seasonal budget.");
        return;
    }
    if (isNaN(area) || area <= 0) {
        alert("Please enter a valid land area.");
        return;
    }

    const btn = document.getElementById('btn-save-edit-profile');
    const btnText = document.getElementById('btn-save-edit-text');
    if (btn) btn.disabled = true;
    if (btnText) btnText.textContent = "Updating...";

    try {
        if (currentFarmer && currentFarmer.id) {
            const res = await fetch('/api/auth/update_profile', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: currentFarmer.id,
                    investment_budget: budget,
                    land_area: area,
                    land_unit: unit
                })
            });
            const data = await res.json();
            if (data.status === 'success' && data.user) {
                setFarmerSession(data.user);
            }
        } else {
            const updated = {
                ...(currentFarmer || {}),
                id: null,
                full_name: currentFarmer ? currentFarmer.full_name : 'Farmer',
                state: currentFarmer ? currentFarmer.state : 'Uttar Pradesh',
                district: currentFarmer ? currentFarmer.district : 'Varanasi',
                investment_budget: budget,
                land_area: area,
                land_unit: unit
            };
            setFarmerSession(updated);
        }

        closeEditProfileModal();
        triggerPrediction();
    } catch (err) {
        console.error('Failed to update profile:', err);
        closeEditProfileModal();
    } finally {
        if (btn) btn.disabled = false;
        if (btnText) btnText.textContent = "Update & Recalculate";
        refreshIcons();
    }
}

// ═══════════════════════════════════════════════
// PRIMARY RUN PREDICTION ENGINE (THE ONE RUN BUTTON)
// ═══════════════════════════════════════════════
function setRunButtonState(loading, message = null) {
    const runBtn = document.getElementById('btn-run-prediction');
    const runBtnText = document.getElementById('btn-run-text');
    if (!runBtn) return;
    
    if (loading) {
        runBtn.disabled = true;
        runBtn.classList.add('opacity-80', 'cursor-not-allowed');
        if (runBtnText) runBtnText.textContent = message || "Running AI Inference & Yield Forecasting...";
        const iconEl = document.getElementById('btn-run-icon');
        if (iconEl && iconEl.parentNode) {
            const newI = document.createElement('i');
            newI.id = 'btn-run-icon';
            newI.setAttribute('data-lucide', 'loader-2');
            newI.className = 'w-5 h-5 text-emerald-200 animate-spin';
            iconEl.parentNode.replaceChild(newI, iconEl);
            refreshIcons();
        }
    } else {
        runBtn.disabled = false;
        runBtn.classList.remove('opacity-80', 'cursor-not-allowed');
        if (runBtnText) runBtnText.textContent = "Run Two-Stage AI Prediction & Save to Account";
        const iconEl = document.getElementById('btn-run-icon');
        if (iconEl && iconEl.parentNode) {
            const newI = document.createElement('i');
            newI.id = 'btn-run-icon';
            newI.setAttribute('data-lucide', 'sparkles');
            newI.className = 'w-5 h-5 text-emerald-200 transition-transform group-hover:scale-110';
            iconEl.parentNode.replaceChild(newI, iconEl);
            refreshIcons();
        }
    }
}

async function triggerPrediction() {
    const farmer = currentFarmer || {
        id: null,
        full_name: 'Farmer',
        state: 'Uttar Pradesh',
        district: 'Varanasi',
        land_area: 5.0,
        land_unit: 'Acres',
        investment_budget: 50000
    };

    setRunButtonState(true);

    const errBanner = document.getElementById('prediction-error-banner');
    const errText = document.getElementById('prediction-error-text');
    if (errBanner) errBanner.classList.add('hidden');

    const payload = {
        user_id: farmer.id,
        farmer_name: farmer.full_name,
        state_name: farmer.state,
        district: farmer.district,
        land_area: farmer.land_area,
        land_unit: farmer.land_unit,
        investment_budget: farmer.investment_budget,
        season: (document.getElementById('hidden_season') && document.getElementById('hidden_season').value) || 'Kharif',

        n: parseFloat(document.getElementById('n').value),
        p: parseFloat(document.getElementById('p').value),
        k: parseFloat(document.getElementById('k').value),
        temperature: parseFloat(document.getElementById('temperature').value),
        humidity: parseFloat(document.getElementById('humidity').value),
        ph: parseFloat(document.getElementById('ph').value),
        rainfall: parseFloat(document.getElementById('rainfall').value)
    };

    const loader = document.getElementById('loading-state');
    const panel = document.getElementById('results-panel');
    
    if (loader) loader.classList.remove('hidden');
    if (panel) panel.classList.add('opacity-50');

    try {
        const response = await fetch('/api/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error(`HTTP Error ${response.status}: Failed to execute prediction`);
        }

        const res = await response.json();

        if (res.status === 'success') {
            const data = res.data;
            const top = data.recommendations[0];
            const y = data.yield_forecast;
            const fin = data.financial_projection;
            const coc = fin.cost_of_cultivation;

            // Stage 1 Crop Decision
            document.getElementById('res-crop').textContent = top.crop;
            document.getElementById('res-confidence').textContent = top.confidence.toFixed(1) + '%';
            
            // Stage 2 Harvest Yield Forecast
            document.getElementById('res-yield').textContent = y.predicted_yield_tons_per_ha.toFixed(2);
            document.getElementById('res-prod').textContent = y.estimated_production_tons.toFixed(2) + ' Tons';
            document.getElementById('res-area-tag').textContent = `for ${payload.land_area} ${payload.land_unit}`;

            // Cost of Cultivation & Feasibility Breakdown
            if (coc) {
                document.getElementById('cost-avail-budget').textContent = '₹' + Math.round(fin.investment_budget_inr).toLocaleString('en-IN');
                document.getElementById('cost-total-required').textContent = '₹' + Math.round(coc.total_required_cost_inr).toLocaleString('en-IN');
                document.getElementById('cost-per-acre-tag').textContent = '₹' + Math.round(coc.per_acre_total).toLocaleString('en-IN') + ' / Acre';
                document.getElementById('cost-breakdown-area-sub').textContent = `for ${payload.land_area} ${payload.land_unit}`;

                // Phase 1: Planting
                document.getElementById('cost-p1-rate').textContent = '₹' + Math.round(coc.per_acre_planting).toLocaleString('en-IN') + '/ac';
                document.getElementById('cost-p1-total').textContent = '₹' + Math.round(coc.total_planting_seeds_inr).toLocaleString('en-IN');

                // Phase 2: Growing
                document.getElementById('cost-p2-rate').textContent = '₹' + Math.round(coc.per_acre_growing).toLocaleString('en-IN') + '/ac';
                document.getElementById('cost-p2-total').textContent = '₹' + Math.round(coc.total_growing_nutrients_inr).toLocaleString('en-IN');

                // Phase 3: Cutting & Harvesting
                document.getElementById('cost-p3-rate').textContent = '₹' + Math.round(coc.per_acre_harvesting).toLocaleString('en-IN') + '/ac';
                document.getElementById('cost-p3-total').textContent = '₹' + Math.round(coc.total_harvesting_cutting_inr).toLocaleString('en-IN');

                // Phase 4: Mandi & Cartage
                document.getElementById('cost-p4-rate').textContent = '₹' + Math.round(coc.per_acre_transport).toLocaleString('en-IN') + '/ac';
                document.getElementById('cost-p4-total').textContent = '₹' + Math.round(coc.total_transport_mandi_inr).toLocaleString('en-IN');

                // Feasibility Status Banner
                const fBanner = document.getElementById('cost-feasibility-banner');
                const fStatus = document.getElementById('cost-feasibility-status');
                const fDelta = document.getElementById('cost-delta-badge');
                const fAdvice = document.getElementById('cost-feasibility-advice');

                const oldIcon = document.getElementById('cost-feasibility-icon');
                const newIcon = document.createElement('i');
                newIcon.id = 'cost-feasibility-icon';

                if (coc.is_sufficient) {
                    fBanner.className = 'p-3.5 rounded-xl bg-emerald-50 border border-emerald-200 flex items-start gap-2.5';
                    newIcon.setAttribute('data-lucide', 'check-circle');
                    newIcon.className = 'w-4 h-4 text-emerald-600 flex-shrink-0 mt-0.5';
                    fStatus.textContent = 'Budget Sufficient';
                    fStatus.className = 'text-xs font-bold text-emerald-900';
                    fDelta.textContent = `+₹${Math.round(coc.budget_delta_inr).toLocaleString('en-IN')} Buffer`;
                    fDelta.className = 'text-[10px] font-extrabold px-2 py-0.5 rounded-full bg-emerald-200/70 text-emerald-800 tabular-nums';
                } else {
                    fBanner.className = 'p-3.5 rounded-xl bg-amber-50 border border-amber-300 flex items-start gap-2.5';
                    newIcon.setAttribute('data-lucide', 'alert-triangle');
                    newIcon.className = 'w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5';
                    fStatus.textContent = 'Budget Deficit';
                    fStatus.className = 'text-xs font-bold text-amber-950';
                    fDelta.textContent = `-₹${Math.round(Math.abs(coc.budget_delta_inr)).toLocaleString('en-IN')} Deficit`;
                    fDelta.className = 'text-[10px] font-extrabold px-2 py-0.5 rounded-full bg-amber-200/70 text-amber-900 tabular-nums';
                }
                if (oldIcon && oldIcon.parentNode) {
                    oldIcon.parentNode.replaceChild(newIcon, oldIcon);
                }
                fAdvice.textContent = coc.feasibility_advice;
            }

            // Financial ROI & Profit Metrics
            document.getElementById('res-budget-display').textContent = '₹' + Math.round(coc ? coc.total_required_cost_inr : fin.investment_budget_inr).toLocaleString('en-IN');
            document.getElementById('res-market-rate').textContent = '₹' + fin.estimated_market_rate_per_ton.toLocaleString('en-IN') + ' / ton';
            document.getElementById('res-gross-revenue').textContent = '₹' + Math.round(fin.estimated_gross_revenue_inr).toLocaleString('en-IN');
            
            const profitEl = document.getElementById('res-net-profit');
            const roiBadge = document.getElementById('res-roi-badge');
            const profitBox = document.getElementById('res-profit-box');
            
            if (fin.estimated_net_profit_inr >= 0) {
                profitEl.textContent = '+₹' + Math.round(fin.estimated_net_profit_inr).toLocaleString('en-IN');
                profitEl.className = 'font-black text-emerald-700 text-sm tabular-nums';
                roiBadge.textContent = '+' + fin.roi_percentage.toFixed(1) + '% ROI';
                roiBadge.className = 'text-[11px] font-bold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-full tabular-nums';
                if (profitBox) profitBox.className = 'flex justify-between py-2 bg-emerald-50/70 px-3 rounded-lg border border-emerald-200';
            } else {
                profitEl.textContent = '-₹' + Math.round(Math.abs(fin.estimated_net_profit_inr)).toLocaleString('en-IN');
                profitEl.className = 'font-black text-red-600 text-sm tabular-nums';
                roiBadge.textContent = fin.roi_percentage.toFixed(1) + '% ROI';
                roiBadge.className = 'text-[11px] font-bold text-red-700 bg-red-50 border border-red-200 px-2 py-0.5 rounded-full tabular-nums';
                if (profitBox) profitBox.className = 'flex justify-between py-2 bg-red-50/70 px-3 rounded-lg border border-red-200';
            }

            // Update Softmax Probability Chart
            const labels = data.recommendations.map(r => r.crop);
            const scores = data.recommendations.map(r => r.confidence);
            initChart(labels, scores);
            refreshIcons();
        } else {
            throw new Error(res.message || 'Prediction calculation error');
        }
    } catch (err) {
        console.error('Prediction failed:', err);
        if (errBanner && errText) {
            errText.textContent = `Backend AI connection error: ${err.message}. Make sure server is running (LAUNCH_PROJECT.bat or python run.py).`;
            errBanner.classList.remove('hidden');
            refreshIcons();
        }
    } finally {
        if (loader) loader.classList.add('hidden');
        if (panel) panel.classList.remove('opacity-50');
        setRunButtonState(false);
        refreshIcons();
    }
}

// ═══════════════════════════════════════════════
// GLOBAL KEYBOARD & DOM LIFECYCLE LISTENERS
// ═══════════════════════════════════════════════
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeEditProfileModal();
        toggleMobileMenu(false);
    }
});

window.addEventListener('DOMContentLoaded', () => {
    refreshIcons();
    initChart(['Rice', 'Jute', 'Pomegranate'], [94.4, 5.6, 0.0]);
    
    const saved = localStorage.getItem('crop_farmer_session');
    if (saved) {
        try {
            const parsed = JSON.parse(saved);
            setFarmerSession(parsed);
        } catch (e) {
            console.error('Session restore failed:', e);
            setFarmerSession(null);
        }
    } else {
        setFarmerSession(null);
    }

    // Run initial live prediction so dashboard is immediately ready
    triggerPrediction();
});
