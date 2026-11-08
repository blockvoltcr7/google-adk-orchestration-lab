/**
 * Audio Narration & Synth Sound Effects Engine
 * Uses Web Speech API for voiceover narration and Web Audio API for futuristic sound effects.
 */

class AudioNarrationEngine {
  constructor() {
    this.enabled = true;
    this.synth = window.speechSynthesis;
    this.audioCtx = null;
    this.currentUtterance = null;
    this.currentChapterId = null;
    this.selectedVoice = null;
    this.speechRate = 1.0;
    this.volume = 0.85;

    this.initAudioContext();
    this.initVoices();
  }

  initAudioContext() {
    try {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (AudioContext) {
        this.audioCtx = new AudioContext();
      }
    } catch (e) {
      console.warn("Web Audio API not supported", e);
    }
  }

  initVoices() {
    if (!this.synth) return;
    const updateVoices = () => {
      const voices = this.synth.getVoices();
      // Prefer modern natural English voices (Google, Daniel, Samantha, Karen, Natural)
      this.selectedVoice = voices.find(v => v.lang.startsWith("en") && (v.name.includes("Natural") || v.name.includes("Google") || v.name.includes("Premium") || v.name.includes("Samantha") || v.name.includes("Daniel"))) ||
                           voices.find(v => v.lang.startsWith("en")) ||
                           voices[0];
    };

    updateVoices();
    if (this.synth.onvoiceschanged !== undefined) {
      this.synth.onvoiceschanged = updateVoices;
    }
  }

  playFuturisticChime(type = "pulse") {
    if (!this.enabled || !this.audioCtx) return;
    if (this.audioCtx.state === "suspended") {
      this.audioCtx.resume();
    }

    const now = this.audioCtx.currentTime;
    const osc = this.audioCtx.createOscillator();
    const gain = this.audioCtx.createGain();

    osc.connect(gain);
    gain.connect(this.audioCtx.destination);

    if (type === "pulse") {
      osc.type = "sine";
      osc.frequency.setValueAtTime(440, now);
      osc.frequency.exponentialRampToValueAtTime(880, now + 0.15);
      gain.gain.setValueAtTime(0.05 * this.volume, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.2);
      osc.start(now);
      osc.stop(now + 0.2);
    } else if (type === "pass") {
      osc.type = "triangle";
      osc.frequency.setValueAtTime(523.25, now); // C5
      osc.frequency.setValueAtTime(659.25, now + 0.08); // E5
      osc.frequency.setValueAtTime(783.99, now + 0.16); // G5
      gain.gain.setValueAtTime(0.08 * this.volume, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.35);
      osc.start(now);
      osc.stop(now + 0.35);
    } else if (type === "fail") {
      osc.type = "sawtooth";
      osc.frequency.setValueAtTime(320, now);
      osc.frequency.linearRampToValueAtTime(160, now + 0.25);
      gain.gain.setValueAtTime(0.08 * this.volume, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.3);
      osc.start(now);
      osc.stop(now + 0.3);
    } else if (type === "transition") {
      osc.type = "sine";
      osc.frequency.setValueAtTime(300, now);
      osc.frequency.exponentialRampToValueAtTime(600, now + 0.2);
      gain.gain.setValueAtTime(0.04 * this.volume, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.25);
      osc.start(now);
      osc.stop(now + 0.25);
    }
  }

  narrateChapter(chapter, isPlaying = true) {
    if (!this.synth || !this.enabled || !isPlaying) {
      this.cancel();
      return;
    }

    if (this.currentChapterId === chapter.id && this.synth.speaking) {
      return; // Already narrating current chapter
    }

    this.cancel();
    this.currentChapterId = chapter.id;

    if (!chapter.voiceText) return;

    this.playFuturisticChime("transition");

    const utterance = new SpeechSynthesisUtterance(chapter.voiceText);
    if (this.selectedVoice) {
      utterance.voice = this.selectedVoice;
    }
    utterance.rate = this.speechRate;
    utterance.pitch = 1.0;
    utterance.volume = this.volume;

    utterance.onend = () => {
      this.currentUtterance = null;
    };

    utterance.onerror = (e) => {
      console.warn("Speech synthesis error", e);
      this.currentUtterance = null;
    };

    this.currentUtterance = utterance;
    try {
      this.synth.speak(utterance);
    } catch (e) {
      console.error(e);
    }
  }

  pause() {
    if (this.synth && this.synth.speaking) {
      this.synth.pause();
    }
  }

  resume() {
    if (this.synth && this.synth.paused) {
      this.synth.resume();
    }
  }

  cancel() {
    if (this.synth) {
      this.synth.cancel();
    }
    this.currentUtterance = null;
    this.currentChapterId = null;
  }

  toggleMute() {
    this.enabled = !this.enabled;
    if (!this.enabled) {
      this.cancel();
    }
    return this.enabled;
  }

  setRate(rate) {
    this.speechRate = rate;
    if (this.currentUtterance && this.synth.speaking) {
      // Re-trigger with new rate if currently speaking
    }
  }
}

window.AudioNarrationEngine = AudioNarrationEngine;
