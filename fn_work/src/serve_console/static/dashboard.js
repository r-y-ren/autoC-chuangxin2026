// 结果仪表盘（演进轮四 R21）：渲染四卡 + 无数据自动播演示轮 + 两两对比
let dashTimer = null;

function fmtFail(fl) {
  if (!fl || !Object.keys(fl).length) return '<p style="color:#8fa3c0">（未失效）</p>';
  let rows = '';
  for (const k in fl) {
    const v = fl[k];
    rows += '<tr><td>' + k + '</td><td>' + (typeof v === 'number' ? v.toFixed(1) : v) + '</td></tr>';
  }
  return '<table><tr><th>样式</th><th>失效电平 dB</th></tr>' + rows + '</table>';
}

function renderDash(d) {
  const L = document.getElementById('card-latest');
  if (L) {
    if (d.empty) {
      L.innerHTML = '<h2>最新结果</h2><b>演示数据生成中…</b><p style="color:#8fa3c0">后台正在跑一轮演示测试，几秒后自动填充</p>';
    } else {
      const badge = d.latest.synthetic
        ? '<span class="badge" style="background:#7d5dbb">合成数据</span>'
        : '<span class="badge" style="background:#2ecc71">实测数据</span>';
      L.innerHTML = '<h2>最新结果 ' + badge + '</h2>'
        + '<p>' + (d.latest.scenario || d.latest.name) + ' · 样本 ' + d.latest.kpi_n + '</p>'
        + fmtFail(d.latest.fail_levels)
        + (d.latest.speed_note ? '<p style="color:#8fa3c0;font-size:.85em">' + d.latest.speed_note + '</p>' : '')
        + (d.latest.cal_note ? '<p style="color:#8fa3c0;font-size:.85em">' + d.latest.cal_note + '</p>' : '')
        + (d.latest.figs && d.latest.figs.length ? '<img src="' + d.latest.figs[0] + '" style="margin-top:6px">' : '');
    }
  }
  const M = document.getElementById('card-model');
  if (M) {
    if (d.empty || !d.model) {
      M.innerHTML = '<h2>识别模型 / 数据集</h2><p style="color:#8fa3c0">暂无模型产物（跑一次演示自动生成）</p>';
    } else {
      M.innerHTML = '<h2>识别模型 / 数据集</h2>'
        + '<p>' + (d.model.f1_line || '') + '</p>'
        + '<p>录制 ' + (d.model.recordings != null ? d.model.recordings : '-')
        + ' · 分组 ' + (d.model.groups != null ? d.model.groups : '-') + '</p>';
    }
  }
  const C = document.getElementById('card-capability');
  if (C && d.capability) {
    C.innerHTML = '<h2>平台能力</h2><table>'
      + '<tr><td>干扰样式库</td><td>' + d.capability.styles + ' 种</td></tr>'
      + '<tr><td>场景卡</td><td>' + d.capability.scenarios + ' 张</td></tr>'
      + '<tr><td>插件槽</td><td>' + d.capability.plugin_slots + ' 类（仪表/链路/样式）</td></tr>'
      + '<tr><td>累计测试</td><td>' + d.capability.total_runs + ' 次</td></tr></table>';
  }
  const H = document.getElementById('card-history');
  if (H) {
    if (d.empty) { H.innerHTML = '<h2>历史与对比</h2><p>暂无</p>'; }
    else {
      const opts = d.history.map(r => '<option value="' + r.name + '">' + r.name + '</option>').join('');
      H.innerHTML = '<h2>历史与对比</h2>'
        + '<div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">'
        + '<select id="cmp-a">' + opts + '</select><span style="color:#8fa3c0">vs</span>'
        + '<select id="cmp-b">' + opts + '</select>'
        + '<button class="btn" onclick="drawCompare()">对比</button></div>'
        + '<table><tr><th>运行</th><th>时间</th><th>失效数</th><th>样本</th></tr>'
        + d.history.slice(0, 8).map(r => '<tr><td><a href="/reports/' + r.name + '">' + r.name + '</a></td><td>' + new Date(r.mtime * 1000).toLocaleString() + '</td><td>' + r.fails + '</td><td>' + r.kpi_n + '</td></tr>').join('')
        + '</table>'
        + '<canvas id="compare-chart" width="900" height="140" style="width:100%;background:#0a0f18;border-radius:8px;margin-top:8px"></canvas>';
    }
  }
  window._dash = d;
}

function drawCompare() {
  const d = window._dash;
  if (!d || !d.history.length) return;
  const a = document.getElementById('cmp-a').value;
  const b = document.getElementById('cmp-b').value;
  const ra = d.history.find(r => r.name === a);
  const rb = d.history.find(r => r.name === b);
  const styles = [...new Set(Object.keys(ra.fail_levels).concat(Object.keys(rb.fail_levels)))];
  const c = document.getElementById('compare-chart');
  const g = c.getContext('2d');
  g.clearRect(0, 0, c.width, c.height);
  if (!styles.length) {
    g.fillStyle = '#8fa3c0';
    g.fillText('两次运行均未失效，无对比数据', 40, 70);
    return;
  }
  const bw = Math.floor((c.width - 60) / styles.length);
  styles.forEach((s, i) => {
    const va = ra.fail_levels[s], vb = rb.fail_levels[s];
    const ha = va == null ? 4 : Math.max(4, (va + 20) / 60 * (c.height - 40));
    const hb = vb == null ? 4 : Math.max(4, (vb + 20) / 60 * (c.height - 40));
    g.fillStyle = '#4da3ff';
    g.fillRect(40 + i * bw, c.height - 20 - ha, bw * 0.4, ha);
    g.fillStyle = '#f1c40f';
    g.fillRect(40 + i * bw + bw * 0.5, c.height - 20 - hb, bw * 0.4, hb);
    g.fillStyle = '#8fa3c0';
    g.fillText(s, 40 + i * bw, c.height - 6);
  });
}

async function loadDash() {
  try {
    const r = await fetch('/api/dashboard');
    const d = await r.json();
    renderDash(d);
    if (d.empty) {
      await fetch('/api/seed_demo', { method: 'POST' });
      if (dashTimer) clearInterval(dashTimer);
      dashTimer = setInterval(async () => {
        try {
          const rr = await fetch('/api/dashboard');
          const dd = await rr.json();
          renderDash(dd);
          if (!dd.empty) { clearInterval(dashTimer); dashTimer = null; }
        } catch (e) { }
      }, 2000);
    }
  } catch (e) { }
}
loadDash();
