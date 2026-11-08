/**
 * Agent SDK Builder Lab - Main Interactive Video & Simulator Application
 */

class InteractiveVideoApp {
  constructor() {
    this.data = window.AGENT_LAB_DATA;
    this.currentTime = 0;
    this.totalDuration = this.data.totalDuration;
    this.isPlaying = false;
    this.playbackRate = 1.0;
    this.captionsVisible = true;
    this.activeScenario = null;
    this.lastFrameTime = performance.now();

    this.renderer = new CanvasArchitectureRenderer("architecture-canvas");
    this.audio = new AudioNarrationEngine();
    this.recorder = new VideoExportEngine(this.renderer.canvas);

    this.initDOM();
    this.initEvents();
    this.initKeyboard();

    // Start render loop
    requestAnimationFrame((t) => this.loop(t));

    // Initial state
    this.updateTimelineUI();
    this.updateChapterUI();
  }

  initDOM() {
    this.dom = {
      playPauseBtn: document.getElementById("btn-play-pause"),
      playIcon: document.getElementById("play-icon"),
      pauseIcon: document.getElementById("pause-icon"),
      prevChapterBtn: document.getElementById("btn-prev-chapter"),
      nextChapterBtn: document.getElementById("btn-next-chapter"),
      replayBtn: document.getElementById("btn-replay"),
      timelineContainer: document.getElementById("timeline-container"),
      timelineProgress: document.getElementById("timeline-progress"),
      timelineHandle: document.getElementById("timeline-handle"),
      timelineTooltip: document.getElementById("timeline-tooltip"),
      timeCurrent: document.getElementById("time-current"),
      timeTotal: document.getElementById("time-total"),
      speedSelect: document.getElementById("speed-select"),
      muteBtn: document.getElementById("btn-mute"),
      volumeHighIcon: document.getElementById("volume-high-icon"),
      volumeMutedIcon: document.getElementById("volume-muted-icon"),
      captionsBtn: document.getElementById("btn-captions"),
      captionsHud: document.getElementById("captions-hud"),
      captionChapter: document.getElementById("caption-chapter"),
      captionStatus: document.getElementById("caption-status-text"),
      captionBody: document.getElementById("caption-body"),
      cameraBtn: document.getElementById("btn-camera-mode"),
      fullscreenBtn: document.getElementById("btn-fullscreen"),
      recordBtn: document.getElementById("btn-record"),
      recordText: document.getElementById("record-text"),
      scenarioSelect: document.getElementById("scenario-select"),
      inspectorDrawer: document.getElementById("inspector-drawer"),
      closeInspectorBtn: document.getElementById("btn-close-inspector"),
      helpBtn: document.getElementById("btn-help"),
      helpModal: document.getElementById("help-modal"),
      closeHelpBtn: document.getElementById("btn-close-help")
    };

    this.dom.timeTotal.textContent = this.formatTime(this.totalDuration);
  }

  initEvents() {
    // Play / Pause
    this.dom.playPauseBtn.addEventListener("click", () => this.togglePlay());
    this.dom.replayBtn.addEventListener("click", () => this.seek(0));

    // Chapter Navigation
    this.dom.prevChapterBtn.addEventListener("click", () => this.prevChapter());
    this.dom.nextChapterBtn.addEventListener("click", () => this.nextChapter());

    // Timeline Scrubbing
    let isDragging = false;
    const handleScrub = (e) => {
      const rect = this.dom.timelineContainer.getBoundingClientRect();
      const pos = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
      this.seek(pos * this.totalDuration);
    };

    this.dom.timelineContainer.addEventListener("mousedown", (e) => {
      isDragging = true;
      handleScrub(e);
    });

    window.addEventListener("mousemove", (e) => {
      if (isDragging) handleScrub(e);

      // Tooltip position
      const rect = this.dom.timelineContainer.getBoundingClientRect();
      if (e.clientX >= rect.left && e.clientX <= rect.right) {
        const pos = (e.clientX - rect.left) / rect.width;
        const time = pos * this.totalDuration;
        this.dom.timelineTooltip.style.left = `${pos * 100}%`;
        const ch = this.getChapterAt(time);
        this.dom.timelineTooltip.textContent = `${this.formatTime(time)} • ${ch ? ch.title : ""}`;
      }
    });

    window.addEventListener("mouseup", () => {
      isDragging = false;
    });

    // Speed Selector
    this.dom.speedSelect.addEventListener("change", (e) => {
      this.playbackRate = parseFloat(e.target.value);
      this.audio.setRate(this.playbackRate);
    });

    // Audio Mute Toggle
    this.dom.muteBtn.addEventListener("click", () => {
      const isMuted = !this.audio.toggleMute();
      this.dom.volumeHighIcon.style.display = isMuted ? "none" : "block";
      this.dom.volumeMutedIcon.style.display = isMuted ? "block" : "none";
    });

    // Captions Toggle
    this.dom.captionsBtn.addEventListener("click", () => {
      this.captionsVisible = !this.captionsVisible;
      this.dom.captionsHud.classList.toggle("hidden", !this.captionsVisible);
      this.dom.captionsBtn.classList.toggle("active", this.captionsVisible);
    });

    // Camera Mode Toggle
    this.dom.cameraBtn.addEventListener("click", () => {
      const newMode = this.renderer.camera.mode === "director" ? "overview" : "director";
      this.renderer.setCameraMode(newMode);
      this.dom.cameraBtn.classList.toggle("active", newMode === "director");
      this.dom.cameraBtn.title = newMode === "director" ? "Director Auto-Focus: ON" : "Director Auto-Focus: OFF (Overview)";
    });

    // Fullscreen
    this.dom.fullscreenBtn.addEventListener("click", () => {
      if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen();
      } else {
        document.exitFullscreen();
      }
    });

