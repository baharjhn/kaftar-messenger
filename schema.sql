DROP DATABASE IF EXISTS Kaftar;
CREATE DATABASE Kaftar;

USE Kaftar;

CREATE TABLE KaftarUser(
	PhoneNo CHAR(11) ,
	UserName VARCHAR(255) NOT NULL,
	Bio VARCHAR(511) ,
	UserPassword VARCHAR(255),
	SelfDestruct ENUM ('3','2','1','0') ,
    PRIMARY KEY(PhoneNo)
);

CREATE TABLE UserSession(
	PhoneNo CHAR(11) NOT NULL,
	FirstAccess DATETIME,
	Device VARCHAR(255),
	LastAccess DATETIME,
	SessionIP CHAR(10) NOT NULL,
	OS VARCHAR(255),
    FOREIGN KEY (PhoneNo) REFERENCES KaftarUser (PhoneNo)
);

CREATE TABLE KaftarChannel(
	ChannelID VARCHAR(255),
	ChannelName VARCHAR(255) NOT NULL,
	ChannelLink VARCHAR(255),
	ChannelAdminPhoneNo CHAR(11) NOT NULL,
	Bio VARCHAR(511),
    PRIMARY KEY(ChannelID),
    FOREIGN KEY (ChannelAdminPhoneNo) REFERENCES KaftarUser (PhoneNo)    
);

CREATE TABLE KaftarGroup(
	GroupID VARCHAR(255) ,
	GroupName VARCHAR(255) NOT NULL,
	GroupLink VARCHAR(255),
    GroupAdminPhoneNo CHAR(11) NOT NULL,
	Bio VARCHAR(511),
    PRIMARY KEY(GroupID)
);


CREATE TABLE PVMessage(
	MessageID CHAR(10),
	ReceiverPhoneNo CHAR(11) NOT NULL, 
	SenderPhoneNo CHAR(11) NOT NULL ,
	Content VARCHAR(255) NOT NULL,
	SentTime DATETIME NOT NULL,
    PRIMARY KEY(MessageID),
    FOREIGN KEY(SenderPhoneNo) REFERENCES KaftarUser(PhoneNo),
    FOREIGN KEY(ReceiverPhoneNo) REFERENCES KaftarUser(PhoneNo)
);

CREATE TABLE GroupMessage(
	MessageID CHAR(10) NOT NULL ,
	ReceiverGroupID CHAR(10) NOT NULL,  
	SenderPhoneNo CHAR(11) NOT NULL ,
	Content VARCHAR(255) NOT NULL,
	SentTime DATETIME NOT NULL,
    PRIMARY KEY(MessageID),
    FOREIGN KEY(SenderPhoneNo) REFERENCES KaftarUser(PhoneNo),
    FOREIGN KEY(ReceiverGroupID) REFERENCES KaftarGroup(GroupID)
);

CREATE TABLE ChannelMessage(
	MessageID CHAR(10) NOT NULL,
	ReceiverChannelID CHAR(10) NOT NULL,
	SenderPhoneNo CHAR(11) NOT NULL ,
	Content VARCHAR(255) NOT NULL,
	SentTime DATETIME NOT NULL,
    PRIMARY KEY(MessageID),
    FOREIGN KEY(SenderPhoneNo) REFERENCES KaftarUser(PhoneNo),
    FOREIGN KEY(ReceiverChannelID) REFERENCES KaftarChannel(ChannelID)
);


CREATE TABLE BlockedUser (
	BlockerPhoneNo CHAR(11) NOT NULL, 
	BlockedPhoneNo CHAR(11) NOT NULL,
	BlockedDate DATE,
    FOREIGN KEY(BlockerPhoneNo) REFERENCES KaftarUser (PhoneNo),
    FOREIGN KEY(BlockedPhoneNo) REFERENCES KaftarUser (PhoneNo)
);

CREATE TABLE ChannelMembership(
	CID CHAR(10) NOT NULL, 
	UserPhoneNo CHAR(11) NOT NULL ,
	LastAccess DATETIME NOT NULL,
    FOREIGN KEY(CID) REFERENCES KaftarChannel (ChannelID),
    FOREIGN KEY(UserPhoneNo) REFERENCES KaftarUser (PhoneNo)
);

CREATE TABLE GroupMembership(
	GID CHAR(10) NOT NULL,
	UserPhoneNo CHAR(11) NOT NULL,
	LastAccess DATETIME NOT NULL,
    FOREIGN KEY (GID) REFERENCES KaftarGroup (GroupID),
    FOREIGN KEY(UserPhoneNo) REFERENCES KaftarUser (PhoneNo)
);

CREATE TABLE PVMembership(
	OwnerPhoneNo char(11) NOT NULL,
    PersonPhoneNo char(11) NOT NULL,
    LastAccess DATETIME NOT NULL
);
        

INSERT INTO KaftarUser (PhoneNo, UserName , Bio , UserPassword , SelfDestruct) VALUES ('-1','System','NULL','password','0');
