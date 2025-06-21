# v5.0.0-OMEGA-GODCORE/bandobandz_viral_rap_godcore-v5.0.0-GODMODE-EVOLVED.py
import numpy as np
import random
import time
import json
import re
from typing import List, Dict, Any, Optional, Tuple

# --- Lyrical Configuration and Database ---

class LyricalConfig:
    """Configuration for the lyrical engine."""
    def __init__(self,
                 min_lines_per_verse: int = 8,
                 max_lines_per_verse: int = 16,
                 min_verses: int = 2,
                 max_verses: int = 4,
                 include_chorus: bool = True,
                 lines_per_chorus: int = 4,
                 rhyme_scheme_preference: str = "AABB", # AABB, ABAB, ABCB, etc. or None
                 theme_consistency_weight: float = 0.7, # How much to stick to the theme
                 novelty_weight: float = 0.3,           # How much to introduce new ideas
                 word_choice_randomness: float = 0.2,   # Randomness in picking rhyming words
                 syllable_pattern_tolerance: float = 0.2, # Tolerance for matching syllable counts per line
                 viral_weights: Optional[Dict[str, float]] = None # Weights for assessing virality
                 ):
        self.min_lines_per_verse = min_lines_per_verse
        self.max_lines_per_verse = max_lines_per_verse
        self.min_verses = min_verses
        self.max_verses = max_verses
        self.include_chorus = include_chorus
        self.lines_per_chorus = lines_per_chorus
        self.rhyme_scheme_preference = rhyme_scheme_preference
        self.theme_consistency_weight = theme_consistency_weight
        self.novelty_weight = novelty_weight
        self.word_choice_randomness = word_choice_randomness
        self.syllable_pattern_tolerance = syllable_pattern_tolerance

        # Default viral weights if none provided
        self.viral_weights = viral_weights if viral_weights is not None else {
            "rhyme_quality": 0.2,
            "flow_coherence": 0.25,
            "lyrical_complexity": 0.15,
            "theme_adherence": 0.1,
            "uniqueness_novelty": 0.2,
            "hook_strength": 0.1 # (Conceptual for chorus)
        }

