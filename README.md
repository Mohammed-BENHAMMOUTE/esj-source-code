# esj-source-code

1) **Generate certificates:** 
   - you can use git bash 
   - write your local ip address of your computer/host like `192.168.0.3` 
   - please create an empty ssl folder under the project directory

    ```
    mkdir ssl && openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout ssl/private_key.pem -out ssl/certificate.pem -subj "//C=US//ST=California//L=San Francisco//O=MyOrganization//OU=MyDepartment//CN=<YOUR_LOCAL_IP>"
    ```
2) **update nginx.conf:**$

    change `<YOUR_LOCAL_IP>` with your local ip same as step 1

```
IP_ADDRESS=192.168.11.107 docker compose up --build -d
keytool -genkeypair -alias myAlias -keyalg RSA -keysize 2048 -storetype PKCS12 -keystore keystore.p12 -validity 3650 -dname "CN=192.168.11.107, OU=MyOrg, O=MyCompany, L=MyCity, ST=MyState, C=US"
keytool -export -alias myAlias -keystore keystore.p12 -file backend-cert.crt
```