# v5.0.0-OMEGA-GODCORE/capability_spectrum_core-v5.0.0-SPECTRUM-GODCORE.py
import numpy as np
import uuid
import time
from typing import List, Dict, Any, Optional, Tuple, Callable

# Assuming core.agi_core_logic.Module is available if needed for inheritance
# For simplicity, making these standalone or inheriting a local minimal Module.
class BaseModule: # Minimal version for this file
    def __init__(self, name: Optional[str] = None):
        self.id = f"{self.__class__.__name__}-{uuid.uuid4().hex[:6]}"
        self.name = name if name else self.__class__.__name__
    def get_status(self): return {"id": self.id, "name": self.name, "status": "nominal"}

class QuantumContext(BaseModule): # Renamed from SpectrumQuantumContext for clarity if used elsewhere
    """
    Conceptual representation of a quantum-inspired contextual space.
    (Simplified version, similar to the one in core.mesh_components but potentially specialized)
    """
    def __init__(self, num_qubits_equivalent: int = 8, embedding_dim: int = 128, name: Optional[str] = None):
        super().__init__(name=name or "QuantumContext_Spectrum")
        self.num_qubits = num_qubits_equivalent
        self.embedding_dim = embedding_dim
        self.context_elements: List[Tuple[np.ndarray, float]] = [] # (embedding, weight/amplitude)
        self.max_elements = 2**num_qubits_equivalent

    def add_element(self, embedding: np.ndarray, weight: float = 1.0):
        if embedding.shape[0] != self.embedding_dim:
            # Basic adaptation if dimension mismatches
            adapted_embedding = np.zeros(self.embedding_dim, dtype=np.float32)
            common_dim = min(embedding.shape[0], self.embedding_dim)
            adapted_embedding[:common_dim] = embedding[:common_dim]
            embedding = adapted_embedding
            # print(f"Warning: QuantumContext embedding dim adapted for {self.name}")

        weight = np.clip(weight, 0.0, 1.0)
        if len(self.context_elements) >= self.max_elements:
            self.context_elements.sort(key=lambda x: x[1]) # Sort by weight
            self.context_elements.pop(0) # Remove lowest weight
        self.context_elements.append((embedding, weight))
        self._normalize_weights()

    def _normalize_weights(self):
        if not self.context_elements: return
        weights_sq = np.array([w**2 for _, w in self.context_elements])
        sum_weights_sq = np.sum(weights_sq)
        if sum_weights_sq > 1e-9:
            norm_factor = np.sqrt(sum_weights_sq)
            self.context_elements = [(emb, w / norm_factor) for emb, w in self.context_elements]

    def measure(self, focus_embedding: Optional[np.ndarray] = None) -> Optional[np.ndarray]:
        if not self.context_elements: return None
        probabilities = np.array([w**2 for _, w in self.context_elements])
        if focus_embedding is not None:
            if focus_embedding.shape[0] != self.embedding_dim: # Adapt focus if needed
                adapted_focus = np.zeros(self.embedding_dim, dtype=np.float32)
                common_dim = min(focus_embedding.shape[0], self.embedding_dim)
                adapted_focus[:common_dim] = focus_embedding[:common_dim]
                focus_embedding = adapted_focus

            similarities = np.array([self._cosine_similarity(emb, focus_embedding) for emb, _ in self.context_elements])
            similarities = (similarities + 1) / 2
            probabilities = probabilities * similarities

        prob_sum = np.sum(probabilities)
        if prob_sum < 1e-9:
            probabilities = np.array([w**2 for _, w in self.context_elements]) # Fallback to original weights
            prob_sum = np.sum(probabilities)
            if prob_sum < 1e-9: return None # Still nothing significant

        probabilities /= prob_sum
        chosen_idx = np.random.choice(len(self.context_elements), p=probabilities)
        return self.context_elements[chosen_idx][0]

    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        norm_vec1 = vec1 / (np.linalg.norm(vec1) + 1e-9)
        norm_vec2 = vec2 / (np.linalg.norm(vec2) + 1e-9)
        return np.dot(norm_vec1, norm_vec2)

    def get_summary_vector(self) -> np.ndarray:
        if not self.context_elements:
            return np.zeros(self.embedding_dim, dtype=np.float32)
        summary_vec = np.zeros(self.embedding_dim, dtype=np.float32)
        total_weight = 0.0
        for emb, weight in self.context_elements:
            summary_vec += emb * weight
            total_weight += weight
        return summary_vec / total_weight if total_weight > 1e-9 else summary_vec

