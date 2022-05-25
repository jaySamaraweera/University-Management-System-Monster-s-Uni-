USE JTKsiversity;
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS users;
CREATE TABLE users (
  uid          INT NOT NULL PRIMARY KEY,
  password     VARCHAR(50) NOT NULL,
  fname        VARCHAR(50) NOT NULL,
  lname        VARCHAR(50) NOT NULL,
  address      VARCHAR(200) NOT NULL,
  email        VARCHAR(50) NOT NULL,
  phone        VARCHAR(50) NOT NULL,
  typeuser     VARCHAR(50) NOT NULL,
  ssn          VARCHAR(50) NOT NULL UNIQUE
);

DROP TABLE IF EXISTS faculty_advisor;
CREATE TABLE faculty_advisor (
  stu_ID         INT NOT NULL,
  advisor_ID     INT NOT NULL,
  foreign key (advisor_ID) references users(uid),
  foreign key (stu_ID) references users(uid),
  PRIMARY KEY(stu_ID, advisor_ID)
);

DROP TABLE if EXISTS students;
CREATE TABLE students (
  uid              INT NOT NULL PRIMARY KEY,
  degree           VARCHAR(50) NOT NULL,
  major            VARCHAR(50) NOT NULL,
  admit_year       INTEGER NOT NULL,
  fac_advisor      INTEGER NOT NULL,
  GPA              FLOAT(3,2) NOT NULL,
  thesis           VARCHAR(256) NOT NULL,
  thesis_approval  INT(1) NOT NULL,
  grad_pending     INT(1) NOT NULL,
  FOREIGN KEY(uid) REFERENCES users(uid),
  FOREIGN KEY(fac_advisor) REFERENCES faculty_advisor(advisor_ID)
);

DROP TABLE IF EXISTS courses;
CREATE TABLE courses (
    course_id       INT NOT NULL PRIMARY KEY,
    course_dname    VARCHAR(50) NOT NULL,
    course_num      INT NOT NULL,
    course_name     VARCHAR(50) NOT NULL,
    credits         INT NOT NULL
);

DROP TABLE IF EXISTS prereqs;
CREATE TABLE prereqs (
    cid      INT NOT NULL,
    preid       INT NOT NULL,
    PRIMARY KEY(cid, preid), 
    FOREIGN KEY(cid) REFERENCES courses(course_id),
    FOREIGN KEY(preid) REFERENCES courses(course_id)
);
  
DROP TABLE IF EXISTS sects;
CREATE TABLE sects (
    sect_id     INT NOT NULL AUTO_INCREMENT,
    courseid     INT NOT NULL,
    sect_num       INT NOT NULL,
    semester      VARCHAR(50) NOT NULL,
    year         INT NOT NULL,
    day_name      VARCHAR(50) NOT NULL,
    start_time    INT NOT NULL,
    end_time      INT NOT NULL,
    prof_id       INT NOT NULL,
    PRIMARY KEY(sect_id),
    FOREIGN KEY(prof_id) REFERENCES users(uid),
    FOREIGN KEY(courseid) REFERENCES courses(course_id)
);

DROP TABLE IF EXISTS takes;
CREATE TABLE takes (
    student_id     INT NOT NULL,
    s_id        INT NOT NULL,
    grade          VARCHAR(50) NOT NULL,
    PRIMARY KEY(student_id, s_id),
    FOREIGN KEY (student_id) REFERENCES students(uid),
    FOREIGN KEY (s_id) REFERENCES sects(sect_id)
);

DROP TABLE IF EXISTS form;
CREATE TABLE form (
    form_ID     INT NOT NULL PRIMARY KEY,
    deg_type        VARCHAR(50) NOT NULL,
    form_fname          VARCHAR(50) NOT NULL
);

DROP TABLE IF EXISTS form_data;
CREATE TABLE form_data (
    form_data_ID     INT NOT NULL,
    form_dept_name        VARCHAR(50) NOT NULL,
    form_course_number          INT NOT NULL,
    FOREIGN KEY (form_data_ID) REFERENCES form(form_ID),
    PRIMARY KEY(form_data_ID, form_dept_name,form_course_number)
);

