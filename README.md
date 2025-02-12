# Pro Tracker

## Overview
Pro Tracker is a productivity tracking application designed to monitor and categorize user activities. The project is divided into two main components:
1. **Frontend**: A React-based frontend that provides a user-friendly interface.
2. **Backend**: A Python-based backend using Flask to track activities locally and provide an API system.

## Project Structure
```
pro_tracker/
│── frontend/            # React frontend
│── backend/             # Python backend with Flask API
│   ├── app.py           # Main Flask application
│   ├── tracker.py       # Script to track and categorize activities
│   ├── requirements.txt # Dependencies
│   ├── config.json      # Configuration file
│── README.md            # Project documentation
```

## Features
- Categorizes user activities as productive or entertainment.
- Tracks local app usage and website interactions.
- Provides an API for frontend interaction.
- Simple and efficient tracking mechanism.

## Installation
### Backend
1. Navigate to the `backend` folder:
   ```sh
   cd backend
   ```
2. Create a virtual environment (optional but recommended):
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Run the Flask API:
   ```sh
   python app.py
   ```

### Frontend
1. Navigate to the `frontend` folder:
   ```sh
   cd frontend
   ```
2. Install dependencies:
   ```sh
   npm install
   ```
3. Start the frontend application:
   ```sh
   npm start
   ```

## API Endpoints
| Method | Endpoint       | Description                     |
|--------|---------------|---------------------------------|
| GET    | /activities   | Get tracked activities         |
| POST   | /track        | Track a new activity           |
| GET    | /status       | Check API status               |

## Future Enhancements
- Implement AI-based activity classification.
- Add user authentication and profiles.
- Export productivity reports.

## Contributing
Feel free to submit pull requests or open issues for improvements!

## License
This project is open-source under the MIT License.