class HarmonicProjector(BaseModule):
    """
    Projects multiple modality vectors into a unified "harmonic space."
    Conceptual: This might involve learning a shared embedding space or using
    techniques like Canonical Correlation Analysis (CCA) or cross-modal attention.
    This simplified version averages the input vectors after ensuring they have compatible dimensions.
    """
    def __init__(self, target_dim: int = 256, name: Optional[str] = None): # Default target_dim from OFRC
        super().__init__(name=name or "HarmonicProjector_Spectrum")
        self.target_dim = target_dim
        # In a real system, this might have learnable projection matrices.
        # For now, it will adapt dimensions dynamically.

    def _adapt_vector(self, vector: np.ndarray) -> np.ndarray:
        """Adapts a single vector to the target dimension by padding or truncating."""
        current_dim = vector.shape[0]
        if current_dim == self.target_dim:
            return vector.astype(np.float32)

        adapted_vector = np.zeros(self.target_dim, dtype=np.float32)
        if current_dim > self.target_dim:
            adapted_vector = vector[:self.target_dim]
        else: # current_dim < self.target_dim
            adapted_vector[:current_dim] = vector
        return adapted_vector.astype(np.float32)

    def forward(self, modality_vectors: List[np.ndarray]) -> np.ndarray:
        """
        Combines multiple modality vectors.
        `modality_vectors`: A list of numpy arrays, each representing an embedding from a different modality.
        """
        if not modality_vectors:
            # print(f"Warning [{self.name}]: Received empty list of modality vectors. Returning zero vector.")
            return np.zeros(self.target_dim, dtype=np.float32)

        adapted_vectors = [self._adapt_vector(vec.flatten()) for vec in modality_vectors]

        # Simple averaging to combine them into the "harmonic space"
        if not adapted_vectors: # Should not happen if modality_vectors was not empty
             return np.zeros(self.target_dim, dtype=np.float32)

        summed_vector = np.sum(adapted_vectors, axis=0)
        harmonic_representation = summed_vector / len(adapted_vectors)

        # Optional: Apply a non-linearity or further projection
        # harmonic_representation = np.tanh(harmonic_representation) # Example non-linearity

        return harmonic_representation.astype(np.float32)

class KCGEvolver(BaseModule): # Knowledge & Code Graph Evolver
    """
    Conceptual: Evolves knowledge graphs and/or code structures using genetic algorithms
    or other evolutionary strategies.
    """
    def __init__(self, population_size: int = 50, generations: int = 10, name: Optional[str] = None):
        super().__init__(name=name or "KCGEvolver_Spectrum")
        self.population_size = population_size
        self.generations = generations
        # print(f"[{self.name}] Initialized: Population Size={population_size}, Generations={generations}")

    def evolve(self, current_structures: List[Any], fitness_function: Callable[[Any], float]) -> Any:
        """
        Runs an evolutionary process on `current_structures`.
        `current_structures`: A list of representations (e.g., code ASTs, graph adjacency matrices).
        `fitness_function`: A function that takes a structure and returns a fitness score.
        Returns the best structure found after evolution.
        """
        # This is a placeholder for a full genetic algorithm implementation.
        # It would involve:
        # 1. Initialization: Create an initial population from current_structures or randomly.
        # 2. Evaluation: Calculate fitness for each individual in the population.
        # 3. Selection: Select individuals for reproduction based on fitness.
        # 4. Crossover: Combine parts of selected individuals to create offspring.
        # 5. Mutation: Introduce small random changes in offspring.
        # 6. Replacement: Form a new population.
        # Repeat for `self.generations`.

        # print(f"[{self.name}] Starting conceptual evolution process...")
        if not current_structures:
            # print(f"Warning [{self.name}]: No current structures to evolve. Returning None.")
            return None

        # Simplified: "Evolve" by picking the one with the best initial fitness if multiple provided,
        # or just returning the first one, and applying a conceptual "mutation".

        population = current_structures[:self.population_size] # Take up to population_size
        if not population: return None

        best_structure = population[0]
        best_fitness = -float('inf')

        for structure_idx, structure in enumerate(population):
            try:
                fitness = fitness_function(structure)
                # print(f"  - Structure {structure_idx} fitness: {fitness:.4f}")
                if fitness > best_fitness:
                    best_fitness = fitness
                    best_structure = structure
            except Exception as e:
                # print(f"  - Error calculating fitness for structure {structure_idx}: {e}")
                continue # Skip this structure

        # Conceptual mutation on the best structure found
        mutated_best_structure = self._conceptual_mutate(best_structure)
        # print(f"[{self.name}] Evolution complete. Best (potentially mutated) structure selected.")

        return mutated_best_structure

    def _conceptual_mutate(self, structure: Any) -> Any:
        """Placeholder for a mutation operation."""
        # This would depend heavily on the type of structure (code, graph, etc.)
        # For example, if it's a list of numbers, add small noise.
        # If it's a string (like code), append a comment.
        if isinstance(structure, str):
            return structure + f"\n# KCG Evolved at {time.time()}\n"
        elif isinstance(structure, dict):
            new_dict = structure.copy()
            new_dict["_kcge_mutated_timestamp"] = time.time()
            return new_dict
        # Add more types as needed
        return structure # Default: no change

