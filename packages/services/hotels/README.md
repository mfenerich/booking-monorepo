# Hotel Booking Platform with Multi-Agent AI

This project implements a hotel booking platform with a multi-agent AI system using Semantic Kernel. The system is built as a monorepo using NX with Python microservices for the backend and React for the frontend.

## Architecture

The platform consists of the following components:

1. **Frontend**: React application for user interface (already implemented)
2. **Microservices**:
   - **Users Service**: Handles user authentication and management
   - **Hotels Service**: Handles hotel listings, details, and reviews
   - **Agent Service**: Implements a multi-agent system using Semantic Kernel for intelligent booking assistance
3. **API Gateway**: NGINX gateway to route requests to appropriate services
4. **Shared Libraries**: Common code shared between services

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Node.js and npm (for frontend development)
- Python 3.11+ (for backend development)
- OpenAI API key (for the agent service)

### Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd hotel-booking-platform
   ```

2. Create a `.env` file in the root directory with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. Modify the frontend to use the real backend:
   ```bash
   python scripts/modify-frontend.py
   ```

4. Start the services using Docker Compose:
   ```bash
   docker-compose up
   ```

5. Access the application:
   - Frontend: http://localhost:3000
   - API Gateway: http://localhost:8080
   - Users Service API: http://localhost:8000
   - Hotels Service API: http://localhost:8001
   - Agent Service API: http://localhost:8002

## Features

### Hotel Service
- Hotel listings with filtering, sorting, and pagination
- Hotel details including images, descriptions, and benefits
- Hotel reviews with rating statistics
- Booking details and reservation options

### User Service
- User registration and authentication
- JWT-based authentication
- User profile management

### Agent Service
- Multi-agent system built with Semantic Kernel
- Coordinator agent to orchestrate interactions
- Specialized agents for search and booking operations
- Natural language interaction for hotel search and booking

## Development

### Service Structure

Each service follows a similar structure:
- `main.py`: Application entry point
- `routers/`: API endpoint definitions
- `services/`: Business logic
- `models/`: Database models (shared)
- `schemas.py`: Data validation schemas

### Database

SQLite is used for development, but the system is designed to work with any SQLAlchemy-supported database. The hotels service automatically seeds the database with hotels from the frontend's JSON data files.

### Running Services Locally

To run services locally without Docker:

1. Install Python dependencies:
   ```bash
   pip install -e ./packages/libs/api
   pip install -e ./packages/libs/auth
   pip install -e ./packages/libs/common
   pip install -e ./packages/libs/db
   pip install -e ./packages/libs/shared-models
   ```

2. Run the services:
   ```bash
   cd packages/services/users
   python -m booking_users.main
   
   cd packages/services/hotels
   python -m booking_hotels.main
   
   cd packages/services/agent
   python -m booking_agent.main
   ```

## API Endpoints

### Hotel Service
- `GET /api/hotels`: List hotels with filtering and pagination
- `GET /api/hotel/{hotelId}`: Get hotel details
- `GET /api/hotel/{hotelId}/booking/enquiry`: Get booking details for a hotel
- `GET /api/hotel/{hotelId}/reviews`: Get reviews for a hotel
- `PUT /api/hotel/add-review`: Add a review for a hotel
- `GET /api/availableCities`: Get list of available cities
- `GET /api/nearbyHotels`: Get nearby hotels
- `GET /api/popularDestinations`: Get popular destinations
- `GET /api/hotels/verticalFilters`: Get hotel filter options

### User Service
- `POST /api/v1/users/register`: Register a new user
- `POST /api/v1/users/login`: User login
- `GET /api/v1/users/auth-user`: Check authentication status
- `POST /api/v1/users/logout`: User logout
- `PUT /api/v1/users/{user_id}`: Update user profile
- `GET /api/v1/users/{user_id}`: Get user details

### Agent Service
- `POST /api/agent/chat`: Chat with the multi-agent system
- `GET /api/agent/sessions/{session_id}`: Get chat history for a session

## Technologies Used

- **Backend**:
  - FastAPI: Web framework
  - SQLAlchemy: ORM
  - Pydantic: Data validation
  - Semantic Kernel: Agent framework
  - JWT: Authentication

- **Frontend**:
  - React: UI framework
  - Tailwind CSS: Styling

- **Infrastructure**:
  - Docker: Containerization
  - NGINX: API Gateway

## License

[MIT](LICENSE)
