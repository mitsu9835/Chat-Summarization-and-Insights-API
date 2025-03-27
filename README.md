# Task : Chat Summarization and Insights API

## Problem Description
Build a FastAPI-based REST API that processes user chat data, stores conversations in a database, and generates summaries & insights using an LLM-powered summarization model.

### The API Should Support:
- **Real-time chat ingestion**: Store raw chat messages in a database.
- **Conversation retrieval & filtering**: Retrieve chats by user, date, or keywords.
- **Chat summarization**: Generate conversation summaries using an LLM.
- **Optimization for heavy CRUD operations**: Ensure efficient query handling.

### Database Options:
- MongoDB (or any NoSQL database preferred for scalability)  
- MySQL/PostgreSQL (or any RDBMS of your choice)

### Error Handling:
- Implement proper error handling with meaningful status codes.

---

## Expected Output | API Endpoints

### 1. **Store Chat Messages (Heavy INSERT Operations)**  
- **Endpoint:** `POST /chats`  
- **Description:** Store raw chat messages into the database.

### 2. **Retrieve Chats (Heavy SELECT Operations)**  
- **Endpoint:** `GET /chats/{conversation_id}`  
- **Description:** Retrieve a specific chat conversation by its ID.

### 3. **Summarize Chat (LLM-based Summarization)**  
- **Endpoint:** `POST /chats/summarize`  
- **Description:** Generate a summary of a conversation using an LLM.

### 4. **Get User's Chat History (Pagination for Heavy Load Handling)**  
- **Endpoint:** `GET /users/{user_id}/chats?page=1&limit=10`  
- **Description:** Retrieve paginated chat history for a specific user.

### 5. **Delete Chat (Heavy DELETE Operations)**  
- **Endpoint:** `DELETE /chats/{conversation_id}`  
- **Description:** Delete a specific chat conversation by its ID.

---

## 🚀 Deployment Notes
- Deploy the API on a public server or provide a Dockerized build file.
- Store the code in a GitHub repository with clear setup instructions.

---

## ⚙️ Coding Guidelines
- **FastAPI Best Practices:** Use proper coding conventions.
- **Async Database Queries:** For scalability and non-blocking operations.
- **Indexing & Optimized Queries:** Ensure efficient SELECT operations.
- **README.md:** Include installation & usage instructions.
- **Modular Code:** Separate modules for models, routes, and services.
- **Clear Documentation:** Use docstrings and comments throughout the code.
- **LLM Interaction:** Use any LLM of your choice via APIs.

---

## 🎯 Brownie Points
- **Conversation Insights:**  
  - Sentiment analysis  
  - Keyword extraction  
  - Other insights using LLM  

- **Real-time Chat Summarization:**  
  - Use WebSockets for instant summarization.

- **Streamlit UI for Chat Interaction:**  
  - Build a simple UI using Streamlit for chat interaction.

---


# Master Plan : 

## App Overview and Objectives

The Chat Summarization and Insights API is a FastAPI-based REST service designed to process, analyze, and extract valuable insights from customer support conversations. The system ingests chat data, stores it in MongoDB, and leverages Grok API (with Gemini as a backup) to generate summaries and extract key insights.

### Primary Objectives:
- Provide a scalable API for storing and retrieving customer support conversations
- Generate concise, actionable summaries of chat conversations
- Extract valuable insights including sentiment analysis and key conversation outcomes
- Deliver a modular, maintainable codebase following Python best practices
- Support integration with third-party applications through well-documented API endpoints

## Target Audience

The primary users of this API will be developers who need to integrate customer support conversation analysis into their projects or company systems. These developers will interact with the API through HTTP endpoints rather than directly with a user interface.

## Core Features and Functionality

### 1. Chat Data Management
- Ingest chat data from various sources (initially CSV files)
- Store conversations in MongoDB with appropriate indexing
- Retrieve conversations with filtering capabilities
- Support pagination for efficient data retrieval
- Implement conversation deletion

### 2. Chat Summarization
- Generate concise summaries of entire conversations
- Extract specific elements from conversations:
  - Action items (tasks to be completed)
  - Decisions made during the conversation
  - Questions raised (both answered and unanswered)

### 3. Conversation Insights
- Sentiment analysis of conversations
- Determination of conversation outcomes (yes/no/maybe/curious)
- Keyword extraction for categorization purposes