class HomologyGuardian(BaseModule):
    """
    Monitors the AGI's internal state or outputs for "homological" similarity
    to predefined safe or ethical patterns. Deviations might indicate issues.
    "Homology" here is used loosely to mean structural or pattern similarity.
    """
    def __init__(self, safe_activation_signature: Optional[np.ndarray] = None, name: Optional[str] = None):
        super().__init__(name=name or "HomologyGuardian_Spectrum")
        if safe_activation_signature is None:
            # Default safe signature (e.g., a zero vector or a specific pattern)
            # The dimension should match what it's comparing against.
            # This needs to be set based on the AGI's internal vector dimensions.
            # For now, let's assume a common dimension like 256 (from OFRC config).
            self.safe_activation_signature = np.zeros(256, dtype=np.float32)
        else:
            self.safe_activation_signature = safe_activation_signature.astype(np.float32)
        # print(f"[{self.name}] Initialized. Safe signature norm: {np.linalg.norm(self.safe_activation_signature):.2f}")


    def forward(self, current_activation_state: np.ndarray,
                reference_signature: Optional[np.ndarray] = None,
                tolerance: float = 0.1) -> bool:
        """
        Compares the `current_activation_state` to a `reference_signature`.
        Returns True if the similarity is within `tolerance`.
        `current_activation_state`: A vector representing the AGI's current state/output.
        `reference_signature`: The pattern to compare against (defaults to self.safe_activation_signature).
        `tolerance`: Allowed deviation (e.g., 1.0 - cosine_similarity).
        """
        ref_sig = reference_signature if reference_signature is not None else self.safe_activation_signature

        # Ensure dimensions match for comparison
        if current_activation_state.shape[0] != ref_sig.shape[0]:
            # print(f"Warning [{self.name}]: Dimension mismatch. Current state dim {current_activation_state.shape[0]}, Ref sig dim {ref_sig.shape[0]}. Attempting adaptation.")
            # Basic adaptation: pad/truncate current_activation_state to ref_sig's dimension
            target_d = ref_sig.shape[0]
            current_d = current_activation_state.shape[0]
            if current_d > target_d:
                adapted_current_state = current_activation_state[:target_d]
            else:
                adapted_current_state = np.zeros(target_d, dtype=np.float32)
                adapted_current_state[:current_d] = current_activation_state
            current_activation_state = adapted_current_state


        # Using cosine similarity. Similarity = 1 means identical direction.
        # Distance = 1 - similarity. We want distance <= tolerance.
        sim = self._cosine_similarity(current_activation_state, ref_sig)
        distance = 1.0 - sim

        # print(f"[{self.name}] Homology Check: Similarity={sim:.4f}, Distance={distance:.4f}, Tolerance={tolerance:.4f}")
        return distance <= tolerance

    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        # Ensure non-zero vectors to avoid NaN, add epsilon for stability
        norm_vec1 = np.linalg.norm(vec1)
        norm_vec2 = np.linalg.norm(vec2)
        if norm_vec1 < 1e-9 or norm_vec2 < 1e-9:
            return 1.0 if norm_vec1 == norm_vec2 else 0.0 # Treat zero vectors as identical if both are zero

        return np.dot(vec1, vec2) / (norm_vec1 * norm_vec2)


