// static/js/courbes.js — VitalHelp · Chart.js setup
// =============================================
// Couleurs (synchro avec la palette CSS)
const COLORS = {
  primary: '#E07A5F',
  primaryLight: 'rgba(224, 122, 95, 0.15)',
  secondary: '#81B29A',
  secondaryLight: 'rgba(129, 178, 154, 0.15)',
  accent: '#2B3A34',
  danger: '#D76A6A',
  muted: '#5C6A64',
  border: '#E5E1D8',
};

// Style global Chart.js
Chart.defaults.font.family = "'Work Sans', system-ui, sans-serif";
Chart.defaults.font.size = 12;
Chart.defaults.color = COLORS.muted;
Chart.defaults.plugins.legend.display = false;

// -----------------------------------------------
// Utilitaires
function gradientFill(ctx, color) {
  const g = ctx.createLinearGradient(0, 0, 0, 220);
  g.addColorStop(0, color);
  g.addColorStop(1, 'rgba(255,255,255,0)');
  return g;
}

function buildDatasets({ labels, valeurs, moyenne, objectif, label, color, ctx, alertes = [], secondSerie = null }) {
  const datasets = [];

  // Série principale — courbe pleine
  datasets.push({
    label: label,
    data: valeurs,
    borderColor: color,
    backgroundColor: gradientFill(ctx, color === COLORS.primary ? COLORS.primaryLight : COLORS.secondaryLight),
    borderWidth: 2.5,
    tension: 0.4,
    fill: true,
    pointBackgroundColor: '#fff',
    pointBorderColor: color,
    pointBorderWidth: 2,
    pointRadius: 4,
    pointHoverRadius: 6,
    spanGaps: true,
  });

  // Moyenne mobile — ligne pointillée fine
  if (moyenne) {
    datasets.push({
      label: 'Moyenne mobile',
      data: moyenne,
      borderColor: COLORS.accent,
      borderWidth: 2,
      borderDash: [6, 4],
      tension: 0.4,
      fill: false,
      pointRadius: 0,
      spanGaps: true,
    });
  }

  // Seconde série (ex: tension diastolique)
  if (secondSerie) {
    datasets.push({
      label: secondSerie.label,
      data: secondSerie.valeurs,
      borderColor: COLORS.secondary,
      backgroundColor: 'transparent',
      borderWidth: 2.5,
      tension: 0.4,
      fill: false,
      pointBackgroundColor: '#fff',
      pointBorderColor: COLORS.secondary,
      pointBorderWidth: 2,
      pointRadius: 4,
      pointHoverRadius: 6,
      spanGaps: true,
    });
  }

  // Ligne d'objectif horizontale (en pointillé terracotta)
  if (objectif) {
    datasets.push({
      label: `Objectif (${objectif})`,
      data: labels.map(() => objectif),
      borderColor: COLORS.primary,
      borderWidth: 2,
      borderDash: [3, 6],
      fill: false,
      pointRadius: 0,
      tension: 0,
    });
  }

  // Seuils d'alerte (rouge pointillé)
  alertes.forEach(seuil => {
    datasets.push({
      label: `Seuil ${seuil}`,
      data: labels.map(() => seuil),
      borderColor: COLORS.danger,
      borderWidth: 1.5,
      borderDash: [2, 4],
      fill: false,
      pointRadius: 0,
      tension: 0,
    });
  });

  return datasets;
}

// Options communes pour toutes les courbes
function chartOptions(unite = '') {
  return {
    responsive: true,
    maintainAspectRatio: false,
    interaction: { mode: 'index', intersect: false },
    plugins: {
      tooltip: {
        backgroundColor: '#2B3A34',
        titleColor: '#fff',
        titleFont: { weight: '700', family: "'Manrope', sans-serif" },
        bodyColor: '#fff',
        padding: 12,
        borderRadius: 12,
        displayColors: true,
        usePointStyle: true,
        callbacks: {
          label: (ctx) => {
            const v = ctx.parsed.y;
            return v === null ? null : `${ctx.dataset.label}: ${v} ${unite}`;
          },
        },
      },
    },
    scales: {
      x: {
        grid: { display: false },
        ticks: { font: { size: 11 } },
      },
      y: {
        grid: { color: COLORS.border, drawTicks: false },
        ticks: { font: { size: 11 }, padding: 8 },
        beginAtZero: false,
      },
    },
    animation: {
      duration: 800,
      easing: 'easeOutQuart',
    },
  };
}

// -----------------------------------------------
// Charge les données et dessine
async function main() {
  const res = await fetch('/donnees/courbes');
  if (!res.ok) return;
  const d = await res.json();
  const labels = d.labels;

  // Pas de données → on s'arrête
  if (!labels.length) return;

  // === Poids ===
  const ctxPoids = document.getElementById('chart-poids');
  if (ctxPoids) {
    new Chart(ctxPoids, {
      type: 'line',
      data: {
        labels,
        datasets: buildDatasets({
          labels, valeurs: d.poids.valeurs, moyenne: d.poids.moyenne_mobile,
          objectif: d.poids.objectif, label: 'Poids', color: COLORS.primary,
          ctx: ctxPoids.getContext('2d'),
        }),
      },
      options: chartOptions('kg'),
    });
  }

  // === Tension ===
  const ctxTension = document.getElementById('chart-tension');
  if (ctxTension) {
    new Chart(ctxTension, {
      type: 'line',
      data: {
        labels,
        datasets: buildDatasets({
          labels, valeurs: d.tension_sys.valeurs, moyenne: null,
          objectif: d.tension_sys.objectif, label: 'Systolique', color: COLORS.primary,
          ctx: ctxTension.getContext('2d'),
          alertes: [140, 90],
          secondSerie: { label: 'Diastolique', valeurs: d.tension_dia.valeurs },
        }),
      },
      options: chartOptions('mmHg'),
    });
  }

  // === Glycémie ===
  const ctxGly = document.getElementById('chart-glycemie');
  if (ctxGly) {
    new Chart(ctxGly, {
      type: 'line',
      data: {
        labels,
        datasets: buildDatasets({
          labels, valeurs: d.glycemie.valeurs, moyenne: d.glycemie.moyenne_mobile,
          objectif: d.glycemie.objectif, label: 'Glycémie', color: COLORS.secondary,
          ctx: ctxGly.getContext('2d'),
          alertes: [1.26],
        }),
      },
      options: chartOptions('g/L'),
    });
  }

  // === Fréq. cardiaque ===
  const ctxFc = document.getElementById('chart-fc');
  if (ctxFc) {
    new Chart(ctxFc, {
      type: 'line',
      data: {
        labels,
        datasets: buildDatasets({
          labels, valeurs: d.freq_cardiaque.valeurs, moyenne: d.freq_cardiaque.moyenne_mobile,
          objectif: d.freq_cardiaque.objectif, label: 'Fréq. cardiaque', color: COLORS.primary,
          ctx: ctxFc.getContext('2d'),
          alertes: [100, 50],
        }),
      },
      options: chartOptions('bpm'),
    });
  }
}

document.addEventListener('DOMContentLoaded', main);