# Powering Up Quickstart Universe: Integrating Live Gemini API Calls for Content Extraction

The Quickstart Universe (QSU) project aims to simplify the process of understanding and setting up new tools and technologies by extracting key information from their quickstart guides. Initially, QSU relied on mock extractors. This post details the journey of integrating a real AI model, Google's Gemini, to perform live content extraction.

## The Starting Point: Mock Extractors and a Vision

Our first step was to lay down the groundwork. We defined an abstract `ContentExtractor` class and several placeholder implementations for popular AI models. This allowed us to build the application flow while deferring the complexity of actual AI integration.

The core idea was an abstract base class:
```python
# app/services/content_extractor.py (Conceptual)
from abc import ABC, abstractmethod
# ... other necessary imports like HttpUrl, ExtractedContent ...

class ContentExtractor(ABC):
    @abstractmethod
    async def extract(self, html_content: str, url: HttpUrl) -> ExtractedContent:
        pass
```

And placeholder implementations like `GeminiExtractor` initially looked like this:
```python
# app/services/content_extractor.py (Initial GeminiExtractor)
class GeminiExtractor(ContentExtractor):
    # Constructor might not have an api_key initially
    def __init__(self): 
        pass

    async def extract(self, html_content: str, url: HttpUrl) -> ExtractedContent:
        # Initial mock logic...
        logger.info(f"GeminiExtractor (Mock) processing URL: {url}")
        return ExtractedContent(
            source_url=url,
            tool_name="Gemini Extracted Tool (Placeholder)",
            extraction_metadata={"source": "GeminiExtractor - Placeholder"}
        )
# ... Other placeholder extractors like GptExtractor, LlamaExtractor followed a similar pattern ...
```
This setup enabled us to develop the UI and backend logic without needing immediate access to live AI models.

## Phase 1: Bringing Gemini to Life - API Key Handling

To use the Gemini API, secure handling of API keys was paramount.

1.  **Configuration**: We decided to use environment variables for API keys, a common and secure practice. The `GeminiExtractor` (and eventually all extractors for consistency) was updated to accept an API key during initialization.

    ```python
    # app/services/content_extractor.py (GeminiExtractor __init__)
    class GeminiExtractor(ContentExtractor):
        def __init__(self, api_key: Optional[str] = None):
            self._api_key = api_key
            # ...
    ```

2.  **Application Logic**: `app/main.py` now reads the `GEMINI_API_KEY` from the environment and passes it to the extractor:

    ```python
    # app/main.py (Snippet)
    import os
    import logging # Assuming logger is configured
    from .services.content_extractor import GeminiExtractor 

    logger = logging.getLogger(__name__)
    # ...
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if gemini_api_key:
        logger.info("Gemini API key found. GeminiExtractor will attempt to use it.")
    else:
        logger.warning("GEMINI_API_KEY environment variable not set. GeminiExtractor will run in mock/placeholder mode.")
    
    extractor = GeminiExtractor(api_key=gemini_api_key)
    ```
    If the key isn't found, the `GeminiExtractor`'s internal logic ensures it gracefully falls back to its mock behavior, preventing crashes and allowing development without a live key.

## Phase 2: Making the Call - Interacting with the Gemini SDK

With API key handling in place, we moved to the core task: calling the Gemini API.

1.  **Dependency**: The `google-generativeai` SDK was added to `pyproject.toml`:
    ```toml
    # pyproject.toml (Snippet)
    [project]
    dependencies = [
        # ... other dependencies ...
        "google-generativeai~=0.5.0" 
    ]
    ```
    This ensures the necessary library is available in our project environment.

2.  **SDK Initialization & API Call**: The `extract` method in `GeminiExtractor` was significantly enhanced to use the SDK:

    ```python
    # app/services/content_extractor.py (GeminiExtractor.extract snippet)
    import google.generativeai as genai
    # ... (logger, ExtractedContent, etc.)

    # Inside the extract method, if self._api_key is present:
    try:
        genai.configure(api_key=self._api_key)
        model = genai.GenerativeModel('gemini-pro') # Or your preferred model
    except Exception as e:
        logger.error(f"Failed to initialize Gemini SDK: {e}", exc_info=True)
        # Return error ExtractedContent
        return ExtractedContent(source_url=url, extraction_metadata={"error": "SDK Init Failed", ...})
    
    # ... (Prompt construction, see next section) ...
    prompt = "Your carefully crafted prompt here..." # Placeholder for actual prompt generation

    try:
        response = model.generate_content(prompt)
        # Process response.text, handle potential blocks/errors
        if response.parts:
            ai_response_text = response.text 
        else:
            # Handle cases where content might be blocked or empty
            logger.warning(f"Gemini API call did not return content. Feedback: {response.prompt_feedback}")
            ai_response_text = None 
            # Return ExtractedContent with appropriate metadata
    except Exception as e:
        logger.error(f"Gemini API call failed: {e}", exc_info=True)
        # Return error ExtractedContent
        return ExtractedContent(source_url=url, extraction_metadata={"error": "API Call Failed", ...})
    ```
    This snippet illustrates the core interaction: configure the SDK, initialize the model, and generate content.