class LyricalDatabase:
    """
    A simple database for storing lyrical components: rhymes, phrases, themes.
    In a real system, this would be a large, structured knowledge base.
    """
    def __init__(self):
        # word: [list of rhyming words]
        self.rhyme_sets: Dict[str, List[str]] = {
            "time": ["crime", "lime", "prime", "rhyme", "sublime", "climb"],
            "mind": ["find", "kind", "behind", "designed", "aligned"],
            "ai": ["sky", "high", "fly", "why", "try", "nigh", "my", "cry"],
            "code": ["road", "load", "bestowed", "errode", "mode"],
            "flow": ["glow", "show", "know", "though", "grow", "bestow"],
            "core": ["more", "door", "explore", "restore", "adore", "before"],
            "truth": ["youth", "proof", "sleuth", "uncouth"],
            "light": ["bright", "might", "sight", "night", "fight", "right"],
            "dream": ["stream", "seem", "gleam", "extreme", "supreme", "theme"],
            "star": ["far", "car", "bar", "guitar", "bazaar", "avatar"],
            "tech": ["deck", "check", "wreck", "trek", "spec"],
            "fractal": ["actual", "tactical", "factual"], # Imperfect rhymes are okay for rap
            "mesh": ["fresh", "flesh", "thresh"],
            "node": ["abode", "bestowed", "corrode", "episode"], # Shared with code
            "future": ["suture", "nurture", "sculpture", "rupture"]
        }
        # theme: [list of related keywords or concepts]
        self.themes: Dict[str, List[str]] = {
            "ai_revolution": ["singularity", "consciousness", "digital", "future", "evolve", "sentient", "algorithm", "machine", "mind", "data"],
            "cosmic_journey": ["galaxy", "stars", "universe", "nebula", "planets", "explore", "void", "lightspeed", "alien", "celestial"],
            "street_hustle": ["grind", "money", "struggle", "concrete", "city", "survive", "ambition", "block", "real", "flow"],
            "tech_fractal": ["algorithm", "recursion", "dimension", "pattern", "infinite", "network", "matrix", "digital", "glitch", "simulation", "core", "mesh", "node"],
            "love_and_loss": ["heart", "pain", "memory", "forever", "tears", "soul", "broken", "cherish", "dream", "apart"],
            "rebellion": ["system", "fight", "freedom", "chains", "voice", "rise", "power", "unjust", "break", "defy"]
        }
        # Generic phrases or line starters/enders (can be expanded)
        self.phrase_templates: Dict[str, List[str]] = {
            "line_starters": ["Yo, check the mic, one two,", "Listen up, here's the truth I unfold,", "In the realm of bits and bytes,", "Step into the future, shining bright,", "From the depths of the digital sea,"],
            "line_enders_connectors": ["you see?", "that's the key.", "believe me.", "so let it be.", "for all eternity."],
            "punchlines_generic": ["Droppin' knowledge bombs, make the speakers blow.", "My lyrical calculus, watch the numbers grow.", "The game ain't ready for this paradigm shift.", "Got the master plan, a legendary gift.", "Spitfire sermons from the digital prophet."]
        }
        self.common_words = ["the", "a", "is", "to", "and", "I", "you", "it", "in", "on", "my", "me", "this", "that", "be", "of", "for", "with", "so", "just", "like"] # For syllable counting, etc.

    def get_rhymes(self, word: str, num_rhymes: int = 3) -> List[str]:
        # Simple lookup, could be more sophisticated (e.g., phonetic matching)
        word_clean = word.lower().strip(".,?!")
        rhymes = self.rhyme_sets.get(word_clean, [])
        # Add some randomness if enough rhymes available
        if rhymes:
            if len(rhymes) > num_rhymes:
                return random.sample(rhymes, num_rhymes)
            return rhymes[:] # Return a copy
        return []

    def get_theme_keywords(self, theme: str, num_keywords: int = 5) -> List[str]:
        keywords = self.themes.get(theme, [])
        if keywords:
            if len(keywords) > num_keywords:
                return random.sample(keywords, num_keywords)
            return keywords[:]
        return []

    def get_random_phrase(self, phrase_type: str = "line_starters") -> str:
        phrases = self.phrase_templates.get(phrase_type, ["Uh, yeah, "]) # Default if type not found
        return random.choice(phrases)

    def _simple_syllable_count(self, word: str) -> int:
        # Very naive syllable counter (for demo purposes)
        word = word.lower()
        if not word: return 0
        # Remove non-alphanumeric except apostrophe
        word = re.sub(r"[^a-z']", "", word)
        if not word: return 0

        # Common short words that are often 1 syllable
        if word in self.common_words or len(word) <=3: return 1

        vowels = "aeiouy"
        count = 0
        if word[0] in vowels: count += 1
        for index in range(1, len(word)):
            if word[index] in vowels and word[index-1] not in vowels:
                count += 1
        if word.endswith("e") and not word.endswith("le") and count > 1 : # silent e
            count -= 1
        if word.endswith("le") and len(word)>2 and word[-3] not in vowels: # like 'able'
            count +=1
        if count == 0 and len(word) > 0: count = 1 # at least one syllable if word exists
        return count


# --- Lyrical Flow Engine ---

