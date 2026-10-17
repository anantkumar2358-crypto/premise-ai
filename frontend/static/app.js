// Premise AI - Blind Spot & Assumption Intelligence Engine

let currentAnalysis = null;
let activeCategoryFilter = 'all';
let activeSeverityFilter = 'all';
let searchQuery = '';
let currentTargetDiscoveryId = null;

document.addEventListener('DOMContentLoaded', () => {
  lucide.createIcons();
  initApiKeyUI();
  initRiskMatrixGrid();
  renderSavedProjectsDropdown();

  // Close saved projects menu when clicking outside
  document.addEventListener('click', (e) => {
    const wrapper = document.getElementById('savedProjectsWrapper');
    if (wrapper && !wrapper.contains(e.target)) {
      toggleSavedProjectsMenu(false);
    }
  });

  // Check if there is an active custom project saved; otherwise load timetable_generator template
  const saved = getSavedProjects();
  if (saved.length > 0) {
    loadSavedProject(saved[0].id);
  } else {
    loadTemplate('timetable_generator');
  }
});

// Custom Project Workspace & State Persistence
function startCustomProject() {
  document.getElementById('projectNameInput').value = 'My Custom Project';
  document.getElementById('documentTextInput').value = '';
  document.getElementById('datasetContentInput').value = '';
  document.getElementById('workflowContentInput').value = '';
  document.getElementById('domainSelect').value = 'general';
  
  const badge = document.getElementById('projectModeBadge');
  if (badge) {
    badge.textContent = 'Custom Project Workspace';
    badge.className = 'text-[11px] px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 font-medium';
  }

  switchInputTab('doc');

  // Focus and select project name input
  const nameInput = document.getElementById('projectNameInput');
  nameInput.focus();
  nameInput.select();
  nameInput.classList.add('ring-2', 'ring-emerald-500');
  setTimeout(() => nameInput.classList.remove('ring-2', 'ring-emerald-500'), 2000);

  // Clear current results and set empty state
  currentAnalysis = {
    project_name: 'My Custom Project',
    health_score: 100,
    risk_priority_index: 0,
    executive_summary: "Ready to audit. Paste your Project Specification (PRD) or document in the box below, then click 'Run Deep Intelligence Audit' to discover blind spots.",
    discoveries: [],
    probing_questions: [],
    summary_stats: { critical_count: 0, high_count: 0, medium_count: 0, low_count: 0, missing_assumptions_count: 0, overlooked_constraints_count: 0, data_risks_count: 0, workflow_bottlenecks_count: 0 },
    engine_used: 'ready'
  };
  renderAnalysisView(currentAnalysis);
  showToast("Started new custom project workspace! Enter your project details below.");
}

function getSavedProjects() {
  try {
    return JSON.parse(localStorage.getItem('premise_saved_projects') || '[]');
  } catch (e) {
    return [];
  }
}

function saveCurrentWorkspaceManually() {
  saveCurrentProjectQuietly(true);
}

function saveCurrentProjectQuietly(showNotification = false) {
  const name = document.getElementById('projectNameInput').value.trim() || 'Untitled Custom Project';
  const doc = document.getElementById('documentTextInput').value;
  const data = document.getElementById('datasetContentInput').value;
  const wf = document.getElementById('workflowContentInput').value;
  const domain = document.getElementById('domainSelect').value;

  if (!doc && !data && !wf && (!currentAnalysis || currentAnalysis.discoveries.length === 0)) {
    if (showNotification) showToast("Workspace is empty. Provide some project details first.");
    return;
  }

  const projects = getSavedProjects();
  const existingIdx = projects.findIndex(p => p.name.toLowerCase() === name.toLowerCase());

  const projObj = {
    id: existingIdx >= 0 ? projects[existingIdx].id : 'proj_' + Date.now(),
    name: name,
    domain: domain,
    doc_text: doc,
    dataset_content: data,
    workflow_content: wf,
    updated_at: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    analysis: currentAnalysis
  };

  if (existingIdx >= 0) {
    projects[existingIdx] = projObj;
  } else {
    projects.unshift(projObj);
  }

  localStorage.setItem('premise_saved_projects', JSON.stringify(projects));
  renderSavedProjectsDropdown();
  if (showNotification) {
    showToast(`Workspace '${name}' saved! You can resume anytime.`);
  }
}

