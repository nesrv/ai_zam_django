// Analytics Home Page Animations

function initParticles() {
    particlesJS('particles-js', {
        particles: {
            number: {
                value: 80,
                density: {
                    enable: true,
                    value_area: 800
                }
            },
            color: {
                value: '#00d4ff'
            },
            shape: {
                type: 'circle',
                stroke: {
                    width: 0,
                    color: '#000000'
                },
                polygon: {
                    nb_sides: 5
                }
            },
            opacity: {
                value: 0.5,
                random: true,
                anim: {
                    enable: true,
                    speed: 1,
                    opacity_min: 0.1,
                    sync: false
                }
            },
            size: {
                value: 3,
                random: true,
                anim: {
                    enable: true,
                    speed: 2,
                    size_min: 0.1,
                    sync: false
                }
            },
            line_linked: {
                enable: true,
                distance: 150,
                color: '#00d4ff',
                opacity: 0.2,
                width: 1
            },
            move: {
                enable: true,
                speed: 1,
                direction: 'none',
                random: true,
                straight: false,
                out_mode: 'out',
                bounce: false,
                attract: {
                    enable: false,
                    rotateX: 600,
                    rotateY: 1200
                }
            }
        },
        interactivity: {
            detect_on: 'canvas',
            events: {
                onhover: {
                    enable: true,
                    mode: 'grab'
                },
                onclick: {
                    enable: true,
                    mode: 'push'
                },
                resize: true
            },
            modes: {
                grab: {
                    distance: 140,
                    line_linked: {
                        opacity: 0.5
                    }
                },
                push: {
                    particles_nb: 4
                }
            }
        },
        retina_detect: true
    });
}

function createDataFlows() {
    const dataFlow = document.getElementById('dataFlow');
    const numStreams = 30;
    
    for (let i = 0; i < numStreams; i++) {
        const stream = document.createElement('div');
        stream.className = 'data-stream';
        
        // Случайное положение
        const left = Math.random() * 100;
        const delay = Math.random() * 5;
        const duration = 3 + Math.random() * 5;
        const width = 1 + Math.random() * 2;
        
        stream.style.left = `${left}%`;
        stream.style.width = `${width}px`;
        stream.style.animationDelay = `${delay}s`;
        stream.style.animationDuration = `${duration}s`;
        
        dataFlow.appendChild(stream);
    }
    
    // Создание эффекта свечения
    for (let i = 0; i < 5; i++) {
        const glow = document.createElement('div');
        glow.className = 'glow-effect';
        
        const left = Math.random() * 100;
        const top = Math.random() * 100;
        const delay = Math.random() * 5;
        
        glow.style.left = `${left}%`;
        glow.style.top = `${top}%`;
        glow.style.animationDelay = `${delay}s`;
        
        document.querySelector('.analytics-container').appendChild(glow);
    }
}

function init3DScene() {
    const container = document.getElementById('sceneContainer');
    
    // Создание сцены Three.js
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    
    const renderer = new THREE.WebGLRenderer({ alpha: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setClearColor(0x000000, 0);
    container.appendChild(renderer.domElement);
    
    // Создание геометрии
    const geometry = new THREE.TorusKnotGeometry(10, 3, 100, 16);
    const material = new THREE.MeshBasicMaterial({ 
        color: 0x00d4ff,
        wireframe: true,
        transparent: true,
        opacity: 0.1
    });
    
    const torusKnot = new THREE.Mesh(geometry, material);
    scene.add(torusKnot);
    
    camera.position.z = 30;
    
    // Анимация
    function animate() {
        requestAnimationFrame(animate);
        
        torusKnot.rotation.x += 0.003;
        torusKnot.rotation.y += 0.005;
        
        renderer.render(scene, camera);
    }
    
    animate();
    
    // Обработка изменения размера окна
    window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });
}

function animateCards() {
    // Анимация карточек
    const cards = document.querySelectorAll('.analytics-card');
    cards.forEach((card, index) => {
        gsap.from(card, {
            opacity: 0,
            y: 50,
            duration: 0.8,
            delay: 0.2 * index,
            ease: 'power3.out'
        });
    });
    
    // Анимация заголовка
    gsap.from('.analytics-header', {
        opacity: 0,
        y: -30,
        duration: 1,
        ease: 'power3.out'
    });
    
    // Анимация тегов
    gsap.from('.tech-tag', {
        opacity: 0,
        scale: 0.5,
        duration: 0.5,
        stagger: 0.1,
        delay: 1,
        ease: 'back.out'
    });
}