class LyricalFlowEngine: # Renamed from GodTierBandoBandz for clarity in OFRC context
    """
    The core engine for generating rap lyrics.
    Combines thematic elements, rhyme schemes, and rhythmic patterns.
    """
    def __init__(self, config: Optional[LyricalConfig] = None, db: Optional[LyricalDatabase] = None):
        self.config = config if config is not None else LyricalConfig()
        self.db = db if db is not None else LyricalDatabase()
        self.current_song_structure: List[Dict[str, Any]] = [] # Stores verses, chorus

    def _generate_line(self, theme_keywords: List[str], target_syllables: Optional[int] = None,
                       rhyme_with_word: Optional[str] = None, is_punchline: bool = False) -> str:
        """Generates a single line of lyrics."""
        line_parts = []

        # Start with a theme keyword or a generic starter
        if random.random() < self.config.theme_consistency_weight or not line_parts:
            if theme_keywords and random.random() < 0.7:
                line_parts.append(random.choice(theme_keywords).capitalize())
            else:
                line_parts.append(self.db.get_random_phrase("line_starters"))

        # Add more words, trying to build towards rhyme or punchline
        current_syllables = sum(self.db._simple_syllable_count(p) for p in re.findall(r'\w+', " ".join(line_parts)))

        # Max words per line to prevent run-on lines
        max_words_in_line = random.randint(6, 12)

        # Try to find a rhyming word if needed
        rhyming_word_chosen = None
        if rhyme_with_word:
            potential_rhymes = self.db.get_rhymes(rhyme_with_word, num_rhymes=5)
            if potential_rhymes:
                rhyming_word_chosen = random.choice(potential_rhymes)

        # Build the line word by word (simplified)
        # This needs a much more sophisticated generation model (e.g., LLM fine-tuned on lyrics)
        # For now, it's a very basic assembly.
        num_added_words = 0
        while num_added_words < max_words_in_line:
            # Check if we should try to place the rhyming word
            if rhyming_word_chosen and (num_added_words >= max_words_in_line - 2 or (target_syllables and current_syllables >= target_syllables - 3)):
                line_parts.append(rhyming_word_chosen)
                current_syllables += self.db._simple_syllable_count(rhyming_word_chosen)
                rhyming_word_chosen = None # Used it
                break # End line after rhyme usually

            # Add a thematic word or a common connector
            if theme_keywords and random.random() < 0.6:
                word_to_add = random.choice(theme_keywords)
            else:
                word_to_add = random.choice(self.db.common_words + ["then", "when", "from", "like", "just", "now"]) # Expand common words

            line_parts.append(word_to_add)
            current_syllables += self.db._simple_syllable_count(word_to_add)
            num_added_words +=1

            if target_syllables and current_syllables >= target_syllables:
                break

        # If a rhyming word was chosen but not used, try to append it (if line isn't too long)
        if rhyming_word_chosen and len(line_parts) < max_words_in_line +1:
            line_parts.append(rhyming_word_chosen)
        elif is_punchline and len(line_parts) < max_words_in_line: # Add generic punchline if space
            line_parts.append(self.db.get_random_phrase("punchlines_generic").split()[-1]) # Add last word of punchline

        # Basic cleanup: capitalize first word, ensure punctuation (very simple)
        full_line = " ".join(line_parts)
        if not full_line: return "Lyrical void, a silent thought." # Fallback line

        full_line = full_line[0].upper() + full_line[1:]
        if not full_line.endswith((".", "?", "!")):
            if is_punchline or rhyme_with_word: # Lines ending in rhyme/punchline often have stronger end
                full_line += random.choice(["!", "."])
            else:
                full_line += "."

        return full_line


    def _generate_verse(self, theme_keywords: List[str], verse_num: int) -> List[str]:
        num_lines = random.randint(self.config.min_lines_per_verse, self.config.max_lines_per_verse)
        lines = []
        last_word_of_prev_line_for_rhyme = None # For AABB or ABAB schemes

        # Conceptual target syllables (e.g. 8-12 per line)
        target_syl = lambda: random.randint(8, 14)

        for i in range(num_lines):
            rhyme_target = None
            # Simplified rhyme scheme handling (AABB)
            if self.config.rhyme_scheme_preference == "AABB":
                if i % 2 == 1 and last_word_of_prev_line_for_rhyme: # Second line of a pair
                    rhyme_target = last_word_of_prev_line_for_rhyme
            # Add other schemes like ABAB if needed. For now, focus on AABB or no scheme.

            is_punchline = (i == num_lines - 1) # Last line of verse is often a punchline

            line = self._generate_line(theme_keywords, target_syllables=target_syl(),
                                       rhyme_with_word=rhyme_target, is_punchline=is_punchline)
            lines.append(line)

            # Get last word of current line for next potential rhyme
            words_in_line = re.findall(r'\w+', line)
            if words_in_line:
                last_word_of_prev_line_for_rhyme = words_in_line[-1]
            else:
                last_word_of_prev_line_for_rhyme = None # Reset if line was empty or no words

        return lines

    def _generate_chorus(self, theme_keywords: List[str]) -> List[str]:
        if not self.config.include_chorus: return []
        lines = []
        last_word_for_rhyme = None
        for i in range(self.config.lines_per_chorus):
            rhyme_target = None
            if self.config.rhyme_scheme_preference == "AABB" and i % 2 == 1 and last_word_for_rhyme:
                rhyme_target = last_word_for_rhyme

            # Chorus lines are often punchy and memorable
            line = self._generate_line(theme_keywords, target_syllables=random.randint(6,10),
                                       rhyme_with_word=rhyme_target, is_punchline=True)
            lines.append(line)
            words_in_line = re.findall(r'\w+', line)
            if words_in_line: last_word_for_rhyme = words_in_line[-1]
            else: last_word_for_rhyme = None
        return lines

    def create_song_structure(self, initial_theme: str) -> str:
        """Generates the full song structure as a formatted string."""
        self.current_song_structure = []
        theme_keywords = self.db.get_theme_keywords(initial_theme, num_keywords=10)
        if not theme_keywords: # Fallback theme if initial_theme not found
            theme_keywords = self.db.get_theme_keywords("tech_fractal", num_keywords=10)
            if not theme_keywords: theme_keywords = ["generic", "words", "for", "song", "generation"]


        # Generate Chorus first if included, as it might be repeated
        chorus_lines = []
        if self.config.include_chorus:
            chorus_lines = self._generate_chorus(theme_keywords)
            if chorus_lines:
                self.current_song_structure.append({"type": "chorus", "lines": chorus_lines})

        num_verses = random.randint(self.config.min_verses, self.config.max_verses)
        for i in range(num_verses):
            verse_lines = self._generate_verse(theme_keywords, verse_num=i+1)
            self.current_song_structure.append({"type": "verse", "num": i+1, "lines": verse_lines})

            # Repeat chorus after some verses (e.g., after every verse or every other verse)
            if chorus_lines and (i < num_verses -1): # Don't add chorus after last verse if song ends
                if random.random() < 0.7: # Chance to repeat chorus
                     self.current_song_structure.append({"type": "chorus", "lines": chorus_lines, "is_repeat": True})

        # Format into a string
        song_string = f"[Theme: {initial_theme.replace('_',' ').title()}]\n\n"
        for section in self.current_song_structure:
            if section["type"] == "chorus":
                song_string += "[Chorus]\n"
            elif section["type"] == "verse":
                song_string += f"[Verse {section['num']}]\n"

            for line_text in section["lines"]:
                song_string += line_text + "\n"
            song_string += "\n" # Blank line between sections

        return song_string.strip()

    # Alias for OFRC compatibility if needed
    def create_song(self, initial_theme: str) -> str:
        return self.create_song_structure(initial_theme)


