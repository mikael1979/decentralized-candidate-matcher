// Ylläpidon tila
const state = {
    systemStatus: {},
    moderationQueue: [],
    ipfsStatus: {},
    currentMeta: null
};

// DOM-elementit
const systemStatusEl = document.getElementById('system-status');
const moderationQueueEl = document.getElementById('moderation-queue');
const ipfsStatusEl = document.getElementById('ipfs-status');
const adminStatsEl = document.getElementById('admin-stats');
const exportDataBtn = document.getElementById('export-data-btn');
const importDataBtn = document.getElementById('import-data-btn');
const clearCacheBtn = document.getElementById('clear-cache-btn');
const metaFormContainer = document.getElementById('meta-form');

// Meta-tiedon hallinta
class MetaManager {
    constructor() {
        this.currentMeta = null;
    }
    
    async loadMeta() {
        try {
            console.log('🔄 Ladataan meta-tietoja...');
            const response = await fetch('/api/meta');
            
            if (!response.ok) {
                throw new Error(`HTTP virhe! status: ${response.status}`);
            }
            
            this.currentMeta = await response.json();
            console.log('✅ Meta-tiedot ladattu:', this.currentMeta);
            
            this.displayMetaForm();
            this.displaySystemStats();
            
        } catch (error) {
            console.error('❌ Meta-tietojen lataus epäonnistui:', error);
            this.showError('Meta-tietojen lataus epäonnistui: ' + error.message);
        }
    }
    
    displayMetaForm() {
        if (!metaFormContainer || !this.currentMeta) return;
        
        const election = this.currentMeta.election || {};
        const name = election.name || {};
        
        metaFormContainer.innerHTML = `
            <div class="admin-card">
                <h3>🗳️ Muokkaa vaalitietoja</h3>
                <form id="edit-meta-form" class="meta-form">
                    <div class="form-group">
                        <label for="election-name-fi">Vaalien nimi (suomeksi):</label>
                        <input type="text" id="election-name-fi" value="${this.escapeHtml(name.fi || '')}" required>
                        <small>Esimerkki: "Kunnallisvaalit 2025"</small>
                    </div>
                    
                    <div class="form-group">
                        <label for="election-name-en">Vaalien nimi (englanniksi):</label>
                        <input type="text" id="election-name-en" value="${this.escapeHtml(name.en || '')}">
                        <small>Esimerkki: "Municipal Election 2025"</small>
                    </div>
                    
                    <div class="form-group">
                        <label for="election-name-sv">Vaalien nimi (ruotsiksi):</label>
                        <input type="text" id="election-name-sv" value="${this.escapeHtml(name.sv || '')}">
                        <small>Esimerkki: "Kommunalval 2025"</small>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label for="election-date">Vaalin päivämäärä:</label>
                            <input type="date" id="election-date" value="${election.date || ''}">
                        </div>
                        
                        <div class="form-group">
                            <label for="election-type">Vaalityyppi:</label>
                            <select id="election-type">
                                <option value="municipal" ${election.type === 'municipal' ? 'selected' : ''}>Kunnallisvaalit</option>
                                <option value="parliamentary" ${election.type === 'parliamentary' ? 'selected' : ''}>Eduskuntavaalit</option>
                                <option value="european" ${election.type === 'european' ? 'selected' : ''}>Europarlamenttivaalit</option>
                                <option value="presidential" ${election.type === 'presidential' ? 'selected' : ''}>Presidentinvaalit</option>
                                <option value="test" ${election.type === 'test' ? 'selected' : ''}>Testivaalit</option>
                            </select>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label for="election-country">Maa:</label>
                        <input type="text" id="election-country" value="${this.escapeHtml(election.country || 'FI')}" maxlength="2">
                        <small>Kaksikirjaiminen maakoodi (esim. FI, SE, NO)</small>
                    </div>
                    
                    <div class="form-actions">
                        <button type="submit" class="btn">
                            💾 Tallenna muutokset
                        </button>
                        <button type="button" id="reset-meta-btn" class="btn secondary">
                            🔄 Palauta alkuperäiset
                        </button>
                    </div>
                </form>
                <div id="meta-result"></div>
            </div>
        `;
        
        // Lisää lomakkeen käsittelijä
        document.getElementById('edit-meta-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.updateMeta();
        });
        
