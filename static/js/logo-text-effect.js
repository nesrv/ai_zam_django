/**
 * Special text effect for the logo
 */
document.addEventListener('DOMContentLoaded', function() {
    const logoText = document.querySelector('.logo-text');
    
    if (logoText) {
        // Create letter-by-letter animation
        const text = logoText.textContent;
        logoText.textContent = '';
        
        // Create wrapper for the animated text
        const wrapper = document.createElement('span');
        wrapper.className = 'logo-text-wrapper';
        logoText.appendChild(wrapper);
        
        // Add each letter with a delay
        for (let i = 0; i < text.length; i++) {
            const letter = document.createElement('span');
            letter.className = 'logo-letter';
            letter.textContent = text[i];
            letter.style.animationDelay = `${i * 0.1}s`;
            wrapper.appendChild(letter);
        }
        
        // Add data-text attribute for shadow effect
        logoText.setAttribute('data-text', text);
    }
});