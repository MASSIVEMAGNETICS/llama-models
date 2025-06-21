# core/mesh_components.py
import numpy as np
import uuid
import time
import json
import hashlib
import collections
from typing import List, Dict, Any, Optional, Tuple, Union, Callable

# --- Foundational Mesh & Memory Components ---

class UniversalEncoder:
    """
    A conceptual universal encoder. In a real system, this would use
    sophisticated models (e.g., Sentence Transformers, image encoders)
    to convert various data types into fixed-size vector embeddings.
    This simplified version uses hashing for non-numeric and direct pass-through/padding for numeric.
    """
    def __init__(self, output_dim: int = 256):
        self.output_dim = output_dim

    def encode(self, data: Any) -> np.ndarray:
        """Encodes various data types into a numpy vector."""
        if isinstance(data, np.ndarray):
            # If already a numpy array, try to reshape or pad/truncate
            flat_data = data.flatten()
            if flat_data.shape[0] == self.output_dim:
                return flat_data.astype(np.float32)
            elif flat_data.shape[0] > self.output_dim:
                return flat_data[:self.output_dim].astype(np.float32)
            else: # flat_data.shape[0] < self.output_dim
                padding = np.zeros(self.output_dim - flat_data.shape[0], dtype=np.float32)
                return np.concatenate([flat_data, padding]).astype(np.float32)
        elif isinstance(data, (list, tuple)) and all(isinstance(x, (int, float)) for x in data):
            # List or tuple of numbers
            arr = np.array(data, dtype=np.float32)
            return self.encode(arr) # Recurse with numpy array
        elif isinstance(data, str):
            # For strings, use a hashing approach to get a pseudo-embedding
            # This is NOT semantically meaningful like a real text embedding.
            # Produces a consistent vector for the same string.
            h = hashlib.sha256(data.encode()).digest() # 32 bytes
            # Convert hash bytes to a sequence of floats
            # Ensure we get output_dim floats
            num_repeats = (self.output_dim * 4 // len(h)) + 1 # Each float32 is 4 bytes
            full_hash_bytes = (h * num_repeats)[:self.output_dim * 4]
            vector = np.frombuffer(full_hash_bytes, dtype=np.float32)
            return vector / np.linalg.norm(vector) if np.linalg.norm(vector) > 0 else vector # Normalize
        elif isinstance(data, (int, float)):
            # For single numbers, create a simple sparse representation
            vector = np.zeros(self.output_dim, dtype=np.float32)
            # Place the number at an index derived from its hash, and its value normalized
            idx = abs(hash(data)) % self.output_dim
            vector[idx] = np.tanh(float(data)) # Normalize with tanh
            return vector
        else:
            # For other data types, convert to string and hash (fallback)
            try:
                s_data = json.dumps(data, sort_keys=True)
            except TypeError:
                s_data = str(data)
            return self.encode(s_data) # Recurse with string representation

    def __call__(self, data: Any) -> np.ndarray:
        return self.encode(data)

class RippleEcho3DMesh:
    """
    Represents a single 3D mesh structure that can propagate signals (ripples).
    Each node in the mesh has a state vector. Ripples are simulated by updating
    node states based on their neighbors.
    """
    def __init__(self, mesh_size: int = 5, feature_dim: int = 64, activation_fn: str = "relu"):
        if not isinstance(mesh_size, int) or mesh_size <= 0:
            raise ValueError("Mesh size must be a positive integer.")
        if not isinstance(feature_dim, int) or feature_dim <= 0:
            raise ValueError("Feature dimension must be a positive integer.")

        self.mesh_size = mesh_size  # e.g., 5 for a 5x5x5 mesh
        self.feature_dim = feature_dim # Dimension of the vector at each mesh node
        self.mesh = np.random.rand(mesh_size, mesh_size, mesh_size, feature_dim).astype(np.float32) * 0.1 # Initialize small random values

        self.activation_fn_name = activation_fn
        if activation_fn == "relu":
            self.activation = lambda x: np.maximum(0, x)
        elif activation_fn == "tanh":
            self.activation = np.tanh
        elif activation_fn == "sigmoid":
            self.activation = lambda x: 1 / (1 + np.exp(-x))
        else:
            self.activation = lambda x: x # Linear activation

        # Precompute neighbor offsets for efficiency
        self.neighbor_offsets = []
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                for k in [-1, 0, 1]:
                    if i == 0 and j == 0 and k == 0:
                        continue
                    self.neighbor_offsets.append((i, j, k))

        self.decay_factor = 0.95 # How much signal decays per step
        self.influence_factor = 0.1 # How much neighbors influence a node

    def _get_neighbors_sum(self, x: int, y: int, z: int) -> np.ndarray:
        """Calculates the sum of feature vectors of neighboring nodes."""
        sum_vec = np.zeros(self.feature_dim, dtype=np.float32)
        valid_neighbors_count = 0
        for dx, dy, dz in self.neighbor_offsets:
            nx, ny, nz = x + dx, y + dy, z + dz
            if 0 <= nx < self.mesh_size and 0 <= ny < self.mesh_size and 0 <= nz < self.mesh_size:
                sum_vec += self.mesh[nx, ny, nz, :]
                valid_neighbors_count +=1

        return sum_vec / valid_neighbors_count if valid_neighbors_count > 0 else sum_vec


    def ripple(self, steps: int = 1):
        """Simulates the ripple effect for a number of steps."""
        for _ in range(steps):
            new_mesh_state = self.mesh.copy() * self.decay_factor # Apply decay to current state
            for i in range(self.mesh_size):
                for j in range(self.mesh_size):
                    for k in range(self.mesh_size):
                        neighbor_influence = self._get_neighbors_sum(i, j, k)
                        # Update node state: current decayed state + influence from neighbors
                        new_mesh_state[i, j, k, :] += self.influence_factor * neighbor_influence

            self.mesh = self.activation(new_mesh_state) # Apply activation function

    def inject_signal(self, position: Tuple[int, int, int], signal_vector: np.ndarray):
        """Injects a signal (feature vector) at a specific position in the mesh."""
        x, y, z = position
        if not (0 <= x < self.mesh_size and 0 <= y < self.mesh_size and 0 <= z < self.mesh_size):
            # print(f"Warning: Signal injection position {position} is out of bounds for mesh size {self.mesh_size}.")
            # Option: wrap around or clamp (here, we'll clamp)
            x = max(0, min(x, self.mesh_size - 1))
            y = max(0, min(y, self.mesh_size - 1))
            z = max(0, min(z, self.mesh_size - 1))

        if signal_vector.shape[0] != self.feature_dim:
            raise ValueError(f"Signal vector dimension {signal_vector.shape[0]} does not match mesh feature dimension {self.feature_dim}.")

        # Add signal to existing node state (or replace, depending on desired behavior)
        self.mesh[x, y, z, :] += signal_vector
        self.mesh[x, y, z, :] = self.activation(self.mesh[x, y, z, :]) # Activate after injection


    def get_mesh_state_summary(self) -> np.ndarray:
        """Returns a summary of the mesh state (e.g., mean pooling)."""
        return np.mean(self.mesh, axis=(0, 1, 2)) # Average over all spatial dimensions

    def reset_mesh(self):
        """Resets the mesh to its initial small random values."""
        self.mesh = np.random.rand(self.mesh_size, self.mesh_size, self.mesh_size, self.feature_dim).astype(np.float32) * 0.1

class FractalMeshStack:
    """
    A stack of RippleEcho3DMeshes, potentially with different sizes or properties,
    representing a hierarchical or multi-resolution fractal structure.
    """
    def __init__(self, num_layers: int = 3, base_mesh_size: int = 8, base_feature_dim: int = 32):
        self.layers: List[RippleEcho3DMesh] = []
        current_mesh_size = base_mesh_size
        current_feature_dim = base_feature_dim

        for i in range(num_layers):
            # Example: decrease mesh size and increase feature dim for higher layers (conceptual)
            # Or keep them same, or other scaling logic
            layer_mesh_size = max(2, current_mesh_size // (i + 1)) # Ensure size is at least 2
            layer_feature_dim = current_feature_dim * (i + 1)

            self.layers.append(RippleEcho3DMesh(mesh_size=layer_mesh_size, feature_dim=layer_feature_dim))
            # print(f"Created FractalMeshStack Layer {i}: Size={layer_mesh_size}, Dim={layer_feature_dim}")


    def process_input(self, input_signal: np.ndarray, steps_per_layer: int = 2) -> np.ndarray:
        """
        Processes an input signal through the stack of meshes.
        The input signal is injected into the first layer.
        Output of one layer can be used to influence the next (simplified here).
        """
        if not self.layers:
            return input_signal # No layers to process

        current_signal = input_signal

        for i, layer in enumerate(self.layers):
            # Adapt current_signal to the layer's feature dimension
            if current_signal.shape[0] != layer.feature_dim:
                # Simple adaptation: use UniversalEncoder or pad/truncate
                # For now, let's use a basic padding/truncation for demonstration
                if current_signal.shape[0] > layer.feature_dim:
                    adapted_signal = current_signal[:layer.feature_dim]
                else:
                    padding = np.zeros(layer.feature_dim - current_signal.shape[0], dtype=np.float32)
                    adapted_signal = np.concatenate([current_signal, padding])
            else:
                adapted_signal = current_signal

            # Inject signal at a central position (or more complex mapping)
            center_pos = (layer.mesh_size // 2, layer.mesh_size // 2, layer.mesh_size // 2)
            layer.inject_signal(center_pos, adapted_signal)
            layer.ripple(steps=steps_per_layer)
            current_signal = layer.get_mesh_state_summary() # Output of this layer becomes input for the next

        return current_signal

    def get_total_elements(self) -> int:
        return sum(layer.mesh.size for layer in self.layers)

class EpisodicMemory:
    """
    A simple episodic memory store using vector similarity for retrieval.
    Stores (embedding, data_payload, metadata) tuples.
    """
    def __init__(self, embedding_dim: int, capacity: int = 1000):
        self.embedding_dim = embedding_dim
        self.capacity = capacity
        self.memory_embeddings: Optional[np.ndarray] = None # Initialize when first memory is added
        self.memory_payloads: List[Any] = []
        self.memory_metadata: List[Dict[str, Any]] = []
        self.encoder = UniversalEncoder(output_dim=embedding_dim) # For encoding queries if needed

    def add_episode(self, data_payload: Any, metadata: Optional[Dict[str, Any]] = None, embedding: Optional[np.ndarray] = None):
        """Adds an episode to the memory."""
        if embedding is None:
            # If no explicit embedding provided, try to encode the payload
            # This is conceptual; a real system might require explicit embeddings or more sophisticated encoding.
            embedding = self.encoder.encode(data_payload)

        if embedding.shape[0] != self.embedding_dim:
            raise ValueError(f"Provided embedding dimension {embedding.shape[0]} does not match memory's dimension {self.embedding_dim}.")

        if self.memory_embeddings is None:
            self.memory_embeddings = np.array([embedding], dtype=np.float32)
        else:
            self.memory_embeddings = np.vstack([self.memory_embeddings, embedding.astype(np.float32)])

        self.memory_payloads.append(data_payload)
        self.memory_metadata.append(metadata if metadata is not None else {})

        # Enforce capacity (FIFO eviction)
        if len(self.memory_payloads) > self.capacity:
            self.memory_embeddings = self.memory_embeddings[1:]
            self.memory_payloads.pop(0)
            self.memory_metadata.pop(0)

    def retrieve_similar_episodes(self, query_embedding: np.ndarray, top_k: int = 5) -> List[Tuple[Any, Dict[str, Any], float]]:
        """Retrieves the top_k most similar episodes based on cosine similarity."""
        if self.memory_embeddings is None or len(self.memory_payloads) == 0:
            return []

        if query_embedding.shape[0] != self.embedding_dim:
            # Try to re-encode if query is not an embedding
            # This assumes query_embedding might be raw data for the query
            # print(f"Warning: Query embedding dim mismatch. Attempting to re-encode query.")
            query_embedding = self.encoder.encode(query_embedding)
            if query_embedding.shape[0] != self.embedding_dim: # Check again after re-encoding
                 raise ValueError(f"Query embedding dimension {query_embedding.shape[0]} does not match memory's dimension {self.embedding_dim} even after re-encode.")


        # Cosine similarity calculation
        norm_query = query_embedding / (np.linalg.norm(query_embedding) + 1e-9)
        norm_memory = self.memory_embeddings / (np.linalg.norm(self.memory_embeddings, axis=1, keepdims=True) + 1e-9)

        similarities = np.dot(norm_memory, norm_query)

        # Get top_k indices
        # If top_k is larger than available memories, adjust k
        effective_k = min(top_k, len(similarities))
        if effective_k <= 0: return []

        # Argsort sorts in ascending order, so we take the last k and reverse them for descending similarity
        sorted_indices = np.argsort(similarities)[-effective_k:][::-1]

        results = []
        for idx in sorted_indices:
            results.append((self.memory_payloads[idx], self.memory_metadata[idx], float(similarities[idx])))

        return results

    def get_memory_count(self) -> int:
        return len(self.memory_payloads)

# --- Advanced Mesh & Tokenization Components ---

class FractalMeshTokenizer:
    """
    Conceptual: Tokenizes text into a multi-dimensional fractal embedding.
    This is a placeholder for a very advanced tokenization scheme.
    A simplified version might map characters or subwords to positions/activations
    within a small 3D mesh, then use a RippleEcho3DMesh to process it.
    """
    def __init__(self, mesh_count: int = 4, mesh_size: int = 4, steps: int = 3, vocab: Optional[List[str]] = None):
        self.mesh_count = mesh_count # Number of parallel meshes used for tokenization
        self.mesh_size = mesh_size   # Size of each 3D mesh (e.g., 4x4x4)
        self.steps = steps           # Ripple steps for each mesh processing

        # Each mesh produces mesh_size^3 features. Total features = mesh_count * (mesh_size^3)
        self.output_dim = self.mesh_count * (self.mesh_size ** 3)

        # Create internal meshes. Feature dim for these internal meshes is 1 (activation value).
        self.internal_meshes = [RippleEcho3DMesh(mesh_size=self.mesh_size, feature_dim=1, activation_fn='tanh') for _ in range(self.mesh_count)]

        self.vocab_map: Dict[str, int] = {}
        self.rev_vocab_map: Dict[int, str] = {}
        if vocab:
            self._create_char_vocab(vocab if isinstance(vocab, list) else list(str(vocab)))
        else:
            # Default simple ASCII character vocabulary if none provided
            self._create_char_vocab([chr(i) for i in range(32, 127)]) # Printable ASCII

    def _create_char_vocab(self, chars: List[str]):
        unique_chars = sorted(list(set(chars)))
        self.vocab_map = {char: i for i, char in enumerate(unique_chars)}
        self.rev_vocab_map = {i: char for i, char in enumerate(unique_chars)}
        self.vocab_size = len(unique_chars)

    def encode(self, text: str) -> np.ndarray:
        """Encodes text into a fractal mesh embedding."""
        if not isinstance(text, str): text = str(text) # Ensure string input

        char_embeddings = []
        for char_idx, char in enumerate(text):
            if char not in self.vocab_map:
                # Handle OOV characters (e.g., map to a generic <UNK> token or skip)
                # For simplicity, skip for now, or use a default vector.
                # Or, assign a random-ish position for unknown chars.
                char_code = len(self.vocab_map) # Use a generic OOV code
            else:
                char_code = self.vocab_map[char]

            # Distribute characters across the meshes
            mesh_idx = char_idx % self.mesh_count

            # Map char_code to a 3D position within the mesh_idx-th mesh
            # This mapping needs to be consistent.
            # Example: x = char_code % mesh_size, y = (char_code // mesh_size) % mesh_size, etc.
            # Ensure max char_code fits within mesh_size^3 positions for a dense mapping.
            # If vocab_size > mesh_size^3, multiple chars might map to same initial pos,
            # but their sequence and mesh_idx will differentiate.

            # Simplified position mapping:
            # Max unique positions in one mesh = mesh_size^3
            # Modulo arithmetic to map char_code into this space.
            max_pos_per_mesh = self.mesh_size ** 3
            local_pos_code = char_code % max_pos_per_mesh

            pos_x = local_pos_code % self.mesh_size
            pos_y = (local_pos_code // self.mesh_size) % self.mesh_size
            pos_z = (local_pos_code // (self.mesh_size**2)) % self.mesh_size

            # Signal is just an activation (e.g., 1.0)
            signal = np.array([1.0], dtype=np.float32)

            # Inject this character's signal into the chosen mesh at the calculated position
            self.internal_meshes[mesh_idx].inject_signal((pos_x, pos_y, pos_z), signal)

        # After injecting all characters, ripple all meshes and collect outputs
        final_embedding_parts = []
        for mesh in self.internal_meshes:
            mesh.ripple(steps=self.steps)
            # The state of each mesh node is 1-dim. Flatten to get mesh_size^3 features.
            mesh_output_flat = mesh.mesh.flatten()
            final_embedding_parts.append(mesh_output_flat)
            mesh.reset_mesh() # Reset for next tokenization

        return np.concatenate(final_embedding_parts).astype(np.float32)

    def decode(self, embedding: np.ndarray) -> str:
        """Conceptual: Decodes a fractal mesh embedding back to text."""
        # This is highly complex and would require a trained decoder model.
        # Placeholder: return a representation of the embedding's activation.
        if embedding.shape[0] != self.output_dim:
            return "[Decode Error: Embedding dimension mismatch]"

        # For a conceptual decode, we could try to find the most "active" character
        # by reversing the encoding's mesh processing (very hard).
        # Simplistic: find max activation in each conceptual mesh part and map back.

        # This is a very rough approximation and not a true inverse.
        text_parts = []
        part_len = self.mesh_size ** 3
        num_chars_to_decode = 0 # Estimate based on non-zero parts or fixed length

        # Determine how many "characters" might be in the embedding
        # This is tricky as the embedding is a result of ripples.
        # Let's assume we try to decode a fixed number of chars, or up to where signal is low.

        # For a *very* basic conceptual decode:
        # Treat each mesh's output part as potentially encoding one character.
        # Find the most active cell in each mesh part and try to map its index back to a char_code.

        decoded_text = ""
        for i in range(self.mesh_count):
            mesh_part_embedding = embedding[i * part_len : (i + 1) * part_len]
            # mesh_part_embedding is (mesh_size**3) long. Reshape to 3D.
            # This part was flattened from a (mesh_size, mesh_size, mesh_size, 1) mesh.

            # Find index of max activation in this part
            if np.sum(np.abs(mesh_part_embedding)) < 1e-3 : # If part is mostly zero, skip
                continue

            max_act_idx_flat = np.argmax(mesh_part_embedding) # Index in the flattened part_len vector

            # This max_act_idx_flat was originally a 3D coordinate (x,y,z) in that mesh.
            # And that (x,y,z) was derived from a char_code.
            # We need to reverse: flat_idx -> (x,y,z) -> char_code.
            # flat_idx = z * mesh_size*mesh_size + y * mesh_size + x (if feature_dim was 1)
            # So, x = flat_idx % mesh_size
            #     y = (flat_idx // mesh_size) % mesh_size
            #     z = (flat_idx // (mesh_size**2)) % mesh_size
            # And local_pos_code was (z * mesh_size**2 + y * mesh_size + x) if mapped this way.
            # The original mapping was:
            #   pos_x = local_pos_code % self.mesh_size
            #   pos_y = (local_pos_code // self.mesh_size) % self.mesh_size
            #   pos_z = (local_pos_code // (self.mesh_size**2)) % self.mesh_size
            # This means local_pos_code = pos_x + pos_y * self.mesh_size + pos_z * self.mesh_size**2
            # (assuming standard row-major flattening for pos_x, pos_y, pos_z order)
            # If the flattened index `max_act_idx_flat` corresponds to (pos_x, pos_y, pos_z) directly,
            # then `max_act_idx_flat` IS the `local_pos_code`.

            approx_char_code = max_act_idx_flat % self.vocab_size # Ensure it's within vocab range
                                                                # This is a huge simplification.

            if approx_char_code in self.rev_vocab_map:
                decoded_text += self.rev_vocab_map[approx_char_code]
            else:
                decoded_text += "?" # Unknown char

        return decoded_text if decoded_text else "[Decode: No strong signal]"


class FractalKernel(Module): # Inherits from a base Module class (defined in agi_core_logic.py)
    """
    A processing kernel that operates on fractal mesh data.
    Conceptual: could be a type of convolutional or graph neural network layer
    adapted for these mesh structures.
    """
    def __init__(self, input_feature_dim: int, output_feature_dim: int, kernel_size: int = 3):
        super().__init__() # Call Module's __init__
        self.input_dim = input_feature_dim
        self.output_dim = output_feature_dim
        self.kernel_size = kernel_size # e.g., 3x3x3 kernel

        # Conceptual weights for the kernel.
        # Shape: (kernel_size, kernel_size, kernel_size, input_dim, output_dim)
        self.weights = np.random.randn(kernel_size, kernel_size, kernel_size, input_feature_dim, output_feature_dim).astype(np.float32) * 0.01
        self.bias = np.zeros(output_feature_dim, dtype=np.float32)
        self.activation = np.tanh # Using tanh activation

    def forward(self, input_mesh_data: RippleEcho3DMesh) -> RippleEcho3DMesh:
        """
        Applies the fractal kernel to the input mesh data.
        Input_mesh_data is an instance of RippleEcho3DMesh.
        Output is a new RippleEcho3DMesh with transformed features.
        This is a simplified convolution-like operation.
        """
        if input_mesh_data.feature_dim != self.input_dim:
            raise ValueError(f"Input mesh feature dimension {input_mesh_data.feature_dim} does not match kernel input dimension {self.input_dim}.")

        mesh_s = input_mesh_data.mesh_size
        output_mesh_array = np.zeros((mesh_s, mesh_s, mesh_s, self.output_dim), dtype=np.float32)

        pad_size = self.kernel_size // 2
        padded_input = np.pad(input_mesh_data.mesh,
                              ((pad_size, pad_size), (pad_size, pad_size), (pad_size, pad_size), (0,0)),
                              mode='constant', constant_values=0)

        for x in range(mesh_s):
            for y in range(mesh_s):
                for z in range(mesh_s):
                    # Extract the local region (receptive field)
                    region = padded_input[x : x+self.kernel_size,
                                          y : y+self.kernel_size,
                                          z : z+self.kernel_size, :]

                    # Perform convolution: sum over (kernel * region)
                    # Output for this position (x,y,z) will be a vector of size self.output_dim
                    # region shape: (ks, ks, ks, input_dim)
                    # self.weights shape: (ks, ks, ks, input_dim, output_dim)
                    # Element-wise product and sum:
                    # einsum: 'ijkl,ijklm->m'  (i,j,k=kernel_dims, l=input_feat, m=output_feat)
                    convolved_vector = np.einsum('ijkl,ijklm->m', region, self.weights)
                    output_mesh_array[x, y, z, :] = self.activation(convolved_vector + self.bias)

        output_mesh = RippleEcho3DMesh(mesh_size=mesh_s, feature_dim=self.output_dim)
        output_mesh.mesh = output_mesh_array
        return output_mesh

    def __call__(self, input_mesh_data: RippleEcho3DMesh) -> RippleEcho3DMesh:
        return self.forward(input_mesh_data)

class QuantumContext:
    """
    Conceptual representation of a quantum-inspired contextual space.
    This is highly abstract and does not simulate actual quantum mechanics.
    It might involve superposition-like states (multiple possibilities) and
    entanglement-like correlations between concepts.
    """
    def __init__(self, num_qubits_equivalent: int = 10, embedding_dim: int = 128):
        self.num_qubits = num_qubits_equivalent # Conceptual number of "qubits"
        self.embedding_dim = embedding_dim # Dimension of embeddings stored/processed

        # State vector in a 2^N dimensional Hilbert space (conceptual)
        # For simplicity, we'll represent context as a set of weighted embeddings.
        # Each "basis state" could be an embedding, and its "amplitude" a weight.
        self.context_elements: List[Tuple[np.ndarray, float]] = [] # (embedding, weight/amplitude)
        self.max_elements = 2**num_qubits_equivalent # Max distinct elements we can "superpose"

    def add_concept(self, embedding: np.ndarray, weight: float = 1.0):
        """Adds a concept (embedding) to the quantum context with a given weight."""
        if embedding.shape[0] != self.embedding_dim:
            raise ValueError("Embedding dimension mismatch.")

        # Normalize weight (conceptual, not true quantum amplitude normalization)
        weight = np.clip(weight, 0.0, 1.0)

        # If concept already exists, update its weight (e.g., reinforcement)
        # This requires comparing embeddings, which can be tricky.
        # For simplicity, assume new concepts are distinct or use a threshold for similarity.

        if len(self.context_elements) < self.max_elements:
            self.context_elements.append((embedding, weight))
        else:
            # Eviction strategy if context is full (e.g., remove lowest weight)
            self.context_elements.sort(key=lambda x: x[1]) # Sort by weight
            self.context_elements.pop(0) # Remove lowest weight
            self.context_elements.append((embedding, weight))

        self._normalize_weights()


    def _normalize_weights(self):
        """Normalizes the weights in the context (conceptually, sum of squares = 1)."""
        if not self.context_elements: return

        weights_sq = np.array([w**2 for _, w in self.context_elements])
        sum_weights_sq = np.sum(weights_sq)
        if sum_weights_sq > 1e-9: # Avoid division by zero
            norm_factor = np.sqrt(sum_weights_sq)
            self.context_elements = [(emb, w / norm_factor) for emb, w in self.context_elements]


    def measure_context(self, focus_embedding: Optional[np.ndarray] = None) -> Optional[np.ndarray]:
        """
        "Measures" the context, collapsing it to a single dominant concept/embedding.
        If focus_embedding is provided, measurement is biased towards concepts similar to focus.
        """
        if not self.context_elements:
            return None

        probabilities = np.array([w**2 for _, w in self.context_elements]) # Probabilities are amplitudes squared

        if focus_embedding is not None:
            if focus_embedding.shape[0] != self.embedding_dim:
                raise ValueError("Focus embedding dimension mismatch.")
            # Modulate probabilities by similarity to focus_embedding
            similarities = np.array([self._cosine_similarity(emb, focus_embedding) for emb, _ in self.context_elements])
            # Ensure similarities are non-negative for probability modulation
            similarities = (similarities + 1) / 2 # Map from [-1, 1] to [0, 1]
            probabilities = probabilities * similarities

        # Normalize probabilities so they sum to 1
        prob_sum = np.sum(probabilities)
        if prob_sum < 1e-9: # If all probabilities are near zero (e.g., no similarity to focus)
            # Fallback: choose based on original weights or randomly
            if not any(w > 1e-6 for _,w in self.context_elements): return None # No significant elements
            probabilities = np.array([w**2 for _, w in self.context_elements])
            prob_sum = np.sum(probabilities)
            if prob_sum < 1e-9: return None


        probabilities /= prob_sum

        # Choose an element based on these probabilities
        chosen_idx = np.random.choice(len(self.context_elements), p=probabilities)

        # "Collapse": For simplicity, return the chosen embedding.
        # A more complex model might update the context after measurement.
        return self.context_elements[chosen_idx][0]

    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        norm_vec1 = vec1 / (np.linalg.norm(vec1) + 1e-9)
        norm_vec2 = vec2 / (np.linalg.norm(vec2) + 1e-9)
        return np.dot(norm_vec1, norm_vec2)

    def get_context_summary_vector(self) -> np.ndarray:
        """Returns a weighted average of all embeddings in the context."""
        if not self.context_elements:
            return np.zeros(self.embedding_dim, dtype=np.float32)

        summary_vec = np.zeros(self.embedding_dim, dtype=np.float32)
        total_weight = 0.0
        for emb, weight in self.context_elements:
            summary_vec += emb * weight # Use original weights for weighted average
            total_weight += weight

        return summary_vec / total_weight if total_weight > 1e-9 else summary_vec


# --- Memory Compression (Placeholder based on OFRC code) ---
class MemoryCompressor:
    """
    Conceptual class for compressing and decompressing memory traces.
    This would involve techniques like autoencoders, PCA, or learned summarization.
    This is a very simplified version based on OFRC's OFRCMemoryPalace structure.
    """
    def __init__(self, phase_dim: int, hot_cache_size: int = 1024): # phase_dim is like embedding_dim
        self.phase_dim = phase_dim
        self.hot_cache_size = hot_cache_size # Number of recent/hot items to keep readily accessible

        # Conceptual storage (replace with actual FAISS or vector DB in full implementation)
        self.compressed_storage = [] # List of (compressed_representation, original_hash, metadata)
        self.hot_cache = collections.OrderedDict() # For quick access to recent items

        # For search, we'd ideally have a vector index (like FAISS)
        # This is a placeholder for that index.
        self.faiss_index = None # Would be a faiss.IndexFlatL2 or similar
        self.indexed_vectors = [] # Store the vectors that are in faiss_index
        self.index_to_payload_map = {} # Maps faiss index ID to actual payload or storage ID

        self.encoder = UniversalEncoder(output_dim=phase_dim) # For creating embeddings

    def _compress(self, data_vector: np.ndarray) -> Any:
        """Conceptual compression. Returns a 'compressed' representation."""
        # Simple "compression": could be PCA, quantization, or just storing the vector itself if no lossy compression.
        # For this placeholder, let's assume it just returns the vector, or a part of it.
        # Or, if data_vector is high-dim, a real autoencoder would reduce it.
        if data_vector.shape[0] > self.phase_dim: # If input vector is larger than phase_dim
            # Simple truncation as "compression"
            return data_vector[:self.phase_dim]
        elif data_vector.shape[0] < self.phase_dim:
            # Pad if smaller
            padding = np.zeros(self.phase_dim - data_vector.shape[0], dtype=data_vector.dtype)
            return np.concatenate([data_vector, padding])
        return data_vector # Assume it's already at target phase_dim


    def _decompress(self, compressed_data: Any) -> np.ndarray:
        """Conceptual decompression. Returns the reconstructed data vector."""
        # If _compress was just truncation/padding or identity, _decompress is similar.
        # If a real autoencoder was used, this would be its decoder part.
        if isinstance(compressed_data, np.ndarray) and compressed_data.shape[0] == self.phase_dim:
            return compressed_data
        # Fallback if format is unexpected
        # print(f"Warning: Cannot decompress data of type {type(compressed_data)}. Returning zero vector.")
        return np.zeros(self.phase_dim, dtype=np.float32)

    def store_memory_entry(self, content_data: Any, text_summary: str,
                           vector_embedding: Optional[np.ndarray] = None,
                           keyword_hashes: Optional[List[str]] = None,
                           emotional_tags: Optional[Dict[str, float]] = None,
                           related_memory_hashes: Optional[List[str]] = None) -> str:
        """
        Stores a memory entry, including its content, summary, and various metadata.
        Returns a unique hash ID for the stored memory.
        """
        if vector_embedding is None:
            vector_embedding = self.encoder.encode(text_summary if text_summary else str(content_data))

        if vector_embedding.shape[0] != self.phase_dim:
            # Adapt embedding to phase_dim if necessary
            vector_embedding = self.encoder.encode(vector_embedding) # Re-encode to target dim

        compressed_vec = self._compress(vector_embedding)

        # Create a unique ID for this memory entry (e.g., hash of content or summary)
        entry_id_material = json.dumps({"summary": text_summary, "ts": time.time()}, sort_keys=True)
        entry_id = hashlib.sha256(entry_id_material.encode()).hexdigest()

        metadata_to_store = {
            "id": entry_id,
            "timestamp": time.time(),
            "text_summary": text_summary,
            "original_content_preview": str(content_data)[:200], # Store a preview
            "keyword_hashes": keyword_hashes or [],
            "emotional_tags": emotional_tags or {},
            "related_memory_hashes": related_memory_hashes or [],
            # Store the actual content separately or a reference to it
            # For this placeholder, we'll assume content_data is small enough to be part of metadata
            "full_content": content_data
        }

        # Add to conceptual FAISS index
        if self.faiss_index is None:
            try:
                import faiss
                self.faiss_index = faiss.IndexFlatL2(self.phase_dim)
                # print("FAISS IndexFlatL2 initialized.")
            except ImportError:
                # print("FAISS not available. Search will be linear scan.")
                self.faiss_index = None # Ensure it's None if import fails

        current_index_id = -1
        if self.faiss_index is not None:
            self.faiss_index.add(np.array([vector_embedding], dtype=np.float32))
            current_index_id = self.faiss_index.ntotal - 1
            self.index_to_payload_map[current_index_id] = metadata_to_store # Map FAISS ID to metadata
            self.indexed_vectors.append(vector_embedding) # Keep a copy for potential rebuilds
        else:
            # Fallback: store in simple list for linear scan if FAISS fails
            self.compressed_storage.append((vector_embedding, entry_id, metadata_to_store))


        # Add to hot cache
        if len(self.hot_cache) >= self.hot_cache_size:
            self.hot_cache.popitem(last=False) # Evict oldest
        self.hot_cache[entry_id] = metadata_to_store

        return entry_id

    def search_memories(self, query_vector: np.ndarray, top_n: int = 5) -> List[Dict[str, Any]]:
        """Searches memories based on vector similarity to the query_vector."""
        if query_vector.shape[0] != self.phase_dim:
            # print(f"Warning: Query vector dim {query_vector.shape[0]} mismatch with phase_dim {self.phase_dim}. Re-encoding query.")
            query_vector = self.encoder.encode(query_vector) # Attempt to fix dimension

        results = []
        if self.faiss_index is not None and self.faiss_index.ntotal > 0:
            distances, indices = self.faiss_index.search(np.array([query_vector], dtype=np.float32), k=min(top_n, self.faiss_index.ntotal))
            for i, faiss_idx in enumerate(indices[0]):
                if faiss_idx != -1: # FAISS returns -1 for invalid indices
                    payload = self.index_to_payload_map.get(faiss_idx)
                    if payload:
                        # Augment payload with distance (or similarity)
                        payload_copy = payload.copy()
                        payload_copy["search_distance"] = float(distances[0][i])
                        results.append(payload_copy)
        else:
            # Fallback to linear scan if FAISS not available or empty
            if not self.compressed_storage: return []

            similarities = []
            for stored_vec, entry_id, metadata in self.compressed_storage:
                # Cosine similarity
                sim = np.dot(query_vector, stored_vec) / (np.linalg.norm(query_vector) * np.linalg.norm(stored_vec) + 1e-9)
                similarities.append({'similarity': sim, 'metadata': metadata})

            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            for item in similarities[:top_n]:
                payload_copy = item['metadata'].copy()
                payload_copy["search_similarity"] = float(item['similarity'])
                results.append(payload_copy)

        return results

    def retrieve_from_cache(self, entry_id: str) -> Optional[Dict[str, Any]]:
        return self.hot_cache.get(entry_id)

    def _load_memory(self, filepath: Optional[str] = None): # Added filepath for OFRC compatibility
        # Placeholder for loading memory state from persistence
        # print("Conceptual: MemoryCompressor._load_memory() called.")
        if filepath and os.path.exists(filepath):
            try:
                # This would load FAISS index, metadata, etc.
                # For now, it's a stub.
                # with open(filepath, 'rb') as f:
                #     data = pickle.load(f)
                #     self.faiss_index = data['faiss_index']
                #     self.index_to_payload_map = data['map']
                #     self.hot_cache = data['cache']
                # print(f"Conceptual: Loaded memory from {filepath}")
                pass
            except Exception as e:
                # print(f"Error loading memory from {filepath}: {e}")
                pass


# Example Usage (for testing individual components)
if __name__ == "__main__":
    print("--- Testing UniversalEncoder ---")
    encoder = UniversalEncoder(output_dim=64)
    vec_str = encoder.encode("hello world")
    print(f"Encoded string (shape {vec_str.shape}): {vec_str[:5]}...")
    vec_num_list = encoder.encode([1,2,3,4,5])
    print(f"Encoded num list (shape {vec_num_list.shape}): {vec_num_list[:5]}...")
    vec_np = encoder.encode(np.random.rand(100))
    print(f"Encoded numpy array (shape {vec_np.shape}): {vec_np[:5]}...")

    print("\n--- Testing RippleEcho3DMesh ---")
    mesh3d = RippleEcho3DMesh(mesh_size=3, feature_dim=8)
    mesh3d.inject_signal((1,1,1), np.random.rand(8).astype(np.float32))
    mesh3d.ripple(steps=2)
    summary = mesh3d.get_mesh_state_summary()
    print(f"Mesh state summary (shape {summary.shape}): {summary[:5]}...")

    print("\n--- Testing FractalMeshStack ---")
    stack = FractalMeshStack(num_layers=2, base_mesh_size=4, base_feature_dim=16)
    input_sig = np.random.rand(16).astype(np.float32) # Matches base_feature_dim of first layer if scaling is identity
    output_sig = stack.process_input(input_sig, steps_per_layer=1)
    print(f"FractalMeshStack output signal (shape {output_sig.shape}): {output_sig[:5]}...")

    print("\n--- Testing EpisodicMemory ---")
    memory = EpisodicMemory(embedding_dim=64, capacity=10)
    for i in range(5):
        payload = f"Episode data {i}"
        meta = {"timestamp": time.time(), "source": "test_run"}
        # Use the encoder from this file for embeddings
        emb = encoder.encode(payload) # encoder has output_dim=64
        memory.add_episode(payload, meta, emb)
    print(f"Memory count: {memory.get_memory_count()}")

    query_payload = "Episode data 3" # Should be similar to one stored
    query_emb = encoder.encode(query_payload)
    similar_episodes = memory.retrieve_similar_episodes(query_emb, top_k=2)
    print("Similar episodes to 'Episode data 3':")
    for p, m, sim_score in similar_episodes:
        print(f"  - Payload: '{p}', Similarity: {sim_score:.4f}, Meta: {m}")

    print("\n--- Testing FractalMeshTokenizer ---")
    # Vocab for tokenizer from a list of strings
    sample_texts = ["hello world", "fractal mesh", "tokenizer test"]
    chars_in_texts = []
    for t in sample_texts: chars_in_texts.extend(list(t))

    tokenizer = FractalMeshTokenizer(mesh_count=2, mesh_size=3, steps=1, vocab=chars_in_texts) # 2 meshes, 3x3x3 each
    # Output dim will be 2 * (3^3) = 54
    print(f"Tokenizer output dim: {tokenizer.output_dim}, Vocab size: {tokenizer.vocab_size}")
    token_embedding = tokenizer.encode("fractal")
    print(f"Encoded 'fractal' (shape {token_embedding.shape}): {token_embedding[:10]}...")
    decoded_text = tokenizer.decode(token_embedding)
    print(f"Decoded (conceptual): '{decoded_text}'")

    # Define Module base class for FractalKernel if not already defined (e.g. in agi_core_logic)
    class Module:
        def __init__(self): self.id = uuid.uuid4()
        def forward(self, *args, **kwargs): raise NotImplementedError
        def __call__(self, *args, **kwargs): return self.forward(*args, **kwargs)

    print("\n--- Testing FractalKernel ---")
    kernel = FractalKernel(input_feature_dim=8, output_feature_dim=16, kernel_size=3)
    input_mesh_for_kernel = RippleEcho3DMesh(mesh_size=5, feature_dim=8) # Matches kernel input_dim
    input_mesh_for_kernel.inject_signal((2,2,2), np.random.rand(8).astype(np.float32))
    input_mesh_for_kernel.ripple(1)

    output_mesh_from_kernel = kernel.forward(input_mesh_for_kernel)
    print(f"Output mesh from kernel: size={output_mesh_from_kernel.mesh_size}, features={output_mesh_from_kernel.feature_dim}")
    print(f"Output mesh summary: {output_mesh_from_kernel.get_mesh_state_summary()[:5]}...")

    print("\n--- Testing QuantumContext ---")
    qc = QuantumContext(num_qubits_equivalent=3, embedding_dim=64) # Max 2^3=8 elements
    qc.add_concept(encoder.encode("quantum idea 1"), weight=0.7)
    qc.add_concept(encoder.encode("classical idea 2"), weight=0.3)
    qc.add_concept(encoder.encode("entangled thought 3"), weight=0.5)

    summary_vec = qc.get_context_summary_vector()
    print(f"QuantumContext summary vector (shape {summary_vec.shape}): {summary_vec[:5]}...")

    focus = encoder.encode("idea related to quantum")
    measured_concept = qc.measure_context(focus_embedding=focus)
    if measured_concept is not None:
        print(f"Measured concept (biased by focus, shape {measured_concept.shape}): {measured_concept[:5]}...")
    else:
        print("Measured context resulted in None (no significant elements or match).")

    print("\n--- Testing MemoryCompressor ---")
    mem_compressor = MemoryCompressor(phase_dim=64, hot_cache_size=5)
    test_payloads = {}
    for i in range(7):
        payload_content = {"data": f"memory content {i}", "value": i*10.5}
        summary = f"This is memory number {i}"
        emb = encoder.encode(summary) # Encoder output_dim=64, matches phase_dim

        entry_hash = mem_compressor.store_memory_entry(
            content_data=payload_content,
            text_summary=summary,
            vector_embedding=emb,
            keyword_hashes=[hashlib.sha256(k.encode()).hexdigest() for k in summary.split()],
            emotional_tags={"joy": i/10}
        )
        test_payloads[entry_hash] = payload_content
        print(f"Stored memory {i}, ID: {entry_hash[:8]}...")

    print(f"Hot cache size: {len(mem_compressor.hot_cache)}")

    query_summary = "memory number 3"
    query_emb_comp = encoder.encode(query_summary)
    search_results = mem_compressor.search_memories(query_emb_comp, top_n=2)
    print(f"Search results for '{query_summary}':")
    for res in search_results:
        dist_or_sim = res.get('search_distance', res.get('search_similarity', 'N/A'))
        metric_name = 'distance' if 'search_distance' in res else 'similarity'
        print(f"  - ID: {res['id'][:8]}, Summary: '{res['text_summary']}', {metric_name}: {dist_or_sim:.4f}")
        # Verify we can get original content (if stored directly or via reference)
        # print(f"    Original content preview: {res.get('original_content_preview')}")
        # Full content (if stored): print(f" Full content: {res.get('full_content')}")

    # Test cache retrieval
    if test_payloads:
        first_entry_id = list(test_payloads.keys())[0] # This might have been evicted from cache
        last_entry_id = list(test_payloads.keys())[-1] # This should be in cache

        cached_item = mem_compressor.retrieve_from_cache(last_entry_id)
        if cached_item:
            print(f"Retrieved '{cached_item['text_summary']}' from hot cache.")
        else:
            print(f"Item {last_entry_id[:8]} not found in hot cache (unexpected).")

        old_item_from_cache = mem_compressor.retrieve_from_cache(first_entry_id)
        if old_item_from_cache:
             print(f"Retrieved old item '{old_item_from_cache['text_summary']}' from hot cache (might be due to small test size).")
        else:
            print(f"Old item {first_entry_id[:8]} correctly not in hot cache (evicted).")

```