        // Lisää reset-painikkeen käsittelijä
        document.getElementById('reset-meta-btn').addEventListener('click', () => {
            this.resetMetaForm();
        });
    }
    
    async updateMeta() {
        const resultDiv = document.getElementById('meta-result');
        try {
            console.log('🔄 Päivitetään meta-tietoja...');
            
            const updatedMeta = {
                ...this.currentMeta,
                election: {
                    ...this.currentMeta.election,
                    name: {
                        fi: document.getElementById('election-name-fi').value.trim(),
                        en: document.getElementById('election-name-en').value.trim(),
                        sv: document.getElementById('election-name-sv').value.trim()
                    },
                    date: document.getElementById('election-date').value,
                    type: document.getElementById('election-type').value,
                    country: document.getElementById('election-country').value.toUpperCase()
                }
            };
            
            // Validointi
            const validationError = this.validateMetaData(updatedMeta);
            if (validationError) {
                resultDiv.innerHTML = `<div class="error-message">❌ ${validationError}</div>`;
                return;
            }
            
            const response = await fetch('/api/update_meta', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(updatedMeta)
            });
            
            const result = await response.json();
            
            if (result.success) {
                resultDiv.innerHTML = `
                    <div class="success-message">
                        ✅ Vaalitiedot päivitetty onnistuneesti!
                        <br><small>Sivu päivittyy automaattisesti...</small>
                    </div>
                `;
                
                // Päivitä sivu uusilla tiedoilla
                setTimeout(() => {
                    window.location.reload();
                }, 2000);
            } else {
                resultDiv.innerHTML = `<div class="error-message">❌ Virhe: ${result.error}</div>`;
            }
            
        } catch (error) {
            console.error('❌ Meta-tietojen päivitys epäonnistui:', error);
            resultDiv.innerHTML = `
                <div class="error-message">
                    ❌ Verkkovirhe: ${error.message}
                </div>
            `;
        }
    }
    
    validateMetaData(meta) {
        const election = meta.election || {};
        const name = election.name || {};
        
        if (!name.fi || name.fi.trim() === '') {
            return 'Vaalien nimi suomeksi on pakollinen';
        }
        
        if (!election.date) {
            return 'Vaalin päivämäärä on pakollinen';
        }
        
        if (!election.country || election.country.length !== 2) {
            return 'Maa-kentässä tulee olla kaksikirjaiminen maakoodi';
        }
        
        // Tarkista päivämäärän muoto
        const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
        if (!dateRegex.test(election.date)) {
            return 'Päivämäärän tulee olla muodossa YYYY-MM-DD';
        }
        
        return null;
    }
    
    resetMetaForm() {
        if (this.currentMeta) {
            this.displayMetaForm();
            document.getElementById('meta-result').innerHTML = `
                <div class="info-message">ℹ️ Lomake palautettu alkuperäiseen tilaan</div>
            `;
        }
    }
    
    displaySystemStats() {
        if (!adminStatsEl || !this.currentMeta) return;
        
        const stats = this.currentMeta.content || {};
        const integrity = this.currentMeta.integrity || {};
        const election = this.currentMeta.election || {};
        
        // Laske ero vaalin päivämäärään
        const electionDate = new Date(election.date);
        const today = new Date();
        const daysUntilElection = Math.ceil((electionDate - today) / (1000 * 60 * 60 * 24));
        
        let electionStatus = '';
        if (daysUntilElection > 0) {
            electionStatus = `${daysUntilElection} päivää vaaleihin`;
        } else if (daysUntilElection === 0) {
            electionStatus = 'Vaalipäivä tänään!';
        } else {
            electionStatus = 'Vaalit menneet';
        }
        
        adminStatsEl.innerHTML = `
            <div class="admin-card">
                <h3>📊 Järjestelmätilastot</h3>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-icon">⚙️</div>
                        <div class="stat-content">
                            <div class="stat-label">Versio</div>
                            <div class="stat-number">${this.currentMeta.version}</div>
                        </div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-icon">❓</div>
                        <div class="stat-content">
                            <div class="stat-label">Kysymyksiä</div>
                            <div class="stat-number">${stats.questions_count || 0}</div>
                        </div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-icon">👤</div>
                        <div class="stat-content">
                            <div class="stat-label">Ehdokkaita</div>
                            <div class="stat-number">${stats.candidates_count || 0}</div>
                        </div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-icon">🏛️</div>
                        <div class="stat-content">
                            <div class="stat-label">Puolueita</div>
                            <div class="stat-number">${stats.parties_count || 0}</div>
                        </div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-icon">🕒</div>
                        <div class="stat-content">
                            <div class="stat-label">Päivitetty</div>
                            <div class="stat-date">${this.formatDateTime(stats.last_updated)}</div>
                        </div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-icon">🔒</div>
                        <div class="stat-content">
                            <div class="stat-label">Integriteetti</div>
                            <div class="stat-status ${integrity.hash ? 'valid' : 'invalid'}">
                                ${integrity.hash ? '✅ Voimassa' : '❌ Ei voimassa'}
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="election-info">
                    <h4>🗳️ Vaalitiedot</h4>
                    <div class="election-details">
                        <strong>${election.name?.fi || 'Nimetön'}</strong><br>
                        <small>
                            Tyypi: ${this.getElectionTypeName(election.type)}<br>
                            Päivämäärä: ${this.formatDate(election.date)}<br>
                            Tila: <span class="election-status">${electionStatus}</span>
                        </small>
                    </div>
                </div>
            </div>
        `;
    }
    
    getElectionTypeName(type) {
        const types = {
            'municipal': 'Kunnallisvaalit',
            'parliamentary': 'Eduskuntavaalit',
            'european': 'Europarlamenttivaalit',
            'presidential': 'Presidentinvaalit',
            'test': 'Testivaalit'
        };
        return types[type] || type;
    }
    
    formatDateTime(dateString) {
        if (!dateString) return 'Ei saatavilla';
        const date = new Date(dateString);
        return date.toLocaleString('fi-FI');
    }
    
    formatDate(dateString) {
        if (!dateString) return 'Ei saatavilla';
        const date = new Date(dateString);
        return date.toLocaleDateString('fi-FI');
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    showError(message) {
        if (metaFormContainer) {
            metaFormContainer.innerHTML = `
                <div class="error-message">
                    ❌ ${message}
                    <br><button onclick="metaManager.loadMeta()" class="btn small">Yritä uudelleen</button>
                </div>
            `;
        }
    }
}

