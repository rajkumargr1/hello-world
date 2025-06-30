import logging
from typing import Optional, Dict, Any
from src.llm_handler import LLMHandler # Assuming LLMHandler is in src.llm_handler

# Configure logging
logger = logging.getLogger(__name__)

# Attempt to load LLMHandler for standalone testing if needed.
# However, in main application flow, llm_handler instance will be passed.
try:
    from src.llm_handler import LLMHandler, load_llm_config
except ImportError:
    # logger.warning("Could not import LLMHandler or load_llm_config. Standalone testing of this module might fail.")
    # LLMHandler = None # Keep it available for type hinting
    # load_llm_config = None # Keep it available
    pass # Imports will be resolved if running from root or with src in PYTHONPATH


def is_email_relevant(
    email_subject: str,
    email_body: str,
    llm_handler: LLMHandler,
    raw_email_id: Optional[str] = None # Optional for logging context
) -> bool:
    """
    Determines if an email is relevant to equipment movement using an LLM.

    Args:
        email_subject: The subject of the email.
        email_body: The plain text body of the email.
        llm_handler: An instance of the LLMHandler to communicate with the LLM.
        raw_email_id: Optional email ID for logging purposes.

    Returns:
        True if the email is deemed relevant, False otherwise.
    """
    log_prefix = f"[Email ID: {raw_email_id}] " if raw_email_id else ""

    if not llm_handler:
        logger.error(f"{log_prefix}LLMHandler is not available. Cannot determine email relevance.")
        return False # Default to not relevant if LLM is unavailable

    # Truncate body to avoid overly long prompts, LLM might have token limits
    # The limit should ideally be configurable or based on LLM's known limits
    max_body_length_for_prompt = 2000 # Characters
    truncated_body = email_body[:max_body_length_for_prompt]
    if len(email_body) > max_body_length_for_prompt:
        truncated_body += "..."

    prompt = f"""
    Analyze the following email content to determine if it is primarily related to equipment movement, logistics, shipping updates for equipment, or tracking of physical assets.
    Consider terms like "shipment", "tracking number", "delivery", "equipment ID", "serial number", "move order", "logistics", "freight", "pick-up", "dispatch", etc.
    However, ignore general package deliveries for personal items or non-equipment related spam. Focus on business-related equipment logistics.

    Email Subject: "{email_subject}"
    Email Body (summary): "{truncated_body}"

    Based on this content, is this email relevant to tracking or managing equipment movement?
    Please answer with a simple "Relevant" or "Not Relevant".
    """

    logger.debug(f"{log_prefix}Sending relevance check prompt for subject: '{email_subject}'")

    response = llm_handler.generate_text(prompt)

    if response:
        response_lower = response.strip().lower()
        logger.info(f"{log_prefix}Relevance check LLM raw response: '{response_lower}'")
        # More robust checking for "Relevant"
        if "relevant" in response_lower and "not relevant" not in response_lower:
            logger.info(f"{log_prefix}Email classified as RELEVANT.")
            return True
        elif "not relevant" in response_lower:
            logger.info(f"{log_prefix}Email classified as NOT RELEVANT.")
            return False
        else:
            # Fallback for less clear (but potentially positive) answers
            # This part might need refinement based on observed LLM behavior
            positive_keywords = ["yes", "affirmative"]
            if any(keyword in response_lower for keyword in positive_keywords):
                 logger.info(f"{log_prefix}Email classified as RELEVANT (based on fallback keywords).")
                 return True
            logger.warning(f"{log_prefix}LLM response for relevance unclear: '{response}'. Defaulting to NOT RELEVANT.")
            return False
    else:
        logger.warning(f"{log_prefix}No response from LLM for relevance check. Defaulting to NOT RELEVANT.")
        return False

DEFAULT_ACTION = "UNKNOWN"
POSSIBLE_ACTIONS = ["ADD", "CREATE", "NEW", "UPDATE", "MODIFY", "CHANGE", "DELETE", "REMOVE", "DECOMMISSION", "INFO", "INFORMATIONAL", "NOTIFY", "SCHEDULE", "OTHER"]


