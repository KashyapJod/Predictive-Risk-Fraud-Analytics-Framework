const scenarios = {
  normal: { user_id: 'u001', amount: 75, country: 'US' },
  suspicious: { user_id: 'u003', amount: 2500, country: 'NG' }
};
const form = document.querySelector('#risk-form');
const timestamp = document.querySelector('#timestamp');
const history = [];
const now = new Date();
now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
timestamp.value = now.toISOString().slice(0, 16);

document.querySelectorAll('.scenario').forEach(button => button.addEventListener('click', () => {
  document.querySelectorAll('.scenario').forEach(item => item.classList.remove('active'));
  button.classList.add('active');
  const data = scenarios[button.dataset.scenario];
  Object.entries(data).forEach(([key, value]) => { document.querySelector(`#${key}`).value = value; });
}));

form.addEventListener('submit', async event => {
  event.preventDefault();
  const button = form.querySelector('button[type="submit"]');
  button.disabled = true;
  button.querySelector('span').textContent = 'Assessing...';
  const payload = { user_id: form.user_id.value, amount: Number(form.amount.value), timestamp: new Date(form.timestamp.value).toISOString(), country: form.country.value.toUpperCase() };
  try {
    const response = await fetch('/predict', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
    if (!response.ok) throw new Error((await response.json()).detail || 'Unable to score transaction');
    const result = await response.json();
    renderResult(result, payload);
  } catch (error) {
    document.querySelector('#result-title').textContent = 'Assessment unavailable';
    document.querySelector('#empty-result').innerHTML = `<p>${error.message}</p><small>Check that the database and model artifacts are available.</small>`;
    document.querySelector('#empty-result').classList.remove('hidden');
    document.querySelector('#result-content').classList.add('hidden');
  } finally {
    button.disabled = false;
    button.querySelector('span').textContent = 'Run risk assessment';
  }
});

function renderResult(result, payload) {
  const actionClass = result.action.toLowerCase();
  document.querySelector('#empty-result').classList.add('hidden');
  document.querySelector('#result-content').classList.remove('hidden');
  document.querySelector('#result-title').textContent = 'Decision ready';
  document.querySelector('#decision').textContent = result.action;
  document.querySelector('#decision').style.color = result.action === 'DENY' ? '#f08b7e' : result.action === 'FLAG' ? '#f1ba6a' : '#c8e7d3';
  document.querySelector('#score').textContent = result.risk_score.toFixed(2);
  document.querySelector('#meter-fill').style.width = `${Math.max(result.risk_score * 100, 2)}%`;
  document.querySelector('#meter-fill').style.background = result.action === 'DENY' ? '#dc6a60' : result.action === 'FLAG' ? '#e6a856' : '#c8e7d3';
  const copy = result.action === 'DENY' ? 'High-signal anomaly. Hold the transaction for investigation.' : result.action === 'FLAG' ? 'Review recommended before releasing this transaction.' : 'This transaction is consistent with the available user context.';
  document.querySelector('#signal-title').textContent = result.action === 'APPROVE' ? 'Low-risk profile' : `${result.action} review signal`;
  document.querySelector('#signal-copy').textContent = copy;
  document.querySelector('#signal-symbol').textContent = result.action === 'APPROVE' ? '+' : '!';
  history.unshift({ ...result, user_id: payload.user_id, amount: payload.amount });
  renderHistory();
}

function renderHistory() {
  document.querySelector('#history-count').textContent = history.length;
  document.querySelector('#history-list').innerHTML = history.slice(0, 4).map(item => `<div class="history-item"><div class="history-user">${item.user_id}<small>$${item.amount.toFixed(2)} · score ${item.risk_score.toFixed(2)}</small></div><span class="history-action ${item.action.toLowerCase()}">${item.action}</span></div>`).join('');
}