// IPFS Synkronointimanageri
class IPFSSyncManager {
    constructor() {
        this.syncInterval = null;
        this.isAutoSync = false;
    }
    
    // Manuaalinen synkronointi
    async manualSync() {
        try {
            console.log('🔄 Käynnistetään manuaalinen synkronointi...');
            const response = await fetch('/api/admin/sync', {
                method: 'POST'
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showSyncResult(result);
                this.startSyncMonitoring();
            } else {
                this.showSyncError(result.error || 'Synkronointi epäonnistui');
            }
            
        } catch (error) {
            console.error('❌ Synkronoinnin virhe:', error);
            this.showSyncError('Verkkovirhe synkronoinnissa: ' + error.message);
        }
    }
    
    // Aloita synkronoinnin seuranta
    startSyncMonitoring() {
        // Päivitä tila säännöllisesti
        this.syncInterval = setInterval(() => {
            this.updateSyncStatus();
        }, 2000);
        
        // Lopeta seuranta 30 sekunnin jälkeen
        setTimeout(() => {
            this.stopSyncMonitoring();
        }, 30000);
    }
    
    // Pysäytä synkronoinnin seuranta
    stopSyncMonitoring() {
        if (this.syncInterval) {
            clearInterval(this.syncInterval);
            this.syncInterval = null;
        }
    }
    
    // Päivitä synkronoinnin tila
    async updateSyncStatus() {
        try {
            const response = await fetch('/api/admin/sync_status');
            const status = await response.json();
            
            this.displaySyncStatus(status);
            
            // Jos synkronointi on valmis, lopeta seuranta
            if (status.status === 'completed' || status.status === 'error') {
                this.stopSyncMonitoring();
            }
            
        } catch (error) {
            console.error('❌ Virhe tilan päivityksessä:', error);
        }
    }
    
    // Näytä synkronoinnin tulos
    showSyncResult(status) {
        const syncResults = document.getElementById('sync-results');
        if (!syncResults) return;
        
        syncResults.innerHTML = `
            <div class="sync-result success">
                <h4>✅ Synkronointi aloitettu</h4>
                <div class="sync-progress">
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: 0%"></div>
                    </div>
                    <div class="progress-text">Alustetaan...</div>
                </div>
            </div>
        `;
    }
    
    // Näytä synkronoinnin virhe
    showSyncError(error) {
        const syncResults = document.getElementById('sync-results');
        if (!syncResults) return;
        
        syncResults.innerHTML = `
            <div class="sync-result error">
                <h4>❌ Synkronointi epäonnistui</h4>
                <p>${error}</p>
                <button onclick="ipfsSyncManager.manualSync()" class="btn small">Yritä uudelleen</button>
            </div>
        `;
    }
    
    // Näytä synkronoinnin tila
    displaySyncStatus(status) {
        const syncResults = document.getElementById('sync-results');
        if (!syncResults) return;
        
        let progress = 0;
        let statusText = '';
        
        switch (status.status) {
            case 'syncing':
                progress = 30;
                statusText = `Etsitään peeritä... (${status.peers_found || 0} löytyi)`;
                break;
            case 'completed':
                progress = 100;
                statusText = `Valmis! ${status.data_imported || 0} uutta dataa tuotu`;
                break;
            case 'error':
                progress = 0;
                statusText = `Virhe: ${status.error || 'Tuntematon virhe'}`;
                break;
            default:
                progress = 0;
                statusText = 'Odottamaan...';
        }
        
        syncResults.innerHTML = `
            <div class="sync-result ${status.status}">
                <h4>${this.getStatusIcon(status.status)} Synkronointi: ${this.getStatusText(status.status)}</h4>
                <div class="sync-progress">
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${progress}%"></div>
                    </div>
                    <div class="progress-text">${statusText}</div>
                </div>
                <div class="sync-details">
                    <div class="sync-stat">
                        <strong>Peeritä löytyi:</strong> ${status.peers_found || 0}
                    </div>
                    <div class="sync-stat">
                        <strong>Dataa tuotu:</strong> ${status.data_imported || 0}
                    </div>
                    <div class="sync-stat">
                        <strong>Viimeisin synkronointi:</strong> ${status.last_sync ? this.formatDateTime(status.last_sync) : 'Ei vielä'}
                    </div>
                </div>
            </div>
        `;
    }
    
    getStatusIcon(status) {
        const icons = {
            'syncing': '🔄',
            'completed': '✅',
            'error': '❌',
            'not_started': '⏸️'
        };
        return icons[status] || '❓';
    }
    
    getStatusText(status) {
        const texts = {
            'syncing': 'Käynnissä',
            'completed': 'Valmis',
            'error': 'Virhe',
            'not_started': 'Ei aloitettu'
        };
        return texts[status] || 'Tuntematon';
    }
    
    formatDateTime(dateString) {
        if (!dateString) return 'Ei saatavilla';
        const date = new Date(dateString);
        return date.toLocaleString('fi-FI');
    }
}

// Avainten hallinta
class KeyManager {
    constructor() {
        this.publicKey = localStorage.getItem('admin_public_key');
        this.privateKey = null;
        this.updateKeyDisplay();
    }
    
