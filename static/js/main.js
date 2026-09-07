/* main.js — PokerTracker Client-Side Enhancements */

// ── Mobile Nav Toggle ──────────────────────────────────────
(function () {
  const toggle = document.getElementById('navToggle');
  const links  = document.querySelector('.nav-links');
  if (!toggle || !links) return;

  toggle.addEventListener('click', () => {
    links.classList.toggle('open');
    const isOpen = links.classList.contains('open');
    toggle.setAttribute('aria-expanded', isOpen);
  });

  // Close when clicking a link
  links.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', () => links.classList.remove('open'));
  });
})();


// ── Auto-dismiss flash messages after 4 seconds ─────────────
(function () {
  const flashes = document.querySelectorAll('.flash');
  flashes.forEach(flash => {
    setTimeout(() => {
      flash.style.animation = 'flashOut 0.3s ease forwards';
      setTimeout(() => flash.remove(), 300);
    }, 4000);
  });

  const style = document.createElement('style');
  style.textContent = `
    @keyframes flashOut {
      to { opacity: 0; transform: translateX(20px); }
    }
  `;
  document.head.appendChild(style);
})();


// ── Add Session Form: Live Net Preview ─────────────────────
(function () {
  const buyInEl     = document.getElementById('buy_in');
  const endAmountEl = document.getElementById('end_amount');
  const previewEl   = document.getElementById('netPreviewValue');

  if (!buyInEl || !endAmountEl || !previewEl) return;

  function updateNetPreview() {
    const buyIn     = parseFloat(buyInEl.value)     || 0;
    const endAmount = parseFloat(endAmountEl.value) || 0;

    if (buyInEl.value === '' && endAmountEl.value === '') {
      previewEl.textContent = '—';
      previewEl.className   = 'net-preview-value';
      return;
    }

    const net = endAmount - buyIn;
    const sign = net > 0 ? '+' : '';
    previewEl.textContent = `${sign}$${Math.abs(net).toFixed(2)}`;

    previewEl.className = 'net-preview-value ' +
      (net > 0 ? 'is-win' : net < 0 ? 'is-loss' : '');
  }

  buyInEl.addEventListener('input', updateNetPreview);
  endAmountEl.addEventListener('input', updateNetPreview);

  // Run once on load in case of pre-filled values (form error repopulation)
  updateNetPreview();
})();


// ── Analytics: Profit Chart ─────────────────────────────────
(function () {
  const canvas = document.getElementById('profitChart');
  if (!canvas) return;

  const labels = window.CHART_LABELS || [];
  const values = window.CHART_VALUES || [];

  if (labels.length === 0) return;

  const isProfit = values[values.length - 1] >= 0;
  const lineColor = isProfit ? '#3ecf8e' : '#e05252';
  const fillColor = isProfit
    ? 'rgba(62, 207, 142, 0.08)'
    : 'rgba(224, 82, 82, 0.08)';

  // Wait for Chart.js to load (it's loaded as a deferred script)
  function initChart() {
    if (typeof Chart === 'undefined') {
      setTimeout(initChart, 100);
      return;
    }

    new Chart(canvas, {
      type: 'line',
      data: {
        labels,
        datasets: [{
          label: 'Cumulative P/L ($)',
          data: values,
          borderColor: lineColor,
          backgroundColor: fillColor,
          borderWidth: 2.5,
          pointRadius: labels.length < 20 ? 5 : 2,
          pointHoverRadius: 7,
          pointBackgroundColor: lineColor,
          pointBorderColor: '#0f0f12',
          pointBorderWidth: 2,
          tension: 0.35,
          fill: true,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: '#1a1a20',
            borderColor: '#2e2e3e',
            borderWidth: 1,
            titleColor: '#8888a0',
            bodyColor: '#e8e8f0',
            padding: 12,
            callbacks: {
              label: ctx => {
                const v = ctx.parsed.y;
                return ` ${v >= 0 ? '+' : ''}$${v.toFixed(2)}`;
              },
            },
          },
        },
        scales: {
          x: {
            grid: { color: 'rgba(46,46,62,0.5)', drawBorder: false },
            ticks: { color: '#8888a0', font: { size: 11 }, maxTicksLimit: 10 },
          },
          y: {
            grid: { color: 'rgba(46,46,62,0.5)', drawBorder: false },
            ticks: {
              color: '#8888a0',
              font: { size: 11 },
              callback: v => `$${v}`,
            },
          },
        },
      },
    });
  }

  initChart();
})();


// ── Staggered fade-in for session table rows ────────────────
(function () {
  const rows = document.querySelectorAll('.session-row');
  rows.forEach((row, i) => {
    row.style.opacity = '0';
    row.style.transform = 'translateY(10px)';
    row.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
    setTimeout(() => {
      row.style.opacity = '1';
      row.style.transform = 'translateY(0)';
    }, 50 + i * 40);
  });
})();


// ── Delete Confirmation Modal ───────────────────────────────
function openDeleteModal(btn) {
  const url = btn.getAttribute('data-delete-url');
  const modal = document.getElementById('deleteModal');
  const form  = document.getElementById('deleteForm');
  if (!modal || !form) return;
  form.setAttribute('action', url);
  modal.style.display = 'flex';
  document.body.style.overflow = 'hidden';
}

function closeDeleteModal() {
  const modal = document.getElementById('deleteModal');
  if (!modal) return;
  modal.style.display = 'none';
  document.body.style.overflow = '';
}

// Close modal on overlay click or ESC
document.addEventListener('DOMContentLoaded', function () {
  const modal = document.getElementById('deleteModal');
  if (!modal) return;
  modal.addEventListener('click', function (e) {
    if (e.target === modal) closeDeleteModal();
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeDeleteModal();
  });
});
