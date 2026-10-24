// 논문 검색 필터 (SCI Papers 페이지)
(function () {
  var q = document.getElementById('q');
  if (!q) return;
  var items = document.querySelectorAll('.paper[data-search]');
  var none = document.getElementById('noresult');
  q.addEventListener('input', function () {
    var v = q.value.trim().toLowerCase(), shown = 0;
    items.forEach(function (li) {
      var hit = !v || li.dataset.search.indexOf(v) !== -1;
      li.hidden = !hit; if (hit) shown++;
    });
    if (none) none.hidden = shown !== 0;
  });
})();

// 첫 화면 사진 슬라이드: 무작위 순서로 5초마다 전환
(function () {
  var box = document.querySelector('.slideshow');
  if (!box) return;
  var slides = Array.prototype.slice.call(box.querySelectorAll('.slide'));
  if (slides.length < 2) return;
  for (var i = slides.length - 1; i > 0; i--) {
    var k = Math.floor(Math.random() * (i + 1)); var t = slides[i]; slides[i] = slides[k]; slides[k] = t;
  }
  slides.forEach(function (s) { s.classList.remove('on'); s.querySelector('img').loading = 'eager'; });
  var n = 0; slides[0].classList.add('on');
  setInterval(function () {
    slides[n].classList.remove('on'); n = (n + 1) % slides.length; slides[n].classList.add('on');
  }, 5000);
})();
