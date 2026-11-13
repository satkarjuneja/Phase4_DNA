-- =====================================================================
-- schema.sql  --  Tower Running database (Team 42, Phase 4)
-- DBMS: MySQL 8.0+ (InnoDB, utf8mb4)
-- Run with:  mysql -u <user> -p < schema.sql
--
-- Baseline: Phase 3 of Team 29 (EER of Team 38), revised as listed in the
-- README "Design Changes" section. Revisions are tagged [REV-n] below:
--   [REV-1] Country.Country_Code added (needed for the Athlete_ID rule)
--   [REV-2] Postal_Code_Directory dropped; City kept in the address
--   [REV-3] Athlete_ID restored as primary key of Athletes;
--           Member_ID kept as UNIQUE NOT NULL FK; ON UPDATE CASCADE
--   [REV-4] Info_Part_1/2 merged into one nullable Additional_Info
--   [REV-5] TWA_Ranking re-keyed (Ranking_ID), Lat -> Last_Score,
--           Dev and Total are generated columns, Ranked_In follows
--   [REV-6] Constraints/triggers from Phase 1 Tables 3 and 4 added,
--           plus a guard that freezes Country.Country_Code
--   [REV-7] FLOAT replaced by DECIMAL for scores and points
--   [REV-8] Athletes.Email_Address and Phone_Number are NOT NULL UNIQUE
-- =====================================================================

DROP DATABASE IF EXISTS tower_running;
CREATE DATABASE tower_running
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;
USE tower_running;

