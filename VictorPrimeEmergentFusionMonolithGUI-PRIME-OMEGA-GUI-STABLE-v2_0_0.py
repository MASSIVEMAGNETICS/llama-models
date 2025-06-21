# VictorPrimeEmergentFusionMonolithGUI-PRIME-OMEGA-GUI-STABLE-v2_0_0.py
import tkinter as tk
from tkinter import scrolledtext, ttk, simpledialog, filedialog, messagebox
import threading
import time
import uuid
import json # For potential config or state saving/loading for GUI itself
import os # For path operations
from typing import List, Dict, Any, Optional, Callable

# --- Conceptual GUI Components ---

class TheLight:
    """
    Conceptual "TheLight" component. In the OFRC, this is a source/detector
    of emergent signals or coherence within the AGI's mesh/state.
    This GUI version provides a visual representation and manual trigger.
    """
    def __init__(self, name: str = "TheLight_Nexus", initial_intensity: float = 0.0,
                 initial_coherence: float = 0.0,
                 on_phase_event_handler: Optional[Dict[str, Any]] = None): # handler: {"callback": func, "threshold": float, "once": bool, "agi_instance": obj}
        self.name = name
        self.intensity = initial_intensity # 0.0 to 1.0, e.g., overall activity level
        self.phase_coherence = initial_coherence # 0.0 to 1.0, e.g., how ordered/resonant the AGI state is
        self.color = self._calculate_light_color() # Hex color string
        self.event_log: List[str] = []
        self.on_phase_event_handler = on_phase_event_handler # To trigger AGI functions

    def update_state(self, new_intensity: Optional[float] = None, new_coherence: Optional[float] = None):
        if new_intensity is not None:
            self.intensity = max(0.0, min(1.0, new_intensity))
        if new_coherence is not None:
            self.phase_coherence = max(0.0, min(1.0, new_coherence))

        self.color = self._calculate_light_color()
        self._log_event(f"State Update: Intensity={self.intensity:.2f}, Coherence={self.phase_coherence:.2f}, Color={self.color}")

        # Check for phase event trigger
        if self.on_phase_event_handler:
            handler_cb = self.on_phase_event_handler.get("callback")
            threshold = self.on_phase_event_handler.get("threshold", 0.95) # Default threshold
            agi_instance_ref = self.on_phase_event_handler.get("agi_instance")

            if handler_cb and callable(handler_cb) and self.phase_coherence >= threshold:
                self._log_event(f"PHASE EVENT TRIGGERED! Coherence {self.phase_coherence:.2f} >= threshold {threshold:.2f}")
                try:
                    if agi_instance_ref: # Pass AGI instance and self (TheLight instance) to callback
                        handler_cb(self, self.phase_coherence) # Callback is agi_instance._trigger_self_replication_event(light_instance, coherence_score)
                    else: # Legacy call if no agi_instance provided
                        handler_cb(self.phase_coherence)
                except Exception as e:
                    self._log_event(f"Error during phase event callback: {e}")

                if self.on_phase_event_handler.get("once", False):
                    self.on_phase_event_handler = None # Trigger only once
                    self._log_event("Phase event handler removed after single trigger.")


    def _calculate_light_color(self) -> str:
        # Simple color mapping:
        # Intensity -> brightness (value in HSV)
        # Coherence -> hue (e.g., red for low coherence, green/blue for high)
        # Saturation can be fixed or also mapped.

        # Hue: 0 (red) for coherence=0, up to 240 (blue) for coherence=1
        # For simplicity, let's map coherence to Green component, intensity to Red/Blue
        # Low coherence (more chaotic) -> more Red
        # High coherence (ordered) -> more Blue
        # Intensity -> overall brightness

        r = int((1 - self.phase_coherence) * self.intensity * 255)
        g = int(self.phase_coherence * self.intensity * 150) # Green less prominent for "tech" feel
        b = int(self.phase_coherence * self.intensity * 255)

        # Ensure values are within 0-255
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))

        return f"#{r:02x}{g:02x}{b:02x}"

    def _log_event(self, message: str):
        log_entry = f"[{time.strftime('%H:%M:%S')}] {self.name}: {message}"
        self.event_log.append(log_entry)
        if len(self.event_log) > 100: # Keep last 100 logs
            self.event_log.pop(0)
        # print(log_entry) # Also print to console for GUI-less context

    def get_status(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "intensity": self.intensity,
            "phase_coherence": self.phase_coherence,
            "current_color": self.color,
            "log_preview": self.event_log[-5:] # Last 5 log entries
        }

    def on_phase_event(self): # Manual trigger for GUI or testing
        """Manually checks and triggers the phase event if conditions met."""
        # print(f"[{self.name}] Manual on_phase_event check called.")
        if self.on_phase_event_handler:
            handler_cb = self.on_phase_event_handler.get("callback")
            threshold = self.on_phase_event_handler.get("threshold", 0.95)
            agi_instance_ref = self.on_phase_event_handler.get("agi_instance")

            if handler_cb and callable(handler_cb) and self.phase_coherence >= threshold:
                self._log_event(f"MANUAL PHASE EVENT TRIGGER! Coherence {self.phase_coherence:.2f} >= threshold {threshold:.2f}")
                try:
                    if agi_instance_ref:
                        handler_cb(self, self.phase_coherence)
                    else:
                        handler_cb(self.phase_coherence)
                except Exception as e:
                    self._log_event(f"Error during manual phase event callback: {e}")

                if self.on_phase_event_handler.get("once", False):
                    self.on_phase_event_handler = None
                    self._log_event("Phase event handler removed after single manual trigger.")
            # else:
                # print(f"  Manual trigger: Conditions not met (Coherence: {self.phase_coherence:.2f}, Threshold: {threshold:.2f}) or no valid callback.")


