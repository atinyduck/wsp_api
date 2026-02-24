-- init.sql

CREATE DATABASE IF NOT EXISTS WSP_System;
USE WSP_System;

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

-- Fill tables with eaxmple data

INSERT INTO Violation (Violation_Code, Violation_Description) VALUES
('SPEED0110', 'Speeding 1-10 mph over limit'),
('SPEED1120', 'Speeding 11-20 mph over limit'),
('SPEED2100', 'Speeding 21+ mph over limit'),
('DUI', 'Driving Under Influence'),
('REDLT', 'Red Light Violation'),
('PARK', 'Illegal Parking'),
('SEATB', 'Seat Belt Violation');

INSERT INTO Officer (Badge_Number, Secret_Hash, First_Name, Last_Name) VALUES
('12345', '$2b$12$NDX7j1uCyk1haIi4qI3SpOW/7QjPOBPn5aDx.QfXiza74rD9.DB7.', 'John', 'Doe'), -- Password is "johndoe"
('67890', '$2b$12$Upn5QUGbIlQpWDyN692QX.qirPZJ5AHVwBWlqevIx4czmfibYhKfe', 'Jane', 'Smith'); -- Password is "janesmith"

INSERT INTO Driver (First_Name, Last_Name, Address, Birth_Date, License_Number, License_State) VALUES
('Alice', 'Johnson', '123 Main St, Anytown, USA', '1985-06-15', 'D1234567', 'CA'),
('Bob', 'Williams', '456 Oak St, Othertown, USA', '1990-09-22', 'W7654321', 'TX');

INSERT INTO Vehicle (VIN, Make, Model, Color, License_Plate, License_State) VALUES
('1HGBH41JXMN109186', 'Honda', 'Civic', 'Blue', 'ABC1234', 'CA'),
('2FTRX18W1XCA12345', 'Ford', 'F-150', 'Red', 'XYZ5678', 'TX');

INSERT INTO Correction_Notice (Violation_Date, Violation_Time, Location, Driver_ID, Officer_ID, VIN) VALUES
('2024-01-15', '14:30:00', '5th Ave & Main St', 1, 1, '1HGBH41JXMN109186'),
('2024-02-20', '09:15:00', 'Oak St & 2nd St', 2, 2, '2FTRX18W1XCA12345');

INSERT INTO Notice_Violation (Notice_ID, Violation_Code) VALUES
(1, 'SPEED0110'),
(2, 'SEATB'),
(2, 'DUI');

-- end of init.sql