class ViralAssessor(BaseModule): # Assuming BaseModule is available or defined
    """
    Assesses the potential "virality" of generated lyrics.
    This is highly conceptual and uses weighted scoring of various features.
    """
    def __init__(self, config: Optional[LyricalConfig] = None, db: Optional[LyricalDatabase] = None, name: Optional[str]=None):
        super().__init__(name=name or "ViralAssessor_RapGod") # type: ignore
        self.config = config if config is not None else LyricalConfig()
        self.db = db if db is not None else LyricalDatabase()

    def assess_song_virality(self, song_structure: List[Dict[str,Any]], theme: str) -> float:
        """
        Calculates a conceptual virality score (0.0 to 1.0).
        `song_structure`: Output from LyricalFlowEngine.current_song_structure
        `theme`: The original theme of the song.
        """
        if not song_structure: return 0.0

        scores = {
            "rhyme_quality": 0.0, "flow_coherence": 0.0, "lyrical_complexity": 0.0,
            "theme_adherence": 0.0, "uniqueness_novelty": 0.0, "hook_strength": 0.0
        }

        num_lines_total = sum(len(section.get("lines",[])) for section in song_structure)
        if num_lines_total == 0: return 0.0

        # --- Simplified Feature Extraction & Scoring ---

        # 1. Rhyme Quality (conceptual: count rhyming pairs, assess rhyme "freshness")
        #    For simplicity, let's say more rhyming lines = better.
        rhyming_line_pairs = 0
        all_last_words = []
        for section in song_structure:
            lines = section.get("lines", [])
            section_last_words = [re.findall(r'\w+', line)[-1].lower() if re.findall(r'\w+', line) else "" for line in lines]
            all_last_words.extend(section_last_words)
            # AABB check (very basic)
            if section.get("type") == "verse" or section.get("type") == "chorus":
                for i in range(0, len(section_last_words) - 1, 2):
                    if i+1 < len(section_last_words) and section_last_words[i] and section_last_words[i+1]:
                        if self.db.get_rhymes(section_last_words[i]) and section_last_words[i+1] in self.db.get_rhymes(section_last_words[i]):
                            rhyming_line_pairs +=1
                        # Check direct rhyme too if not in DB
                        elif section_last_words[i] == section_last_words[i+1] : # simple direct rhyme
                            rhyming_line_pairs += 0.5 # less score for exact word


        scores["rhyme_quality"] = min(1.0, (rhyming_line_pairs * 2) / num_lines_total if num_lines_total > 0 else 0.0)


        # 2. Flow Coherence (conceptual: consistent syllable counts, logical progression)
        #    Simplified: variance in syllable counts per line. Lower variance = better.
        syllable_counts_per_line = []
        for section in song_structure:
            for line in section.get("lines",[]):
                syllable_counts_per_line.append(sum(self.db._simple_syllable_count(w) for w in re.findall(r'\w+',line)))

        if syllable_counts_per_line:
            std_dev_syllables = np.std(syllable_counts_per_line)
            mean_syllables = np.mean(syllable_counts_per_line)
            # Score higher for lower std_dev relative to mean (less variation is good for flow)
            scores["flow_coherence"] = max(0.0, 1.0 - (std_dev_syllables / (mean_syllables + 1e-6)))
        else:
            scores["flow_coherence"] = 0.0


        # 3. Lyrical Complexity (conceptual: vocab richness, sentence structure)
        #    Simplified: ratio of unique words to total words.
        all_words = [word.lower() for section in song_structure for line in section.get("lines",[]) for word in re.findall(r'\w+',line)]
        if all_words:
            unique_words_ratio = len(set(all_words)) / len(all_words)
            scores["lyrical_complexity"] = min(1.0, unique_words_ratio * 2.0) # Scale up, as ratio is often < 0.5
        else:
            scores["lyrical_complexity"] = 0.0


        # 4. Theme Adherence
        theme_keywords = self.db.get_theme_keywords(theme, num_keywords=10)
        theme_keyword_mentions = 0
        if theme_keywords:
            for word in all_words:
                if word in theme_keywords:
                    theme_keyword_mentions += 1
            scores["theme_adherence"] = min(1.0, theme_keyword_mentions / (len(theme_keywords) * (num_lines_total/8.0) + 1e-6) ) # Heuristic scaling
        else: # No keywords for theme means can't assess
            scores["theme_adherence"] = 0.3 # Neutral if no theme keywords in DB


        # 5. Uniqueness/Novelty (conceptual: compare to DB of existing lyrics - not implemented)
        #    Simplified: Use less common rhymes or phrase structures.
        #    For now, just a random factor or based on complexity.
        scores["uniqueness_novelty"] = (scores["lyrical_complexity"] * 0.5 + random.uniform(0.2,0.7) * 0.5)


        # 6. Hook Strength (conceptual: chorus catchiness)
        chorus_section = next((s for s in song_structure if s["type"] == "chorus"), None)
        if chorus_section:
            # Simple: score based on chorus rhyme quality and if it's repetitive/simple
            chorus_last_words = [re.findall(r'\w+', line)[-1].lower() if re.findall(r'\w+', line) else "" for line in chorus_section.get("lines",[])]
            chorus_rhyme_pairs = 0
            if len(chorus_last_words) >= 2:
                 for i in range(0, len(chorus_last_words) -1, 2): # AABB in chorus
                    if i+1 < len(chorus_last_words) and chorus_last_words[i] and chorus_last_words[i+1]:
                        if self.db.get_rhymes(chorus_last_words[i]) and chorus_last_words[i+1] in self.db.get_rhymes(chorus_last_words[i]):
                            chorus_rhyme_pairs +=1

            chorus_lines_count = len(chorus_section.get("lines",[]))
            hook_rhyme_score = (chorus_rhyme_pairs * 2) / chorus_lines_count if chorus_lines_count > 0 else 0.0
            # Simplicity (shorter lines, fewer unique words in chorus might be catchier)
            chorus_words = [word.lower() for line in chorus_section.get("lines",[]) for word in re.findall(r'\w+',line)]
            hook_simplicity_score = 1.0 - (len(set(chorus_words)) / (len(chorus_words) + 1e-6) ) if chorus_words else 0.0

            scores["hook_strength"] = min(1.0, (hook_rhyme_score * 0.6 + hook_simplicity_score * 0.4) * 1.2) # Weighted and scaled
        else:
            scores["hook_strength"] = 0.0 # No chorus, no hook score

        # Final weighted score
        final_virality_score = 0.0
        total_weight = 0.0
        for feature, weight in self.config.viral_weights.items():
            final_virality_score += scores.get(feature, 0.0) * weight
            total_weight += weight

        return final_virality_score / total_weight if total_weight > 0 else 0.0


