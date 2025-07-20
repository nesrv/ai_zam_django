/**
 * 3D Logo Effects
 */
document.addEventListener('DOMContentLoaded', function() {
    const logo = document.querySelector('.logo');
    const logoContainer = document.querySelector('.logo-container');
    
    if (logo && logoContainer) {
        // Add 3D rotation effect on mouse move
        logoContainer.addEventListener('mousemove', function(e) {
            const rect = logoContainer.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            const rotateY = (x - centerX) / 20;
            const rotateX = (centerY - y) / 20;
            
            logo.style.transform = `rotateY(${rotateY}deg) rotateX(${rotateX}deg)`;
            
            // Update glow position
            const logoGlow = document.querySelector('.logo-glow');
            if (logoGlow) {
                logoGlow.style.background = `radial-gradient(circle at ${x}px ${y}px, rgba(0, 212, 255, 0.3), transparent 70%)`;
            }
        });
        
        // Reset transform on mouse leave
        logoContainer.addEventListener('mouseleave', function() {
            logo.style.transform = 'rotateY(0deg) rotateX(0deg)';
        });
    }
});