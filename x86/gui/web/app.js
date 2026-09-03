(() => {
  "use strict";

  const DEFAULT_STEPS = [
    { id: "welcome", title: "시작", heading: "26x86에 오신 것을 환영합니다", desc: "오래된 Mac에서 최신 macOS를 사용할 수 있도록 단계별로 안내합니다." },
    { id: "detect", title: "1. 내 Mac 확인", heading: "내 Mac 확인", desc: "하드웨어 정보를 확인합니다." },
    { id: "build", title: "2. 패치 생성", heading: "패치 생성", desc: "OpenCore EFI를 만듭니다." },
    { id: "patch", title: "3. 설치·패치", heading: "설치·패치", desc: "EFI 설치와 루트 패치를 진행합니다." },
    { id: "done", title: "4. 완료", heading: "설정이 완료되었습니다", desc: "필요하면 루트 패치를 적용하세요." },
  ];

  const state = {
    steps: DEFAULT_STEPS.slice(),
    currentStep: 0,
    appInfo: null,
    detect: null,
    macos: null,
    patchSummary: "패치 정보를 불러오는 중…",
    canBuild: true,
    buildCompleted: false,
    busy: false,
    bridgeReady: false,
  };

  const els = {
    stepper: document.getElementById("stepper"),
    stepContent: document.getElementById("step-content"),
    btnPrev: document.getElementById("btn-prev"),
    btnNext: document.getElementById("btn-next"),
    progressBar: document.getElementById("progress-bar"),
    stepCounter: document.getElementById("step-counter"),
    statusText: document.getElementById("status-text"),
    versionText: document.getElementById("version-text"),
    appTitle: document.getElementById("app-title"),
    appSubtitle: document.getElementById("app-subtitle"),
    logo: document.getElementById("logo"),
    logoFallback: document.getElementById("logo-fallback"),
    toastHost: document.getElementById("toast-host"),
    settingsDialog: document.getElementById("settings-dialog"),
    settingAnalytics: document.getElementById("setting-analytics"),
    settingVerbose: document.getElementById("setting-verbose"),
  };

  const QT_BRIDGE_METHODS = [
    "get_app_info",
    "get_steps",
    "detect",
    "get_macos_choices",
    "set_target_os",
    "get_patch_status",
    "get_status",
    "get_settings",
    "save_settings",
    "host_can_build",
    "launch_wx_action",
    "reveal_log",
    "open_guide",
  ];

  function promisifyQtBridge(bridge) {
    if (!bridge || bridge.__qtWrapped) {
      return bridge;
    }
    const wrapped = { __qtWrapped: true };
    QT_BRIDGE_METHODS.forEach((name) => {
      wrapped[name] = function (...args) {
        return new Promise((resolve, reject) => {
          try {
            const fn = bridge[name];
            if (typeof fn !== "function") {
              reject(new Error(`${name} is not available`));
              return;
            }
            fn.apply(bridge, args.concat([(result) => resolve(result)]));
          } catch (err) {
            reject(err);
          }
        });
      };
    });
    return wrapped;
  }

  function getBridgeApi() {
    if (window.pywebview && window.pywebview.api) {
      return window.pywebview.api;
    }
    return null;
  }

  function connectQtWebChannel() {
    if (getBridgeApi()) {
      return;
    }
    if (typeof QWebChannel === "undefined" || typeof qt === "undefined" || !qt.webChannelTransport) {
      return;
    }
    new QWebChannel(qt.webChannelTransport, (channel) => {
      if (channel.objects && channel.objects.bridge) {
        window.pywebview = { api: promisifyQtBridge(channel.objects.bridge) };
        window.dispatchEvent(new Event("pywebviewready"));
      }
    });
  }

  function api(method, ...args) {
    const surface = getBridgeApi();
    if (surface && typeof surface[method] === "function") {
      const result = surface[method](...args);
      return result && typeof result.then === "function" ? result : Promise.resolve(result);
    }
    return Promise.reject(new Error("Python bridge API unavailable"));
  }

  function whenBridgeReady(callback) {
    if (getBridgeApi()) {
      callback();
      return;
    }

    connectQtWebChannel();

    let attempts = 0;
    const maxAttempts = 200;
    const timer = window.setInterval(() => {
      attempts += 1;
      connectQtWebChannel();
      if (getBridgeApi()) {
        window.clearInterval(timer);
        callback();
      } else if (attempts >= maxAttempts) {
        window.clearInterval(timer);
        const banner = document.getElementById("boot-banner");
        if (banner) {
          banner.innerHTML = "Python 브릿지에 아직 연결되지 않았습니다. 창은 정상입니다.";
        }
        setStatus("브릿지 대기 시간 초과");
        toast("Python bridge API 연결 실패 — UI는 표시됩니다", "error");
        try { bindGlobalActions(); renderStepContent(); } catch (_) {}
      }
    }, 50);

    window.addEventListener(
      "pywebviewready",
      () => {
        window.clearInterval(timer);
        callback();
      },
      { once: true }
    );
  }

  function setStatus(text) {
    els.statusText.textContent = text || "준비됨";
  }

  function toast(message, kind = "info") {
    const node = document.createElement("div");
    node.className = `toast${kind === "error" ? " error" : ""}`;
    node.textContent = message;
    els.toastHost.appendChild(node);
    setTimeout(() => node.remove(), 3200);
  }

  function escapeHtml(value) {
    return String(value ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function infoRow(label, value) {
    return `<div class="info-row"><span class="label">${escapeHtml(label)}</span><span class="value">${escapeHtml(value || "—")}</span></div>`;
  }

  function renderStepper() {
    els.stepper.innerHTML = state.steps
      .map(
        (step, index) =>
          `<button type="button" class="step-btn${index === state.currentStep ? " active" : ""}${index < state.currentStep ? " done" : ""}" data-step="${index}">${escapeHtml(step.title)}</button>`
      )
      .join("");

    els.stepper.querySelectorAll(".step-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        const idx = Number(btn.dataset.step);
        if (!Number.isNaN(idx)) goToStep(idx);
      });
    });

    const total = state.steps.length || 1;
    const pct = ((state.currentStep + 1) / total) * 100;
    els.progressBar.style.width = `${pct}%`;
    els.stepCounter.textContent = `${state.currentStep + 1} / ${total}`;
    els.btnPrev.disabled = state.currentStep <= 0 || state.busy;
    els.btnNext.disabled = state.currentStep >= total - 1 || state.busy;
  }

  function renderWelcome(step) {
    return `
      <div class="welcome-hero">
        <div class="hero-icon">26</div>
        <h2>${escapeHtml(step.heading)}</h2>
        <p class="lead">${escapeHtml(step.desc)}</p>
        <p class="lead">버전 ${escapeHtml(state.appInfo?.version || "")} · ${escapeHtml(state.appInfo?.bundle_id || "")}</p>
      </div>
      <div class="actions">
        <button type="button" class="btn primary" id="action-start">시작하기</button>
        <button type="button" class="btn secondary" id="action-guide">사용 설명서</button>
      </div>
    `;
  }

  function renderDetect(step) {
    const d = state.detect || {};
    const platformNote = !d.host_is_mac && d.macos_only_note
      ? `<div class="note">${escapeHtml(d.macos_only_note)}</div>`
      : "";
    const modelLabel = d.host_is_mac === false ? "호스트" : "Mac 모델";
    const osLabel = d.host_is_mac === false ? "호스트 OS" : "현재 macOS";
    return `
      <h2>${escapeHtml(step.heading)}</h2>
      <p class="lead">${escapeHtml(step.desc)}</p>
      ${platformNote}
      <div class="info-grid">
        ${infoRow(modelLabel, d.model)}
        ${infoRow("제품명", d.marketing_name)}
        ${infoRow("프로세서", d.cpu || "확인됨")}
        ${infoRow(osLabel, `${d.os_version || "—"} (${d.os_build || "—"})`)}
      </div>
      <div class="actions">
        <button type="button" class="btn secondary" id="action-redetect">다시 확인</button>
        <button type="button" class="btn secondary" id="action-model">모델 변경</button>
      </div>
    `;
  }

  function renderBuild(step) {
    const macos = state.macos || { choices: [], selected_kernel: null };
    const selected = macos.choices.find((c) => c.kernel === macos.selected_kernel) || macos.choices[0];
    const warn = !state.canBuild
      ? `<div class="note">${escapeHtml(
          state.buildMessage ||
            state.appInfo?.macos_only_message ||
            "이 Mac에서는 EFI를 만들 수 없습니다. 다른 지원 Mac에서 실행하거나 고급 모드 설정을 확인해 주세요."
        )}</div>`
      : "";
    const options = macos.choices
      .map(
        (c) =>
          `<option value="${c.kernel}"${c.kernel === macos.selected_kernel ? " selected" : ""}>${escapeHtml(c.label)}</option>`
      )
      .join("");

    return `
      <h2>${escapeHtml(step.heading)}</h2>
      <p class="lead">${escapeHtml(step.desc)}</p>
      ${warn}
      <label for="macos-select"><strong>설치할 macOS</strong></label>
      <select id="macos-select" class="field">${options}</select>
      <div class="info-grid">
        ${infoRow("현재 실행 중", macos.current_marketing || "—")}
        ${infoRow("선택한 버전", selected?.label || "—")}
        ${macos.recommended ? infoRow("Apple 공식 지원", macos.recommended) : ""}
        ${infoRow("대상 Mac", state.detect?.marketing_name || state.detect?.model || "—")}
      </div>
      <div class="actions">
        <button type="button" class="btn primary" id="action-build"${state.canBuild ? "" : " disabled"}>패치 생성 시작</button>
      </div>
    `;
  }

  function renderPatch(step) {
    const needBuild = !state.buildCompleted
      ? `<div class="note">먼저 패치(EFI)를 생성해 주세요. 생성 후 EFI 설치와 루트 패치를 진행할 수 있습니다.</div>`
      : "";
    return `
      <h2>${escapeHtml(step.heading)}</h2>
      <p class="lead">${escapeHtml(step.desc)}</p>
      ${needBuild}
      <div class="patch-summary" id="patch-summary">${escapeHtml(state.patchSummary)}</div>
      <div class="actions">
        <button type="button" class="btn primary" id="action-install">EFI 설치 시작</button>
        <button type="button" class="btn secondary" id="action-patch">루트 패치 적용</button>
        <button type="button" class="btn secondary" id="action-unpatch">루트 패치 되돌리기</button>
      </div>
    `;
  }

  function renderDone(step) {
    return `
      <div class="welcome-hero">
        <div class="done-check">✓</div>
        <h2>${escapeHtml(step.heading)}</h2>
        <p class="lead">${escapeHtml(step.desc)}</p>
      </div>
      <div class="info-grid">
        ${infoRow("Mac 모델", state.detect?.model)}
        ${infoRow("macOS", state.detect?.os_version)}
      </div>
      <div class="actions">
        <button type="button" class="btn secondary" id="action-log">로그 파일 보기</button>
        <button type="button" class="btn secondary" id="action-advanced" ${state.appInfo?.advanced_enabled ? "" : "disabled"}>고급 모드</button>
        <button type="button" class="btn primary" id="action-finish">종료</button>
      </div>
    `;
  }

  function renderStepContent() {
    const step = state.steps[state.currentStep];
    if (!step) return;

    const builders = {
      welcome: renderWelcome,
      detect: renderDetect,
      build: renderBuild,
      patch: renderPatch,
      done: renderDone,
    };

    const html = (builders[step.id] || renderWelcome)(step);
    els.stepContent.innerHTML = html;
    bindStepActions(step.id);
    setStatus(step.title);
    renderStepper();
  }

  async function bindStepActions(stepId) {
    const bind = (id, handler) => {
      const node = document.getElementById(id);
      if (node) node.addEventListener("click", handler);
    };

    if (stepId === "welcome") {
      bind("action-start", () => goToStep(1));
      bind("action-guide", () => api("open_guide").catch(() => toast("도움말을 열 수 없습니다.", "error")));
    }

    if (stepId === "detect") {
      bind("action-redetect", async () => {
        setStatus("Mac 정보를 확인하는 중…");
        try {
          const result = await api("detect", true);
          state.detect = result.detect;
          renderStepContent();
          toast("Mac 정보 확인 완료");
        } catch (err) {
          toast(String(err.message || err), "error");
        } finally {
          setStatus("준비됨");
        }
      });
      bind("action-model", async () => {
        const result = await api("launch_wx_action", "model_change");
        if (!result.ok) toast(result.error || "모델 변경을 시작할 수 없습니다.", "error");
        else toast("모델 선택 창을 열었습니다.");
      });
    }

    if (stepId === "build") {
      const select = document.getElementById("macos-select");
      if (select) {
        select.addEventListener("change", async () => {
          const kernel = Number(select.value);
          const result = await api("set_target_os", kernel);
          if (result.ok) {
            state.macos.selected_kernel = kernel;
            renderStepContent();
          }
        });
      }
      bind("action-build", async () => {
        setStatus("패치 생성 창을 여는 중…");
        const result = await api("launch_wx_action", "build");
        if (!result.ok) {
          toast(result.error || "패치 생성을 시작할 수 없습니다.", "error");
        } else {
          state.buildCompleted = true;
          toast("패치 생성 창을 열었습니다.");
        }
        setStatus("준비됨");
      });
    }

    if (stepId === "patch") {
      bind("action-install", async () => {
        const result = await api("launch_wx_action", "install");
        if (!result.ok) toast(result.error || "EFI 설치를 시작할 수 없습니다.", "error");
        else toast("EFI 설치 창을 열었습니다.");
      });
      bind("action-patch", async () => {
        const result = await api("launch_wx_action", "patch");
        if (!result.ok) toast(result.error || "루트 패치를 시작할 수 없습니다.", "error");
        else toast("루트 패치 창을 열었습니다.");
      });
      bind("action-unpatch", async () => {
        const result = await api("launch_wx_action", "unpatch");
        if (!result.ok) toast(result.error || "되돌리기를 시작할 수 없습니다.", "error");
        else toast("루트 패치 되돌리기 창을 열었습니다.");
      });
    }

    if (stepId === "done") {
      bind("action-log", () => api("reveal_log"));
      bind("action-advanced", async () => {
        const result = await api("launch_wx_action", "advanced");
        if (!result.ok) toast(result.error || "고급 모드를 열 수 없습니다.", "error");
      });
      bind("action-finish", () => window.close());
    }
  }

  function goToStep(index) {
    if (index < 0 || index >= state.steps.length) return;
    state.currentStep = index;
    renderStepContent();
    if (state.steps[index]?.id === "patch") {
      refreshPatchStatus();
    }
  }

  async function refreshPatchStatus() {
    const summaryEl = document.getElementById("patch-summary");
    if (summaryEl) summaryEl.innerHTML = `<span class="spinner"></span>불러오는 중…`;
    try {
      const result = await api("get_patch_status");
      state.patchSummary = result.summary || "패치 정보 없음";
      if (summaryEl) summaryEl.textContent = state.patchSummary;
    } catch (err) {
      state.patchSummary = "패치 정보를 불러오지 못했습니다.";
      if (summaryEl) summaryEl.textContent = state.patchSummary;
    }
  }

  async function loadInitialData() {
    const [appInfo, steps, detectResult, macos, buildCheck, status] = await Promise.all([
      api("get_app_info"),
      api("get_steps"),
      api("detect", false),
      api("get_macos_choices"),
      api("host_can_build"),
      api("get_status"),
    ]);

    state.appInfo = appInfo;
    state.steps = steps;
    state.detect = detectResult.detect;
    state.macos = macos;
    state.canBuild = !!buildCheck.can_build;
    state.buildMessage = buildCheck.message || null;
    state.buildCompleted = !!status.build_completed;

    els.appTitle.textContent = appInfo.app_name;
    els.appSubtitle.textContent = appInfo.bundle_id;
    els.versionText.textContent = `v${appInfo.version}`;

    if (appInfo.logo_url) {
      els.logo.src = appInfo.logo_url;
      els.logo.hidden = false;
      els.logoFallback.hidden = true;
    }

    state.bridgeReady = true;
    const banner = document.getElementById("boot-banner");
    if (banner) banner.remove();
    renderStepContent();
    setStatus(appInfo.status_ready);
  }

  async function openSettings() {
    try {
      const result = await api("get_settings");
      const settings = result.settings || {};
      els.settingAnalytics.checked = !!settings.analytics;
      els.settingVerbose.checked = !!settings.verbose_logging;
      els.settingsDialog.showModal();
    } catch (err) {
      toast("설정을 불러올 수 없습니다.", "error");
    }
  }

  async function saveSettings(event) {
    event.preventDefault();
    try {
      const result = await api("save_settings", {
        analytics: els.settingAnalytics.checked,
        verbose_logging: els.settingVerbose.checked,
      });
      if (!result.ok) throw new Error(result.error || "save failed");
      els.settingsDialog.close();
      toast("설정을 저장했습니다.");
    } catch (err) {
      toast(String(err.message || err), "error");
    }
  }

  function bindGlobalActions() {
    els.btnPrev.addEventListener("click", () => goToStep(state.currentStep - 1));
    els.btnNext.addEventListener("click", () => goToStep(state.currentStep + 1));
    document.getElementById("btn-settings").addEventListener("click", openSettings);
    document.getElementById("btn-help").addEventListener("click", () => api("open_guide"));
    document.getElementById("settings-cancel").addEventListener("click", () => els.settingsDialog.close());
    document.getElementById("settings-save").addEventListener("click", saveSettings);

    document.addEventListener("keydown", (event) => {
      if (event.key === "ArrowRight" && (event.metaKey || event.ctrlKey)) {
        goToStep(Math.min(state.steps.length - 1, state.currentStep + 1));
      }
      if (event.key === "ArrowLeft" && (event.metaKey || event.ctrlKey)) {
        goToStep(Math.max(0, state.currentStep - 1));
      }
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    try { renderStepper(); setStatus("UI 로딩 중…"); } catch (_) {}
  });

  whenBridgeReady(() => {
    bindGlobalActions();
    loadInitialData().catch((err) => {
      toast(String(err.message || err), "error");
      const banner = document.getElementById("boot-banner");
      if (banner) banner.textContent = "Python 데이터를 불러오지 못했습니다. UI 골격은 표시됩니다.";
      setStatus("데이터 로드 실패");
      renderStepContent();
    });
  });
})();
