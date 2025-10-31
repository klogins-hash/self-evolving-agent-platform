// Enhanced JavaScript for Self-Evolving Agent Platform

// Auto-refresh functionality
let autoRefreshInterval;
let isAutoRefreshEnabled = true;

// Initialize enhanced features when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeEnhancements();
    setupAutoRefresh();
    setupKeyboardShortcuts();
    setupNotifications();
});

// Initialize all UI enhancements
function initializeEnhancements() {
    console.log('🚀 Initializing Self-Evolving Agent Platform enhancements...');
    
    // Add live indicators to status elements
    addLiveIndicators();
    
    // Setup smooth scrolling
    setupSmoothScrolling();
    
    // Initialize tooltips
    initializeTooltips();
    
    // Setup real-time clock
    setupRealTimeClock();
    
    console.log('✅ UI enhancements loaded successfully');
}

// Auto-refresh dashboard data
function setupAutoRefresh() {
    if (isAutoRefreshEnabled) {
        autoRefreshInterval = setInterval(() => {
            const dashboardElements = document.querySelectorAll('.live-indicator');
            if (dashboardElements.length > 0) {
                console.log('🔄 Auto-refreshing dashboard data...');
                // Trigger a subtle visual feedback
                dashboardElements.forEach(el => {
                    el.style.opacity = '0.5';
                    setTimeout(() => {
                        el.style.opacity = '1';
                    }, 200);
                });
            }
        }, 30000); // Refresh every 30 seconds
    }
}

// Add live indicators to status elements
function addLiveIndicators() {
    const statusElements = document.querySelectorAll('.agent-status-active, .status-badge.active');
    statusElements.forEach(el => {
        el.classList.add('live-indicator');
        
        // Add a small pulse dot
        const dot = document.createElement('span');
        dot.className = 'live-dot';
        dot.style.cssText = `
            display: inline-block;
            width: 8px;
            height: 8px;
            background: #10b981;
            border-radius: 50%;
            margin-left: 8px;
            animation: pulse 2s infinite;
        `;
        el.appendChild(dot);
    });
}

// Keyboard shortcuts
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + D for Dashboard
        if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
            e.preventDefault();
            triggerCommand('dashboard');
        }
        
        // Ctrl/Cmd + A for Agents
        if ((e.ctrlKey || e.metaKey) && e.key === 'a') {
            e.preventDefault();
            triggerCommand('agents');
        }
        
        // Ctrl/Cmd + T for Tasks
        if ((e.ctrlKey || e.metaKey) && e.key === 't') {
            e.preventDefault();
            triggerCommand('tasks');
        }
        
        // Ctrl/Cmd + N for New Agent
        if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
            e.preventDefault();
            triggerCommand('create agent');
        }
        
        // Escape to clear/help
        if (e.key === 'Escape') {
            triggerCommand('help');
        }
    });
    
    // Show keyboard shortcuts hint
    setTimeout(() => {
        showNotification('💡 Tip: Use Ctrl+D for Dashboard, Ctrl+A for Agents, Ctrl+T for Tasks', 'info', 5000);
    }, 2000);
}

// Trigger a command (simulate user input)
function triggerCommand(command) {
    const messageInput = document.querySelector('input[placeholder*="message"], textarea[placeholder*="message"]');
    if (messageInput) {
        messageInput.value = command;
        messageInput.focus();
        
        // Trigger enter key
        const enterEvent = new KeyboardEvent('keydown', {
            key: 'Enter',
            code: 'Enter',
            keyCode: 13,
            bubbles: true
        });
        messageInput.dispatchEvent(enterEvent);
    }
}

// Setup smooth scrolling
function setupSmoothScrolling() {
    document.documentElement.style.scrollBehavior = 'smooth';
}

// Initialize tooltips for enhanced UX
function initializeTooltips() {
    const elementsWithTooltips = document.querySelectorAll('[title]');
    elementsWithTooltips.forEach(el => {
        el.addEventListener('mouseenter', showTooltip);
        el.addEventListener('mouseleave', hideTooltip);
    });
}

// Show custom tooltip
function showTooltip(e) {
    const tooltip = document.createElement('div');
    tooltip.className = 'custom-tooltip';
    tooltip.textContent = e.target.getAttribute('title');
    tooltip.style.cssText = `
        position: absolute;
        background: #1f2937;
        color: white;
        padding: 8px 12px;
        border-radius: 6px;
        font-size: 14px;
        z-index: 1000;
        pointer-events: none;
        opacity: 0;
        transition: opacity 0.3s ease;
    `;
    
    document.body.appendChild(tooltip);
    
    // Position tooltip
    const rect = e.target.getBoundingClientRect();
    tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
    tooltip.style.top = rect.top - tooltip.offsetHeight - 8 + 'px';
    
    // Show with animation
    setTimeout(() => {
        tooltip.style.opacity = '1';
    }, 10);
    
    // Store reference for cleanup
    e.target._tooltip = tooltip;
}

// Hide custom tooltip
function hideTooltip(e) {
    if (e.target._tooltip) {
        e.target._tooltip.remove();
        delete e.target._tooltip;
    }
}

