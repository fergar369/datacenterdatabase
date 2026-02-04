// DataCenter Intelligence Platform - Main JavaScript

// Global state
const AppState = {
    lastUpdate: null,
    isUpdating: false,
    eventSource: null
};

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    loadLastUpdate();
    setupEventListeners();
    setupRealtimeUpdates();
});

// Initialize application
function initializeApp() {
    console.log('DataCenter Intelligence Platform initialized');
}

// Setup event listeners
function setupEventListeners() {
    // Update button
    const updateButton = document.getElementById('updateButton');
    if (updateButton) {
        updateButton.addEventListener('click', triggerManualUpdate);
    }
}

// Load last update timestamp
function loadLastUpdate() {
    fetch('/api/statistics')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.statistics.last_update) {
                updateLastUpdateDisplay(data.statistics.last_update);
            } else {
                document.getElementById('lastUpdate').textContent = 'Never';
            }
        })
        .catch(error => {
            console.error('Error loading last update:', error);
            document.getElementById('lastUpdate').textContent = 'Error';
        });
}

// Update last update display
function updateLastUpdateDisplay(timestamp) {
    const lastUpdateElement = document.getElementById('lastUpdate');
    if (!lastUpdateElement) return;

    const date = new Date(timestamp);
    const now = new Date();
    const diffMinutes = Math.floor((now - date) / 60000);

    let displayText;
    if (diffMinutes < 1) {
        displayText = 'Just now';
    } else if (diffMinutes < 60) {
        displayText = `${diffMinutes} min ago`;
    } else if (diffMinutes < 1440) {
        const hours = Math.floor(diffMinutes / 60);
        displayText = `${hours} hour${hours > 1 ? 's' : ''} ago`;
    } else {
        displayText = date.toLocaleDateString();
    }

    lastUpdateElement.textContent = `Updated: ${displayText}`;
    lastUpdateElement.className = 'badge bg-success';
}

// Trigger manual update
function triggerManualUpdate() {
    if (AppState.isUpdating) {
        showToast('Update already in progress', 'warning');
        return;
    }

    AppState.isUpdating = true;
    const updateButton = document.getElementById('updateButton');
    const originalHTML = updateButton.innerHTML;

    updateButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Updating...';
    updateButton.disabled = true;

    fetch('/api/update')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast('Data updated successfully!', 'success');
                updateLastUpdateDisplay(data.timestamp);

                // Reload current page data
                if (typeof loadProjects === 'function') {
                    loadProjects();
                }
            } else {
                showToast(`Update failed: ${data.error}`, 'danger');
            }
        })
        .catch(error => {
            console.error('Error updating data:', error);
            showToast('Update failed. Please try again.', 'danger');
        })
        .finally(() => {
            AppState.isUpdating = false;
            updateButton.innerHTML = originalHTML;
            updateButton.disabled = false;
        });
}

// Setup real-time updates using Server-Sent Events
function setupRealtimeUpdates() {
    // Only setup if on dashboard or home page
    if (!window.location.pathname.match(/^\/(dashboard)?$/)) {
        return;
    }

    try {
        AppState.eventSource = new EventSource('/api/updates/stream');

        AppState.eventSource.onmessage = function(event) {
            try {
                const data = JSON.parse(event.data);

                if (data.type === 'new_projects' && data.count > 0) {
                    showNewProjectNotification(data.projects);
                } else if (data.type === 'heartbeat') {
                    console.log('Server heartbeat received');
                }
            } catch (error) {
                console.error('Error processing SSE message:', error);
            }
        };

        AppState.eventSource.onerror = function(error) {
            console.error('SSE connection error:', error);
            // Reconnect after 30 seconds
            setTimeout(() => {
                if (AppState.eventSource) {
                    AppState.eventSource.close();
                    setupRealtimeUpdates();
                }
            }, 30000);
        };

        console.log('Real-time updates enabled');
    } catch (error) {
        console.error('Error setting up real-time updates:', error);
    }
}

