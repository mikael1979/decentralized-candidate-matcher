// admin.js - Korjattu versio mock-datalla
console.log('🚀 Admin-sivu latautuu...');

// Mock-data testaamista varten
const MOCK_DATA = {
    systemStatus: {
        version: '1.0.0',
        active_users: 1,
        uptime: 3600,
        status: 'running'
    },
    moderationQueue: [
        {
            id: 1,
            question: { fi: "Pitäisikö kaupungin rakentaa uusi uimahalli?" },
            category: { fi: "Liikunta" },
            tags: ["liikunta", "uimahalli", "rahoitus"],
            created_by: "user123"
        }
    ],
    ipfsStatus: {
        connected: true,
        peers: 3,
        storage_used: 15728640, // 15 MB
        storage_max: 104857600, // 100 MB
        last_sync: new Date().toISOString()
    },
    adminStats: {
        total_questions: 5,
        total_candidates: 4,
        total_parties: 3,
        total_answers: 20,
        avg_answers_per_candidate: 5,
        last_updated: new Date().toISOString()
    }
};

// Sovelluksen tila
const state = {
    systemStatus: {},
    moderationQueue: [],
    ipfsStatus: {},
    adminStats: {},
    currentMeta: null,
    syncStatus: 'not_started',
    useMockData: true // Käytetään mock-dataa kunnes API:t on toteutettu
};

// DOM-elementit
let systemStatusEl, moderationQueueEl, ipfsStatusEl, adminStatsEl;
let exportDataBtn, importDataBtn, clearCacheBtn;
let generateKeysBtn, copyPublicKeyBtn, loadPrivateKeyBtn;
let manualSyncBtn, checkPeersBtn, startSyncBtn, stopSyncBtn;

// Alustus
document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ DOM ladattu, alustetaan admin-sivua...');
    initializeAdminPage();
});

async function initializeAdminPage() {
    try {
        // Etsi DOM-elementit
        findDOMElements();
        
        // Alusta välilehdet
        initializeTabs();
        
        // Aseta tapahtumankäsittelijät
        setupEventHandlers();
        
        // Lataa alustavat tiedot
        await loadInitialData();
        
        console.log('✅ Admin-sivu alustettu onnistuneesti');
        
    } catch (error) {
        console.error('❌ Admin-sivun alustus epäonnistui:', error);
        showError('Sivun alustus epäonnistui: ' + error.message);
    }
}

// Etsi DOM-elementit
function findDOMElements() {
    console.log('🔍 Etsitään DOM-elementtejä...');
    
    // Peruselementit
    systemStatusEl = document.getElementById('system-status');
    moderationQueueEl = document.getElementById('moderation-queue');
    ipfsStatusEl = document.getElementById('ipfs-status');
    adminStatsEl = document.getElementById('admin-stats');
    
    // Painikkeet
    exportDataBtn = document.getElementById('export-data-btn');
    importDataBtn = document.getElementById('import-data-btn');
    clearCacheBtn = document.getElementById('clear-cache-btn');
    generateKeysBtn = document.getElementById('generate-keys-btn');
    copyPublicKeyBtn = document.getElementById('copy-public-key-btn');
    loadPrivateKeyBtn = document.getElementById('load-private-key-btn');
    manualSyncBtn = document.getElementById('manual-sync-btn');
    checkPeersBtn = document.getElementById('check-peers-btn');
    startSyncBtn = document.getElementById('start-sync-btn');
    stopSyncBtn = document.getElementById('stop-sync-btn');
    
    console.log('✅ DOM-elementit löydetty');
}

// Alusta välilehdet
function initializeTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            const tabName = e.target.dataset.tab;
            switchTab(tabName);
        });
    });
    
    console.log('✅ Välilehdet alustettu');
}

// Vaihda välilehteä
function switchTab(tabName) {
    console.log(`🔄 Vaihdetaan välilehteä: ${tabName}`);
    
    // Poista aktiiviset luokat
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    // Aseta uusi aktiivinen välilehti
    const activeButton = document.querySelector(`[data-tab="${tabName}"]`);
    const activeContent = document.getElementById(`${tabName}-tab`);
    
    if (activeButton && activeContent) {
        activeButton.classList.add('active');
        activeContent.classList.add('active');
    }
}

