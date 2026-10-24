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