    // Generoi uusi avainpari
    async generateKeyPair() {
        try {
            console.log('🔑 Generoidaan uutta avainparia...');
            
            // Mock-toteutus - oikeassa järjestelmässä käytettäisiin Web Crypto API:a
            const keyPair = this.mockGenerateKeyPair();
            
            // Tallenna julkinen avain
            this.publicKey = keyPair.publicKey;
            localStorage.setItem('admin_public_key', this.publicKey);
            
            // Näytä yksityinen avain (vain tällä kertaa!)
            this.showPrivateKey(keyPair.privateKey);
            
            this.updateKeyDisplay();
            
            return keyPair;
            
        } catch (error) {
            console.error('❌ Virhe avainparin generoinnissa:', error);
            throw error;
        }
    }
    
    // Mock-avainparin generointi
    mockGenerateKeyPair() {
        const timestamp = Date.now();
        return {
            publicKey: `pub_${timestamp}_${Math.random().toString(36).substr(2, 9)}`,
            privateKey: `priv_${timestamp}_${Math.random().toString(36).substr(2, 9)}`,
            generatedAt: new Date().toISOString()
        };
    }
    
    // Näytä yksityinen avain (varoitus käyttäjälle)
    showPrivateKey(privateKey) {
        const keysResult = document.getElementById('keys-result');
        if (!keysResult) return;
        
        keysResult.innerHTML = `
            <div class="warning-message">
                <h4>⚠️ TALLENNA YKSITYINEN AVAIN TURVALLISESTI!</h4>
                <p>Yksityistä avainta ei voida palauttaa jos kadotat sen.</p>
                <div class="private-key-display">
                    <strong>Yksityinen avain:</strong>
                    <code>${privateKey}</code>
                </div>
                <div class="key-actions">
                    <button id="copy-private-key-btn" class="btn small warning">📋 Kopioi yksityinen avain</button>
                    <button id="download-private-key-btn" class="btn small">💾 Lataa tiedostona</button>
                </div>
            </div>
        `;
        
        // Kopioi yksityinen avain
        document.getElementById('copy-private-key-btn').addEventListener('click', () => {
            navigator.clipboard.writeText(privateKey).then(() => {
                alert('✅ Yksityinen avain kopioitu leikepöydälle!');
            }).catch(err => {
                console.error('❌ Kopiointi epäonnistui:', err);
                alert('❌ Kopiointi epäonnistui');
            });
        });
        
        // Lataa yksityinen avain tiedostona
        document.getElementById('download-private-key-btn').addEventListener('click', () => {
            this.downloadPrivateKey(privateKey);
        });
    }
    
