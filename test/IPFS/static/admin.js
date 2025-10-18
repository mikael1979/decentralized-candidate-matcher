// Ylläpidon tila
const state = {
    systemStatus: {},
    moderationQueue: [],
    ipfsStatus: {}
};

// DOM-elementit
const systemStatusEl = document.getElementById('system-status');
const moderationQueueEl = document.getElementById('moderation-queue');
const ipfsStatusEl = document.getElementById('ipfs-status');
const adminStatsEl = document.getElementById('admin-stats');
const exportDataBtn = document.getElementById('export-data-btn');
const importDataBtn = document.getElementById('import-data-btn');
const clearCacheBtn = document.getElementById('clear-cache-btn');

// IPFS Synkronointimanageri
class IPFSSyncManager {
    constructor() {
        this.syncInterval = null;
        this.isAutoSync = false;
    }
    
    // Manuaalinen synkronointi
    async manualSync() {
        try {
            const response = await fetch('/api/admin/sync', {
                method: 'POST'
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showSyncResult(result.status);
                this.startSyncMonitoring();
            } else {
                this.showSyncError(result.error);
            }
            
        } catch (error) {
            console.error('Synkronoinnin virhe:', error);
            this.showSyncError('Verkkovirhe synkronoinnissa');
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
            console.error('Virhe tilan päivityksessä:', error);
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
                    <div class="progress-text">Etsitään peeritä...</div>
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
                statusText = `Etsitään peeritä... (${status.peers_found} löytyi)`;
                break;
            case 'completed':
                progress = 100;
                statusText = `Valmis! ${status.data_imported} uutta dataa tuotu`;
                break;
            case 'error':
                progress = 0;
                statusText = `Virhe: ${status.error}`;
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
                        <strong>Peeritä löytyi:</strong> ${status.peers_found}
                    </div>
                    <div class="sync-stat">
                        <strong>Dataa tuotu:</strong> ${status.data_imported}
                    </div>
                    <div class="sync-stat">
                        <strong>Viimeisin synkronointi:</strong> ${status.last_sync ? new Date(status.last_sync).toLocaleString('fi-FI') : 'Ei vielä'}
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
    
    // Hae peerit
    async loadPeers() {
        try {
            const response = await fetch('/api/admin/peers');
            const peers = await response.json();
            
            this.displayPeers(peers);
            
        } catch (error) {
            console.error('Virhe peerien latauksessa:', error);
        }
    }
    
    // Näytä peerit
    displayPeers(peers) {
        const peersContainer = document.getElementById('peers-container');
        if (!peersContainer) return;
        
        if (peers.length === 0) {
            peersContainer.innerHTML = '<div class="no-data">Ei peeritä saatavilla</div>';
            return;
        }
        
        peersContainer.innerHTML = `
            <h4>Löydetyt peerit (${peers.length})</h4>
            <div class="peers-list">
                ${peers.map(peer => `
                    <div class="peer-item">
                        <div class="peer-id">${peer.id}</div>
                        <div class="peer-info">
                            <span class="data-type">${peer.data_type}</span>
                            <span class="last-updated">${new Date(peer.last_updated).toLocaleString('fi-FI')}</span>
                        </div>
                        <div class="peer-actions">
                            <button class="btn small" onclick="syncManager.syncWithPeer('${peer.id}')">
                                Synkronoi
                            </button>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    // Synkronoi tietyn peerin kanssa
    async syncWithPeer(peerId) {
        // Toteutus yksittäisen peerin synkronointiin
        console.log(`Synkronoidaan peerin ${peerId} kanssa`);
        alert(`Synkronoidaan peerin ${peerId} kanssa - tämä on vielä kehitteillä`);
    }
    
    // Ota automaattinen synkronointi käyttöön
    async enableAutoSync() {
        try {
            const response = await fetch('/api/admin/enable_auto_sync', {
                method: 'POST'
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.isAutoSync = true;
                this.updateAutoSyncButton();
                alert('Automaattinen synkronointi otettu käyttöön');
            } else {
                alert('Automaattisen synkronoinnin käyttöönotto epäonnistui');
            }
            
        } catch (error) {
            console.error('Virhe automaattisen synkronoinnin käyttöönotossa:', error);
            alert('Verkkovirhe automaattisen synkronoinnin käyttöönotossa');
        }
    }
    
    // Poista automaattinen synkronointi käytöstä
    async disableAutoSync() {
        try {
            const response = await fetch('/api/admin/disable_auto_sync', {
                method: 'POST'
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.isAutoSync = false;
                this.updateAutoSyncButton();
                alert('Automaattinen synkronointi poistettu käytöstä');
            } else {
                alert('Automaattisen synkronoinnin poisto käytöstä epäonnistui');
            }
            
        } catch (error) {
            console.error('Virhe automaattisen synkronoinnin poistossa:', error);
            alert('Verkkovirhe automaattisen synkronoinnin poistossa');
        }
    }
    
    // Päivitä automaattisen synkronoinnin painike
    updateAutoSyncButton() {
        const autoSyncBtn = document.getElementById('auto-sync-btn');
        if (!autoSyncBtn) return;
        
        if (this.isAutoSync) {
            autoSyncBtn.textContent = 'Poista automaattinen synkronointi käytöstä';
            autoSyncBtn.classList.remove('secondary');
            autoSyncBtn.classList.add('warning');
        } else {
            autoSyncBtn.textContent = 'Ota automaattinen synkronointi käyttöön';
            autoSyncBtn.classList.remove('warning');
            autoSyncBtn.classList.add('secondary');
        }
    }
}

// Alusta synkronointimanageri
const syncManager = new IPFSSyncManager();

// Lataa järjestelmän tila
async function loadSystemStatus() {
    try {
        const response = await fetch('/api/admin/status');
        const data = await response.json();
        state.systemStatus = data;
        
        displaySystemStatus(data);
        
    } catch (error) {
        console.error('Virhe tilan lataamisessa:', error);
        systemStatusEl.innerHTML = '<div class="error">Tilan lataus epäonnistui</div>';
    }
}

// Näytä järjestelmän tila
function displaySystemStatus(status) {
    systemStatusEl.innerHTML = `
        <div class="status-grid">
            <div class="status-item">
                <span class="status-label">Käynnissä:</span>
                <span class="status-value ${status.is_running ? 'success' : 'error'}">
                    ${status.is_running ? '✅ Kyllä' : '❌ Ei'}
                </span>
            </div>
            <div class="status-item">
                <span class="status-label">Käyttäjiä online:</span>
                <span class="status-value">${status.active_users || 0}</span>
            </div>
            <div class="status-item">
                <span class="status-label">Viimeisin varmuus:</span>
                <span class="status-value">${status.last_backup || 'Ei saatavilla'}</span>
            </div>
            <div class="status-item">
                <span class="status-label">Versio:</span>
                <span class="status-value">${status.version || '1.0.0'}</span>
            </div>
        </div>
    `;
}

// Lataa moderointijono
async function loadModerationQueue() {
    try {
        const response = await fetch('/api/admin/moderation_queue');
        const queue = await response.json();
        state.moderationQueue = queue;
        
        displayModerationQueue(queue);
        
    } catch (error) {
        console.error('Virhe moderointijonon lataamisessa:', error);
        moderationQueueEl.innerHTML = '<div class="error">Moderointijonon lataus epäonnistui</div>';
    }
}

// Näytä moderointijono
function displayModerationQueue(queue) {
    if (queue.length === 0) {
        moderationQueueEl.innerHTML = '<div class="no-data">Ei kysymyksiä odottamassa moderointia</div>';
        return;
    }
    
    moderationQueueEl.innerHTML = queue.map(question => `
        <div class="moderation-item">
            <div class="question-text">${question.question?.fi || question.question}</div>
            <div class="question-meta">
                Lähettäjä: ${question.submitter || 'Tuntematon'} | 
                Aika: ${new Date(question.timestamp).toLocaleDateString('fi-FI')}
            </div>
            <div class="moderation-actions">
                <button class="btn small" onclick="approveQuestion(${question.id})">
                    Hyväksy
                </button>
                <button class="btn small warning" onclick="rejectQuestion(${question.id})">
                    Hylkää
                </button>
            </div>
        </div>
    `).join('');
}

// Hyväksy kysymys
async function approveQuestion(questionId) {
    try {
        const response = await fetch(`/api/admin/approve_question/${questionId}`, {
            method: 'POST'
        });
        
        if (response.ok) {
            loadModerationQueue(); // Päivitä jono
            loadAdminStats(); // Päivitä tilastot
        } else {
            alert('Kysymyksen hyväksyminen epäonnistui');
        }
    } catch (error) {
        console.error('Virhe hyväksynnässä:', error);
        alert('Virhe hyväksynnässä');
    }
}

// Hylkää kysymys
async function rejectQuestion(questionId) {
    try {
        const response = await fetch(`/api/admin/reject_question/${questionId}`, {
            method: 'POST'
        });
        
        if (response.ok) {
            loadModerationQueue(); // Päivitä jono
            loadAdminStats(); // Päivitä tilastot
        } else {
            alert('Kysymyksen hylkääminen epäonnistui');
        }
    } catch (error) {
        console.error('Virhe hylkäyksessä:', error);
        alert('Virhe hylkäyksessä');
    }
}

// Lataa IPFS-tila
async function loadIPFSStatus() {
    try {
        const response = await fetch('/api/admin/ipfs_status');
        const status = await response.json();
        state.ipfsStatus = status;
        
        displayIPFSStatus(status);
        
    } catch (error) {
        console.error('Virhe IPFS-tilan lataamisessa:', error);
        ipfsStatusEl.innerHTML = '<div class="error">IPFS-tilan lataus epäonnistui</div>';
    }
}

// Näytä IPFS-tila
function displayIPFSStatus(status) {
    ipfsStatusEl.innerHTML = `
        <div class="status-grid">
            <div class="status-item">
                <span class="status-label">Yhdistetty:</span>
                <span class="status-value ${status.connected ? 'success' : 'error'}">
                    ${status.connected ? '✅ Kyllä' : '❌ Ei'}
                </span>
            </div>
            <div class="status-item">
                <span class="status-label">Peerejä:</span>
                <span class="status-value">${status.peer_count || 0}</span>
            </div>
            <div class="status-item">
                <span class="status-label">Tallennustila:</span>
                <span class="status-value">${status.storage_used || '0'} / ${status.storage_max || '0'}</span>
            </div>
            <div class="status-item">
                <span class="status-label">Pinnattuja tiedostoja:</span>
                <span class="status-value">${status.pinned_count || 0}</span>
            </div>
        </div>
    `;
}

// Lataa ylläpidon tilastot
async function loadAdminStats() {
    try {
        const response = await fetch('/api/admin/stats');
        const stats = await response.json();
        
        displayAdminStats(stats);
        
    } catch (error) {
        console.error('Virhe tilastojen lataamisessa:', error);
        adminStatsEl.innerHTML = '<div class="error">Tilastojen lataus epäonnistui</div>';
    }
}

// Näytä ylläpidon tilastot
function displayAdminStats(stats) {
    adminStatsEl.innerHTML = `
        <div class="stats-grid">
            <div class="stat-card">
                <h4>Käyttäjät</h4>
                <div class="stat-number">${stats.total_users || 0}</div>
                <div class="stat-label">Rekisteröitynyttä</div>
            </div>
            <div class="stat-card">
                <h4>Kysymykset</h4>
                <div class="stat-number">${stats.total_questions || 0}</div>
                <div class="stat-label">Käsitelty</div>
            </div>
            <div class="stat-card">
                <h4>Ehdokkaat</h4>
                <div class="stat-number">${stats.total_candidates || 0}</div>
                <div class="stat-label">Rekisteröitynyttä</div>
            </div>
            <div class="stat-card">
                <h4>Puolueet</h4>
                <div class="stat-number">${stats.total_parties || 0}</div>
                <div class="stat-label">Aktiivista</div>
            </div>
        </div>
    `;
}

// Vie data
exportDataBtn.addEventListener('click', async () => {
    try {
        const response = await fetch('/api/admin/export_data');
        const blob = await response.blob();
        
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `vaalikone-data-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        
    } catch (error) {
        console.error('Virhe datan viennissä:', error);
        alert('Datan vienti epäonnistui');
    }
});

// Tuo data
importDataBtn.addEventListener('click', () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    
    input.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;
        
        try {
            const formData = new FormData();
            formData.append('file', file);
            
            const response = await fetch('/api/admin/import_data', {
                method: 'POST',
                body: formData
            });
            
            if (response.ok) {
                alert('Data tuotu onnistuneesti!');
                location.reload(); // Päivitä sivu
            } else {
                alert('Datan tuonti epäonnistui');
            }
        } catch (error) {
            console.error('Virhe datan tuonnissa:', error);
            alert('Datan tuonti epäonnistui');
        }
    });
    
    input.click();
});

// Tyhjennä välimuisti
clearCacheBtn.addEventListener('click', async () => {
    if (!confirm('Haluatko varmasti tyhjentää välimuistin? Tämä voi hidastaa sovellusta väliaikaisesti.')) {
        return;
    }
    
    try {
        const response = await fetch('/api/admin/clear_cache', {
            method: 'POST'
        });
        
        if (response.ok) {
            alert('Välimuisti tyhjennetty onnistuneesti!');
        } else {
            alert('Välimuistin tyhjennys epäonnistui');
        }
    } catch (error) {
        console.error('Virhe välimuistin tyhjennyksessä:', error);
        alert('Välimuistin tyhjennys epäonnistui');
    }
});

// Lisää synkronointiosio admin-sivulle
function addSyncSection() {
    const adminGrid = document.querySelector('.admin-grid');
    if (!adminGrid) return;
    
    const syncSection = document.createElement('div');
    syncSection.className = 'admin-card';
    syncSection.innerHTML = `
        <h3>IPFS Synkronointi</h3>
        <div class="sync-controls">
            <button id="manual-sync-btn" class="btn">Manuaalinen synkronointi</button>
            <button id="auto-sync-btn" class="btn secondary">Ota automaattinen synkronointi käyttöön</button>
            <button id="view-peers-btn" class="btn secondary">Näytä peerit</button>
        </div>
        <div id="sync-results" class="sync-results">
            <div class="no-data">Synkronointia ei ole suoritettu</div>
        </div>
        <div id="peers-container" class="peers-container" style="display: none;"></div>
    `;
    
    adminGrid.appendChild(syncSection);
    
    // Aseta tapahtumankäsittelijät
    document.getElementById('manual-sync-btn').addEventListener('click', () => {
        syncManager.manualSync();
    });
    
    document.getElementById('auto-sync-btn').addEventListener('click', () => {
        if (syncManager.isAutoSync) {
            syncManager.disableAutoSync();
        } else {
            syncManager.enableAutoSync();
        }
    });
    
    document.getElementById('view-peers-btn').addEventListener('click', () => {
        const peersContainer = document.getElementById('peers-container');
        if (peersContainer.style.display === 'none') {
            peersContainer.style.display = 'block';
            syncManager.loadPeers();
        } else {
            peersContainer.style.display = 'none';
        }
    });
}

// Alustus
function init() {
    loadSystemStatus();
    loadModerationQueue();
    loadIPFSStatus();
    loadAdminStats();
    
    // Lisää synkronointiosio
    addSyncSection();
    
    // Päivitä tilat säännöllisesti
    setInterval(() => {
        loadSystemStatus();
        loadIPFSStatus();
    }, 30000);
}

document.addEventListener('DOMContentLoaded', init);
