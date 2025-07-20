/**
 * Background particles animation for risk prediction dashboard
 */
document.addEventListener('DOMContentLoaded', function() {
    const container = document.querySelector('.particles-container');
    if (!container) return;
    
    // Create particles
    const particleCount = 30;
    const particleTypes = ['particle-1', 'particle-2', 'particle-3', 'particle-4', 'particle-5'];
    
    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.classList.add('particle');
        particle.classList.add(particleTypes[Math.floor(Math.random() * particleTypes.length)]);
        
        // Random position
        particle.style.left = `${Math.random() * 100}%`;
        particle.style.top = `${Math.random() * 100}%`;
        
        // Random animation delay
        particle.style.animationDelay = `${Math.random() * 10}s`;
        
        container.appendChild(particle);
    }
});