function loadSavedProject(id) {
  const projects = getSavedProjects();
  const proj = projects.find(p => p.id === id);
  if (!proj) return;

  document.getElementById('projectNameInput').value = proj.name;
  document.getElementById('domainSelect').value = proj.domain || 'general';
  document.getElementById('documentTextInput').value = proj.doc_text || '';
  document.getElementById('datasetContentInput').value = proj.dataset_content || '';
  document.getElementById('workflowContentInput').value = proj.workflow_content || '';

  const badge = document.getElementById('projectModeBadge');
  if (badge) {
    badge.textContent = `Workspace: ${proj.name}`;
    badge.className = 'text-[11px] px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 font-medium';
  }

  toggleSavedProjectsMenu(false);

  if (proj.analysis && proj.analysis.discoveries && proj.analysis.discoveries.length > 0) {
    currentAnalysis = proj.analysis;
    renderAnalysisView(currentAnalysis);
    showToast(`Resumed workspace '${proj.name}'`);
  } else {
    runAnalysis();
  }
}

function deleteSavedProject(e, id) {
  e.stopPropagation();
  let projects = getSavedProjects();
  projects = projects.filter(p => p.id !== id);
  localStorage.setItem('premise_saved_projects', JSON.stringify(projects));
  renderSavedProjectsDropdown();
  showToast("Project workspace deleted.");
}

function clearAllSavedProjects() {
  if (confirm("Clear all saved custom project workspaces?")) {
    localStorage.removeItem('premise_saved_projects');
    renderSavedProjectsDropdown();
    showToast("All saved workspaces cleared.");
  }
}

function toggleSavedProjectsMenu(force) {
  const menu = document.getElementById('savedProjectsMenu');
  if (!menu) return;
  if (force !== undefined) {
    if (force) menu.classList.remove('hidden');
    else menu.classList.add('hidden');
  } else {
    menu.classList.toggle('hidden');
  }
}

function renderSavedProjectsDropdown() {
  const projects = getSavedProjects();
  const label = document.getElementById('savedProjectsBtnLabel');
  if (label) label.textContent = `My Projects (${projects.length})`;

  const list = document.getElementById('savedProjectsList');
  if (!list) return;

  if (projects.length === 0) {
    list.innerHTML = `<div class="px-3 py-2 text-slate-500 text-[11px] text-center">No saved custom projects yet.<br><span class="text-indigo-400">Click 'Save Workspace' to save.</span></div>`;
    return;
  }

  list.innerHTML = projects.map(p => `
    <div onclick="loadSavedProject('${p.id}')" class="px-3 py-2 hover:bg-slate-700/50 flex items-center justify-between cursor-pointer border-b border-slate-800 last:border-0 group transition">
      <div>
        <div class="font-semibold text-slate-200 group-hover:text-indigo-300 transition">${escapeHtml(p.name)}</div>
        <div class="text-[10px] text-slate-400">Updated: ${p.updated_at}</div>
      </div>
      <button onclick="deleteSavedProject(event, '${p.id}')" class="text-slate-500 hover:text-rose-400 p-1 rounded hover:bg-slate-800" title="Delete workspace">
        <i data-lucide="trash-2" class="w-3.5 h-3.5"></i>
      </button>
    </div>
  `).join('');

  lucide.createIcons();
}

function showToast(msg) {
  let toast = document.getElementById('appToast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'appToast';
    toast.className = 'fixed bottom-5 right-5 z-50 bg-emerald-600 text-white px-4 py-2.5 rounded-xl shadow-2xl text-xs font-semibold flex items-center space-x-2 transition-all duration-300 transform translate-y-12 opacity-0';
    document.body.appendChild(toast);
  }
  toast.innerHTML = `<i data-lucide="check-circle" class="w-4 h-4"></i><span>${msg}</span>`;
  lucide.createIcons();
  toast.classList.remove('translate-y-12', 'opacity-0');
  setTimeout(() => {
    toast.classList.add('translate-y-12', 'opacity-0');
  }, 3500);
}

