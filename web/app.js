(function () {
  var root = document.body.dataset.root || "";

  // navbar shadow on scroll
  var nav = document.getElementById("nav");
  function onScroll() { nav.classList.toggle("scrolled", window.scrollY > 8); }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  // mobile sidebar
  var burger = document.getElementById("burger");
  var sidebar = document.getElementById("sidebar");
  if (burger) {
    burger.addEventListener("click", function () {
      if (sidebar) {
        sidebar.classList.toggle("open");
      } else {
        window.location.href = root + "informaciya/komandy/";
      }
    });
  }

  // search
  var modal = document.getElementById("search-modal");
  var input = document.getElementById("search-input");
  var results = document.getElementById("search-results");
  var index = null;

  function openSearch() {
    modal.hidden = false;
    input.value = "";
    results.innerHTML = "";
    input.focus();
    if (!index) {
      fetch(root + "search-index.json")
        .then(function (r) { return r.json(); })
        .then(function (data) { index = data; });
    }
  }
  function closeSearch() { modal.hidden = true; }

  document.getElementById("search-open").addEventListener("click", openSearch);
  document.getElementById("search-backdrop").addEventListener("click", closeSearch);
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") closeSearch();
    if ((e.ctrlKey || e.metaKey) && e.key === "k") { e.preventDefault(); openSearch(); }
  });

  input.addEventListener("input", function () {
    var q = input.value.trim().toLowerCase();
    results.innerHTML = "";
    if (!q || !index) return;
    var hits = [];
    for (var i = 0; i < index.length; i++) {
      var p = index[i];
      var inTitle = p.title.toLowerCase().indexOf(q) !== -1;
      var pos = p.text.toLowerCase().indexOf(q);
      if (inTitle || pos !== -1) hits.push({ p: p, score: inTitle ? 0 : 1, pos: pos });
    }
    hits.sort(function (a, b) { return a.score - b.score; });
    hits.slice(0, 8).forEach(function (h) {
      var a = document.createElement("a");
      a.className = "search-result";
      a.href = root + h.p.url;
      var snippet = h.pos > -1
        ? "…" + h.p.text.substring(Math.max(0, h.pos - 40), h.pos + 80) + "…"
        : h.p.text.substring(0, 110);
      a.innerHTML =
        '<div class="sr-title">' + h.p.icon + " " + h.p.title + "</div>" +
        '<div class="sr-text"></div>';
      a.querySelector(".sr-text").textContent = snippet;
      results.appendChild(a);
    });
  });
})();
