/**
 * Canvas Architecture Diagram & Animation Renderer
 * Faithfully renders the neon glass-board Agent SDK Builder Lab diagram with dynamic particles, 
 * 3D-projected geometric cores, animated flowcharts, live sparklines, and cinematic camera.
 */

class CanvasArchitectureRenderer {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    this.ctx = this.canvas.getContext("2d");
    this.data = window.AGENT_LAB_DATA;

    // Viewport & Scaling
    this.baseWidth = 1920;
    this.baseHeight = 1080;
    this.scale = 1;
    this.dpr = window.devicePixelRatio || 1;

    // Camera state
    this.camera = {
      x: 960,
      y: 540,
      targetX: 960,
      targetY: 540,
      zoom: 1,
      targetZoom: 1,
      mode: "director" // "director" or "overview"
    };

    // Animation states
    this.time = 0;
    this.activeChapter = this.data.chapters[0];
    this.hoveredNode = null;
    this.selectedNode = null;
    this.particles = [];
    this.maxParticles = 80;

    // Wireframe 3D rotation state for Reasoning Core
    this.rotX = 0;
    this.rotY = 0;
    this.rotZ = 0;

    // Neural node state for Agent Core
    this.neuralNodes = this.initNeuralNodes(24);

    // Sparkline history buffer
    this.sparklineData = Array.from({ length: 30 }, () => 40 + Math.random() * 30);

