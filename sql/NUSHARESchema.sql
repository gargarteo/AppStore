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
password VARCHAR(64) NOT NULL CHECK ((LENGTH(password) > 5) and (LENGTH(password) < 13)),
suspend BOOLEAN DEFAULT FALSE,
CHECK (users.current_borrowed_items <= users.max_request)
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
return_date DATE NOT NULL CHECK(date_needed < return_date),
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
returned_date DATE,
days_overdue INT DEFAULT 0.00
);
CREATE TABLE vouchers(
voucher_id SERIAL PRIMARY KEY,
voucher_name VARCHAR(64) NOT NULL,
merchant_name VARCHAR(64) NOT NULL,
voucher_value INTEGER NOT NULL,
used BOOLEAN NOT NULL DEFAULT FALSE,
owner_of_voucher VARCHAR(64) references users(school_email));




CREATE TABLE vouch (
voucher_name VARCHAR(64) NOT NULL PRIMARY KEY,
merchant_name VARCHAR(64) NOT NULL,
voucher_value INTEGER NOT NULL CHECK (voucher_value >0),
points_required INTEGER NOT NULL CHECK(points_required >0)
);