DROP TABLE IF EXISTS APPLICATION;
CREATE TABLE APPLICATION (
  AID              INTEGER not null AUTO_INCREMENT PRIMARY KEY, 
  UID              INT not null,
  SUBMITTED          int(1),
  REVIEWED         int(1),
  YEAR_SUBMITTED   int(4),
  SEMSTR_SUBMITTED int(3),
  INTERESTS         varchar(100),
  EXPERIENCE       varchar(100),
  APPLIED_DEGREE   int(3),
  GRE_VERBAL       int(3),
  GRE_QUANT        int(3),
  TOEFL_SCORE      int(3),
  TOEFL_YEAR       int(4),
  GRE_ADV_SCORE    int(3),
  GRE_ADV_SUBJ     varchar(20),
  FOREIGN KEY (SEMSTR_SUBMITTED) REFERENCES SEMESTER(num_semestr),
  FOREIGN KEY (APPLIED_DEGREE) REFERENCES DEGREE(num_degree),
  FOREIGN KEY (UID) REFERENCES users(uid)
);


DROP TABLE IF EXISTS STATUS;
CREATE TABLE STATUS (
  num_status      INTEGER not null AUTO_INCREMENT PRIMARY KEY,
  status          varchar(50) not null
);

DROP TABLE IF EXISTS APP_STATUS;
CREATE TABLE APP_STATUS (
  AID            int(3) not null PRIMARY KEY,
  app_status     int(3) not null,
  FOREIGN KEY (AID) REFERENCES APPLICATION(AID),
  FOREIGN KEY (app_status) REFERENCES STATUS(num_status)
); 
	

DROP TABLE IF EXISTS SEMESTER;
CREATE TABLE SEMESTER (
  num_semestr      INTEGER not null AUTO_INCREMENT PRIMARY KEY,
  semester         varchar(50) not null
);

DROP TABLE IF EXISTS DEGREE;
CREATE TABLE DEGREE (
  num_degree      INTEGER not null AUTO_INCREMENT PRIMARY KEY,
  degree          varchar(50) not null
);  

DROP TABLE IF EXISTS TRANSCRIPT;
CREATE TABLE TRANSCRIPT(
  UID            INT,
  SUBMITTED      int(1),
  FOREIGN KEY (UID) REFERENCES users(uid)
);
  
DROP TABLE IF EXISTS REC_LETTER_RATING;
CREATE TABLE REC_LETTER_RATING(
  UID            INT not null,
  rating         int(1),
  generic        int(1),
  credible       int(1)
);

DROP TABLE IF EXISTS REC_LETTER;
CREATE TABLE REC_LETTER(
  UID            INT,
  fname          varchar(50),
  lname          varchar(50),
  letter         varchar(1000),
  FOREIGN KEY (UID) REFERENCES APPLICATION(UID)
);

DROP TABLE IF EXISTS APPLICATION_REVIEW;
CREATE TABLE APPLICATION_REVIEW (
  reviewerID     INT,
  AID          int(3),       
  comments       varchar(100),
  deficiency     varchar(100),
  decision       int(1),
  FOREIGN KEY (decision) REFERENCES DECISION(decision_num),
  FOREIGN KEY (AID) REFERENCES APPLICATION(AID),
  FOREIGN KEY (reviewerID) REFERENCES users(uid)
);

DROP TABLE IF EXISTS DECISION;
CREATE TABLE DECISION (
  decision_num   INTEGER not null AUTO_INCREMENT PRIMARY KEY,
  decision       varchar(30)
); 

DROP TABLE IF EXISTS PRIOR_DEGREE;
CREATE TABLE PRIOR_DEGREE (
  UID            INT,	 
  prior_deg      int(3) not null,
  gpa            float(3,2),
  major          varchar(50),
  year           int(4),
  schoolname     varchar(50),
  FOREIGN KEY (UID) REFERENCES users(uid),
  FOREIGN KEY (prior_deg) REFERENCES DEGREE(num_degree)
);


SET FOREIGN_KEY_CHECKS = 1;