3.  **Response Parsing & Error Handling**: The AI's response is expected to be JSON. We implemented robust parsing and error handling for various scenarios:
    *   If the API call itself fails (network issues, server errors).
    *   If the response is blocked by safety filters (the Gemini API provides reasons for this, which we now log).
    *   If the response isn't valid JSON.
    *   In each case, we log the issue and populate `ExtractedContent` with appropriate error metadata, ensuring the application remains resilient and provides feedback on failures.

## Engineering the Prompt: Guidance for the AI

A crucial part of working with LLMs is prompt engineering. Our initial prompt, which guides the AI on what to extract and how to format it, was hardcoded in the `GeminiExtractor`. For better maintainability and easier iteration, we externalized it.

1.  **Prompt File**: The prompt now resides in `app/services/prompts/gemini_extract_prompt.txt`. It uses placeholders like `{url}` and `{html_snippet}` for dynamic content.
    ```text
    # app/services/prompts/gemini_extract_prompt.txt (Snippet)
    Analyze the following HTML content from {url} and extract quickstart information.
    Focus on:
    - Tool name and version
    - Key dependencies (name, version, type like OS, language, library)
    - Configuration parameters (parameter name, default value, description, file_path if applicable)
    - Setup or installation steps (description, command, type like download, configure, build, run, verify)
    - Docker image name, run commands, or docker-compose snippets if present.
    - A brief raw text summary of the tool or process.
    - A suitable title for this quickstart guide.

    Return the information in a structured JSON format like this:
    {{
      "tool_name": "ExampleTool",
      # ... (rest of the JSON structure example) ...
    }}

    HTML Content (first 10000 characters):
    {html_snippet}
    ```
2.  **Loading the Prompt**: `GeminiExtractor` now reads this file and uses `prompt_template.format(url=str(url), html_snippet=html_snippet)` to create the final prompt.

    ```python
    # app/services/content_extractor.py (GeminiExtractor snippets)
    from pathlib import Path
    # ...
    class GeminiExtractor(ContentExtractor):
        def __init__(self, api_key: Optional[str] = None):
            self._api_key = api_key
            self.prompt_template_path = Path(__file__).parent / "prompts" / "gemini_extract_prompt.txt"
        
        async def extract(self, html_content: str, url: HttpUrl) -> ExtractedContent:
            # ... (inside if self._api_key block)
            try:
                prompt_template = self.prompt_template_path.read_text()
            except FileNotFoundError:
                logger.error(f"Prompt template file not found: {self.prompt_template_path}")
                # Handle error, return ExtractedContent with error metadata
            
            html_snippet = html_content[:10000] # Use a snippet of the HTML
            prompt = prompt_template.format(url=str(url), html_snippet=html_snippet)
            # ... rest of the API call logic
    ```

## Iterative Refinements: Learning from CI

Throughout this process, Continuous Integration (CI) played a vital role in maintaining code quality and catching issues early:
*   **Linting**: Our CI pipeline, using tools like Ruff, caught an unused import of `MockContentExtractor` in `app/main.py` after we switched the default to `GeminiExtractor`.
*   **Dependency Validation**: An early attempt to specify the `google-generativeai` dependency in `pyproject.toml` was incorrectly formatted. CI's package build step failed, highlighting the error and leading to a fix for PEP 508 compliance (e.g., changing `google-generativeai = "^0.5.0"` to `"google-generativeai~=0.5.0"` within the list).
*   **Testing (Implicitly)**: Although not explicitly shown here, if test suites were in place that mocked or instantiated extractors, `TypeError`s would have appeared when constructor signatures for our extractor classes diverged (e.g., some taking `api_key` and others not). This prompted a fix to standardize all extractor `__init__` methods to accept `api_key: Optional[str] = None`, ensuring consistency.

## Current Status and The Road Ahead

The `GeminiExtractor` in Quickstart Universe is now capable of making live API calls to Google's Gemini model, parsing structured information from web pages. This is a significant step up from relying solely on mock data and opens the door to genuinely intelligent content extraction.

Future enhancements for QSU's AI capabilities could include:
*   Implementing streaming responses from the AI for a more real-time feel on the frontend.
*   Activating and implementing the other placeholder extractors (GPT, Claude, Llama, etc.), potentially with a selection mechanism for the user or based on cost/performance.
*   Adding more sophisticated prompt management, including versioning and A/B testing of different prompts.
*   Exploring techniques like Retrieval Augmented Generation (RAG) if we build up a corpus of quickstart information.

This integration journey demonstrates a practical approach to incorporating powerful AI capabilities into an application, emphasizing secure configuration, robust error handling, maintainable prompt engineering, and the value of iterative development guided by CI feedback.
```
