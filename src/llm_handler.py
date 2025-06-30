import os
import yaml
import logging
import google.generativeai as genai
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
logger = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = 'config/config.yaml' # Should ideally be passed or centrally managed

# Helper to load config if needed independently, though typically config is passed around
def load_llm_config(config_path: str = DEFAULT_CONFIG_PATH) -> Dict[str, Any]:
    """Loads the LLM specific configuration from the main config file."""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        if not config or 'llm' not in config:
            raise ValueError("LLM configuration section ('llm') not found or config is empty.")
        return config['llm']
    except FileNotFoundError:
        logger.error(f"Configuration file not found at {config_path}")
        raise
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML configuration for LLM: {e}")
        raise
    except ValueError as e:
        logger.error(f"LLM Configuration error: {e}")
        raise

class LLMHandler:
    def __init__(self, config: Dict[str, Any]):
        """
        Initializes the LLMHandler.
        Expects a dictionary 'config' containing an 'llm' sub-dictionary with:
        - api_key_env_var: Name of the environment variable for the API key.
        - model: The model name to use (e.g., "gemini-pro").
        - (Optional) generation_config: A dictionary for generation parameters.
        - (Optional) safety_settings: A list of dictionaries for safety settings.
        """
        self.llm_config = config.get('llm', {})
        if not self.llm_config:
            raise ValueError("LLM configuration ('llm' section) is missing from the provided config.")

        self.api_key_env_var = self.llm_config.get('api_key_env_var')
        if not self.api_key_env_var:
            raise ValueError("LLM API key environment variable name ('api_key_env_var') not specified in config.")

        self.api_key = os.environ.get(self.api_key_env_var)
        if not self.api_key:
            raise ValueError(f"LLM API key not found in environment variable '{self.api_key_env_var}'.")

        self.model_name = self.llm_config.get('model', 'gemini-pro')

        # Configure the Gemini client
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(
                self.model_name,
                generation_config=self.llm_config.get('generation_config'),
                safety_settings=self.llm_config.get('safety_settings')
            )
            logger.info(f"LLMHandler initialized with model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to configure Gemini SDK or initialize model: {e}")
            raise

    def generate_text(self, prompt: str) -> Optional[str]:
        """
        Generates text using the configured LLM.

        Args:
            prompt: The prompt to send to the LLM.

        Returns:
            The text response from the LLM, or None if an error occurs.
        """
        if not self.model:
            logger.error("LLM model is not initialized.")
            return None

        logger.debug(f"Sending prompt to LLM ({self.model_name}): '{prompt[:100]}...'")
        try:
            response = self.model.generate_content(prompt)
            # Assuming the response structure for Gemini API. Adjust if different.
            # Check for empty or blocked responses
            if not response.parts:
                if response.prompt_feedback and response.prompt_feedback.block_reason:
                    logger.warning(f"Prompt was blocked by LLM. Reason: {response.prompt_feedback.block_reason_message or response.prompt_feedback.block_reason}")
                else:
                    logger.warning("LLM response is empty or does not contain parts.")
                return None

            # Concatenate text from all parts if multiple exist
            full_text_response = "".join(part.text for part in response.parts if hasattr(part, 'text'))

            if not full_text_response.strip():
                 logger.warning("LLM generated an empty text response.")
                 return None

            logger.debug(f"Received response from LLM: '{full_text_response[:100]}...'")
            return full_text_response

        except Exception as e:
            logger.error(f"Error during LLM text generation: {e}", exc_info=True)
            # Specific error handling for Gemini can be added here if needed
            # e.g., if type(e) == google.api_core.exceptions.PermissionDenied: ...
            return None

# Example Usage (for testing purposes)
if __name__ == '__main__':
    logger.info("Starting LLMHandler example...")

    # Ensure your config.yaml has the 'llm' section correctly defined
    # and the API key environment variable (e.g., LLM_API_KEY) is set.
    # Example:
    # In config/config.yaml:
    # llm:
    #   api_key_env_var: "GEMINI_API_KEY" # Or your chosen env var name
    #   model: "gemini-pro"
    #   # Optional generation_config and safety_settings for Gemini
    #   generation_config:
    #     temperature: 0.7
    #     top_p: 1.0
    #     top_k: 40
    #     max_output_tokens: 2048
    #   safety_settings:
    #     - category: HARASSMENT
    #       threshold: BLOCK_MEDIUM_AND_ABOVE
    #     - category: HATE_SPEECH
    #       threshold: BLOCK_MEDIUM_AND_ABOVE
    #     - category: SEXUALLY_EXPLICIT
    #       threshold: BLOCK_MEDIUM_AND_ABOVE
    #     - category: DANGEROUS_CONTENT
    #       threshold: BLOCK_MEDIUM_AND_ABOVE


    # Create a .env file like this for testing:
    # GEMINI_API_KEY=your_actual_gemini_api_key
    # from dotenv import load_dotenv
    # load_dotenv() # Call this if you use a .env file

    try:
        # This assumes config/config.yaml exists and is correctly populated
        # For this standalone test, we directly load the main config.
        # In the main application, the config dict would be passed from the orchestrator.
        with open(DEFAULT_CONFIG_PATH, 'r') as f:
            full_config = yaml.safe_load(f)

        if not full_config or 'llm' not in full_config:
            logger.error(f"LLM configuration section not found in {DEFAULT_CONFIG_PATH}")
            exit(1)

        llm_handler = LLMHandler(config=full_config) # Pass the whole config dict

        test_prompt = "Explain what an equipment movement in logistics is in one sentence."
        logger.info(f"Sending test prompt: \"{test_prompt}\"")

        response_text = llm_handler.generate_text(test_prompt)

        if response_text:
            logger.info(f"LLM Response:\n{response_text}")
        else:
            logger.warning("LLM did not return a response or an error occurred.")

        test_prompt_2 = "Is the following email about equipment movement? Subject: Urgent Delivery Update, Body: Your package an HXT455 is arriving tomorrow."
        logger.info(f"Sending test prompt 2: \"{test_prompt_2}\"")
        response_text_2 = llm_handler.generate_text(test_prompt_2)
        if response_text_2:
            logger.info(f"LLM Response 2:\n{response_text_2}")
        else:
            logger.warning("LLM did not return a response for prompt 2 or an error occurred.")


    except ValueError as e:
        logger.error(f"Initialization or Configuration Error: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred in the LLMHandler example: {e}", exc_info=True)

    logger.info("LLMHandler example finished.")
