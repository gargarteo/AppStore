/*******************

  Create the schema

********************/
CREATE TABLE users (
name VARCHAR(64) NOT NULL, 
school_email VARCHAR(64) PRIMARY KEY CHECK (school_email LIKE '%@u.nus.edu'), 
current_borrowed_items INT CHECK(current_borrowed_items<= 2) NOT NULL DEFAULT 0.00,
demerit_points INT NOT NULL CHECK(demerit_points<= 8) DEFAULT 0.00,
vouchers_points INT NOT NULL DEFAULT 0.00,
max_request INT NOT NULL DEFAULT 2.00,
password VARCHAR(64) NOT NULL,
suspend BOOLEAN DEFAULT FALSE,
CHECK (users.current_borrowed_items <= users.max_request),
CHECK (LENGTH(users.password) >= 6)
);

CREATE TABLE category (
category VARCHAR(64) PRIMARY KEY UNIQUE
);

CREATE TABLE location (
location VARCHAR(64) PRIMARY KEY UNIQUE
);

CREATE TABLE requests (
request_id SERIAL PRIMARY KEY,
item VARCHAR(64) NOT NULL,
loaner VARCHAR(64) REFERENCES users(school_email) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
category VARCHAR(64) NOT NULL,
date_needed DATE NOT NULL,
time_needed TIME NOT NULL,
return_date DATE NOT NULL,
return_time TIME NOT NULL,
meetup_location VARCHAR(64),
accepted BOOLEAN DEFAULT false
);



CREATE TABLE loan (
request_id INT PRIMARY KEY REFERENCES requests(request_id) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
borrower VARCHAR(64) NOT NULL REFERENCES users(school_email),
owner VARCHAR(64) NOT NULL REFERENCES users(school_email),
item VARCHAR(64) NOT NULL,
date_borrowed DATE NOT NULL,
return_deadline DATE,
returned_date DATE
);


CREATE TABLE vouchers(
voucher_id VARCHAR(64) PRIMARY KEY,
voucher_name VARCHAR(64) NOT NULL,
merchant_name VARCHAR(64) NOT NULL,
voucher_value INTEGER NOT NULL,
points_required NUMERIC,
used BOOLEAN NOT NULL DEFAULT FALSE,
owner_of_voucher VARCHAR(64) references users(school_email));
