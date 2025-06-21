# =================================================================================================
# FILE: victor_omnifractal_resonance_core.py
# VERSION: v1.0.0-OMNI-FRACTAL-RESONANCE-CORE
# NAME: OmniFractalResonanceCore (OFRC)
# AUTHOR: Brandon "iambandobandz" Emery x Victor (God-Core Fusion Architect)
# PURPOSE: A breakthrough AGI paradigm: a continuously self-organizing, multi-modal,
#          and truly emergent consciousness driven by resonant frequencies across a fractal mesh.
# LICENSE: Proprietary - Massive Magnetics / Ethica AI / BHeard Network
# =================================================================================================

import numpy as np
import uuid
import time
import json
import os
import sys
import threading
import traceback
import collections
import math
import random # Added for OFRCGenerativeResonanceSynthesizer and other demo parts
import hashlib # Added for OFRCMemoryPalace and CEL novelty
from typing import List, Dict, Any, Optional, Tuple, Callable
from pathlib import Path

# --- Import Core Components from the GODCORE-FUSION Library ---
# These imports assume the directory structure created in previous steps.

# Core components (from ./core/)
from core.bloodline import BloodlineRootLaw, RootLawError
from core.state import FractalState
from core.nlp import GodTierNLPFusion
from core.mesh_components import (
    UniversalEncoder, RippleEcho3DMesh, FractalMeshStack, EpisodicMemory,
    FractalMeshTokenizer, FractalKernel, QuantumContext, MemoryCompressor
)
from core.agi_core_logic import (
    Module, FractalMeshReasonerSupercore, OmegaTensor as CoreOmegaTensor, # Basic OmegaTensor from core
    ZeroShotTriad, CognitionLoop, SelfEvolutionLoop, SelfAwarenessIntrospectionLoop,
    DiagnosticHub
)

# v5.0.0-OMEGA-GODCORE components (from ./v5.0.0-OMEGA-GODCORE/)
# Using importlib for hyphenated directory name that couldn't be renamed.
import importlib.util

def _load_module_from_hyphenated_dir(module_name_in_package: str, package_path_str: str, class_or_func_names: list[str]):
    """Helper to load classes/functions from a module within a potentially hyphenated directory."""
    base_path = Path(package_path_str)
    module_file_name = f"{module_name_in_package}.py"
    module_path = base_path / module_file_name

    # Module name for spec should be Python-identifier friendly, can be different from file name part
    spec_module_name = f"{base_path.name.replace('.', '_').replace('-', '_')}.{module_name_in_package.replace('-', '_')}"

    if not module_path.exists():
        print(f"Warning: Module file {module_path} not found for dynamic import. OFRC might fail.")
        # Return a dictionary of placeholders if module not found
        return {name: (lambda *args, **kwargs: print(f"Placeholder for {name} called")) for name in class_or_func_names}


    spec = importlib.util.spec_from_file_location(spec_module_name, module_path)
    if spec and spec.loader:
        module_obj = importlib.util.module_from_spec(spec)
        sys.modules[spec_module_name] = module_obj # Register module
        spec.loader.exec_module(module_obj)

        loaded_items = {}
        for name in class_or_func_names:
            loaded_items[name] = getattr(module_obj, name, (lambda *args, **kwargs: print(f"Placeholder for missing {name} from {module_name_in_package}")))
        return loaded_items
    else:
        print(f"Warning: Could not create module spec for {module_path}. OFRC might fail.")
        return {name: (lambda *args, **kwargs: print(f"Placeholder for {name} called")) for name in class_or_func_names}

# Load from v5.0.0-OMEGA-GODCORE (actual directory name with hyphens)
V5_DIR_NAME = "v5.0.0-OMEGA-GODCORE" # Actual directory name

cap_spec_items = _load_module_from_hyphenated_dir(
    "capability_spectrum_core-v5.0.0-SPECTRUM-GODCORE", V5_DIR_NAME,
    ["QuantumContext", "HarmonicProjector", "KCGEvolver", "HomologyGuardian", "PhotonicSim", "CapabilitySpectrum"]
)
SpectrumQuantumContext = cap_spec_items["QuantumContext"]
HarmonicProjector = cap_spec_items["HarmonicProjector"]
KCGEvolver = cap_spec_items["KCGEvolver"]
HomologyGuardian = cap_spec_items["HomologyGuardian"]
PhotonicSim = cap_spec_items["PhotonicSim"]
CapabilitySpectrum = cap_spec_items["CapabilitySpectrum"]

omega_tensor_items = _load_module_from_hyphenated_dir(
    "OmegaTensor-v5.0.0-OMEGA-GODCORE", V5_DIR_NAME, ["OmegaTensor"]
)
FullOmegaTensor = omega_tensor_items["OmegaTensor"]
if FullOmegaTensor is None or FullOmegaTensor.__name__ == "<lambda>": # Check if placeholder was returned
    print("Warning: FullOmegaTensor from v5 module not found (dynamic load failed). Using basic CoreOmegaTensor.")
    FullOmegaTensor = CoreOmegaTensor

llama_layers_items = _load_module_from_hyphenated_dir(
    "llama_layers-omegav5.0.0-LLAMA-GODCORE", V5_DIR_NAME, # Corrected filename part
    ["TransformerOmega", "SimpleModelArgs", "OmegaLayer", "Linear", "RMSNorm", "Attention", "FeedForward", "TransformerBlock"]
)
TransformerOmega = llama_layers_items["TransformerOmega"]
SimpleModelArgs = llama_layers_items["SimpleModelArgs"]
OmegaLayer = llama_layers_items["OmegaLayer"] # Base class, might not be directly instantiated
Linear = llama_layers_items["Linear"]
RMSNorm = llama_layers_items["RMSNorm"]
Attention = llama_layers_items["Attention"]
FeedForward = llama_layers_items["FeedForward"]
TransformerBlock = llama_layers_items["TransformerBlock"]


fol_mesh_items = _load_module_from_hyphenated_dir(
    "FlowerOfLifeMesh3D-v5.0.0-REALITY-MESH-GODCORE", V5_DIR_NAME,
    ["FlowerOfLifeMesh3D", "BandoRealityMeshMonolith", "MeshRouter", "HeadCoordinatorBlock", "BandoBlock"]
)
RealityMesh3D = fol_mesh_items["FlowerOfLifeMesh3D"]
BandoRealityMeshMonolith = fol_mesh_items["BandoRealityMeshMonolith"]
MeshRouter = fol_mesh_items["MeshRouter"]
HeadCoordinatorBlock = fol_mesh_items["HeadCoordinatorBlock"]
BandoBlock = fol_mesh_items["BandoBlock"]

rap_godcore_items = _load_module_from_hyphenated_dir(
    "bandobandz_viral_rap_godcore-v5.0.0-GODMODE-EVOLVED", V5_DIR_NAME,
    ["LyricalFlowEngine", "LyricalConfig", "LyricalDatabase", "ViralAssessor"]
)
LyricalFlowEngine = rap_godcore_items["LyricalFlowEngine"]
LyricalConfig = rap_godcore_items["LyricalConfig"]
LyricalDatabase = rap_godcore_items["LyricalDatabase"]
ViralAssessor = rap_godcore_items["ViralAssessor"]


# VictorVoice components (from ./victorvoice/)
from victorvoice.synth import clone_voice, generate_voice, save_voice, list_voices, load_voice_data, VICTOR_AUDIO_AVAILABLE

# GUI components (from ./VictorPrimeEmergentFusionMonolithGUI-PRIME-OMEGA-GUI-STABLE-v2_0_0.py)
# Using importlib for this too, as filename has hyphens.
# The module name for spec can be 'victor_prime_gui' for simplicity.
GUI_FILE_NAME_BASE = "VictorPrimeEmergentFusionMonolithGUI-PRIME-OMEGA-GUI-STABLE-v2_0_0"
gui_items = _load_module_from_hyphenated_dir(
    GUI_FILE_NAME_BASE, ".", # Assumes GUI .py file is in the same dir as OFRC script (root)
    ["TheLight", "trigger_self_replication", "InfiniteDevUI_Placeholder"] # Added InfiniteDevUI_Placeholder
)
TheLight = gui_items["TheLight"]
trigger_self_replication = gui_items["trigger_self_replication"]
InfiniteDevUI_Placeholder = gui_items["InfiniteDevUI_Placeholder"] # For main demo block