INSERT INTO DECISION (decision) VALUES ('Reject');
INSERT INTO DECISION (decision) VALUES ('Borderline Admit');
INSERT INTO DECISION (decision) VALUES ('Admit without aid');
INSERT INTO DECISION (decision) VALUES ('Admit with aid');

INSERT INTO SEMESTER (semester) VALUES ('FALL 2022');
INSERT INTO SEMESTER (semester) VALUES ('SPRING 2023');

INSERT INTO STATUS (status) VALUES ('Incomplete');
INSERT INTO STATUS (status) VALUES ('Under Review');
INSERT INTO STATUS (status) VALUES ('Accepted With Aid');
INSERT INTO STATUS (status) VALUES ('Accepted Without Aid');
INSERT INTO STATUS (status) VALUES ('Rejected');

INSERT INTO DEGREE (degree) VALUES ('BA/BS');
INSERT INTO DEGREE (degree) VALUES ('MS');
INSERT INTO DEGREE (degree) VALUES ('PHD');
INSERT INTO DEGREE (degree) VALUES ("");

INSERT INTO users VALUES(0,'no','thankyou','fsd','mexico city','sdf@gwu.edu','321-994-1918','advisor','111-11-9990');

INSERT INTO users VALUES(12312312,'pass','John','Lennon','800 22nd St NW, Washington, DC 20052','lennon@gwu.edu','202-994-1918','applicant','111-11-1111');
INSERT INTO users VALUES(23242820,'pass','Bhagirath','Narahari','801 22nd Street, N.W. Room 713, Washington, DC 20052','narahari@gwu.edu','202-994-8324','facultyreviewer','102-00-1991');
INSERT INTO users VALUES(23242821,'pass','Heller','Wood','801 22nd Street, N.W. Room 713, Washington, DC 20052','wood@gwu.edu','202-994-8325','facultyreviewer','102-28-2201');
INSERT INTO users VALUES(66666666,'pass','Ringo','Starr','801 22nd Street, N.W. Room 713, Washington, DC 20052','starr@gwu.edu','202-994-8322','applicant','222-11-1111');
INSERT INTO users VALUES(24242821,'pass','Bingo','Barr','801 22nd Street, N.W. Room 713, Washington, DC 20052','barr@gwu.edu','232-122-3123','gradsecretary','232-21-1111');
INSERT INTO users VALUES(29242821,'pass','Boris','Meepoy','801 22nd Street, N.W. Room 713, Washington, DC 20052','meepoy@gwu.edu','232-122-8323','cac','232-11-3111');
INSERT INTO APPLICATION VALUES(23,12312312,1,0,1992,1,'add','subtract',2,130,130,1,1980,200,'iofsdjk');
INSERT INTO TRANSCRIPT VALUES(12312312,0);
INSERT INTO users VALUES(32423432,'pass','Bagoff','Naryharry','801 22nd Street, N.W. Room 713, Washington, DC 20052','nary@gwu.edu','202-994-8328','professor','232-11-9119');

INSERT INTO users VALUES(23242818,'pass','Bhagirath','Narahari','801 22nd Street, N.W. Room 713, Washington, DC 20052','narahari@gwu.edu','202-994-8328','professor','232-81-3111');
INSERT INTO users VALUES(29182909,'pass','Joe','Biden','1600 Pennsylvania Ave NW, Washington, DC 20500','joebiden@fakeemail.com','202-647-4000','admin','552-19-1020');
INSERT INTO users VALUES(88888888,'pass','Billie','Holiday','26 West 87th Street, New York, NY 10024','billieholiday@fakeemail.com','202-675-2398','student','112-19-1020');
INSERT INTO users VALUES(99999999,'pass','Diana','Krall','2280 Armenia Rd, Chester, SC 29706','dianakrall@fakeemail.com','202-675-2245','student','112-19-343');
INSERT INTO users VALUES(23232323,'pass','Nancy','Pelosi','3111 K St NW, Washington, DC 20007','speaker@fakeemail.com','202-342-6033','gradsecretary','222-19-1020');
INSERT INTO users VALUES(23242833,'pass','Hyeong-Ah','Choi','801 22nd Street, N.W. Room 713, Washington, DC 20052','hchoi@gwu.edu','202-994-5916','professor','322-19-1020');