    // Video Export / Recording
    this.recorder.onStateChange = (isRec) => {
      this.dom.recordBtn.classList.toggle("recording", isRec);
      this.dom.recordText.textContent = isRec ? "Stop Recording" : "Record Video";
    };

    this.dom.recordBtn.addEventListener("click", () => {
      if (this.recorder.isRecording) {
        this.recorder.stopRecording();
      } else {
        this.recorder.startRecording();
        if (!this.isPlaying) this.togglePlay();
      }
    });

    // Scenario Picker
    this.dom.scenarioSelect.addEventListener("change", (e) => {
      const scKey = e.target.value;
      if (scKey === "interactive") {
        this.activeScenario = null;
      } else {
        this.loadScenario(scKey);
      }
    });

    // Canvas Interactive Click & Hover
    this.renderer.canvas.addEventListener("mousemove", (e) => {
      const node = this.renderer.getNodeAt(e.clientX, e.clientY);
      this.renderer.hoveredNode = node ? node.id : null;
      this.renderer.canvas.style.cursor = node ? "pointer" : "default";
    });

    this.renderer.canvas.addEventListener("click", (e) => {
      const node = this.renderer.getNodeAt(e.clientX, e.clientY);
      if (node) {
        this.openInspector(node);
      }
    });

    // Inspector Drawer Close
    this.dom.closeInspectorBtn.addEventListener("click", () => {
      this.closeInspector();
    });