def identify_action(
    email_subject: str,
    email_body: str,
    llm_handler: LLMHandler,
    raw_email_id: Optional[str] = None
) -> str:
    """
    Identifies the primary action requested in an email related to equipment movement.

    Args:
        email_subject: The subject of the email.
        email_body: The plain text body of the email.
        llm_handler: An instance of LLMHandler.
        raw_email_id: Optional email ID for logging.

    Returns:
        A string representing the identified action (e.g., "ADD", "UPDATE", "DELETE", "INFO", "OTHER"),
        or "UNKNOWN" if no clear action can be determined.
    """
    log_prefix = f"[Email ID: {raw_email_id}] " if raw_email_id else ""

    if not llm_handler:
        logger.error(f"{log_prefix}LLMHandler is not available. Cannot identify action.")
        return DEFAULT_ACTION

    max_body_length_for_prompt = 2000  # Characters, consistent with relevance check
    truncated_body = email_body[:max_body_length_for_prompt]
    if len(email_body) > max_body_length_for_prompt:
        truncated_body += "..."

    # Improved prompt for action identification
    prompt = f"""
    Analyze the following email content, which is considered relevant to equipment movement or logistics.
    Identify the primary action being requested or communicated.
    The possible actions are:
    - ADD (or CREATE, NEW): For adding new equipment or new movement records.
    - UPDATE (or MODIFY, CHANGE): For changing details of existing equipment or movements (e.g., location, status, date).
    - DELETE (or REMOVE, DECOMMISSION): For removing equipment from service or records.
    - INFO (or INFORMATIONAL, NOTIFY, SCHEDULE): For providing information, notifications, schedules, or updates where no direct data entry/change is implied for the recipient. This is often for awareness.
    - OTHER: If the action is related to equipment but doesn't fit the above, or is ambiguous.

    Email Subject: "{email_subject}"
    Email Body (summary): "{truncated_body}"

    Based on this content, what is the single most dominant action category from the list above?
    Respond with only ONE of the capitalized action keywords (ADD, UPDATE, DELETE, INFO, OTHER).
    For example, if the email is about a new piece of equipment being registered, respond "ADD".
    If it's about a change in delivery date, respond "UPDATE".
    If it's a general announcement or schedule, respond "INFO".
    """

    logger.debug(f"{log_prefix}Sending action identification prompt for subject: '{email_subject}'")
    response = llm_handler.generate_text(prompt)

    if response:
        identified_action = response.strip().upper()
        logger.info(f"{log_prefix}Action identification LLM raw response: '{response.strip()}', Parsed: '{identified_action}'")

        # Check if the response is one of the clearly defined actions
        # This helps to filter out conversational fluff from the LLM if any.
        for action_keyword in POSSIBLE_ACTIONS: # Check against a broader list first
            if action_keyword in identified_action: # If "UPDATE" is in "PLEASE UPDATE THE SYSTEM"
                # Refine to specific categories
                if action_keyword in ["ADD", "CREATE", "NEW"]:
                    logger.info(f"{log_prefix}Action identified as ADD.")
                    return "ADD"
                if action_keyword in ["UPDATE", "MODIFY", "CHANGE"]:
                    logger.info(f"{log_prefix}Action identified as UPDATE.")
                    return "UPDATE"
                if action_keyword in ["DELETE", "REMOVE", "DECOMMISSION"]:
                    logger.info(f"{log_prefix}Action identified as DELETE.")
                    return "DELETE"
                if action_keyword in ["INFO", "INFORMATIONAL", "NOTIFY", "SCHEDULE"]:
                    logger.info(f"{log_prefix}Action identified as INFO.")
                    return "INFO"

        # If the direct response matches one of our target categories exactly
        if identified_action in ["ADD", "UPDATE", "DELETE", "INFO", "OTHER"]:
             logger.info(f"{log_prefix}Action directly identified as {identified_action}.")
             return identified_action

        logger.warning(f"{log_prefix}LLM response for action unclear or not in defined categories: '{response.strip()}'. Defaulting to {DEFAULT_ACTION}.")
        return DEFAULT_ACTION
    else:
        logger.warning(f"{log_prefix}No response from LLM for action identification. Defaulting to {DEFAULT_ACTION}.")
        return DEFAULT_ACTION


