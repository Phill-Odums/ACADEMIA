// Main Interactive JavaScript for Academic Projects Marketplace

document.addEventListener('DOMContentLoaded', () => {
    // Lucide Icons initialization if loaded
    if (window.lucide) {
        window.lucide.createIcons();
    }

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-box');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(() => alert.remove(), 400);
        }, 5000);
    });

    // Interest capture AJAX submission
    const interestForm = document.getElementById('interest-form');
    if (interestForm) {
        interestForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const submitBtn = interestForm.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="animate-spin inline-block mr-2">⏳</span> Submitting...';

            const formData = new FormData(interestForm);
            const actionUrl = interestForm.getAttribute('action');

            try {
                const response = await fetch(actionUrl, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });
                const result = await response.json();

                if (response.ok && result.status === 'success') {
                    const modalContent = document.getElementById('interest-modal-content');
                    if (modalContent) {
                        modalContent.innerHTML = `
                            <div class="text-center py-6">
                                <div class="w-14 h-14 bg-emerald-50 text-emerald-600 rounded-full flex items-center justify-center mx-auto mb-4 text-xl font-bold">
                                    ✓
                                </div>
                                <h3 class="font-heading text-lg font-bold text-navy mb-2">Interest Logged</h3>
                                <p class="text-slate-600 text-sm mb-6">${result.message}</p>
                                <button onclick="closeInterestModal()" class="btn btn-primary">
                                    Close
                                </button>
                            </div>
                        `;
                    }
                } else {
                    alert(result.message || 'Unable to record interest. Please try again.');
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalText;
                }
            } catch (err) {
                alert('An error occurred. Please try again later.');
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            }
        });
    }
});

// Modal helpers
window.openInterestModal = function() {
    const modal = document.getElementById('interest-modal');
    if (modal) {
        modal.classList.remove('hidden');
        modal.classList.add('flex');
    }
};

window.closeInterestModal = function() {
    const modal = document.getElementById('interest-modal');
    if (modal) {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
    }
};

window.openRejectModal = function(projectId, projectTitle) {
    const modal = document.getElementById('reject-modal');
    const form = document.getElementById('reject-form');
    const titleElem = document.getElementById('reject-project-title');
    if (modal && form) {
        form.action = `/analytics/reject/${projectId}/`;
        if (titleElem) titleElem.textContent = projectTitle;
        modal.classList.remove('hidden');
        modal.classList.add('flex');
    }
};

window.closeRejectModal = function() {
    const modal = document.getElementById('reject-modal');
    if (modal) {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
    }
};