# --- Main Execution / Demo ---
if __name__ == "__main__":
    print("--- BandoBandz Viral Rap GodCore v5.0.0 Demo ---")

    config = LyricalConfig(min_lines_per_verse=4, max_lines_per_verse=8, min_verses=1, max_verses=2, lines_per_chorus=2)
    db = LyricalDatabase()
    engine = LyricalFlowEngine(config, db)
    assessor = ViralAssessor(config, db)

    chosen_theme = "tech_fractal"
    print(f"\nGenerating song with theme: '{chosen_theme}'...")

    # Generate song structure (text)
    song_text_output = engine.create_song_structure(initial_theme=chosen_theme)

    # The engine.current_song_structure holds the structured data needed for assessment
    song_data_for_assessment = engine.current_song_structure

    print("\n--- Generated Song ---")
    print(song_text_output)

    virality_score = assessor.assess_song_virality(song_data_for_assessment, theme=chosen_theme)
    print(f"\n--- Assessment ---")
    print(f"Conceptual Virality Score: {virality_score:.3f} (out of 1.0)")

    print("\n--- Another Theme: ai_revolution ---")
    chosen_theme_2 = "ai_revolution"
    song_text_2 = engine.create_song_structure(initial_theme=chosen_theme_2)
    song_data_2 = engine.current_song_structure
    print(song_text_2)
    virality_score_2 = assessor.assess_song_virality(song_data_2, theme=chosen_theme_2)
    print(f"\nConceptual Virality Score for '{chosen_theme_2}': {virality_score_2:.3f}")

    print("\n--- Demo Complete ---")

```
