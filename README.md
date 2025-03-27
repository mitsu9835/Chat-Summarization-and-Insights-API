# Chat Summarization and Insights API

A FastAPI-based REST API that processes user chat data, stores conversations in MongoDB, and generates summaries & insights using LLM technologies.

## Features

- **Real-time chat ingestion**: Store raw chat messages in MongoDB
- **Conversation retrieval & filtering**: Retrieve chats by user, date, or keywords
- **Chat summarization**: Generate conversation summaries using LLM
- **Conversation insights**: Extract action items, decisions, questions, and sentiment
- **Optimized for heavy CRUD operations**: Efficient query handling with proper indexing

## Tech Stack

- **FastAPI**: Modern, fast web framework
- **MongoDB**: NoSQL database for storing conversations
- **Motor**: Async MongoDB driver
- ** 