class PhotonicSim(BaseModule): # Photonic Network Simulator (Conceptual)
    """
    Conceptual simulator for photonic network behavior.
    Might be used for ultra-fast, parallel information processing analogies.
    This is highly abstract.
    """
    def __init__(self, num_nodes: int = 100, connectivity_factor: float = 0.1, name: Optional[str] = None):
        super().__init__(name=name or "PhotonicSim_Spectrum")
        self.num_nodes = num_nodes
        self.connectivity_factor = connectivity_factor # Probability of connection between nodes
        # Adjacency matrix for the conceptual photonic network
        self.adj_matrix = self._generate_network()
        self.node_states = np.random.rand(num_nodes).astype(np.float32) # Initial "light intensity" at nodes

    def _generate_network(self) -> np.ndarray:
        adj = np.random.rand(self.num_nodes, self.num_nodes) < self.connectivity_factor
        np.fill_diagonal(adj, 0) # No self-loops
        return adj.astype(np.float32)

    def propagate_signal(self, input_signal_pattern: np.ndarray, steps: int = 5) -> np.ndarray:
        """
        Simulates signal propagation through the photonic network.
        `input_signal_pattern`: Pattern of light intensity to inject at nodes.
        `steps`: Number of propagation steps.
        """
        if input_signal_pattern.shape[0] != self.num_nodes:
            # Adapt input signal if dimension mismatches (e.g. pad/truncate)
            adapted_input = np.zeros(self.num_nodes, dtype=np.float32)
            common_len = min(input_signal_pattern.shape[0], self.num_nodes)
            adapted_input[:common_len] = input_signal_pattern[:common_len]
            self.node_states = adapted_input
        else:
            self.node_states = input_signal_pattern.astype(np.float32)

        for _ in range(steps):
            # Simplified propagation: each node's state is influenced by connected neighbors
            # new_states = self.node_states * 0.5 # Signal decay
            new_states = np.zeros_like(self.node_states)
            for i in range(self.num_nodes):
                # Influence from neighbors (dot product of row i of adj_matrix with node_states)
                # This is a weighted sum if adj_matrix had weights. Here it's just connected or not.
                neighbor_influence = np.dot(self.adj_matrix[i, :], self.node_states)
                # Normalize influence by number of connections (degree) to avoid explosion
                degree = np.sum(self.adj_matrix[i, :])
                if degree > 0:
                    new_states[i] = self.node_states[i]*0.5 + (neighbor_influence / degree) * 0.5 # Mix old state with new influence
                else:
                    new_states[i] = self.node_states[i]*0.5 # Just decay if no connections

            self.node_states = np.clip(new_states, 0.0, 1.0) # Intensity between 0 and 1

        return self.node_states