// Tab switching for inputs
function switchInputTab(tab) {
  ['doc', 'data', 'workflow'].forEach(t => {
    const btn = document.getElementById(`tabBtn-${t}`);
    const content = document.getElementById(`tabContent-${t}`);
    if (t === tab) {
      btn.className = "px-4 py-2 rounded-t-lg border-b-2 border-indigo-500 text-indigo-400 bg-slate-800/40 flex items-center space-x-1.5";
      content.classList.remove('hidden');
    } else {
      btn.className = "px-4 py-2 rounded-t-lg border-b-2 border-transparent text-slate-400 hover:text-slate-200 flex items-center space-x-1.5";
      content.classList.add('hidden');
    }
  });
}

// API Key Management
function initApiKeyUI() {
  const key = localStorage.getItem('gemini_api_key');
  const btn = document.getElementById('apiKeyBtnLabel');
  if (key) {
    btn.textContent = "Gemini Key (Active)";
    document.getElementById('engineModeIndicator').textContent = "Engine: Gemini 2.5 Flash + Heuristics";
    document.getElementById('geminiApiKeyInput').value = key;
  } else {
    btn.textContent = "Offline Mode (Click to Add Key)";
  }
}

function openApiKeyModal() {
  document.getElementById('apiKeyModal').classList.remove('hidden');
}

function closeApiKeyModal() {
  document.getElementById('apiKeyModal').classList.add('hidden');
}

function saveApiKey() {
  const key = document.getElementById('geminiApiKeyInput').value.trim();
  if (key) {
    localStorage.setItem('gemini_api_key', key);
    initApiKeyUI();
  }
  closeApiKeyModal();
}

function clearApiKey() {
  localStorage.removeItem('gemini_api_key');
  document.getElementById('geminiApiKeyInput').value = '';
  initApiKeyUI();
  closeApiKeyModal();
}

// Template Loading
async function loadTemplate(templateId) {
  try {
    const res = await fetch(`/api/templates/${templateId}`);
    if (!res.ok) throw new Error("Template not found");
    const tmpl = await res.json();

    document.getElementById('projectNameInput').value = tmpl.title;
    document.getElementById('domainSelect').value = tmpl.domain;
    document.getElementById('documentTextInput').value = tmpl.document_text || '';
    document.getElementById('datasetContentInput').value = tmpl.dataset_content || '';
    document.getElementById('workflowContentInput').value = tmpl.workflow_content || '';

    // Automatically run analysis on template load
    runAnalysis();
  } catch (err) {
    console.error("Error loading template:", err);
  }
}

// File Upload Handlers
function handleDocFileUpload(e) {
  const file = e.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = (evt) => {
    document.getElementById('documentTextInput').value = evt.target.result;
    switchInputTab('doc');
  };
  reader.readAsText(file);
}

function handleDataFileUpload(e) {
  const file = e.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = (evt) => {
    document.getElementById('datasetContentInput').value = evt.target.result;
    switchInputTab('data');
  };
  reader.readAsText(file);
}

// Execute Analysis
async function runAnalysis() {
  const runBtn = document.getElementById('runAuditBtn');
  runBtn.disabled = true;
  runBtn.innerHTML = `<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i><span>Auditing System...</span>`;
  lucide.createIcons();

  const payload = {
    project_name: document.getElementById('projectNameInput').value,
    document_text: document.getElementById('documentTextInput').value,
    dataset_content: document.getElementById('datasetContentInput').value,
    dataset_name: "Uploaded Dataset",
    workflow_content: document.getElementById('workflowContentInput').value,
    domain: document.getElementById('domainSelect').value,
    api_key: localStorage.getItem('gemini_api_key') || null
  };

  try {
    const res = await fetch('/api/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      const errData = await res.json();
      throw new Error(errData.detail || "Analysis request failed");
    }

    currentAnalysis = await res.json();
    renderAnalysisView(currentAnalysis);
    // Auto-save project progress
    saveCurrentProjectQuietly(false);
  } catch (err) {
    alert("Audit Error: " + err.message);
  } finally {
    runBtn.disabled = false;
    runBtn.innerHTML = `<i data-lucide="sparkles" class="w-4 h-4"></i><span>Run Deep Intelligence Audit</span>`;
    lucide.createIcons();
  }
}

