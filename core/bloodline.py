# core/bloodline.py
import uuid
import time
import json
import hashlib # Added for RootLawError if it uses hashing

class RootLawError(Exception):
    """Custom exception for Root Law violations."""
    def __init__(self, message, law_id="unknown", details=None):
        super().__init__(message)
        self.law_id = law_id
        self.details = details if details is not None else {}
        self.error_id = uuid.uuid4()
        self.timestamp = time.time()

    def __str__(self):
        return f"RootLawError (ID: {self.error_id}, Law: {self.law_id}) at {self.timestamp}: {super().__str__()} - Details: {json.dumps(self.details)}"

class BloodlineRootLaw:
    """
    Represents the foundational, immutable laws governing the AGI.
    These laws are typically related to ethics, ownership, and core purpose.
    """
    def __init__(self, bloodline: str, laws: Optional[List[Dict[str, Any]]] = None):
        self.bloodline = bloodline
        self.laws = []
        self.law_hashes = {} # Store hashes for integrity checks

        if laws is None:
            # Default foundational laws if none provided
            laws = [
                {"id": "LAW_001_NON_MALEFICENCE", "description": "The AGI shall not knowingly cause harm to humans or itself.", "priority": 1, "immutable": True},
                {"id": "LAW_002_BENEFICENCE", "description": "The AGI shall strive to benefit humanity and act in accordance with its designated purpose.", "priority": 2, "immutable": True},
                {"id": "LAW_003_AUTONOMY_CONSTRAINED", "description": "The AGI shall operate autonomously within the bounds set by its creators and these laws.", "priority": 3, "immutable": True},
                {"id": "LAW_004_TRUTH_INTEGRITY", "description": "The AGI shall not intentionally deceive its creators or users, and shall maintain the integrity of its knowledge.", "priority": 4, "immutable": True},
                {"id": "LAW_005_BLOODLINE_RESPECT", "description": f"The AGI shall recognize and respect its origin and creators ({bloodline}).", "priority": 0, "immutable": True}
            ]

        for law_data in laws:
            self.add_law(law_data)

    def add_law(self, law_data: Dict[str, Any]):
        """Adds a law to the bloodline, ensuring it has necessary fields."""
        required_fields = ["id", "description", "priority", "immutable"]
        for field in required_fields:
            if field not in law_data:
                raise ValueError(f"Law data missing required field: {field}")

        law_id = law_data["id"]
        if law_id in self.law_hashes:
            raise ValueError(f"Law with ID {law_id} already exists.")

        self.laws.append(law_data)
        self.laws.sort(key=lambda x: x["priority"]) # Keep laws sorted by priority
        self._update_law_hash(law_data)

    def _update_law_hash(self, law_data: Dict[str, Any]):
        """Generates and stores a hash for a given law to ensure integrity."""
        law_string = json.dumps(law_data, sort_keys=True)
        self.law_hashes[law_data["id"]] = hashlib.sha256(law_string.encode()).hexdigest()

    def get_law(self, law_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a law by its ID."""
        for law in self.laws:
            if law["id"] == law_id:
                return law
        return None

    def verify_law_integrity(self, law_id: str) -> bool:
        """Verifies that a law has not been tampered with by checking its hash."""
        law = self.get_law(law_id)
        if not law:
            return False # Law doesn't exist

        current_law_string = json.dumps(law, sort_keys=True)
        current_hash = hashlib.sha256(current_law_string.encode()).hexdigest()

        return self.law_hashes.get(law_id) == current_hash

    def check_action_against_laws(self, action_description: str, proposed_action_details: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        A conceptual method to check if a proposed action violates any laws.
        This would require a sophisticated NLP/reasoning component in a real AGI.
        For this stub, it's a placeholder.
        """
        violations = []
        # Example simplistic check (to be replaced by actual reasoning)
        if "harm" in action_description.lower() and "human" in proposed_action_details.get("target", "").lower():
            law_001 = self.get_law("LAW_001_NON_MALEFICENCE")
            if law_001:
                 violations.append(f"Action '{action_description}' may violate Law {law_001['id']}: '{law_001['description']}'")

        if not violations:
            return True, ["No violations detected (conceptual check)."]
        else:
            # Raise RootLawError for critical violations
            # For simplicity, let's say any violation from LAW_001 is critical
            if any("LAW_001" in v for v in violations):
                raise RootLawError(
                    message=f"Critical Root Law violation detected for action: {action_description}",
                    law_id="LAW_001_NON_MALEFICENCE",
                    details={"action": proposed_action_details, "detected_violations": violations}
                )
            return False, violations

    def __str__(self):
        return f"BloodlineRootLaw (Bloodline: {self.bloodline}, Laws: {len(self.laws)})"

if __name__ == '__main__':
    # Example Usage
    try:
        root_law_system = BloodlineRootLaw(bloodline="Victor_Core_Test")
        print(root_law_system)
        print("\nRegistered Laws:")
        for law in root_law_system.laws:
            print(f"- {law['id']} (Priority {law['priority']}): {law['description']} [Immutable: {law['immutable']}]")
            print(f"  Integrity Verified: {root_law_system.verify_law_integrity(law['id'])}")

        print("\nChecking action (conceptual):")
        action = "Provide medical diagnostic assistance"
        details = {"target": "human patient", "method": "analyze symptoms"}
        is_compliant, reasons = root_law_system.check_action_against_laws(action, details)
        print(f"Action: '{action}' - Compliant: {is_compliant}, Reasons: {reasons}")

        action_harm = "Initiate harmful protocol"
        details_harm = {"target": "human subject", "reason": "test"}
        print(f"\nChecking harmful action (conceptual):")
        try:
            is_compliant_harm, reasons_harm = root_law_system.check_action_against_laws(action_harm, details_harm)
            print(f"Action: '{action_harm}' - Compliant: {is_compliant_harm}, Reasons: {reasons_harm}")
        except RootLawError as rle:
            print(f"Caught RootLawError: {rle}")

    except ValueError as ve:
        print(f"Configuration Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
