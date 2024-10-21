# Library Service API

The Library Management System is a RESTful API designed to manage a library's book inventory, borrowings, users, and payments. 
The service aims to modernize library operations, enabling users to browse books, make borrowings, and payments online.

## Getting Started
These instructions will help you set up the Library Management System for development and testing purposes.

### Local Installation
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
   ```sh
   # This key dynamically changes the django configuration.
   # Should be "False" if running locally and "True" if via Docker.
   USE_DOCKER=False

   # Required settings for PostgreSQL
   POSTGRES_DB=<your db>
   POSTGRES_USER=<your db user>
   POSTGRES_PASSWORD=<your db password>
   POSTGRES_HOST=db
   POSTGRES_PORT=5432
   PGDATA=/var/lib/postgresql/data

   # Django settings
   DJANGO_SECRET_KEY=<your Django secret key>
   DJANGO_DEBUG=True

   # 3rd party settings
   TELEGRAM_BOT_TOKEN=<your Telegram bot Token>
   STRIPE_API_KEY=<your Stripe secret key>
   ```
5. Run migrations:
   ```sh
   python manage.py migrate
   ```
6. (Optional) Load data to db:
   ```sh
   python manage.py loaddata fixtures/data.json
   ```
7. Create a superuser:
   _Note_: you can a use superuser from fixture with email `admin@admin.com` and password `admin`
   ```sh
   python manage.py createsuperuser
   ```
8. Start the server:
   ```sh
   python manage.py runserver localhost:8000
   ```

### Running with Docker
1. Build and start the services:
   ```sh
   docker-compose up --build
   ```
2. The application will be accessible at `http://localhost:8000`.

#### Optionally

To load sample data:
```sh
docker exec -it <your_container_name> sh
python manage.py loaddata fixtures/data.json
```

### Telegram Bot Integration
The Library Management System integrates with Telegram to provide real-time notifications for administrators.
In order to use it, you need to create your Telegram bot and get your bot token
1. Search for `@botfather` in Telegram.
2. Start a conversation with BotFather by clicking on the Start button.
3. Type `/newbot`, and follow the prompts to set up a new bot. The BotFather will give you a token that you need to put in your .env file.
4. Run Telegram bot:
   _Note_: Implement steps 4-7 if you run it locally.
   ```sh
   python notifications/run_telegram_bot.py
   ```
5. Create schedule instances for periodic task:
   ```sh
   python manage.py create_crontab_schedule
   ```
6. Run Celery and Celery-Beat. Notifications about overdue books are sent periodically using Celery tasks:
   ```sh
   celery -A library_service worker --loglevel=info
   celery -A library_service beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
   ```
#### Admin Access:
To start receiving notifications, an admin needs to authenticate via the Telegram bot.
1. Use `/start` to initiate the process.
2. Enter your email and password when prompted.
3. Upon successful authentication, your Telegram chat ID will be linked with your account, and you’ll start receiving notifications.

### Stripe Integration
The Library Management System uses Stripe for handling payments related to book borrowings. Users can complete payments via a secure Stripe Checkout session.
To obtain a Stripe API key, you need to follow these steps:

1. Sign up for a Stripe Account https://stripe.com/.
2. Once registered, log in to your Stripe account using your credentials.
3. After logging in, you’ll be redirected to the Stripe Dashboard. On the left-hand side menu, navigate to Developers > API keys.
4. Under the Secret Key section, click the "Reveal test key" button (if using the test environment), or get your live secret key if you are in production mode.
5. Copy the key and add it to your .env file in your project.
6. To keep track of expired Stripe payments each minute, you need to have an interval schedule:
   ```sh
   python manage.py create_interval_schedule
   ```
_Notice_: In order for task to run each minute you need to have Celery and Celery-Beat running (see step 6 in Telegram Bot Integration)

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
- **API Documentation**: Available at `api/schema/swagger-ui/` for easy exploration of available endpoints.
- **Book Management**: Create, read, update, and delete books in the library.
- **User Management**: Register, authenticate, and manage user profiles.
- **Borrowing Management**: Borrow and return books, with automatic inventory updates.
- **Payment System**: Integration with Stripe to handle payments for book borrowings. Tracking expired payments.
- **Notifications**: Integration with Telegram to notify administrators of new borrowings, overdue books and successful payments.