// Render the Comprehensive View
function renderAnalysisView(data) {
  updateHealthScore(data.health_score);

  // Top Metrics
  document.getElementById('critCountDisplay').textContent = data.summary_stats.critical_count || 0;
  document.getElementById('totalDiscDisplay').textContent = data.discoveries.length;
  document.getElementById('rpiDisplay').textContent = `Aggregate RPI: ${data.risk_priority_index}`;
  document.getElementById('questionCountDisplay').textContent = data.probing_questions.length;
  document.getElementById('unresolvedQuestionBadge').textContent = `${data.probing_questions.filter(q => !q.is_resolved).length} Unanswered`;

  // Engine indicator
  document.getElementById('engineBadge').textContent = data.engine_used.replace(/_/g, ' ').toUpperCase();

  // Executive Summary
  document.getElementById('executiveSummaryText').textContent = data.executive_summary;

  // Category Counts & Bars
  const total = Math.max(1, data.discoveries.length);
  const s = data.summary_stats;

  const setCat = (id, count) => {
    document.getElementById(`catCount${id}`).textContent = count;
    const pct = Math.round((count / total) * 100);
    document.getElementById(`catBar${id}`).style.width = `${pct}%`;
  };

  setCat('Assumptions', s.missing_assumptions_count || 0);
  setCat('Constraints', s.overlooked_constraints_count || 0);
  setCat('Data', s.data_risks_count || 0);
  setCat('Workflow', s.workflow_bottlenecks_count || 0);

  // Render 5x5 Matrix
  renderRiskMatrix(data.discoveries);

  // Render Probing Questions
  renderProbingQuestions(data.probing_questions);

  // Render Discoveries Stream
  renderDiscoveries();
}

function updateHealthScore(score) {
  const display = document.getElementById('healthScoreDisplay');
  const status = document.getElementById('healthScoreStatus');
  const path = document.getElementById('healthCirclePath');

  display.textContent = score;
  const dashoffset = `${score}, 100`;
  path.setAttribute('stroke-dasharray', dashoffset);

  if (score >= 75) {
    path.setAttribute('class', 'text-emerald-500 transition-all duration-700 stroke-current');
    status.textContent = "Robust Resilience";
    status.className = "text-sm font-semibold text-emerald-400 mt-0.5";
  } else if (score >= 50) {
    path.setAttribute('class', 'text-amber-500 transition-all duration-700 stroke-current');
    status.textContent = "Moderate Exposure";
    status.className = "text-sm font-semibold text-amber-400 mt-0.5";
  } else {
    path.setAttribute('class', 'text-rose-500 transition-all duration-700 stroke-current');
    status.textContent = "Critical Vulnerability";
    status.className = "text-sm font-semibold text-rose-400 mt-0.5";
  }
}

// 5x5 Matrix Construction
function initRiskMatrixGrid() {
  const grid = document.getElementById('riskMatrixGrid');
  grid.innerHTML = '';
  // 5 rows (Impact: 5 down to 1), 5 cols (Likelihood: 1 to 5)
  for (let r = 5; r >= 1; r--) {
    for (let c = 1; c <= 5; c++) {
      const cell = document.createElement('div');
      cell.id = `cell-${r}-${c}`;
      cell.className = 'matrix-cell bg-slate-800/40 border border-slate-700/50 p-1 flex flex-wrap gap-1 items-center justify-center';

      // Color tint based on cell risk
      const cellScore = r * c;
      if (cellScore >= 16) cell.classList.add('bg-rose-950/20');
      else if (cellScore >= 10) cell.classList.add('bg-amber-950/20');
      else if (cellScore >= 6) cell.classList.add('bg-yellow-950/20');
      else cell.classList.add('bg-emerald-950/20');

      grid.appendChild(cell);
    }
  }
}

function renderRiskMatrix(discoveries) {
  // Clear all dots from cells
  for (let r = 1; r <= 5; r++) {
    for (let c = 1; c <= 5; c++) {
      const cell = document.getElementById(`cell-${r}-${c}`);
      if (cell) cell.innerHTML = '';
    }
  }

  discoveries.forEach((d) => {
    const imp = Math.min(5, Math.max(1, d.impact_score));
    const lik = Math.min(5, Math.max(1, d.likelihood_score));
    const cell = document.getElementById(`cell-${imp}-${lik}`);
    if (cell) {
      const dot = document.createElement('div');
      dot.className = 'matrix-dot cursor-pointer';

      if (d.severity === 'critical') dot.classList.add('bg-rose-500', 'ring-2', 'ring-rose-400/50');
      else if (d.severity === 'high') dot.classList.add('bg-amber-500');
      else if (d.severity === 'medium') dot.classList.add('bg-yellow-400');
      else dot.classList.add('bg-emerald-400');

      if (d.status === 'resolved') {
        dot.classList.add('opacity-30', 'line-through');
      }

      dot.title = `[${d.severity.toUpperCase()}] ${d.title} (RPN: ${d.rpn})`;
      dot.onclick = () => scrollToDiscovery(d.id);
      cell.appendChild(dot);
    }
  });
}

