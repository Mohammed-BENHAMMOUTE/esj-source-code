# ESJ Source Code

Follow these steps to run the application.

**Note:** You can use Git Bash or any terminal for the following commands.

## 1) Generate Certificates for Frontend (nginx)
   - Find and note your local IP address, such as `192.168.0.3`.
   - Create an empty `ssl` folder under the project directory.
   - Run the following command to generate SSL certificates for the frontend (nginx):
   ```bash
   mkdir ssl && openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout ssl/private_key.pem -out ssl/certificate.pem -subj "//C=US//ST=California//L=San Francisco//O=MyOrganization//OU=MyDepartment//CN=<YOUR_LOCAL_IP>"
   ```

   Replace `<YOUR_LOCAL_IP>` with your actual IP address.

## 2) Update nginx.conf

   - In the `nginx` folder, open the `nginx.conf` file.
   - Replace all instances of `<YOUR_LOCAL_IP>` with your local IP address (the same IP used in Step 1).

## 3) Generate Certificate for Backend

   Run the following command to generate a certificate for the backend:

   ```bash
   keytool -genkeypair -alias myAlias -keyalg RSA -keysize 2048 -storetype PKCS12 -keystore ./esj-backend/src/main/resources/keystore.p12 -validity 3650 -dname "CN=<YOUR_LOCAL_IP>, OU=MyOrg, O=MyCompany, L=MyCity, ST=MyState, C=US"
   ```

   - Replace `<YOUR_LOCAL_IP>` with your actual IP address.
   - Use `123456789` as the password when prompted.

   Next, export the certificate as a `.crt` file by running this command:

   ```
   keytool -export -alias myAlias -keystore ./esj-backend/src/main/resources/keystore.p12 -file backend-cert.crt
   ```

## 4) Run the Application

   Now, you can build and run the application using Docker Compose:

   ```bash
   IP_ADDRESS=<YOUR_LOCAL_IP> docker compose up --build -d
   ```

   Replace `<YOUR_LOCAL_IP>` with your actual IP address.

## 5) Accessing the Application from Other Computers

   To allow other computers to access the application:
   - Export the `backend-cert.crt` file and install it as a trusted certificate on those computers.