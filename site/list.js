/* 全部事件：搜索 + 按类型、AI 证据筛选。没有 JS 时列表照样全部显示 */
(function () {
  var rows = [].slice.call(document.querySelectorAll(".row")), q = document.getElementById("q"), count = document.getElementById("count");
  var pick = { cat: "", ev: "" };
  document.getElementById("tools").hidden = false;

  function apply() {
    var words = q.value.trim().toLowerCase().split(/\s+/).filter(Boolean), n = 0;
    rows.forEach(function (r) {
      var hay = r.getAttribute("data-q"), ok = (!pick.cat || r.getAttribute("data-cat") === pick.cat) && (!pick.ev || r.getAttribute("data-ev") === pick.ev);
      for (var i = 0; ok && i < words.length; i++) ok = hay.indexOf(words[i]) >= 0;
      r.parentNode.hidden = !ok;
      if (ok) n++;
    });
    count.textContent = count.getAttribute("data-tpl").replace("{n}", n);
    document.getElementById("empty").hidden = n > 0;
  }

  [].forEach.call(document.querySelectorAll(".chips"), function (group) {
    group.addEventListener("click", function (e) {
      var b = e.target.closest("button");
      if (!b) return;
      pick[group.getAttribute("data-key")] = b.getAttribute("data-v");
      [].forEach.call(group.children, function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
      apply();
    });
  });
  q.addEventListener("input", apply);
  apply();
})();