function scrollToDiscovery(id) {
  const card = document.getElementById(`card-${id}`);
  if (card) {
    card.scrollIntoView({ behavior: 'smooth', block: 'center' });
    card.classList.add('ring-2', 'ring-indigo-500', 'pulse-glow');
    setTimeout(() => {
      card.classList.remove('ring-2', 'ring-indigo-500', 'pulse-glow');
    }, 2500);
  }
}

// Probing Questions (Unknown Unknowns)
function renderProbingQuestions(questions) {
  const container = document.getElementById('probingQuestionsContainer');
  container.innerHTML = '';

  if (!questions || questions.length === 0) {
    container.innerHTML = `<div class="col-span-2 text-center text-xs text-slate-500 py-4">No unasked probing questions identified for this scope.</div>`;
    return;
  }

  questions.forEach((q, idx) => {
    const card = document.createElement('div');
    card.className = `p-4 rounded-xl border transition ${
      q.is_resolved 
        ? 'bg-dark-950/60 border-emerald-500/30' 
        : 'bg-dark-850 border-slate-800 hover:border-slate-700'
    }`;

    let optionsHtml = '';
    if (q.suggested_options && q.suggested_options.length > 0) {
      optionsHtml = `
        <div class="mt-2 space-y-1.5">
          <div class="text-[11px] font-medium text-slate-400">Recommended Strategic Stances:</div>
          ${q.suggested_options.map((opt, oIdx) => `
            <button onclick="selectQuestionOption('${q.id}', '${encodeURIComponent(opt)}')" class="w-full text-left text-xs px-2.5 py-1.5 rounded-lg bg-dark-900 border border-slate-700/70 hover:border-indigo-500 hover:text-indigo-200 transition text-slate-300">
              👉 ${opt}
            </button>
          `).join('')}
        </div>
      `;
    }

    card.innerHTML = `
      <div class="flex items-start justify-between gap-2">
        <div class="flex items-center space-x-2">
          <span class="text-xs font-bold text-indigo-400">Q${idx + 1}</span>
          <h4 class="text-xs font-semibold text-slate-200">${q.question}</h4>
        </div>
        ${q.is_resolved 
          ? `<span class="text-[10px] px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-medium">Addressed</span>`
          : `<span class="text-[10px] px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 font-medium">Open</span>`
        }
      </div>

      <p class="text-xs text-slate-400 mt-2"><strong class="text-slate-300">Why It Matters:</strong> ${q.why_it_matters}</p>

      ${q.user_answer 
        ? `<div class="mt-3 p-2.5 rounded-lg bg-emerald-950/20 border border-emerald-500/20 text-xs text-emerald-300">
             <strong>Decision Formulated:</strong> ${q.user_answer}
           </div>`
        : optionsHtml
      }
    `;

    container.appendChild(card);
  });
}

async function selectQuestionOption(questionId, encodedOption) {
  const answer = decodeURIComponent(encodedOption);
  try {
    const res = await fetch('/api/answer-question', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question_id: questionId, answer: answer })
    });
    const result = await res.json();
    if (result.success) {
      // Update local state
      const q = currentAnalysis.probing_questions.find(item => item.id === questionId);
      if (q) {
        q.user_answer = answer;
        q.is_resolved = true;
      }
      currentAnalysis.health_score = result.health_score;
      currentAnalysis.risk_priority_index = result.risk_priority_index;
      renderAnalysisView(currentAnalysis);
      saveCurrentProjectQuietly(false);
    }
  } catch (err) {
    alert("Failed to submit question answer: " + err.message);
  }
}

// Discovery Cards Stream & Filtering
function setCategoryFilter(cat) {
  activeCategoryFilter = cat;
  ['all', 'missing_assumption', 'overlooked_constraint', 'data_risk', 'workflow_bottleneck'].forEach(c => {
    const btn = document.getElementById(`filterCat-${c}`);
    if (btn) {
      if (c === cat) {
        btn.className = "px-3 py-1.5 rounded-lg bg-indigo-600 text-white transition";
      } else {
        btn.className = "px-3 py-1.5 rounded-lg bg-dark-850 border border-slate-800 text-slate-400 hover:text-white transition";
      }
    }
  });
  renderDiscoveries();
}

