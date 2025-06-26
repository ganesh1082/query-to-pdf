# AI-Powered Professional Report Generator (v2.0)

This project generates comprehensive, professional research reports from a single prompt. It uses Google's Gemini for content and chart data generation, Matplotlib/Seaborn for data visualization, and Typst for high-quality PDF rendering.

## Key Features

- 🤖 **AI-Driven Content**: Leverages Gemini 1.5 Flash to generate an entire multi-page report structure, including text and data, from one prompt.
- 📊 **Dynamic Visualizations**: Automatically creates professional charts (bar, line, pie, etc.) based on the AI-generated data.
- 📄 **High-Quality PDF Output**: Uses [Typst](https://typst.app/), a modern typesetting system, to produce clean, professional, and beautiful PDF documents.
- 🔧 **Customizable**: Easily configure report details, topics, and page count via command-line arguments.
- ⚙️ **Streamlined & Robust**: Refactored for simplicity, removing legacy code and focusing on a reliable generation pipeline.

## Prerequisites

1.  **Python 3.10+**
2.  **Typst**: You must have the Typst compiler installed and available in your system's PATH.
    - **Installation Guide**: [https://github.com/typst/typst#installation](https://github.com/typst/typst#installation)
3.  **Google Gemini API Key**:
    - Get one from [Google AI Studio](https://aistudio.google.com/app/apikey).

## Quick Setup

1.  **Clone the Repository**

    ```bash
    git clone <your-repo-url>
    cd query-to-pdf
    ```

2.  **Set up a Virtual Environment**

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure API Key**
    - Create a file named `.env` in the project root.
    - Add your Gemini API key to it:
      ```env
      GEMINI_API_KEY="your-google-gemini-api-key"
      ```

## How to Run

Execute the report generator from your terminal.

**Generate a Default Report:**

```bash
python -m query_to_pdf.index
```
