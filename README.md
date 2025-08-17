# Broken Link Finder Application

A simple Python application that crawls my Graduate School - University of Houston website to identify broken links and saves the results in a JSON file, which then uploaded as an artifact via GitHub Actions. The crawler complies with the University of Houston`robots.txt` rules.

## How It Works

- **Primary Links from CSV:**  
  The application fetches the primary links from a CSV file.

- **Iterate Over Links:**  
  It iterates over each primary link and fetches the corresponding page.

- **Identify Broken Links:**  
  On each page, the application extracts all links and verifies their validity.  
  🔍 **Note:** Only links found within the **body** of the page are checked — links in the **header** and **footer** are excluded.  
  Broken links are recorded in the JSON report and saved as an artifact via GitHub Actions.



