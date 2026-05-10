-- init.sql

CREATE DATABASE IF NOT EXISTS NYPD_Citation_System;
USE NYPD_Citation_System;

-- 1. Create Driver Table
CREATE TABLE Driver (
    Driver_ID INT AUTO_INCREMENT PRIMARY KEY,
    First_Name VARCHAR(50),
    Last_Name VARCHAR(50),
    Address VARCHAR(255),
    Birth_Date DATE,
    License_Number VARCHAR(20) UNIQUE,
    License_State CHAR(2)
);

-- 2. Create Officer Table
CREATE TABLE Officer (
    Officer_ID INT AUTO_INCREMENT PRIMARY KEY,
    Badge_Number VARCHAR(20) UNIQUE,
    Secret_Hash VARCHAR(255),
    First_Name VARCHAR(50),
    Last_Name VARCHAR(50)
);

-- 3. Create Vehicle Table
CREATE TABLE Vehicle (
    VIN VARCHAR(17) PRIMARY KEY,
    Make VARCHAR(50),
    Model VARCHAR(50),
    Color VARCHAR(20),
    License_Plate VARCHAR(10),
    License_State CHAR(2)
);

-- 4. Create Correction Notice Table
CREATE TABLE Correction_Notice (
    Notice_ID INT AUTO_INCREMENT PRIMARY KEY,
    Violation_Date DATE,
    Violation_Time VARCHAR(8),
    Location VARCHAR(255),
    Driver_ID INT,
    Officer_ID INT,
    VIN VARCHAR(17),
    FOREIGN KEY (Driver_ID) REFERENCES Driver(Driver_ID),
    FOREIGN KEY (Officer_ID) REFERENCES Officer(Officer_ID),
    FOREIGN KEY (VIN) REFERENCES Vehicle(VIN)
);

-- 5. Create the Violation lookup table (The 'Catalog')
CREATE TABLE Violation (
    Violation_Code VARCHAR(10) PRIMARY KEY,
    Violation_Description VARCHAR(255)
);

-- 6. Create the Linking Table (The 'Bridge')
CREATE TABLE Notice_Violation (
    Notice_ID INT,
    Violation_Code VARCHAR(10),
    PRIMARY KEY (Notice_ID, Violation_Code),
    FOREIGN KEY (Notice_ID) REFERENCES Correction_Notice(Notice_ID) ON DELETE CASCADE,
    FOREIGN KEY (Violation_Code) REFERENCES Violation(Violation_Code)
);

-- Fill tables with example data

INSERT INTO Violation (Violation_Code, Violation_Description) VALUES
('SPEED0110', 'Speeding 1-10 mph over limit'),
('SPEED1120', 'Speeding 11-20 mph over limit'),
('SPEED2130', 'Speeding 21-30 mph over limit'),
('SPEED31', 'Speeding 31+ mph over limit'),
('REDLT', 'Running Red Light'),
('PARK', 'Illegal Parking'),
('SEATB', 'No Seatbelt'),
('RECK', 'Reckless Driving'),
('LANEC', 'Improper Lane Change'),
('REG', 'Expired Registration'),
('OTHER', 'Other Violation');

INSERT INTO Officer (Badge_Number, Secret_Hash, First_Name, Last_Name) VALUES
('B99001', '$2b$12$NDX7j1uCyk1haIi4qI3SpOW/7QjPOBPn5aDx.QfXiza74rD9.DB7.', 'Jake', 'Peralta'), -- Password is "johndoe"
('B99002', '$2b$12$Upn5QUGbIlQpWDyN692QX.qirPZJ5AHVwBWlqevIx4czmfibYhKfe', 'Amy', 'Santiago'); -- Password is "janesmith"

INSERT INTO Driver (First_Name, Last_Name, Address, Birth_Date, License_Number, License_State) VALUES
('Raymond', 'Holt', '1234 Precinct Way, Brooklyn, NY', '1955-03-21', 'NY1234567', 'NY'),
('Michael', 'Hitchcock', '5678 Duty Lane, Brooklyn, NY', '1972-08-14', 'NY7654321', 'NY'),
('Norm', 'Scully', '9101 Donut St, Brooklyn, NY', '1970-11-08', 'NY1111111', 'NY'),
('Charles', 'Boyle', '1121 Food Ave, Brooklyn, NY', '1984-07-10', 'NY2222222', 'NY');

INSERT INTO Vehicle (VIN, Make, Model, Color, License_Plate, License_State) VALUES
('2G1FB1E39D1234567', 'Chevrolet', 'Impala', 'Black', 'NYPD001', 'NY'),
('3G5DA03E32S547894', 'Cadillac', 'DeVille', 'Beige', 'WHEEL', 'NY'),
('1HGBH41JXMN109186', 'Honda', 'Civic', 'Blue', 'B99-001', 'NY'),
('2FTRX18W1XCA12345', 'Ford', 'Taurus', 'Gray', 'B99-002', 'NY');

INSERT INTO Correction_Notice (Violation_Date, Violation_Time, Location, Driver_ID, Officer_ID, VIN) VALUES
('2026-01-15', '14:30:00', '5th Ave & Main St, Brooklyn', 1, 1, '2G1FB1E39D1234567'),
('2026-02-20', '09:15:00', 'Flatbush Ave & Prospect Park, Brooklyn', 2, 2, '3G5DA03E32S547894'),
('2026-03-10', '16:45:00', 'Atlantic Ave & Classon Ave, Brooklyn', 3, 1, '1HGBH41JXMN109186'),
('2026-04-05', '11:20:00', 'Nostrand Ave & Myrtle Ave, Brooklyn', 4, 2, '2FTRX18W1XCA12345');

INSERT INTO Notice_Violation (Notice_ID, Violation_Code) VALUES
(1, 'SPEED0110'),
(2, 'REDLT'),
(3, 'PARK'),
(4, 'SEATB');

-- end of init.sql