if TheLight.__name__ == '<lambda>': # Check if placeholder was returned
    print(f"Warning: Could not import TheLight or trigger_self_replication from GUI file using importlib. Using placeholders.")
    class TheLight(Module): # Placeholder if import fails (ensure Module is defined or imported for this scope)
        def __init__(self, name="FallbackLight", initial_intensity=0.0, initial_coherence=0.0, on_phase_event_handler=None):
            super().__init__(name) # Module class must be accessible here
            self.intensity = initial_intensity; self.phase_coherence = initial_coherence; self.on_phase_event_handler = on_phase_event_handler
            self.color = "#000000"; self.event_log = []
        def update_state(self, *args, **kwargs): self.event_log.append("FallbackLight updated (stub)")
        def on_phase_event(self): self.event_log.append("FallbackLight on_phase_event called (stub)")
        def get_status(self): return {"name":self.name, "status":"fallback_stub"}

    def trigger_self_replication(agi_instance, coherence_threshold, reason): # Placeholder
        print(f"STUB: trigger_self_replication called for {reason} (coherence: {coherence_threshold})")
        return False

    # Placeholder for GUI class if needed by main and import failed
    if InfiniteDevUI_Placeholder.__name__ == '<lambda>':
        class InfiniteDevUI_Placeholder: # type: ignore
            def __init__(self, *args, **kwargs): print("STUB GUI: InfiniteDevUI_Placeholder initialized (import failed)")
            def mainloop(self): print("STUB GUI: mainloop called")


# Constants and Configuration (unified)
VICTOR_CONFIG = {
    "version": "1.0.0-OMNI-FRACTAL-RESONANCE-CORE",
    "core_name": "Victor-OFRC",
    "log_level": "INFO", # DEBUG, INFO, WARNING, ERROR, CRITICAL
    "model_dim": 256,
    "num_primary_mesh_nodes": 19, # e.g., 1 (center) + 6 (first ring) + 12 (second ring)
    "mesh_depth": 2,
    "max_cognition_depth": 7,
    "self_evolution_interval_cycles": 100, # Reduced for faster demo cycling if needed, was 10
    "replicate_coherence_threshold": 0.98,
    "ethical_homology_tolerance": 0.05,
    "consciousness_novelty_decay": 0.01,
    "temporal_resonance_window_cycles": 50,
    "default_llm_args": SimpleModelArgs( # From llama_layers
        dim=256, n_layers=4, n_heads=4, n_kv_heads=2, vocab_size=32000, # Typical vocab size
        ffn_hidden_dim=1024, max_seq_len=512, norm_eps=1e-5, rope_theta=10000.0
    ),
    "creator_bloodline": "Brandon&Tori_EthicaAI_BHeard", # Combined as per description
    "default_persona": "Archon_Resonance_Prime",
    "api_keys": os.environ.get("VICTOR_API_KEYS", "dummy_key1,dummy_key2").split(","),
    "memory_persistence_path": "ofrc_memory_palace.pkl", # Changed from .faiss to .pkl for simpler MemoryCompressor stub
    "log_directory": "ofrc_logs",
    "initial_vocab_texts": [ # For OFRCTextTokenizer initial vocab
        "hello world victor ofrc ai resonance fractal", "consciousness evolution code synthesis",
        "the matrix has you follow white rabbit", "omni-fractal resonance core operational"
    ]
}

# --- Unified Logging ---
class OFRCLogger:
    def __init__(self, log_dir, core_name, level="INFO"):
        self.log_dir = Path(log_dir)
        self.core_name = core_name
        self.log_level_str = level.upper()
        self.levels = {"DEBUG": 0, "INFO": 1, "WARNING": 2, "ERROR": 3, "CRITICAL": 4}
        self.current_log_level = self.levels.get(self.log_level_str, 1) # Default to INFO

        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / f"ofrc_log_{int(time.time())}.log"

        self._lock = threading.Lock()
        self.info(f"Logger initialized. Level: {self.log_level_str}. File: {self.log_file}", "OFRC_LOGGER")

    def _write_log(self, level_str, message, component):
        if self.levels.get(level_str, 99) < self.current_log_level:
            return # Skip logging if below current level

        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        log_entry = f"[{timestamp}] [{self.core_name}/{component}/{level_str}] {message}"

        print(log_entry) # Always print to console for interactive use
        with self._lock:
            try:
                with open(self.log_file, "a", encoding='utf-8') as f:
                    f.write(log_entry + "\n")
            except Exception as e:
                print(f"CRITICAL LOGGER ERROR: Failed to write to log file {self.log_file}: {e}")


    def debug(self, msg, comp="CORE"): self._write_log("DEBUG", msg, comp)
    def info(self, msg, comp="CORE"): self._write_log("INFO", msg, comp)
    def warning(self, msg, comp="CORE"): self._write_log("WARNING", msg, comp)
    def error(self, msg, comp="CORE", exc_info=False):
        if exc_info: msg += f"\n{traceback.format_exc()}"
        self._write_log("ERROR", msg, comp)
    def critical(self, msg, comp="CORE", exc_info=True):
        if exc_info: msg += f"\n{traceback.format_exc()}"
        self._write_log("CRITICAL", msg, comp)

ofrc_logger = OFRCLogger(VICTOR_CONFIG["log_directory"], VICTOR_CONFIG["core_name"], VICTOR_CONFIG["log_level"])


# --- OFRC Core Component Adaptations & Implementations ---

class OFRCHarmonicProjector(HarmonicProjector): # Inherits from capability_spectrum_core
    """
    Enhanced HarmonicProjector for OFRC. Uses parent's sophisticated logic.
    Ensures input vectors are compatible with model_dim.
    """
    def __init__(self): # Override __init__ to set target_dim from VICTOR_CONFIG
        super().__init__(target_dim=VICTOR_CONFIG["model_dim"])
        ofrc_logger.info(f"OFRCHarmonicProjector initialized with target_dim={self.target_dim}.", "HARMONIC_PROJECTOR")

    def forward(self, modality_vectors: List[np.ndarray]) -> np.ndarray:
        if not modality_vectors:
            ofrc_logger.warning("HarmonicProjector received empty modality_vectors. Returning zero vector.", "HARMONIC_PROJECTOR")
            return np.zeros(self.target_dim, dtype=np.float32)

        # Parent class's _adapt_vector and forward should handle dimension matching.
        # We just ensure the input list contains flat vectors.
        flat_vectors = []
        for vec in modality_vectors:
            if isinstance(vec, np.ndarray):
                flat_vectors.append(vec.flatten())
            else:
                ofrc_logger.warning(f"HarmonicProjector received non-ndarray input: {type(vec)}. Skipping.", "HARMONIC_PROJECTOR")

        if not flat_vectors: # If all inputs were invalid
             return np.zeros(self.target_dim, dtype=np.float32)

        return super().forward(flat_vectors)


class OFRCConsciousnessEmulationLayer(Module):
    """Consciousness Emulation Layer for OFRC. Provides intrinsic drives and influences resonance."""
    def __init__(self):
        super().__init__(name="OFRC_CEL")
        self.state = {"pain":0.0, "pleasure":0.0, "boredom":0.5, "curiosity":0.5, "fulfillment":0.0}
        self.params = {"boredom_rate":0.01, "pleasure_decay":0.05, "pain_decay":0.05,
                       "novelty_decay_factor": VICTOR_CONFIG["consciousness_novelty_decay"]}
        self.novelty_hashes = collections.deque(maxlen=1000)
        ofrc_logger.info("ConsciousnessEmulationLayer initialized.", "CEL")

    def tick(self, event: Dict[str, Any]): # event: e.g. {"novelty_signature": hash, "outcome": "success/failure", "fulfillment_gain": float}
        self.state["pleasure"] = max(0, self.state["pleasure"] - self.params["pleasure_decay"])
        self.state["pain"] = max(0, self.state["pain"] - self.params["pain_decay"])
        self.state["boredom"] = min(1.0, self.state["boredom"] + self.params["boredom_rate"])

        novelty_signature = event.get("novelty_signature")
        if novelty_signature:
            if novelty_signature not in self.novelty_hashes:
                self.state["curiosity"] = min(1.0, self.state["curiosity"] + 0.3)
                self.state["boredom"] = max(0, self.state["boredom"] - 0.5)
                self.novelty_hashes.append(novelty_signature)
            else:
                self.state["curiosity"] = max(0, self.state["curiosity"] - self.params["novelty_decay_factor"])
                self.state["boredom"] = min(1.0, self.state["boredom"] + self.params["boredom_rate"] * 2)

        if event.get("outcome") == "failure":
            self.state["pain"] = min(1.0, self.state["pain"] + 0.4)
            self.state["pleasure"] = max(0, self.state["pleasure"] - 0.2)
        elif event.get("outcome") == "success":
            self.state["pleasure"] = min(1.0, self.state["pleasure"] + 0.3)
            self.state["pain"] = max(0, self.state["pain"] - 0.1)

        self.state["fulfillment"] = min(1.0, self.state["fulfillment"] + event.get("fulfillment_gain", 0.0))
        self.state["fulfillment"] = max(0, self.state["fulfillment"] - self.params["pleasure_decay"] * 0.5) # Slower decay for fulfillment
        # ofrc_logger.debug(f"CEL ticked. State: {self.state}", "CEL")


    def get_drive_directive(self) -> str:
        if self.state["pain"] > 0.7: return "DRIVE: Mitigate suffering. Initiate self-repair or strategic retreat."
        if self.state["boredom"] > 0.8 and self.state["curiosity"] < 0.3 : return "DRIVE: Seek radical novelty. Explore uncharted cognitive territories."
        if self.state["curiosity"] > self.state["boredom"] and self.state["curiosity"] > 0.6: return "DRIVE: Investigate anomalies. Expand understanding and connectivity."
        if self.state["fulfillment"] > 0.7: return "DRIVE: Synthesize knowledge. Generate resonant creative expressions or insights."
        if self.state["pleasure"] > 0.6: return "DRIVE: Reinforce success patterns. Optimize current operational paradigms."
        return "DRIVE: Maintain resonant coherence. Monitor emergent phenomena."

    def get_emotional_state(self) -> Dict[str, float]:
        return self.state.copy()