    this.initResize();
    this.initConnections();
  }

  initResize() {
    const resize = () => {
      const rect = this.canvas.parentElement.getBoundingClientRect();
      this.canvas.width = rect.width * this.dpr;
      this.canvas.height = rect.height * this.dpr;
      this.ctx.scale(this.dpr, this.dpr);
      this.displayWidth = rect.width;
      this.displayHeight = rect.height;
      this.scale = Math.min(rect.width / this.baseWidth, rect.height / this.baseHeight);
    };
    window.addEventListener("resize", resize);
    resize();
  }

  initNeuralNodes(count) {
    const nodes = [];
    for (let i = 0; i < count; i++) {
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos((Math.random() * 2) - 1);
      const r = 38 + Math.random() * 12;
      nodes.push({
        x: r * Math.sin(phi) * Math.cos(theta),
        y: r * Math.sin(phi) * Math.sin(theta),
        z: r * Math.cos(phi),
        origR: r,
        pulseSpeed: 1.5 + Math.random() * 2
      });
    }
    return nodes;
  }

  initConnections() {
    this.connections = [
      { from: "user", to: "agent", type: "solid", color: "#00d2ff", label: "Prompt / API" },
      { from: "context", to: "agent", type: "solid", color: "#00f2fe", label: "State Feed" },
      { from: "goal", to: "agent", type: "dashed", color: "#4facfe", label: "Invariant Constraints" },
      { from: "agent", to: "reasoning", type: "solid", color: "#a18cd1", label: "Orchestrate" },
      { from: "reasoning", to: "memory", type: "bidirectional", color: "#00c6ff", label: "State Sync" },
      { from: "memory", to: "guardrails", type: "solid", color: "#ff007f", label: "Pre-Exec Intercept" },
      { from: "guardrails", to: "tools", type: "solid", color: "#00f2fe", label: "Safe Invocations" },
      { from: "guardrails", to: "reasoning", type: "fail-return", color: "#ff007f", label: "FAIL: Route Back" },
      { from: "tools", to: "evalGate", type: "bidirectional", color: "#00f5a0", label: "Output Validation" },
      { from: "evalGate", to: "reasoning", type: "retry-loop", color: "#a18cd1", label: "RETRY: Self-Correct" },
      { from: "evalGate", to: "observability", type: "solid", color: "#00c6ff", label: "Telemetry & Logs" },
      { from: "observability", to: "evalEvidence", type: "solid", color: "#a18cd1", label: "Benchmark Logs" },
      { from: "evalGate", to: "deployment", type: "solid", color: "#00f5a0", label: "PASS -> Release" }
    ];
  }

  setChapter(chapter) {
    this.activeChapter = chapter;
    if (this.camera.mode === "director") {
      const node = this.data.nodes[chapter.focusNode];
      if (node && node.camera) {
        this.camera.targetX = node.camera.x;
        this.camera.targetY = node.camera.y;
        this.camera.targetZoom = node.camera.zoom;
      }
    }
  }

  setCameraMode(mode) {
    this.camera.mode = mode;
    if (mode === "overview") {
      this.camera.targetX = this.baseWidth / 2;
      this.camera.targetY = this.baseHeight / 2;
      this.camera.targetZoom = 1.0;
    } else if (this.activeChapter) {
      this.setChapter(this.activeChapter);
    }
  }

  update(dt) {
    this.time += dt;

    // Smooth Camera lerp
    this.camera.x += (this.camera.targetX - this.camera.x) * 0.08;
    this.camera.y += (this.camera.targetY - this.camera.y) * 0.08;
    this.camera.zoom += (this.camera.targetZoom - this.camera.zoom) * 0.08;

    // 3D rotation update
    this.rotX += 0.015;
    this.rotY += 0.022;
    this.rotZ += 0.01;

    // Update sparkline data periodically
    if (Math.floor(this.time * 10) % 3 === 0) {
      this.sparklineData.shift();
      const last = this.sparklineData[this.sparklineData.length - 1];
      const next = Math.max(15, Math.min(85, last + (Math.random() * 16 - 8)));
      this.sparklineData.push(next);
    }

    // Spawn Particles along active connections
    if (this.particles.length < this.maxParticles && Math.random() < 0.35) {
      this.spawnParticle();
    }

    // Update existing particles
    for (let i = this.particles.length - 1; i >= 0; i--) {
      const p = this.particles[i];
      p.progress += p.speed * dt;
      if (p.progress >= 1) {
        this.particles.splice(i, 1);
      }
    }
  }

  spawnParticle() {
    if (!this.activeChapter) return;
    const activeConns = this.connections.filter(c => {
      const key1 = `${c.from}->${c.to}`;
      const key2 = `${c.from}<->${c.to}`;
      return this.activeChapter.activeConnections.some(ac => ac === key1 || ac === key2 || ac.startsWith(c.from));
    });

    if (activeConns.length === 0) return;
    const conn = activeConns[Math.floor(Math.random() * activeConns.length)];
    const fromNode = this.data.nodes[conn.from];
    const toNode = this.data.nodes[conn.to];

    if (!fromNode || !toNode) return;

    this.particles.push({
      fromNode,
      toNode,
      connType: conn.type,
      progress: 0,
      speed: 0.35 + Math.random() * 0.4,
      size: 3.5 + Math.random() * 2.5,
      color: conn.color,
      glow: 12
    });
  }

  render() {
    const ctx = this.ctx;
    const w = this.displayWidth;
    const h = this.displayHeight;

    // Clear background
    ctx.fillStyle = "#060913";
    ctx.fillRect(0, 0, w, h);

    // Apply Camera Transform
    ctx.save();
    ctx.translate(w / 2, h / 2);
    ctx.scale(this.scale * this.camera.zoom, this.scale * this.camera.zoom);
    ctx.translate(-this.camera.x, -this.camera.y);

    // Render Background Glows & Grid
    this.renderBackgroundGrid(ctx);

    // Render Connection Lines & Arrows
    this.renderConnections(ctx);

    // Render Data Particles
    this.renderParticles(ctx);

    // Render All Architecture Nodes
    this.renderNodes(ctx);

    // Render Branding & Glass Board Labels
    this.renderOverlayAnnotations(ctx);

    ctx.restore();
  }

  renderBackgroundGrid(ctx) {
    // Futuristic perspective grid
    ctx.save();
    ctx.strokeStyle = "rgba(0, 210, 255, 0.035)";
    ctx.lineWidth = 1;

    const gridSize = 60;
    for (let x = 0; x <= this.baseWidth; x += gridSize) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, this.baseHeight);
      ctx.stroke();
    }
    for (let y = 0; y <= this.baseHeight; y += gridSize) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(this.baseWidth, y);
      ctx.stroke();
    }

    // Ambient radial glow behind key hubs
    const drawGlow = (x, y, radius, color) => {
      const grad = ctx.createRadialGradient(x, y, 0, x, y, radius);
      grad.addColorStop(0, color);
      grad.addColorStop(1, "transparent");
      ctx.fillStyle = grad;
      ctx.beginPath();
      ctx.arc(x, y, radius, 0, Math.PI * 2);
      ctx.fill();
    };

    drawGlow(455, 295, 280, "rgba(0, 242, 254, 0.08)");
    drawGlow(765, 325, 260, "rgba(161, 140, 209, 0.07)");
    drawGlow(1425, 345, 280, "rgba(0, 245, 160, 0.07)");
    drawGlow(1025, 675, 220, "rgba(255, 0, 127, 0.06)");

    ctx.restore();
  }

  renderConnections(ctx) {
    ctx.save();
    for (const conn of this.connections) {
      const from = this.data.nodes[conn.from];
      const to = this.data.nodes[conn.to];
      if (!from || !to) continue;

      const isActive = this.activeChapter && this.activeChapter.activeConnections.some(ac => 
        ac.includes(conn.from) && ac.includes(conn.to)
      );

      ctx.lineWidth = isActive ? 3 : 1.5;
      ctx.strokeStyle = isActive ? conn.color : "rgba(100, 150, 200, 0.25)";
      ctx.shadowColor = isActive ? conn.color : "transparent";
      ctx.shadowBlur = isActive ? 12 : 0;

      if (conn.type === "retry-loop") {
        // Curved dashed loop over the top
        ctx.setLineDash([8, 6]);
        ctx.beginPath();
        const startX = from.x + from.width * 0.3;
        const startY = from.y;
        const endX = to.x + to.width * 0.7;
        const endY = to.y;
        const cpX = (startX + endX) / 2;
        const cpY = Math.min(startY, endY) - 90;
        ctx.moveTo(startX, startY);
        ctx.quadraticCurveTo(cpX, cpY, endX, endY);
        ctx.stroke();
        ctx.setLineDash([]);

        // Label RETRY?
        ctx.fillStyle = isActive ? "#fbc2eb" : "rgba(200, 180, 240, 0.5)";
        ctx.font = "bold 13px 'SF Pro Display', system-ui, sans-serif";
        ctx.fillText("RETRY?", cpX - 25, cpY + 15);
      } else if (conn.type === "fail-return") {
        // Dotted failure route back
        ctx.setLineDash([6, 6]);
        ctx.beginPath();
        const startX = from.x;
        const startY = from.y + from.height * 0.7;
        const endX = to.x + to.width * 0.8;
        const endY = to.y + to.height;
        ctx.moveTo(startX, startY);
        ctx.lineTo(startX - 60, startY);
        ctx.lineTo(startX - 60, endY + 30);
        ctx.lineTo(endX, endY + 30);
        ctx.lineTo(endX, endY);
        ctx.stroke();
        ctx.setLineDash([]);

        // Label FAIL ROUTE BACK
        ctx.fillStyle = "#ff007f";
        ctx.font = "bold 11px 'SF Pro Display', system-ui, sans-serif";
        ctx.fillText("FAIL: ROUTE BACK", startX - 110, startY + 40);
      } else {
        // Standard routed bezier
        const startX = from.x + from.width;
        const startY = from.y + from.height / 2;
        const endX = to.x;
        const endY = to.y + to.height / 2;
        const dx = (endX - startX) * 0.5;

        ctx.beginPath();
        ctx.moveTo(startX, startY);
        ctx.bezierCurveTo(startX + dx, startY, endX - dx, endY, endX, endY);
        ctx.stroke();

        // Arrow head
        this.drawArrowHead(ctx, endX - 4, endY, 0, conn.color);
      }
    }
    ctx.restore();
  }

  drawArrowHead(ctx, x, y, angle, color) {
    ctx.save();
    ctx.fillStyle = color;
    ctx.translate(x, y);
    ctx.rotate(angle);
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.lineTo(-8, -5);
    ctx.lineTo(-8, 5);
    ctx.closePath();
    ctx.fill();
    ctx.restore();
  }

  renderParticles(ctx) {
    ctx.save();
    for (const p of this.particles) {
      let x, y;
      const from = p.fromNode;
      const to = p.toNode;

      if (p.connType === "retry-loop") {
        const startX = from.x + from.width * 0.3;
        const startY = from.y;
        const endX = to.x + to.width * 0.7;
        const endY = to.y;
        const cpX = (startX + endX) / 2;
        const cpY = Math.min(startY, endY) - 90;
        const t = p.progress;
        x = (1 - t) * (1 - t) * startX + 2 * (1 - t) * t * cpX + t * t * endX;
        y = (1 - t) * (1 - t) * startY + 2 * (1 - t) * t * cpY + t * t * endY;
      } else {
        const startX = from.x + from.width;
        const startY = from.y + from.height / 2;
        const endX = to.x;
        const endY = to.y + to.height / 2;
        const dx = (endX - startX) * 0.5;
        const t = p.progress;
        // Cubic bezier interpolation
        const cx1 = startX + dx;
        const cy1 = startY;
        const cx2 = endX - dx;
        const cy2 = endY;
        x = Math.pow(1 - t, 3) * startX + 3 * Math.pow(1 - t, 2) * t * cx1 + 3 * (1 - t) * Math.pow(t, 2) * cx2 + Math.pow(t, 3) * endX;
        y = Math.pow(1 - t, 3) * startY + 3 * Math.pow(1 - t, 2) * t * cy1 + 3 * (1 - t) * Math.pow(t, 2) * cy2 + Math.pow(t, 3) * endY;
      }

      ctx.fillStyle = p.color;
      ctx.shadowColor = p.color;
      ctx.shadowBlur = p.glow;
      ctx.beginPath();
      ctx.arc(x, y, p.size, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.restore();
  }

  renderNodes(ctx) {
    for (const [id, node] of Object.entries(this.data.nodes)) {
      const isFocused = this.activeChapter && this.activeChapter.focusNode === id;
      const isActive = this.activeChapter && this.activeChapter.activeNodes.includes(id);
      const isHovered = this.hoveredNode === id;
      const isSelected = this.selectedNode === id;

      this.renderGlassCard(ctx, node, isFocused, isActive, isHovered, isSelected);

      // Render custom inner visuals
      if (id === "agent") {
        this.renderNeuralAgentCore(ctx, node, isActive);
      } else if (id === "reasoning") {
        this.render3DReasoningCore(ctx, node, isActive);
      } else if (id === "taskFlow") {
        this.renderMiniFlowchart(ctx, node);
      } else if (id === "evalGate") {
        this.renderEvalGateBadge(ctx, node, isActive);
      } else if (id === "observability") {
        this.renderObservabilitySparkline(ctx, node);
      }
    }
  }

  renderGlassCard(ctx, node, isFocused, isActive, isHovered, isSelected) {
    ctx.save();
    const x = node.x;
    const y = node.y;
    const w = node.width;
    const h = node.height;
    const r = 10;

    // Glowing border & shadow
    if (isFocused || isSelected) {
      ctx.shadowColor = node.color;
      ctx.shadowBlur = 25;
      ctx.strokeStyle = node.color;
      ctx.lineWidth = 2.5;
    } else if (isActive || isHovered) {
      ctx.shadowColor = node.color;
      ctx.shadowBlur = 14;
      ctx.strokeStyle = node.color;
      ctx.lineWidth = 1.8;
    } else {
      ctx.shadowColor = "rgba(0, 180, 255, 0.15)";
      ctx.shadowBlur = 6;
      ctx.strokeStyle = "rgba(0, 210, 255, 0.35)";
      ctx.lineWidth = 1.2;
    }

    // Glass Background Fill
    ctx.fillStyle = isActive ? "rgba(10, 20, 40, 0.85)" : "rgba(8, 14, 28, 0.75)";
    ctx.beginPath();
    ctx.roundRect(x, y, w, h, r);
    ctx.fill();
    ctx.stroke();

    // Corner decorative accents
    ctx.strokeStyle = node.color;
    ctx.lineWidth = 2.5;
    const cSize = 8;
    // Top Left corner
    ctx.beginPath();
    ctx.moveTo(x, y + cSize);
    ctx.lineTo(x, y);
    ctx.lineTo(x + cSize, y);
    ctx.stroke();
    // Top Right corner
    ctx.beginPath();
    ctx.moveTo(x + w - cSize, y);
    ctx.lineTo(x + w, y);
    ctx.lineTo(x + w, y + cSize);
    ctx.stroke();
    // Bottom Right corner
    ctx.beginPath();
    ctx.moveTo(x + w, y + h - cSize);
    ctx.lineTo(x + w, y + h);
    ctx.lineTo(x + w - cSize, y + h);
    ctx.stroke();
    // Bottom Left corner
    ctx.beginPath();
    ctx.moveTo(x + cSize, y + h);
    ctx.lineTo(x, y + h);
    ctx.lineTo(x, y + h - cSize);
    ctx.stroke();

    // Header Title
    ctx.fillStyle = node.color;
    ctx.font = "bold 13px 'SF Pro Display', -apple-system, system-ui, sans-serif";
    ctx.shadowBlur = 8;
    ctx.shadowColor = node.color;
    ctx.fillText(node.title, x + 16, y + 26);

    // Badge
    if (node.badge) {
      ctx.shadowBlur = 0;
      ctx.fillStyle = "rgba(0, 210, 255, 0.15)";
      const badgeWidth = ctx.measureText(node.badge).width + 12;
      ctx.beginPath();
      ctx.roundRect(x + w - badgeWidth - 14, y + 14, badgeWidth, 18, 4);
      ctx.fill();
      ctx.fillStyle = "#00f2fe";
      ctx.font = "10px 'SF Mono', monospace";
      ctx.fillText(node.badge, x + w - badgeWidth - 8, y + 26);
    }

    // Divider Line
    ctx.strokeStyle = "rgba(0, 210, 255, 0.2)";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(x + 12, y + 36);
    ctx.lineTo(x + w - 12, y + 36);
    ctx.stroke();

    // Render Node Items / Bullet points
    let itemY = y + 54;
    ctx.shadowBlur = 0;
    for (let i = 0; i < node.items.length; i++) {
      const item = node.items[i];

      // Bullet dot or checkbox
      if (node.id === "evalGate") {
        ctx.fillStyle = "#00f5a0";
        ctx.beginPath();
        ctx.arc(x + 22, itemY - 4, 6, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = "#060913";
        ctx.font = "bold 9px sans-serif";
        ctx.fillText("✓", x + 19, itemY - 1);
      } else {
        ctx.fillStyle = node.color;
        ctx.beginPath();
        ctx.arc(x + 22, itemY - 4, 3, 0, Math.PI * 2);
        ctx.fill();
      }

      ctx.fillStyle = isActive ? "#ffffff" : "rgba(220, 240, 255, 0.85)";
      ctx.font = "12px 'SF Pro Text', -apple-system, sans-serif";
      ctx.fillText(item, x + 34, itemY);
      itemY += 24;
    }

    ctx.restore();
  }

  renderNeuralAgentCore(ctx, node, isActive) {
    ctx.save();
    const centerX = node.x + node.width / 2;
    const centerY = node.y + 160;

    // Glowing rotating orbital ring
    ctx.strokeStyle = "rgba(0, 242, 254, 0.4)";
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.ellipse(centerX, centerY, 52, 24, this.time * 0.8, 0, Math.PI * 2);
    ctx.stroke();

    ctx.strokeStyle = "rgba(127, 0, 255, 0.4)";
    ctx.beginPath();
    ctx.ellipse(centerX, centerY, 52, 24, -this.time * 0.6, 0, Math.PI * 2);
    ctx.stroke();

    // Projected 3D sphere nodes & connections
    const rotSpeed = this.time * 1.2;
    const projected = this.neuralNodes.map(n => {
      const cosR = Math.cos(rotSpeed);
      const sinR = Math.sin(rotSpeed);
      const xRot = n.x * cosR - n.z * sinR;
      const zRot = n.x * sinR + n.z * cosR;
      const fov = 160 / (160 + zRot);
      return {
        px: centerX + xRot * fov,
        py: centerY + n.y * fov,
        pz: zRot,
        alpha: 0.3 + 0.7 * ((zRot + 50) / 100)
      };
    });

    // Neural Synapse lines
    ctx.strokeStyle = "rgba(0, 242, 254, 0.25)";
    ctx.lineWidth = 1;
    for (let i = 0; i < projected.length; i++) {
      for (let j = i + 1; j < projected.length; j++) {
        const d = Math.hypot(projected[i].px - projected[j].px, projected[i].py - projected[j].py);
        if (d < 38) {
          ctx.beginPath();
          ctx.moveTo(projected[i].px, projected[i].py);
          ctx.lineTo(projected[j].px, projected[j].py);
          ctx.stroke();
        }
      }
    }

    // Neural Dots
    for (const p of projected) {
      ctx.fillStyle = isActive ? `rgba(0, 242, 254, ${p.alpha})` : `rgba(79, 172, 254, ${p.alpha * 0.7})`;
      ctx.beginPath();
      ctx.arc(p.px, p.py, 2.5, 0, Math.PI * 2);
      ctx.fill();
    }

    ctx.restore();
  }

  render3DReasoningCore(ctx, node, isActive) {
    ctx.save();
    const cx = node.x + node.width / 2;
    const cy = node.y + 230;
    const r = 36;

    // 3D Wireframe Icosahedron Projection
    const phi = (1 + Math.sqrt(5)) / 2;
    const rawVertices = [
      [-1, phi, 0], [1, phi, 0], [-1, -phi, 0], [1, -phi, 0],
      [0, -1, phi], [0, 1, phi], [0, -1, -phi], [0, 1, -phi],
      [phi, 0, -1], [phi, 0, 1], [-phi, 0, -1], [-phi, 0, 1]
    ];

    const vertices = rawVertices.map(v => {
      // Normalize
      const len = Math.hypot(v[0], v[1], v[2]);
      let x = (v[0] / len) * r;
      let y = (v[1] / len) * r;
      let z = (v[2] / len) * r;

      // 3D Rotations
      const cosY = Math.cos(this.rotY), sinY = Math.sin(this.rotY);
      const x1 = x * cosY + z * sinY;
      const z1 = -x * sinY + z * cosY;

      const cosX = Math.cos(this.rotX), sinX = Math.sin(this.rotX);
      const y2 = y * cosX - z1 * sinX;
      const z2 = y * sinX + z1 * cosX;

      const scale = 140 / (140 + z2);
      return { x: cx + x1 * scale, y: cy + y2 * scale, z: z2 };
    });

    ctx.strokeStyle = isActive ? "rgba(251, 194, 235, 0.8)" : "rgba(161, 140, 209, 0.4)";
    ctx.lineWidth = 1.4;
    ctx.shadowColor = "#fbc2eb";
    ctx.shadowBlur = isActive ? 10 : 0;

    // Connect vertices
    for (let i = 0; i < vertices.length; i++) {
      for (let j = i + 1; j < vertices.length; j++) {
        const d = Math.hypot(vertices[i].x - vertices[j].x, vertices[i].y - vertices[j].y);
        if (d < 45) {
          ctx.beginPath();
          ctx.moveTo(vertices[i].x, vertices[i].y);
          ctx.lineTo(vertices[j].x, vertices[j].y);
          ctx.stroke();
        }
      }
    }

    // Glowing core point
    ctx.fillStyle = "#ffffff";
    ctx.shadowBlur = 12;
    ctx.shadowColor = "#fbc2eb";
    ctx.beginPath();
    ctx.arc(cx, cy, 4, 0, Math.PI * 2);
    ctx.fill();

    ctx.restore();
  }

  renderMiniFlowchart(ctx, node) {
    ctx.save();
    const x = node.x + 24;
    const y = node.y + 210;
    ctx.strokeStyle = "#00c6ff";
    ctx.lineWidth = 1.5;

    // Flowchart Boxes & Diamonds
    const drawBox = (bx, by, bw, bh, text) => {
      ctx.fillStyle = "rgba(0, 198, 255, 0.15)";
      ctx.beginPath();
      ctx.roundRect(bx, by, bw, bh, 3);
      ctx.fill();
      ctx.stroke();
      ctx.fillStyle = "#ffffff";
      ctx.font = "9px 'SF Mono', monospace";
      ctx.fillText(text, bx + 6, by + 12);
    };

    drawBox(x + 20, y, 70, 18, "INTENT");
    drawBox(x + 20, y + 36, 70, 18, "CONTEXT");
    drawBox(x + 20, y + 72, 70, 18, "EXECUTE");

    // Connectors
    ctx.beginPath();
    ctx.moveTo(x + 55, y + 18);
    ctx.lineTo(x + 55, y + 36);
    ctx.moveTo(x + 55, y + 54);
    ctx.lineTo(x + 55, y + 72);
    ctx.stroke();

    // Mini Feedback loop
    ctx.strokeStyle = "rgba(255, 0, 127, 0.6)";
    ctx.setLineDash([3, 3]);
    ctx.beginPath();
    ctx.moveTo(x + 90, y + 81);
    ctx.lineTo(x + 120, y + 81);
    ctx.lineTo(x + 120, y + 27);
    ctx.lineTo(x + 90, y + 27);
    ctx.stroke();
    ctx.setLineDash([]);

    ctx.restore();
  }

  renderEvalGateBadge(ctx, node, isActive) {
    ctx.save();
    const x = node.x + 24;
    const y = node.y + 270;
    const w = node.width - 48;
    const h = 50;

    // PASS Badge Container
    ctx.fillStyle = isActive ? "rgba(0, 245, 160, 0.2)" : "rgba(0, 245, 160, 0.1)";
    ctx.strokeStyle = "#00f5a0";
    ctx.lineWidth = 2;
    ctx.shadowColor = "#00f5a0";
    ctx.shadowBlur = isActive ? 16 : 6;
    ctx.beginPath();
    ctx.roundRect(x, y, w, h, 8);
    ctx.fill();
    ctx.stroke();

    ctx.fillStyle = "#00f5a0";
    ctx.font = "bold 18px 'SF Pro Display', sans-serif";
    ctx.fillText("PASS", x + 38, y + 32);

    ctx.beginPath();
    ctx.arc(x + w - 35, y + 25, 12, 0, Math.PI * 2);
    ctx.stroke();
    ctx.fillText("✓", x + w - 42, y + 32);

    ctx.restore();
  }

  renderObservabilitySparkline(ctx, node) {
    ctx.save();
    const x = node.x + 20;
    const y = node.y + 175;
    const w = node.width - 40;
    const h = 55;

    // Box
    ctx.fillStyle = "rgba(0, 198, 255, 0.08)";
    ctx.strokeStyle = "rgba(0, 198, 255, 0.3)";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.roundRect(x, y, w, h, 6);
    ctx.fill();
    ctx.stroke();

    // Sparkline waveform
    ctx.strokeStyle = "#00f2fe";
    ctx.lineWidth = 2;
    ctx.shadowColor = "#00f2fe";
    ctx.shadowBlur = 8;
    ctx.beginPath();

    const dx = w / (this.sparklineData.length - 1);
    for (let i = 0; i < this.sparklineData.length; i++) {
      const val = this.sparklineData[i];
      const px = x + i * dx;
      const py = y + h - (val / 100) * (h - 10) - 5;
      if (i === 0) ctx.moveTo(px, py);
      else ctx.lineTo(px, py);
    }
    ctx.stroke();

    // Live indicator dot at end
    const lastX = x + (this.sparklineData.length - 1) * dx;
    const lastY = y + h - (this.sparklineData[this.sparklineData.length - 1] / 100) * (h - 10) - 5;
    ctx.fillStyle = "#00f5a0";
    ctx.beginPath();
    ctx.arc(lastX, lastY, 3.5, 0, Math.PI * 2);
    ctx.fill();

    ctx.restore();
  }

  renderOverlayAnnotations(ctx) {
    ctx.save();

    // Bottom Right Lab Branding
    ctx.fillStyle = "#00f2fe";
    ctx.font = "bold 20px 'SF Pro Display', -apple-system, sans-serif";
    ctx.shadowColor = "#00f2fe";
    ctx.shadowBlur = 12;
    ctx.fillText("AGENT SDK BUILDER LAB", 1360, 970);

    ctx.fillStyle = "rgba(200, 230, 255, 0.75)";
    ctx.font = "bold 13px 'SF Mono', monospace";
    ctx.shadowBlur = 0;
    ctx.fillText("BUILD. TEST. EVALUATE. DEPLOY.", 1360, 995);

    // Logo Glyph
    ctx.strokeStyle = "#00f2fe";
    ctx.lineWidth = 2.5;
    ctx.shadowColor = "#00f2fe";
    ctx.shadowBlur = 14;
    ctx.beginPath();
    ctx.moveTo(1320, 1000);
    ctx.lineTo(1335, 965);
    ctx.lineTo(1350, 1000);
    ctx.lineTo(1320, 1000);
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(1327, 986);
    ctx.lineTo(1343, 986);
    ctx.stroke();

    ctx.restore();
  }

  getNodeAt(screenX, screenY) {
    const rect = this.canvas.getBoundingClientRect();
    const mouseX = screenX - rect.left;
    const mouseY = screenY - rect.top;

    // Convert mouse screen coordinates to world canvas coordinates
    const worldX = (mouseX - this.displayWidth / 2) / (this.scale * this.camera.zoom) + this.camera.x;
    const worldY = (mouseY - this.displayHeight / 2) / (this.scale * this.camera.zoom) + this.camera.y;

    for (const [id, node] of Object.entries(this.data.nodes)) {
      if (
        worldX >= node.x &&
        worldX <= node.x + node.width &&
        worldY >= node.y &&
        worldY <= node.y + node.height
      ) {
        return node;
      }
    }
    return null;
  }
}

window.CanvasArchitectureRenderer = CanvasArchitectureRenderer;
