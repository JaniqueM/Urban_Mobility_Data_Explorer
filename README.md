NYC Taxi Trip Analysis

Overview
This project is a fullstack data-driven application built to analyze urban mobility patterns using the NYC Taxi Trip dataset. It demonstrates the complete pipeline from data cleaning and storage to API development and interactive frontend visualization.

The system enables users to explore trip trends, demand patterns, and traffic behavior through a dashboard powered by a RESTful API.

Objectives
- Clean and preprocess a large real-world dataset (1.4M+ records)
- Design and implement a fullstack architecture
- Build custom algorithmic logic without relying on built-in shortcuts
- Extract and interpret meaningful urban mobility insights
- Present findings through an interactive dashboard

Tech Stack
1. Frontend
HTML
CSS
JavaScript
Chart.js (for visualizations)

2. Backend
Python
Flask (REST API)
Database
SQLite

3. Data Processing
Pandas

System Architecture
The application follows a three-tier architecture:
- Frontend (Presentation Layer):
Handles user interaction, filtering, and visualization.
- Backend (Application Layer):
Processes requests, applies business logic, and serves data via API endpoints.
- Database (Data Layer):
Stores cleaned and enriched taxi trip data with indexing for performance.
Dataset
Source: NYC Taxi and Limousine Commission
Records: ~1.4 million trips
Key fields:
Pickup & drop-off timestamps
GPS coordinates
Trip duration
Passenger count
Data Cleaning & Preparation

Key steps:
Removed invalid GPS coordinates outside NYC bounds
Filtered unrealistic trip durations (<60s or >2hrs)
Removed invalid passenger counts (0 or >6)
Dropped missing and duplicate records
Created derived fields:
Estimated distance
Average speed
Features
Interactive dashboard for data exploration
Filtering by time, day, and trip characteristics
API endpoints for analytics:
Trips by hour
Average duration by day
Speed analysis
Custom Algorithm

A manual algorithm was implemented to identify Top-K busiest pickup hours:

Uses a dictionary for counting frequency
Applies selection sort (no built-in sorting functions)
Time complexity: O(n) overall
Key Insights
Peak Demand Hours
Highest taxi usage occurs during morning and evening rush hours.
Weekend Trip Behavior
Trips are longer on weekends, indicating leisure travel patterns.
Traffic Congestion Patterns
Speeds drop significantly during peak hours, showing congestion impact.
Challenges

Technical
Handling large dataset efficiently
Filtering accurate geographic boundaries
Estimating missing distance values

Team
Time clashes between members
Overlapping roles
Uneven workload distribution
Communication gaps
Version control conflicts
Integration issues between components
Future Improvements
Use real distance calculations (Haversine formula)
Migrate to PostgreSQL for scalability
Add geospatial heatmaps
Implement real-time data streaming
Deploy application to cloud
Add machine learning for trip prediction
How to Run the Project
Clone the repository:
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
Create a virtual environment:
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
Install dependencies:
pip install -r requirements.txt
Run the backend:
python app.py
Open the frontend:
Open index.html in your browser
Or access via localhost if configured
Project Structure
project/
│
├── backend/
│   ├── app.py
│   ├── database.db
│
├── frontend/
│   ├── index.html
│   ├── styles.css
│   ├── script.js
│
├── data/
│   └── train.csv
│
├── README.md
└── requirements.txt

Conclusion
This project demonstrates a complete data engineering and fullstack workflow. It highlights how raw data can be transformed into actionable insights through careful design, algorithmic thinking, and system integration.