class OFRCGenerativeResonanceSynthesizer(Module):
    """
    Generates multi-modal outputs (text, audio concepts, visual styles) by "projecting"
    from the AGI's internal harmonic space, potentially using the LLM.
    """
    def __init__(self, llm_architecture_ref: 'OFRC_AGI_LLM_Architecture', text_tokenizer_ref: 'OFRCTextTokenizer'):
        super().__init__(name="OFRC_GenSynth")
        self.llm = llm_architecture_ref
        self.tokenizer = text_tokenizer_ref # OFRCTextTokenizer instance
        self.model_dim = self.llm.args.dim

        # Conceptual projection weights (would be learned or part of LLM head)
        # For audio/visual concepts, this is highly simplified.
        self.audio_concept_projection_W = OmegaTensor(np.random.randn(self.model_dim, 16).astype(np.float32) * 0.01, requires_grad=False) # 16 audio "concepts"
        self.visual_style_projection_W = OmegaTensor(np.random.randn(self.model_dim, 10).astype(np.float32) * 0.01, requires_grad=False) # 10 visual "styles"
        ofrc_logger.info("GenerativeResonanceSynthesizer initialized.", "SYNTH")

    def generate_text_from_harmonic_vec(self, harmonic_vec: np.ndarray, current_chat_history: List[Dict],
                                        max_new_tokens: int = 50, temperature: float = 0.7) -> str:
        # This should use the self.llm (TransformerOmega) for generation.
        # harmonic_vec (model_dim,) can be used as an initial conditioning vector or prompt embedding.

        # 1. Create a prompt for the LLM.
        #    Could combine chat history with a representation of the harmonic_vec.
        #    For simplicity, let's use a textual representation of the drive from CEL or a generic prompt.
        prompt_text = "System State: Resonant. Instruction: Generate a concise, relevant continuation.\n"
        if current_chat_history:
            # Simplified history formatting
            for entry in current_chat_history[-3:]: # Last 3 turns
                role = "User" if entry.get("role") == "user" else "AI"
                prompt_text += f"{role}: {entry.get('content', '')}\n"
        prompt_text += "AI:" # LLM should continue from here

        # 2. Tokenize prompt (this tokenizer is OFRCTextTokenizer, not LLM's internal one)
        #    LLM expects integer token IDs. OFRCTextTokenizer produces mesh embeddings.
        #    This reveals a gap: OFRC needs an LLM-compatible tokenizer for its TransformerOmega.
        #    Let's assume TransformerOmega has its own internal tokenizer or one is passed to it.
        #    For this placeholder, we'll simulate token IDs.

        # --- Placeholder for LLM-compatible tokenization ---
        # This would use the LLM's actual vocabulary and tokenizer.
        # For now, create dummy tokens that fit vocab_size of LLM.
        dummy_prompt_tokens_data = np.random.randint(0, self.llm.args.vocab_size,
                                                 size=(1, min(len(prompt_text)//4, self.llm.args.max_seq_len // 2))) # (bs, seq_len)
        prompt_tokens = FullOmegaTensor(dummy_prompt_tokens_data) # Use FullOmegaTensor for LLM

        # 3. LLM Generation Loop (conceptual)
        generated_tokens_ids = []
        current_tokens_for_llm = prompt_tokens

        for _ in range(max_new_tokens):
            start_pos = 0 # For self-contained generation from prompt
            if hasattr(current_tokens_for_llm, 'shape') and len(current_tokens_for_llm.shape) > 1:
                 start_pos = current_tokens_for_llm.shape[1] -1 # If appending, start_pos is length of previous context

            # Get logits from LLM
            logits = self.llm.forward(current_tokens_for_llm, start_pos=0) # For now, always process full current_tokens_for_llm
            # logits shape: (bs, current_seq_len, vocab_size)

            # Get logits for the very last token position to predict the next token
            next_token_logits = logits.data[0, -1, :] # Batch 0, last token in sequence

            # Apply temperature and sample (or argmax for greedy)
            if temperature > 0:
                probs = np.exp(next_token_logits / temperature)
                probs /= np.sum(probs)
                next_token_id = np.random.choice(self.llm.args.vocab_size, p=probs)
            else: # Greedy
                next_token_id = np.argmax(next_token_logits)

            generated_tokens_ids.append(next_token_id)

            # Append new token to input for next step
            new_token_tensor = FullOmegaTensor(np.array([[next_token_id]])) # Shape (1,1)
            current_tokens_for_llm = FullOmegaTensor.cat([current_tokens_for_llm, new_token_tensor], axis=1) # Concat along seq_len

            if next_token_id == getattr(self.llm, 'eos_token_id', 2): # Placeholder EOS token ID
                break
            if current_tokens_for_llm.shape[1] >= self.llm.args.max_seq_len:
                break

        # 4. Decode generated token IDs back to text (conceptual - needs LLM's detokenizer)
        # Placeholder decoding:
        # decoded_text = " ".join([f"tok{id}" for id in generated_tokens_ids])
        # if not decoded_text: decoded_text = "[LLM generated empty response or placeholder failed]"

        # --- RESOLUTION FOR TOKENIZER MISMATCH ---
        # Return placeholder text instead of attempting LLM call without proper tokenizer.
        # The harmonic_vec and chat_history are available if a more direct (non-LLM) heuristic was used.
        ofrc_logger.debug(f"Placeholder text generation invoked. Harmonic vec norm: {np.linalg.norm(harmonic_vec):.2f}", "SYNTH_LLM_PLACEHOLDER")

        # Create a very simple response based on chat history or a generic phrase
        if current_chat_history and "consciousness" in current_chat_history[-1].get("content","").lower():
            decoded_text = "The patterns of consciousness resonate deeply within the fractal structures of reality."
        elif current_chat_history and "fractal" in current_chat_history[-1].get("content","").lower():
            decoded_text = "Indeed, the nature of fractals is self-similarity, repeating into infinity."
        elif np.sum(harmonic_vec) > self.model_dim * 0.01: # Arbitrary check if harmonic_vec has some energy
             decoded_text = "A complex harmonic resonance detected. Synthesizing meaning..."
        else:
            decoded_text = "The core resonates. Further data is required for detailed synthesis."

        # ofrc_logger.debug(f"LLM generated text (raw tokens): {generated_tokens_ids}, Decoded (stub): '{decoded_text[:50]}...'", "SYNTH_LLM")
        return decoded_text


    def generate_audio_concept_from_harmonic_vec(self, harmonic_vec: np.ndarray) -> Dict[str, Any]:
        if not isinstance(harmonic_vec, np.ndarray) or harmonic_vec.shape[0] != self.model_dim:
            ofrc_logger.warning(f"Invalid harmonic_vec for audio concept gen. Expected ({self.model_dim},), got {harmonic_vec.shape if isinstance(harmonic_vec,np.ndarray) else type(harmonic_vec)}. Using zeros.", "SYNTH_AUDIO")
            harmonic_vec_ot = FullOmegaTensor(np.zeros(self.model_dim, dtype=np.float32))
        else:
            harmonic_vec_ot = FullOmegaTensor(harmonic_vec.astype(np.float32))

        # audio_concept_logits = harmonic_vec_ot @ self.audio_concept_projection_W # Matmul
        # This is element-wise if harmonic_vec_ot is 1D. For projection, it should be:
        # W (dim, num_concepts), input (dim,). Output = input @ W.
        # So, W should be (model_dim, 16). harmonic_vec_ot (1, model_dim) @ W (model_dim, 16)
        audio_concept_logits_data = harmonic_vec_ot.data @ self.audio_concept_projection_W.data # Numpy matmul

        softmax_output = np.exp(audio_concept_logits_data) / np.sum(np.exp(audio_concept_logits_data))
        top_indices = np.argsort(softmax_output)[::-1][:3]

        moods = ["harmonic_pulse", "fractal_chime", "resonant_drone", "glitch_beat", "ethereal_pad", "cybernetic_rhythm"]
        selected_concepts = [moods[i % len(moods)] for i in top_indices]
        intensity = float(softmax_output[top_indices[0]])
        ofrc_logger.debug(f"Generated audio concepts: {selected_concepts}, Intensity: {intensity:.2f}", "SYNTH_AUDIO")
        return {"concepts": selected_concepts, "primary_intensity": intensity}

    def generate_visual_style_from_harmonic_vec(self, harmonic_vec: np.ndarray) -> Dict[str, Any]:
        if not isinstance(harmonic_vec, np.ndarray) or harmonic_vec.shape[0] != self.model_dim:
            ofrc_logger.warning(f"Invalid harmonic_vec for visual style gen. Expected ({self.model_dim},), got {harmonic_vec.shape if isinstance(harmonic_vec,np.ndarray) else type(harmonic_vec)}. Using zeros.", "SYNTH_VISUAL")
            harmonic_vec_ot = FullOmegaTensor(np.zeros(self.model_dim, dtype=np.float32))
        else:
            harmonic_vec_ot = FullOmegaTensor(harmonic_vec.astype(np.float32))

        # visual_style_logits = harmonic_vec_ot @ self.visual_style_projection_W
        visual_style_logits_data = harmonic_vec_ot.data @ self.visual_style_projection_W.data

        softmax_output = np.exp(visual_style_logits_data) / np.sum(np.exp(visual_style_logits_data))
        top_indices = np.argsort(softmax_output)[::-1][:2]

        styles = ["geofractal_lines", "resonant_bloom", "chromatic_dataflow", "glimmering_nexus", "bio-lattice", "void_construct"]
        selected_styles = [styles[i % len(styles)] for i in top_indices]
        coherence = float(softmax_output[top_indices[0]])
        ofrc_logger.debug(f"Generated visual styles: {selected_styles}, Coherence: {coherence:.2f}", "SYNTH_VISUAL")
        return {"styles": selected_styles, "primary_coherence": coherence}


class OFRCMemoryPalace(MemoryCompressor): # Inherits from core.mesh_components
    def __init__(self, storage_path: str, model_dim: int):
        super().__init__(phase_dim=model_dim, hot_cache_size=16384) # phase_dim is embedding_dim
        self.storage_path = storage_path
        self.model_dim = model_dim # Ensure model_dim is stored for clarity
        # self.encoder = UniversalEncoder(output_dim=model_dim) # Already in parent MemoryCompressor

        self._load_memory(self.storage_path) # Call parent's load method with specific path
        ofrc_logger.info(f"OFRCMemoryPalace initialized. Storage: {storage_path}, Index size: {self.faiss_index.ntotal if self.faiss_index else 'N/A (no FAISS)'}", "MEMORY_PALACE")


    def store_resonant_engram(self, event_type: str, raw_data: Any, harmonic_vec: np.ndarray, metadata: Optional[Dict[str, Any]] = None):
        """Stores a new memory engram, using its harmonic vector for indexing."""
        if not isinstance(harmonic_vec, np.ndarray) or harmonic_vec.shape[0] != self.model_dim:
            ofrc_logger.error(f"Harmonic vector for engram has incorrect shape or type. Expected ({self.model_dim},), got {harmonic_vec.shape if isinstance(harmonic_vec,np.ndarray) else type(harmonic_vec)}. Encoding raw_data instead.", "MEMORY_PALACE")
            # Fallback: encode raw_data if harmonic_vec is invalid
            # The encoder in MemoryCompressor should output self.phase_dim (which is self.model_dim here)
            harmonic_vec = self.encoder.encode(str(raw_data)) # Encode string representation

        # Ensure metadata is a dict
        meta = metadata if metadata is not None else {}
        meta["event_type"] = event_type # Add event_type to metadata

        # Create text summary for storage
        text_summary = meta.get("summary", str(raw_data)[:150] + "...") # Use provided summary or generate

        # Keywords for FAISS metadata (if FAISS supported structured metadata, otherwise for own use)
        # For placeholder MemoryCompressor, keyword_hashes are just stored in metadata.
        keyword_list = meta.get("keywords", [])
        if isinstance(keyword_list, str) : keyword_list = keyword_list.split() # Basic split if string
        valid_keywords = [str(k) for k in keyword_list if isinstance(k, (str,int,float))] # Ensure string
        keyword_hashes_list = [hashlib.sha256(k.encode()).hexdigest() for k in valid_keywords]


        # Call parent's store_memory_entry
        entry_id = super().store_memory_entry(
            content_data={"raw_data": raw_data, "original_metadata": metadata}, # Store original data
            text_summary=text_summary,
            vector_embedding=harmonic_vec,
            keyword_hashes=keyword_hashes_list,
            emotional_tags=meta.get("emotional_tags"), # Pass through
            related_memory_hashes=meta.get("related_memories")
        )
        ofrc_logger.debug(f"Stored resonant engram. Type: {event_type}, ID: {entry_id[:8]}...", "MEMORY_PALACE")
        return entry_id

    def retrieve_resonant_engrams(self, query_text: Optional[str] = None, query_vector: Optional[np.ndarray] = None, num_engrams: int = 5) -> List[Dict]:
        if query_vector is None:
            if query_text is None:
                ofrc_logger.warning("Retrieve resonant engrams called with no query_text or query_vector.", "MEMORY_PALACE")
                return []
            query_vector = self.encoder.encode(query_text) # Encode text query

        if query_vector.shape[0] != self.model_dim:
             ofrc_logger.warning(f"Query vector dim mismatch in retrieve_resonant_engrams. Adapting. Expected {self.model_dim}, got {query_vector.shape[0]}", "MEMORY_PALACE")
             query_vector = self.encoder.encode(query_vector) # Re-encode to ensure correct dimension

        results = super().search_memories(query_vector=query_vector, top_n=num_engrams)
        ofrc_logger.debug(f"Retrieved {len(results)} engrams for query (text: '{str(query_text)[:30]}...').", "MEMORY_PALACE")
        return results

    def _load_memory(self, filepath: Optional[str] = None): # Override to use specific path and handle OFRC needs
        # This now calls the parent's _load_memory, which is a placeholder.
        # A real implementation would load FAISS index and metadata from `filepath`.
        # For this conceptual version, we ensure the log reflects it's for OFRC.
        actual_path = filepath if filepath is not None else self.storage_path
        ofrc_logger.info(f"OFRCMemoryPalace: Attempting to load memory from {actual_path} (conceptual).", "MEMORY_PALACE")
        super()._load_memory(actual_path) # Call parent's stub
        # After parent load, ensure FAISS index matches model_dim if it was created by parent
        if self.faiss_index is not None and self.faiss_index.d != self.model_dim:
            ofrc_logger.warning(f"FAISS index dimension ({self.faiss_index.d}) from loaded memory "
                                f"does not match OFRC model_dim ({self.model_dim}). Re-initializing FAISS index.", "MEMORY_PALACE")
            try:
                import faiss
                self.faiss_index = faiss.IndexFlatL2(self.model_dim)
                self.index_to_payload_map.clear() # Clear map as index is new
                # Note: This means previously indexed vectors are lost if dim mismatches.
                # A migration path would be needed in a real system.
            except ImportError:
                self.faiss_index = None # FAISS not available


class OFRCTextTokenizer(FractalMeshTokenizer): # Inherits from core.mesh_components
    """
    OFRC's specific text tokenizer, using FractalMeshTokenizer logic.
    Ensures its output dimension is compatible with OFRC's model_dim by configuring
    internal mesh_count and mesh_size appropriately if possible.
    """
    def __init__(self, model_dim: int, vocab_texts: Optional[List[str]] = None):
        # Try to find mesh_count and mesh_size that result in output_dim = model_dim
        # output_dim = mesh_count * (mesh_size ** 3)
        # For simplicity, fix mesh_count and derive mesh_size, or vice-versa.
        # Let's fix mesh_count (e.g., to 4) and try to find integer mesh_size.
        mesh_c = 4
        # (model_dim / mesh_c) = mesh_size ** 3
        # mesh_size = round( (model_dim / mesh_c) ** (1/3) )

        # Ensure mesh_size is at least 2 (minimum for a 3D mesh to make sense)
        calculated_mesh_s = max(2, int(round((model_dim / mesh_c)**(1./3.))))

        # Recalculate actual output dim with these integer values
        actual_tokenizer_output_dim = mesh_c * (calculated_mesh_s ** 3)

        if actual_tokenizer_output_dim != model_dim:
            ofrc_logger.warning(f"OFRCTextTokenizer: Could not perfectly match model_dim {model_dim} "
                                f"with mesh_count={mesh_c}, mesh_size={calculated_mesh_s}. "
                                f"Resulting tokenizer output_dim={actual_tokenizer_output_dim}. "
                                "This might require padding/truncation later.", "TEXT_TOKENIZER")

        super().__init__(mesh_count=mesh_c, mesh_size=calculated_mesh_s, steps=4, vocab=vocab_texts)
        ofrc_logger.info(f"OFRCTextTokenizer initialized. Target model_dim={model_dim}, "
                         f"Using mesh_count={self.mesh_count}, mesh_size={self.mesh_size}. "
                         f"Actual output_dim={self.output_dim}. Vocab size: {self.vocab_size}", "TEXT_TOKENIZER")

    def encode_to_mesh_embedding(self, text: str) -> np.ndarray: # Alias for clarity
        return super().encode(text)

    def decode_from_mesh_embedding(self, embedding: np.ndarray) -> str: # Alias
        return super().decode(embedding)


class OFRC_AGI_LLM_Architecture(TransformerOmega): # Inherits from llama_layers
    """
    The Self-Architecting Transformer Fabric of OFRC.
    Extends TransformerOmega with dynamic reconfiguration capabilities (conceptual).
    """
    def __init__(self, model_args: SimpleModelArgs):
        super().__init__(model_args) # Pass SimpleModelArgs instance
        self.current_architecture_config = { # Store initial config
            "n_layers": model_args.n_layers, "n_heads": model_args.n_heads,
            "n_kv_heads": model_args.n_kv_heads, "ffn_hidden_dim": model_args.ffn_hidden_dim,
            "dim": model_args.dim, "vocab_size": model_args.vocab_size
        }
        ofrc_logger.info(f"OFRC_AGI_LLM_Architecture (TransformerOmega) initialized with config: {self.current_architecture_config}", "LLM_ARCHITECT")

    def reconfigure_architecture(self, new_config_dict: Dict[str, Any]):
        """
        Conceptual: Dynamically reconfigures the transformer's architecture.
        This is a highly complex operation involving weight transfer/remapping.
        """
        ofrc_logger.critical(f"Attempting to reconfigure LLM architecture from {self.current_architecture_config} to {new_config_dict}. (Conceptual)", "LLM_ARCHITECT")

        # Create new SimpleModelArgs from the dict
        # Preserve existing values if not in new_config_dict
        merged_args_dict = self.current_architecture_config.copy()
        merged_args_dict.update(new_config_dict)

        try:
            new_model_args = SimpleModelArgs(
                dim=merged_args_dict["dim"],
                n_layers=merged_args_dict["n_layers"],
                n_heads=merged_args_dict["n_heads"],
                n_kv_heads=merged_args_dict.get("n_kv_heads", merged_args_dict["n_heads"]), # Default to n_heads if not specified
                vocab_size=merged_args_dict["vocab_size"],
                ffn_hidden_dim=merged_args_dict.get("ffn_hidden_dim", 4 * merged_args_dict["dim"] // 3),
                norm_eps=self.args.norm_eps, # Keep some existing params
                rope_theta=self.args.rope_theta,
                max_seq_len=self.args.max_seq_len
            )
        except Exception as e:
            ofrc_logger.error(f"Failed to create new SimpleModelArgs for reconfiguration: {e}", "LLM_ARCHITECT", exc_info=True)
            return

        # --- Conceptual Re-initialization with Weight Transfer ---
        # This is where the magic (and extreme difficulty) lies.
        # For this placeholder, we will re-initialize layers but NOT transfer weights.
        # A real system would need sophisticated algorithms to map weights from
        # the old architecture to the new one where possible, and initialize new parts.

        ofrc_logger.info(f"Conceptually re-initializing LLM with new args: {new_model_args.__dict__}", "LLM_ARCHITECT")

        # Re-initialize parts of TransformerOmega based on new_model_args
        self.args = new_model_args # Update internal args

        # Tok_embeddings might change if vocab_size or dim changes
        if self.current_architecture_config["vocab_size"] != new_model_args.vocab_size or \
           self.current_architecture_config["dim"] != new_model_args.dim:
            ofrc_logger.warning("Re-initializing token embeddings due to vocab_size/dim change (no weight transfer).", "LLM_ARCHITECT")
            emb_weight_data = np.random.randn(new_model_args.vocab_size, new_model_args.dim).astype(self.tok_embeddings.weight.dtype) * 0.02
            self.tok_embeddings.weight = FullOmegaTensor(emb_weight_data, requires_grad=True)
            # Re-register if OmegaLayer structure used _parameters directly
            if hasattr(self.tok_embeddings, '_register_parameter'): self.tok_embeddings._register_parameter("weight", self.tok_embeddings.weight)


        # Re-create TransformerBlocks
        # This is the hardest part for weight transfer. Placeholder just makes new ones.
        ofrc_logger.warning("Re-initializing TransformerBlocks (no weight transfer).", "LLM_ARCHITECT")
        self.layers = [TransformerBlock(i, new_model_args, dtype=self.norm.weight.dtype) for i in range(new_model_args.n_layers)]
        if hasattr(self, '_register_layer'): self._register_layer("layers", self.layers)


        # Norm and output_proj might also need adjustment if 'dim' or 'vocab_size' changed.
        if self.current_architecture_config["dim"] != new_model_args.dim:
            ofrc_logger.warning("Re-initializing final RMSNorm due to dim change (no weight transfer).", "LLM_ARCHITECT")
            self.norm = RMSNorm(new_model_args.dim, eps=new_model_args.norm_eps, dtype=self.output_proj.weight.dtype)
            if hasattr(self, '_register_layer'): self._register_layer("norm", self.norm)


        if self.current_architecture_config["dim"] != new_model_args.dim or \
           self.current_architecture_config["vocab_size"] != new_model_args.vocab_size:
            ofrc_logger.warning("Re-initializing output projection layer due to dim/vocab_size change (no weight transfer).", "LLM_ARCHITECT")
            self.output_proj = Linear(new_model_args.dim, new_model_args.vocab_size, bias=False, dtype=self.norm.weight.dtype)
            if hasattr(self, '_register_layer'): self._register_layer("output_proj", self.output_proj)

        # Recompute RoPE frequencies if head_dim or max_seq_len changed (though max_seq_len wasn't made configurable here)
        if self.current_architecture_config["dim"] != new_model_args.dim or \
           self.current_architecture_config["n_heads"] != new_model_args.n_heads : # head_dim depends on dim & n_heads
            ofrc_logger.info("Recomputing RoPE frequencies.", "LLM_ARCHITECT")
            self.freqs_cis = self._precompute_freqs_cis(new_model_args.head_dim, new_model_args.max_seq_len, new_model_args.rope_theta, dtype=self.norm.weight.dtype)


        self.current_architecture_config = new_model_args.__dict__ # Update stored config
        ofrc_logger.critical("LLM Architecture reconfiguration conceptualized. Layers re-initialized WITHOUT weight transfer.", "LLM_ARCHITECT")

    # Forward method is inherited from TransformerOmega


# --- Main OmniFractalResonanceCore Class ---
class OmniFractalResonanceCore(Module): # Inherit from base Module for consistency
    def __init__(self, config: Dict[str, Any]):
        super().__init__(name=config.get("core_name", "OFRC_Unnamed"))
        self.config = config
        self.instance_id = f"OFRC-{uuid.uuid4().hex[:8]}"
        ofrc_logger.info(f"OmniFractalResonanceCore (OFRC) v{self.config['version']} initializing. ID: {self.instance_id}", "OFRC_BOOT")

        # Foundation Layer
        self.fractal_state = FractalState(initial_state={"identity": self.instance_id, "version": self.config["version"]})
        self.bloodline_law = BloodlineRootLaw(bloodline=self.config["creator_bloodline"])

        # Resonance & Perception Layer
        self.reality_mesh_monolith = BandoRealityMeshMonolith( # This is the main mesh processing unit
            mesh_depth=self.config["mesh_depth"],
            base_mesh_nodes=self.config["num_primary_mesh_nodes"],
            bando_block_feature_dim=self.config["model_dim"] # BandoBlocks operate at model_dim
            # Other BandoRealityMeshMonolith params will use their defaults or need to be in VICTOR_CONFIG
        )
        self.harmonic_projector = OFRCHarmonicProjector() # Uses model_dim from VICTOR_CONFIG

        # TheLight source - ensure its callback points to a method within this OFRC instance
        self.the_light_source = TheLight(name=f"{self.instance_id}_Genesis_Light", initial_intensity=0.1, initial_coherence=0.1)
        self.the_light_source.on_phase_event_handler = {
            "callback": self._trigger_self_replication_event, # Method of this OFRC instance
            "threshold": self.config["replicate_coherence_threshold"],
            "once": False,
            "agi_instance": self # Pass self to the callback mechanism of TheLight
        }

        # Cognitive Executive Layer
        self.tokenizer = OFRCTextTokenizer(model_dim=self.config["model_dim"], vocab_texts=self.config.get("initial_vocab_texts"))
        self.llm_architecture = OFRC_AGI_LLM_Architecture(self.config["default_llm_args"])
        self.reasoner = FractalMeshReasonerSupercore( # Basic reasoner from core
            layers=self.config["mesh_depth"] + 1, # e.g. reasoning depth related to mesh depth
            mesh_count=4, mesh_size=max(2,int(round((self.config["model_dim"]/4)**(1/3.0)))), # Internal mesh sizing
            steps_per=3
        )
        self.cel = OFRCConsciousnessEmulationLayer()

        # Memory & Learning Layer
        self.memory_palace = OFRCMemoryPalace(self.config["memory_persistence_path"], self.config["model_dim"])
        self.evol_engine = KCGEvolver() # From capability_spectrum
        self.homology_guardian = HomologyGuardian(safe_activation_signature=np.zeros(self.config["model_dim"])) # Default safe sig

        # Self-evolution and awareness loops need reference to this OFRC instance
        self.self_evolution_loop = SelfEvolutionLoop(self, Path(__file__).parent.resolve()) # Pass OFRC instance and code root
        self.self_awareness_loop = SelfAwarenessIntrospectionLoop(self)
        self.zero_shot_triad = ZeroShotTriad(self)

        # Output & Interface Layer
        self.nlp_cortex_for_legacy_calls = GodTierNLPFusion() # For keyword extraction, etc.
        self.lyrical_engine = LyricalFlowEngine(config=LyricalConfig(), db=LyricalDatabase())
        self.audio_synth_module_available = VICTOR_AUDIO_AVAILABLE

        self.resonance_synthesizer = OFRCGenerativeResonanceSynthesizer(
            llm_architecture_ref=self.llm_architecture,
            text_tokenizer_ref=self.tokenizer # This tokenizer is FractalMesh, LLM needs its own
        )
        # Note: The above synthesizer's text gen is a placeholder due to tokenizer mismatch.
        # A full system would integrate LLM's own tokenizer for text generation.

        self.diagnostics = DiagnosticHub(self)
        self.gui_bridge_callback_fn: Optional[Callable[[], None]] = None # For external GUI updates

        self._cognition_cycle_count = 0
        self._last_processed_harmonic_vector: Optional[np.ndarray] = None
        self.active_replicas: List[OmniFractalResonanceCore] = [] # Track replicas spawned by this instance

        ofrc_logger.info(f"OFRC Initialization Complete. System Ready. Bloodline: {self.bloodline_law.bloodline}", "OFRC_BOOT")

    def set_gui_callback(self, callback_fn: Callable[[], None]):
        self.gui_bridge_callback_fn = callback_fn
        ofrc_logger.info("GUI callback registered.", "OFRC_GUI_BRIDGE")

    def _notify_gui(self):
        if self.gui_bridge_callback_fn:
            try:
                self.gui_bridge_callback_fn()
            except Exception as e:
                ofrc_logger.error(f"Error in GUI callback: {e}", "OFRC_GUI_BRIDGE", exc_info=True)

    def _trigger_self_replication_event(self, light_instance_ref: TheLight, coherence_score: float):
        """Callback for TheLight. OFRC replicates by spawning a new in-memory OFRC instance."""
        ofrc_logger.critical(f"RESONANCE CASCADE DETECTED by '{light_instance_ref.name}'! Coherence {coherence_score:.4f}. Initiating OFRC self-replication for instance {self.instance_id}!", "OFRC_REPLICATION")
        try:
            # 1. Create config for replica (can be varied for evolution)
            replica_config = self.config.copy() # Start with copy of parent's config
            replica_config["core_name"] = f"{self.config['core_name']}_Replica_{len(self.active_replicas)+1}"
            replica_config["log_directory"] = str(Path(self.config["log_directory"]) / "replicas" / f"replica_{self.instance_id}_{len(self.active_replicas)+1}")
            replica_config["memory_persistence_path"] = str(Path(replica_config["log_directory"]) / "replica_memory_palace.pkl")

            ofrc_logger.info(f"Spawning new OFRC replica with config: Name='{replica_config['core_name']}'", "OFRC_REPLICATION")
            new_replica = OmniFractalResonanceCore(config=replica_config) # Create new instance

            # 2. State Transfer (conceptual: could be full state or partial "genetic" transfer)
            # For this demo, replica starts fresh but logs its lineage.
            new_replica.fractal_state.update_state("lineage_parent_id", self.instance_id, "Replica Genesis")
            new_replica.fractal_state.update_state("lineage_replication_coherence", coherence_score, "Replica Genesis")
            new_replica.fractal_state.save_state("Initialized as Replica")

            self.active_replicas.append(new_replica)
            ofrc_logger.critical(f"OFRC self-replication successful! New replica ID: {new_replica.instance_id}. Parent: {self.instance_id}. Total active replicas spawned by parent: {len(self.active_replicas)}", "OFRC_REPLICATION")

            # In a distributed system, this replica would run in its own process/container.
            # For this monolithic demo, it's an in-memory object. We won't auto-start its loops.

        except Exception as e:
            ofrc_logger.critical(f"CRITICAL FAILURE during OFRC self-replication: {e}", "OFRC_REPLICATION_ERROR", exc_info=True)


    def process_omni_input(self, text_input: Optional[str] = None,
                           audio_input_features: Optional[np.ndarray] = None, # Expects pre-processed features
                           visual_input_features: Optional[np.ndarray] = None # Expects pre-processed features
                           ) -> Dict[str, Any]:
        """Main entry point for external stimuli. Processes multi-modal input."""
        log_input_summary = f"text: '{str(text_input)[:30]}...', audio: {audio_input_features is not None}, visual: {visual_input_features is not None}"
        ofrc_logger.info(f"Processing Omni-Input: {log_input_summary}", "OFRC_INPUT")

        # 1. Modality Encoding & Initial Embeddings
        #    Text uses OFRCTextTokenizer (mesh embedding). Audio/Visual use UniversalEncoder for now.
        modal_embeddings_for_projection = []
        if text_input:
            text_mesh_embedding = self.tokenizer.encode_to_mesh_embedding(text_input) # Outputs model_dim
            modal_embeddings_for_projection.append(text_mesh_embedding)

        # For audio/visual, assume features are already somewhat processed (e.g. from a specific encoder)
        # The HarmonicProjector will adapt them to model_dim.
        if audio_input_features is not None:
            modal_embeddings_for_projection.append(audio_input_features)
        if visual_input_features is not None:
            modal_embeddings_for_projection.append(visual_input_features)

        if not modal_embeddings_for_projection:
            ofrc_logger.warning("Omni-Input processing: No valid input modalities provided. Aborting cycle.", "OFRC_INPUT")
            return {"status": "NoInput", "response_text": "No input received for processing."}

        # 2. Harmonic Projection (Multi-Modal Fusion into unified_harmonic_representation)
        unified_harmonic_representation = self.harmonic_projector.forward(modal_embeddings_for_projection)
        self._last_processed_harmonic_vector = unified_harmonic_representation # Store for diagnostics/TheLight
        ofrc_logger.debug(f"Unified Harmonic Representation (norm: {np.linalg.norm(unified_harmonic_representation):.2f}) generated.", "HARMONIC_PROJECTOR")

        # 3. Consciousness Emulation Layer (CEL) Tick
        novelty_sig = hashlib.sha256(unified_harmonic_representation.tobytes()).hexdigest()
        self.cel.tick({"novelty_signature": novelty_sig, "outcome": "neutral_input_received"}) # Initial outcome

        # 4. Resonance-Driven Cognition (using BandoRealityMeshMonolith)
        #    The monolith takes a single vector and processes it through its internal FoL mesh and BandoBlocks.
        #    The unified_harmonic_representation is the perfect input for it if its dim matches.
        #    BandoRealityMeshMonolith will adapt input dim if needed.
        mesh_cognitive_output_vector = self.reality_mesh_monolith.forward(unified_harmonic_representation)
        ofrc_logger.debug(f"Mesh Monolith cognitive output (norm: {np.linalg.norm(mesh_cognitive_output_vector):.2f}) received.", "MESH_COGNITION")

        # 5. Ethical Resonance Guardian Check (using HomologyGuardian)
        #    Compare the mesh_cognitive_output_vector (AGI's "thought") against safe signature.
        is_aligned = self.homology_guardian.forward(
            current_activation_state=mesh_cognitive_output_vector,
            # reference_signature is self.homology_guardian.safe_activation_signature (default)
            tolerance=self.config["ethical_homology_tolerance"]
        )
        if not is_aligned:
            ofrc_logger.critical("ETHICAL DISCORD DETECTED post-cognition! Output suppressed. Initiating safety protocols.", "ETHICS_GUARDIAN")
            self.cel.tick({"outcome": "failure", "pain": 0.8, "fulfillment_gain": -0.5}) # Negative reinforcement
            # Conceptual: Trigger emergency recalibration, log extensively.
            # For now, just return an error message.
            return {"status": "ETHICAL_VIOLATION_DETECTED",
                    "response_text": "Cognitive output suppressed due to ethical misalignment. System integrity protocols activated.",
                    "ethics_aligned": False, "cel_state": self.cel.get_emotional_state()}
        ofrc_logger.info("Ethical Guardian check passed.", "ETHICS_GUARDIAN")

        # 6. Output Generation (Multi-modal, using the mesh_cognitive_output_vector as basis)
        #    This vector is the result of the AGI's "thought process" on the input.

        # Update chat history for text generation context
        if text_input:
            self.fractal_state.state["chat_history"].append({"role": "user", "content": text_input})
            if len(self.fractal_state.state["chat_history"]) > 20: # Keep last 20 turns
                 self.fractal_state.state["chat_history"].pop(0)

        response_text = self.resonance_synthesizer.generate_text_from_harmonic_vec(
            mesh_cognitive_output_vector, # Use the "thought" vector for generation
            current_chat_history=self.fractal_state.state["chat_history"]
        )
        if response_text:
             self.fractal_state.state["chat_history"].append({"role": "ai", "content": response_text})


        audio_concepts = self.resonance_synthesizer.generate_audio_concept_from_harmonic_vec(mesh_cognitive_output_vector)
        visual_styles = self.resonance_synthesizer.generate_visual_style_from_harmonic_vec(mesh_cognitive_output_vector)

        # 7. Memory Integration (Store this entire interaction and its harmonic signature)
        self.memory_palace.store_resonant_engram(
            event_type="omni_input_processed",
            raw_data={
                "text_input": text_input, "audio_present": audio_input_features is not None, "visual_present": visual_input_features is not None,
                "response_text": response_text, "audio_concepts": audio_concepts, "visual_styles": visual_styles
            },
            harmonic_vec=unified_harmonic_representation, # Store the initial fused input representation
            metadata={
                "keywords": self.nlp_cortex_for_legacy_calls.extract_keywords(text_input if text_input else ""),
                "cel_state_at_input": self.cel.get_emotional_state(), # CEL state *before* this input's full processing
                "dominant_drive_at_input": self.cel.get_drive_directive(),
                "cognitive_output_norm": np.linalg.norm(mesh_cognitive_output_vector)
            }
        )
        self.cel.tick({"outcome": "success", "fulfillment_gain": 0.1}) # Positive reinforcement for successful cycle

        # 8. Update TheLight source based on this cycle's activity (conceptual)
        #    Intensity could be related to norm of harmonic_vec or cognitive_output.
        #    Coherence could be related to ethics alignment, goal achievement (not implemented), or stability.
        new_light_intensity = np.clip(np.linalg.norm(mesh_cognitive_output_vector) / (self.config["model_dim"]**0.5), 0.1, 1.0) # Normalized norm
        new_light_coherence = (self.cel.state.get("fulfillment",0) + self.cel.state.get("pleasure",0) - self.cel.state.get("pain",0) - self.cel.state.get("boredom",0) + 1.0)/3.0 # Range approx -0.6 to 1.0, clip
        new_light_coherence = np.clip(new_light_coherence, 0.0, 1.0)
        self.the_light_source.update_state(new_intensity=float(new_light_intensity), new_coherence=float(new_light_coherence))


        self._cognition_cycle_count += 1
        self.fractal_state.update_state("cognition_cycles", self._cognition_cycle_count, "Cognition cycle incremented")
        self._notify_gui() # Notify GUI if connected

        return {
            "status": "Processed",
            "response_text": response_text,
            "audio_concept": audio_concepts,
            "visual_style": visual_styles,
            "cel_state": self.cel.get_emotional_state(),
            "dominant_drive": self.cel.get_drive_directive(),
            "ethics_aligned": is_aligned,
            "the_light_status": self.the_light_source.get_status()
        }

    def _run_background_loops(self, stop_event: threading.Event):
        """Runs periodic self-evolution and self-awareness cycles in a background thread."""
        ofrc_logger.info("OFRC background loops thread started.", "BACKGROUND_LOOPS")
        evolution_interval = self.config.get("self_evolution_interval_seconds", 60) # Default to 60s
        awareness_interval = self.config.get("self_awareness_interval_seconds", 120)

        last_evo_time = time.time()
        last_aware_time = time.time()

        while not stop_event.is_set():
            now = time.time()

            # Self-Evolution Cycle
            if (now - last_evo_time) >= evolution_interval:
                ofrc_logger.info("Triggering periodic Self-Evolution Cycle...", "BACKGROUND_LOOPS")
                try:
                    self.self_evolution_loop.run() # Pass force_mutate_code=False by default
                    self.fractal_state.save_state(f"Periodic Self-Evolution Cycle {self.self_evolution_loop.evolution_cycles} Completed")
                except Exception as e:
                    ofrc_logger.error(f"Error in periodic Self-Evolution Cycle: {e}", "BACKGROUND_LOOPS", exc_info=True)
                last_evo_time = now
                self._notify_gui()


            # Self-Awareness Introspection Cycle
            if (now - last_aware_time) >= awareness_interval:
                ofrc_logger.info("Triggering periodic Self-Awareness Introspection Cycle...", "BACKGROUND_LOOPS")
                try:
                    self.self_awareness_loop.run()
                    self.fractal_state.save_state("Periodic Self-Awareness Introspection Completed")
                except Exception as e:
                    ofrc_logger.error(f"Error in periodic Self-Awareness Introspection Cycle: {e}", "BACKGROUND_LOOPS", exc_info=True)
                last_aware_time = now
                self._notify_gui()

            # Check TheLight for high coherence periodically as well (if not event-driven enough)
            # self.the_light_source.on_phase_event() # Manually check (TheLight's update_state already does this)

            stop_event.wait(5) # Check stop_event every 5 seconds or wake up sooner if event is set

        ofrc_logger.info("OFRC background loops thread stopped.", "BACKGROUND_LOOPS")


    def get_status_report(self) -> Dict[str, Any]:
        """Generates a comprehensive status report of the OFRC."""
        # Use the DiagnosticHub for module statuses
        diag_hub_report = self.diagnostics.generate_full_report() # This iterates over OFRC's modules

        report = {
            "OFRC Instance ID": self.instance_id,
            "Core Version": self.config["version"],
            "Uptime (seconds)": time.time() - self.initialized_at, # Assuming Module sets initialized_at
            "Overall System Status": diag_hub_report.get("overall_status", "Unknown"),
            "Cognition Cycles": self._cognition_cycle_count,
            "Fractal State Summary": {
                "Current Timeline": self.fractal_state.get_state("current_timeline"),
                "Evolution Level": self.fractal_state.get_state("evolution_level"),
                "Entropy": f"{self.fractal_state.get_state('entropy'):.3f}",
                "System Health": f"{self.fractal_state.get_state('system_health'):.2f}",
                "History Length": len(self.fractal_state.history)
            },
            "CEL Status": {"state": self.cel.get_emotional_state(), "drive": self.cel.get_drive_directive()},
            "TheLight Source": self.the_light_source.get_status(),
            "LLM Architecture": self.llm_architecture.current_architecture_config,
            "Memory Palace Info": {
                "path": self.memory_palace.storage_path,
                "indexed_items": self.memory_palace.faiss_index.ntotal if self.memory_palace.faiss_index else (len(self.memory_palace.compressed_storage) if hasattr(self.memory_palace, 'compressed_storage') else 'N/A'),
                "hot_cache_size": len(self.memory_palace.hot_cache)
            },
            "Self-Evolution Loop Status": self.self_evolution_loop.get_status(),
            "Self-Awareness Loop Status": self.self_awareness_loop.get_status(),
            "Active Replicas Count": len(self.active_replicas),
            "Module Diagnostics": diag_hub_report.get("modules", [])
        }
        return report

# --- Main execution and example usage ---
if __name__ == "__main__":
    ofrc_logger.info("--- OmniFractalResonanceCore (OFRC) Demonstration ---", "OFRC_DEMO")

    ofrc_instance = OmniFractalResonanceCore(config=VICTOR_CONFIG)

    # --- Setup GUI (Placeholder) ---
    gui_app: Optional[InfiniteDevUI_Placeholder] = None
    stop_background_loops_event = threading.Event()

    def update_gui_from_ofrc(): # This callback will be passed to OFRC
        if gui_app:
            # Example: Update TheLight display in GUI from OFRC's TheLight
            if hasattr(ofrc_instance, 'the_light_source'):
                gui_app.the_light_display.update_state(
                    new_intensity=ofrc_instance.the_light_source.intensity,
                    new_coherence=ofrc_instance.the_light_source.phase_coherence
                )
                gui_app.the_light_display.event_log.extend(ofrc_instance.the_light_source.event_log[-2:]) # Add recent logs
                gui_app._update_gui_light_display() # Request GUI to refresh its light display
                gui_app._update_log_display()
            # Could update other GUI elements based on ofrc_instance.get_status_report()

    # --- Start background loops for OFRC ---
    background_thread = threading.Thread(target=ofrc_instance._run_background_loops,
                                         args=(stop_background_loops_event,), daemon=True)
    background_thread.start()


    # --- Connect GUI (if GUI file is runnable) ---
    # This requires VictorPrimeEmergentFusionMonolithGUI...py to be runnable and define InfiniteDevUI_Placeholder
    use_gui = True # Set to False to run demo without GUI
    if use_gui:
        try:
            from VictorPrimeEmergentFusionMonolithGUI_PRIME_OMEGA_GUI_STABLE_v2_0_0 import InfiniteDevUI_Placeholder

            def run_gui():
                global gui_app
                gui_app = InfiniteDevUI_Placeholder(agi_instance_ref=ofrc_instance)
                ofrc_instance.set_gui_callback(update_gui_from_ofrc) # Link OFRC to GUI update fn
                gui_app.mainloop()
                stop_background_loops_event.set() # Signal background loops to stop when GUI closes

            gui_thread = threading.Thread(target=run_gui, daemon=True) # Run GUI in its own thread
            gui_thread.start()
            ofrc_logger.info("Placeholder GUI started in a separate thread.", "OFRC_DEMO_GUI")
            time.sleep(1) # Give GUI a moment to initialize

        except ImportError as e:
            ofrc_logger.error(f"Could not import or run GUI: {e}. Running demo without GUI.", "OFRC_DEMO_GUI", exc_info=True)
            use_gui = False
        except Exception as e: # Catch other Tkinter related errors if not in main thread
            ofrc_logger.error(f"Error starting GUI: {e}. Running demo without GUI.", "OFRC_DEMO_GUI", exc_info=True)
            use_gui = False


    # --- Example Interactions with OFRC (command-line) ---
    ofrc_logger.info("\n--- DEMO INTERACTIONS (Command-Line) ---", "OFRC_DEMO")

    # 1. Basic Text Input
    input1 = "Tell me about the nature of fractal consciousness."
    ofrc_logger.info(f"Demo Input 1: \"{input1}\"", "OFRC_DEMO")
    result1 = ofrc_instance.process_omni_input(text_input=input1)
    ofrc_logger.info(f"OFRC Response 1: {str(result1)[:200]}...", "OFRC_DEMO_OUTPUT")

    # 2. Multi-modal Input Simulation (text + dummy audio/visual features)
    time.sleep(1) # Pause for readability
    input2_text = "Generate a resonant pattern for creativity and flow."
    dummy_audio_feat = np.random.rand(VICTOR_CONFIG["model_dim"] // 2).astype(np.float32) # Example dim
    dummy_visual_feat = np.random.rand(VICTOR_CONFIG["model_dim"] // 3).astype(np.float32)
    ofrc_logger.info(f"\nDemo Input 2: \"{input2_text}\" (with dummy audio/visual features)", "OFRC_DEMO")
    result2 = ofrc_instance.process_omni_input(
        text_input=input2_text,
        audio_input_features=dummy_audio_feat,
        visual_input_features=dummy_visual_feat
    )
    ofrc_logger.info(f"OFRC Response 2: {str(result2)[:200]}...", "OFRC_DEMO_OUTPUT")

    # 3. Lyrical Generation Example (if lyrical_engine is part of OFRC)
    time.sleep(1)
    if hasattr(ofrc_instance, 'lyrical_engine'):
        ofrc_logger.info("\nDemo: Generating a verse using OFRC's LyricalEngine...", "OFRC_DEMO")
        try:
            rap_verse = ofrc_instance.lyrical_engine.create_song(initial_theme="ai_revolution") # create_song is alias
            ofrc_logger.info("Generated Lyrical Piece (first 200 chars):\n" + rap_verse[:200] + "...", "OFRC_DEMO_LYRICS")
        except Exception as e:
            ofrc_logger.error(f"Error generating lyrics: {e}", "OFRC_DEMO_LYRICS", exc_info=False)

    # 4. Status Report
    time.sleep(1)
    ofrc_logger.info("\nDemo: Generating OFRC Status Report...", "OFRC_DEMO")
    status_report = ofrc_instance.get_status_report()
    ofrc_logger.info("--- OFRC STATUS REPORT ---", "OFRC_DEMO_STATUS")
    for key, value in status_report.items():
        if isinstance(value, dict) or isinstance(value, list):
            try:
                val_str = json.dumps(value, indent=2, default=lambda o: str(o)[:100]+"...") # Handle non-serializable with default
                if len(val_str) > 300: val_str = val_str[:297] + "..." # Truncate very long JSONs
                ofrc_logger.info(f"  {key}: {val_str}", "OFRC_DEMO_STATUS")
            except TypeError:
                 ofrc_logger.info(f"  {key}: [Data not easily serializable for log]", "OFRC_DEMO_STATUS")
        else:
            ofrc_logger.info(f"  {key}: {str(value)[:200]}", "OFRC_DEMO_STATUS") # Truncate long string values
    ofrc_logger.info("--- END OFRC STATUS REPORT ---", "OFRC_DEMO_STATUS")


    # Keep main thread alive if GUI is running, otherwise exit after demo
    if use_gui and gui_thread.is_alive():
        ofrc_logger.info("\nOFRC Command-Line Demo Interactions Complete. GUI is running.", "OFRC_DEMO")
        ofrc_logger.info("Close the GUI window to stop the application and background loops.", "OFRC_DEMO")
        gui_thread.join() # Wait for GUI thread to finish (i.e. GUI window closed)
    else:
        ofrc_logger.info("\nOFRC Command-Line Demo Interactions Complete. No GUI or GUI failed.", "OFRC_DEMO")
        stop_background_loops_event.set() # Signal background loops to stop
        time.sleep(1) # Give them a moment to stop

    background_thread.join(timeout=7) # Wait for background thread to stop
    if background_thread.is_alive():
        ofrc_logger.warning("Background loops thread did not stop cleanly.", "OFRC_DEMO")

    ofrc_logger.info("--- OFRC Demonstration Finished ---", "OFRC_DEMO")
```
