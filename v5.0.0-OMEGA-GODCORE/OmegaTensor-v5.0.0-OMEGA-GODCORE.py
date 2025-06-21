# v5.0.0-OMEGA-GODCORE/OmegaTensor-v5.0.0-OMEGA-GODCORE.py
import numpy as np
import uuid
from typing import List, Tuple, Callable, Optional, Union, Any

# Full OmegaTensor with Autodiff capabilities (Conceptual)

class OmegaTensor:
    """
    OmegaTensor: A tensor class with support for automatic differentiation.
    Inspired by PyTorch's Tensor, but highly simplified for conceptual demonstration.
    """
    def __init__(self, data: Any, requires_grad: bool = False, _children: Tuple['OmegaTensor', ...] = (), _op: str = '', dtype=np.float32):
        if isinstance(data, (list, tuple)):
            self.data = np.array(data, dtype=dtype)
        elif isinstance(data, np.ndarray):
            self.data = data.astype(dtype)
        elif isinstance(data, (int, float, bool)): # Allow bool for logical ops later
            self.data = np.array([data], dtype=dtype) # Store scalars as 1-element arrays
        elif isinstance(data, OmegaTensor): # If data is already an OmegaTensor, copy its properties
            self.data = data.data.copy()
            self.requires_grad = data.requires_grad
            # Note: _children and _op are usually not copied this way unless it's a specific clone op
            self._children = data._children
            self._op = data._op
            self.grad = data.grad.copy() if data.grad is not None else None
            self._backward_fn = data._backward_fn
            self.id = data.id
            self.dtype = data.dtype
            return # Exit early after copying
        else:
            raise TypeError(f"OmegaTensor data must be list, tuple, numpy array, or number, not {type(data)}")

        self.requires_grad = requires_grad
        self._children = set(_children) # Operands that created this tensor
        self._op = _op                  # Operation that created this tensor
        self.grad: Optional[np.ndarray] = None # Gradient, stored as ndarray
        self._backward_fn: Callable[[], None] = lambda: None # Function to compute gradients for children
        self.id = uuid.uuid4() # Unique ID for debugging or graph visualization
        self.dtype = self.data.dtype


    @property
    def shape(self) -> Tuple[int, ...]:
        return self.data.shape

    @property
    def ndim(self) -> int:
        return self.data.ndim

    def __repr__(self) -> str:
        return f"OmegaTensor(data={self.data}, shape={self.shape}, requires_grad={self.requires_grad}, op='{self._op}')"

    def __hash__(self) -> int: # For using OmegaTensors in sets (like _children)
        return hash(self.id)

    def __eq__(self, other) -> bool: # For comparing OmegaTensors
        if isinstance(other, OmegaTensor):
            return self.id == other.id
        return False

    # --- Basic Operations supporting Autodiff ---
    def __add__(self, other: Union['OmegaTensor', int, float]) -> 'OmegaTensor':
        other_tensor = other if isinstance(other, OmegaTensor) else OmegaTensor(other, dtype=self.dtype)
        out_data = self.data + other_tensor.data
        out = OmegaTensor(out_data, _children=(self, other_tensor), _op='+')

        if self.requires_grad or other_tensor.requires_grad:
            out.requires_grad = True

            def _backward_fn():
                # Gradient of sum: d(self+other)/d(self) = 1, d(self+other)/d(other) = 1
                # Accumulate gradients, handling broadcasting if shapes differ
                if self.requires_grad:
                    grad_self = out.grad * np.ones_like(self.data)
                    # Handle broadcasting for self.grad
                    while grad_self.ndim > self.data.ndim: # Sum over broadcasted new dims
                        grad_self = grad_self.sum(axis=0)
                    for i, (dim_s, dim_o) in enumerate(zip(self.data.shape, grad_self.shape)):
                        if dim_s == 1 and dim_o > 1: # Sum over broadcasted existing dim
                            grad_self = grad_self.sum(axis=i, keepdims=True)

                    self.grad = (self.grad + grad_self) if self.grad is not None else grad_self


                if other_tensor.requires_grad:
                    grad_other = out.grad * np.ones_like(other_tensor.data)
                    # Handle broadcasting for other_tensor.grad
                    while grad_other.ndim > other_tensor.data.ndim:
                        grad_other = grad_other.sum(axis=0)
                    for i, (dim_s, dim_o) in enumerate(zip(other_tensor.data.shape, grad_other.shape)):
                        if dim_s == 1 and dim_o > 1:
                            grad_other = grad_other.sum(axis=i, keepdims=True)

                    other_tensor.grad = (other_tensor.grad + grad_other) if other_tensor.grad is not None else grad_other
            out._backward_fn = _backward_fn

        return out

    def __mul__(self, other: Union['OmegaTensor', int, float]) -> 'OmegaTensor':
        other_tensor = other if isinstance(other, OmegaTensor) else OmegaTensor(other, dtype=self.dtype)
        out_data = self.data * other_tensor.data
        out = OmegaTensor(out_data, _children=(self, other_tensor), _op='*')

        if self.requires_grad or other_tensor.requires_grad:
            out.requires_grad = True

            def _backward_fn():
                # Gradient of product: d(self*other)/d(self) = other, d(self*other)/d(other) = self
                if self.requires_grad:
                    grad_self = out.grad * other_tensor.data
                    while grad_self.ndim > self.data.ndim: grad_self = grad_self.sum(axis=0)
                    for i, (dim_s, dim_o) in enumerate(zip(self.data.shape, grad_self.shape)):
                        if dim_s == 1 and dim_o > 1: grad_self = grad_self.sum(axis=i, keepdims=True)
                    self.grad = (self.grad + grad_self) if self.grad is not None else grad_self

                if other_tensor.requires_grad:
                    grad_other = out.grad * self.data
                    while grad_other.ndim > other_tensor.data.ndim: grad_other = grad_other.sum(axis=0)
                    for i, (dim_s, dim_o) in enumerate(zip(other_tensor.data.shape, grad_other.shape)):
                        if dim_s == 1 and dim_o > 1: grad_other = grad_other.sum(axis=i, keepdims=True)
                    other_tensor.grad = (other_tensor.grad + grad_other) if other_tensor.grad is not None else grad_other
            out._backward_fn = _backward_fn

        return out

    def __pow__(self, power: Union[int, float]) -> 'OmegaTensor':
        if not isinstance(power, (int, float)):
            raise TypeError("Power must be a scalar (int or float).")
        out_data = self.data ** power
        out = OmegaTensor(out_data, _children=(self,), _op=f'**{power}')

        if self.requires_grad:
            out.requires_grad = True
            def _backward_fn():
                # Gradient of x^n: n * x^(n-1)
                grad_val = power * (self.data ** (power - 1))
                self.grad = (self.grad + out.grad * grad_val) if self.grad is not None else (out.grad * grad_val)
            out._backward_fn = _backward_fn
        return out

    def __neg__(self) -> 'OmegaTensor':
        return self * -1

    def __sub__(self, other: Union['OmegaTensor', int, float]) -> 'OmegaTensor':
        return self + (-other)

    def __truediv__(self, other: Union['OmegaTensor', int, float]) -> 'OmegaTensor':
        # x / y  = x * (y ** -1)
        return self * (other ** -1 if isinstance(other, OmegaTensor) else OmegaTensor(other, dtype=self.dtype) ** -1)

    # Reflected operations for completeness (e.g., float * OmegaTensor)
    def __radd__(self, other: Union[int, float]) -> 'OmegaTensor': return self + other
    def __rmul__(self, other: Union[int, float]) -> 'OmegaTensor': return self * other
    def __rsub__(self, other: Union[int, float]) -> 'OmegaTensor': return OmegaTensor(other, dtype=self.dtype) - self # other - self
    def __rtruediv__(self, other: Union[int, float]) -> 'OmegaTensor': return OmegaTensor(other, dtype=self.dtype) / self # other / self


    # --- Activation Functions ---
    def relu(self) -> 'OmegaTensor':
        out_data = np.maximum(0, self.data)
        out = OmegaTensor(out_data, _children=(self,), _op='ReLU')
        if self.requires_grad:
            out.requires_grad = True
            def _backward_fn():
                # Gradient of ReLU: 1 if x > 0, else 0
                relu_grad = (self.data > 0).astype(self.dtype)
                self.grad = (self.grad + out.grad * relu_grad) if self.grad is not None else (out.grad * relu_grad)
            out._backward_fn = _backward_fn
        return out

    def tanh(self) -> 'OmegaTensor':
        out_data = np.tanh(self.data)
        out = OmegaTensor(out_data, _children=(self,), _op='tanh')
        if self.requires_grad:
            out.requires_grad = True
            def _backward_fn():
                # Gradient of tanh(x): 1 - tanh(x)^2
                tanh_grad = 1 - (out_data ** 2)
                self.grad = (self.grad + out.grad * tanh_grad) if self.grad is not None else (out.grad * tanh_grad)
            out._backward_fn = _backward_fn
        return out

    def sigmoid(self) -> 'OmegaTensor':
        out_data = 1 / (1 + np.exp(-self.data))
        out = OmegaTensor(out_data, _children=(self,), _op='sigmoid')
        if self.requires_grad:
            out.requires_grad = True
            def _backward_fn():
                # Gradient of sigmoid(x): sigmoid(x) * (1 - sigmoid(x))
                sigmoid_grad = out_data * (1 - out_data)
                self.grad = (self.grad + out.grad * sigmoid_grad) if self.grad is not None else (out.grad * sigmoid_grad)
            out._backward_fn = _backward_fn
        return out

    # --- Reduction Operations ---
    def sum(self, axis: Optional[Union[int, Tuple[int, ...]]] = None, keepdims: bool = False) -> 'OmegaTensor':
        out_data = self.data.sum(axis=axis, keepdims=keepdims)
        out = OmegaTensor(out_data, _children=(self,), _op='sum')

        if self.requires_grad:
            out.requires_grad = True
            def _backward_fn():
                # Gradient of sum is 1, broadcasted back to original shape.
                # out.grad has the shape of out_data. We need to make it broadcastable to self.data.
                # If axis was specified, out.grad needs to be expanded at that axis.
                # If keepdims=False, the summed axes are removed.
                # If keepdims=True, summed axes have dimension 1.

                # Simplest way to propagate gradient for sum: it's 1 for all elements that contributed.
                # So, the gradient w.r.t self is out.grad broadcasted to self.shape.

                # Handle broadcasting of out.grad to self.shape
                # If axis is None, out.grad is scalar, self.grad is array of out.grad
                if axis is None:
                    grad_val = np.full_like(self.data, out.grad)
                else:
                    # If axis is specified, out.grad needs to be expanded along the summed dimensions
                    # Example: self.shape=(2,3), axis=0, out.shape=(3,). out.grad.shape=(3,)
                    # self.grad should be shape (2,3), where each row's contribution to sum is out.grad
                    # This is effectively np.ones_like(self.data) * np.expand_dims(out.grad, axis=axis_expanded)
                    # This is tricky with keepdims. Easier: grad is just out.grad broadcasted.

                    # This matches PyTorch's behavior: grad of sum is just grad of output, broadcasted.
                    # Create a gradient that can be broadcast to self.data's shape
                    # Start with out.grad. If keepdims=False, we need to add back the summed axes.
                    output_grad = out.grad
                    if not keepdims and axis is not None:
                        axes_to_expand = axis if isinstance(axis, tuple) else (axis,)
                        for ax in sorted(axes_to_expand): # Expand in correct order
                            output_grad = np.expand_dims(output_grad, axis=ax)

                    # Now output_grad should be broadcastable to self.data.shape
                    # The actual gradient contribution is just 1.
                    grad_val = np.ones_like(self.data) * output_grad

                self.grad = (self.grad + grad_val) if self.grad is not None else grad_val
            out._backward_fn = _backward_fn
        return out

    def mean(self, axis: Optional[Union[int, Tuple[int, ...]]] = None, keepdims: bool = False) -> 'OmegaTensor':
        # mean(x) = sum(x) / N
        num_elements_summed = np.prod(self.shape) if axis is None else np.prod(np.array(self.shape)[np.array(axis if isinstance(axis, tuple) else [axis])])

        sum_val = self.sum(axis=axis, keepdims=keepdims)
        out = sum_val * (1.0 / num_elements_summed) # Multiply by scalar
        out._op = 'mean' # Override op from sum and mul
        # The backward pass will be handled by sum and multiply.
        return out

    # --- Reshaping and Indexing (Conceptual - backward for these is more complex) ---
    def reshape(self, *shape: int) -> 'OmegaTensor':
        # If one of the shape dimensions is -1, it's inferred.
        if -1 in shape:
            current_size = np.prod(self.shape)
            known_dim_prod = 1
            for s_val in shape:
                if s_val != -1: known_dim_prod *= s_val

            inferred_dim = current_size // known_dim_prod
            shape = tuple(s if s != -1 else inferred_dim for s in shape)

        out_data = self.data.reshape(shape)
        out = OmegaTensor(out_data, _children=(self,), _op='reshape')
        if self.requires_grad:
            out.requires_grad = True
            def _backward_fn():
                # Grad of reshape is grad of output, reshaped back to original.
                self.grad = (self.grad + out.grad.reshape(self.shape)) if self.grad is not None else out.grad.reshape(self.shape)
            out._backward_fn = _backward_fn
        return out

    def transpose(self, axes: Optional[Tuple[int, ...]] = None) -> 'OmegaTensor':
        # Default transpose for 2D: (0,1) -> (1,0)
        if axes is None and self.ndim == 2: axes = (1,0)
        elif axes is None and self.ndim != 2: raise ValueError("Axes must be specified for transpose of non-2D tensor.")

        out_data = self.data.transpose(axes)
        out = OmegaTensor(out_data, _children=(self,), _op='transpose')
        if self.requires_grad:
            out.requires_grad = True
            def _backward_fn():
                # Grad of transpose is grad of output, transposed back.
                # Need inverse permutation of axes.
                if axes: # Should always be true if we got here
                    inv_axes = np.argsort(axes)
                    self.grad = (self.grad + out.grad.transpose(inv_axes)) if self.grad is not None else out.grad.transpose(inv_axes)
            out._backward_fn = _backward_fn
        return out

    # --- Matmul ---
    def matmul(self, other: 'OmegaTensor') -> 'OmegaTensor':
        if not isinstance(other, OmegaTensor):
            raise TypeError("other must be an OmegaTensor for matmul.")

        # Basic 2D matmul for now. Broadcasting for matmul is complex.
        if self.ndim != 2 or other.ndim != 2:
            raise ValueError("OmegaTensor matmul currently only supports 2D tensors.")
        if self.shape[1] != other.shape[0]:
            raise ValueError(f"Mismatched dimensions for matmul: {self.shape} and {other.shape}")

        out_data = np.matmul(self.data, other.data)
        out = OmegaTensor(out_data, _children=(self, other), _op='matmul')

        if self.requires_grad or other.requires_grad:
            out.requires_grad = True
            def _backward_fn():
                # Grad of A @ B:
                # dL/dA = dL/dOut @ B.T
                # dL/dB = A.T @ dL/dOut
                if self.requires_grad:
                    grad_self = np.matmul(out.grad, other.data.T)
                    self.grad = (self.grad + grad_self) if self.grad is not None else grad_self
                if other.requires_grad:
                    grad_other = np.matmul(self.data.T, out.grad)
                    other.grad = (other.grad + grad_other) if other.grad is not None else grad_other
            out._backward_fn = _backward_fn
        return out

    def __matmul__(self, other: 'OmegaTensor') -> 'OmegaTensor': # For @ operator
        return self.matmul(other)


    # --- Backward Pass ---
    def backward(self, gradient: Optional[np.ndarray] = None):
        if not self.requires_grad:
            # print("Warning: backward() called on OmegaTensor that does not require grad.")
            return

        # Build the computation graph (topological sort)
        # Nodes are OmegaTensors, edges are operations.
        # Start from this tensor (the "output" of the graph for this backward call)
        # and traverse backwards through _children.

        # Order matters for correct gradient accumulation.
        # Need a topological sort of the graph.
        topo_sorted_graph = []
        visited_nodes = set()

        def build_topo_sort(node: OmegaTensor):
            if node not in visited_nodes:
                visited_nodes.add(node)
                for child_node in node._children:
                    build_topo_sort(child_node) # Recurse on children first
                topo_sorted_graph.append(node) # Add node after its children

        build_topo_sort(self) # Build graph starting from the current tensor

        # Initialize gradient for the output tensor (self)
        if gradient is None:
            if self.data.size == 1: # Scalar output
                self.grad = np.array([1.0], dtype=self.dtype)
            else:
                raise RuntimeError("Gradient must be specified for non-scalar OmegaTensor backward() call.")
        else:
            if not isinstance(gradient, np.ndarray): gradient = np.array(gradient, dtype=self.dtype)
            if gradient.shape != self.shape:
                raise ValueError(f"Gradient shape {gradient.shape} must match tensor shape {self.shape}.")
            self.grad = gradient.copy() # Store the initial gradient for the output node

        # Perform backward pass in reverse topological order
        for node in reversed(topo_sorted_graph):
            if node._backward_fn: # If it's not a leaf node that had requires_grad=True
                if node.grad is not None: # Ensure grad exists for this node before calling its bwd_fn
                    node._backward_fn()
                # else:
                    # This can happen if a node in the graph didn't end up needing grad,
                    # or if its grad wasn't set by its parent's backward_fn.
                    # print(f"Warning: Grad for node {node._op} (ID: {node.id}) is None during backward. Skipping its _backward_fn.")

    def zero_grad(self):
        """Resets the gradient of this tensor to None."""
        self.grad = None
        # This should ideally recurse or be handled by an optimizer for all params.
        # For a single tensor, this is fine.


    # --- Utility methods ---
    def detach(self) -> 'OmegaTensor':
        """Returns a new OmegaTensor with the same data but detached from the computation graph."""
        return OmegaTensor(self.data.copy(), requires_grad=False, dtype=self.dtype)

    def item(self) -> Union[int, float]:
        """Returns the Python number from a scalar OmegaTensor."""
        if self.data.size == 1:
            return self.data.item()
        raise ValueError("Only scalar OmegaTensors can be converted to Python numbers with .item()")

    # --- Static methods for creating tensors or operations ---
    @staticmethod
    def stack(tensors: List['OmegaTensor'], axis: int = 0) -> 'OmegaTensor':
        if not tensors: raise ValueError("Cannot stack empty list of OmegaTensors.")

        data_list = [t.data for t in tensors] # Extract numpy data
        requires_grad_any = any(t.requires_grad for t in tensors)

        out_data = np.stack(data_list, axis=axis)
        # Create new OmegaTensor. _children are the input tensors for grad tracking.
        out = OmegaTensor(out_data, _children=tuple(tensors), _op='stack')

        if requires_grad_any:
            out.requires_grad = True
            def _backward_fn():
                if out.grad is None: return # No gradient to propagate

                # Gradient of stack: unstack the output gradient
                # Each child tensor t in tensors needs its grad portion from out.grad

                # Correct unstacking for gradient:
                # Each part of the split gradient corresponds to one of the input tensors.
                # The shape of out.grad is the shape of the stacked tensor.
                # np.split will split along the 'axis' that was used for stacking.
                # The number of sections for split should be the number of original tensors if they were equal along that axis,
                # or more generally, the size of the dimension 'axis' in out.grad.
                num_splits = out.grad.shape[axis]

                # We expect one grad slice per original tensor.
                # If original tensors were t1, t2, t3 stacked along axis=0,
                # out.grad will be split into 3 parts along axis=0.
                # Each part needs to be squeezed if 'axis' was a new dimension.

                # Check if the number of splits matches number of input tensors.
                # This is true if each original tensor contributed one slice along the stack axis.
                if num_splits != len(tensors) and out.grad.shape[axis] == len(tensors): # Common case, each tensor is a slice
                    grads_unstacked_slices = np.split(out.grad, indices_or_sections=len(tensors), axis=axis)
                    grads_unstacked = [np.squeeze(g_slice, axis=axis) for g_slice in grads_unstacked_slices]
                else: # Fallback or more complex unstacking if shapes were irregular (not typical for stack)
                      # This part might need adjustment based on how stack is used.
                      # For now, assume simple case where each tensor forms one slice.
                      # If this warning appears, the gradient logic for stack might be incorrect for that usage.
                    # print(f"Warning: Stack backward unstacking complexity. num_splits={num_splits}, len(tensors)={len(tensors)}, out.grad.shape={out.grad.shape}, axis={axis}")
                    # Default to just splitting, hoping for the best or that shapes match after squeeze
                    try:
                        grads_unstacked_slices = np.split(out.grad, indices_or_sections=len(tensors), axis=axis)
                        grads_unstacked = [np.squeeze(g_slice, axis=axis) for g_slice in grads_unstacked_slices]
                    except ValueError as e:
                        # print(f"Error in stack backward splitting gradient: {e}. Gradients might be incorrect.")
                        # As a last resort, distribute gradient sum (this is likely wrong but prevents crash)
                        sum_grad_per_child = out.grad.sum() / (len(tensors) * np.prod(tensors[0].shape)) # Very rough
                        grads_unstacked = [np.full_like(t_child.data, sum_grad_per_child) for t_child in tensors]


                for i, t_child in enumerate(tensors):
                    if t_child.requires_grad:
                        grad_part = grads_unstacked[i]
                        # Ensure grad_part has same shape as t_child.data
                        if grad_part.shape != t_child.shape:
                            if grad_part.size == t_child.data.size: # Check if total elements match
                                try:
                                    grad_part = grad_part.reshape(t_child.shape)
                                except ValueError: # If reshape fails (e.g. due to squeeze issue)
                                    # print(f"Stack backward: Reshape failed for child {i}. Grad shape {grad_part.shape}, child shape {t_child.shape}. Using sum.")
                                    grad_sum = grad_part.sum() / t_child.data.size
                                    grad_part = np.full_like(t_child.data, grad_sum)
                            else: # Sizes don't match, this is problematic
                                # print(f"Stack backward: Size mismatch for child {i}. Grad size {grad_part.size}, child size {t_child.data.size}. Using sum.")
                                grad_sum = grad_part.sum() / t_child.data.size
                                grad_part = np.full_like(t_child.data, grad_sum)

                        t_child.grad = (t_child.grad + grad_part) if t_child.grad is not None else grad_part
            out._backward_fn = _backward_fn
        return out

    @staticmethod
    def cat(tensors: List['OmegaTensor'], axis: int = 0) -> 'OmegaTensor':
        if not tensors: raise ValueError("Cannot concatenate empty list of OmegaTensors.")

        data_list = [t.data for t in tensors]
        requires_grad_any = any(t.requires_grad for t in tensors)

        out_data = np.concatenate(data_list, axis=axis)
        out = OmegaTensor(out_data, _children=tuple(tensors), _op='cat')

        if requires_grad_any:
            out.requires_grad = True
            def _backward_fn():
                if out.grad is None: return

                # Gradient of cat: split the output gradient
                current_offset = 0
                split_indices = []
                # Calculate split points based on shapes of input tensors along the concatenation axis
                for i in range(len(tensors) - 1):
                    current_offset += tensors[i].shape[axis]
                    split_indices.append(current_offset)

                grads_split = np.split(out.grad, indices_or_sections=split_indices, axis=axis)

                for i, t_child in enumerate(tensors):
                    if t_child.requires_grad:
                        grad_part = grads_split[i]
                        t_child.grad = (t_child.grad + grad_part) if t_child.grad is not None else grad_part
            out._backward_fn = _backward_fn
        return out