# --- Conceptual Self-Replication Trigger ---
# This function would be part of the AGI's core logic, not directly in GUI file usually.
# Placed here as it was in the original filename reference.
# The `TheLight` component above now handles calling a callback from the AGI instance.

def trigger_self_replication(agi_instance: Any, coherence_threshold: float = 0.98,
                             reason: str = "High Coherence Event") -> bool:
    """
    Conceptual trigger for AGI self-replication.
    `agi_instance`: The AGI instance that might replicate.
    `coherence_threshold`: The AGI's internal coherence must meet this to replicate.
    """
    # print(f"\nAttempting to trigger self-replication for AGI: {getattr(agi_instance, 'instance_id', 'Unknown AGI')}")
    # print(f"Reason: {reason}, Required Coherence: {coherence_threshold:.2f}")

    # 1. Check AGI's internal coherence (conceptual)
    # This would query a part of the AGI that measures its own state coherence.
    # For this demo, let's assume the agi_instance has a `the_light_source` like OFRC.
    current_coherence = 0.0
    light_source_name = "UnknownLight"

    if hasattr(agi_instance, 'the_light_source') and isinstance(agi_instance.the_light_source, TheLight):
        current_coherence = agi_instance.the_light_source.phase_coherence
        light_source_name = agi_instance.the_light_source.name
        # print(f"  Retrieved coherence {current_coherence:.2f} from AGI's TheLight source '{light_source_name}'.")
    elif hasattr(agi_instance, 'get_status_report'): # Fallback: try to get from status report
        status = agi_instance.get_status_report()
        # This depends on how coherence might be reported.
        # For now, this is a loose check.
        current_coherence = status.get("SystemCoherence", status.get("PhaseCoherence", random.uniform(0.7, 0.99))) # Dummy
        # print(f"  Retrieved conceptual coherence {current_coherence:.2f} from AGI status report.")
    else:
        # print("  AGI instance does not have a direct coherence measure. Simulating high coherence for demo.")
        current_coherence = 0.99 # Simulate high coherence if cannot be found

    if current_coherence >= coherence_threshold:
        # print(f"  Coherence requirement met ({current_coherence:.2f} >= {coherence_threshold:.2f}).")
        # 2. Initiate replication process (highly conceptual)
        # This would involve:
        #   - Allocating resources for a new AGI instance.
        #   - Copying the AGI's core code and knowledge base (or a snapshot).
        #   - Initializing the new instance, possibly with some variations (evolution).
        #   - Establishing communication or isolation as per design.
        # print("  CONCEPTUAL: Initiating AGI self-replication sequence...")
        time.sleep(0.1) # Simulate resource allocation

        # In a real system, this would involve complex OS/Cloud interactions.
        # For OFRC, this is handled by `agi_instance._trigger_self_replication_event` via TheLight callback.
        # This standalone function is more of a direct command.
        if hasattr(agi_instance, '_trigger_self_replication_event') and callable(agi_instance._trigger_self_replication_event):
            # print("  Calling AGI's internal replication trigger...")
            # The internal trigger expects (light_instance, coherence_score)
            # We need a dummy light_instance here if calling directly.
            dummy_light = TheLight(name="DirectTriggerLight", initial_coherence=current_coherence)
            dummy_light.on_phase_event_handler = {"agi_instance": agi_instance} # Ensure agi_instance is there for the callback's context

            # The AGI's method might already check coherence.
            # Here, we are forcing it based on the external check.
            agi_instance._trigger_self_replication_event(dummy_light, current_coherence)
            # print("  AGI internal replication trigger called. Outcome depends on AGI's implementation.")
            return True # Assume the call was made.
        else:
            # print("  AGI instance does not have a '_trigger_self_replication_event' method. Conceptual replication 'succeeded'.")
            # Simulate creating a "replica ID"
            replica_id = f"Replica_of_{getattr(agi_instance, 'instance_id', 'OriginalAGI')}_{uuid.uuid4().hex[:4]}"
            # print(f"  New AGI Replica conceptually created with ID: {replica_id}")
            return True
    else:
        # print(f"  Coherence requirement NOT met ({current_coherence:.2f} < {coherence_threshold:.2f}). Replication aborted.")
        return False