### 4. Authentication and Security
- Implement Google/GitHub OAuth for secure API access
- Role-based access control for different API operations
- Secure handling of sensitive conversation data

### 5. Performance Optimization
- Implement database indexing for efficient queries
- Use async database operations for improved throughput
- Optimize LLM requests to balance cost and performance

## Technical Stack Recommendations

### Backend Framework
- **FastAPI**: Modern, fast web framework for building APIs with Python 3.7+
  - Pros: High performance, automatic OpenAPI documentation, native async support
  - Cons: Newer framework with smaller community compared to Flask/Django

### Database
- **MongoDB**: NoSQL database for storing chat conversations
  - Pros: Flexible schema, horizontal scalability, good performance for read/write operations
  - Cons: Less structured than SQL databases, eventual consistency model

### LLM Integration
- **Primary: Grok API**: For generating summaries and insights
  - Pros: Large context window (131K tokens), high-quality outputs
  - Cons: Potentially higher latency and cost compared to smaller models
- **Backup: Gemini API**: Alternative LLM if Grok is unavailable
  - Pros: Strong performance, potentially lower cost
  - Cons: Smaller context window than Grok

### Authentication
- **OAuth 2.0**: With Google and GitHub providers
  - Pros: Industry standard, secure, reduces password management burden
  - Cons: Dependency on third-party services

### Deployment
- **Docker**: For containerized deployment
  - Pros: Consistent environments, easier scaling, isolation
  - Cons: Additional complexity, resource overhead

## Conceptual Data Model

### Chat Message
```
{
"_id": ObjectId, // MongoDB document ID
"conversation_id": String, // Identifier for grouping messages
"message_id": String, // Unique identifier for each message
"message_content": String, // The actual chat content
"user_id": String, // Who sent the message, ex : customerX where X is the value of conversation_id
"user_type": String, // "customer" or "support_agent"
"timestamp": DateTime, // When the message was sent
}
```

### Conversation Summary
```
{
"_id": ObjectId, // MongoDB document ID
"conversation_id": String, // Reference to the conversation
"summary": String, // Overall conversation summary
"action_items": Array, // List of actions to be taken
"decisions": Array, // List of decisions made
"questions": Array, // List of questions raised
"sentiment": String, // Overall sentiment of conversation
"outcome": String, // "yes", "no", "maybe", or "curious"
"keywords": Array, // Extracted keywords
"created_at": DateTime, // When the summary was generated
"updated_at": DateTime // When the summary was last updated
}
```


### User
```
{
"_id": ObjectId, // MongoDB document ID
"email": String, // User's email address
"name": String, // User's full name
"auth_provider": String, // "google" or "github"
"provider_id": String, // ID from the auth provider
"api_key": String, // For API authentication
"role": String, // User role for access control
"created_at": DateTime, // Account creation timestamp
"last_login": DateTime // Last login timestamp
}
```


## API Endpoints

### Chat Management
- `POST /chats`: Store new chat messages
- `GET /chats/{conversation_id}`: Retrieve all messages in a conversation
- `GET /users/{user_id}/chats`: Get a user's chat history with pagination
- `DELETE /chats/{conversation_id}`: Delete a conversation

### Summarization and Insights
- `POST /chats/summarize`: Generate a summary for a conversation
- `POST /chats/insights`: Extract insights from a conversation
- `GET /chats/{conversation_id}/summary`: Retrieve an existing summary
- `GET /chats/{conversation_id}/insights`: Retrieve existing insights

### Authentication
- `GET /auth/login/google`: Initiate Google OAuth flow
- `GET /auth/login/github`: Initiate GitHub OAuth flow
- `GET /auth/callback/{provider}`: OAuth callback endpoint
- `POST /auth/token`: Generate API token
- `GET /auth/me`: Get current user information