// Real-time clock in header
function setupRealTimeClock() {
    const clockElement = document.createElement('div');
    clockElement.id = 'real-time-clock';
    clockElement.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: rgba(255, 255, 255, 0.9);
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 14px;
        font-weight: 600;
        color: #374151;
        backdrop-filter: blur(10px);
        z-index: 999;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    `;
    
    document.body.appendChild(clockElement);
    
    function updateClock() {
        const now = new Date();
        clockElement.textContent = now.toLocaleTimeString();
    }
    
    updateClock();
    setInterval(updateClock, 1000);
}

// Enhanced notification system
function setupNotifications() {
    window.showNotification = function(message, type = 'info', duration = 3000) {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        // Auto-remove after duration
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, duration);
    };
}

// Performance monitoring
function monitorPerformance() {
    // Monitor page load time
    window.addEventListener('load', () => {
        const loadTime = performance.now();
        console.log(`📊 Page loaded in ${loadTime.toFixed(2)}ms`);
        
        if (loadTime > 3000) {
            showNotification('⚠️ Slow loading detected. Check your connection.', 'warning');
        }
    });
    
    // Monitor memory usage (if available)
    if ('memory' in performance) {
        setInterval(() => {
            const memory = performance.memory;
            const usedMB = Math.round(memory.usedJSHeapSize / 1048576);
            
            if (usedMB > 100) {
                console.warn(`⚠️ High memory usage: ${usedMB}MB`);
            }
        }, 60000); // Check every minute
    }
}

// Enhanced form validation
function setupFormValidation() {
    document.addEventListener('input', function(e) {
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
            validateField(e.target);
        }
    });
}

function validateField(field) {
    const value = field.value.trim();
    let isValid = true;
    let message = '';
    
    // Basic validation rules
    if (field.required && !value) {
        isValid = false;
        message = 'This field is required';
    } else if (field.type === 'email' && value && !isValidEmail(value)) {
        isValid = false;
        message = 'Please enter a valid email address';
    } else if (field.minLength && value.length < field.minLength) {
        isValid = false;
        message = `Minimum ${field.minLength} characters required`;
    }
    
    // Update field styling
    field.style.borderColor = isValid ? '#10b981' : '#ef4444';
    
    // Show/hide validation message
    let errorElement = field.parentNode.querySelector('.validation-error');
    if (!isValid && message) {
        if (!errorElement) {
            errorElement = document.createElement('div');
            errorElement.className = 'validation-error';
            errorElement.style.cssText = 'color: #ef4444; font-size: 12px; margin-top: 4px;';
            field.parentNode.appendChild(errorElement);
        }
        errorElement.textContent = message;
    } else if (errorElement) {
        errorElement.remove();
    }
    
    return isValid;
}

function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

// Data export functionality
function setupDataExport() {
    window.exportData = function(data, filename, format = 'json') {
        let content, mimeType;
        
        if (format === 'json') {
            content = JSON.stringify(data, null, 2);
            mimeType = 'application/json';
        } else if (format === 'csv') {
            content = convertToCSV(data);
            mimeType = 'text/csv';
        }
        
        const blob = new Blob([content], { type: mimeType });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `${filename}.${format}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        showNotification(`📥 Data exported as ${filename}.${format}`, 'success');
    };
}

function convertToCSV(data) {
    if (!Array.isArray(data) || data.length === 0) return '';
    
    const headers = Object.keys(data[0]);
    const csvRows = [headers.join(',')];
    
    for (const row of data) {
        const values = headers.map(header => {
            const value = row[header];
            return typeof value === 'string' ? `"${value.replace(/"/g, '""')}"` : value;
        });
        csvRows.push(values.join(','));
    }
    
    return csvRows.join('\n');
}

// Theme switching
function setupThemeToggle() {
    const themeToggle = document.createElement('button');
    themeToggle.innerHTML = '🌙';
    themeToggle.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        border: none;
        background: #2563eb;
        color: white;
        font-size: 20px;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        z-index: 1000;
        transition: all 0.3s ease;
    `;
    
    themeToggle.addEventListener('click', toggleTheme);
    document.body.appendChild(themeToggle);
}

function toggleTheme() {
    const isDark = document.body.classList.toggle('dark-theme');
    const themeToggle = document.querySelector('button[style*="bottom: 20px"]');
    
    if (themeToggle) {
        themeToggle.innerHTML = isDark ? '☀️' : '🌙';
    }
    
    // Save preference
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
    
    showNotification(`🎨 Switched to ${isDark ? 'dark' : 'light'} theme`, 'info');
}

// Initialize all enhancements
document.addEventListener('DOMContentLoaded', function() {
    initializeEnhancements();
    monitorPerformance();
    setupFormValidation();
    setupDataExport();
    setupThemeToggle();
    
    // Load saved theme
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-theme');
    }
});

// Add CSS animations for slideOut
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    .dark-theme {
        filter: invert(1) hue-rotate(180deg);
    }
    
    .dark-theme img,
    .dark-theme video,
    .dark-theme canvas,
    .dark-theme svg {
        filter: invert(1) hue-rotate(180deg);
    }
`;
document.head.appendChild(style);

console.log('🎉 Self-Evolving Agent Platform UI enhancements fully loaded!');