function applyFilters() {
  activeSeverityFilter = document.getElementById('severityFilter').value;
  searchQuery = document.getElementById('searchFilterInput').value.toLowerCase().trim();
  renderDiscoveries();
}

function renderDiscoveries() {
  const container = document.getElementById('discoveriesContainer');
  container.innerHTML = '';

  if (!currentAnalysis || !currentAnalysis.discoveries || currentAnalysis.discoveries.length === 0) {
    container.innerHTML = `<div class="text-center text-xs text-slate-500 py-12">No discoveries recorded yet. Run an audit to uncover blind spots.</div>`;
    return;
  }

  let filtered = currentAnalysis.discoveries.filter(d => {
    if (activeCategoryFilter !== 'all' && d.category !== activeCategoryFilter) return false;
    if (activeSeverityFilter !== 'all') {
      if (activeSeverityFilter === 'high' && (d.severity !== 'high' && d.severity !== 'critical')) return false;
      else if (activeSeverityFilter !== 'high' && d.severity !== activeSeverityFilter) return false;
    }
    if (searchQuery) {
      const match = d.title.toLowerCase().includes(searchQuery) ||
                    d.summary.toLowerCase().includes(searchQuery) ||
                    d.evidence.toLowerCase().includes(searchQuery) ||
                    d.recommendation.toLowerCase().includes(searchQuery);
      if (!match) return false;
    }
    return true;
  });

  if (filtered.length === 0) {
    container.innerHTML = `<div class="text-center text-xs text-slate-500 py-8">No findings matching active filters.</div>`;
    return;
  }

  filtered.forEach(d => {
    const card = document.createElement('div');
    card.id = `card-${d.id}`;
    card.className = `bg-dark-900 border rounded-2xl p-5 space-y-4 transition ${
      d.status === 'resolved' 
        ? 'border-emerald-500/30 opacity-70 bg-dark-950' 
        : (d.severity === 'critical' ? 'border-rose-500/40 hover:border-rose-500/60' : 'border-slate-800 hover:border-slate-700')
    }`;

    // Severity badge color
    let sevBadge = `<span class="px-2 py-0.5 rounded text-[11px] font-bold bg-slate-800 text-slate-300">LOW</span>`;
    if (d.severity === 'critical') sevBadge = `<span class="px-2.5 py-0.5 rounded text-[11px] font-bold bg-rose-500/10 text-rose-400 border border-rose-500/30">🚨 CRITICAL</span>`;
    else if (d.severity === 'high') sevBadge = `<span class="px-2.5 py-0.5 rounded text-[11px] font-bold bg-amber-500/10 text-amber-400 border border-amber-500/30">⚠️ HIGH</span>`;
    else if (d.severity === 'medium') sevBadge = `<span class="px-2.5 py-0.5 rounded text-[11px] font-bold bg-yellow-500/10 text-yellow-400 border border-yellow-500/30">⚡ MEDIUM</span>`;

    // Category format
    const categoryPretty = d.category.replace(/_/g, ' ').toUpperCase();

    // Action checklist HTML
    let actionItemsHtml = '';
    if (d.action_items && d.action_items.length > 0) {
      actionItemsHtml = `
        <div class="mt-3 space-y-1.5">
          <div class="text-[11px] font-semibold text-slate-300 uppercase tracking-wider">Actionable Remediation Checklist:</div>
          <div class="space-y-1">
            ${d.action_items.map((item, aIdx) => `
              <label class="flex items-start space-x-2 text-xs text-slate-300 cursor-pointer">
                <input type="checkbox" class="mt-0.5 rounded bg-dark-950 border-slate-700 text-indigo-500 focus:ring-0">
                <span>${item}</span>
              </label>
            `).join('')}
          </div>
        </div>
      `;
    }

    // Mitigation code block HTML
    let codeHtml = '';
    if (d.mitigation_code) {
      codeHtml = `
        <div class="mt-3">
          <div class="flex items-center justify-between text-[11px] text-slate-400 mb-1">
            <span class="font-semibold uppercase tracking-wider">Defensive Guardrail Snippet:</span>
            <button onclick="copySnippet('${d.id}')" class="text-indigo-400 hover:text-indigo-300 flex items-center space-x-1">
              <i data-lucide="copy" class="w-3 h-3"></i>
              <span id="copyBtn-${d.id}">Copy Code</span>
            </button>
          </div>
          <pre id="codeSnippet-${d.id}" class="bg-dark-950 border border-slate-800 rounded-xl p-3 text-xs font-mono text-emerald-400 overflow-x-auto leading-relaxed"><code>${escapeHtml(d.mitigation_code)}</code></pre>
        </div>
      `;
    }

    // Notes HTML
    let notesHtml = '';
    if (d.user_notes) {
      notesHtml = `
        <div class="mt-2 text-xs p-2.5 rounded-lg bg-indigo-950/30 border border-indigo-500/20 text-indigo-300">
          <strong>Implementation Note:</strong> ${d.user_notes}
        </div>
      `;
    }

    card.innerHTML = `
      <!-- Header row -->
      <div class="flex flex-wrap items-start justify-between gap-2 border-b border-slate-800/80 pb-3">
        <div class="space-y-1">
          <div class="flex flex-wrap items-center gap-2">
            ${sevBadge}
            <span class="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-400 font-medium">${categoryPretty}</span>
            <span class="text-xs px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 font-mono">RPN: ${d.rpn} (Imp:${d.impact_score} × Lik:${d.likelihood_score} × Det:${d.detectability_score})</span>
            ${d.cognitive_bias ? `<span class="text-xs text-amber-400 italic">Bias: ${d.cognitive_bias}</span>` : ''}
          </div>
          <h3 class="text-sm font-bold text-slate-100">${d.title}</h3>
          <div class="text-xs text-slate-500 flex items-center space-x-1">
            <i data-lucide="map-pin" class="w-3 h-3"></i>
            <span>${d.location}</span>
          </div>
        </div>

        <!-- Status & Actions -->
        <div class="flex items-center space-x-2">
          <button onclick="toggleItemStatus('${d.id}')" class="px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
            d.status === 'resolved' 
              ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 hover:bg-emerald-500/30' 
              : 'bg-dark-800 text-slate-300 border border-slate-700 hover:border-slate-600'
          }">
            ${d.status === 'resolved' ? '✓ Mitigated' : 'Mark Mitigated'}
          </button>
          <button onclick="openNotesModal('${d.id}', '${encodeURIComponent(d.title)}')" class="px-2.5 py-1.5 rounded-lg text-xs bg-dark-800 text-slate-400 hover:text-white border border-slate-700" title="Add Implementation Note">
            <i data-lucide="file-edit" class="w-3.5 h-3.5"></i>
          </button>
        </div>
      </div>

      <!-- Evidence Grounding Callout -->
      <div class="evidence-quote-box p-3 rounded-r-xl">
        <div class="text-[10px] uppercase font-bold text-indigo-400 tracking-wider mb-0.5 flex items-center space-x-1">
          <i data-lucide="quote" class="w-3 h-3"></i>
          <span>Evidence Grounding in Artifact</span>
        </div>
        <p class="text-xs italic text-slate-300 font-mono">"${d.evidence}"</p>
      </div>

      <!-- Core Description -->
      <div class="text-xs text-slate-300 leading-relaxed">
        <p><strong class="text-slate-200">The Blind Spot:</strong> ${d.summary}</p>
      </div>

      <!-- Failure Scenario Blast Radius -->
      <div class="bg-rose-950/10 border border-rose-500/20 rounded-xl p-3 text-xs text-rose-300/90 leading-relaxed">
        <div class="font-semibold text-rose-400 flex items-center space-x-1.5 mb-1">
          <i data-lucide="flame" class="w-3.5 h-3.5"></i>
          <span>Production Blast Radius Scenario</span>
        </div>
        <p>${d.failure_scenario}</p>
      </div>

      <!-- Recommendation -->
      <div class="bg-indigo-950/15 border border-indigo-500/20 rounded-xl p-3 text-xs text-indigo-200/90 leading-relaxed">
        <div class="font-semibold text-indigo-400 flex items-center space-x-1.5 mb-1">
          <i data-lucide="shield-check" class="w-3.5 h-3.5"></i>
          <span>Evidence-Based Remediation</span>
        </div>
        <p>${d.recommendation}</p>
      </div>

      ${actionItemsHtml}
      ${codeHtml}
      ${notesHtml}
    `;

    container.appendChild(card);
  });

  lucide.createIcons();
}

