/**
 * Client-Side Video Recording & Export Engine
 * Captures the HTML5 Canvas 60FPS stream and exports an MP4/WebM video file.
 */

class VideoExportEngine {
  constructor(canvas) {
    this.canvas = canvas;
    this.mediaRecorder = null;
    this.recordedChunks = [];
    this.isRecording = false;
    this.onStateChange = null;
  }

  startRecording() {
    if (this.isRecording) return;
    this.recordedChunks = [];

    try {
      const stream = this.canvas.captureStream(60); // 60 FPS
      const options = { mimeType: "video/webm;codecs=vp9" };

      if (!MediaRecorder.isTypeSupported(options.mimeType)) {
        options.mimeType = "video/webm";
      }

      this.mediaRecorder = new MediaRecorder(stream, options);

      this.mediaRecorder.ondataavailable = (e) => {
        if (e.data && e.data.size > 0) {
          this.recordedChunks.push(e.data);
        }
      };

      this.mediaRecorder.onstop = () => {
        this.saveRecording();
      };

      this.mediaRecorder.start(100); // 100ms slice
      this.isRecording = true;
      if (this.onStateChange) this.onStateChange(true);
    } catch (e) {
      console.error("Recording error:", e);
      alert("Canvas Video Recording is not supported in this browser environment: " + e.message);
    }
  }

  stopRecording() {
    if (!this.isRecording || !this.mediaRecorder) return;
    this.mediaRecorder.stop();
    this.isRecording = false;
    if (this.onStateChange) this.onStateChange(false);
  }

  saveRecording() {
    if (this.recordedChunks.length === 0) return;
    const blob = new Blob(this.recordedChunks, { type: "video/webm" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.style.display = "none";
    a.href = url;
    a.download = `agent-sdk-builder-lab-${Date.now()}.webm`;
    document.body.appendChild(a);
    a.click();
    setTimeout(() => {
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    }, 100);
  }
}

window.VideoExportEngine = VideoExportEngine;
