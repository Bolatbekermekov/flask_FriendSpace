# Friendspace

Friendspace is a social networking platform developed using Flask, allowing users to connect, share posts, and interact with friends in a dynamic online community.

## Features

- **User Authentication:** Secure login and registration system using Flask-Login and password hashing for enhanced security.
- **Profile Customization:** Users can personalize their profiles by updating personal information, profile pictures, and bio details.
- **Post Management:** Ability to create, edit, and delete posts, facilitating a seamless content sharing experience.
- **Search Functionality:** Robust search feature enabling users to discover posts by titles and content.
- **Password Recovery:** Implemented a password recovery system for users who have forgotten their passwords.

## Technologies Used

- **Flask:** Utilized the Flask web framework to build the backend of the application.
- **SQLAlchemy:** Integrated SQLAlchemy for efficient database management and query handling.
- **Flask-Mail:** Incorporated Flask-Mail to manage and send emails for password recovery.
- **Werkzeug:** Leveraged Werkzeug for secure password hashing and file securement.
- **Bootstrap:** Used Bootstrap for frontend UI/UX design, ensuring a responsive and visually appealing interface.

## Project Structure

The project includes modules for user management, post creation, profile customization, and error handling. It also features a robust search functionality for posts.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install required packages from `requirements.txt`.

```bash
pip install -r requirements.txt
Running the Project
To run the project, use the following command:

bash
Copy code
python app.py
This project is intended to be deployed on a web server. Instructions for deployment and setup can be found in the project documentation.

Contributing
Contributions are welcome! Feel free to fork this repository, create a pull request, or open issues for any suggestions or bug reports.
