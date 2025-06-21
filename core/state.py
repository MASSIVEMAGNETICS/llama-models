# core/state.py
import uuid
import time
import json
import pickle # For serialization
import os
import copy # For deep copying states

class FractalState:
    """
    Manages the AGI's state, including history, timelines, and evolution.
    The state is "fractal" in the sense that it can branch and maintain
    multiple coherent timelines for hypothetical reasoning or rollbacks.
    """
    def __init__(self, initial_state: Optional[Dict[str, Any]] = None, max_history_depth: int = 100):
        self.instance_id = f"FS-{uuid.uuid4().hex[:6]}"
        self.max_history_depth = max_history_depth

        # Core state dictionary
        self.state: Dict[str, Any] = {
            "identity": f"VictorCore_Instance_{self.instance_id}",
            "version": "0.1.0-alpha",
            "creation_timestamp": time.time(),
            "last_updated_timestamp": time.time(),
            "current_timeline": "main_timeline",
            "evolution_level": 0,
            "entropy": 0.0, # A measure of system disorder or uncertainty
            "operational_mode": "nominal", # e.g., nominal, learning, crisis, self_repair
            "consciousness_metrics": {}, # Placeholder for CEL outputs
            "active_modules": [],
            "recent_errors": [],
            "system_health": 1.0, # 0.0 (critical) to 1.0 (optimal)
            "meta": {} # For additional, less structured metadata
        }
        if initial_state:
            self.state.update(initial_state)

        # History management: stores snapshots of the state dictionary
        # Each entry in history is a tuple: (timestamp, timeline_id, state_snapshot)
        self.history: collections.deque[Tuple[float, str, Dict[str, Any]]] = collections.deque(maxlen=max_history_depth)
        self._save_current_state_to_history("genesis") # Initial state snapshot

        # Timeline management: stores divergent states
        # Key: timeline_id, Value: list of state snapshots for that timeline
        self.timelines: Dict[str, List[Dict[str, Any]]] = {
            "main_timeline": [copy.deepcopy(self.state)]
        }

        self.lock = threading.Lock() # For thread-safe state modifications

    def _save_current_state_to_history(self, event_description: str):
        """Internal method to save a deep copy of the current state to history."""
        with self.lock:
            snapshot = copy.deepcopy(self.state)
            snapshot["meta"]["history_event"] = event_description
            snapshot["meta"]["history_timestamp"] = time.time()

            self.history.append((snapshot["meta"]["history_timestamp"], self.state["current_timeline"], snapshot))

            # Also update the current timeline's log
            if self.state["current_timeline"] not in self.timelines:
                self.timelines[self.state["current_timeline"]] = [] # Should not happen if managed properly
            self.timelines[self.state["current_timeline"]].append(snapshot)

            # Prune timeline history if it exceeds max_history_depth (optional, can grow large)
            if len(self.timelines[self.state["current_timeline"]]) > self.max_history_depth * 2: # Allow more than deque for active timeline
                self.timelines[self.state["current_timeline"]] = self.timelines[self.state["current_timeline"]][-self.max_history_depth:]


    def update_state(self, key: str, value: Any, event_description: Optional[str] = None):
        """Updates a specific key in the state and records the change."""
        with self.lock:
            if key in self.state or key.startswith("custom_"): # Allow new custom keys
                self.state[key] = value
                self.state["last_updated_timestamp"] = time.time()
                if event_description:
                    self._save_current_state_to_history(event_description)
                else:
                    self._save_current_state_to_history(f"Update key: {key}")
            else:
                # Consider logging a warning or error for non-standard keys
                # For now, we'll allow adding new keys but it's better to define them upfront.
                self.state[key] = value
                self.state["last_updated_timestamp"] = time.time()
                self._save_current_state_to_history(f"Update new key: {key}")


    def get_state(self, key: Optional[str] = None) -> Any:
        """Retrieves the entire state or a specific key from it."""
        with self.lock:
            if key:
                return self.state.get(key)
            return copy.deepcopy(self.state) # Return a copy to prevent external modification

    def save_state(self, event_description: str):
        """Explicitly saves the current state to history."""
        self._save_current_state_to_history(event_description)

    def undo(self, steps: int = 1) -> bool:
        """
        Rolls back the state on the current timeline by a number of steps.
        Restores state from history.
        """
        with self.lock:
            if steps <= 0 or steps > len(self.history):
                return False # Cannot undo

            # Find history entries relevant to the current timeline
            current_timeline_history = [h for h in list(self.history) if h[1] == self.state["current_timeline"]]

            if steps > len(current_timeline_history): # Not enough history on this timeline
                 # Try to find the (n-steps)th overall history item if timeline specific fails
                if len(self.history) >= steps +1: # Need at least steps+1 to have a previous state
                    # The state to restore is (len - steps -1)th from the end of history
                    # This is equivalent to the (steps)th previous state.
                    # Example: history = [s0, s1, s2, s3], current is s3. undo 1 step -> s2.
                    # steps=1, restore_index = len-1-1 = len-2.
                    # steps=2, restore_index = len-1-2 = len-3.
                    try:
                        # We want to restore the state that was current *before* the last `steps` changes.
                        # If history has [H0, H1, H2, H3 (current)], undo 1 step means restore H2.
                        # H2 is at index len(history)-2.
                        # So, if steps=1, we want history[len-1-1]. If steps=k, history[len-1-k]
                        restore_index = len(self.history) - 1 - steps
                        if restore_index < 0: return False # Not enough history overall

                        _, _, state_to_restore = self.history[restore_index]
                        self.state = copy.deepcopy(state_to_restore)
                        self.state["last_updated_timestamp"] = time.time()
                        self.state["meta"]["history_event"] = f"Rolled back {steps} steps (general history)"

                        # The history deque itself is not modified, new states will push out old ones.
                        # We add the restored state as a new "current" state.
                        self._save_current_state_to_history(f"State restored after rollback of {steps} general steps")
                        return True
                    except IndexError:
                        return False # Should not happen if length check is correct
                else:
                    return False


            # If current timeline specific history is sufficient:
            # The state to restore is the (steps)-th previous state on this timeline.
            # Example: timeline_history = [T0, T1, T2, T3 (current)]. Undo 1 step -> T2.
            # T2 is at index len(timeline_history)-2.
            try:
                restore_idx_timeline = len(current_timeline_history) - 1 - steps
                if restore_idx_timeline < 0: return False

                _, _, state_to_restore_timeline = current_timeline_history[restore_idx_timeline]
                self.state = copy.deepcopy(state_to_restore_timeline)
                self.state["last_updated_timestamp"] = time.time()
                self.state["meta"]["history_event"] = f"Rolled back {steps} steps on timeline '{self.state['current_timeline']}'"
                self._save_current_state_to_history(f"State restored after rollback on timeline '{self.state['current_timeline']}'")
                return True
            except IndexError:
                 return False # Should not happen

    def create_timeline(self, new_timeline_id: str, from_history_step: Optional[int] = None) -> bool:
        """
        Creates a new timeline, branching from the current state or a specified history point.
        `from_history_step`: if provided, branches from the Nth step back in the current timeline's history.
        """
        with self.lock:
            if new_timeline_id in self.timelines:
                return False # Timeline already exists

            if from_history_step is not None:
                current_timeline_log = self.timelines.get(self.state["current_timeline"], [])
                if from_history_step <= 0 or from_history_step > len(current_timeline_log):
                    return False # Invalid history step

                # The state to branch from is (from_history_step)-th from the end of current_timeline_log
                branch_state_index = len(current_timeline_log) - from_history_step
                branch_state = copy.deepcopy(current_timeline_log[branch_state_index])
            else:
                branch_state = copy.deepcopy(self.state) # Branch from current state

            branch_state["current_timeline"] = new_timeline_id
            branch_state["meta"]["branched_from_timeline"] = self.state["current_timeline"]
            branch_state["meta"]["branched_at_timestamp"] = time.time()

            self.timelines[new_timeline_id] = [branch_state]
            # Optionally, switch to the new timeline immediately
            # self.switch_timeline(new_timeline_id, "Timeline created: " + new_timeline_id)
            return True

    def switch_timeline(self, timeline_id: str, event_description: Optional[str] = None) -> bool:
        """Switches the active state to a different timeline."""
        with self.lock:
            if timeline_id not in self.timelines or not self.timelines[timeline_id]:
                return False # Timeline does not exist or is empty

            # Save current state before switching
            self._save_current_state_to_history(f"Switching from timeline '{self.state['current_timeline']}'")

            self.state = copy.deepcopy(self.timelines[timeline_id][-1]) # Load last state of target timeline
            self.state["current_timeline"] = timeline_id # Ensure it's set correctly
            self.state["last_updated_timestamp"] = time.time()

            desc = event_description if event_description else f"Switched to timeline '{timeline_id}'"
            self._save_current_state_to_history(desc) # Record the switch in the new timeline
            return True

    def merge_timeline(self, source_timeline_id: str, strategy: str = "overwrite_current", event_description: Optional[str] = None) -> bool:
        """
        Merges another timeline into the current one.
        `strategy`: 'overwrite_current', 'discard_source_changes_on_conflict', 'apply_source_changes_prefer_source'.
        This is a complex operation; this implementation is simplified.
        """
        with self.lock:
            if source_timeline_id not in self.timelines or not self.timelines[source_timeline_id]:
                return False # Source timeline invalid
            if source_timeline_id == self.state["current_timeline"]:
                return True # Already on this timeline, nothing to merge

            source_timeline_last_state = copy.deepcopy(self.timelines[source_timeline_id][-1])

            # Simplified merge: overwrite current state with source timeline's last state
            if strategy == "overwrite_current":
                self.state = source_timeline_last_state
                self.state["current_timeline"] = self.state["current_timeline"] # Keep current timeline ID
                self.state["meta"]["merged_from_timeline"] = source_timeline_id
                self.state["meta"]["merge_strategy"] = strategy
                self.state["last_updated_timestamp"] = time.time()

                desc = event_description if event_description else f"Merged timeline '{source_timeline_id}' using '{strategy}'"
                self._save_current_state_to_history(desc)
                # Optionally, delete the source timeline after merge
                # del self.timelines[source_timeline_id]
                return True
            else:
                # More complex strategies would involve diffing states and resolving conflicts.
                # This is a placeholder for such logic.
                print(f"Warning: Merge strategy '{strategy}' not fully implemented. Using simplified overwrite.")
                self.state = source_timeline_last_state # Fallback to overwrite
                self.state["current_timeline"] = self.state["current_timeline"]
                self.state["meta"]["merged_from_timeline"] = source_timeline_id
                self.state["meta"]["merge_strategy"] = strategy + " (simplified)"
                self._save_current_state_to_history(f"Attempted merge of '{source_timeline_id}' with '{strategy}'")

                return False # Indicate complex merge not fully done.

    def export_state(self, filepath: str) -> bool:
        """Exports the current full FractalState (including history and timelines) to a file."""
        with self.lock:
            try:
                data_to_export = {
                    "instance_id": self.instance_id,
                    "max_history_depth": self.max_history_depth,
                    "state": self.state,
                    "history": list(self.history), # Convert deque to list for serialization
                    "timelines": self.timelines
                }
                with open(filepath, "wb") as f:
                    pickle.dump(data_to_export, f)
                return True
            except Exception as e:
                print(f"Error exporting state: {e}")
                return False

    def import_state(self, filepath: str) -> bool:
        """Imports a FractalState from a file, overwriting the current one."""
        with self.lock:
            if not os.path.exists(filepath):
                return False
            try:
                with open(filepath, "rb") as f:
                    imported_data = pickle.load(f)

                self.instance_id = imported_data.get("instance_id", self.instance_id)
                self.max_history_depth = imported_data.get("max_history_depth", self.max_history_depth)
                self.state = imported_data["state"]
                self.history = collections.deque(imported_data.get("history", []), maxlen=self.max_history_depth)
                self.timelines = imported_data.get("timelines", {"main_timeline": [copy.deepcopy(self.state)]})

                # Ensure current timeline exists in timelines object after import
                if self.state["current_timeline"] not in self.timelines:
                    self.timelines[self.state["current_timeline"]] = [copy.deepcopy(self.state)]
                elif not self.timelines[self.state["current_timeline"]]: # If timeline exists but is empty
                     self.timelines[self.state["current_timeline"]].append(copy.deepcopy(self.state))

                self.state["last_updated_timestamp"] = time.time() # Mark as updated now
                self._save_current_state_to_history("State imported from file")
                return True
            except Exception as e:
                print(f"Error importing state: {e}")
                return False

    def get_history_log(self, last_n: Optional[int] = None) -> List[Dict[str, Any]]:
        """Returns a summary of the history log."""
        log_summary = []
        history_list = list(self.history)

        entries_to_show = history_list
        if last_n is not None and last_n > 0:
            entries_to_show = history_list[-last_n:]

        for ts, timeline, state_snap in entries_to_show:
            log_summary.append({
                "timestamp": ts,
                "timeline": timeline,
                "event": state_snap.get("meta", {}).get("history_event", "Unknown event"),
                "evolution_level": state_snap.get("evolution_level", "N/A"),
                "operational_mode": state_snap.get("operational_mode", "N/A")
            })
        return log_summary