    // Help Modal
    this.dom.helpBtn.addEventListener("click", () => {
      this.dom.helpModal.classList.add("open");
    });
    this.dom.closeHelpBtn.addEventListener("click", () => {
      this.dom.helpModal.classList.remove("open");
    });
    this.dom.helpModal.addEventListener("click", (e) => {
      if (e.target === this.dom.helpModal) {
        this.dom.helpModal.classList.remove("open");
      }
    });
  }

  initKeyboard() {
    window.addEventListener("keydown", (e) => {
      if (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA" || e.target.tagName === "SELECT") return;

      switch (e.key) {
        case " ":
          e.preventDefault();
          this.togglePlay();
          break;
        case "ArrowLeft":
          e.preventDefault();
          this.seek(Math.max(0, this.currentTime - 5));
          break;
        case "ArrowRight":
          e.preventDefault();
          this.seek(Math.min(this.totalDuration, this.currentTime + 5));
          break;
        case "m":
        case "M":
          this.dom.muteBtn.click();
          break;
        case "c":
        case "C":
          this.dom.captionsBtn.click();
          break;
        case "d":
        case "D":
          this.dom.cameraBtn.click();
          break;
        case "f":
        case "F":
          this.dom.fullscreenBtn.click();
          break;
        case "Escape":
          this.closeInspector();
          this.dom.helpModal.classList.remove("open");
          break;
      }
    });
  }

  togglePlay() {
    this.isPlaying = !this.isPlaying;
    this.dom.playIcon.style.display = this.isPlaying ? "none" : "block";
    this.dom.pauseIcon.style.display = this.isPlaying ? "block" : "none";

    if (this.isPlaying) {
      const ch = this.getCurrentChapter();
      if (ch) this.audio.narrateChapter(ch, true);
    } else {
      this.audio.pause();
    }
  }

  seek(time) {
    this.currentTime = Math.max(0, Math.min(this.totalDuration, time));
    this.updateTimelineUI();
    this.updateChapterUI();

    const ch = this.getCurrentChapter();
    if (ch) {
      this.renderer.setChapter(ch);
      if (this.isPlaying) {
        this.audio.narrateChapter(ch, true);
      }
    }
  }

  getCurrentChapter() {
    return this.getChapterAt(this.currentTime);
  }

  getChapterAt(time) {
    return this.data.chapters.find(ch => time >= ch.start && time < ch.end) || this.data.chapters[this.data.chapters.length - 1];
  }

  prevChapter() {
    const curr = this.getCurrentChapter();
    const idx = this.data.chapters.indexOf(curr);
    if (idx > 0) {
      this.seek(this.data.chapters[idx - 1].start);
    } else {
      this.seek(0);
    }
  }

  nextChapter() {
    const curr = this.getCurrentChapter();
    const idx = this.data.chapters.indexOf(curr);
    if (idx < this.data.chapters.length - 1) {
      this.seek(this.data.chapters[idx + 1].start);
    }
  }

  loadScenario(key) {
    const sc = this.data.scenarios[key];
    if (!sc) return;
    this.activeScenario = sc;

    // Reset to start of video and highlight scenario
    this.seek(0);
    this.audio.cancel();

    // Custom HUD alert
    this.dom.captionChapter.textContent = sc.name;
    this.dom.captionStatus.textContent = sc.badge;
    this.dom.captionBody.textContent = sc.description;
  }

  openInspector(node) {
    this.renderer.selectedNode = node.id;
    this.dom.inspectorDrawer.classList.add("open");

    document.getElementById("drawer-title").textContent = node.title;
    document.getElementById("drawer-badge").textContent = node.badge || "Component";
    document.getElementById("drawer-adk-pattern").textContent = node.adkPattern || "ADK Primitive";
    document.getElementById("drawer-description").textContent = node.description || "";
    document.getElementById("drawer-code").textContent = node.adkSnippet || "# No ADK snippet defined";

    // Setup Copy Code Button
    const copyBtn = document.getElementById("btn-copy-code");
    copyBtn.onclick = () => {
      navigator.clipboard.writeText(node.adkSnippet || "");
      copyBtn.textContent = "Copied!";
      setTimeout(() => copyBtn.textContent = "Copy", 1500);
    };
  }

  closeInspector() {
    this.renderer.selectedNode = null;
    this.dom.inspectorDrawer.classList.remove("open");
  }

  updateTimelineUI() {
    const progress = (this.currentTime / this.totalDuration) * 100;
    this.dom.timelineProgress.style.width = `${progress}%`;
    this.dom.timelineHandle.style.left = `${progress}%`;
    this.dom.timeCurrent.textContent = this.formatTime(this.currentTime);
  }

  updateChapterUI() {
    const ch = this.getCurrentChapter();
    if (!ch) return;

    this.dom.captionChapter.textContent = ch.title;
    this.dom.captionStatus.textContent = ch.status;
    this.dom.captionBody.textContent = ch.subtitle;
  }

  loop(timestamp) {
    const dt = Math.min((timestamp - this.lastFrameTime) / 1000, 0.1);
    this.lastFrameTime = timestamp;

    if (this.isPlaying) {
      const prevChapter = this.getCurrentChapter();
      this.currentTime += dt * this.playbackRate;

      if (this.currentTime >= this.totalDuration) {
        this.currentTime = this.totalDuration;
        this.isPlaying = false;
        this.dom.playIcon.style.display = "block";
        this.dom.pauseIcon.style.display = "none";
      }

      this.updateTimelineUI();

      const newChapter = this.getCurrentChapter();
      if (newChapter !== prevChapter) {
        this.updateChapterUI();
        this.renderer.setChapter(newChapter);
        this.audio.narrateChapter(newChapter, true);
      }
    }

    // Update Renderer Physics & Particles
    this.renderer.update(dt);

    // Render Canvas Frame
    this.renderer.render();

    requestAnimationFrame((t) => this.loop(t));
  }

  formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  }
}

window.addEventListener("DOMContentLoaded", () => {
  window.app = new InteractiveVideoApp();
});