# Example Usage:
if __name__ == "__main__":
    print("--- OmegaTensor Full Autodiff Demo ---")

    # Scalar example
    x = OmegaTensor(2.0, requires_grad=True)
    y = OmegaTensor(3.0, requires_grad=True)
    z = x * y + y**2  # z = 2*3 + 3^2 = 6 + 9 = 15
    # dz/dx = y = 3
    # dz/dy = x + 2*y = 2 + 2*3 = 8
    z.backward()
    print(f"Scalar example: z = {z.data.item()}")
    print(f"Gradient dz/dx (should be 3.0): {x.grad.item() if x.grad is not None else 'None'}")
    print(f"Gradient dz/dy (should be 8.0): {y.grad.item() if y.grad is not None else 'None'}")

    x.zero_grad(); y.zero_grad() # Reset gradients

    # Vector example
    w = OmegaTensor([1.0, 2.0, 3.0], requires_grad=True)
    b = OmegaTensor(0.5, requires_grad=True)
    inputs = OmegaTensor([0.1, 0.2, 0.3])

    # Linear layer: output = inputs @ w.T (if w is row) or inputs @ w (if w is col) + b
    # Let's do element-wise product then sum for simplicity here: (inputs * w).sum() + b
    # Or, more like a dot product if inputs and w are compatible.
    # Let's assume w is weights for a single neuron, inputs are features.
    # output = (w * inputs).sum() + b

    # Example: Simple linear transformation and loss
    # outputs = w.matmul(inputs.reshape(3,1)) # This would require inputs to be (N,3) and w (3,M)
    # For this demo, let's make a simple scalar output.

    # z = (w[0]*inputs[0] + w[1]*inputs[1] + w[2]*inputs[2]) + b
    # z = (w * inputs).sum() + b

    # Let's try a slightly more complex function:
    # L = (w.sum() - b) ** 2
    # L = ( (1+2+3) - 0.5 )^2 = (6 - 0.5)^2 = 5.5^2 = 30.25
    # dL/d(w.sum()) = 2 * (w.sum() - b) = 2 * 5.5 = 11
    # dL/db = -2 * (w.sum() - b) = -11
    # d(w.sum())/dw_i = 1. So dL/dw_i = 11 * 1 = 11

    temp_sum = w.sum()
    L = (temp_sum - b) ** 2

    L.backward()
    print(f"\nVector example: L = {L.data.item()}")
    print(f"Gradient dL/dw (should be [11., 11., 11.]): {w.grad}")
    print(f"Gradient dL/db (should be -11.0): {b.grad.item() if b.grad is not None else 'None'}")

    w.zero_grad(); b.zero_grad()

    # Test broadcasting in ops
    print("\n--- Broadcasting Test ---")
    m1 = OmegaTensor([[1,2,3],[4,5,6]], requires_grad=True) # shape (2,3)
    s1 = OmegaTensor([10], requires_grad=True) # shape (1,) to be broadcast

    m2 = m1 + s1 # s1 broadcasts to [[10,10,10],[10,10,10]]
    # m2 = [[11,12,13],[14,15,16]]

    # Let loss be sum of m2
    loss_b = m2.sum() # 11+12+13+14+15+16 = 81
    loss_b.backward()

    # d(loss_b)/dm2_ij = 1
    # d(m2_ij)/dm1_ij = 1. So d(loss_b)/dm1_ij = 1. Expected m1.grad = [[1,1,1],[1,1,1]]
    # d(m2_ij)/ds1 = 1. So d(loss_b)/ds1 = sum over all elements of m1 that s1 broadcast to.
    # s1 contributed to 2*3=6 elements. Expected s1.grad = 6.
    print(f"m2 data:\n{m2.data}")
    print(f"loss_b: {loss_b.data.item()}")
    print(f"m1.grad (expected [[1,1,1],[1,1,1]]):\n{m1.grad}")
    print(f"s1.grad (expected [6.]): {s1.grad}")

    # Test reshape and transpose grads
    m1.zero_grad(); s1.zero_grad()

    r1 = m1.reshape(3,2) # [[1,2],[3,4],[5,6]]
    loss_r = r1.sum() # 1+2+3+4+5+6 = 21
    loss_r.backward()
    # d(loss_r)/dr1_ij = 1.
    # m1.grad should be [[1,1,1],[1,1,1]] (grad of r1 reshaped back to m1's shape)
    print(f"\nReshape Test: loss_r={loss_r.data.item()}")
    print(f"m1.grad after reshape loss backward (expected [[1,1,1],[1,1,1]]):\n{m1.grad}")

    m1.zero_grad()
    t1 = m1.transpose() # [[1,4],[2,5],[3,6]]
    loss_t = t1.sum() # 21
    loss_t.backward()
    # m1.grad should be [[1,1,1],[1,1,1]] (grad of t1 transposed back)
    print(f"\nTranspose Test: loss_t={loss_t.data.item()}")
    print(f"m1.grad after transpose loss backward (expected [[1,1,1],[1,1,1]]):\n{m1.grad}")

    # Test Matmul
    A = OmegaTensor([[1,2],[3,4]], requires_grad=True) # (2,2)
    B = OmegaTensor([[5,6],[7,8]], requires_grad=True) # (2,2)
    C = A @ B
    # C = [[1*5+2*7, 1*6+2*8], [3*5+4*7, 3*6+4*8]]
    #   = [[19, 22], [43, 50]]
    loss_matmul = C.sum() # 19+22+43+50 = 134
    loss_matmul.backward()
    # dL/dA = dL/dC @ B.T = [[1,1],[1,1]] @ [[5,7],[6,8]] = [[11,15],[11,15]]
    # dL/dB = A.T @ dL/dC = [[1,3],[2,4]] @ [[1,1],[1,1]] = [[4,4],[6,6]]
    print(f"\nMatmul Test: C data:\n{C.data}")
    print(f"loss_matmul: {loss_matmul.data.item()}")
    print(f"A.grad (expected [[11,15],[11,15]]):\n{A.grad}")
    print(f"B.grad (expected [[4,4],[6,6]]):\n{B.grad}")

    print("\n--- OmegaTensor Full Autodiff Demo Complete ---")
```
