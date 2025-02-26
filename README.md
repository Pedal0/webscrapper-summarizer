# Web Scraper & LLM Summary Application

This application is designed to scrape websites and summarize the extracted content using an AI model via OpenRouter.

## Features

- **Web Scraping:** Extracts text elements (e.g., paragraphs) from target websites.
- **AI Summarization:** Uses OpenRouter to generate a clear and concise summary of the scraped information.
- **Text-to-Speech:** Converts summaries into audio using ElevenLabs' voice synthesis API.
- **Thematic Analysis:** Supports multiple themes/categories for scraping and summarization.

## Installation

1. **Clone the Repository:**

   ```
   git clone <repository_url>
   cd webscrapper-summarizer
   ```

2. **Install Dependencies Using Pipenv:**

   ```
   pipenv install
   pipenv shell
   ```

3. **Create Environment File:**
   Create a `.env` file at the root of the project with the following content:
   ```
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   ELEVEN_LABS_API_KEY=your_elevenlabs_api_key_here
   ```
   You can obtain your API keys at:
   - [OpenRouter](https://openrouter.ai/) - For AI text generation
   - [ElevenLabs](https://elevenlabs.io/) - For text-to-speech audio generation

## Configuration

- **Themes and Sites:**
  - The available themes and corresponding URLs for scraping are defined in the `scraper.py` file under the `theme_url_mapping` dictionary.
  - To add new sites or categories, update the `theme_url_mapping` in `scraper.py` accordingly.

## Usage

1. **Running the App:**
   Launch the Streamlit application:
   ```
   streamlit run main.py
   ```
2. **Select a Theme:**
   On the application interface, select a theme to start scraping relevant websites.

3. **Scraping and Summarization:**
   Click the "Lancer le scraping" (Start Scraping) button to scrape data from the selected site, which will then be summarized by the integrated AI model.

## Extending the Application

- **Adding New Sites/Categories:**

  - Update `scrapper/scraper.py` by adding new entries to the `theme_url_mapping` dictionary.
  - Ensure that the new category is also reflected in the configuration files (e.g., `data/themes.json`) if needed.

- **Customizing the Scraper:**
  - The scraper is implemented in the `WebScraper` class in `scrapper/scraper.py`. Customize the parsing logic in the `_parse_html` method if necessary.
