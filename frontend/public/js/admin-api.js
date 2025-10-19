/**
 * Shared API helper functions for IntelliAttend Admin Panel
 */

// Check authentication on page load
function checkAdminAuth() {
    const adminToken = localStorage.getItem('admin_token');
    if (!adminToken) {
        window.location.href = '/admin?logout=success';
        return false;
    }
    return true;
}

// Get admin token
function getAdminToken() {
    return localStorage.getItem('admin_token');
}

// API request helper with proper error handling
function apiRequest(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${getAdminToken()}`
        }
    };
    
    const mergedOptions = {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...options.headers
        }
    };
    
    return fetch(url, mergedOptions)
        .then(response => {
            if (response.status === 401) {
                // Token expired or invalid
                localStorage.removeItem('admin_token');
                window.location.href = '/admin?logout=success';
                throw new Error('Unauthorized');
            }
            
            // Check if response is OK before trying to parse JSON
            if (!response.ok) {
                // Try to parse error response, fallback to generic message
                return response.json()
                    .then(errorData => {
                        throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
                    })
                    .catch(() => {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    });
            }
            
            return response.json();
        })
        .catch(error => {
            // If it's a network error or JSON parsing error
            if (error instanceof TypeError) {
                throw new Error('Network error. Please check your connection and try again.');
            }
            throw error;
        });
}

// Admin logout function
function adminLogout() {
    if (confirm('Are you sure you want to logout?')) {
        // Call logout API to invalidate token
        const adminToken = localStorage.getItem('admin_token');
        if (adminToken) {
            fetch('/api/admin/auth/logout', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${adminToken}`
                }
            })
            .then(() => {
                // Clear admin token and redirect to login page
                localStorage.removeItem('admin_token');
                window.location.href = '/admin?logout=success';
            })
            .catch(() => {
                // Even if logout fails, clear token and redirect
                localStorage.removeItem('admin_token');
                window.location.href = '/admin?logout=success';
            });
        } else {
            window.location.href = '/admin?logout=success';
        }
    }
}

// Show alert message
function showAdminAlert(type, message, containerId = 'alert-container') {
    const alertContainer = document.getElementById(containerId);
    if (alertContainer) {
        alertContainer.innerHTML = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'} me-2"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
    }
}

// Debounce function for search inputs
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