// Aseta tapahtumankäsittelijät
function setupEventHandlers() {
    console.log('🔧 Asetetaan tapahtumankäsittelijät...');
    
    // Data hallinta
    if (exportDataBtn) {
        exportDataBtn.addEventListener('click', handleExportData);
    }
    if (importDataBtn) {
        importDataBtn.addEventListener('click', handleImportData);
    }
    if (clearCacheBtn) {
        clearCacheBtn.addEventListener('click', handleClearCache);
    }
    
    // Avainten hallinta
    if (generateKeysBtn) {
        generateKeysBtn.addEventListener('click', handleGenerateKeys);
    }
    if (copyPublicKeyBtn) {
        copyPublicKeyBtn.addEventListener('click', handleCopyPublicKey);
    }
    if (loadPrivateKeyBtn) {
        loadPrivateKeyBtn.addEventListener('click', handleLoadPrivateKey);
    }
    
    console.log('✅ Tapahtumankäsittelijät asetettu');
}

// Lataa alustavat tiedot
async function loadInitialData() {
    console.log('📥 Ladataan alustavia tietoja...');
    
    try {
        await loadSystemStatus();
        await loadModerationQueue();
        await loadIPFSStatus();
        await loadAdminStats();
        
    } catch (error) {
        console.error('❌ Alustavien tietojen lataus epäonnistui:', error);
        // Jatketaan mock-datalla
        useMockDataAsFallback();
    }
}

// Lataa järjestelmän tila
async function loadSystemStatus() {
    try {
        showLoading(systemStatusEl, 'Ladataan järjestelmän tilaa...');
        
        if (state.useMockData) {
            // Käytetään mock-dataa
            await new Promise(resolve => setTimeout(resolve, 500)); // Simuloi latausaikaa
            state.systemStatus = MOCK_DATA.systemStatus;
            renderSystemStatus();
            return;
        }
        
        const response = await fetch('/api/admin/status');
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        state.systemStatus = await response.json();
        renderSystemStatus();
        
    } catch (error) {
        console.warn('Järjestelmätilan API ei saatavilla, käytetään mock-dataa:', error);
        state.systemStatus = MOCK_DATA.systemStatus;
        renderSystemStatus();
    }
}

// Renderöi järjestelmän tila
function renderSystemStatus() {
    if (!systemStatusEl) return;
    
    const status = state.systemStatus;
    
    systemStatusEl.innerHTML = `
        <div class="status-grid">
            <div class="status-item">
                <span class="status-label">Tila:</span>
                <span class="status-value success">✅ Käynnissä</span>
            </div>
            <div class="status-item">
                <span class="status-label">Versio:</span>
                <span class="status-value">${status.version || '1.0.0'}</span>
            </div>
            <div class="status-item">
                <span class="status-label">Käyttäjiä:</span>
                <span class="status-value">${status.active_users || 0}</span>
            </div>
            <div class="status-item">
                <span class="status-label">Käynnissä:</span>
                <span class="status-value">${formatUptime(status.uptime)}</span>
            </div>
        </div>
        <div class="status-footer">
            <small>${state.useMockData ? '🔸 Demo-tila - Mock-data käytössä' : '✅ Yhdistetty palvelimeen'}</small>
        </div>
    `;
}

// Lataa moderaatiojono
async function loadModerationQueue() {
    try {
        showLoading(moderationQueueEl, 'Ladataan moderaatiojonoa...');
        
        if (state.useMockData) {
            await new Promise(resolve => setTimeout(resolve, 500));
            state.moderationQueue = MOCK_DATA.moderationQueue;
            renderModerationQueue();
            return;
        }
        
        const response = await fetch('/api/admin/moderation_queue');
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        state.moderationQueue = await response.json();
        renderModerationQueue();
        
    } catch (error) {
        console.warn('Moderaatiojonon API ei saatavilla, käytetään mock-dataa:', error);
        state.moderationQueue = MOCK_DATA.moderationQueue;
        renderModerationQueue();
    }
}

