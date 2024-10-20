# Library Service API

The Library Management System is a RESTful API designed to manage a library's book inventory, borrowings, users, and payments. 
The service aims to modernize library operations, enabling users to browse books, make borrowings, and payments online.

## Getting Started
These instructions will help you set up the Library Management System for development and testing purposes.

### Installation
1. Clone the repository:
   ```sh
   git clone git@github.com:OleksiukStepan/library-service-api.git
   cd library-service-api
   ```
2. Create a virtual environment and activate it:
   ```sh
   python -m venv venv
   source venv/bin/activate
   venv\Scripts\activate (on Windows)
   ```
3. Install the required dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   Create a `.env` file in the root directory and add the following variables:
   ```
   # This key dynamically changes the django configuration.
   # Should be "False" if running locally and "True" if via Docker.
   USE_DOCKER=False

   # Required settings for PostgreSQL
   POSTGRES_DB=library
   POSTGRES_USER=library
   POSTGRES_PASSWORD=library
   POSTGRES_HOST=db_library
   POSTGRES_PORT=5432
   PGDATA=/var/lib/postgresql/data

   # Django settings
   DJANGO_SECRET_KEY=your_secret_key
   DJANGO_DEBUG=True

   # 3rd party settings
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   STRIPE_API_KEY=your_stripe_secret_key
   ```

### Running with Docker
1. Build and start the services:
   ```sh
   docker-compose up --build
   ```
2. The application will be accessible at `http://localhost:8000`.

## Optionally

#### Loading Initial Data:
To load sample data:
```sh
docker exec -it <your_container_name> sh
python manage.py loaddata data.json
```

#### Creating a Superuser:
To access the admin panel, create a superuser:
```sh
docker exec -it <your_container_name> sh
python manage.py createsuperuser
```
Use the following credentials when prompted:
- Email: `user@library.com`
- Password: `user_lib_12345`

## Usage
### Authentication
The API uses JWT for authentication. You can obtain a token by sending a POST request to:
```sh
POST /api/users/token/
```

You will receive access and refresh tokens to authenticate API requests.

### Available Endpoints
- `/books/` - Manage library books (list, add, update, delete).
- `/users/` - Manage users (register, authenticate, get profile).
- `/borrowings/` - Manage book borrowings (create, list, return).
- `/payments/` - Handle payments for borrowings via Stripe.

## Features
- **JWT Authentication**: Secure access to the API using JSON Web Tokens (JWT).
- **Admin Panel**: Accessible at `/admin/` for managing the database.
- **API Documentation**: Available at `/api/v1/doc/swagger/` for easy exploration of available endpoints.
- **Book Management**: Create, read, update, and delete books in the library.
- **User Management**: Register, authenticate, and manage user profiles.
- **Borrowing Management**: Borrow and return books, with automatic inventory updates.
- **Payment System**: Integration with Stripe to handle payments for book borrowings.
- **Notifications**: Integration with Telegram to notify administrators of new borrowings and overdue books.