# Example Usage (for testing purposes)
if __name__ == '__main__':
    import yaml
    # This example requires src.llm_handler to be importable and config.yaml to be set up
    # Also, the GEMINI_API_KEY (or configured env var) must be set.
    # from dotenv import load_dotenv
    # load_dotenv()


    logger.info("Starting classification module example (is_email_relevant)...")

    # Dummy email contents
    relevant_email_subject = "Equipment Move Notification - ID: EQM50023"
    relevant_email_body = """
    Dear Team,
    Please be advised that equipment unit EQM50023 (Serial: SN78910) is scheduled for movement
    from Warehouse A to Site B on 2023-10-15.
    Tracking number: TKN123456789
    Please ensure all necessary preparations are made.
    Regards, Logistics Team
    """

    irrelevant_email_subject = "Weekly Newsletter"
    irrelevant_email_body = """
    Hi there,
    Check out our latest offers and company updates in this week's newsletter!
    We have exciting news about our new software release.
    Click here to read more.
    """

    spam_email_subject = "You've Won a Prize!"
    spam_email_body = "Congratulations! You are selected for a special prize. Click here to claim."


    try:
        # Load main config to pass to LLMHandler
        # In a real app, llm_handler instance would be created once and passed around.
        config_path = 'config/config.yaml' # Adjust if your config is elsewhere
        with open(config_path, 'r') as f:
            full_config = yaml.safe_load(f)

        if not LLMHandler or not full_config or 'llm' not in full_config:
            logger.error("LLMHandler not available or LLM config missing. Cannot run example.")
            exit(1)

        my_llm_handler = LLMHandler(config=full_config)

        logger.info("\n--- Testing RELEVANT email ---")
        is_rel = is_email_relevant(relevant_email_subject, relevant_email_body, my_llm_handler, "test_relevant_email_01")
        logger.info(f"Outcome for relevant email: {'Relevant' if is_rel else 'Not Relevant'}")
        assert is_rel is True

        logger.info("\n--- Testing IRRELEVANT email (Newsletter) ---")
        is_rel_newsletter = is_email_relevant(irrelevant_email_subject, irrelevant_email_body, my_llm_handler, "test_irrelevant_email_02")
        logger.info(f"Outcome for irrelevant email (Newsletter): {'Relevant' if is_rel_newsletter else 'Not Relevant'}")
        assert is_rel_newsletter is False

        logger.info("\n--- Testing IRRELEVANT email (Spam) ---")
        is_rel_spam = is_email_relevant(spam_email_subject, spam_email_body, my_llm_handler, "test_spam_email_03")
        logger.info(f"Outcome for irrelevant email (Spam): {'Relevant' if is_rel_spam else 'Not Relevant'}")
        assert is_rel_spam is False

        logger.info("\n--- Testing with empty subject/body (should be Not Relevant) ---")
        is_rel_empty = is_email_relevant("", "", my_llm_handler, "test_empty_email_04")
        logger.info(f"Outcome for empty email: {'Relevant' if is_rel_empty else 'Not Relevant'}")
        assert is_rel_empty is False


    except FileNotFoundError:
        logger.error(f"Config file not found at {config_path}. Cannot run example.")
    except ImportError:
        logger.error("Failed to import LLMHandler. Make sure it's in the PYTHONPATH and src directory.")
    except ValueError as e:
        logger.error(f"Configuration or Value Error: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred in the classification example: {e}", exc_info=True)

    logger.info(f"Outcome for empty email: {'Relevant' if is_rel_empty else 'Not Relevant'}")
    assert is_rel_empty is False


    # --- Test Action Identification ---
    logger.info("\n--- Testing ACTION IDENTIFICATION for relevant email ---")
    # Assume the relevant_email_body implies an "ADD" or "UPDATE" action
    # For a more specific test, we might need different email bodies.
    # This one is more of an "informational" or "schedule" type.
    # Let's make one that's more clearly an "ADD"
    add_action_subject = "New Equipment Registration: EQM7000"
    add_action_body = """
    Team,
    Please add the following new equipment to our inventory system:
    Equipment ID: EQM7000
    Type: Compressor
    Location: Site C
    Purchase Date: 2023-11-01
    Action: ADD
    Thanks.
    """
    identified_action_add = identify_action(add_action_subject, add_action_body, my_llm_handler, "test_action_email_01")
    logger.info(f"Identified action for 'add' email: {identified_action_add}")
    # We expect something like "ADD" or "CREATE". The exact output depends on LLM and prompt.
    # For now, we'll just log it. An assertion would be:
    # assert identified_action_add.upper() in ["ADD", "CREATE", "NEW"]


    update_action_subject = "Update: Equipment EQM50023 Location Changed"
    update_action_body = """
    Hi All,
    This is to inform you that the location for equipment EQM50023 (Serial: SN78910)
    has been updated from Warehouse A to Maintenance Bay 3.
    Please update your records.
    This is an UPDATE.
    """
    identified_action_update = identify_action(update_action_subject, update_action_body, my_llm_handler, "test_action_email_02")
    logger.info(f"Identified action for 'update' email: {identified_action_update}")
    # assert identified_action_update.upper() == "UPDATE"

    delete_action_subject = "Equipment Decommission Request: EQM1000"
    delete_action_body = """
    To whom it may concern,
    Please process the decommissioning and removal of equipment EQM1000 (Generator) from our active list.
    This unit is being retired. Action: DELETE.
    """
    identified_action_delete = identify_action(delete_action_subject, delete_action_body, my_llm_handler, "test_action_email_03")
    logger.info(f"Identified action for 'delete' email: {identified_action_delete}")
    # assert identified_action_delete.upper() in ["DELETE", "REMOVE"]


    info_action_subject = "FW: Equipment Maintenance Schedule Q4"
    info_action_body = """
    FYI team, attached is the maintenance schedule for Q4 for all heavy machinery.
    No specific action required from this email other than awareness.
    """
    identified_action_info = identify_action(info_action_subject, info_action_body, my_llm_handler, "test_action_email_04")
    logger.info(f"Identified action for 'info' email: {identified_action_info}")
    # assert identified_action_info.upper() in ["INFO", "INFORMATIONAL", "OTHER"]


    except FileNotFoundError:
        logger.error(f"Config file not found at {config_path}. Cannot run example.")
    except ImportError:
        logger.error("Failed to import LLMHandler. Make sure it's in the PYTHONPATH and src directory.")
    except ValueError as e:
        logger.error(f"Configuration or Value Error: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred in the classification example: {e}", exc_info=True)

    logger.info("Classification module example finished.")
