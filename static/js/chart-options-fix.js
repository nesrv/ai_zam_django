/**
 * Global Chart.js options fix
 */
document.addEventListener('DOMContentLoaded', function() {
    if (typeof Chart !== 'undefined') {
        // Set global defaults
        Chart.defaults.maintainAspectRatio = false;
        Chart.defaults.responsive = true;
        
        // Add resize event listener
        window.addEventListener('resize', function() {
            for (let id in Chart.instances) {
                Chart.instances[id].resize();
            }
        });
    }
});