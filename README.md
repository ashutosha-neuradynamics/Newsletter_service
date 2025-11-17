# Newsletter Service

A robust newsletter scheduling and delivery service built with FastAPI, PostgreSQL, Celery, and Docker. This service allows you to schedule newsletter content for specific topics and automatically send them to subscribers at designated times.

## 🏗️ Architecture

The service consists of the following components:

- **FastAPI Web Server**: RESTful API for managing topics, subscribers, subscriptions, and content
- **PostgreSQL Database**: Stores all application data (topics, subscribers, subscriptions, content)
- **Redis**: Message broker and result backend for Celery
- **Celery Worker**: Processes email sending tasks asynchronously
- **Celery Beat**: Periodic scheduler that checks for due content every minute

### Technology Stack

- **Backend Framework**: FastAPI 0.104.1
- **Database**: PostgreSQL 15
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **Task Queue**: Celery 5.3.4 with Redis
- **Email Service**: Brevo (formerly Sendinblue) API
- **Containerization**: Docker & Docker Compose

## 🚀 Local Development

### Prerequisites

- Docker and Docker Compose installed
- Python 3.11+ (for local development without Docker)
- Brevo API key (optional for development - emails will be logged to console)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Pier_assignment
   ```

2. **Set up environment variables**
   
   Create a `.env` file in the root directory:
   ```env
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/newsletter
   CELERY_BROKER_URL=redis://localhost:6379/0
   CELERY_RESULT_BACKEND=redis://localhost:6379/1
   CELERY_REDBEAT_REDIS_URL=redis://localhost:6379/0
   BREVO_API_KEY=your_brevo_api_key_here
   BREVO_FROM_EMAIL=newsletter@example.com
   BREVO_FROM_NAME=Newsletter Service
   ```

3. **Start the services**
   ```bash
   docker-compose up --build
   ```

   This will start:
   - PostgreSQL database on port 5432
   - Redis on port 6379
   - FastAPI web server on port 8000
   - Celery worker
   - Celery beat scheduler

4. **Run database migrations**
   ```bash
   docker-compose exec web alembic upgrade head
   ```

5. **Access the API**
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

### Running Tests

```bash
# Run all tests
docker-compose exec web pytest

# Run specific test file
docker-compose exec web pytest tests/test_models.py

# Run with coverage
docker-compose exec web pytest --cov=app tests/
```

## 📚 API Documentation

### Base URL
- Local: `http://localhost:8000`
- Production: `https://newsletterservice-production.up.railway.app`

### Endpoints

#### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "ok"
}
```

#### Topics

**Create Topic**
```http
POST /api/topics/
Content-Type: application/json

{
  "name": "Technology",
  "description": "Tech news and updates"
}
```

**List Topics**
```http
GET /api/topics/
```

**Get Topic by ID**
```http
GET /api/topics/{topic_id}
```

**Update Topic**
```http
PATCH /api/topics/{topic_id}
Content-Type: application/json

{
  "description": "Updated description",
  "is_active": true
}
```

**Delete Topic**
```http
DELETE /api/topics/{topic_id}
```

#### Subscribers

**Create Subscriber**
```http
POST /api/subscribers/
Content-Type: application/json

{
  "email": "user@example.com"
}
```

**List Subscribers**
```http
GET /api/subscribers/
```

**Get Subscriber by ID**
```http
GET /api/subscribers/{subscriber_id}
```

**Update Subscriber**
```http
PATCH /api/subscribers/{subscriber_id}
Content-Type: application/json

{
  "is_active": false
}
```

#### Subscriptions

**Create Subscription** (Subscribe a user to a topic)
```http
POST /api/subscriptions/
Content-Type: application/json

{
  "subscriber_id": 1,
  "topic_id": 1
}
```

**List Subscriptions**
```http
GET /api/subscriptions/
GET /api/subscriptions/?subscriber_id=1
GET /api/subscriptions/?topic_id=1
```

**Update Subscription**
```http
PATCH /api/subscriptions/{subscription_id}
Content-Type: application/json

{
  "is_active": false
}
```

#### Content

**Create Content** (Schedule a newsletter)
```http
POST /api/content/
Content-Type: application/json