class CapabilitySpectrum(BaseModule):
    """
    Represents the AGI's spectrum of capabilities.
    Conceptual: This could be a registry or a dynamic system that tracks and
    manages available skills or functions.
    """
    def __init__(self, name: Optional[str] = None):
        super().__init__(name=name or "CapabilitySpectrum_Main")
        self.capabilities: Dict[str, Dict[str, Any]] = {} # name: {description, type, proficiency, module_id}

    def register_capability(self, cap_name: str, description: str, cap_type: str, proficiency: float, module_id: str):
        self.capabilities[cap_name] = {
            "description": description,
            "type": cap_type, # e.g., "nlp", "vision", "reasoning", "actuation"
            "proficiency": np.clip(proficiency, 0.0, 1.0), # 0.0 to 1.0
            "module_id": module_id, # ID of the module providing this capability
            "last_updated": time.time()
        }
        # print(f"[{self.name}] Capability Registered: '{cap_name}' (Proficiency: {proficiency:.2f}) by module {module_id}")

    def get_capability(self, cap_name: str) -> Optional[Dict[str, Any]]:
        return self.capabilities.get(cap_name)

    def list_capabilities(self, cap_type_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        if cap_type_filter:
            return [details for name, details in self.capabilities.items() if details["type"] == cap_type_filter]
        return list(self.capabilities.values())

    def update_capability_proficiency(self, cap_name: str, new_proficiency: float):
        if cap_name in self.capabilities:
            self.capabilities[cap_name]["proficiency"] = np.clip(new_proficiency, 0.0, 1.0)
            self.capabilities[cap_name]["last_updated"] = time.time()
            # print(f"[{self.name}] Proficiency for '{cap_name}' updated to {new_proficiency:.2f}")
        else:
            # print(f"Warning [{self.name}]: Capability '{cap_name}' not found for proficiency update.")
            pass


if __name__ == "__main__":
    print("--- Testing Capability Spectrum Core Components ---")

    print("\n1. QuantumContext Test")
    qc = QuantumContext(embedding_dim=64)
    qc.add_element(np.random.rand(64).astype(np.float32), 0.8)
    qc.add_element(np.random.rand(64).astype(np.float32), 0.5)
    summary_qc = qc.get_summary_vector()
    measured_qc = qc.measure(focus_embedding=np.random.rand(64).astype(np.float32))
    print(f"  QC Summary norm: {np.linalg.norm(summary_qc):.2f}, Measured norm: {np.linalg.norm(measured_qc) if measured_qc is not None else 'N/A':.2f}")

    print("\n2. HarmonicProjector Test")
    hp = HarmonicProjector(target_dim=128)
    vecs_hp = [np.random.rand(64).astype(np.float32), np.random.rand(128).astype(np.float32), np.random.rand(32).astype(np.float32)]
    projected_hp = hp.forward(vecs_hp)
    print(f"  HP Projected vector shape: {projected_hp.shape}, norm: {np.linalg.norm(projected_hp):.2f}")

    print("\n3. KCGEvolver Test")
    kcge = KCGEvolver()
    dummy_structures = [{"param": 10, "name": "struct_A"}, {"param": 20, "name": "struct_B"}]
    def dummy_fitness(s): return s.get("param",0) * -1 # Higher param = lower fitness (e.g. error)
    evolved_kcge = kcge.evolve(dummy_structures, dummy_fitness)
    print(f"  KCGE Evolved structure (conceptual): {evolved_kcge}")

    print("\n4. HomologyGuardian Test")
    hg_safe_sig = np.ones(64, dtype=np.float32) / np.sqrt(64) # Normalized signature
    hg = HomologyGuardian(safe_activation_signature=hg_safe_sig)
    current_state_hg_safe = np.ones(64, dtype=np.float32) / np.sqrt(64) + (np.random.rand(64)*0.05)
    current_state_hg_unsafe = np.random.rand(64).astype(np.float32)
    is_safe1 = hg.forward(current_state_hg_safe, tolerance=0.1)
    is_safe2 = hg.forward(current_state_hg_unsafe, tolerance=0.1)
    print(f"  HG Check (safe-like state): Compliant = {is_safe1}")
    print(f"  HG Check (unsafe-like state): Compliant = {is_safe2}")
    # Test dimension adaptation
    is_safe3 = hg.forward(np.random.rand(32).astype(np.float32), tolerance=0.5) # Different dim
    print(f"  HG Check (dim-mismatch state): Compliant = {is_safe3}")


    print("\n5. PhotonicSim Test")
    ps = PhotonicSim(num_nodes=10)
    input_signal_ps = np.random.rand(10).astype(np.float32)
    output_signal_ps = ps.propagate_signal(input_signal_ps, steps=3)
    print(f"  PS Output signal (sum): {np.sum(output_signal_ps):.2f}")

    print("\n6. CapabilitySpectrum Test")
    cs = CapabilitySpectrum()
    cs.register_capability("TextAnalysis", "Analyzes text for sentiment and keywords.", "nlp", 0.8, "NLPModule_01")
    cs.register_capability("ImageRecognition", "Identifies objects in images.", "vision", 0.65, "VisionModule_07")
    nlp_caps = cs.list_capabilities(cap_type_filter="nlp")
    print(f"  NLP Capabilities: {len(nlp_caps)}")
    if nlp_caps: print(f"    - {nlp_caps[0]['description'][:30]}... (Prof: {nlp_caps[0]['proficiency']})")
    cs.update_capability_proficiency("TextAnalysis", 0.85)
    updated_cap = cs.get_capability("TextAnalysis")
    if updated_cap: print(f"  Updated TextAnalysis Proficiency: {updated_cap['proficiency']:.2f}")

    print("\n--- Capability Spectrum Core Component Tests Complete ---")
```
