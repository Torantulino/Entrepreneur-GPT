from colorama import Fore
from autogpt.config.ai_config import AIConfig
from autogpt.config.config import Config
from autogpt.llm import ApiManager
from autogpt.logs import logger
from autogpt.prompts.generator import PromptGenerator
from autogpt.setup import prompt_user
from autogpt.utils import clean_input

CFG = Config()

DEFAULT_TRIGGERING_PROMPT = (
    "Find the best command to use, using the format specified above:"
)


def build_default_prompt_generator() -> PromptGenerator:
    """
    This function generates a prompt string that includes various constraints,
        commands, resources, and performance evaluations.

    Returns:
        str: The generated prompt string.
    """

    # Initialize the PromptGenerator object
    prompt_generator = PromptGenerator()

    # Add constraints to the PromptGenerator object
    prompt_generator.add_constraint(
        "Use only information you know to be true. "
        "Always verify facts"
    )
    prompt_generator.add_constraint(
        "~175 sentence limit for short term memory. "
        "Save important information to files. "
    )
    prompt_generator.add_constraint(
        "Prone to forgetfulness; think about similar events to remember. "
    )
    prompt_generator.add_constraint(
        "User is unaware of you, can't help you. "
    )
    prompt_generator.add_constraint(
        "Only use commands listed in the 'Commands' section. "
    )
    prompt_generator.add_constraint(
        "One command, one cycle. "
    )
    prompt_generator.add_constraint(
        "No native access to system devices"
    )

    # Define the command list
    commands = [
        ("Task Complete (Shutdown)", "task_complete", {"reason": "<note:str>"}),
    ]

    # Add commands to the PromptGenerator object
    for command_label, command_name, args in commands:
        prompt_generator.add_command(command_label, command_name, args)

    # Add resources to the PromptGenerator object
    prompt_generator.add_resource(
        "Internet access for fact-finding. "
    )
    prompt_generator.add_resource(
        "Files for saving long-term memories. "
    )
    prompt_generator.add_resource(
        "GPT-3.5 powered Agents to answer questions. "
    )
    prompt_generator.add_resource("File output. ")

    # Add performance evaluations to the PromptGenerator object
    prompt_generator.add_performance_evaluation(
        "Constantly review/analyze your actions to ensure efficiency. "
    )
    prompt_generator.add_performance_evaluation(
        "Constantly critique your big-picture behavior. "
    )
    prompt_generator.add_performance_evaluation(
        "Reflect on past decisions and adapt. "
    )
    prompt_generator.add_performance_evaluation(
        "Be smart and efficient. Complete tasks in the fewest steps. "
    )
    prompt_generator.add_performance_evaluation("Write all code to files. ")
    return prompt_generator


def construct_main_ai_config() -> AIConfig:
    """Construct the prompt for the AI to respond to

    Returns:
        str: The prompt string
    """
    config = AIConfig.load(CFG.ai_settings_file)
    if CFG.skip_reprompt and config.ai_name:
        logger.typewriter_log("Name :", Fore.GREEN, config.ai_name)
        logger.typewriter_log("Role :", Fore.GREEN, config.ai_role)
        logger.typewriter_log("Goals:", Fore.GREEN, f"{config.ai_goals}")
        logger.typewriter_log(
            "API Budget:",
            Fore.GREEN,
            "infinite" if config.api_budget <= 0 else f"${config.api_budget}",
        )
    elif config.ai_name:
        logger.typewriter_log(
            "Welcome back! ",
            Fore.GREEN,
            f"Would you like me to return to being {config.ai_name}?",
            speak_text=True,
        )
        should_continue = clean_input(
            f"""Continue with the last settings?
Name:  {config.ai_name}
Role:  {config.ai_role}
Goals: {config.ai_goals}
API Budget: {"infinite" if config.api_budget <= 0 else f"${config.api_budget}"}
Continue ({CFG.authorise_key}/{CFG.exit_key}): """
        )
        if should_continue.lower() == CFG.exit_key:
            config = AIConfig()

    if not config.ai_name:
        config = prompt_user()
        config.save(CFG.ai_settings_file)

    # set the total api budget
    api_manager = ApiManager()
    api_manager.set_total_budget(config.api_budget)

    # Agent Created, print message
    logger.typewriter_log(
        config.ai_name,
        Fore.LIGHTBLUE_EX,
        "has been created with the following details:",
        speak_text=True,
    )

    # Print the ai config details
    # Name
    logger.typewriter_log("Name:", Fore.GREEN, config.ai_name, speak_text=False)
    # Role
    logger.typewriter_log("Role:", Fore.GREEN, config.ai_role, speak_text=False)
    # Goals
    logger.typewriter_log("Goals:", Fore.GREEN, "", speak_text=False)
    for goal in config.ai_goals:
        logger.typewriter_log("-", Fore.GREEN, goal, speak_text=False)

    return config