-- ---------------------------------------------------------------------
-- Country
-- Country_Code is embedded in every Athlete_ID, so it is immutable
-- (enforced by trg_country_bu below).
-- ---------------------------------------------------------------------
CREATE TABLE Country (
  Country_Name VARCHAR(100) NOT NULL,
  Country_Code CHAR(3)      NOT NULL,                       -- [REV-1]
  PRIMARY KEY (Country_Name),
  UNIQUE KEY uq_country_code (Country_Code),
  CONSTRAINT ck_country_code CHECK (REGEXP_LIKE(Country_Code, '^[A-Z]{3}$', 'c'))
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Members (superclass of Athletes and Team)
-- ---------------------------------------------------------------------
CREATE TABLE Members (
  Member_ID  INT          NOT NULL AUTO_INCREMENT,
  First_Name VARCHAR(100) NOT NULL,
  Last_Name  VARCHAR(100) NOT NULL,
  PRIMARY KEY (Member_ID),
  INDEX idx_members_last_name (Last_Name)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Tour and Championship
-- ---------------------------------------------------------------------
CREATE TABLE Tour (
  `Year`    INT          NOT NULL,
  Tour_Name VARCHAR(150) NOT NULL,
  PRIMARY KEY (`Year`),
  CONSTRAINT ck_tour_year CHECK (`Year` BETWEEN 1000 AND 9999)
) ENGINE=InnoDB;

CREATE TABLE Championship (
  Name    VARCHAR(150) NOT NULL,
  `Year`  INT          NOT NULL,
  `Level` ENUM('World','Continental','National') NOT NULL,
  PRIMARY KEY (Name, `Year`),
  CONSTRAINT ck_champ_year CHECK (`Year` BETWEEN 1000 AND 9999)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Statistics (kept distinct from individual race results)
-- ---------------------------------------------------------------------
CREATE TABLE Statistics (
  Stat_ID      INT            NOT NULL AUTO_INCREMENT,
  Stat_Rank    INT UNSIGNED   NOT NULL,                     -- "Rank" is reserved in MySQL 8
  Score        DECIMAL(10,2)  NOT NULL,                     -- [REV-7]
  Country_Name VARCHAR(100)   NOT NULL,
  PRIMARY KEY (Stat_ID),
  CONSTRAINT ck_stat_rank  CHECK (Stat_Rank > 0),
  CONSTRAINT ck_stat_score CHECK (Score >= 0),
  CONSTRAINT fk_stat_country FOREIGN KEY (Country_Name)
    REFERENCES Country (Country_Name)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- TWA_Ranking  [REV-5]
-- One row per ranking entry. Previously keyed on Country alone, which
-- allowed only one row per country. "Lat" in Phase 1 was a typo for "Last".
-- Dev   = Score - Last_Score (0 when there is no previous score)
-- Total = Races + Tour_Points (as defined in Phase 1)
-- ---------------------------------------------------------------------
CREATE TABLE TWA_Ranking (
  Ranking_ID   INT           NOT NULL AUTO_INCREMENT,
  Country      VARCHAR(100)  NOT NULL,
  Ranking      INT UNSIGNED  NOT NULL,
  D_Plus_Minus VARCHAR(10)   NULL,
  Last_Score   DECIMAL(10,2) NULL,
  Score        DECIMAL(10,2) NOT NULL,
  Dev          DECIMAL(10,2) GENERATED ALWAYS AS (Score - COALESCE(Last_Score, Score)) STORED,
  Races        INT UNSIGNED  NOT NULL DEFAULT 0,
  Tour_Points  DECIMAL(10,2) NOT NULL DEFAULT 0,
  Total        DECIMAL(12,2) GENERATED ALWAYS AS (Races + Tour_Points) STORED,
  Gender       ENUM('Male','Female') NOT NULL,
  PRIMARY KEY (Ranking_ID),
  INDEX idx_ranking_gender_rank (Gender, Ranking),
  CONSTRAINT ck_rank_pos   CHECK (Ranking > 0),
  CONSTRAINT ck_rank_score CHECK (Score >= 0),
  CONSTRAINT ck_rank_last  CHECK (Last_Score IS NULL OR Last_Score >= 0),
  CONSTRAINT ck_rank_tour  CHECK (Tour_Points >= 0),
  CONSTRAINT fk_ranking_country FOREIGN KEY (Country)
    REFERENCES Country (Country_Name)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Athletes (subclass of Members)  [REV-3]
-- Athlete_ID format: 3 capital letters (country code) + 4-digit birth
-- year + M/F + 3 digits, e.g. POL1985M001.
-- Whether the ID agrees with country, birth year and gender is checked
-- by the triggers further below (needs a lookup in Country).
-- Email_Address and Phone_Number are mandatory and unique  [REV-8].
-- ---------------------------------------------------------------------
CREATE TABLE Athletes (
  Athlete_ID    VARCHAR(11)  NOT NULL,
  Member_ID     INT          NOT NULL,
  Email_Address VARCHAR(255) NOT NULL,                      -- [REV-8]
  Phone_Number  VARCHAR(20)  NOT NULL,                      -- [REV-8]
  Company_Name  VARCHAR(150) NULL,
  Date_of_Birth DATE         NOT NULL,
  Gender        ENUM('Male','Female') NOT NULL,
  Street        VARCHAR(200) NULL,
  City          VARCHAR(100) NULL,                          -- [REV-2]
  Postal_Code   VARCHAR(20)  NULL,
  Country_Name  VARCHAR(100) NOT NULL,                      -- COMPETES_FOR
  PRIMARY KEY (Athlete_ID),
  UNIQUE KEY uq_athlete_member (Member_ID),
  UNIQUE KEY uq_athlete_email  (Email_Address),
  UNIQUE KEY uq_athlete_phone  (Phone_Number),
  CONSTRAINT ck_athlete_id    CHECK (REGEXP_LIKE(Athlete_ID, '^[A-Z]{3}[0-9]{4}[MF][0-9]{3}$', 'c')),
  CONSTRAINT ck_athlete_email CHECK (Email_Address REGEXP '^[^@ ]+@[^@ ]+[.][^@ ]+$'),
  CONSTRAINT ck_athlete_phone CHECK (Phone_Number REGEXP '^[+][0-9]{7,15}$'),
  CONSTRAINT ck_athlete_dob   CHECK (Date_of_Birth > '1900-01-01'),
  CONSTRAINT fk_athlete_member FOREIGN KEY (Member_ID)
    REFERENCES Members (Member_ID)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_athlete_country FOREIGN KEY (Country_Name)
    REFERENCES Country (Country_Name)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;
-- Age is derived from Date_of_Birth and is computed in queries, not stored.

-- ---------------------------------------------------------------------
-- Team (subclass of Members)
-- ---------------------------------------------------------------------
CREATE TABLE Team (
  Member_ID    INT          NOT NULL,
  Role         ENUM('President','Sports Director','Association Representative') NOT NULL,
  Description  TEXT         NULL,
  Country_Name VARCHAR(100) NOT NULL,                       -- REPRESENTS
  PRIMARY KEY (Member_ID),
  CONSTRAINT fk_team_member FOREIGN KEY (Member_ID)
    REFERENCES Members (Member_ID)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_team_country FOREIGN KEY (Country_Name)
    REFERENCES Country (Country_Name)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE Team_Social_Media (
  Member_ID           INT          NOT NULL,
  Social_Media_Handle VARCHAR(255) NOT NULL,
  PRIMARY KEY (Member_ID, Social_Media_Handle),
  CONSTRAINT fk_tsm_team FOREIGN KEY (Member_ID)
    REFERENCES Team (Member_ID)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Venue (weak entity owned by Country via HELD_IN)
-- A country that still has venues cannot be deleted (RESTRICT).
-- ---------------------------------------------------------------------
CREATE TABLE Venue (
  Country_Name     VARCHAR(100) NOT NULL,
  Name             VARCHAR(150) NOT NULL,
  Number_of_Stairs INT UNSIGNED NOT NULL,
  Special_Info     TEXT         NULL,
  Street           VARCHAR(200) NULL,
  City             VARCHAR(100) NOT NULL,                   -- [REV-2]
  Postal_Code      VARCHAR(20)  NULL,
  PRIMARY KEY (Country_Name, Name),
  CONSTRAINT ck_venue_stairs CHECK (Number_of_Stairs > 0),
  CONSTRAINT fk_venue_country FOREIGN KEY (Country_Name)
    REFERENCES Country (Country_Name)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- News (weak entity owned by Team via WRITES)
-- ---------------------------------------------------------------------
CREATE TABLE News (
  Member_ID INT          NOT NULL,
  `Date`    DATE         NOT NULL,
  Title     VARCHAR(255) NOT NULL,
  `Text`    TEXT         NOT NULL,
  Category  VARCHAR(100) NULL,
  PRIMARY KEY (Member_ID, `Date`, Title),
  CONSTRAINT fk_news_team FOREIGN KEY (Member_ID)
    REFERENCES Team (Member_ID)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Race
-- PREVIOUS_EDITION: Previous_Race_ID is UNIQUE (1:1) and cleared, not
-- deleted, when the neighbouring edition is deleted.
-- Tour_Year/Position and Championship_* must be both set or both NULL
-- (enforced in trigger).
-- ---------------------------------------------------------------------
CREATE TABLE Race (
  Race_ID            INT          NOT NULL AUTO_INCREMENT,
  Race_Name          VARCHAR(200) NOT NULL,
  Race_Date          DATE         NOT NULL,
  Edition_Number     INT UNSIGNED NOT NULL,
  Race_Link          VARCHAR(500) NULL,
  Factor             SMALLINT UNSIGNED NOT NULL,
  Last_Factor        SMALLINT UNSIGNED NULL,
  Result_Link        VARCHAR(500) NULL,
  Result_Link_Old    VARCHAR(500) NULL,
  Category           VARCHAR(50)  NULL,
  Additional_Info    TEXT         NULL,                     -- [REV-4]
  Previous_Race_ID   INT          NULL,                     -- PREVIOUS_EDITION
  Venue_Country      VARCHAR(100) NOT NULL,                 -- HELD_AT (total)
  Venue_Name         VARCHAR(150) NOT NULL,
  Tour_Year          INT          NULL,                     -- PART_OF
  Position           INT UNSIGNED NULL,
  Championship_Name  VARCHAR(150) NULL,                     -- DESIGNATED_AS
  Championship_Year  INT          NULL,
  PRIMARY KEY (Race_ID),
  UNIQUE KEY uq_race_previous (Previous_Race_ID),
  UNIQUE KEY uq_race_tour_position (Tour_Year, Position),
  INDEX idx_race_name (Race_Name),
  INDEX idx_race_date (Race_Date),
  CONSTRAINT ck_race_edition CHECK (Edition_Number > 0),
  CONSTRAINT ck_race_factor  CHECK (Factor IN (40,60,80,120,160,200,240,280)),
  CONSTRAINT ck_race_lastfac CHECK (Last_Factor IS NULL OR Last_Factor IN (40,60,80,120,160,200,240,280)),
  CONSTRAINT ck_race_position CHECK (Position IS NULL OR Position > 0),
  CONSTRAINT fk_race_previous FOREIGN KEY (Previous_Race_ID)
    REFERENCES Race (Race_ID)
    ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT fk_race_venue FOREIGN KEY (Venue_Country, Venue_Name)
    REFERENCES Venue (Country_Name, Name)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_race_tour FOREIGN KEY (Tour_Year)
    REFERENCES Tour (`Year`)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_race_champ FOREIGN KEY (Championship_Name, Championship_Year)
    REFERENCES Championship (Name, `Year`)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE Race_Distances_Offered (
  Race_ID  INT         NOT NULL,
  Distance VARCHAR(30) NOT NULL,
  PRIMARY KEY (Race_ID, Distance),
  CONSTRAINT fk_rdo_race FOREIGN KEY (Race_ID)
    REFERENCES Race (Race_ID)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- PARTICIPATES_IN (also covers upcoming races that have no results yet)
-- ---------------------------------------------------------------------
CREATE TABLE Participates_In (
  Athlete_ID VARCHAR(11) NOT NULL,
  Race_ID    INT         NOT NULL,
  PRIMARY KEY (Athlete_ID, Race_ID),
  INDEX idx_pi_race (Race_ID),
  CONSTRAINT fk_pi_athlete FOREIGN KEY (Athlete_ID)
    REFERENCES Athletes (Athlete_ID)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_pi_race FOREIGN KEY (Race_ID)
    REFERENCES Race (Race_ID)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- RANKED_IN  [REV-5]
-- ---------------------------------------------------------------------
CREATE TABLE Ranked_In (
  Athlete_ID VARCHAR(11) NOT NULL,
  Ranking_ID INT         NOT NULL,
  PRIMARY KEY (Athlete_ID, Ranking_ID),
  INDEX idx_ri_ranking (Ranking_ID),
  CONSTRAINT fk_ri_athlete FOREIGN KEY (Athlete_ID)
    REFERENCES Athletes (Athlete_ID)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_ri_ranking FOREIGN KEY (Ranking_ID)
    REFERENCES TWA_Ranking (Ranking_ID)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Race_Result (result attributes of the athlete-race pair)
-- No two athletes share a place in one race and category.
-- Deleting a race deletes its results (ON DELETE CASCADE).
-- ---------------------------------------------------------------------
CREATE TABLE Race_Result (
  Athlete_ID  VARCHAR(11)  NOT NULL,
  Race_ID     INT          NOT NULL,
  Place       INT UNSIGNED NOT NULL,
  Finish_Time TIME(2)      NOT NULL,
  Category    VARCHAR(50)  NOT NULL,
  Points      DECIMAL(8,2) NOT NULL DEFAULT 0,              -- [REV-7]
  PRIMARY KEY (Athlete_ID, Race_ID),
  UNIQUE KEY uq_result_place (Race_ID, Category, Place),
  CONSTRAINT ck_result_place  CHECK (Place > 0),
  CONSTRAINT ck_result_points CHECK (Points >= 0),
  CONSTRAINT fk_rr_athlete FOREIGN KEY (Athlete_ID)
    REFERENCES Athletes (Athlete_ID)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_rr_race FOREIGN KEY (Race_ID)
    REFERENCES Race (Race_ID)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- APPEARED_IN (ternary: Athlete, Race, Statistics)
-- (Athlete_ID, Race_ID) must have a result. Deleting a race removes the
-- appearances but never the Statistics rows themselves.
-- ---------------------------------------------------------------------
CREATE TABLE Appeared_In (
  Athlete_ID VARCHAR(11) NOT NULL,
  Race_ID    INT         NOT NULL,
  Stat_ID    INT         NOT NULL,
  PRIMARY KEY (Athlete_ID, Race_ID, Stat_ID),
  INDEX idx_ai_stat (Stat_ID),
  CONSTRAINT fk_ai_result FOREIGN KEY (Athlete_ID, Race_ID)
    REFERENCES Race_Result (Athlete_ID, Race_ID)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_ai_stat FOREIGN KEY (Stat_ID)
    REFERENCES Statistics (Stat_ID)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- =====================================================================
-- Procedures and triggers for rules that CHECK cannot express  [REV-6]
-- =====================================================================
DELIMITER $$

-- Country: the code is embedded in Athlete_IDs, and MySQL does not fire
-- triggers for cascaded FK actions, so changing it would silently break
-- every athlete ID of that country. Forbid the change.
CREATE TRIGGER trg_country_bu BEFORE UPDATE ON Country
FOR EACH ROW
BEGIN
  IF NEW.Country_Code <> OLD.Country_Code THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Country_Code cannot change: it is embedded in Athlete_IDs';
  END IF;
END$$

-- Athlete: date of birth in the past; Athlete_ID agrees with the country
-- code, birth year and gender.
CREATE PROCEDURE chk_athlete(
  IN p_id      VARCHAR(11),
  IN p_country VARCHAR(100),
  IN p_dob     DATE,
  IN p_gender  VARCHAR(10)
)
BEGIN
  DECLARE v_code CHAR(3);

  IF p_dob >= CURDATE() THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Date_of_Birth must be in the past';
  END IF;

  SELECT Country_Code INTO v_code FROM Country WHERE Country_Name = p_country;

  IF LEFT(p_id, 3) <> v_code
     OR SUBSTRING(p_id, 4, 4) <> CAST(YEAR(p_dob) AS CHAR)
     OR SUBSTRING(p_id, 8, 1) <> IF(p_gender = 'Male', 'M', 'F') THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Athlete_ID does not match country code, birth year and gender';
  END IF;
END$$

CREATE TRIGGER trg_athletes_bi BEFORE INSERT ON Athletes
FOR EACH ROW
BEGIN
  IF EXISTS (SELECT 1 FROM Team WHERE Member_ID = NEW.Member_ID) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Member is already a Team member (disjoint specialization)';
  END IF;
  CALL chk_athlete(NEW.Athlete_ID, NEW.Country_Name, NEW.Date_of_Birth, NEW.Gender);
END$$

CREATE TRIGGER trg_athletes_bu BEFORE UPDATE ON Athletes
FOR EACH ROW
BEGIN
  CALL chk_athlete(NEW.Athlete_ID, NEW.Country_Name, NEW.Date_of_Birth, NEW.Gender);
END$$

CREATE TRIGGER trg_team_bi BEFORE INSERT ON Team
FOR EACH ROW
BEGIN
  IF EXISTS (SELECT 1 FROM Athletes WHERE Member_ID = NEW.Member_ID) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Member is already an Athlete (disjoint specialization)';
  END IF;
END$$

-- Race: previous edition must have a smaller edition number and an earlier
-- date and must not be the race itself; tour and championship columns must
-- be set together.
CREATE PROCEDURE chk_race(
  IN p_id          INT,
  IN p_prev        INT,
  IN p_edition     INT UNSIGNED,
  IN p_date        DATE,
  IN p_tour        INT,
  IN p_position    INT UNSIGNED,
  IN p_champ_name  VARCHAR(150),
  IN p_champ_year  INT
)
BEGIN
  DECLARE v_ed   INT UNSIGNED;
  DECLARE v_date DATE;

  IF p_prev IS NOT NULL THEN
    IF p_prev = p_id THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'A race cannot be its own previous edition';
    END IF;
    SELECT Edition_Number, Race_Date INTO v_ed, v_date FROM Race WHERE Race_ID = p_prev;
    IF v_ed IS NOT NULL AND NOT (v_ed < p_edition AND v_date < p_date) THEN
      SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Previous edition must have a smaller Edition_Number and an earlier date';
    END IF;
  END IF;

  IF (p_tour IS NULL) <> (p_position IS NULL) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Tour_Year and Position must both be set or both be NULL';
  END IF;

  IF (p_champ_name IS NULL) <> (p_champ_year IS NULL) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Championship_Name and Championship_Year must both be set or both be NULL';
  END IF;
END$$

CREATE TRIGGER trg_race_bi BEFORE INSERT ON Race
FOR EACH ROW
BEGIN
  CALL chk_race(NEW.Race_ID, NEW.Previous_Race_ID, NEW.Edition_Number, NEW.Race_Date,
                NEW.Tour_Year, NEW.Position, NEW.Championship_Name, NEW.Championship_Year);
END$$

CREATE TRIGGER trg_race_bu BEFORE UPDATE ON Race
FOR EACH ROW
BEGIN
  CALL chk_race(NEW.Race_ID, NEW.Previous_Race_ID, NEW.Edition_Number, NEW.Race_Date,
                NEW.Tour_Year, NEW.Position, NEW.Championship_Name, NEW.Championship_Year);
END$$

-- Results exist only for races that have already taken place.
CREATE TRIGGER trg_result_bi BEFORE INSERT ON Race_Result
FOR EACH ROW
BEGIN
  IF (SELECT Race_Date FROM Race WHERE Race_ID = NEW.Race_ID) > CURDATE() THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Results cannot be entered for a race in the future';
  END IF;
END$$

CREATE TRIGGER trg_result_bu BEFORE UPDATE ON Race_Result
FOR EACH ROW
BEGIN
  IF (SELECT Race_Date FROM Race WHERE Race_ID = NEW.Race_ID) > CURDATE() THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Results cannot be entered for a race in the future';
  END IF;
END$$

-- A result implies participation.
CREATE TRIGGER trg_result_ai AFTER INSERT ON Race_Result
FOR EACH ROW
BEGIN
  INSERT IGNORE INTO Participates_In (Athlete_ID, Race_ID) VALUES (NEW.Athlete_ID, NEW.Race_ID);
END$$

DELIMITER ;