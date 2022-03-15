/*******************

  Cleaning script

*******************/



BEGIN TRANSCATION; 
SET CONSTRAINTS ALL DEFERRED;
DROP TABLE IF EXISTS vouchers;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS category;
DROP TABLE IF EXISTS location;
DROP TABLE IF EXISTS request;
DROP TABLE IF EXISTS loan;
END TRANSCATION; 
