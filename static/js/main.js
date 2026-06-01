// ── Mobile nav toggle ──────────────────────────────────────────
(function () {
  var toggle = document.getElementById('navToggle');
  var links  = document.getElementById('navLinks');
  if (toggle && links) {
    toggle.addEventListener('click', function () {
      links.classList.toggle('open');
    });
  }
})();

// ── Admin sidebar toggle ───────────────────────────────────────
(function () {
  var btn     = document.getElementById('sidebarToggle');
  var sidebar = document.querySelector('.admin-sidebar');
  if (btn && sidebar) {
    btn.addEventListener('click', function () {
      sidebar.classList.toggle('open');
    });
    // Close on outside click
    document.addEventListener('click', function (e) {
      if (sidebar.classList.contains('open') &&
          !sidebar.contains(e.target) &&
          e.target !== btn) {
        sidebar.classList.remove('open');
      }
    });
  }
})();

// ── Image carousel ─────────────────────────────────────────────
function getCarouselState(btn) {
  var carousel = btn.closest('.carousel');
  var track    = carousel.querySelector('.carousel-track');
  var slides   = carousel.querySelectorAll('.carousel-slide');
  var index    = parseInt(carousel.getAttribute('data-index'), 10) || 0;
  return { carousel: carousel, track: track, slides: slides, index: index };
}

function updateCarousel(carousel, track, slides, newIndex) {
  var total = slides.length;
  newIndex = ((newIndex % total) + total) % total;
  carousel.setAttribute('data-index', newIndex);
  // RTL: slide to the right means decreasing index visually
  track.style.transform = 'translateX(' + (newIndex * 100) + '%)';
}

function carouselNext(btn) {
  var s = getCarouselState(btn);
  updateCarousel(s.carousel, s.track, s.slides, s.index + 1);
}

function carouselPrev(btn) {
  var s = getCarouselState(btn);
  updateCarousel(s.carousel, s.track, s.slides, s.index - 1);
}

// ── Star rating (contact form) ─────────────────────────────────
(function () {
  var container = document.getElementById('starRating');
  var hidden    = document.getElementById('ratingInput');
  if (!container || !hidden) return;

  var stars = container.querySelectorAll('.star-input');

  function setRating(val) {
    hidden.value = val;
    stars.forEach(function (s, i) {
      s.classList.toggle('active', i < val);
    });
  }

  // Default to 5
  setRating(5);

  stars.forEach(function (star, idx) {
    star.addEventListener('mouseover', function () {
      stars.forEach(function (s, i) {
        s.classList.toggle('active', i <= idx);
      });
    });
    star.addEventListener('mouseout', function () {
      setRating(parseInt(hidden.value, 10));
    });
    star.addEventListener('click', function () {
      setRating(idx + 1);
    });
  });
})();

// ── Auto-dismiss flash messages ────────────────────────────────
(function () {
  var flashes = document.querySelectorAll('.flash');
  flashes.forEach(function (el) {
    setTimeout(function () {
      el.style.transition = 'opacity 0.5s';
      el.style.opacity = '0';
      setTimeout(function () { el.remove(); }, 500);
    }, 4000);
  });
})();
