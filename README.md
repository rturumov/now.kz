# 📰 Now.kz — News Portal of Kazakhstan

## Project Overview

Now.kz is a news portal built with Django.  
Users can read news articles, leave comments, and authors can publish their own materials.  
The project is based on a modular architecture and uses abstract models for scalability and clean code.


## How to Run the Project

### Requirements

Make sure you have installed:
- Python 3.10 or higher
- pip
- virtualenv (optional but recommended)

### Setup Steps

1. Clone the repository:

    ```
    git clone <repository-url>
    ```

2. Create and activate a virtual environment:

    ```
    python -m venv venv
    source venv/bin/activate      # macOS/Linux  
    venv\Scripts\activate         # Windows
    ```

3. Install dependencies:

    ```
    pip install -r requirements/local.txt
    ```

4. Apply database migrations:

    ```
    python manage.py migrate
    ```

5. Create a superuser

    ```
    python manage.py createsuperuser
    ```

6. Run the development server

    ```
    python manage.py runserver
    ```

7. Follow the link: `http://127.0.0.1:8000/`

## 📦 Apps and Models

### 1. abstracts  
Contains abstract models reused in other applications.  
- AbstractBaseModel — base model with fields created_at, updated_at, and is_deleted.

---

### 2. accounts  
Handles user and author management.  
- User — user model (login, email, bio, avatar).  
- Author — author profile linked to a user (one-to-one relationship).

---

### 3. news  
Stores all data related to news content.  
- Category — news category (e.g., Politics, Sports, Technology).  
- News — news article (title, content, image, category, author, publish date).

---

### 4. comments  
Manages user comments on news articles.  
- Comment — comment made by a user, supports threaded replies.

---

### 5. contacts  
Handles messages sent via the contact form.  
- ContactMessage — message from a user (name, email, subject, message text, read status).

---

## 🗂️ Database Schema

![Database Schema](dbScheme.png)    