    // Lataa yksityinen avain tiedostona
    downloadPrivateKey(privateKey) {
        const data = {
            privateKey: privateKey,
            generatedAt: new Date().toISOString(),
            system: 'Hajautettu Vaalikone',
            warning: 'SAVE THIS FILE SECURELY - PRIVATE KEY CANNOT BE RECOVERED'
        };
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `vaalikone_private_key_${Date.now()}.json`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    }
    
    updateKeyDisplay() {
        const keysDisplay = document.getElementById('keys-display');
        if (!keysDisplay) return;
        
        if (this.publicKey) {
            keysDisplay.innerHTML = `
                <div class="key-info">
                    <h4>🔑 Nykyinen julkinen avain</h4>
                    <code class="public-key">${this.publicKey}</code>
                    <p><small>Avain on tallennettu selaimen local storageen</small></p>
                </div>
            `;
        } else {
            keysDisplay.innerHTML = `
                <div class="no-keys">
                    <p>Ei avainta generoitu</p>
                    <button onclick="keyManager.generateKeyPair()" class="btn">🔑 Generoi uusi avainpari</button>
                </div>
            `;
        }
    }
}

// Alusta managerit
const metaManager = new MetaManager();
const ipfsSyncManager = new IPFSSyncManager();
const keyManager = new KeyManager();

// Välilehtien käsittely
function initTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabName = button.dataset.tab;
            
