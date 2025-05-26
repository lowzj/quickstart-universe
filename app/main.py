import os
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import requests
import logging
from pydantic import HttpUrl  # Added for URL validation/casting

# Service and model imports
from .services.content_extractor import ExtractedContent, GeminiExtractor

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
templates = Jinja2Templates(
    directory="app/templates"
)  # Assumes templates are in 'app/templates'

# Instantiate the extractor
# Future enhancement: Allow extractor selection via environment variable or configuration
gemini_api_key = os.getenv("GEMINI_API_KEY")
if gemini_api_key:
    logger.info("Gemini API key found. GeminiExtractor will attempt to use it.")
else:
    logger.warning(
        "GEMINI_API_KEY environment variable not set. "
        "GeminiExtractor will run in mock/placeholder mode."
    )
extractor = GeminiExtractor(api_key=gemini_api_key)


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/process-url", response_class=HTMLResponse)
async def process_url(request: Request, url: str = Form(...)):
    raw_content_snippet = None
    extracted_info = None
    bash_script = None
    docker_compose_script = None
    error_message = None
    simulated_steps = []  # Initialize the list

    try:
        simulated_steps.append(f"Attempting to fetch content from: {url}")
        logger.info(f"Fetching URL: {url}")
        response = requests.get(
            url, timeout=10, headers={"User-Agent": "QuickstartUniverseMVP/0.1"}
        )
        response.raise_for_status()
        html_content = response.text
        raw_content_snippet = html_content[:500]
        simulated_steps.append("Successfully fetched content snippet.")

        # Convert string URL to Pydantic HttpUrl for the extractor
        try:
            pydantic_url_obj = HttpUrl(url)
            simulated_steps.append(f"URL validated: {pydantic_url_obj}")
        except ValueError as e:  # Pydantic validation error for HttpUrl
            logger.error(f"URL validation error: {url} - {e}")
            error_message = f"Invalid URL format: {url}. Please enter a valid URL (e.g., http://example.com)."
            simulated_steps.append(f"Error: Invalid URL format - {url}. Details: {e}")
            return templates.TemplateResponse(
                "index.html",
                {
                    "request": request,
                    "submitted_url": url,
                    "error": error_message,
                    "raw_content_snippet": raw_content_snippet,
                    "simulated_steps": simulated_steps,
                },
            )

        # Call the content extractor
        simulated_steps.append(
            f"Calling ContentExtractor ({extractor.__class__.__name__}) for URL: {pydantic_url_obj}"
        )
        extracted_data: ExtractedContent = await extractor.extract(
            html_content=html_content, url=pydantic_url_obj
        )
        extracted_info = extracted_data.model_dump(
            mode='json', exclude_none=True
        )  # Ensure JSON-serializable types
        simulated_steps.append(
            f"ContentExtractor ({extractor.__class__.__name__}) finished. Tool identified: {extracted_data.tool_name or 'None'}"
        )

        # Generate placeholder scripts based on extracted_data
        if extracted_data.docker_run_command:
            bash_script = f'''#!/bin/bash
echo "Attempting to run {extracted_data.tool_name or "tool"} Docker container (from Extractor)..."
{extracted_data.docker_run_command}
echo "{extracted_data.tool_name or "Tool"} container should be running. Check with 'docker ps'."'''
            simulated_steps.append("Generated Bash script placeholder.")
        else:
            bash_script = "# No Docker run command suggested by extractor."
            simulated_steps.append("No Bash script generated (no docker_run_command).")

        if extracted_data.docker_compose_snippet:
            docker_compose_script = extracted_data.docker_compose_snippet
            simulated_steps.append("Using Docker Compose snippet from extractor.")
        else:
            docker_compose_script = (
                "# No Docker Compose snippet suggested by extractor."
            )
            simulated_steps.append("No Docker Compose snippet found.")

        # If the extractor itself indicates no tool was found via its metadata or tool_name
        # Note: The specific string "MockExtractor - No specific tool recognized" might need to be generalized
        # if we want this logic to apply to other extractors that might also signal "no tool recognized".
        # For now, this specific check might not be hit if GeminiExtractor always returns some tool name.
        if (
            not extracted_data.tool_name
            and extracted_info.get("extraction_metadata", {}).get("source")
            == "MockExtractor - No specific tool recognized" # This specific check might become less relevant
        ):
            if "message" not in extracted_info:
                extracted_info["message"] = (
                    "No specific tool recognized by content extractor."
                )

    except requests.Timeout:
        logger.error(f"Timeout when fetching URL: {url}")
        error_message = (
            "The request timed out. The server might be slow or the URL incorrect."
        )
        simulated_steps.append(f"Error: Timeout fetching URL {url}.")
    except requests.RequestException as e:
        logger.error(f"Error fetching URL {url}: {e}")
        error_message = f"Could not fetch content from URL: {e}"
        simulated_steps.append(
            f"Error: Could not fetch content from URL {url}. Details: {e}"
        )
    except Exception as e:  # Catch-all for other unexpected errors
        logger.error(
            f"An unexpected error occurred during processing: {e}", exc_info=True
        )  # Log stack trace
        error_message = f"An unexpected error occurred: {str(e)}"
        simulated_steps.append(f"Error: An unexpected error occurred: {str(e)}")

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "submitted_url": url,
            "raw_content_snippet": raw_content_snippet,
            "extracted_info": extracted_info,
            "bash_script": bash_script,
            "docker_compose_script": docker_compose_script,
            "error": error_message,
            "simulated_steps": simulated_steps,  # Add this to the context
        },
    )


# To run (from the directory containing 'app'):
# uvicorn app.main:app --reload
