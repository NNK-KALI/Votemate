# Votemate

Installation
------------

1. Install ganache:
   
   Arch linux `yay -S ganache-bin`

2. Start ganache > New workspace >  save workspace

3. Clone this repo
    ```
    git clone https://github.com/NNK-KALI/Votemate.git
    ```

4. Change directory to the cloned repo
    ```
    cd Votemate
    ```

5. Create a virtual environment
    ```
    python -m venv venv
    ```

6. Activate environment
    ```
    source venv/bin/activate
    ```

7. Install requirements
    ```
    pip install -r requirements.txt
    ```

8. Set environment variable:

    create a file with name `.env` and set the values

    ```
    GOOGLE_EMAIL_PASSWORD=<your-google-app-password>
    HOST_GMAIL_ADDRESS=<your-gmail-address>
    HTTP_PROVIDER=http://127.0.0.1:7545
    GANANCHE_ADMIN_ACCOUNT_INDEX=0
    DJANGO_SECRET_KEY=<your-django-secret-key>
    ```
    Inorder to send emails to the users we need a mail server. In this project I am using Google's mail service.To send a mail using django's SMTP we need to provide the credentials. so we need to create a app password(note: you need to enable 2FA before creating app password).
    
    You need to also generate django secret key [refer](https://codinggear.blog/django-generate-secret-key/)

9. Apply migrations
    ```
    python manage.py makemigrations
    python manage.py migrate
    ```

10. Create super user 
    ```
    python manage.py createsuperuser
    ```
    Enter Email and password


Running 
-------

1. Start server (note: you should be in the project directory where `manage.py` is there)
    ```
    python manage.py runserver
    ```
