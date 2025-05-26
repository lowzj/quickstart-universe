# Powering Up Quickstart Universe: Integrating Live Gemini API Calls for Content Extraction

The Quickstart Universe (QSU) project aims to simplify the process of understanding and setting up new tools and technologies by extracting key information from their quickstart guides. Initially, QSU relied on mock extractors. This post details the journey of integrating a real AI model, Google's Gemini, to perform live content extraction.

## The Starting Point: Mock Extractors and a Vision

Our first step was to lay down the groundwork. We defined an abstract `ContentExtractor` class and several placeholder implementations for popular AI models:

```python
# app/services/content_extractor.py (Conceptual)
class ContentExtractor(ABC):
    @abstractmethod
    async def extract(self, html_content: str, url: HttpUrl) -> ExtractedContent:
        pass

class GeminiExtractor(ContentExtractor):
    async def extract(self, html_content: str, url: HttpUrl) -> ExtractedContent:
        # Initial mock logic...
        logger.info(f"GeminiExtractor (Mock) processing URL: {url}")
        return ExtractedContent(
            source_url=url,
            tool_name="Gemini Extracted Tool (Placeholder)",
            extraction_metadata={"source": "GeminiExtractor - Placeholder"}
        )
# ... other placeholder extractors (Gpt, Llama, etc.) ...
```
This allowed us to build the application flow while deferring the complexity of actual AI integration.

## Phase 1: Bringing Gemini to Life - API Key Handling

To use the Gemini API, secure handling of API keys was paramount.

1.  **Configuration**: We decided to use environment variables for API keys, a common and secure practice. The `GeminiExtractor` was updated to accept an API key during initialization.
2.  **Application Logic**: `app/main.py` now reads the `GEMINI_API_KEY` from the environment:

    ```python
    # app/main.py (Snippet)
    import os
    # ...
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if gemini_api_key:
        logger.info("Gemini API key found. GeminiExtractor will attempt to use it.")
    else:
        logger.warning("GEMINI_API_KEY environment variable not set. GeminiExtractor will run in mock/placeholder mode.")
    
    extractor = GeminiExtractor(api_key=gemini_api_key)
    ```
    If the key isn't found, the extractor gracefully falls back to its mock behavior.

## Phase 2: Making the Call - Interacting with the Gemini SDK

With API key handling in place, we moved to the core task: calling the Gemini API.

1.  **Dependency**: The `google-generativeai` SDK was added to `pyproject.toml`:
    ```toml
    # pyproject.toml (Snippet)
    [project]
    dependencies = [
        # ... other dependencies
        "google-generativeai~=0.5.0"
    ]
    ```
2.  **SDK Initialization & API Call**: The `extract` method in `GeminiExtractor` was significantly enhanced:

    ```python
    # app/services/content_extractor.py (GeminiExtractor.extract snippet)
    import google.generativeai as genai
    # ... (logger, ExtractedContent, etc.)

    # Inside the extract method, if self._api_key is present:
    try:
        genai.configure(api_key=self._api_key)
        model = genai.GenerativeModel('gemini-pro') # Or your preferred model
    except Exception as e:
        logger.error(f"Failed to initialize Gemini SDK: {e}")
        # Return error ExtractedContent
    
    # ... (Prompt construction, see next section) ...

    try:
        response = model.generate_content(prompt)
        # Process response.text, handle potential blocks/errors
        ai_response_text = response.text 
    except Exception as e:
        logger.error(f"Gemini API call failed: {e}")
        # Return error ExtractedContent
    ```
3.  **Response Parsing & Error Handling**: The AI's response is expected to be JSON. We implemented robust parsing and error handling:
    *   If the API call fails (network, server errors).
    *   If the response is blocked by safety filters (the Gemini API provides reasons for this).
    *   If the response isn't valid JSON.
    *   In each case, we log the issue and populate `ExtractedContent` with appropriate error metadata, ensuring the application remains resilient.

## Engineering the Prompt: Guidance for the AI

A crucial part of working with LLMs is prompt engineering. Our initial prompt was hardcoded in the `GeminiExtractor`. For better maintainability, we externalized it:

1.  **Prompt File**: The prompt now resides in `app/services/prompts/gemini_extract_prompt.txt`. It uses placeholders like `{url}` and `{html_snippet}`.
    ```text
    # app/services/prompts/gemini_extract_prompt.txt (Snippet)
    Analyze the following HTML content from {url} and extract quickstart information.
    Focus on:
    - Tool name and version
    # ... (rest of the detailed prompt) ...
    Return the information in a structured JSON format...
    HTML Content (first 10000 characters):
    {html_snippet}
    ```
2.  **Loading the Prompt**: `GeminiExtractor` now reads this file and uses `prompt_template.format(url=str(url), html_snippet=html_snippet)` to create the final prompt.

    ```python
    # app/services/content_extractor.py (GeminiExtractor.extract snippet)
    from pathlib import Path
    # ...
    # (In __init__): self.prompt_template_path = Path(__file__).parent / "prompts" / "gemini_extract_prompt.txt"
    
    # (In extract):
    try:
        prompt_template = self.prompt_template_path.read_text()
    except FileNotFoundError:
        # Handle error
    
    html_snippet = html_content[:10000]
    prompt = prompt_template.format(url=str(url), html_snippet=html_snippet)
    ```

## Iterative Refinements: Learning from CI

Throughout this process, Continuous Integration (CI) played a vital role:
*   **Linting**: Caught an unused import.
*   **Dependency Validation**: Highlighted an incorrectly formatted dependency in `pyproject.toml`, leading to a fix ensuring PEP 508 compliance.
*   **Testing (Implicitly)**: Showed `TypeError`s when constructor signatures for our extractor classes diverged, prompting a fix to standardize them.

## Current Status and The Road Ahead

The `GeminiExtractor` in Quickstart Universe is now capable of making live API calls to Google's Gemini model, parsing structured information from web pages. This is a significant step up from mock data.

Future enhancements could include:
*   Implementing streaming responses for a more real-time feel on the frontend.
*   Activating and implementing the other placeholder extractors (GPT, Claude, etc.).
*   Adding more sophisticated prompt management and versioning.

This integration journey demonstrates a practical approach to incorporating powerful AI capabilities into an application, emphasizing configuration management, robust error handling, and iterative development.