{
  "topic_id": 1,
  "title": "Weekly Tech Update",
  "body": "This is the newsletter content...",
  "scheduled_at": "2024-12-01T10:00:00Z"
}
```

**List Content**
```http
GET /api/content/
GET /api/content/?topic_id=1
GET /api/content/?status=pending
```

**Get Content by ID**
```http
GET /api/content/{content_id}
```

**Update Content**
```http
PATCH /api/content/{content_id}
Content-Type: application/json

{
  "title": "Updated Title",
  "status": "cancelled"
}
```

### Content Status Values

- `pending`: Content is scheduled but not yet sent
- `sent`: Content has been successfully sent
- `failed`: Content sending failed
- `cancelled`: Content was cancelled before sending

## 🚢 Deployment to Railway

### Prerequisites

1. Railway account (sign up at https://railway.app)
2. Railway CLI installed (optional, can use web interface)
3. Git repository with your code

### Deployment Steps

1. **Create a new Railway project**
   - Go to https://railway.app
   - Click "New Project"
   - Select "Deploy from GitHub repo" (or use Railway CLI)

2. **Add Services**

   You'll need to create 5 services:
   
   **a. PostgreSQL Database**
   - Click "New" → "Database" → "Add PostgreSQL"
   - Railway will automatically provide `DATABASE_URL` environment variable
   
   **b. Redis**
   - Click "New" → "Database" → "Add Redis"
   - Railway will automatically provide `REDIS_URL` environment variable
   
   **c. Web Service (FastAPI)**
   - Click "New" → "GitHub Repo" → Select your repository
   - Railway will detect the Dockerfile
   - Set the start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Add environment variables (see below)
   
   **d. Celery Worker**
   - Click "New" → "GitHub Repo" → Select your repository
   - Set the start command: `celery -A app.celery_app worker --loglevel=info`
   - Add environment variables (see below)
   
   **e. Celery Beat**
   - Click "New" → "GitHub Repo" → Select your repository
   - Set the start command: `celery -A app.celery_app beat --loglevel=info`
   - Add environment variables (see below)

3. **Configure Environment Variables**

   For each service (Web, Celery Worker, Celery Beat), add these environment variables:
   
   ```env
   DATABASE_URL=<from PostgreSQL service>
   CELERY_BROKER_URL=<from Redis service, e.g., redis://default:password@redis.railway.internal:6379>
   CELERY_RESULT_BACKEND=<same as CELERY_BROKER_URL>
   CELERY_REDBEAT_REDIS_URL=<same as CELERY_BROKER_URL>
   BREVO_API_KEY=<your_brevo_api_key>
   BREVO_FROM_EMAIL=<your_sender_email>
   BREVO_FROM_NAME=<your_sender_name>
   PORT=<automatically set by Railway for web service>
   ```

4. **Run Database Migrations**

   After the web service is deployed, run migrations:
   
   ```bash
   # Using Railway CLI
   railway run alembic upgrade head
   
   # Or connect to the web service shell and run:
   alembic upgrade head
   ```

5. **Verify Deployment**

   - Check the web service logs to ensure it started successfully
   - Visit your Railway app URL: `https://your-app.railway.app/docs`
   - Test the health endpoint: `https://your-app.railway.app/health`

### Railway-Specific Notes

- Railway automatically provides `$PORT` environment variable for web services
- Use Railway's internal service URLs for database connections (e.g., `redis.railway.internal`)
- Railway provides free tier with limited resources - monitor usage
- Consider using Railway's volume mounts for persistent data if needed

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Yes | - |
| `CELERY_BROKER_URL` | Redis broker URL for Celery | Yes | - |
| `CELERY_RESULT_BACKEND` | Redis result backend URL | Yes | - |
| `CELERY_REDBEAT_REDIS_URL` | Redis URL for RedBeat scheduler | No | - |
| `BREVO_API_KEY` | Brevo API key for email sending | No* | - |
| `BREVO_FROM_EMAIL` | Sender email address | No | `newsletter@example.com` |
| `BREVO_FROM_NAME` | Sender name | No | `Newsletter Service` |

*If `BREVO_API_KEY` is not set, emails will be logged to console instead of being sent (development mode).

### Getting Brevo API Key