# --- Minimal GUI Application (Illustrative) ---
# This is a very basic Tkinter GUI to visualize TheLight and interact.
# A full "InfiniteDevUI" would be vastly more complex (e.g., using web frameworks or advanced GUI toolkits).

class InfiniteDevUI_Placeholder(tk.Tk):
    def __init__(self, agi_instance_ref: Optional[Any] = None): # Pass a reference to the AGI if available
        super().__init__()
        self.title("Victor Prime GUI - TheLight Nexus (Placeholder)")
        self.geometry("600x450")
        self.configure(bg="#1e1e1e") # Dark background

        self.agi_instance = agi_instance_ref # Store reference to AGI (e.g. OFRC instance)

        # --- TheLight Visualization ---
        self.the_light_display = TheLight(name="GUI_Visual_Light") # Independent TheLight for GUI display
        if self.agi_instance and hasattr(self.agi_instance, 'the_light_source'):
            # If AGI has its own TheLight, GUI can reflect that one.
            # For this demo, let's assume GUI controls its own visual TheLight,
            # but can also *trigger* events on the AGI's TheLight.
            pass

        self.light_canvas = tk.Canvas(self, width=100, height=100, bg="#101010", highlightthickness=0)
        self.light_canvas.pack(pady=20)
        self.light_oval = self.light_canvas.create_oval(10, 10, 90, 90, fill=self.the_light_display.color, outline="#333")

        self.status_label = ttk.Label(self, text="TheLight Status: Intensity=0.00, Coherence=0.00",
                                     foreground="#bbb", background="#1e1e1e", font=("Consolas", 10))
        self.status_label.pack(pady=5)

        # --- Controls for TheLight ---
        controls_frame = ttk.Frame(self, style="Dark.TFrame")
        controls_frame.pack(pady=10, padx=10, fill=tk.X)

        ttk.Label(controls_frame, text="Intensity:", style="Dark.TLabel").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.intensity_scale = ttk.Scale(controls_frame, from_=0.0, to=1.0, orient=tk.HORIZONTAL, length=150, command=self._update_gui_light_from_scales)
        self.intensity_scale.set(self.the_light_display.intensity)
        self.intensity_scale.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(controls_frame, text="Coherence:", style="Dark.TLabel").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.coherence_scale = ttk.Scale(controls_frame, from_=0.0, to=1.0, orient=tk.HORIZONTAL, length=150, command=self._update_gui_light_from_scales)
        self.coherence_scale.set(self.the_light_display.phase_coherence)
        self.coherence_scale.grid(row=1, column=1, padx=5, pady=5)

        # --- AGI Interaction Buttons ---
        action_frame = ttk.Frame(self, style="Dark.TFrame")
        action_frame.pack(pady=10, padx=10, fill=tk.X)

        self.sync_with_agi_button = ttk.Button(action_frame, text="Sync from AGI's TheLight", command=self._sync_from_agi_light, style="Dark.TButton")
        self.sync_with_agi_button.pack(side=tk.LEFT, padx=5)
        if not (self.agi_instance and hasattr(self.agi_instance, 'the_light_source')):
            self.sync_with_agi_button.config(state=tk.DISABLED)

        self.trigger_agi_phase_event_button = ttk.Button(action_frame, text="Trigger AGI Phase Event", command=self._trigger_agi_phase_event, style="Dark.TButton")
        self.trigger_agi_phase_event_button.pack(side=tk.LEFT, padx=5)
        if not (self.agi_instance and hasattr(self.agi_instance, 'the_light_source')):
             self.trigger_agi_phase_event_button.config(state=tk.DISABLED)

        self.trigger_replication_button = ttk.Button(action_frame, text="Cmd: AGI Self-Replicate", command=self._command_agi_self_replicate, style="Dark.TButton")
        self.trigger_replication_button.pack(side=tk.LEFT, padx=5)
        if not self.agi_instance: # Disable if no AGI instance
            self.trigger_replication_button.config(state=tk.DISABLED)


        # Log display for TheLight events
        self.log_text = scrolledtext.ScrolledText(self, height=6, width=70, wrap=tk.WORD, bg="#252525", fg="#ccc", font=("Consolas", 9), relief=tk.FLAT)
        self.log_text.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        self.log_text.insert(tk.END, "GUI Initialized. TheLight event log:\n")
        self.log_text.config(state=tk.DISABLED)

        self._setup_styles()
        self._update_gui_light_display() # Initial display update

    def _setup_styles(self):
        style = ttk.Style(self)
        style.theme_use('clam') # Use a theme that allows more customization
        style.configure("Dark.TFrame", background="#1e1e1e")
        style.configure("Dark.TLabel", foreground="#bbb", background="#1e1e1e", font=("Consolas", 10))
        style.configure("Dark.TButton", foreground="#fff", background="#333", borderwidth=1, relief=tk.RAISED, font=("Consolas", 10))
        style.map("Dark.TButton", background=[('active', '#555')], relief=[('pressed', tk.SUNKEN)])
        style.configure("Horizontal.TScale", background="#1e1e1e", troughcolor="#444")


    def _update_gui_light_from_scales(self, event=None):
        intensity = self.intensity_scale.get()
        coherence = self.coherence_scale.get()
        self.the_light_display.update_state(new_intensity=intensity, new_coherence=coherence)
        self._update_gui_light_display()
        self._update_log_display()

    def _update_gui_light_display(self):
        self.light_canvas.itemconfig(self.light_oval, fill=self.the_light_display.color)
        status_txt = f"TheLight Status: Intensity={self.the_light_display.intensity:.2f}, Coherence={self.the_light_display.phase_coherence:.2f}"
        self.status_label.config(text=status_txt)

    def _update_log_display(self):
        self.log_text.config(state=tk.NORMAL)
        # Efficiently update log: clear only if needed, or append intelligently
        # For simplicity, just show last N entries from the_light_display's log
        self.log_text.delete('1.0', tk.END)
        self.log_text.insert(tk.END, "TheLight Event Log (GUI Visual Light):\n")
        for entry in self.the_light_display.event_log[-10:]: # Show last 10
            self.log_text.insert(tk.END, entry + "\n")
        self.log_text.see(tk.END) # Scroll to end
        self.log_text.config(state=tk.DISABLED)

    def _sync_from_agi_light(self):
        if self.agi_instance and hasattr(self.agi_instance, 'the_light_source'):
            agi_light = self.agi_instance.the_light_source
            if isinstance(agi_light, TheLight):
                self.the_light_display.update_state(new_intensity=agi_light.intensity, new_coherence=agi_light.phase_coherence)
                # Copy AGI's light log to GUI's light log for context
                self.the_light_display.event_log.extend(agi_light.event_log[-5:]) # Add last 5 from AGI
                while len(self.the_light_display.event_log) > 100: self.the_light_display.event_log.pop(0)

                self._update_gui_light_display()
                self._update_log_display()
                self.intensity_scale.set(agi_light.intensity)
                self.coherence_scale.set(agi_light.phase_coherence)
                messagebox.showinfo("Sync", "GUI TheLight synced with AGI's TheLight state.")
            else:
                messagebox.showerror("Sync Error", "AGI's 'the_light_source' is not a valid TheLight instance.")
        else:
            messagebox.showerror("Sync Error", "AGI instance or its TheLight source not available.")

    def _trigger_agi_phase_event(self):
        if self.agi_instance and hasattr(self.agi_instance, 'the_light_source'):
            agi_light = self.agi_instance.the_light_source
            if isinstance(agi_light, TheLight):
                # Set AGI's light coherence to GUI's current coherence to test trigger
                # This is for testing; normally AGI light updates internally.
                # agi_light.update_state(new_coherence=self.the_light_display.phase_coherence)

                # Call the AGI's TheLight on_phase_event method to check and trigger its callback
                self.the_light_display._log_event(f"Manually requesting AGI's TheLight '{agi_light.name}' to check phase event.")
                agi_light.on_phase_event() # This will use AGI Light's current coherence.

                # Update GUI log with AGI's light log to see if event triggered
                self.the_light_display.event_log.extend(agi_light.event_log[-5:])
                while len(self.the_light_display.event_log) > 100: self.the_light_display.event_log.pop(0)
                self._update_log_display()
                messagebox.showinfo("AGI Phase Event", "Requested AGI's TheLight to check its phase event. See log.")
            else:
                messagebox.showerror("Trigger Error", "AGI's 'the_light_source' is not a valid TheLight instance.")
        else:
            messagebox.showerror("Trigger Error", "AGI instance or its TheLight source not available for phase event.")


    def _command_agi_self_replicate(self):
        if self.agi_instance:
            self.the_light_display._log_event("GUI Command: Attempting AGI Self-Replication...")
            self._update_log_display()

            # Use the standalone trigger_self_replication function
            # It needs a coherence threshold. We can use the GUI's current coherence scale value
            # as a *simulated* current AGI coherence for this direct command.
            # Or, a fixed high threshold to test the mechanism.

            # Let's assume for this direct command, we test if AGI *would* replicate if its coherence
            # was, for example, the value on the GUI's coherence scale.
            # The trigger_self_replication function itself will check the AGI's actual coherence (or simulate it).

            threshold_for_command = self.coherence_scale.get() # Use GUI scale as test threshold

            success = trigger_self_replication(self.agi_instance, coherence_threshold=threshold_for_command, reason="GUI Command Trigger")

            if success:
                self.the_light_display._log_event("AGI Self-Replication initiated (conceptual).")
                messagebox.showinfo("Self-Replication", "AGI self-replication process initiated (conceptually).")
            else:
                self.the_light_display._log_event("AGI Self-Replication conditions not met or failed.")
                messagebox.showwarning("Self-Replication", "AGI self-replication conditions not met or failed.")
            self._update_log_display()
        else:
             messagebox.showerror("Replication Error", "No AGI instance available to command replication.")


