document.addEventListener('DOMContentLoaded', function() {
  console.log('Neuro-script.js загружен');
  
  // Проверяем наличие canvas на странице
  var canvas = document.getElementById('canvas');
  console.log('Canvas найден:', canvas);
  if (!canvas) {
    console.error('Canvas не найден на странице');
    return;
  }
  
  var context = canvas.getContext('2d');
  console.log('Canvas context получен:', context);
  if (!context) {
    console.error('Не удалось получить canvas context');
    return;
  }

  console.log('Canvas размеры:', canvas.width, 'x', canvas.height);
  console.log('Canvas стили:', getComputedStyle(canvas).width, 'x', getComputedStyle(canvas).height);

  window.requestAnimFrame = function () {
    return (
      window.requestAnimationFrame ||
      window.webkitRequestAnimationFrame ||
      window.mozRequestAnimationFrame ||
      window.oRequestAnimationFrame ||
      window.msRequestAnimationFrame ||
      function (callback) {
        window.setTimeout(callback, 1000 / 60);
      }
    );
  }();

  //get DPI
  let dpi = window.devicePixelRatio || 1;
  context.scale(dpi, dpi);

  function fix_dpi() {
    //get CSS height
    //the + prefix casts it to an integer
    //the slice method gets rid of "px"
    let style_height = +getComputedStyle(canvas).getPropertyValue("height").slice(0, -2);
    let style_width = +getComputedStyle(canvas).getPropertyValue("width").slice(0, -2);

    //scale the canvas
    canvas.setAttribute('height', style_height * dpi);
    canvas.setAttribute('width', style_width * dpi);
  }

  var particle_count = 70,
    particles = [],
    couleurs = ["#CC0099", "#FFFF66", "#FF0000", "#FF9900"];
  
  function Particle() {
    this.radius = Math.round((Math.random() * 2) + 2);
    this.x = Math.floor((Math.random() * ((+getComputedStyle(canvas).getPropertyValue("width").slice(0, -2) * dpi) - this.radius + 1) + this.radius));
    this.y = Math.floor((Math.random() * ((+getComputedStyle(canvas).getPropertyValue("height").slice(0, -2) * dpi) - this.radius + 1) + this.radius));
    this.color = couleurs[Math.floor(Math.random() * couleurs.length)];
    this.speedx = Math.round((Math.random() * 81) + 0) / 100;
    this.speedy = Math.round((Math.random() * 81) + 0) / 100;

    switch (Math.round(Math.random() * couleurs.length)) {
      case 1:
        this.speedx *= 1;
        this.speedy *= 1;
        break;
      case 2:
        this.speedx *= -1;
        this.speedy *= 1;
        break;
      case 3:
        this.speedx *= 1;
        this.speedy *= -1;
        break;
      case 4:
        this.speedx *= -1;
        this.speedy *= -1;
        break;
    }

    this.move = function () {
      context.beginPath();
      context.globalCompositeOperation = 'source-over';
      context.fillStyle = this.color;
      context.globalAlpha = 1;
      context.arc(this.x, this.y, this.radius, 0, Math.PI * 2, false);
      context.fill();
      context.closePath();

      this.x = this.x + this.speedx;
      this.y = this.y + this.speedy;

      if (this.x <= 0 + this.radius) {
        this.speedx *= -1;
      }
      if (this.x >= canvas.width - this.radius) {
        this.speedx *= -1;
      }
      if (this.y <= 0 + this.radius) {
        this.speedy *= -1;
      }
      if (this.y >= canvas.height - this.radius) {
        this.speedy *= -1;
      }

      for (var j = 0; j < particle_count; j++) {
        var particleActuelle = particles[j],
          yd = particleActuelle.y - this.y,
          xd = particleActuelle.x - this.x,
          d = Math.sqrt(xd * xd + yd * yd);

        if (d < 200) {
          context.beginPath();
          context.globalAlpha = (200 - d) / (200 - 0);
          context.globalCompositeOperation = 'destination-over';
          context.lineWidth = 1;
          context.moveTo(this.x, this.y);
          context.lineTo(particleActuelle.x, particleActuelle.y);
          context.strokeStyle = this.color;
          context.lineCap = "round";
          context.stroke();
          context.closePath();
        }
      }
    };
  }

  function initAnimation() {
    try {
      console.log('Инициализация анимации...');
      fix_dpi();
      console.log('DPI исправлен');
      for (var i = 0; i < particle_count; i++) {
        var particle = new Particle();
        particles.push(particle);
      }
      console.log('Создано частиц:', particles.length);
      animate();
      console.log('Анимация запущена');
    } catch (e) {
      console.error("Error initializing animation:", e);
    }
  }

  function animate() {
    try {
      fix_dpi();
      context.clearRect(0, 0, canvas.width, canvas.height);
      for (var i = 0; i < particle_count; i++) {
        particles[i].move();
      }
      requestAnimFrame(animate);
    } catch (e) {
      console.error("Error in animation:", e);
    }
  }

  // Запускаем анимацию с небольшой задержкой
  setTimeout(initAnimation, 500);
});