1. Sign up at https://www.brevo.com/
2. Go to Settings → API Keys
3. Create a new API key
4. Copy the key and set it as `BREVO_API_KEY` environment variable

## 🧪 Testing

The project includes comprehensive tests following TDD principles:

- **Model Tests**: Test database models and relationships
- **API Tests**: Test all REST endpoints
- **Scheduling Logic Tests**: Test content scheduling and subscriber retrieval
- **Celery Task Tests**: Test background task execution

Run tests:
```bash
pytest tests/
```

## 📊 How It Works

1. **Create Topics**: Define newsletter categories (e.g., "Technology", "Science")
2. **Add Subscribers**: Register users with their email addresses
3. **Create Subscriptions**: Link subscribers to topics they're interested in
4. **Schedule Content**: Create newsletter content with a scheduled send time
5. **Automatic Delivery**: 
   - Celery Beat checks every minute for content due to be sent
   - For each due content, it enqueues a send task
   - Celery Worker processes the task:
     - Retrieves all active subscribers for the content's topic
     - Sends emails via Brevo API
     - Updates content status (sent/failed)

## ✨ Improvements & Future Enhancements

### Potential Improvements

1. **Authentication & Authorization**
   - Add API key authentication or JWT tokens
   - Role-based access control (admin, editor, viewer)
   - Rate limiting to prevent abuse

2. **Email Enhancements**
   - HTML email templates with styling
   - Email personalization (merge tags)
   - Unsubscribe links
   - Email tracking (open rates, click rates)

3. **Scalability**
   - Horizontal scaling of Celery workers
   - Database connection pooling
   - Caching layer (Redis) for frequently accessed data
   - CDN for static assets

4. **Monitoring & Observability**
   - Application performance monitoring (APM)
   - Structured logging with correlation IDs
   - Metrics and dashboards (Prometheus, Grafana)
   - Error tracking (Sentry)

5. **Features**
   - Content templates
   - A/B testing for newsletters
   - Scheduled content preview
   - Bulk operations API
   - Webhook notifications for events

6. **Reliability**
   - Retry logic with exponential backoff
   - Dead letter queue for failed tasks
   - Database backup and recovery
   - Health check endpoints for all services

## ⚠️ Known Limitations & Pitfalls

### Current Limitations

1. **No Authentication**: APIs are currently open - anyone with the URL can access them
   - **Mitigation**: Deploy behind a reverse proxy with authentication, or add API key auth

2. **Simple Time Zone Handling**: All times are in UTC
   - **Mitigation**: Add timezone support per subscriber or content

3. **No Email Retry Logic**: If email sending fails, it's marked as failed without retry
   - **Mitigation**: Implement retry mechanism with exponential backoff (partially implemented in Celery tasks)

4. **Limited Error Handling**: Basic error messages, no detailed error tracking
   - **Mitigation**: Integrate error tracking service (e.g., Sentry)

5. **No Rate Limiting**: API endpoints can be called unlimited times
   - **Mitigation**: Add rate limiting middleware

6. **Single Worker**: Celery worker runs as a single process
   - **Mitigation**: Scale horizontally by running multiple worker instances

7. **No Email Queue Management**: Failed emails are logged but not easily retryable
   - **Mitigation**: Add admin interface to retry failed sends

8. **Database Migrations**: Manual migration execution required
   - **Mitigation**: Add automatic migration on startup (with caution)

9. **No Content Validation**: Content body is not validated for HTML/formatting
   - **Mitigation**: Add content validation and sanitization

10. **Limited Monitoring**: No built-in monitoring or alerting
    - **Mitigation**: Add health checks, metrics, and alerting

### Deployment Considerations

- **Railway Free Tier**: Limited resources - monitor usage and upgrade if needed
- **Database Backups**: Set up automated backups for production
- **Environment Variables**: Keep sensitive data (API keys) secure
- **Scaling**: Railway auto-scales, but monitor costs
- **Cold Starts**: First request after inactivity may be slow

## 📝 License

This project is part of an assignment submission.

## 🤝 Contributing

This is an assignment project. For questions or issues, please contact the repository owner.

## 📧 Contact

For questions about this service, please refer to the assignment documentation.