// Item Resolution Toggle
async function toggleItemStatus(id) {
  const d = currentAnalysis.discoveries.find(item => item.id === id);
  if (!d) return;

  const newStatus = d.status === 'resolved' ? 'open' : 'resolved';
  try {
    const res = await fetch('/api/resolve-item', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ discovery_id: id, status: newStatus })
    });
    const result = await res.json();
    if (result.success) {
      d.status = newStatus;
      currentAnalysis.health_score = result.health_score;
      currentAnalysis.risk_priority_index = result.risk_priority_index;
      renderAnalysisView(currentAnalysis);
      saveCurrentProjectQuietly(false);
    }
  } catch (err) {
    alert("Failed to update status: " + err.message);
  }
}

// Implementation Notes Modal
function openNotesModal(id, encodedTitle) {
  currentTargetDiscoveryId = id;
  const title = decodeURIComponent(encodedTitle);
  document.getElementById('notesModalTitle').textContent = `Document Mitigation: ${title}`;
  const d = currentAnalysis.discoveries.find(item => item.id === id);
  document.getElementById('notesModalInput').value = d && d.user_notes ? d.user_notes : '';
  document.getElementById('notesModal').classList.remove('hidden');
}

function closeNotesModal() {
  document.getElementById('notesModal').classList.add('hidden');
}

