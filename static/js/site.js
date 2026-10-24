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

// 슬라이드/캐러셀: 한 장씩 표시, 일정 시간마다 다음 장으로
document.querySelectorAll('.slideshow').forEach(function (box) {
  var slides = Array.prototype.slice.call(box.querySelectorAll('.slide'));
  var dots = Array.prototype.slice.call(box.querySelectorAll('.dots button'));
  if (slides.length < 2) return;
  if (box.dataset.random) {
    for (var i = slides.length - 1; i > 0; i--) {
      var k = Math.floor(Math.random() * (i + 1)); var t = slides[i]; slides[i] = slides[k]; slides[k] = t;
    }
  }
  var n = 0, ms = +box.dataset.interval || 5000, timer;
  function show(i) {
    slides.forEach(function (s) { s.classList.remove('on'); });
    dots.forEach(function (d) { d.classList.remove('on'); });
    n = i; slides[n].classList.add('on');
    if (dots.length) dots[box.dataset.random ? 0 : n].classList.add('on');
  }
  function start() { clearInterval(timer); timer = setInterval(function () { show((n + 1) % slides.length); }, ms); }
  dots.forEach(function (d, i) { d.addEventListener('click', function () { show(i); start(); }); });
  show(0); start();
});

// 연도 버튼/주소의 #연도로 이동하면 해당 연도 펼치기, 검색 중엔 모두 펼치기
function openYear(id){var d=document.getElementById(id); if(d&&d.tagName==='DETAILS'){d.open=true;}}
document.querySelectorAll('.yearbar a').forEach(function(a){a.addEventListener('click',function(){openYear(a.getAttribute('href').slice(1));});});
if(location.hash) openYear(location.hash.slice(1));
(function(){var q=document.getElementById('q'); if(!q) return; q.addEventListener('input',function(){ if(q.value.trim()) document.querySelectorAll('details.ygroup').forEach(function(d){d.open=true;}); });})();
