# DataEngineer_NY_Project

## Project Overview

The **DataEngineer_NY_Project** harnesses Docker to orchestrate a multi-container application that interacts with various New York Times APIs. It efficiently captures data from the New York Times' Articles, Books, and other APIs, stores this data in a structured database, and then displays it on a dynamically generated website.

## Features

- **Data Collection**: Automated data fetching from multiple New York Times APIs.
- **Data Storage**: Efficient storage of fetched data in a structured database.
- **Web Presentation**: A user-friendly website that presents the collected data.
- **Docker Orchestration**: Utilizes Docker containers to manage the application's microservices architecture.

## Architecture

This project includes four main Docker containers:
- **Data Fetcher**: Connects to New York Times APIs to collect articles, books, and other data.
- **Database**: Stores all the fetched data in a manageable and query-able format.
- **Backend Server**: Handles API requests from the frontend and interacts with the database to retrieve data.
- **Frontend Webapp**: Displays the data in a user-friendly format on the web.

## Prerequisites

Before you begin, ensure you have Docker installed on your system. [Download Docker here](https://www.docker.com/products/docker-desktop).

## Installation

Clone the repository to your local machine:

```bash
git clone https://github.com/KSuljic/DataEngineer_NY_Project.git
cd DataEngineer_NY_Project
```

To spin up the project, run:

```bash
docker-compose up --build
```

## Usage

After running the docker containers, you can access the website at http://localhost:PORT/, where PORT is the port specified in your Docker configuration for the frontend service.
Contributing

Contributions are welcome! Feel free to fork the repository and submit pull requests.
License

This project is licensed under the MIT License - see the LICENSE.md file for details.
Acknowledgments

    New York Times for providing the APIs used in this project.
