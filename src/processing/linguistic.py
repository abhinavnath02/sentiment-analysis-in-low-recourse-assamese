import regex

class LinguisticValidator:
    """
    Validates if text contains Assamese content and filters out other scripts.
    Uses Unicode blocks used by Assamese (Bengali script block).
    """
    
    # Bengali/Assamese Unicode Block: U+0980 to U+09FF
    ASSAMESE_BLOCK_PATTERN = regex.compile(r'[\u0980-\u09FF]')
    
    # Distinctive Characters
    CH_ASSAMESE_RA = '\u09F0' # ৰ
    CH_ASSAMESE_WA = '\u09F1' # ৱ
    
    CH_BENGALI_RA = '\u09B0'  # র
    
    @staticmethod
    def get_script_stats(text: str) -> dict:
        """
        Analyzes the text for script composition.
        """
        total_chars = len(text)
        if total_chars == 0:
            return {"indic_ratio": 0.0, "has_assamese_unique": False, "has_bengali_unique": False}
            
        # Count Indic characters (Block U+0980 - U+09FF)
        indic_chars = len(LinguisticValidator.ASSAMESE_BLOCK_PATTERN.findall(text))
        indic_ratio = indic_chars / total_chars
        
        has_assamese_unique = (LinguisticValidator.CH_ASSAMESE_RA in text) or \
                              (LinguisticValidator.CH_ASSAMESE_WA in text)
                              
        has_bengali_unique = (LinguisticValidator.CH_BENGALI_RA in text)
        
        return {
            "indic_ratio": indic_ratio,
            "has_assamese_unique": has_assamese_unique,
            "has_bengali_unique": has_bengali_unique
        }

    @staticmethod
    def is_assamese_script(text: str, threshold: float = 0.5) -> bool:
        """
        Checks if the text contains a significant portion of Assamese/Bengali script characters
        AND does not contain explicit Bengali-only characters.
        
        Args:
            text (str): Input string.
            threshold (float): Ratio of Assamese characters required to pass.
            
        Returns:
            bool: True if passes the threshold and is not Bengali.
        """
        if not text:
            return False
            
        stats = LinguisticValidator.get_script_stats(text)
        
        # Criterion 1: Must be largely Indic script
        if stats["indic_ratio"] < threshold:
            return False
            
        # Criterion 2: Must NOT have Bengali-specific 'Ra' (រ)
        if stats["has_bengali_unique"]:
            return False
            
        # Criterion 3: Ideally has Assamese traits, but for short texts we might be lenient 
        # as long as negative constraints (Bit 2) are not met.
        # However, to be strict for a dataset, we might prefer enforcing Assamese traits 
        # if the text is long enough. For now, we allow ambiguous texts (like "ধন্যবাদ")
        # because they are valid Assamese words too, provided no Bengali logic is found.
        
        return True
