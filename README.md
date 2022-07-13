# ASALogParser
## Set of scripts to log user activity using Cisco AnyConnect VPN software

### How to use

---

#### VPN User Script
- Connects to the PostgreSQL database using psycopg2
- Parse through the VPN logs for the last 60 days and get the most recent login for each user
- Combine the list of users and logins with a listing of all service requests regarding VPN access
- If a user has not:
  - A) Logged into the VPN in the last 30 days or
  - B) Put in a ticket to request VPN access within the last 30 days
- Remove them from the appropriate access group

---

#### 