INSERT INTO users VALUES(23242819,'pass','Bhagirath','Narahari','801 22nd Street, N.W. Room 713, Washington, DC 20052','narahari@gwu.edu','202-994-8330','advisor','201-29-2342');
INSERT INTO users VALUES(23242919,'pass','Gabriel','Parmer','801 22nd Street, N.W. Room 713, Washington, DC 20052','parmer@gwu.edu','202-994-8330','advisor','201-29-2222');
INSERT INTO users VALUES(23243019,'pass','Poorvi','Vora','801 22nd Street, N.W. Room 713, Washington, DC 20052','parmer@gwu.edu','202-994-8330','gradsecretary','201-29-1112');
INSERT INTO users VALUES(55555555,'pass','Paul','McCartney','2280 Armenia Rd, Chester, SC 29706','McCartney@fakeemail.com','202-675-2245','student','121-19-2322');
INSERT INTO users VALUES(66666667,'pass','George','Harrison','801 22nd Street, N.W. Room 713, Washington, DC 20052','Harrison@gwu.edu','202-994-8322','student','219-11-2322');
INSERT INTO users VALUES(77777777,'pass','Eric','Clapton','801 22nd Street, N.W. Room 713, Washington, DC 20052','bingo@gwu.edu','202-994-8322','alumni','219-11-3029');
INSERT INTO users VALUES(99192090,'pass','Ringo','Starr','801 22nd Street, N.W. Room 713, Washington, DC 20052','bingo@gwu.edu','202-994-8322','student','219-11-2849');

INSERT INTO faculty_advisor VALUES ('55555555', '23242819');
INSERT INTO faculty_advisor VALUES ('66666667', '23242919');
INSERT INTO faculty_advisor VALUES ('77777777', '23242819');
INSERT INTO faculty_advisor VALUES ('99192090', '23242919');
INSERT INTO faculty_advisor VALUES ('88888888', '0');
INSERT INTO faculty_advisor VALUES ('99999999', '0');



INSERT INTO students VALUES(55555555,'MS','Computer Science', 2020, 0, 0.0, '', 0, 0);
INSERT INTO students VALUES(66666667,'MS','Computer Science', 2020, 0, 0.0, '', 0, 0);
INSERT INTO students VALUES(77777777,'MS','Computer Science', 2012, 23242819, 3.70, 'hehe', 1, 1);
INSERT INTO students VALUES(99192090,'PHD','Computer Science', 2020, 0, 0.0, 'jklfsd', 0, 0);
INSERT INTO students VALUES(88888888,'MS','Computer Science', 2020, 0, 0.0, '', 0, 0);
INSERT INTO students VALUES(99999999,'MS','Computer Science', 2020, 0, 0.0, '', 0, 0);


