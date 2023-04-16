CREATE TABLE student (
	username VARCHAR(255),
	password VARCHAR(32),
	subject VARCHAR(255),
	email VARCHAR(255),
	address VARCHAR(255),
	PRIMARY KEY (username)
);

CREATE TABLE teacher (
	username VARCHAR(255),
	password VARCHAR(32),
	subject VARCHAR(255),
	email VARCHAR(255),
	PRIMARY KEY (username)
);

CREATE TABLE donator (
	username VARCHAR(255),
	password VARCHAR(32),
	email VARCHAR(255),
	PRIMARY KEY (username)
);

CREATE TABLE donation (
	id VARCHAR(10),
	title VARCHAR(255),
	username VARCHAR(255),
	description TEXT,
	subject VARCHAR(255),
	PRIMARY KEY(id),
	FOREIGN KEY (username) REFERENCES donator(username)
);