# --- Main Application Runner ---
if __name__ == "__main__":
    # For demo, create a dummy AGI instance that has a TheLight component
    class DummyAGIForGUI:
        def __init__(self):
            self.instance_id = "DummyAGI_001"
            # This AGI's own TheLight source
            self.the_light_source = TheLight(name="AGI_Internal_Light", initial_intensity=0.3, initial_coherence=0.2)
            # Setup a simple callback for its TheLight's phase event
            self.the_light_source.on_phase_event_handler = {
                "callback": self._internal_replication_trigger,
                "threshold": 0.9, # AGI's own threshold
                "agi_instance": self # Pass self to the callback
            }
            self.replication_log = []

        def _internal_replication_trigger(self, light_instance_that_triggered: TheLight, coherence_score: float):
            # This method is called by self.the_light_source when its coherence meets its threshold
            log_msg = f"INTERNAL REPLICATION TRIGGERED by '{light_instance_that_triggered.name}'! Coherence: {coherence_score:.2f}. Replicating {self.instance_id}..."
            # print(log_msg)
            self.replication_log.append(log_msg)
            # Simulate creating a replica ID
            new_id = f"Replica_of_{self.instance_id}_{uuid.uuid4().hex[:4]}"
            self.replication_log.append(f"  New replica conceptualized: {new_id}")
            light_instance_that_triggered._log_event(f"Callback: Replication for {self.instance_id} initiated. New conceptual ID: {new_id}")


        def get_status_report(self): # Dummy method for trigger_self_replication fallback
            return {"SystemCoherence": self.the_light_source.phase_coherence}

        # This method allows the standalone trigger_self_replication to call the internal one
        def _trigger_self_replication_event(self, light_instance: TheLight, coherence_score: float):
            # This is what OFRC's TheLight callback would point to.
            # It might have its own checks or directly call the replication logic.
            self._internal_replication_trigger(light_instance, coherence_score)


    dummy_agi = DummyAGIForGUI()

    # Simulate AGI's internal TheLight changing over time (in a separate thread for GUI responsiveness)
    def simulate_agi_light_changes(agi_ref):
        for i in range(20): # Simulate a few changes
            if not app_running_flag[0]: break # Stop if GUI closes
            time.sleep(2)
            new_i = random.uniform(0.1, 0.9)
            new_c = random.uniform(0.0, 1.0) # Test high coherence sometimes
            if hasattr(agi_ref, 'the_light_source') and agi_ref.the_light_source:
                agi_ref.the_light_source.update_state(new_intensity=new_i, new_coherence=new_c)
                # print(f"  (SimThread) AGI Light updated: I={new_i:.2f}, C={new_c:.2f}")
        # print("  (SimThread) AGI Light simulation finished.")

    app_running_flag = [True] # Use a list to make it mutable for the thread

    app = InfiniteDevUI_Placeholder(agi_instance_ref=dummy_agi)

    simulation_thread = threading.Thread(target=simulate_agi_light_changes, args=(dummy_agi,), daemon=True)
    simulation_thread.start()

    try:
        app.mainloop()
    finally:
        app_running_flag[0] = False # Signal thread to stop
        # print("GUI closed. Exiting.")
```