-- COURSES
INSERT INTO courses(course_id, course_dname, course_num, course_name, credits) VALUES (1,'CSCI',6221,'SW Paradigms',3);
INSERT INTO courses(course_id, course_dname, course_num, course_name, credits) VALUES (2,'CSCI',6461,'Computer Architecture',3);
INSERT INTO courses(course_id, course_dname, course_num, course_name, credits) VALUES (3,'CSCI',6212,'Algorithms',3);
INSERT INTO courses(course_id, course_dname, course_num, course_name, credits) VALUES (4,'CSCI',6232,'Networks 1',3);
INSERT INTO courses(course_id, course_dname, course_num, course_name, credits) VALUES (5,'CSCI',6233,'Networks 2',3);
INSERT INTO courses(course_id, course_dname, course_num, course_name, credits) VALUES (6,'CSCI',6241,'Database 1',3);
INSERT INTO courses(course_id, course_dname, course_num, course_name, credits) VALUES (7,'CSCI',6242,'Database 2',3);
INSERT INTO courses(course_id, course_dname, course_num, course_name, credits) VALUES (8,'CSCI',6246,'Compilers',3);
INSERT INTO courses(course_id, course_dname, course_num, course_name, credits) VALUES (9,'CSCI',6251,'Cloud Computing',3);
INSERT INTO courses(course_id, course_dname, course_num, course_name, credits) VALUES (11,'CSCI',6260,'Multimedia',3);
INSERT INTO courses(course_id, course_dname, course_num, course_name, credits) VALUES (12,'CSCI',6262,'Graphics 1',3);
INSERT INTO courses(course_id, course_dname, course_num, course_name, credits) VALUES (13,'CSCI',6283,'Security 1',3);
INSERT INTO courses(course_id, course_dname, course_num, course_name, credits) VALUES (14,'CSCI',6284,'Cryptography',3);
INSERT INTO courses(course_id, course_dname, course_num, course_name, credits) VALUES (15,'CSCI',6286,'Network Security',3);
INSERT INTO courses(course_id, course_dname, course_num, course_name, credits) VALUES (16,'CSCI',6384,'Cryptography 2',3);
INSERT INTO courses(course_id, course_dname, course_num, course_name, credits) VALUES (17,'ECE',6241,'Communication Theory',3);
INSERT INTO courses(course_id, course_dname, course_num, course_name, credits) VALUES (18,'ECE',6242,'Information Theory',2);
INSERT INTO courses(course_id, course_dname, course_num, course_name, credits) VALUES (19,'MATH',6210,'Logic',2);
INSERT INTO courses(course_id, course_dname, course_num, course_name, credits) VALUES (20,'CSCI',6339,'Embedded Systems',3);
INSERT INTO courses(course_id, course_dname, course_num, course_name, credits) VALUES (21,'CSCI',6220,'Machine Learning',3);
INSERT INTO courses(course_id, course_dname, course_num, course_name, credits) VALUES (22,'CSCI',6325,'Algorithms 2',3);

-- Prereq
INSERT INTO prereqs(cid, preid) VALUES(5,4);
INSERT INTO prereqs(cid, preid) VALUES(7,6);
INSERT INTO prereqs(cid, preid) VALUES(8,2);
INSERT INTO prereqs(cid, preid) VALUES(8,3);
INSERT INTO prereqs(cid, preid) VALUES(9,2);
INSERT INTO prereqs(cid, preid) VALUES(13,3);
INSERT INTO prereqs(cid, preid) VALUES(14,3);
INSERT INTO prereqs(cid, preid) VALUES(15,13);
INSERT INTO prereqs(cid, preid) VALUES(15,4);
INSERT INTO prereqs(cid, preid) VALUES(22,3);
INSERT INTO prereqs(cid, preid) VALUES(20,2);
INSERT INTO prereqs(cid, preid) VALUES(20,3);
INSERT INTO prereqs(cid, preid) VALUES(16,14);


-- Sections
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(1,1,'Spring',2022,'M',1500,1730,32423432);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(2,1,'Spring',2022,'T',1500,1730,23242818);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(3,1,'Spring',2022,'W',1500,1730,23242833);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(4,1,'Spring',2022,'M',1800,2030,32423432);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(5,1,'Spring',2022,'T',1800,2030,32423432);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(6,1,'Spring',2022,'W',1800,2030,32423432);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(7,1,'Spring',2022,'R',1800,2030,32423432);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(8,1,'Spring',2022,'T',1500,1730,32423432);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(9,1,'Spring',2022,'M',1800,2030,32423432);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(11,1,'Spring',2022,'R',1800,2030,32423432);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(12,1,'Spring',2022,'W',1800,2030,32423432);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(13,1,'Spring',2022,'T',1800,2030,32423432);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(14,1,'Spring',2022,'M',1800,2030,32423432);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(15,1,'Spring',2022,'W',1800,2030,32423432);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(16,1,'Spring',2022,'W',1500,1730,32423432);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(17,1,'Spring',2022,'M',1800,2030,32423432);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(18,1,'Spring',2022,'T',1800,2030,32423432);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(19,1,'Spring',2022,'M',1800,2030,32423432);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(20,1,'Spring',2022,'R',1600,1830,32423432);


INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(1,2,'Fall',2022,'M',1500,1730,32423432);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(2,2,'Fall',2022,'T',1500,1730,23242818);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(3,2,'Fall',2022,'W',1500,1730,23242833);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(4,2,'Fall',2022,'M',1800,2030,32423432);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(5,2,'Fall',2022,'T',1800,2030,32423432);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(6,2,'Fall',2022,'W',1800,2030,32423432);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(7,2,'Fall',2022,'R',1800,2030,32423432);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(8,2,'Fall',2022,'T',1500,1730,32423432);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(9,2,'Fall',2022,'M',1800,2030,32423432);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(11,2,'Fall',2022,'R',1800,2030,32423432);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(12,2,'Fall',2022,'W',1800,2030,32423432);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(13,2,'Fall',2022,'T',1800,2030,32423432);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(14,2,'Fall',2022,'M',1800,2030,32423432);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(15,2,'Fall',2022,'W',1800,2030,32423432);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(16,2,'Fall',2022,'W',1500,1730,32423432);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(17,2,'Fall',2022,'M',1800,2030,32423432);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(18,2,'Fall',2022,'T',1800,2030,32423432);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(19,2,'Fall',2022,'M',1800,2030,32423432);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(20,2,'Fall',2022,'R',1600,1830,32423432);

INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(1,3,'Spring',2023,'M',1500,1730,32423432);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(2,3,'Spring',2023,'T',1500,1730,23242818);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(3,3,'Spring',2023,'W',1500,1730,23242833);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(4,3,'Spring',2023,'M',1800,2030,32423432);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(5,3,'Spring',2023,'T',1800,2030,32423432);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(6,3,'Spring',2023,'W',1800,2030,32423432);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(7,3,'Spring',2023,'R',1800,2030,32423432);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(8,3,'Spring',2023,'T',1500,1730,32423432);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(9,3,'Spring',2023,'M',1800,2030,32423432);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(11,3,'Spring',2023,'R',1800,2030,32423432);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(12,3,'Spring',2023,'W',1800,2030,32423432);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(13,3,'Spring',2023,'T',1800,2030,32423432);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(14,3,'Spring',2023,'M',1800,2030,32423432);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(15,3,'Spring',2023,'W',1800,2030,32423432);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(16,3,'Spring',2023,'W',1500,1730,32423432);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(17,3,'Spring',2023,'M',1800,2030,32423432);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(18,3,'Spring',2023,'T',1800,2030,32423432);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(19,3,'Spring',2023,'M',1800,2030,32423432);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(20,3,'Spring',2023,'R',1600,1830,32423432);

INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(1,4,'Fall',2023,'M',1500,1730,32423432);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(2,4,'Fall',2023,'T',1500,1730,23242818);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(3,4,'Fall',2023,'W',1500,1730,23242833);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(4,4,'Fall',2023,'M',1800,2030,32423432);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(5,4,'Fall',2023,'T',1800,2030,32423432);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(6,4,'Fall',2023,'W',1800,2030,32423432);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(7,4,'Fall',2023,'R',1800,2030,32423432);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(8,4,'Fall',2023,'T',1500,1730,32423432);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(9,4,'Fall',2023,'M',1800,2030,32423432);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(11,4,'Fall',2023,'R',1800,2030,32423432);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(12,4,'Fall',2023,'W',1800,2030,32423432);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(13,4,'Fall',2023,'T',1800,2030,32423432);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(14,4,'Fall',2023,'M',1800,2030,32423432);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(15,4,'Fall',2023,'W',1800,2030,32423432);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(16,4,'Fall',2023,'W',1500,1730,32423432);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(17,4,'Fall',2023,'M',1800,2030,32423432);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(18,4,'Fall',2023,'T',1800,2030,32423432);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(19,4,'Fall',2023,'M',1800,2030,32423432);
INSERT INTO sects(courseid, sect_num, semester, year, day_name, start_time, end_time, prof_id) VALUES(20,4,'Fall',2023,'R',1600,1830,32423432);
-- Takes
INSERT INTO takes(student_id, s_id, grade) VALUES(88888888, 2, 'IP');
INSERT INTO takes(student_id, s_id, grade) VALUES(88888888, 3, 'IP');
INSERT INTO takes(student_id, s_id, grade) VALUES(55555555, 1, 'A');
INSERT INTO takes(student_id, s_id, grade) VALUES(55555555, 2, 'A');
INSERT INTO takes(student_id, s_id, grade) VALUES(55555555, 3, 'A');
INSERT INTO takes(student_id, s_id, grade) VALUES(55555555, 4, 'A');
INSERT INTO takes(student_id, s_id, grade) VALUES(55555555, 5, 'A');
INSERT INTO takes(student_id, s_id, grade) VALUES(55555555, 6, 'B');
INSERT INTO takes(student_id, s_id, grade) VALUES(55555555, 7, 'B');
INSERT INTO takes(student_id, s_id, grade) VALUES(55555555, 8, 'B');
INSERT INTO takes(student_id, s_id, grade) VALUES(55555555, 12, 'B');
INSERT INTO takes(student_id, s_id, grade) VALUES(55555555, 13, 'B');
INSERT INTO takes(student_id, s_id, grade) VALUES(66666667, 1, 'B');
INSERT INTO takes(student_id, s_id, grade) VALUES(66666667, 2, 'B');
INSERT INTO takes(student_id, s_id, grade) VALUES(66666667, 3, 'B');
INSERT INTO takes(student_id, s_id, grade) VALUES(66666667, 4, 'B');
INSERT INTO takes(student_id, s_id, grade) VALUES(66666667, 5, 'B');
INSERT INTO takes(student_id, s_id, grade) VALUES(66666667, 6, 'B');
INSERT INTO takes(student_id, s_id, grade) VALUES(66666667, 7, 'B');
INSERT INTO takes(student_id, s_id, grade) VALUES(66666667, 13, 'B');
INSERT INTO takes(student_id, s_id, grade) VALUES(66666667, 14, 'B');
INSERT INTO takes(student_id, s_id, grade) VALUES(66666667, 18, 'B');
INSERT INTO takes(student_id, s_id, grade) VALUES(99192090, 1, 'A');
INSERT INTO takes(student_id, s_id, grade) VALUES(99192090, 2, 'A');
INSERT INTO takes(student_id, s_id, grade) VALUES(99192090, 3, 'A');
INSERT INTO takes(student_id, s_id, grade) VALUES(99192090, 4, 'A');
INSERT INTO takes(student_id, s_id, grade) VALUES(99192090, 5, 'A');
INSERT INTO takes(student_id, s_id, grade) VALUES(99192090, 6, 'A');
INSERT INTO takes(student_id, s_id, grade) VALUES(99192090, 7, 'A');
INSERT INTO takes(student_id, s_id, grade) VALUES(99192090, 8, 'A');
INSERT INTO takes(student_id, s_id, grade) VALUES(99192090, 9, 'A');
INSERT INTO takes(student_id, s_id, grade) VALUES(99192090, 10, 'A');
INSERT INTO takes(student_id, s_id, grade) VALUES(99192090, 11, 'A');
INSERT INTO takes(student_id, s_id, grade) VALUES(99192090, 12, 'A');
INSERT INTO takes(student_id, s_id, grade) VALUES(77777777, 1, 'B');
INSERT INTO takes(student_id, s_id, grade) VALUES(77777777, 2, 'B');
INSERT INTO takes(student_id, s_id, grade) VALUES(77777777, 3, 'B');
INSERT INTO takes(student_id, s_id, grade) VALUES(77777777, 4, 'B');
INSERT INTO takes(student_id, s_id, grade) VALUES(77777777, 5, 'B');
INSERT INTO takes(student_id, s_id, grade) VALUES(77777777, 6, 'B');
INSERT INTO takes(student_id, s_id, grade) VALUES(77777777, 7, 'B');
INSERT INTO takes(student_id, s_id, grade) VALUES(77777777, 13, 'A');
INSERT INTO takes(student_id, s_id, grade) VALUES(77777777, 14, 'A');
INSERT INTO takes(student_id, s_id, grade) VALUES(77777777, 15, 'A');

