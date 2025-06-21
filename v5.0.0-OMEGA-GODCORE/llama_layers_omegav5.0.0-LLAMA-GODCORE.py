# v5.0.0-OMEGA-GODCORE/llama_layers_omegav5.0.0-LLAMA-GODCORE.py
import numpy as np
import math
from typing import List, Optional, Tuple, Dict, Any

# Assuming OmegaTensor is the custom tensor class from OmegaTensor-v5.0.0-OMEGA-GODCORE.py
# For this file, we'll use a placeholder if the full one isn't directly importable,
# or assume it's made available in the environment.
try:
    from .OmegaTensor-v5.0.0-OMEGA-GODCORE import OmegaTensor
except ImportError:
    # Fallback to a simpler OmegaTensor if the detailed one is not found or relative import fails
    print("Warning: FullOmegaTensor not found for llama_layers. Using basic OmegaTensor placeholder.")
    class OmegaTensor: # Basic placeholder matching core.agi_core_logic.OmegaTensor
        def __init__(self, data: Any, requires_grad: bool = False, dtype=np.float32):
            if isinstance(data, (list, tuple)): self.data = np.array(data, dtype=dtype)
            elif isinstance(data, np.ndarray): self.data = data.astype(dtype)
            elif isinstance(data, (int, float)): self.data = np.array([data], dtype=dtype)
            else: raise TypeError(f"Data must be list, tuple, ndarray, int, or float, not {type(data)}")
            self.requires_grad = requires_grad; self.grad = None; self.shape = self.data.shape; self.dtype = self.data.dtype
            self._children = (); self._op = ''; self._backward_fn = lambda: None
        def numpy(self): return self.data
        def __add__(self, other): return OmegaTensor(self.data + (other.data if isinstance(other, OmegaTensor) else other))
        def __mul__(self, other): return OmegaTensor(self.data * (other.data if isinstance(other, OmegaTensor) else other))
        def sum(self, axis=None, keepdims=False): return OmegaTensor(self.data.sum(axis=axis, keepdims=keepdims))
        def reshape(self, *shape): return OmegaTensor(self.data.reshape(*shape))
        def transpose(self, axes=None): return OmegaTensor(self.data.transpose(axes))
        def __matmul__(self, other): return OmegaTensor(np.matmul(self.data, other.data if isinstance(other, OmegaTensor) else other))
        def backward(self, gradient=None): pass # Placeholder
        @staticmethod
        def stack(tensors: List['OmegaTensor'], axis: int = 0) -> 'OmegaTensor':
            return OmegaTensor(np.stack([t.data for t in tensors], axis=axis))
        # Add other methods as needed by the LLaMA layers, e.g. exp, log, sqrt, slicing, etc.
        def __getitem__(self, key): return OmegaTensor(self.data[key]) # Basic slicing
        def exp(self): return OmegaTensor(np.exp(self.data))
        def log(self): return OmegaTensor(np.log(self.data))
        def sqrt(self): return OmegaTensor(np.sqrt(self.data))
        def to(self, device: Optional[str]=None, dtype: Optional[Any]=None) -> 'OmegaTensor': # Compatibility with PyTorch-like code
            if dtype: self.data = self.data.astype(dtype); self.dtype = dtype
            return self


# --- Model Arguments and Base Layer ---
class SimpleModelArgs:
    def __init__(self, dim: int = 256, n_layers: int = 4, n_heads: int = 4, n_kv_heads: Optional[int] = None,
                 vocab_size: int = 5000, ffn_hidden_dim: Optional[int] = None,
                 norm_eps: float = 1e-5, rope_theta: float = 10000.0,
                 max_seq_len: int = 512):
        self.dim = dim
        self.n_layers = n_layers
        self.n_heads = n_heads
        self.n_kv_heads = n_kv_heads if n_kv_heads is not None else n_heads # For Grouped Query Attention
        self.vocab_size = vocab_size
        self.ffn_hidden_dim = ffn_hidden_dim if ffn_hidden_dim is not None else 4 * dim // 3 # Approximation
        self.norm_eps = norm_eps
        self.rope_theta = rope_theta
        self.max_seq_len = max_seq_len
        self.head_dim = dim // n_heads
        if self.head_dim * n_heads != dim:
            raise ValueError("Dimension 'dim' must be divisible by 'n_heads'.")