async function saveItemNotes() {
  const notes = document.getElementById('notesModalInput').value.trim();
  if (currentTargetDiscoveryId) {
    try {
      const res = await fetch('/api/resolve-item', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          discovery_id: currentTargetDiscoveryId,
          status: 'resolved',
          notes: notes
        })
      });
      const result = await res.json();
      if (result.success) {
        const d = currentAnalysis.discoveries.find(item => item.id === currentTargetDiscoveryId);
        if (d) {
          d.status = 'resolved';
          d.user_notes = notes;
        }
        currentAnalysis.health_score = result.health_score;
        currentAnalysis.risk_priority_index = result.risk_priority_index;
        renderAnalysisView(currentAnalysis);
        saveCurrentProjectQuietly(false);
      }
    } catch (err) {
      alert("Failed to record mitigation: " + err.message);
    }
  }
  closeNotesModal();
}

// Copy Code Snippet
function copySnippet(id) {
  const codeEl = document.getElementById(`codeSnippet-${id}`);
  if (codeEl) {
    navigator.clipboard.writeText(codeEl.innerText);
    const btn = document.getElementById(`copyBtn-${id}`);
    btn.textContent = "Copied!";
    setTimeout(() => {
      btn.textContent = "Copy Code";
    }, 2000);
  }
}

// Export Dropdown & Functions
function toggleExportMenu() {
  const menu = document.getElementById('exportMenu');
  menu.classList.toggle('hidden');
}

document.addEventListener('click', (e) => {
  const wrapper = document.getElementById('exportDropdownWrapper');
  if (wrapper && !wrapper.contains(e.target)) {
    document.getElementById('exportMenu').classList.add('hidden');
  }
});

async function exportReport(format) {
  if (!currentAnalysis) {
    alert("Please run or load an analysis first.");
    return;
  }
  document.getElementById('exportMenu').classList.add('hidden');

  if (format === 'markdown') {
    const res = await fetch('/api/export-report/markdown', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(currentAnalysis)
    });
    const md = await res.text();
    downloadFile(md, `${currentAnalysis.project_name.replace(/\s+/g, '_')}_BlindSpot_Audit.md`, 'text/markdown');
  } else if (format === 'html') {
    const res = await fetch('/api/export-report/html', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(currentAnalysis)
    });
    const html = await res.text();
    const printWindow = window.open('', '_blank');
    printWindow.document.write(html);
    printWindow.document.close();
    printWindow.focus();
  } else if (format === 'json') {
    const jsonStr = JSON.stringify(currentAnalysis, null, 2);
    downloadFile(jsonStr, `${currentAnalysis.project_name.replace(/\s+/g, '_')}_Audit.json`, 'application/json');
  }
}

function downloadFile(content, fileName, mimeType) {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = fileName;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}
