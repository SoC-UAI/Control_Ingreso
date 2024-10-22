# Access Control Application for Security and Research Lab (SoC) - Adolfo Ibáñez University, Viña del Mar

## Overview

This application manages the access control of the Security and Research Lab at Adolfo Ibáñez University in Viña del Mar. It displays the current students present in the lab on a screen connected to a Raspberry Pi 4, which is set up to use a TV for display. The application also generates a QR code to facilitate easy access for students to log in or out through an online form.

The system aims to streamline the lab's attendance monitoring process, ensuring that everyone who enters or leaves is registered accordingly.

## Features

- **Attendance Display**: Shows the list of students currently inside the lab, highlighting tutors.
- **Login/Logout System**: Uses an online form accessible via QR code to register entry and exit.
- **Records Management**: Keeps track of attendance records and allows administrators to view them securely.

## Operation

1. **Login/Logout Process**: The login/logout form can be accessed via the displayed QR code on the lab's TV screen. Users must select their name, choose either "Entrada" (Entry) or "Salida" (Exit), and input a password to confirm their action.

2. **Dashboard Display**: The TV shows the list of students in the lab, dynamically updated every few seconds. Students identified as tutors are highlighted for distinction.

3. **Records**: Administrators can access detailed records of lab attendance, including the name, action (entry/exit), and timestamp.

## Project Structure

- **Backend**: Powered by Flask, managing form submission, attendance updates, and data retrieval.
- **Frontend**: HTML pages serve different purposes:
  - [`index.html`](index.html): Main display page showing students present in the lab. Refreshes every 600 seconds.
  - [`login.html`](login.html): Login/logout form for students to register their entry or exit.
  - [`records.html`](records.html): Shows the full list of entries and exits for administrative purposes.
  - [`home.html`](home.html): Acts as the homepage with navigation options for registering entry/exit and viewing records.

## Requirements

The project was developed in Python 3.11 and it's dependencies are listed in [`requirements.txt`](requirements.txt):

```
Flask==2.2.5
qrcode[pil]==7.3.1
google-api-python-client==2.39.0
google-auth==2.6.6
google-auth-oauthlib==0.4.6
google-auth-httplib2==0.1.0
requests==2.32.2
werkzeug==3.0.3
schedule==1.2.2
python-dotenv==1.0.1
```

To install them, run:

```bash
pip install -r requirements.txt
```
after cloning the project.

## Setup Instructions
### Raspberry / TV Setup

1. **Hardware Setup**: Connect a TV to the Raspberry Pi using an HDMI cable.

2. **Cloning the Project**: Clone this repository to the Raspberry Pi:

   ```bash
   git clone <repository-url>
   cd <repository-folder>
   ```

3. **Environment Variables**: Create a `.env` file for Google API credentials and set up the necessary environmental variables, such as `CLIENT_ID`, `CLIENT_SECRET`, etc. Use the `xxxxxxxx-yyyyyyyyyy.json` for the appropriate service account credentials. The should be generated using [Google Cloud Platform](https://console.cloud.google.com/).

4. **Running the Application**: Start the Flask server:

   ```bash
   python ingresos.py
   ```

   The app will be accessible at `http://<raspberry-pi-ip>:5001`. You can change the port modifying the value on the Python code.

5. **Display Configuration**: Set up the Raspberry Pi to automatically open a browser in fullscreen mode to `http://localhost:5001` upon boot. This ensures the student presence screen is always visible.

## Usage

1. **Student Entry/Exit**: Students use the QR code displayed on the TV screen to access the form [`login.html`](login.html). They must select their name, action (entry or exit), and provide the password to confirm their entry or exit.

2. **Viewing Records**: Administrators can view the complete list of attendance records [`records.html`](records.html) by entering an administrative password.

## File Descriptions

- **`index.html`**: Displays the current students in the lab along with a QR code for easy login/logout.
- **`login.html`**: Form for students to log in or out. Password-protected.
- **`records.html`**: Displays all attendance records. Password-protected for admin use.
- **`home.html`**: Homepage providing access to login/logout and records viewing.
- **`xxxxxxxx-yyyyyyyyyy.json`**: Service account credentials for Google API access.
- **`registros.json`**: Contains attendance records, including the name, action, and timestamp.
- **`requirements.txt`**: Lists all necessary packages for the application.

### Web Setup

For the public web section of this app, the site was deployed to [PythonAnywhere](https://www.pythonanywhere.com/) since it fits the needs of this project. You can choose any host you like, but these instructions are based on this platform and no other is mantained here at the moment.

1. Create an account and create a Web App using `Flask`, `Python 3.10` and change the name of the main file of the app to `ingresos.py` when prompted.

2. Go to the Files section, and inside the `mysite/` directory upload the contents inside the [`WEB`](/WEB/) folder. Be sure to mantain the order of the files, keeping the structure of the `static/` and `templates/` folders and it's contents.
   Inside the `<your_username>/` folder, along with `mysite/` put the `xxxxxxxx-yyyyyyyyyy.json` file with the credentials for Google API.

3. Open a Bash Console on PythonAnywhere, and install the requirement:

   ```bash
   pip install gspread
   ```
   Then make sure to close the console by typing `exit`.

4. Go to the Web tab again, enable `Force HTTPS` under the Security section, and restart the app.

5. You are now good to go! By default, your site is live at `https://<your_username>.pythonanywhere.com/`.

## Development Notes

- **Google API Integration**: The application uses Google APIs for secure record handling and potential data export.
- **Auto Refresh**: The student list on the screen refreshes every 3 seconds for real-time updates.
- **Styling**: Custom styles and JavaScript (such as `particles.js`) are used to provide a visually appealing interface.

## Future Improvements

- **RFID Integration**: Add RFID scanning for quicker entry/exit registration.
- **Notification System**: Send notifications to students or admins when predefined conditions are met (e.g., overcrowding).

## Contributors

- Sebastián Dinator - Developer and Maintainer

Feel free to contribute by forking the repository and submitting pull requests.

## License

This project is licensed under the GNU GPLv3 License.