if __name__ == '__main__':
    # Example Usage
    fs = FractalState(initial_state={"system_name": "VictorDemo"})
    print(f"Initial State ({fs.state['current_timeline']}): {fs.get_state('system_name')}, Evo: {fs.get_state('evolution_level')}")

    fs.update_state("evolution_level", 1, "First evolution cycle")
    fs.update_state("entropy", 0.1, "Entropy increased slightly")
    print(f"State after updates ({fs.state['current_timeline']}): Evo: {fs.get_state('evolution_level')}, Entropy: {fs.get_state('entropy')}")

    # Create a new timeline
    fs.create_timeline("hypothetical_scenario_A")
    print(f"Created timeline: 'hypothetical_scenario_A'")

    # Switch to the new timeline and make changes
    fs.switch_timeline("hypothetical_scenario_A", "Exploring scenario A")
    fs.update_state("operational_mode", "simulation", "Scenario A: simulation mode active")
    fs.update_state("custom_scenario_param", 123, "Set scenario parameter")
    print(f"State on timeline '{fs.state['current_timeline']}': Mode: {fs.get_state('operational_mode')}, Param: {fs.get_state('custom_scenario_param')}")

    # Switch back to main timeline
    fs.switch_timeline("main_timeline", "Returning to main operations")
    print(f"State on timeline '{fs.state['current_timeline']}': Evo: {fs.get_state('evolution_level')}, Mode: {fs.get_state('operational_mode')}")
    # Note: custom_scenario_param should not exist on main_timeline unless merged

    # Undo last change on main timeline
    fs.undo(1)
    print(f"State after undo on '{fs.state['current_timeline']}': Evo: {fs.get_state('evolution_level')}, Entropy: {fs.get_state('entropy')}") # Entropy should be back to 0.0

    # Export and import
    state_file = "fractal_state_backup.pkl"
    if fs.export_state(state_file):
        print(f"State exported to {state_file}")

        fs_new = FractalState() # Create a fresh instance
        if fs_new.import_state(state_file):
            print(f"State imported into new instance. Current timeline: {fs_new.get_state('current_timeline')}, Evo: {fs_new.get_state('evolution_level')}")
            os.remove(state_file) # Clean up

    print("\nHistory Log (last 5 entries):")
    for entry in fs.get_history_log(last_n=5):
        print(f"- {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(entry['timestamp']))} [{entry['timeline']}] Event: {entry['event']}, Evo: {entry['evolution_level']}")

    print(f"\nTotal history entries: {len(fs.history)}")
    print(f"Timelines available: {list(fs.timelines.keys())}")