// Show notification for new projects
function showNewProjectNotification(projects) {
    const notificationBody = document.getElementById('notificationBody');
    const notificationToast = document.getElementById('notificationToast');

    if (!notificationBody || !notificationToast) return;

    let content = `<p class="mb-2"><strong>${projects.length} new verified project${projects.length > 1 ? 's' : ''} detected!</strong></p><ul class="mb-0">`;

    projects.slice(0, 3).forEach(project => {
        content += `<li>${project.project_name || 'Unnamed'} - ${project.capacity_mw} MW</li>`;
    });

    if (projects.length > 3) {
        content += `<li><em>...and ${projects.length - 3} more</em></li>`;
    }

    content += '</ul>';

    notificationBody.innerHTML = content;

    const toast = new bootstrap.Toast(notificationToast, {
        autohide: true,
        delay: 10000
    });
    toast.show();

    // Play notification sound (optional)
    playNotificationSound();
}

// Play notification sound
function playNotificationSound() {
    // Only play if user has interacted with the page (browser requirement)
    try {
        const audio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBSuA0fPTgjMGHm/A8OKZSAwcZ7fq56NQEQ1Lquv0vGwfBTaH1fXPfiwGK3vL8dmSQw0XXrTq6KRTEgxIp+L0wGwgBzaD1PbNfSsHKXnK89ySRQ4aX7Tq6KFTEg1Hp+P0v2shBzZ/1ffMfiwHJ3nK8dyRRhAaYLPr6KBSEQ1Dp+T1vGsfBTJ90fXOey0HI3nL8tuQRQ8bXrPr56FRDw1Cp+T1u2oeBzaB0/XNeSsGI3fI89uNRQ4bYLPq6J9RDw5Bp+T1u2keBzaB0vXNfCsGI3TH89qLRQ8bX7Ls6J5QDg5Bp+T1u2keBTN/0fTMfSsGI3TH89qLRQ8bX7Lr6J5QDw5Bp+T1vGkeBTJ+0fTMfSoGI3TH8tmMRg8aX7Lr6J5RDw5Bp+T2u2oeBTN/0fTMfSwGJHTH89mLRg8aX7Lr6J5RDw5Bp+T2u2oeBTN/0fTMfCsGJHTH89mMRg8aX7Lr6J5RDw5Bp+T2u2oeBTN/0fTMfCwGI3TH89mMRg8aX7Lr6J5RDw5Bp+T2u2oeBTN/0fTMfCwGI3TH89mMRg8aX7Lr6J5RDw5Bp+T2u2oeBTN/0fTMfCwGI3TH89mMRg8aX7Lr6J5RDw5Bp+T2u2oeBTN/0fTMfCwGI3TH89mMRg8aX7Lr6J5RDw5Bp+T2u2oeBTN/0fTMfCwGI3TH89mMRg8aX7Lr6J5RDw5Bp+T2u2oeBTN/0fTMfCwGI3TH89mMRg8aX7Lr6J5RDw5Bp+T2u2oeBTN/0fTMfCwGI3TH89mMRg==');
        audio.volume = 0.3;
        audio.play().catch(e => console.log('Could not play notification sound:', e));
    } catch (error) {
        // Silent fail
    }
}

// Show toast notification
function showToast(message, type = 'info') {
    const toastHTML = `
        <div class="toast align-items-center text-white bg-${type} border-0" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;

    // Create toast container if it doesn't exist
    let toastContainer = document.querySelector('.toast-container.position-fixed');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }

    // Add toast to container
    const toastElement = document.createElement('div');
    toastElement.innerHTML = toastHTML;
    toastContainer.appendChild(toastElement.firstElementChild);

    // Initialize and show toast
    const toast = new bootstrap.Toast(toastElement.firstElementChild);
    toast.show();

    // Remove from DOM after hidden
    toastElement.firstElementChild.addEventListener('hidden.bs.toast', function() {
        toastElement.remove();
    });
}

// Format number with commas
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

// Format currency
function formatCurrency(num) {
    return '$' + formatNumber(Math.round(num));
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Export to CSV
function exportToCSV() {
    window.location.href = '/api/export?format=csv';
}

// Export to JSON
function exportToJSON() {
    window.location.href = '/api/export?format=json';
}

// Export to GeoJSON
function exportToGeoJSON() {
    window.location.href = '/api/export?format=geojson';
}

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    if (AppState.eventSource) {
        AppState.eventSource.close();
    }
});

// Utility: Debounce function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Utility: Throttle function
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Error handler
window.addEventListener('error', function(event) {
    console.error('Application error:', event.error);
});

// Log application version
console.log('%cDataCenter Intelligence Platform v1.0', 'color: #007bff; font-size: 16px; font-weight: bold;');
console.log('%cVerified data from reputable sources', 'color: #6c757d; font-size: 12px;');