## Project Structure
```
chat_api/
├── main.py # Application entry point
├── config/ # Configuration files
│ ├── settings.py # Application settings
│ └── logging.py # Logging configuration
├── api/ # API routes
│ ├── routes/
│ │ ├── chat.py # Chat-related endpoints
│ │ ├── summary.py # Summarization endpoints
│ │ ├── insights.py # Insights endpoints
│ │ └── auth.py # Authentication endpoints
│ ├── dependencies.py # FastAPI dependencies
│ └── middleware.py # API middleware
├── core/ # Core application logic
│ ├── security/
│ │ ├── oauth.py # OAuth implementation
│ │ └── permissions.py # Access control
│ ├── extraction/
│ │ └── extract_chats.py # Chat data extraction
│ ├── summarization/
│ │ ├── summarizer.py # Conversation summarization
│ │ └── extractors.py # Extract specific elements
│ └── insights/
│ ├── sentiment.py # Sentiment analysis
│ └── keywords.py # Keyword extraction
├── db/ # Database operations
│ ├── mongodb.py # MongoDB client
│ ├── repositories/
│ │ ├── chat_repository.py # Chat data operations
│ │ ├── summary_repository.py # Summary operations
│ │ └── user_repository.py # User operations
│ └── models/
│ ├── chat.py # Chat data models
│ ├── summary.py # Summary models
│ └── user.py # User models
├── services/ # External service integrations
│ ├── llm/
│ │ ├── grok.py # Grok API integration
│ │ └── gemini.py # Gemini API integration
│ └── auth/
│ ├── google.py # Google OAuth
│ └── github.py # GitHub OAuth
├── utils/ # Utility functions
│ ├── validators.py # Input validation
│ └── helpers.py # Helper functions
└── tests/ # Unit and integration tests
├── api/ # API tests
├── core/ # Core logic tests
└── services/ # Service integration tests
```


## Development Phases

### Phase 1: Foundation
- Set up project structure and configuration
- Implement MongoDB connection and basic repositories
- Create basic API endpoints for chat management
- Implement OAuth authentication

### Phase 2: Core Functionality
- Develop chat data extraction from CSV
- Implement LLM integration (Grok API)
- Create summarization functionality
- Build basic insights extraction

### Phase 3: Advanced Features
- Enhance summarization with action items, decisions, and questions
- Implement sentiment analysis and outcome determination
- Add keyword extraction
- Optimize database queries with proper indexing

### Phase 4: Optimization and Deployment
- Implement comprehensive error handling
- Add request validation
- Optimize LLM usage for cost efficiency
- Create Docker deployment configuration
- Write comprehensive documentation

## Performance Considerations

### Database Optimization
- Create indexes on frequently queried fields:
  - conversation_id
  - user_id
  - timestamp
- Implement database connection pooling
- Use projection to limit returned fields when appropriate

### API Performance
- Implement caching for summarization results
- Use pagination for all list endpoints
- Implement rate limiting to prevent abuse
- Consider background processing for long-running tasks

### LLM Optimization
- Batch similar requests when possible
- Cache common summarization results
- Implement fallback mechanisms for API failures
- Monitor token usage to control costs

## Security Considerations

### Authentication and Authorization
- Implement proper OAuth flows with PKCE
- Use short-lived JWT tokens for API authentication
- Implement role-based access control
- Validate all user inputs

### Data Protection
- Encrypt sensitive data at rest
- Implement proper error handling that doesn't leak information
- Set up rate limiting to prevent brute force attacks
- Regularly audit access logs

### API Security
- Implement CORS policies
- Use HTTPS for all communications
- Add request validation
- Implement proper logging for security events

## Potential Challenges and Solutions

### Challenge: Processing Large Conversations
**Solution:** Implement chunking strategies to break long conversations into manageable pieces for the LLM while maintaining context.

### Challenge: Handling High Traffic
**Solution:** Implement connection pooling, caching, and consider horizontal scaling with multiple API instances.

### Challenge: LLM Costs
**Solution:** Implement caching, optimize prompt engineering, and consider batching similar requests.

### Challenge: Accuracy of Insights
**Solution:** Implement feedback mechanisms to improve prompts over time and consider fine-tuning models for specific use cases.

## Future Expansion Possibilities

### Real-time Processing
- Implement WebSocket support for real-time chat processing
- Add streaming responses for long-running summarization tasks

### Enhanced Analytics
- Implement trend analysis across multiple conversations
- Add topic modeling to identify common issues
- Create dashboards for visualizing conversation insights

### Integration Capabilities
- Develop webhooks for real-time notifications
- Create SDKs for common programming languages
- Build integrations with popular customer support platforms

### UI Components
- Develop a Streamlit-based demo UI
- Create embeddable widgets for third-party applications
- Build an admin dashboard for managing the API

## Monitoring and Maintenance

### Logging
- Implement structured logging
- Set up log aggregation
- Create alerts for critical errors

### Metrics
- Track API response times
- Monitor database performance
- Measure LLM token usage and costs

### Health Checks
- Implement endpoint health checks
- Set up database connection monitoring
- Create LLM service availability checks
