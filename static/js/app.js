// Genel JavaScript işlevleri

// DOM yüklendiğinde çalışacak fonksiyonlar
document.addEventListener('DOMContentLoaded', function() {
    // Flash mesajları otomatik kapatma
    setTimeout(() => {
        document.querySelectorAll('.flash').forEach(flash => {
            flash.style.animation = 'slideOut 0.3s ease forwards';
            setTimeout(() => flash.remove(), 300);
        });
    }, 5000);
    
    // Modal ESC ile kapatma
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeAllModals();
        }
    });
    
    // Form validasyonları
    setupFormValidations();
    
    // Tooltip'leri başlat (eğer varsa)
    initTooltips();
});

// Modal işlevleri
function closeAllModals() {
    document.querySelectorAll('.modal.active').forEach(modal => {
        modal.classList.remove('active');
    });
    document.querySelectorAll('.modal-backdrop.active').forEach(backdrop => {
        backdrop.classList.remove('active');
    });
    document.body.style.overflow = 'auto';
}

// Form validasyonları
function setupFormValidations() {
    // Sayısal inputlar için negatif değer kontrolü
    document.querySelectorAll('input[type="number"]').forEach(input => {
        input.addEventListener('input', function() {
            if (this.value < 0) {
                this.value = 0;
            }
        });
    });
    
    // Fiyat inputları için ondalık kontrol
    document.querySelectorAll('input[step="0.01"]').forEach(input => {
        input.addEventListener('blur', function() {
            if (this.value && !isNaN(this.value)) {
                this.value = parseFloat(this.value).toFixed(2);
            }
        });
    });
    
    // Form submit öncesi boş alan kontrolü
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = this.querySelectorAll('[required]');
            let hasEmptyField = false;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    hasEmptyField = true;
                    field.style.borderColor = '#ef4444';
                    field.addEventListener('input', function() {
                        this.style.borderColor = '#e2e8f0';
                    }, { once: true });
                }
            });
            
            if (hasEmptyField) {
                e.preventDefault();
                showToast('Lütfen tüm gerekli alanları doldurun', 'error');
            }
        });
    });
}

// Toast bildirim sistemi
function showToast(message, type = 'info', duration = 3000) {
    // Mevcut toast'ları temizle
    document.querySelectorAll('.toast').forEach(toast => toast.remove());
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    const icon = type === 'success' ? 'check-circle' : 
                 type === 'error' ? 'exclamation-circle' : 
                 type === 'warning' ? 'exclamation-triangle' : 'info-circle';
    
    toast.innerHTML = `
        <i class="fas fa-${icon}"></i>
        <span>${message}</span>
    `;
    
    document.body.appendChild(toast);
    
    // Animasyon için timeout
    setTimeout(() => toast.classList.add('show'), 100);
    
    // Otomatik kaldırma
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, duration);
    
    // Click ile kaldırma
    toast.addEventListener('click', () => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    });
}

// Tooltip sistemi (opsiyonel)
function initTooltips() {
    document.querySelectorAll('[data-tooltip]').forEach(element => {
        element.addEventListener('mouseenter', function() {
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = this.dataset.tooltip;
            document.body.appendChild(tooltip);
            
            const rect = this.getBoundingClientRect();
            tooltip.style.position = 'absolute';
            tooltip.style.top = (rect.top - tooltip.offsetHeight - 5) + 'px';
            tooltip.style.left = (rect.left + (rect.width - tooltip.offsetWidth) / 2) + 'px';
            tooltip.style.zIndex = '9999';
            tooltip.style.background = '#1e293b';
            tooltip.style.color = 'white';
            tooltip.style.padding = '5px 10px';
            tooltip.style.borderRadius = '4px';
            tooltip.style.fontSize = '0.8rem';
            tooltip.style.whiteSpace = 'nowrap';
            
            this._tooltip = tooltip;
        });
        
        element.addEventListener('mouseleave', function() {
            if (this._tooltip) {
                this._tooltip.remove();
                this._tooltip = null;
            }
        });
    });
}

// Onay dialogları
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Loading state göstergesi
function showLoading(element) {
    const originalContent = element.innerHTML;
    element.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Yükleniyor...';
    element.disabled = true;
    
    return () => {
        element.innerHTML = originalContent;
        element.disabled = false;
    };
}

// AJAX işlemleri için yardımcı fonksiyon
async function makeRequest(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return { success: true, data };
    } catch (error) {
        console.error('Request failed:', error);
        return { success: false, error: error.message };
    }
}

// Sayfa yenileme ohne reload
function refreshPage() {
    window.location.reload();
}

// Local Storage işlemleri
const Storage = {
    set: (key, value) => {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (e) {
            console.error('LocalStorage set error:', e);
        }
    },
    
    get: (key, defaultValue = null) => {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (e) {
            console.error('LocalStorage get error:', e);
            return defaultValue;
        }
    },
    
    remove: (key) => {
        try {
            localStorage.removeItem(key);
        } catch (e) {
            console.error('LocalStorage remove error:', e);
        }
    }
};

// Anlık zaman gösterimi
function updateClock() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('tr-TR');
    const dateString = now.toLocaleDateString('tr-TR');
    
    document.querySelectorAll('.current-time').forEach(element => {
        element.textContent = timeString;
    });
    
    document.querySelectorAll('.current-date').forEach(element => {
        element.textContent = dateString;
    });
}

// Saat güncellemeyi başlat
setInterval(updateClock, 1000);
updateClock(); // İlk yükleme

// Sayfa görünürlük API'si ile performans optimizasyonu
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        // Sayfa gizlendiğinde ağır işlemleri durdur
        clearInterval(window.clockInterval);
    } else {
        // Sayfa görünür olduğunda işlemleri başlat
        window.clockInterval = setInterval(updateClock, 1000);
    }
});

// Print işlevi (raporlar için)
function printPage() {
    window.print();
}

// Export işlevleri
window.CafeApp = {
    showToast,
    confirmAction,
    showLoading,
    makeRequest,
    refreshPage,
    Storage,
    printPage
};