            // Poista aktiiviset luokat
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Aseta uusi aktiivinen välilehti
            button.classList.add('active');
            document.getElementById(`${tabName}-tab`).classList.add('active');
            
            // Lataa välilehden sisältö tarvittaessa
            if (tabName === 'meta') {
                metaManager.loadMeta();
            } else if (tabName === 'sync') {
                ipfsSyncManager.updateSyncStatus();
            }
        });
    });
}

// Lataa järjestelmän tila
async function loadSystemStatus() {
    try {
        const response = await fetch('/api/admin/status');
        state.systemStatus = await response.json();
        updateSystemStatusDisplay();
    } catch (error) {
        console.error('❌ Järjestelmätilan lataus epäonnistui:', error);
    }
}

// Päivitä järjestelmätilan näyttö
function updateSystemStatusDisplay() {
    if (!systemStatusEl) return;
    
    systemStatusEl.innerHTML = `
        <div class="status-grid">
            <div class="status-item">
                <span class="status-label">Tila:</span>
                <span class="status-value success">✅ Käynnissä</span>
            </div>
            <div class="status-item">
                <span class="status-label">Versio:</span>
                <span class="status-value">${state.systemStatus.version || '0.0.1'}</span>
            </div>
            <div class="status-item">
                <span class="status-label">Käyttäjiä:</span>
                <span class="status-value">${state.systemStatus.active_users || 0}</span>
            </div>
            <div class="status-item">
                <span class="status-label">Viimeisin varmuuskopio:</span>
                <span class="status-value">${formatDateTime(state.systemStatus.last_backup)}</span>
            </div>
        </div>
    `;
}

// Apufunktio päivämäärän muotoiluun
function formatDateTime(dateString) {
    if (!dateString) return 'Ei saatavilla';
    const date = new Date(dateString);
    return date.toLocaleString('fi-FI');
}

// Alustus
function init() {
    console.log('🚀 Alustetaan admin-sivu...');
    
    // Alusta välilehdet
    initTabs();
    
    // Lataa järjestelmän tila
    loadSystemStatus();
    
    // Lataa meta-tiedot
    metaManager.loadMeta();
    
    // Aseta tapahtumankäsittelijät painikkeille
    if (exportDataBtn) {
        exportDataBtn.addEventListener('click', exportData);
    }
    
    if (importDataBtn) {
        importDataBtn.addEventListener('click', importData);
    }
    
    if (clearCacheBtn) {
        clearCacheBtn.addEventListener('click', clearCache);
    }
    
    console.log('✅ Admin-sivu alustettu');
}

// Data vienti
async function exportData() {
    try {
        const response = await fetch('/api/admin/export_data');
        const data = await response.json();
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `vaalikone_export_${Date.now()}.json`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        
        alert('✅ Data vienti onnistui!');
    } catch (error) {
        console.error('❌ Data vienti epäonnistui:', error);
        alert('❌ Data vienti epäonnistui: ' + error.message);
    }
}

// Data tuonti
async function importData() {
    alert('⚠️ Data tuonti ominaisuus on vielä kehitteillä');
    // Toteutus puuttuu
}

// Välimuistin tyhjennys
async function clearCache() {
    try {
        const response = await fetch('/api/admin/clear_cache', {
            method: 'POST'
        });
        const result = await response.json();
        
        if (result.success) {
            alert('✅ Välimuisti tyhjennetty onnistuneesti!');
        } else {
            alert('❌ Välimuistin tyhjennys epäonnistui');
        }
    } catch (error) {
        console.error('❌ Välimuistin tyhjennys epäonnistui:', error);
        alert('❌ Välimuistin tyhjennys epäonnistui: ' + error.message);
    }
}

// Käynnistä sovellus
document.addEventListener('DOMContentLoaded', init);
