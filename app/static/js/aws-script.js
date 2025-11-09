// AWS Control Panel JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Add loading states to forms when submitted (not on button click)
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            // Find submit button in this form
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                // Save original content
                const originalHTML = submitBtn.innerHTML;
                // Show loading state
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Procesando...';
                submitBtn.disabled = true;
                
                // Re-enable after a timeout in case of errors (10 seconds)
                setTimeout(() => {
                    submitBtn.innerHTML = originalHTML;
                    submitBtn.disabled = false;
                }, 10000);
            }
            // Let the form submit naturally
        });
    });

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});