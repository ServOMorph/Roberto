const $ = (selector) => document.querySelector(selector);
let state = null;

function selectedMacro() {
  return state?.macros.find((macro) => macro.id === state.selectedId);
}

function render(next) {
  state = next;
  const active = state.status !== 'ready';
  $('#status-label').textContent = state.status === 'recording' ? 'ENREGISTREMENT' : state.status === 'playing' ? 'LECTURE' : 'PRÊT';
  $('#status-message').textContent = state.message;
  $('#status-dot').className = `status-dot ${active ? 'live' : ''}`;
  $('#record-mode').classList.toggle('active', state.actionMode === 'record');
  $('#play-mode').classList.toggle('active', state.actionMode === 'play');
  $('#record-mode').disabled = active;
  $('#play-mode').disabled = active;
  $('#new-macro').disabled = active;
  $('#record-moves').checked = state.recordMouseMoves;
  $('#record-moves').disabled = active;
  $('#mode-help').textContent = state.actionMode === 'record'
    ? (state.pendingName ? `Prochaine macro : ${state.pendingName}` : 'Créez une macro, puis appuyez sur F8.')
    : 'Sélectionnez une macro, puis appuyez sur F8.';

  const list = $('#macro-list');
  list.replaceChildren();
  if (!state.macros.length) {
    list.innerHTML = '<p class="empty">Aucune macro enregistrée.</p>';
  }
  state.macros.forEach((macro) => {
    const row = document.createElement('div');
    row.className = 'macro-row';
    const item = document.createElement('button');
    item.className = `macro-item ${macro.id === state.selectedId ? 'selected' : ''}`;
    item.disabled = active;
    item.innerHTML = `<span>${escapeHtml(macro.name)}</span><small>${macro.events} événements · ${formatDate(macro.createdAt)}</small>`;
    item.onclick = async () => render(await window.pywebview.api.select_macro(macro.id));
    const rename = document.createElement('button');
    rename.className = 'macro-rename';
    rename.title = `Renommer ${macro.name}`;
    rename.textContent = 'Renommer';
    rename.disabled = active;
    rename.onclick = async () => {
      const name = window.prompt('Nouveau nom de la macro :', macro.name);
      if (name !== null) render(await window.pywebview.api.rename_macro(macro.id, name));
    };
    row.append(item, rename);
    list.append(row);
  });
  const macro = selectedMacro();
  $('#detail').classList.toggle('hidden', !macro);
  if (macro && document.activeElement !== $('#macro-name')) $('#macro-name').value = macro.name;
  $('#save-name').disabled = active;
  $('#delete-macro').disabled = active;
}

function escapeHtml(value) {
  const box = document.createElement('span');
  box.textContent = value;
  return box.innerHTML;
}

function formatDate(value) {
  return new Intl.DateTimeFormat('fr-FR', { dateStyle: 'short', timeStyle: 'short' }).format(new Date(value));
}

async function refresh() {
  render(await window.pywebview.api.get_state());
}

window.addEventListener('pywebviewready', async () => {
  $('#record-mode').onclick = async () => render(await window.pywebview.api.set_action_mode('record'));
  $('#play-mode').onclick = async () => render(await window.pywebview.api.set_action_mode('play'));
  $('#record-moves').onchange = async (event) => render(await window.pywebview.api.set_record_mouse_moves(event.target.checked));
  $('#new-macro').onclick = async () => {
    const name = window.prompt('Nom de la macro :', '');
    if (name !== null) render(await window.pywebview.api.prepare_recording(name));
  };
  $('#save-name').onclick = async () => {
    const macro = selectedMacro();
    if (macro) render(await window.pywebview.api.rename_macro(macro.id, $('#macro-name').value));
  };
  $('#delete-macro').onclick = async () => {
    const macro = selectedMacro();
    if (macro && window.confirm(`Supprimer « ${macro.name} » ?`)) render(await window.pywebview.api.delete_macro(macro.id));
  };
  await refresh();
  setInterval(refresh, 350);
});