// Renderöi moderaatiojono
function renderModerationQueue() {
    if (!moderationQueueEl) return;
    
    if (!state.moderationQueue || state.moderationQueue.length === 0) {
        moderationQueueEl.innerHTML = `
            <div class="no-data">
                <p>🎉 Ei odottavia kysymyksiä moderointiin!</p>
                <p class="subtext">Kaikki kysymykset on käsitelty.</p>
                ${state.useMockData ? '<small>🔸 Demo-tila</small>' : ''}
            </div>
        `;
        return;
    }
    
    moderationQueueEl.innerHTML = `
        <div class="moderation-header">
            <h4>Odottaa moderointia (${state.moderationQueue.length} kpl)</h4>
            ${state.useMockData ? '<small>🔸 Demo-tila</small>' : ''}
        </div>
        <div class="moderation-list">
            ${state.moderationQueue.map(item => `
                <div class="moderation-item">
                    <div class="moderation-question">
                        <strong>${item.question?.fi || 'Kysymys'}</strong>
                        <div class="question-meta">
                            <span class="category">${item.category?.fi || 'Yleinen'}</span>
                            <span class="tags">${(item.tags || []).map(tag => `<span class="tag">${tag}</span>`).join('')}</span>
                        </div>
                        <small>Lähettäjä: ${item.created_by || 'tuntematon'}</small>
                    </div>
                    <div class="moderation-actions">
                        <button class="btn small success" onclick="approveQuestion(${item.id})">
                            ✅ Hyväksy
                        </button>
                        <button class="btn small warning" onclick="rejectQuestion(${item.id})">
                            ❌ Hylkää
                        </button>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

// Lataa IPFS-tila
async function loadIPFSStatus() {
    try {
        showLoading(ipfsStatusEl, 'Ladataan IPFS-tilaa...');
        
        if (state.useMockData) {
            await new Promise(resolve => setTimeout(resolve, 500));
            state.ipfsStatus = MOCK_DATA.ipfsStatus;
            renderIPFSStatus();
            return;
        }
        
        const response = await fetch('/api/admin/ipfs_status');
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        state.ipfsStatus = await response.json();
        renderIPFSStatus();
        
    } catch (error) {
        console.warn('IPFS-tilan API ei saatavilla, käytetään mock-dataa:', error);
        state.ipfsStatus = MOCK_DATA.ipfsStatus;
        renderIPFSStatus();
    }
}

// Renderöi IPFS-tila
function renderIPFSStatus() {
    if (!ipfsStatusEl) return;
    
    const status = state.ipfsStatus;
    
    ipfsStatusEl.innerHTML = `
        <div class="status-grid">
            <div class="status-item">
                <span class="status-label">Yhteys:</span>
                <span class="status-value ${status.connected ? 'success' : 'error'}">
                    ${status.connected ? '✅ Yhdistetty' : '❌ Katkaistu'}
                </span>
            </div>
            <div class="status-item">
                <span class="status-label">Peerit:</span>
                <span class="status-value">${status.peers || 0}</span>
            </div>
            <div class="status-item">
                <span class="status-label">Tallennustila:</span>
                <span class="status-value">${formatBytes(status.storage_used)} / ${formatBytes(status.storage_max)}</span>
            </div>
            <div class="status-item">
                <span class="status-label">Viimeisin synkronointi:</span>
                <span class="status-value">${formatDateTime(status.last_sync)}</span>
            </div>
        </div>
        <div class="status-footer">
            ${state.useMockData ? '<small>🔸 Demo-tila - Mock-data käytössä</small>' : ''}
            <button class="btn small" onclick="loadIPFSStatus()">🔄 Päivitä</button>
        </div>
    `;
}

// Lataa admin-tilastot
async function loadAdminStats() {
    try {
        showLoading(adminStatsEl, 'Ladataan tilastoja...');
        
        if (state.useMockData) {
            await new Promise(resolve => setTimeout(resolve, 500));
            state.adminStats = MOCK_DATA.adminStats;
            renderAdminStats();
            return;
        }
        
        const response = await fetch('/api/admin/stats');
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        state.adminStats = await response.json();
        renderAdminStats();
        
    } catch (error) {
        console.warn('Tilastojen API ei saatavilla, käytetään mock-dataa:', error);
        state.adminStats = MOCK_DATA.adminStats;
        renderAdminStats();
    }
}

// Renderöi admin-tilastot
function renderAdminStats() {
    if (!adminStatsEl) return;
    
    const stats = state.adminStats;
    
    adminStatsEl.innerHTML = `
        <div class="stat-card">
            <div class="stat-icon">❓</div>
            <div class="stat-content">
                <div class="stat-number">${stats.total_questions || 0}</div>
                <div class="stat-label">Kysymyksiä</div>
            </div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">👤</div>
            <div class="stat-content">
                <div class="stat-number">${stats.total_candidates || 0}</div>
                <div class="stat-label">Ehdokkaita</div>
            </div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">🏛️</div>
            <div class="stat-content">
                <div class="stat-number">${stats.total_parties || 0}</div>
                <div class="stat-label">Puolueita</div>
            </div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">💬</div>
            <div class="stat-content">
                <div class="stat-number">${stats.total_answers || 0}</div>
                <div class="stat-label">Vastauksia</div>
            </div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">📊</div>
            <div class="stat-content">
                <div class="stat-number">${stats.avg_answers_per_candidate || 0}</div>
                <div class="stat-label">Keskiarvo vastauksia</div>
            </div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">🕒</div>
            <div class="stat-content">
                <div class="stat-date">${formatDateTime(stats.last_updated)}</div>
                <div class="stat-label">Päivitetty</div>
            </div>
        </div>
    `;
}

// TAPAHTUMANKÄSITTELIJÄT

// Data vienti
async function handleExportData() {
    try {
        showInfo('📤 Viedään dataa...');
        
        // Mock-toiminto - oikeassa toteutuksessa tämä kutsuisi API:a
        const mockData = {
            questions: state.adminStats.total_questions,
            candidates: state.adminStats.total_candidates,
            parties: state.adminStats.total_parties,
            exported_at: new Date().toISOString()
        };
        
        const blob = new Blob([JSON.stringify(mockData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `vaalikone_demo_export_${Date.now()}.json`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        
        showSuccess('✅ Demo-data vienti onnistui!');
        
    } catch (error) {
        console.error('❌ Data vienti epäonnistui:', error);
        showError('Data vienti epäonnistui: ' + error.message);
    }
}

// Data tuonti
async function handleImportData() {
    showInfo('📥 Data tuonti ominaisuus on vielä kehitteillä');
}

// Välimuistin tyhjennys
async function handleClearCache() {
    try {
        showInfo('🗑️ Tyhjennetään välimuisti...');
        
        // Mock-toiminto
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        showSuccess('✅ Välimuisti tyhjennetty onnistuneesti! (demo)');
        
    } catch (error) {
        console.error('❌ Välimuistin tyhjennys epäonnistui:', error);
        showError('Välimuistin tyhjennys epäonnistui: ' + error.message);
    }
}

// Avainten hallinta
async function handleGenerateKeys() {
    try {
        showInfo('🔑 Generoidaan avainparia...');
        
        // Mock-avainten generointi
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        const mockPublicKey = `mock_pub_key_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        const mockPrivateKey = `mock_priv_key_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        
        document.getElementById('keys-result').innerHTML = `
            <div class="success-message">
                ✅ Avainpari luotu onnistuneesti! (demo)
                <div class="key-preview">
                    <strong>Julkinen avain:</strong>
                    <code>${mockPublicKey}</code>
                    <br>
                    <strong>Yksityinen avain:</strong>
                    <code>${mockPrivateKey}</code>
                </div>
                <small>🔸 Huomio: Nämä ovat demo-avaimia</small>
            </div>
        `;
        
        updatePublicKeyDisplay(mockPublicKey);
        
    } catch (error) {
        console.error('❌ Avaimen luonti epäonnistui:', error);
        showError('Avaimen luonti epäonnistui: ' + error.message);
    }
}

// Päivitä julkinen avain näyttö
function updatePublicKeyDisplay(publicKey) {
    const publicKeyEl = document.getElementById('current-public-key');
    const copyBtn = document.getElementById('copy-public-key-btn');
    
    if (publicKeyEl && copyBtn) {
        publicKeyEl.innerHTML = `
            <code>${publicKey}</code>
            <small>🔸 Demo-avain</small>
        `;
        copyBtn.style.display = 'inline-block';
    }
}

// Kopioi julkinen avain
async function handleCopyPublicKey() {
    const publicKeyEl = document.getElementById('current-public-key');
    const publicKey = publicKeyEl.querySelector('code')?.textContent;
    
    if (!publicKey) {
        showError('Ei julkista avainta saatavilla');
        return;
    }
    
    try {
        await navigator.clipboard.writeText(publicKey);
        showSuccess('✅ Julkinen avain kopioitu leikepöydälle!');
    } catch (error) {
        console.error('❌ Kopiointi epäonnistui:', error);
        showError('Kopiointi epäonnistui');
    }
}

// Lataa yksityinen avain
function handleLoadPrivateKey() {
    showInfo('🔐 Yksityisen avaimen lataus on vielä kehitteillä');
}

// MODERAATIO-TOIMINNOT
async function approveQuestion(questionId) {
    try {
        showInfo(`✅ Hyväksytään kysymys ${questionId}...`);
        
        // Mock-toiminto
        await new Promise(resolve => setTimeout(resolve, 500));
        
        showSuccess(`✅ Kysymys ${questionId} hyväksytty! (demo)`);
        
        // Poista hyväksytty kysymys jonosta
        state.moderationQueue = state.moderationQueue.filter(item => item.id !== questionId);
        renderModerationQueue();
        
    } catch (error) {
        console.error('Kysymyksen hyväksyminen epäonnistui:', error);
        showError('Kysymyksen hyväksyminen epäonnistui: ' + error.message);
    }
}

async function rejectQuestion(questionId) {
    try {
        showInfo(`❌ Hylätään kysymys ${questionId}...`);
        
        // Mock-toiminto
        await new Promise(resolve => setTimeout(resolve, 500));
        
        showSuccess(`✅ Kysymys ${questionId} hylätty! (demo)`);
        
        // Poista hylätty kysymys jonosta
        state.moderationQueue = state.moderationQueue.filter(item => item.id !== questionId);
        renderModerationQueue();
        
    } catch (error) {
        console.error('Kysymyksen hylkääminen epäonnistui:', error);
        showError('Kysymyksen hylkääminen epäonnistui: ' + error.message);
    }
}

// APUFUNKTIOT

function showLoading(element, message = 'Ladataan...') {
    if (element) {
        element.innerHTML = `
            <div class="loading">
                <div class="spinner"></div>
                <p>${message}</p>
            </div>
        `;
    }
}

function showError(message) {
    // Yksinkertainen error-ilmoitus
    alert('❌ ' + message);
}

function showSuccess(message) {
    // Yksinkertainen success-ilmoitus
    alert('✅ ' + message);
}

function showInfo(message) {
    // Yksinkertainen info-ilmoitus
    console.log('ℹ️ ' + message);
}

function formatDateTime(dateString) {
    if (!dateString) return 'Ei saatavilla';
    try {
        const date = new Date(dateString);
        return date.toLocaleString('fi-FI');
    } catch {
        return 'Virheellinen päivämäärä';
    }
}

function formatUptime(seconds) {
    if (!seconds) return '0 s';
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${minutes}min`;
}

function formatBytes(bytes) {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function useMockDataAsFallback() {
    console.log('🔄 Käytetään mock-dataa fallbackina...');
    state.useMockData = true;
    state.systemStatus = MOCK_DATA.systemStatus;
    state.moderationQueue = MOCK_DATA.moderationQueue;
    state.ipfsStatus = MOCK_DATA.ipfsStatus;
    state.adminStats = MOCK_DATA.adminStats;
    
    renderSystemStatus();
    renderModerationQueue();
    renderIPFSStatus();
    renderAdminStats();
}

// Julkiset funktiot (käytettävissä HTML:stä)
window.approveQuestion = approveQuestion;
window.rejectQuestion = rejectQuestion;
window.loadSystemStatus = loadSystemStatus;
window.loadModerationQueue = loadModerationQueue;
window.loadIPFSStatus = loadIPFSStatus;
window.loadAdminStats = loadAdminStats;
