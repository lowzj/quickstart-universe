# Quickstart Universe ✨🚀

**One-click to ignite your tool universe!**

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/lowzj/quickstart-universe)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)
[![Stars](https://img.shields.io/github/stars/lowzj/quickstart-universe.svg?style=social)](https://github.com/lowzj/quickstart-universe/stargazers)
[![Forks](https://img.shields.io/github/forks/lowzj/quickstart-universe.svg?style=social)](https://github.com/lowzj/quickstart-universe/network/members)
[![Issues](https://img.shields.io/github/issues/lowzj/quickstart-universe.svg)](https://github.com/lowzj/quickstart-universe/issues)

---

## 🎯 Core Value

Quickstart Universe aims to drastically reduce the time spent on learning and deploying new tools from hours or even days to mere minutes. By leveraging AI to analyze Quickstart documentation, we generate one-click deployment scripts for various environments, significantly lowering the barrier to entry for new technologies and boosting productivity and the joy of exploration.

---

## 🌟 Key Features

*   **Intelligent Input:**
    *   Auto-search for relevant Quickstart docs by tool name.
    *   Direct URL input for Quickstart documentation.
    *   Upload Quickstart documents (Markdown, TXT, PDF).
    *   Analyze Git repository addresses.
*   **AI-Powered Analysis Engine:**
    *   Deep understanding of document content using Large Language Models (LLM) and NLP.
    *   Accurate extraction of dependencies, configuration parameters, build steps, startup commands, and verification methods.
    *   Conversion of natural language instructions into standardized operational sequences.
*   **Multi-Environment Script Generation:**
    *   **Local:** Shell scripts (Bash/Zsh/PowerShell), Docker (`Dockerfile`, `docker-compose.yml`).
    *   **Container Orchestration:** Kubernetes (Deployment, Service, ConfigMap YAMLs, etc.).
    *   **(Future) Cloud Platforms:** AWS CloudFormation, Azure ARM, GCP Deployment Manager.
    *   **(Future) Configuration Management:** Ansible Playbooks, Terraform HCL.
*   **User-Friendly Interaction:**
    *   Clean and intuitive user interface.
    *   Script preview and online editing capabilities.
    *   History tracking and one-click copy/download.
*   **Community-Driven Hub ("Universe Hub"):** (Planned)
    *   Pre-validated Quickstart scripts for popular tools.
    *   User contributions, sharing, and rating of scripts.

---

## Current CLI Functionality

This section describes the current command-line interface for interacting with components.

### How to use?

```bash
python3 qsu.py ${component}
```

### Components List

* [kafka](./kafka)

---

## 💡 How It Works

1.  **Input:** User provides a tool name, the URL of a Quickstart document, or uploads the document directly.
2.  **AI Analysis:** Our AI engine parses the document, extracting key deployment information such as dependencies, configurations, commands, etc.
3.  **Script Generation:** Based on the analysis and the user's selected target environment, the corresponding deployment script is generated.
4.  **Deploy!:** The user obtains the script, reviews it, and can then quickly deploy the tool.

---

## 🚀 Supported Output Environments

We aim to support a wide range of deployment environments:

*   **Local Development:**
    *   `Bash` (Linux)
    *   `Zsh` (macOS/Linux)
    *   `PowerShell` (Windows)
    *   `Dockerfile`
    *   `docker-compose.yml`
*   **Containers & Orchestration:**
    *   `Kubernetes YAMLs` (Deployments, Services, ConfigMaps, etc.)
*   **Future:**
    *   AWS (CloudFormation, EC2 User Data)
    *   Azure (ARM Templates, Azure CLI)
    *   GCP (Deployment Manager, gcloud CLI)
    *   Ansible Playbooks
    *   Terraform Modules

---

## AI Model Integration

The application has been updated to support content extraction from quickstart documents using various AI models. This allows for more sophisticated parsing of HTML content to identify key setup steps, dependencies, and configurations.

Placeholder implementations for the following AI models have been added to `app/services/content_extractor.py`:
- `GeminiExtractor`
- `GptExtractor`
- `LlamaExtractor`
- `DeepSeekExtractor`
- `ClaudeExtractor`

These are currently **placeholders** and do not make live API calls. To enable full functionality for any of these extractors, users would need to:
1.  **Install the respective Python SDK:** For example, for Gemini, you would install `google-generativeai`. A placeholder for this is in `pyproject.toml`.
2.  **Configure API Keys:** Securely manage API keys, typically via environment variables (e.g., `GEMINI_API_KEY`) or a dedicated configuration file. The extractor classes would need to be updated to load these keys.
3.  **Implement API Logic:** Within each extractor class (e.g., `GeminiExtractor.extract`), implement the actual logic for:
    *   Initializing the AI model's client with the API key.
    *   Constructing an appropriate prompt using the input HTML content.
    *   Making the API call to the model.
    *   Parsing the model's response to populate the `ExtractedContent` Pydantic model.

### Configuring Gemini (Google AI Studio)

To enable the `GeminiExtractor` to make actual API calls to the Google AI Studio (Gemini API), you need to configure your API key:

1.  **Set the Environment Variable**:
    The `GeminiExtractor` expects your API key to be available as an environment variable named `GEMINI_API_KEY`. You can set this in your shell session or `.env` file:
    ```bash
    export GEMINI_API_KEY="YOUR_API_KEY_HERE"
    ```
    Replace `"YOUR_API_KEY_HERE"` with your actual API key obtained from Google AI Studio.

2.  **Dependency Installation**:
    The `google-generativeai` package, which is the Python SDK for the Gemini API, is now listed as a dependency in `pyproject.toml` (e.g., `google-generativeai = "^0.5.0"`). Ensure it's installed in your project's environment. If you are managing dependencies manually or setting up a new environment, you might need to install it, for example, using a command like:
    ```bash
    uv pip sync pyproject.toml 
    ```
    (or `pip install google-generativeai` if you're managing packages individually).

If the `GEMINI_API_KEY` environment variable is not set, the `GeminiExtractor` will automatically fall back to using mock/placeholder data, and a warning will be logged indicating this. This allows for development and testing without requiring a live API key.

Currently, `app/main.py` is configured to use `GeminiExtractor`. This can be easily changed by modifying the `extractor` variable instantiation in `app/main.py` to use one of the other implemented placeholder extractors (e.g., `extractor = GptExtractor()`).

---

## 🗺️ Roadmap

*   **✅ MVP (Completed/In Progress):**
    *   Core AI analysis engine, supporting URL input.
    *   Generation of Shell (Bash) and Docker Compose scripts.
    *   Coverage for an initial set of popular tools.
*   **➡️ V1.0 (Next Steps):**
    *   Support for tool name search and Markdown/TXT file uploads.
    *   Enhanced AI analysis capabilities for more complex document structures.
    *   Addition of Kubernetes YAML and PowerShell script generation.
    *   Implementation of user accounts, history, and basic feedback features.
    *   Broader coverage of popular tools.
*   **🌌 V1.5+ (Future Vision):**
    *   Launch of the "Universe Hub" community feature.
    *   Support for native cloud platform deployment templates (AWS, Azure, GCP).
    *   Support for configuration management tools (Ansible, Terraform).
    *   API access for CI/CD integration.
    *   IDE plugins (e.g., VS Code).

---

## 🛠️ Tech Stack (Tentative)

*   **Frontend:** React / Vue.js / Svelte
*   **Backend API:** Python (FastAPI / Flask) / Node.js (Express) / Go
*   **AI Core:**
    *   LLM: OpenAI API (GPT-4/3.5-turbo), Claude API, or open-source models (Llama, Mixtral)
    *   NLP: spaCy, NLTK
    *   Document Processing: `BeautifulSoup`, `PyPDF2`, `python-markdown2`
    *   Vector Database: Pinecone, Weaviate, ChromaDB (for RAG)
*   **Database:** PostgreSQL / MongoDB
*   **Task Queue:** Celery / RabbitMQ
*   **Deployment:** Docker, Kubernetes

---

## 🚀 Getting Started

Quickstart Universe is currently under active development. Stay tuned for our first public release!

You can:
1.  **Star ⭐** this project to follow the latest progress.
2.  **Watch 👀** this project to receive update notifications.
3.  Join our discussion (Link to Discord/Slack/Mailing List - if available).

---

## Development Setup with `uv`

This project uses `uv` for package management and virtual environments.

1.  **Create/Recreate Virtual Environment**:
    ```bash
    uv venv
    ```
    This will create a `.venv` directory in the project root.

2.  **Activate Virtual Environment**:
    *   macOS/Linux:
        ```bash
        source .venv/bin/activate
        ```
    *   Windows (PowerShell):
        ```bash
        .venv\Scripts\Activate.ps1
        ```

3.  **Install Dependencies**:
    Once the virtual environment is activated, install dependencies from `pyproject.toml`:
    ```bash
    uv pip sync pyproject.toml
    ```
    (Note: `uv sync` might also work depending on `uv` version and project setup.)


4.  **Adding New Dependencies**:
    *   To add a runtime dependency:
        ```bash
        uv add <package_name>
        ```
    *   To add a development dependency (e.g., linters, test tools):
        ```bash
        uv add --dev <package_name>
        ```

5.  **Running the Web Application**:
    Once dependencies are installed and the virtual environment is active, run the FastAPI application using Uvicorn:
    ```bash
    uvicorn app.main:app --reload
    ```
    This command should be run from the project root directory (the directory containing the `app` folder). The application will typically be available at `http://127.0.0.1:8000`.

## Development Environment & CI/CD

### VS Code Configuration
This project includes recommended VS Code settings in `.vscode/settings.json`. These settings configure:
- The Python interpreter to use the project's virtual environment (`.venv`).
- Ruff as the default linter and formatter, with format-on-save enabled.
- `unittest` as the testing framework, with appropriate discovery settings.

Using these settings can help maintain code quality and consistency across collaborators.

### GitHub Actions
This project utilizes GitHub Actions for automation:
- **Continuous Integration (CI)**: On every push to `main`/`master` or pull request targeting these branches, the CI pipeline (`.github/workflows/ci.yml`) automatically runs linters (Ruff) and tests (`unittest`) across multiple Python versions.
- **Continuous Deployment (CD)**: When a new version tag (e.g., `v0.1.0`) is pushed, the workflow in `.github/workflows/publish.yml` automatically builds the package and publishes it to PyPI. It also creates a corresponding GitHub Release.

---

## 🤝 Contributing

We warmly welcome contributions of all kinds! Whether it's bug reports, feature suggestions, or code contributions.

Please check our `CONTRIBUTING.md` (to be created) file for detailed contribution guidelines.

Key areas for contribution:
*   **Provide Quickstart document samples:** Help us test and improve the accuracy of AI analysis.
*   **Feedback on generated script quality:** Let us know which scripts work well and which have issues.
*   **Code contributions:** Help us implement new features or fix bugs.
*   **Documentation improvement:** Help us refine the README and other documents.

---

## LICENSE

**QUICKSTART UNIVERSE** is licensed under the Apache License, Version 2.0. See [LICENSE](./LICENSE) for the full license text.

---

Let's build the future of tool deployment together! 💡
