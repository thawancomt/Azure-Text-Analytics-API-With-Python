# Text Analysis Application

This project is a web application that leverages Azure Text Analytics to analyze text input for sentiment, entities, linked entities, key phrases, and language detection. The results are stored in a SQLite database and displayed on a web interface.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [API Endpoints](#api-endpoints)
- [Database Schema](#database-schema)
- [Contributing](#contributing)
- [License](#license)

## Features

- Sentiment Analysis
- Entity Recognition
- Linked Entity Recognition
- Key Phrase Extraction
- Language Detection
- Data persistence using SQLite
- Web interface for input and displaying results

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/thawancomt/Azure-Text-Analytics-API-With-Python.git
    cd Azure-Text-Analytics-API-With-Python
    cd  app
    ```

2. Create a virtual environment and activate it:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

4. Set up environment variables:
    - Create a `.env` file in the root directory.
    - Add your Azure Text Analytics API key and endpoint:
        ```
        KEY=your_azure_text_analytics_key
        ENDPOINT=your_azure_text_analytics_endpoint
        SECRET_KEY=your_flask_secret_key
        ```

5. Initialize the database:
    ```sh
    python -m flask shell
    from app.models.Model import SqlitDatabase
    db = SqlitDatabase()
    db.CreateTables()
    exit()
    ```

## Usage

1. Run the application:
    ```sh
    python -m flask --app app run --debug
    ```

2. Open your web browser and navigate to `http://127.0.0.1:5000`.

3. Enter your text input and select the analyses you want to perform.

## Project Structure