// Form validation and interaction scripts

// Swap form validation - prevent selecting same person
function initSwapFormValidation() {
    const requesterSelect = document.querySelector('select[name="requester"]');
    const targetSelect = document.querySelector('select[name="target"]');
    
    if (!requesterSelect || !targetSelect) return;
    
    requesterSelect.addEventListener('change', function() {
        const selectedValue = this.value;
        
        if (targetSelect.value === selectedValue) {
            targetSelect.value = '';
        }
        
        Array.from(targetSelect.options).forEach(option => {
            option.disabled = option.value === selectedValue && option.value !== '';
        });
    });
    
    targetSelect.addEventListener('change', function() {
        const selectedValue = this.value;
        
        if (requesterSelect.value === selectedValue) {
            requesterSelect.value = '';
        }
        
        Array.from(requesterSelect.options).forEach(option => {
            option.disabled = option.value === selectedValue && option.value !== '';
        });
    });
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initSwapFormValidation();
});