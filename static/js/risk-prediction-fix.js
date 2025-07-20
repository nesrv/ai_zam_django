/**
 * Simple fix for chart sizing issues
 */
document.addEventListener('DOMContentLoaded', function() {
    // Set Chart.js defaults to prevent overflow
    if (typeof Chart !== 'undefined') {
        Chart.defaults.maintainAspectRatio = false;
        Chart.defaults.responsive = true;
    }
    
    // Hide loader after page loads
    setTimeout(() => {
        const loader = document.getElementById('loader');
        if (loader) {
            loader.style.opacity = '0';
            setTimeout(() => {
                loader.style.display = 'none';
            }, 500);
        }
    }, 1500);
});