```python
# core/state.py
import uuid
import time
import json
import pickle # For serialization
import os
import copy # For deep copying states
import collections # For deque
from typing import List, Dict, Any, Optional, Tuple, Deque # Type hinting

class FractalState:
    """
    Manages the AGI's state, including history, timelines, and evolution.
    The state is "fractal" in the sense that it can branch and maintain
    multiple coherent timelines for hypothetical reasoning or rollbacks.
    """
    def __init__(self, initial_state: Optional[Dict[str, Any]] = None, max_history_depth: int = 100):
        self.instance_id = f"FS-{uuid.uuid4().hex[:6]}"
        self.max_history_depth = max_history_depth

        # Core state dictionary
        self.state: Dict[str, Any] = {
            "identity": f"VictorCore_Instance_{self.instance_id}",
            "version": "0.1.0-alpha",
            "creation_timestamp": time.time(),
            "last_updated_timestamp": time.time(),
            "current_timeline": "main_timeline",
            "evolution_level": 0,
            "entropy": 0.0, # A measure of system disorder or uncertainty
            "operational_mode": "nominal", # e.g., nominal, learning, crisis, self_repair
            "consciousness_metrics": {}, # Placeholder for CEL outputs
            "active_modules": [],
            "recent_errors": [],
            "system_health": 1.0, # 0.0 (critical) to 1.0 (optimal)
            "meta": {} # For additional, less structured metadata
        }
        if initial_state:
            self.state.update(initial_state)

        # History management: stores snapshots of the state dictionary
        # Each entry in history is a tuple: (timestamp, timeline_id, state_snapshot)
        self.history: Deque[Tuple[float, str, Dict[str, Any]]] = collections.deque(maxlen=max_history_depth)
        self._save_current_state_to_history("genesis") # Initial state snapshot

        # Timeline management: stores divergent states
        # Key: timeline_id, Value: list of state snapshots for that timeline
        self.timelines: Dict[str, List[Dict[str, Any]]] = {
            "main_timeline": [copy.deepcopy(self.state)]
        }

        self.lock = threading.Lock() # For thread-safe state modifications

    def _save_current_state_to_history(self, event_description: str):
        """Internal method to save a deep copy of the current state to history."""
        with self.lock:
            snapshot = copy.deepcopy(self.state)
            snapshot["meta"]["history_event"] = event_description
            snapshot["meta"]["history_timestamp"] = time.time()

            self.history.append((snapshot["meta"]["history_timestamp"], self.state["current_timeline"], snapshot))

            # Also update the current timeline's log
            if self.state["current_timeline"] not in self.timelines:
                self.timelines[self.state["current_timeline"]] = []
            self.timelines[self.state["current_timeline"]].append(snapshot)

            if len(self.timelines[self.state["current_timeline"]]) > self.max_history_depth * 2:
                self.timelines[self.state["current_timeline"]] = self.timelines[self.state["current_timeline"]][-self.max_history_depth:]


    def update_state(self, key: str, value: Any, event_description: Optional[str] = None):
        """Updates a specific key in the state and records the change."""
        with self.lock:
            self.state[key] = value
            self.state["last_updated_timestamp"] = time.time()
            desc = event_description if event_description else f"Update key: {key}"
            self._save_current_state_to_history(desc)


    def get_state(self, key: Optional[str] = None) -> Any:
        """Retrieves the entire state or a specific key from it."""
        with self.lock:
            if key:
                return self.state.get(key)
            return copy.deepcopy(self.state)

    def save_state(self, event_description: str):
        """Explicitly saves the current state to history."""
        self._save_current_state_to_history(event_description)

    def undo(self, steps: int = 1) -> bool:
        """
        Rolls back the state on the current timeline by a number of steps.
        Restores state from history.
        """
        with self.lock:
            if steps <= 0: return False

            current_timeline_history_snapshots = [h_snap for ts, tl_id, h_snap in list(self.history) if tl_id == self.state["current_timeline"]]

            if steps >= len(current_timeline_history_snapshots): # Cannot go back further than the beginning of this timeline's history
                # If trying to undo beyond current timeline's start, check overall history for a valid state
                if steps < len(self.history):
                    # Restore the (len(history) - 1 - steps)-th state from global history
                    # This is the state *before* the last 'steps' changes in global history.
                    _ts, _tl, state_to_restore = self.history[len(self.history) - 1 - steps]
                    self.state = copy.deepcopy(state_to_restore)
                    self.state["last_updated_timestamp"] = time.time()
                    self._save_current_state_to_history(f"Rolled back {steps} global steps to state from timeline '{_tl}'")
                    return True
                return False # Not enough global history either

            # If sufficient history on the current timeline:
            # The state to restore is `steps` snapshots back *within the filtered list for this timeline*.
            # e.g. current_timeline_history_snapshots = [S0, S1, S2 (current)]. steps=1 -> S1. S1 is at index len-2.
            state_to_restore = current_timeline_history_snapshots[len(current_timeline_history_snapshots) - 1 - steps]
            self.state = copy.deepcopy(state_to_restore)
            self.state["last_updated_timestamp"] = time.time()
            self._save_current_state_to_history(f"Rolled back {steps} steps on timeline '{self.state['current_timeline']}'")
            return True

    def create_timeline(self, new_timeline_id: str, from_history_step: Optional[int] = None) -> bool:
        """
        Creates a new timeline, branching from the current state or a specified history point
        within the *current timeline's history log*.
        `from_history_step`: Nth step back in current timeline's log (1 = last state, etc.).
        """
        with self.lock:
            if new_timeline_id in self.timelines:
                return False

            current_timeline_log = self.timelines.get(self.state["current_timeline"], [])
            if not current_timeline_log: # Should not happen if initialized correctly
                 branch_state = copy.deepcopy(self.state) # Fallback
            elif from_history_step is not None:
                if from_history_step <= 0 or from_history_step > len(current_timeline_log):
                    return False
                branch_state_index = len(current_timeline_log) - from_history_step
                branch_state = copy.deepcopy(current_timeline_log[branch_state_index])
            else:
                branch_state = copy.deepcopy(self.state)

            branch_state["current_timeline"] = new_timeline_id
            branch_state["meta"]["branched_from_timeline"] = self.state["current_timeline"]
            branch_state["meta"]["branched_at_timestamp"] = time.time()

            self.timelines[new_timeline_id] = [branch_state]
            return True

    def switch_timeline(self, timeline_id: str, event_description: Optional[str] = None) -> bool:
        """Switches the active state to a different timeline."""
        with self.lock:
            if timeline_id not in self.timelines or not self.timelines[timeline_id]:
                return False

            self._save_current_state_to_history(f"Switching from timeline '{self.state['current_timeline']}'")

            self.state = copy.deepcopy(self.timelines[timeline_id][-1])
            self.state["current_timeline"] = timeline_id
            self.state["last_updated_timestamp"] = time.time()

            desc = event_description if event_description else f"Switched to timeline '{timeline_id}'"
            self._save_current_state_to_history(desc)
            return True

    def merge_timeline(self, source_timeline_id: str, strategy: str = "overwrite_current", event_description: Optional[str] = None) -> bool:
        """Simplified merge: overwrites current state with source timeline's last state."""
        with self.lock:
            if source_timeline_id not in self.timelines or not self.timelines[source_timeline_id]:
                return False
            if source_timeline_id == self.state["current_timeline"]:
                return True

            source_timeline_last_state = copy.deepcopy(self.timelines[source_timeline_id][-1])

            if strategy == "overwrite_current":
                # Preserve the current timeline's ID after overwriting content
                current_id_before_merge = self.state["current_timeline"]
                self.state = source_timeline_last_state
                self.state["current_timeline"] = current_id_before_merge
                self.state["meta"]["merged_from_timeline"] = source_timeline_id
                self.state["meta"]["merge_strategy"] = strategy
                self.state["last_updated_timestamp"] = time.time()

                desc = event_description if event_description else f"Merged timeline '{source_timeline_id}' using '{strategy}'"
                self._save_current_state_to_history(desc)
                return True
            else:
                print(f"Warning: Merge strategy '{strategy}' not fully implemented. No merge performed.")
                return False

    def export_state(self, filepath: str) -> bool:
        """Exports the current full FractalState to a file."""
        with self.lock:
            try:
                data_to_export = {
                    "instance_id": self.instance_id,
                    "max_history_depth": self.max_history_depth,
                    "state": self.state,
                    "history": list(self.history),
                    "timelines": self.timelines
                }
                with open(filepath, "wb") as f:
                    pickle.dump(data_to_export, f)
                return True
            except Exception as e:
                print(f"Error exporting state: {e}")
                return False

    def import_state(self, filepath: str) -> bool:
        """Imports a FractalState from a file, overwriting the current one."""
        with self.lock:
            if not os.path.exists(filepath):
                return False
            try:
                with open(filepath, "rb") as f:
                    imported_data = pickle.load(f)

                self.instance_id = imported_data.get("instance_id", self.instance_id)
                self.max_history_depth = imported_data.get("max_history_depth", self.max_history_depth)
                self.state = imported_data["state"]
                self.history = collections.deque(imported_data.get("history", []), maxlen=self.max_history_depth)
                self.timelines = imported_data.get("timelines", {"main_timeline": [copy.deepcopy(self.state)]})

                if self.state["current_timeline"] not in self.timelines: # Ensure consistency
                    self.timelines[self.state["current_timeline"]] = [copy.deepcopy(self.state)]
                elif not self.timelines[self.state["current_timeline"]]:
                     self.timelines[self.state["current_timeline"]].append(copy.deepcopy(self.state))

                self.state["last_updated_timestamp"] = time.time()
                self._save_current_state_to_history("State imported from file")
                return True
            except Exception as e:
                print(f"Error importing state: {e}")
                return False

    def get_history_log(self, last_n: Optional[int] = None) -> List[Dict[str, Any]]:
        """Returns a summary of the history log."""
        log_summary = []
        history_list = list(self.history)

        entries_to_show = history_list
        if last_n is not None and last_n > 0:
            entries_to_show = history_list[-last_n:]

        for ts, timeline, state_snap in entries_to_show:
            log_summary.append({
                "timestamp": ts,
                "timeline": timeline,
                "event": state_snap.get("meta", {}).get("history_event", "Unknown event"),
                "evolution_level": state_snap.get("evolution_level", "N/A"),
                "operational_mode": state_snap.get("operational_mode", "N/A")
            })
        return log_summary

if __name__ == '__main__':
    fs = FractalState(initial_state={"system_name": "VictorDemoFS"})
    print(f"Initial State ({fs.state['current_timeline']}): Name: {fs.get_state('system_name')}, Evo: {fs.get_state('evolution_level')}")

    fs.update_state("evolution_level", 1, "Evo cycle 1")
    fs.update_state("entropy", 0.1, "Entropy up")
    print(f"State after updates ({fs.state['current_timeline']}): Evo: {fs.get_state('evolution_level')}, Entropy: {fs.get_state('entropy')}")

    fs.create_timeline("scenario_X")
    print(f"Created timeline: 'scenario_X'")

    fs.switch_timeline("scenario_X", "Exploring X")
    fs.update_state("operational_mode", "sim_X", "Scenario X active")
    fs.update_state("param_X", 42, "Set X param")
    print(f"State on timeline '{fs.state['current_timeline']}': Mode: {fs.get_state('operational_mode')}, Param_X: {fs.get_state('param_X')}")

    fs.switch_timeline("main_timeline", "Back to main")
    print(f"State on timeline '{fs.state['current_timeline']}': Evo: {fs.get_state('evolution_level')}, Param_X: {fs.get_state('param_X')}") # param_X should be None

    fs.undo(1) # Undo "Entropy up"
    print(f"State after undo on '{fs.state['current_timeline']}': Evo: {fs.get_state('evolution_level')}, Entropy: {fs.get_state('entropy')}")

    fs.undo(1) # Undo "Evo cycle 1"
    print(f"State after second undo on '{fs.state['current_timeline']}': Evo: {fs.get_state('evolution_level')}, Name: {fs.get_state('system_name')}")

    state_file = "fractal_state_demo.pkl"
    if fs.export_state(state_file):
        print(f"State exported to {state_file}")
        fs_new_instance = FractalState()
        if fs_new_instance.import_state(state_file):
            print(f"Imported. Timeline: {fs_new_instance.get_state('current_timeline')}, Evo: {fs_new_instance.get_state('evolution_level')}, Name: {fs_new_instance.get_state('system_name')}")
            if os.path.exists(state_file): os.remove(state_file)

    print("\nFull History Log (main instance, last 10):")
    for entry in fs.get_history_log(last_n=10):
        print(f"- {time.strftime('%H:%M:%S', time.gmtime(entry['timestamp']))} [{entry['timeline']}] Evt: {entry['event'][:30]}, EvoLvl: {entry['evolution_level']}")

    print(f"\nTotal history entries: {len(fs.history)}")
    print(f"Timelines: {list(fs.timelines.keys())}")

    # Test merge
    fs.switch_timeline("scenario_X", "Re-exploring X for merge")
    fs.update_state("param_X", 99, "Updated X param before merge attempt")
    fs.switch_timeline("main_timeline", "Back to main to receive merge")
    print(f"Main timeline before merge. Param_X: {fs.get_state('param_X')}, Mode: {fs.get_state('operational_mode')}")
    fs.merge_timeline("scenario_X", strategy="overwrite_current", event_description="Merging X into main")
    print(f"Main timeline AFTER merge. Param_X: {fs.get_state('param_X')}, Mode: {fs.get_state('operational_mode')}") # Mode should be sim_X, Param_X should be 99
    print(f"Current timeline ID: {fs.get_state('current_timeline')}") # Should still be main_timeline
```