class OmegaLayer(object): # Base class for layers, for parameter tracking (conceptual)
    def __init__(self):
        self._parameters: Dict[str, OmegaTensor] = {}
        self._sub_layers: Dict[str, 'OmegaLayer'] = {}

    def parameters(self) -> List[OmegaTensor]:
        params = list(self._parameters.values())
        for sub_layer_dict in self._sub_layers.values():
            if isinstance(sub_layer_dict, OmegaLayer): # If it's a single sub-layer
                 params.extend(sub_layer_dict.parameters())
            elif isinstance(sub_layer_dict, list): # If it's a list of sub-layers (like TransformerBlocks)
                for sub_layer in sub_layer_dict:
                    if isinstance(sub_layer, OmegaLayer):
                        params.extend(sub_layer.parameters())
        return params

    def _register_parameter(self, name: str, tensor: OmegaTensor):
        if not isinstance(tensor, OmegaTensor):
            raise TypeError(f"Cannot register '{name}' - not an OmegaTensor.")
        self._parameters[name] = tensor

    def _register_layer(self, name: str, layer: Union['OmegaLayer', List['OmegaLayer']]):
        # Check if layer or elements in list are OmegaLayer instances
        is_valid = False
        if isinstance(layer, OmegaLayer):
            is_valid = True
        elif isinstance(layer, list) and all(isinstance(l, OmegaLayer) for l in layer):
            is_valid = True

        if not is_valid:
            raise TypeError(f"Cannot register '{name}' - not an OmegaLayer or list of OmegaLayers.")
        self._sub_layers[name] = layer

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.forward(*args, **kwargs)

    def forward(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError("Subclasses of OmegaLayer must implement forward().")


# --- Core LLaMA Components using OmegaTensor ---

class Linear(OmegaLayer):
    def __init__(self, in_features: int, out_features: int, bias: bool = True, dtype=np.float32):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features

        # Xavier initialization (conceptual, using numpy for placeholder)
        limit = np.sqrt(6 / (in_features + out_features))
        weight_data = np.random.uniform(-limit, limit, (out_features, in_features)).astype(dtype)
        self.weight = OmegaTensor(weight_data, requires_grad=True)
        self._register_parameter("weight", self.weight)

        if bias:
            bias_data = np.zeros(out_features, dtype=dtype) # Initialize bias to zeros
            self.bias = OmegaTensor(bias_data, requires_grad=True)
            self._register_parameter("bias", self.bias)
        else:
            self.bias = None

    def forward(self, x: OmegaTensor) -> OmegaTensor:
        # x shape: (..., in_features)
        # weight shape: (out_features, in_features)
        # Output shape: (..., out_features)

        # Reshape x if it's more than 2D for matmul, then reshape back
        original_shape = x.shape
        if x.ndim > 2:
            x_reshaped = x.reshape(-1, original_shape[-1]) # (batch_size * seq_len, in_features)
        else:
            x_reshaped = x

        # (out_features, in_features) @ (in_features, batch_size * seq_len) -> (out_features, batch_size*seq_len)
        # Then transpose to (batch_size*seq_len, out_features)
        # Or, x @ W.T : (batch*seq, in) @ (in, out) -> (batch*seq, out)
        output = x_reshaped @ self.weight.transpose() # OmegaTensor matmul and transpose

        if self.bias is not None:
            output = output + self.bias # Broadcasting bias

        if x.ndim > 2:
            final_shape = original_shape[:-1] + (self.out_features,)
            output = output.reshape(*final_shape)

        return output

class RMSNorm(OmegaLayer):
    def __init__(self, dim: int, eps: float = 1e-5, dtype=np.float32):
        super().__init__()
        self.eps = eps
        # Gain parameter (learnable)
        self.weight = OmegaTensor(np.ones(dim, dtype=dtype), requires_grad=True)
        self._register_parameter("weight", self.weight)

    def _norm(self, x: OmegaTensor) -> OmegaTensor:
        # x shape: (..., dim)
        # rrms = 1 / sqrt(mean(x^2) + eps)
        # output = x * rrms
        variance = (x * x).mean(axis=-1, keepdims=True) # Mean along the last dimension (dim)
        rrms = (variance + self.eps).sqrt() # Element-wise sqrt
        rrms = OmegaTensor(1.0, dtype=x.dtype) / rrms # Element-wise division
        return x * rrms

    def forward(self, x: OmegaTensor) -> OmegaTensor:
        # x shape: (..., dim)
        # Output = _norm(x) * weight
        # The weight is applied element-wise along the 'dim' dimension.
        normalized_x = self._norm(x)
        return normalized_x * self.weight # Broadcasting weight


def apply_rotary_embeddings(x: OmegaTensor, freqs_cis: OmegaTensor) -> OmegaTensor:
    """
    Applies rotary positional embeddings (RoPE) to input tensor x.
    x: Input tensor of shape (batch_size, seq_len, n_heads, head_dim)
    freqs_cis: Precomputed sin/cos frequencies of shape (seq_len, head_dim / 2, 2) or (seq_len, head_dim)
               If (..., head_dim), it's already complex numbers: cos(theta) + i*sin(theta)
               Here, we'll assume it's (seq_len, head_dim) where freqs_cis[t, d] = m*theta_d
               and we need to compute cos and sin.

               A common way: freqs_cis is (max_seq_len, head_dim // 2) containing 'm*theta_d' values.
               We then compute cos and sin.
               Or, freqs_cis is (max_seq_len, head_dim) with interleaved cos/sin or complex.

    Let's assume freqs_cis is precomputed complex numbers (cos + i sin) of shape (seq_len, head_dim).
    This means freqs_cis[t, d] = cos(m_t * theta_d) + i * sin(m_t * theta_d)
    And x is (batch, seq_len, n_heads, head_dim)
    We need to reshape x to view pairs of features for rotation.
    x_ = x.reshape(*x.shape[:-1], -1, 2) -> (batch, seq_len, n_heads, head_dim/2, 2)
    x_complex = x_[..., 0] + 1j * x_[..., 1]

    freqs_complex = freqs_cis (if already complex)

    x_rotated_complex = x_complex * freqs_complex (element-wise complex multiplication)

    x_out_real = x_rotated_complex.real
    x_out_imag = x_rotated_complex.imag
    x_out = stack([x_out_real, x_out_imag], axis=-1).reshape(*x.shape)
    """
    # Simplified RoPE application based on common PyTorch implementations.
    # x: (bs, sl, nh, hd)
    # freqs_cis: (sl, hd) - complex numbers (cos + j*sin)

    x_shape = x.shape
    x_float = x.data # Get numpy array for complex ops, then wrap back

    # Reshape x to (bs, sl, nh, hd/2, 2) to separate real/imaginary parts for rotation
    x_reshaped = x_float.reshape(*x_shape[:-1], -1, 2)

    # Convert to complex numbers: x_complex = x0 + j*x1
    # x_complex shape: (bs, sl, nh, hd/2)
    x_complex = x_reshaped[..., 0] + 1j * x_reshaped[..., 1]

    # freqs_cis is (sl, hd). We need it as (sl, 1, hd/2) complex for broadcasting with x_complex.
    # Assuming freqs_cis is already cos(m*theta) + j*sin(m*theta) and needs reshaping/broadcasting.
    # If freqs_cis is (sl, hd), it means it has cos,sin,cos,sin...
    # Or, if it's (sl, hd/2) complex, then it's already good.
    # Let's assume freqs_cis is (seq_len, head_dim) where head_dim is even,
    # and stores cos_0, sin_0, cos_1, sin_1, ...

    freqs_cis_data = freqs_cis.data # (sl, hd)
    # Reshape freqs_cis to (sl, 1, hd/2, 2) then convert to complex (sl, 1, hd/2)
    freqs_reshaped = freqs_cis_data.reshape(freqs_cis_data.shape[0], 1, -1, 2) # (sl, 1, hd/2, 2)
    freqs_complex = freqs_reshaped[..., 0] + 1j * freqs_reshaped[..., 1] # (sl, 1, hd/2)

    # Element-wise multiplication: x_complex * freqs_complex (broadcasting freqs)
    # x_complex: (bs, sl, nh, hd/2)
    # freqs_complex: (sl, 1, hd/2) -> broadcasts to (1, sl, 1, hd/2) or (bs, sl, nh, hd/2)
    # For broadcasting, ensure seq_len matches. freqs_complex may need slicing if x.seq_len < max_seq_len
    # Let's assume freqs_complex is already sliced to current seq_len of x.
    # So, freqs_complex is (x.seq_len, 1, head_dim/2)

    # x_rotated_complex = x_complex * freqs_complex[:, np.newaxis, :] # Broadcasting (sl,nh,hd/2)
    # Correct broadcasting: freqs_complex should be (1, sl, 1, hd/2) to multiply with (bs, sl, nh, hd/2)
    # Or (sl, 1, hd/2) and rely on numpy's broadcasting rules if x_complex is (bs,sl,nh,hd/2)
    # x_complex shape: (bs, sl, n_heads, head_dim/2)
    # freqs_complex shape: (sl, 1, head_dim/2)
    # After broadcasting freqs_complex to (1, sl, 1, head_dim/2) or similar:
    x_rotated_complex = x_complex * freqs_complex # NumPy handles broadcasting

    # Convert back to real and imaginary parts
    x_out_real = x_rotated_complex.real
    x_out_imag = x_rotated_complex.imag

    # Stack them back and reshape to original x shape
    # x_out_stacked shape: (bs, sl, nh, hd/2, 2)
    x_out_stacked = np.stack((x_out_real, x_out_imag), axis=-1)
    # x_out reshaped: (bs, sl, nh, hd)
    x_out_data = x_out_stacked.reshape(*x_shape)

    # Wrap in OmegaTensor. This operation's backward pass is complex.
    # For now, we'll assume it's part of a larger differentiable block or handled by framework.
    # If RoPE is non-learnable, it doesn't need grad itself.
    return OmegaTensor(x_out_data, requires_grad=x.requires_grad) # Pass requires_grad


class Attention(OmegaLayer):
    def __init__(self, args: SimpleModelArgs, dtype=np.float32):
        super().__init__()
        self.args = args
        self.n_heads = args.n_heads
        self.n_kv_heads = args.n_kv_heads # For Grouped Query Attention (GQA)
        self.head_dim = args.dim // args.n_heads

        self.repeats = self.n_heads // self.n_kv_heads # How many times KV heads are repeated for Q heads in GQA

        self.wq = Linear(args.dim, args.n_heads * self.head_dim, bias=False, dtype=dtype)
        self.wk = Linear(args.dim, args.n_kv_heads * self.head_dim, bias=False, dtype=dtype)
        self.wv = Linear(args.dim, args.n_kv_heads * self.head_dim, bias=False, dtype=dtype)
        self.wo = Linear(args.n_heads * self.head_dim, args.dim, bias=False, dtype=dtype)
        self._register_layer("wq", self.wq)
        self._register_layer("wk", self.wk)
        self._register_layer("wv", self.wv)
        self._register_layer("wo", self.wo)

        # KV cache (conceptual, simple dict for placeholders)
        self.cache_k: Optional[OmegaTensor] = None
        self.cache_v: Optional[OmegaTensor] = None


    def forward(self, x: OmegaTensor, start_pos: int, freqs_cis: OmegaTensor, mask: Optional[OmegaTensor]) -> OmegaTensor:
        # x: (bs, seq_len, dim)
        # freqs_cis: (max_seq_len, head_dim) - complex sin/cos for RoPE
        # mask: (seq_len, seq_len) or similar for causal attention

        bsz, seqlen, _ = x.shape

        xq, xk, xv = self.wq(x), self.wk(x), self.wv(x)
        # xq: (bs, seq_len, n_heads * head_dim)
        # xk: (bs, seq_len, n_kv_heads * head_dim)
        # xv: (bs, seq_len, n_kv_heads * head_dim)

        xq = xq.reshape(bsz, seqlen, self.n_heads, self.head_dim)
        xk = xk.reshape(bsz, seqlen, self.n_kv_heads, self.head_dim)
        xv = xv.reshape(bsz, seqlen, self.n_kv_heads, self.head_dim)

        # Apply RoPE if freqs_cis is provided
        # Slice freqs_cis for the current processing window [start_pos : start_pos + seqlen]
        current_freqs_cis = freqs_cis[start_pos : start_pos + seqlen]
        xq = apply_rotary_embeddings(xq, current_freqs_cis)
        xk = apply_rotary_embeddings(xk, current_freqs_cis)

        # KV Caching (conceptual)
        if start_pos == 0: # First token, initialize cache
            self.cache_k = xk
            self.cache_v = xv
        else: # Append to cache
            if self.cache_k is not None and self.cache_v is not None:
                # Assuming xk, xv are for the *new* tokens (seqlen=1 usually for generation)
                self.cache_k = OmegaTensor.cat([self.cache_k, xk], axis=1) # Concat along seq_len dim
                self.cache_v = OmegaTensor.cat([self.cache_v, xv], axis=1)
            else: # Should not happen if start_pos > 0
                self.cache_k = xk; self.cache_v = xv

        # Use cached keys and values for attention calculation
        keys = self.cache_k
        values = self.cache_v

        # Repeat K, V heads for Grouped Query Attention (GQA) if n_kv_heads < n_heads
        if self.repeats > 1:
            # keys: (bs, cache_seq_len, n_kv_heads, head_dim) -> (bs, cache_seq_len, n_heads, head_dim)
            # values: (bs, cache_seq_len, n_kv_heads, head_dim) -> (bs, cache_seq_len, n_heads, head_dim)

            # Simplistic repeat: stack and reshape, or use np.repeat then wrap.
            # This needs careful handling with OmegaTensor's backward pass.
            # For placeholder, assume a function that does this correctly.
            keys_data = keys.data.repeat(self.repeats, axis=2) # Repeat along n_kv_heads dimension
            values_data = values.data.repeat(self.repeats, axis=2)
            keys = OmegaTensor(keys_data, requires_grad=keys.requires_grad) # Simplistic re-wrap
            values = OmegaTensor(values_data, requires_grad=values.requires_grad)


        # Transpose for attention calculation: (bs, n_heads, seq_len, head_dim)
        xq = xq.transpose((0, 2, 1, 3)) # Query for current tokens
        keys = keys.transpose((0, 2, 1, 3)) # Keys from cache (full sequence so far)
        values = values.transpose((0, 2, 1, 3)) # Values from cache

        # Scaled Dot-Product Attention
        # scores = (xq @ keys.transpose((0, 1, 3, 2))) / math.sqrt(self.head_dim)
        # xq: (bs, n_heads, q_seq_len, head_dim)
        # keys.T: (bs, n_heads, head_dim, kv_cache_seq_len)
        # scores: (bs, n_heads, q_seq_len, kv_cache_seq_len)
        scores = (xq @ keys.transpose((0,1,3,2))) * (1.0 / math.sqrt(self.head_dim))

        if mask is not None:
            # Apply mask (e.g., for causal attention)
            # Mask shape should be broadcastable to scores.
            # Example mask: (q_seq_len, kv_cache_seq_len), fill with -inf where attention not allowed.
            # Mask might need slicing if q_seq_len or kv_cache_seq_len change.
            # Current mask is for the full attention matrix up to kv_cache_len x kv_cache_len.
            # We need mask for q_len (current tokens) x kv_cache_len (all tokens so far).
            current_q_len = xq.shape[2]
            current_kv_len = keys.shape[3]

            # This mask logic is typical for self-attention where Q, K, V come from same sequence.
            # For generation, Q is new token(s), K,V are all previous.
            # The mask ensures Q attends only to past K,V.
            # If mask is (max_sl, max_sl), slice it: mask[start_pos : start_pos+q_len, :kv_cache_len]
            # This simplified version assumes mask is correctly shaped or broadcastable.
            # For causal mask, typically: mask values are 0 or -np.inf. scores = scores + mask.
            scores = scores + mask[:, :, :current_q_len, :current_kv_len] # Ensure mask matches score shape up to current lengths


        # Softmax
        # Softmax = exp(scores) / sum(exp(scores), axis=-1, keepdims=True)
        # For numerical stability: scores = scores - max(scores, axis=-1, keepdims=True)
        # scores_max = scores.data.max(axis=-1, keepdims=True) # Max along kv_seq_len
        # scores_stabilized_data = scores.data - scores_max
        # attn_weights_data = np.exp(scores_stabilized_data) / np.sum(np.exp(scores_stabilized_data), axis=-1, keepdims=True)
        # attn_weights = OmegaTensor(attn_weights_data, requires_grad=True) # Simplified grad handling for softmax

        # Using a conceptual softmax that works with OmegaTensor
        def softmax_stable(s: OmegaTensor, axis: int = -1) -> OmegaTensor:
            s_max = OmegaTensor(s.data.max(axis=axis, keepdims=True), requires_grad=False) # Detach max for stability
            e_s = (s - s_max).exp() # s - s_max should handle broadcasting
            return e_s / e_s.sum(axis=axis, keepdims=True)

        attn_weights = softmax_stable(scores, axis=-1)

        # Output = attn_weights @ values
        # attn_weights: (bs, n_heads, q_seq_len, kv_cache_seq_len)
        # values: (bs, n_heads, kv_cache_seq_len, head_dim)
        # output_attention: (bs, n_heads, q_seq_len, head_dim)
        output_attention = attn_weights @ values

        # Concatenate heads and project
        # Reshape to (bs, q_seq_len, n_heads * head_dim)
        output_concat = output_attention.transpose((0, 2, 1, 3)).reshape(bsz, seqlen, -1)

        return self.wo(output_concat)


class FeedForward(OmegaLayer):
    def __init__(self, dim: int, hidden_dim: int, dtype=np.float32):
        super().__init__()
        self.w1 = Linear(dim, hidden_dim, bias=False, dtype=dtype)
        self.w2 = Linear(hidden_dim, dim, bias=False, dtype=dtype)
        self.w3 = Linear(dim, hidden_dim, bias=False, dtype=dtype) # For SwiGLU
        self._register_layer("w1", self.w1)
        self._register_layer("w2", self.w2)
        self._register_layer("w3", self.w3)

    def forward(self, x: OmegaTensor) -> OmegaTensor:
        # SwiGLU activation: silu(w1(x)) * w3(x)
        # silu(x) = x * sigmoid(x)

        swish_x = self.w1(x) # (bs, seq_len, hidden_dim)
        silu_out = swish_x * swish_x.sigmoid()

        gated_x = self.w3(x) # (bs, seq_len, hidden_dim)

        activated = silu_out * gated_x # Element-wise product

        return self.w2(activated) # Project back to dim


class TransformerBlock(OmegaLayer):
    def __init__(self, layer_id: int, args: SimpleModelArgs, dtype=np.float32):
        super().__init__()
        self.layer_id = layer_id
        self.args = args

        self.attention = Attention(args, dtype=dtype)
        self.feed_forward = FeedForward(dim=args.dim, hidden_dim=args.ffn_hidden_dim, dtype=dtype)

        self.attention_norm = RMSNorm(args.dim, eps=args.norm_eps, dtype=dtype)
        self.ffn_norm = RMSNorm(args.dim, eps=args.norm_eps, dtype=dtype)

        self._register_layer("attention", self.attention)
        self._register_layer("feed_forward", self.feed_forward)
        self._register_layer("attention_norm", self.attention_norm)
        self._register_layer("ffn_norm", self.ffn_norm)

    def forward(self, x: OmegaTensor, start_pos: int, freqs_cis: OmegaTensor, mask: Optional[OmegaTensor]) -> OmegaTensor:
        # Residual connection after attention
        # h = x + attention(RMSNorm(x))
        normed_x_attn = self.attention_norm(x)
        h = x + self.attention(normed_x_attn, start_pos, freqs_cis, mask)

        # Residual connection after feed-forward
        # out = h + feed_forward(RMSNorm(h))
        normed_h_ffn = self.ffn_norm(h)
        out = h + self.feed_forward(normed_h_ffn)

        return out


class TransformerOmega(OmegaLayer): # The main Transformer model
    def __init__(self, model_args: SimpleModelArgs, dtype=np.float32):
        super().__init__()
        self.args = model_args

        self.tok_embeddings = OmegaLayer() # Conceptually an Embedding layer
        # Embedding weights: (vocab_size, dim)
        emb_weight_data = np.random.randn(model_args.vocab_size, model_args.dim).astype(dtype) * 0.02
        self.tok_embeddings.weight = OmegaTensor(emb_weight_data, requires_grad=True)
        self.tok_embeddings._register_parameter("weight", self.tok_embeddings.weight)
        self._register_layer("tok_embeddings", self.tok_embeddings)

        self.layers = [TransformerBlock(i, model_args, dtype=dtype) for i in range(model_args.n_layers)]
        self._register_layer("layers", self.layers) # Register list of layers

        self.norm = RMSNorm(model_args.dim, eps=model_args.norm_eps, dtype=dtype)
        self._register_layer("norm", self.norm)

        self.output_proj = Linear(model_args.dim, model_args.vocab_size, bias=False, dtype=dtype)
        self._register_layer("output_proj", self.output_proj)

        # Precompute RoPE frequencies
        self.freqs_cis = self._precompute_freqs_cis(model_args.head_dim, model_args.max_seq_len, model_args.rope_theta, dtype=dtype)

    def _precompute_freqs_cis(self, head_dim: int, max_seq_len: int, theta: float, dtype=np.float32) -> OmegaTensor:
        # Based on LLaMA's RoPE:
        # freqs = 1.0 / (theta ** (arange(0, head_dim, 2)[:(head_dim//2)] / head_dim))
        # t = arange(max_seq_len)
        # freqs = outer(t, freqs) -> (max_seq_len, head_dim//2)
        # freqs_cis = polar(ones_like(freqs), freqs) -> complex numbers (cos + j*sin)
        # This results in shape (max_seq_len, head_dim//2) complex.
        # For use in apply_rotary_embeddings, we might need (max_seq_len, head_dim) real (interleaved).

        freqs_part = np.arange(0, head_dim, 2, dtype=dtype)[:(head_dim // 2)] / head_dim
        freqs = 1.0 / (theta ** freqs_part)

        t = np.arange(max_seq_len, dtype=dtype)
        freqs_outer = np.outer(t, freqs) # Shape: (max_seq_len, head_dim // 2)

        # freqs_cis_complex = np.exp(1j * freqs_outer) # This is cos(m*theta) + j*sin(m*theta)
        # To get (max_seq_len, head_dim) real, with interleaved cos/sin:
        cos_vals = np.cos(freqs_outer)
        sin_vals = np.sin(freqs_outer)

        freqs_cis_real_interleaved = np.zeros((max_seq_len, head_dim), dtype=dtype)
        freqs_cis_real_interleaved[:, 0::2] = cos_vals
        freqs_cis_real_interleaved[:, 1::2] = sin_vals

        return OmegaTensor(freqs_cis_real_interleaved, requires_grad=False)


    def forward(self, tokens: OmegaTensor, start_pos: int = 0) -> OmegaTensor:
        # tokens: (bs, seq_len) - integer token IDs
        _bsz, seqlen = tokens.shape

        # Token embeddings
        # h = self.tok_embeddings(tokens) -> This would be table lookup.
        # For OmegaTensor, use advanced indexing if available, or one-hot multiply.
        # Simplified embedding lookup:
        h_data = self.tok_embeddings.weight.data[tokens.data] # Numpy advanced indexing
        h = OmegaTensor(h_data, requires_grad=self.tok_embeddings.weight.requires_grad) # Simplistic grad prop for embedding

        # Get relevant part of freqs_cis for current sequence length and start_pos
        # The freqs_cis is (max_seq_len, head_dim).
        # apply_rotary_embeddings expects freqs for the current window.
        # current_freqs_cis = self.freqs_cis[start_pos : start_pos + seqlen]
        # This slicing is handled inside Attention forward method now.

        # Causal mask for self-attention
        # Mask shape: (1, 1, seqlen, seqlen) - broadcastable
        # For generation (seqlen=1), mask is not strictly needed for the new token,
        # but the KV cache ensures causality.
        # For training (seqlen > 1), causal mask is crucial.
        mask = None
        if seqlen > 1:
            # Create upper triangular matrix of -inf, diagonal 0.
            mask_data = np.full((seqlen, seqlen), -np.inf, dtype=h.dtype)
            mask_data = np.triu(mask_data, k=1) # Upper triangle (exclusive of diagonal) is -inf
            # Add dimensions for broadcasting: (1,1,seqlen,seqlen)
            mask = OmegaTensor(mask_data[np.newaxis, np.newaxis, :, :], requires_grad=False)

        # Pass through transformer blocks
        for layer in self.layers:
            h = layer(h, start_pos, self.freqs_cis, mask) # Pass full freqs_cis, layer will slice

        h = self.norm(h)
        output_logits = self.output_proj(h) # (bs, seq_len, vocab_size)

        return output_logits


# --- Example Usage ---
if __name__ == "__main__":
    print("--- LLaMA Layers with OmegaTensor Demo ---")

    args = SimpleModelArgs(
        dim=64, n_layers=2, n_heads=4, n_kv_heads=2, # GQA with n_kv_heads=2
        vocab_size=100, ffn_hidden_dim=128, max_seq_len=32
    )
    dtype_np = np.float32 # Define numpy dtype for consistency

    print(f"Model Args: dim={args.dim}, layers={args.n_layers}, heads={args.n_heads}, kv_heads={args.n_kv_heads}, vocab={args.vocab_size}")

    # 1. Test Linear Layer
    linear_layer = Linear(args.dim, args.ffn_hidden_dim, dtype=dtype_np)
    input_linear = OmegaTensor(np.random.rand(2, args.max_seq_len, args.dim).astype(dtype_np), requires_grad=True)
    output_linear = linear_layer(input_linear)
    print(f"Linear Layer: Input shape {input_linear.shape}, Output shape {output_linear.shape}")
    # Conceptual backward (if OmegaTensor had full AD)
    # loss_linear = output_linear.sum()
    # loss_linear.backward()
    # print(f"  Linear weight grad norm (conceptual): {np.linalg.norm(linear_layer.weight.grad.numpy()) if linear_layer.weight.grad else 'N/A'}")


    # 2. Test RMSNorm
    rms_norm_layer = RMSNorm(args.dim, eps=args.norm_eps, dtype=dtype_np)
    input_rms = OmegaTensor(np.random.rand(2, args.max_seq_len, args.dim).astype(dtype_np) * 5, requires_grad=True) # Scaled input
    output_rms = rms_norm_layer(input_rms)
    print(f"RMSNorm Layer: Input mean/std {input_rms.data.mean():.2f}/{input_rms.data.std():.2f}, Output mean/std {output_rms.data.mean():.2f}/{output_rms.data.std():.2f}")
    print(f"  Output shape {output_rms.shape}. RMSNorm weight value (example): {rms_norm_layer.weight.data[0]}")


    # 3. Test TransformerOmega Model (Full Run)
    model = TransformerOmega(args, dtype=dtype_np)
    print(f"TransformerOmega initialized. Total parameters (conceptual count): {len(model.parameters())}")

    # Dummy input tokens (batch_size=1, seq_len=10)
    batch_size_test = 1
    seq_len_test = 10
    dummy_tokens_data = np.random.randint(0, args.vocab_size, (batch_size_test, seq_len_test))
    dummy_tokens = OmegaTensor(dummy_tokens_data)

    print(f"Input tokens shape: {dummy_tokens.shape}")

    # Forward pass (training mode, start_pos=0)
    logits_train = model(dummy_tokens, start_pos=0)
    print(f"Logits (train mode): Shape {logits_train.shape}") # Expected: (bs, seq_len, vocab_size)

    # Simulate generation (token by token)
    # Reset KV caches by re-instantiating attention layers or clearing cache (conceptual)
    # For this demo, let's re-initialize caches in attention layers if we were to run generation loop.
    # Or, for a single next token, ensure start_pos is handled.
    # The current model's Attention layers manage their own cache internally based on start_pos.

    print("\nSimulating generation (one token):")
    # Assume we have processed `seq_len_test - 1` tokens, now processing the last one.
    last_token_input = OmegaTensor(dummy_tokens_data[:, -1:], dtype=dummy_tokens.dtype) # Shape (bs, 1)
    start_pos_gen = seq_len_test -1

    # To correctly use KV cache for generation, the model should be called token by token in a loop.
    # The provided TransformerOmega structure with internal KV cache in Attention layers
    # is designed for this. If start_pos=0, cache is reset. If start_pos > 0, cache is appended.

    # Let's simulate a few steps of generation to see KV cache in action:
    current_generated_tokens = []
    current_input_token = OmegaTensor(np.array([[dummy_tokens_data[0,0]]]), dtype=dummy_tokens.dtype) # Start with first token

    print("Generating 3 more tokens...")
    for i in range(3):
        current_start_pos = i # KV cache builds up from pos 0, 1, 2...
        print(f" Step {i}: Input token shape {current_input_token.shape}, start_pos={current_start_pos}")

        logits_gen_step = model(current_input_token, start_pos=current_start_pos)
        # logits_gen_step shape: (bs, 1, vocab_size)

        # Get next token by argmax (greedy decoding)
        next_token_id_data = np.argmax(logits_gen_step.data[:, -1, :], axis=-1) # Get from last position of seq_len dim
        next_token_id = next_token_id_data[0] # Assuming batch size 1
        current_generated_tokens.append(next_token_id)

        print(f"  Logits shape: {logits_gen_step.shape}, Next token ID: {next_token_id}")

        # Update input for next step
        current_input_token = OmegaTensor(np.array([[next_token_id]]), dtype=dummy_tokens.dtype)

        # Check KV cache size in one of the attention layers (conceptual check)
        # seq_len of cache_k should be i+1 after this step (for the first token processed, then +1 each time)
        # Example: Layer 0 Attention's cache_k shape
        # cache_k_shape_l0 = model.layers[0].attention.cache_k.shape if model.layers[0].attention.cache_k is not None else "None"
        # print(f"  Layer 0 Attention cache_k shape: {cache_k_shape_l0}")


    print(f"Generated token IDs: {current_generated_tokens}")

    # Check parameters count (conceptual)
    total_params = 0
    for p in model.parameters():
        total_params += p.data.size
    print(f"\nTotal conceptual parameters in TransformerOmega: {total_params}")

    print("\n--- LLaMA Layers Demo Complete ---")

```
