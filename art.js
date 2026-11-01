/* 每个事件一张原创图：画面表现事件经过，数量来自 data/events.json 里的事实 */
(function () {
  var W = 480, H = 345;
  var RED = "#ff6a45", AMB = "#ffb04a", CRM = "#ffe9c7", TEAL = "#4fe8bd", ICE = "#a9b4ff", DIM = "rgba(255,240,220,.2)";

  function glow(c, col, b) { c.shadowColor = col; c.shadowBlur = b; }
  function plain(c) { c.shadowBlur = 0; c.globalAlpha = 1; c.setLineDash([]); }
  function line(c, pts, col, w, b) {
    glow(c, col, b === undefined ? 12 : b);
    c.strokeStyle = col; c.lineWidth = w || 2; c.lineCap = "round"; c.lineJoin = "round";
    c.beginPath(); c.moveTo(pts[0][0], pts[0][1]);
    for (var i = 1; i < pts.length; i++) c.lineTo(pts[i][0], pts[i][1]);
    c.stroke(); c.shadowBlur = 0;
  }
  function dot(c, x, y, r, col, b) {
    if (b) glow(c, col, b);
    c.fillStyle = col; c.beginPath(); c.arc(x, y, r, 0, 6.2832); c.fill(); c.shadowBlur = 0;
  }
  function ring(c, x, y, r, col, w, b) {
    glow(c, col, b === undefined ? 10 : b);
    c.strokeStyle = col; c.lineWidth = w || 2; c.beginPath(); c.arc(x, y, r, 0, 6.2832); c.stroke(); c.shadowBlur = 0;
  }
  function box(c, x, y, w, h, col, lw, r, b) {
    glow(c, col, b === undefined ? 10 : b);
    c.strokeStyle = col; c.lineWidth = lw || 2; c.beginPath();
    c.roundRect(x, y, w, h, r === undefined ? 6 : r); c.stroke(); c.shadowBlur = 0;
  }
  function fill(c, x, y, w, h, col, b) {
    if (b) glow(c, col, b);
    c.fillStyle = col; c.fillRect(x, y, w, h); c.shadowBlur = 0;
  }
  function wave(c, x0, x1, y, amp, col, seed, w) {
    var pts = [], x = x0, i = 0;
    while (x <= x1) {
      var env = Math.sin((x - x0) / (x1 - x0) * Math.PI);
      pts.push([x, y + Math.sin(i * 1.7 + seed) * Math.sin(i * 0.41 + seed * 2) * amp * env]);
      x += 4; i++;
    }
    line(c, pts, col, w || 2, 14);
  }
  /* 话筒 */
  function handset(c, x, y, s, col) {
    c.save(); c.translate(x, y + 30 * s); c.rotate(-0.42); c.translate(-x, -(y + 30 * s));
    glow(c, col, 16); c.strokeStyle = col; c.lineWidth = 9 * s; c.lineCap = "round";
    c.beginPath(); c.arc(x, y + 60 * s, 74 * s, Math.PI * 1.18, Math.PI * 1.82); c.stroke();
    c.lineWidth = 2; c.shadowBlur = 0;
    var a = [x - 70 * s, y + 26 * s], b = [x + 70 * s, y + 26 * s];
    c.fillStyle = col; glow(c, col, 12);
    c.beginPath(); c.roundRect(a[0] - 18 * s, a[1] - 6 * s, 36 * s, 24 * s, 7 * s); c.fill();
    c.beginPath(); c.roundRect(b[0] - 18 * s, b[1] - 6 * s, 36 * s, 24 * s, 7 * s); c.fill();
    c.shadowBlur = 0; c.restore();
  }
  /* 手机外框 */
  function phone(c, x, y, w, h, col) {
    box(c, x, y, w, h, col, 2.5, 12, 14);
    line(c, [[x + w * 0.38, y + 9], [x + w * 0.62, y + 9]], col, 2, 4);
  }
  /* 对话气泡 */
  function bubble(c, x, y, w, h, col, tail) {
    box(c, x, y, w, h, col, 2, 9, 10);
    var t = tail || 1;
    line(c, [[x + (t > 0 ? 18 : w - 18), y + h], [x + (t > 0 ? 12 : w - 12), y + h + 11], [x + (t > 0 ? 30 : w - 30), y + h]], col, 2, 6);
  }
  /* 信封 */
  function mail(c, x, y, w, h, col) {
    box(c, x, y, w, h, col, 2, 4, 8);
    line(c, [[x, y], [x + w / 2, y + h * 0.58], [x + w, y]], col, 1.6, 4);
  }
  /* 一个人的头像 */
  function person(c, x, y, s, col, dash) {
    if (dash) c.setLineDash([4, 4]);
    ring(c, x, y - 7 * s, 7 * s, col, 1.6, 6);
    c.strokeStyle = col; c.lineWidth = 1.6; c.beginPath(); c.arc(x, y + 15 * s, 13 * s, Math.PI * 1.12, Math.PI * 1.88); c.stroke();
    c.setLineDash([]);
  }
  function arrow(c, x0, y0, x1, y1, col) {
    line(c, [[x0, y0], [x1, y1]], col, 2, 8);
    var a = Math.atan2(y1 - y0, x1 - x0);
    line(c, [[x1 - Math.cos(a - 0.5) * 10, y1 - Math.sin(a - 0.5) * 10], [x1, y1], [x1 - Math.cos(a + 0.5) * 10, y1 - Math.sin(a + 0.5) * 10]], col, 2, 8);
  }
  function grid(c, n, x0, y0, x1, y1, draw) {
    var w = x1 - x0, h = y1 - y0, cols = Math.ceil(Math.sqrt(n * w / h)), rows = Math.ceil(n / cols), sx = w / cols, sy = h / rows;
    for (var i = 0; i < n; i++) draw(x0 + (i % cols) * sx, y0 + Math.floor(i / cols) * sy, i, sx, sy);
  }

  var SCENES = {
    /* 克隆的声音从话筒传出，一笔钱在一小时内转走 */
    "uk-energy-voice-2019": function (c) {
      handset(c, 150, 92, 0.95, CRM);
      wave(c, 56, 246, 186, 46, AMB, 1.2, 2.2);
      arrow(c, 262, 150, 372, 150, RED);
      ring(c, 410, 150, 34, RED, 3, 18);
      line(c, [[410, 128], [410, 150], [426, 160]], RED, 2.5, 8);
    },
    /* 一个熟悉的声音，加两封邮件，17 个被告 */
    "uae-bank-voice-2020": function (c) {
      handset(c, 110, 74, 0.72, CRM);
      wave(c, 34, 190, 142, 30, AMB, 2.4, 2);
      mail(c, 218, 46, 86, 56, CRM);
      mail(c, 240, 84, 86, 56, AMB);
      arrow(c, 336, 96, 386, 96, RED);
      for (var i = 0; i < 17; i++) person(c, 66 + (i % 9) * 44, 200 + Math.floor(i / 9) * 44 - 2, 0.62, i % 3 ? RED : AMB);
    },
    /* 五边形冒烟，股指短暂下探 0.29% 后回升 */
    "pentagon-fake-image-2023": function (c) {
      var pts = [], i, cx = 132, cy = 116, r = 74;
      for (i = 0; i <= 5; i++) pts.push([cx + Math.cos(i * 1.2566 - 1.5708) * r, cy + Math.sin(i * 1.2566 - 1.5708) * r * 0.82]);
      line(c, pts, ICE, 2.6, 14);
      var inner = pts.map(function (p) { return [cx + (p[0] - cx) * 0.5, cy + (p[1] - cy) * 0.5]; });
      line(c, inner, ICE, 1.4, 6);
      for (i = 0; i < 9; i++) ring(c, 170 + i * 8 + Math.sin(i) * 7, 96 - i * 9, 7 + i * 2.1, "rgba(255,233,199,.26)", 1.4, 3);
      var chart = [[252, 110], [292, 106], [326, 112], [344, 208], [362, 118], [404, 110], [456, 106]];
      line(c, chart, ICE, 2.6, 14);
      dot(c, 344, 208, 5, RED, 14);
      c.setLineDash([3, 5]); line(c, [[240, 110], [464, 110]], DIM, 1, 0); c.setLineDash([]);
    },
    /* 视频会议里全是伪造的人，只有一个真人；下面是 15 笔转账 */
    "arup-deepfake-meeting-2024": function (c) {
      for (var y = 0; y < 3; y++) for (var x = 0; x < 4; x++) {
        var bx = 62 + x * 92, by = 26 + y * 74, real = x === 2 && y === 1;
        box(c, bx, by, 82, 64, real ? TEAL : RED, real ? 2.6 : 1.6, 5, real ? 16 : 7);
        person(c, bx + 41, by + 30, 1, real ? TEAL : RED, !real);
      }
      for (var i = 0; i < 15; i++) fill(c, 62 + i * 24.6, 266, 18, 10, RED, 8);
    },
    /* 语音留言来自错误的渠道，被挡在盾牌外 */
    "lastpass-ceo-voice-2024": function (c) {
      bubble(c, 42, 44, 150, 54, DIM);
      bubble(c, 66, 118, 150, 54, DIM);
      bubble(c, 42, 192, 150, 54, CRM);
      wave(c, 56, 178, 219, 18, AMB, 3.2, 2);
      arrow(c, 214, 208, 272, 208, AMB);
      var s = [[352, 62], [428, 92], [420, 202], [352, 260], [284, 202], [276, 92], [352, 62]];
      line(c, s, TEAL, 3.2, 20);
      line(c, [[314, 158], [342, 188], [394, 124]], TEAL, 4, 14);
    },
    /* Teams 会议：一格是旧视频，CEO 的位置没有画面，只有聊天窗 */
    "wpp-ceo-teams-2024": function (c) {
      box(c, 34, 46, 186, 138, TEAL, 2.2, 7, 12);
      person(c, 127, 108, 2.2, TEAL, true);
      c.setLineDash([6, 6]); box(c, 236, 46, 112, 138, DIM, 1.6, 7, 0); c.setLineDash([]);
      bubble(c, 364, 56, 92, 30, CRM, -1);
      bubble(c, 364, 104, 92, 30, CRM, -1);
      bubble(c, 364, 152, 92, 30, TEAL, -1);
      wave(c, 34, 222, 222, 16, TEAL, 1.9, 2);
    },
    /* 一本书挡住了克隆的声音 */
    "ferrari-ceo-voice-2024": function (c) {
      wave(c, 22, 212, 138, 62, AMB, 4.1, 2.2);
      line(c, [[250, 60], [250, 216]], TEAL, 3, 16);
      line(c, [[250, 60], [226, 46], [226, 200], [250, 216]], TEAL, 2, 10);
      line(c, [[250, 60], [346, 34], [346, 188], [250, 216]], TEAL, 2.6, 14);
      line(c, [[250, 60], [438, 34], [438, 188], [250, 216]], TEAL, 2.6, 14);
      for (var i = 0; i < 6; i++) line(c, [[270, 84 + i * 18], [414, 62 + i * 18]], "rgba(79,232,189,.42)", 1.3, 0);
      line(c, [[368, 240], [390, 262], [434, 214]], TEAL, 3.4, 12);
    },
    /* 一个点代表一起投诉，共 22,364 个 */
    "fbi-ic3-ai-2025": function (c) {
      c.fillStyle = ICE;
      var n = 22364, cols = 262, sx = 436 / cols, sy = sx * 1.02;
      for (var i = 0; i < n; i++) c.fillRect(22 + (i % cols) * sx, 26 + Math.floor(i / cols) * sy, 1.05, 1.05);
    },
    /* 中枢连向约 30 个目标；人只在几个决策点出现 */
    "gtg-1002-espionage-2025": function (c) {
      var cx = 240, cy = 142, i;
      for (i = 0; i < 30; i++) {
        var a = i / 30 * 6.2832, r = 96 + (i % 3) * 22, x = cx + Math.cos(a) * r * 1.65, y = cy + Math.sin(a) * r;
        line(c, [[cx, cy], [x, y]], "rgba(169,180,255,.34)", 1, 0);
        dot(c, x, y, 3.6, ICE, 8);
      }
      dot(c, cx, cy, 14, ICE, 26);
      ring(c, cx, cy, 24, ICE, 1.5, 8);
      for (i = 0; i < 6; i++) {
        var b = i / 6 * 6.2832 + 0.4;
        person(c, cx + Math.cos(b) * 62, cy + Math.sin(b) * 44, 0.62, i < 4 ? CRM : "rgba(255,233,199,.45)", i >= 4);
      }
    },
    /* 95 格代表 €9,500 万：53 格追回，36 格下落不明，6 格没有解释 */
    "fideuram-voice-clone-2026": function (c) {
      bubble(c, 34, 30, 96, 44, CRM);
      arrow(c, 140, 52, 182, 52, AMB);
      handset(c, 238, 24, 0.5, CRM);
      arrow(c, 300, 52, 342, 52, AMB);
      box(c, 354, 26, 92, 54, RED, 2.4, 5, 14);
      ring(c, 400, 53, 15, RED, 2, 8);
      grid(c, 95, 34, 104, 446, 268, function (x, y, i, sx, sy) {
        var col = i < 53 ? TEAL : i < 89 ? RED : "rgba(255,255,255,.2)";
        fill(c, x, y, sx - 3, sy - 3, col, i >= 53 && i < 89 ? 6 : 0);
      });
    },
    /* 账户被骑劫，语音一笔笔要钱，储蓄条被抽空 */
    "hk-whatsapp-father-2026": function (c) {
      phone(c, 40, 22, 128, 230, CRM);
      bubble(c, 56, 62, 96, 34, AMB);
      wave(c, 64, 144, 79, 11, AMB, 2.2, 1.8);
      bubble(c, 56, 118, 96, 34, AMB);
      wave(c, 64, 144, 135, 11, AMB, 3.3, 1.8);
      bubble(c, 56, 174, 96, 34, AMB);
      wave(c, 64, 144, 191, 11, AMB, 4.4, 1.8);
      arrow(c, 186, 138, 246, 138, RED);
      for (var i = 0; i < 10; i++) {
        if (i < 9) box(c, 270 + i * 18, 196 - i * 16, 150 - i * 18, 13, "rgba(255,106,69,.24)", 1, 3, 0);
        else fill(c, 270 + i * 18, 196 - i * 16, 150 - i * 18, 13, RED, 12);
      }
      line(c, [[262, 214], [428, 214]], RED, 2.4, 14);
    },
    /* 七栋楼最先被点名，后来总数升到 16 家 */
    "kr-artex-financial-breach-2026": function (c) {
      var i, cx = 240;
      for (i = 0; i < 16; i++) {
        var x = 26 + i * 28, hot = i >= 4 && i < 11, h = 66 + ((i * 37) % 62);
        box(c, x, 214 - h, 22, h, hot ? ICE : "rgba(169,180,255,.28)", hot ? 2 : 1.2, 2, hot ? 12 : 0);
        for (var w = 0; w < Math.floor(h / 18); w++) fill(c, x + 6, 214 - h + 8 + w * 18, 10, 5, hot ? ICE : "rgba(169,180,255,.2)");
        if (hot) line(c, [[x + 11, 214 - h], [cx, 26]], "rgba(169,180,255,.5)", 1.2, 5);
      }
      ring(c, cx, 26, 11, CRM, 2, 16);
      dot(c, cx, 26, 4, CRM, 12);
    },
    /* 把银行卡贴到手机上，背后是约 170 名受害者 */
    "nl-ai-bank-calls-2026": function (c) {
      grid(c, 170, 250, 22, 462, 268, function (x, y) { dot(c, x + 5, y + 5, 2.5, RED, 5); });
      phone(c, 56, 24, 124, 228, CRM);
      c.save(); c.translate(120, 148); c.rotate(-0.16);
      box(c, -86, -50, 172, 104, AMB, 2.6, 9, 16);
      fill(c, -86, -28, 172, 15, "rgba(255,176,74,.5)");
      c.restore();
      for (var i = 1; i < 4; i++) {
        glow(c, CRM, 10); c.strokeStyle = CRM; c.lineWidth = 2;
        c.beginPath(); c.arc(190, 90, i * 15, -0.8, 0.8); c.stroke(); c.shadowBlur = 0;
      }
    },
    /* 钱包里的硬件，隐藏芯片读走 24 个词 */
    "ledger-hardware-implant-2026": function (c) {
      box(c, 40, 92, 232, 100, CRM, 2.6, 16, 14);
      box(c, 62, 112, 110, 60, "rgba(255,233,199,.38)", 1.4, 4, 0);
      fill(c, 196, 122, 44, 40, RED, 22);
      for (var p = 0; p < 6; p++) {
        line(c, [[196, 128 + p * 6], [188, 128 + p * 6]], RED, 1.2, 0);
        line(c, [[240, 128 + p * 6], [248, 128 + p * 6]], RED, 1.2, 0);
      }
      for (var i = 0; i < 24; i++) {
        var x = 292 + (i % 6) * 28, y = 56 + Math.floor(i / 6) * 44;
        box(c, x, y, 21, 13, RED, 1.4, 3, 8);
      }
      arrow(c, 246, 142, 284, 142, RED);
    },
    /* 模型逃出测试环境，走到另一家公司的系统里 */
    "openai-hugging-face-escape-2026": function (c) {
      var x = 44, y = 96, s = 124;
      line(c, [[x, y], [x + s, y], [x + s, y + 40]], ICE, 2.4, 14);
      line(c, [[x + s, y + 86], [x + s, y + s], [x, y + s], [x, y]], ICE, 2.4, 14);
      line(c, [[x, y], [x + 34, y - 30], [x + s + 34, y - 30], [x + s, y]], ICE, 1.8, 8);
      line(c, [[x + s + 34, y - 30], [x + s + 34, y + 94], [x + s, y + s]], ICE, 1.8, 8);
      for (var i = 0; i < 16; i++) dot(c, x + 16 + (i % 4) * 26, y + 20 + Math.floor(i / 4) * 24, 4, "rgba(169,180,255,.4)");
      var trail = [[x + s - 10, y + 62], [x + s + 48, y + 62], [x + s + 80, y + 18], [x + s + 118, y + 72], [x + s + 150, y + 40], [x + s + 182, y + 58]];
      line(c, trail, CRM, 2.8, 18);
      dot(c, trail[0][0], trail[0][1], 7, CRM, 18);
      box(c, 366, 66, 84, 118, AMB, 2.6, 6, 16);
      line(c, [[366, 112], [356, 118], [366, 124]], AMB, 2.4, 6);
      for (var k = 0; k < 4; k++) line(c, [[378, 88 + k * 22], [438, 88 + k * 22]], "rgba(255,176,74,.5)", 1.4, 0);
    },
    /* 8 个智能体 → 21 个系统 → 85 个账号 → 2,500 条记录；左边的人是否在场有争议 */
    "taiwan-agent-attack-2026": function (c) {
      var i, a = [], b = [];
      person(c, 26, 136, 1.2, "rgba(255,233,199,.6)", true);
      for (i = 0; i < 8; i++) { a.push([70, 44 + i * 26]); dot(c, 70, 44 + i * 26, 6, ICE, 12); }
      for (i = 0; i < 21; i++) {
        b.push([168, 22 + i * 12.2]);
        line(c, [a[i % 8], b[i]], "rgba(169,180,255,.3)", 0.9, 0);
        fill(c, 164, 19 + i * 12.2, 9, 6, ICE, 5);
      }
      for (i = 0; i < 85; i++) {
        var x = 258 + (i % 6) * 8, y = 18 + Math.floor(i / 6) * 17.4;
        line(c, [b[i % 21], [x, y]], "rgba(169,180,255,.1)", 0.6, 0);
        dot(c, x, y, 2.4, CRM);
      }
      c.fillStyle = RED;
      var cols = 62;
      for (i = 0; i < 2500; i++) c.fillRect(322 + (i % cols) * 2.3, 20 + Math.floor(i / cols) * 5.8, 1.4, 1.4);
    },
    /* 1,342 个格子被锁，密钥从未发出 */
    "jadepuffer-agentic-ransomware-2026": function (c) {
      grid(c, 1342, 22, 20, 458, 228, function (x, y, i, sx, sy) { fill(c, x, y, sx - 1.2, sy - 1.2, i % 17 ? "rgba(169,180,255,.5)" : ICE); });
      ring(c, 150, 268, 16, CRM, 2.8, 14);
      line(c, [[166, 268], [234, 268], [234, 282]], CRM, 2.8, 12);
      line(c, [[218, 268], [218, 278]], CRM, 2.8, 8);
      c.setLineDash([5, 7]); line(c, [[252, 268], [420, 268]], "rgba(255,233,199,.32)", 1.6, 0); c.setLineDash([]);
      line(c, [[432, 256], [456, 280]], RED, 3, 12);
      line(c, [[456, 256], [432, 280]], RED, 3, 12);
    },
    /* 63 个点代表 $63 亿：30 个被冻结，33 个没有；10 条链向外散开 */
    "binance-hot-wallet-2026": function (c) {
      var cx = 240, cy = 142, i, p = [];
      for (i = 0; i < 6; i++) p.push([cx + Math.cos(i * 1.0472) * 34, cy + Math.sin(i * 1.0472) * 34]);
      p.push(p[0]);
      line(c, p, AMB, 3, 22);
      for (i = 0; i < 10; i++) {
        var a = i / 10 * 6.2832 + 0.2;
        line(c, [[cx + Math.cos(a) * 38, cy + Math.sin(a) * 38], [cx + Math.cos(a) * 112 * 1.5, cy + Math.sin(a) * 112]], "rgba(255,106,69,.4)", 1.2, 4);
      }
      for (i = 0; i < 63; i++) {
        var t = i / 63 * 6.2832, r = 124 + (i % 3) * 10;
        dot(c, cx + Math.cos(t) * r * 1.62, cy + Math.sin(t) * r * 0.98, 3.4, i < 30 ? ICE : RED, 9);
      }
    }
  };

  /* 没有专属图的事件按类型自动生成，贡献者不用写代码 */
  var GENERIC = {
    voice: function (c) { handset(c, 240, 78, 1.05, CRM); wave(c, 96, 384, 196, 56, AMB, 2.7, 2.4); },
    video: function (c) {
      for (var y = 0; y < 3; y++) for (var x = 0; x < 4; x++) {
        box(c, 62 + x * 92, 26 + y * 74, 82, 64, RED, 1.6, 5, 7);
        person(c, 103 + x * 92, 56 + y * 74, 1, RED, true);
      }
    },
    breach: function (c) {
      for (var i = 0; i < 9; i++) {
        var h = 70 + ((i * 53) % 90);
        box(c, 86 + i * 34, 230 - h, 26, h, ICE, 1.8, 2, 10);
        line(c, [[99 + i * 34, 230 - h], [240, 30]], "rgba(169,180,255,.4)", 1.1, 4);
      }
      ring(c, 240, 30, 12, CRM, 2, 16);
    },
    market: function (c) {
      line(c, [[60, 110], [170, 104], [226, 112], [262, 224], [296, 118], [360, 110], [424, 104]], ICE, 2.8, 14);
      dot(c, 262, 224, 6, RED, 16);
    },
    theft: function (c) {
      var p = [], i, cx = 240, cy = 140;
      for (i = 0; i < 7; i++) p.push([cx + Math.cos(i * 1.0472) * 42, cy + Math.sin(i * 1.0472) * 42]);
      line(c, p, AMB, 3, 22);
      for (i = 0; i < 14; i++) {
        var a = i / 14 * 6.2832;
        line(c, [[cx + Math.cos(a) * 48, cy + Math.sin(a) * 48], [cx + Math.cos(a) * 190, cy + Math.sin(a) * 112]], "rgba(255,106,69,.5)", 1.3, 5);
        dot(c, cx + Math.cos(a) * 190, cy + Math.sin(a) * 112, 4, RED, 10);
      }
    },
    supply: function (c) {
      box(c, 110, 88, 260, 112, CRM, 2.6, 16, 14);
      fill(c, 262, 122, 54, 44, RED, 22);
      box(c, 134, 110, 106, 66, "rgba(255,233,199,.38)", 1.4, 4, 0);
    },
    autonomous: function (c) {
      var cx = 240, cy = 140, i;
      for (i = 0; i < 20; i++) {
        var a = i / 20 * 6.2832, x = cx + Math.cos(a) * 180, y = cy + Math.sin(a) * 104;
        line(c, [[cx, cy], [x, y]], "rgba(169,180,255,.34)", 1, 0);
        dot(c, x, y, 3.8, ICE, 8);
      }
      dot(c, cx, cy, 15, ICE, 26);
      ring(c, cx, cy, 26, ICE, 1.5, 8);
    },
    aggregate: function (c) {
      grid(c, 900, 30, 30, 450, 270, function (x, y) { c.fillStyle = ICE; c.fillRect(x, y, 3, 3); });
    }
  };

  function background(c, tone, seedText) {
    var seed = 7, k;
    for (k = 0; k < seedText.length; k++) seed = (seed * 31 + seedText.charCodeAt(k)) >>> 0;
    function r() { seed = (seed * 1664525 + 1013904223) >>> 0; return seed / 4294967296; }
    var pal = tone === "loss" ? ["#7a2614", "#6a3f12"] : tone === "blocked" ? ["#0f4a3c", "#16604f"] : ["#262e6e", "#3b2a6a"];
    c.fillStyle = "#0b0a0e"; c.fillRect(0, 0, W, H);
    c.globalCompositeOperation = "screen";
    for (k = 0; k < 3; k++) {
      var x = r() * W, y = r() * H, rad = 170 + r() * 170, g = c.createRadialGradient(x, y, 0, x, y, rad);
      g.addColorStop(0, pal[k % 2]); g.addColorStop(1, "rgba(0,0,0,0)");
      c.fillStyle = g; c.fillRect(0, 0, W, H);
    }
    c.globalCompositeOperation = "source-over";
  }

  window.AISecArt = {
    draw: function (cv, ev, tone) {
      var c = cv.getContext("2d"), s = cv.width / W;
      c.setTransform(s, 0, 0, s, 0, 0);
      background(c, tone, ev.id);
      (SCENES[ev.id] || GENERIC[ev.category] || GENERIC.aggregate)(c);
      plain(c);
    }
  };
})();
