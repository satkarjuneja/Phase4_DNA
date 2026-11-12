-- =====================================================================
-- populate.sql  --  Tower Running database (Team 42, Phase 4)
-- Run AFTER schema.sql:  mysql -u <user> -p < populate.sql
--
-- Source: https://www.towerrunning.com/ (race pages, news posts, team
-- page, TWA Ranking page). Collected in November 2026.
--
-- WHAT IS REAL (taken from the site)
--   * Races, dates, factors, last factors, edition numbers, result links,
--     previous-edition chains, venues (stairs/floors), championships
--   * Podium names, places and finish times (Changsha 2024, SWFC
--     Shanghai 2025, Taipei 101 Run Up 2026)
--   * Team page (Presidium / national association representatives)
--   * News titles and the facts they report (text is paraphrased)
--   * Athlete_IDs that the site prints itself: CHN1984M001 (Wenbo Zeng),
--     CHN1984M002 (Liangliang He), CHN1991M001 (Jiandong Xue),
--     HKG1986F001 (Tsz Yau Li), TPE1997M003 (Ching Chun Lo)
--
-- WHAT IS NOT PUBLIC ON THE SITE (needed because the schema says NOT NULL)
--   * Date_of_Birth (month/day), Email_Address, Phone_Number of athletes.
--     Birth YEARS are approximate where the site does not print the ID.
--     E-mails use the reserved example.org domain and phone numbers are
--     synthetic (+99...), so no real person's contact data is invented.
--   * Points for places outside the podium (the TWA scoring matrix is an
--     image/xlsx). Podium points follow the pattern visible on the site
--     (winner = factor, 2nd = 80 %, 3rd = 66.7 %). Non-podium = 0.00.
--   * TWA_Ranking rows are DERIVED from the results loaded below; they are
--     not a copy of the official monthly xlsx ranking (not machine-readable).
--
-- NOTES
--   * Taiwan uses Country_Code 'TPE' because the site's Athlete_IDs use
--     TPE (e.g. TPE1997M003), although race pages show the venue as TWN.
--   * Race 3 (SWFC 2023) -> Race 11 (SWFC 2025): the site lists the 2025
--     race with "Previous edition: 2024"; the 2024 race is not loaded, so
--     the chain jumps over it.
--   * Results triggers also insert Participates_In automatically.
-- =====================================================================

SET NAMES utf8mb4;
USE tower_running;

-- ---------------------------------------------------------------------
-- Country
-- ---------------------------------------------------------------------
INSERT INTO Country (Country_Name, Country_Code) VALUES
('Argentina',      'ARG'),
('Australia',      'AUS'),
('Austria',        'AUT'),
('Azerbaijan',     'AZE'),
('Chile',          'CHI'),
('China',          'CHN'),
('Croatia',        'CRO'),
('Czech Republic', 'CZE'),
('Estonia',        'EST'),
('Georgia',        'GEO'),
('Germany',        'GER'),
('Hong Kong',      'HKG'),
('Italy',          'ITA'),
('Japan',          'JPN'),
('Malaysia',       'MAS'),
('Mexico',         'MEX'),
('Poland',         'POL'),
('Singapore',      'SGP'),
('Slovakia',       'SVK'),
('Spain',          'ESP'),
('Switzerland',    'SUI'),
('Taiwan',         'TPE'),
('United Kingdom', 'GBR'),
('United States',  'USA');

-- ---------------------------------------------------------------------
-- Members (1-29 athletes, 30-38 team)
-- ---------------------------------------------------------------------
INSERT INTO Members (Member_ID, First_Name, Last_Name) VALUES
( 1, 'Ryoji',       'Watanabe'),
( 2, 'Wai Ching',   'Soh'),
( 3, 'Mark',        'Bourne'),
( 4, 'Fabio',       'Ruga'),
( 5, 'Piotr',       'Lobodzinski'),
( 6, 'Ching Chun',  'Lo'),
( 7, 'Sih-Ming',    'Han'),
( 8, 'Wenbo',       'Zeng'),
( 9, 'Masayuki',    'Fujita'),
(10, 'Muhammad',    'Hazim'),
(11, 'Mark',        'Ewell'),
(12, 'Eugin',       'Lee Yu Jun'),
(13, 'Jiandong',    'Xue'),
(14, 'Liangliang',  'He'),
(15, 'Tea',         'Faber'),
(16, 'Annemarie',   'Wilhelm'),
(17, 'Yuko',        'Tateishi'),
(18, 'Valentina',   'Belotti'),
(19, 'Gejun',       'Zhang'),
(20, 'Jui Chuan',   'Chao'),
(21, 'Ming',        'He'),
(22, 'Tsz Yau',     'Li'),
(23, 'Lei',         'Peng'),
(24, 'Suzy',        'Walsham'),
(25, 'Andrea',      'Mayr'),
(26, 'Cindy',       'Harris'),
(27, 'Josie',       'Riseley'),
(28, 'Serene',      'Cheong'),
(29, 'Monica',      'Carl'),
(30, 'Michael',     'Reichetzeder'),
(31, 'Tomas',       'Celko'),
(32, 'Roberto',     'Velazquez'),
(33, 'Jindrich',    'Schick'),
(34, 'Klaudio',     'Torres'),
(35, 'Priit',       'Parro'),
(36, 'Diego',       'Saenz'),
(37, 'Irakli',      'Chubinashvili'),
(38, 'Eddie',       'Tan');

-- ---------------------------------------------------------------------
-- Athletes  (Athlete_ID = country code + birth year + M/F + 3 digits)
-- ---------------------------------------------------------------------
INSERT INTO Athletes
  (Athlete_ID, Member_ID, Email_Address, Phone_Number, Company_Name,
   Date_of_Birth, Gender, Street, City, Postal_Code, Country_Name) VALUES
('JPN1989M001',  1, 'ryoji.watanabe@example.org',    '+9900000001', NULL, '1989-03-14', 'Male',   NULL, NULL, NULL, 'Japan'),
('MAS1987M001',  2, 'waiching.soh@example.org',      '+9900000002', NULL, '1987-07-21', 'Male',   NULL, NULL, NULL, 'Malaysia'),
('AUS1983M001',  3, 'mark.bourne@example.org',       '+9900000003', NULL, '1983-11-02', 'Male',   NULL, NULL, NULL, 'Australia'),
('ITA1992M001',  4, 'fabio.ruga@example.org',        '+9900000004', NULL, '1992-05-30', 'Male',   NULL, NULL, NULL, 'Italy'),
('POL1985M001',  5, 'piotr.lobodzinski@example.org', '+9900000005', NULL, '1985-09-09', 'Male',   NULL, NULL, NULL, 'Poland'),
('TPE1997M003',  6, 'chingchun.lo@example.org',      '+9900000006', NULL, '1997-01-18', 'Male',   NULL, NULL, NULL, 'Taiwan'),
('CHN1990M001',  7, 'sihming.han@example.org',       '+9900000007', NULL, '1990-10-05', 'Male',   NULL, NULL, NULL, 'China'),
('CHN1984M001',  8, 'wenbo.zeng@example.org',        '+9900000008', NULL, '1984-04-12', 'Male',   NULL, NULL, NULL, 'China'),
('JPN1988M001',  9, 'masayuki.fujita@example.org',   '+9900000009', NULL, '1988-08-25', 'Male',   NULL, NULL, NULL, 'Japan'),
('MAS1996M001', 10, 'muhammad.hazim@example.org',    '+9900000010', NULL, '1996-12-03', 'Male',   NULL, NULL, NULL, 'Malaysia'),
('USA1980M001', 11, 'mark.ewell@example.org',        '+9900000011', NULL, '1980-02-27', 'Male',   NULL, NULL, NULL, 'United States'),
('SGP1995M001', 12, 'eugin.lee@example.org',         '+9900000012', NULL, '1995-06-16', 'Male',   NULL, NULL, NULL, 'Singapore'),
('CHN1991M001', 13, 'jiandong.xue@example.org',      '+9900000013', NULL, '1991-09-28', 'Male',   NULL, NULL, NULL, 'China'),
('CHN1984M002', 14, 'liangliang.he@example.org',     '+9900000014', NULL, '1984-12-19', 'Male',   NULL, NULL, NULL, 'China'),
('CRO1993F001', 15, 'tea.faber@example.org',         '+9900000015', NULL, '1993-04-08', 'Female', NULL, NULL, NULL, 'Croatia'),
('AUT1990F001', 16, 'annemarie.wilhelm@example.org', '+9900000016', NULL, '1990-07-11', 'Female', NULL, NULL, NULL, 'Austria'),
('JPN1988F001', 17, 'yuko.tateishi@example.org',     '+9900000017', NULL, '1988-10-22', 'Female', NULL, NULL, NULL, 'Japan'),
('ITA1984F001', 18, 'valentina.belotti@example.org', '+9900000018', NULL, '1984-03-03', 'Female', NULL, NULL, NULL, 'Italy'),
('CHN1992F001', 19, 'gejun.zhang@example.org',       '+9900000019', NULL, '1992-11-14', 'Female', NULL, NULL, NULL, 'China'),
('TPE1991F001', 20, 'juichuan.chao@example.org',     '+9900000020', NULL, '1991-05-06', 'Female', NULL, NULL, NULL, 'Taiwan'),
('CHN1990F001', 21, 'ming.he@example.org',           '+9900000021', NULL, '1990-08-17', 'Female', NULL, NULL, NULL, 'China'),
('HKG1986F001', 22, 'tszyau.li@example.org',         '+9900000022', NULL, '1986-01-29', 'Female', NULL, NULL, NULL, 'Hong Kong'),
('CHN1988F001', 23, 'lei.peng@example.org',          '+9900000023', NULL, '1988-06-24', 'Female', NULL, NULL, NULL, 'China'),
('AUS1979F001', 24, 'suzy.walsham@example.org',      '+9900000024', NULL, '1979-09-15', 'Female', NULL, NULL, NULL, 'Australia'),
('AUT1979F001', 25, 'andrea.mayr@example.org',       '+9900000025', NULL, '1979-06-07', 'Female', NULL, NULL, NULL, 'Austria'),
('USA1975F001', 26, 'cindy.harris@example.org',      '+9900000026', NULL, '1975-10-10', 'Female', NULL, NULL, NULL, 'United States'),
('AUS1990F001', 27, 'josie.riseley@example.org',     '+9900000027', NULL, '1990-02-14', 'Female', NULL, NULL, NULL, 'Australia'),
('SGP1990F001', 28, 'serene.cheong@example.org',     '+9900000028', NULL, '1990-12-01', 'Female', NULL, NULL, NULL, 'Singapore'),
('GER1985F001', 29, 'monica.carl@example.org',       '+9900000029', NULL, '1985-05-20', 'Female', NULL, NULL, NULL, 'Germany');

-- ---------------------------------------------------------------------
-- Team (TWA "Our Team" page: Presidium + national association reps)
-- ---------------------------------------------------------------------
INSERT INTO Team (Member_ID, Role, Description, Country_Name) VALUES
(30, 'Sports Director',            'Presidium member; founded towerrunning.com in 2001 and represents Towerrunning Austria.', 'Austria'),
(31, 'Association Representative', 'Towerrunning Slovakia; founder and president of the Slovak association since 2014.',      'Slovakia'),
(32, 'Association Representative', 'Towerrunning Mexico.',                                                                    'Mexico'),
(33, 'Association Representative', 'Czech Towerrunning Association.',                                                         'Czech Republic'),
(34, 'Association Representative', 'Run Up Chile.',                                                                           'Chile'),
(35, 'Association Representative', 'Towerrunning Estonia.',                                                                   'Estonia'),
(36, 'Association Representative', 'Towerrunning Argentina.',                                                                 'Argentina'),
(37, 'Association Representative', 'Towerrunning Georgia.',                                                                   'Georgia'),
(38, 'Association Representative', 'Towerrunning Association of Singapore, founded in August 2020.',                          'Singapore');

INSERT INTO Team_Social_Media (Member_ID, Social_Media_Handle) VALUES
(30, 'https://www.facebook.com/TowerrunningWorldwide');

-- ---------------------------------------------------------------------
-- News (posts by the sports director)
-- ---------------------------------------------------------------------
INSERT INTO News (Member_ID, `Date`, Title, `Text`, Category) VALUES
(30, '2014-12-01', 'Register !',
 'Athletes are invited to join the worldwide ranking by registering with the TWA. The yearly fee is 24 EUR, reduced to 18 EUR for athletes aged 50+ or under 20.',
 'Uncategorized'),
(30, '2024-06-04', 'Official Pictures Towerrunning World Championships Taipei 101 Run Up May 4',
 'Official photos of the 2024 World Championships at Taipei 101 are available in a shared album. Thanks to the Taipei organizing team for the event.',
 'Announcement'),
(30, '2024-10-10', 'Monica Carl (GER) & Ryoji Watanabe (JPN) are ESBRU Champions 2024',
 'Monica Carl of Germany and Ryoji Watanabe of Japan won the 2024 Empire State Building Run Up.',
 'Race Report'),
(30, '2024-11-24', 'Valentina Belotti & Ryoji Watanabe Towerrunning Tour Champions 2024',
 'The 2024 Towerrunning Tour was decided at the final race at Shanghai Tower. Valentina Belotti and Ryoji Watanabe were crowned Tour Champions.',
 'Breaking News'),
(30, '2025-01-11', 'Tea Faber & Ryoji Watanabe winners at PingAn',
 'Tea Faber and Ryoji Watanabe won the Towerrunning 200 race at the PingAn Finance Centre in Shenzhen (3201 stairs).',
 'Top 6'),
(30, '2025-05-24', 'Top10 - Towerrunning 160 - DC Tower Run - Vienna - May 24, 2025',
 'Second edition of the DC Tower Run in Vienna, 1412 stairs to floor 58. Wai Ching Soh and Tea Faber took the wins.',
 'Top 10'),
(30, '2025-06-30', 'Towerrunning Asian & Oceanian Championships 2025',
 'Announcement of the 2025 continental championships for Asia and Oceania.',
 'Announcement'),
(30, '2025-08-07', 'Announcement - Towerrunning 60 - SKYWinD - Baku - September 28, 2025',
 'A new country joins the Towerrunning Tour: Azerbaijan, with a Towerrunning 60 race in Baku on September 28, 2025.',
 'Announcement'),
(30, '2025-10-26', 'Top3 - Towerrunning 160 - Sky Marathon SWFC - Shanghai - October 26, 2025',
 'Valentina Belotti (ITA, 18:38) and Wai Ching Soh (MAS, 15:20) are the 2025 Sky Marathon champions at the Shanghai World Financial Center.',
 'Top 3'),
(30, '2026-04-01', '25 Years of "towerrunning.com"',
 'On April 1, 2001 the domain towerrunning.com went online as a simple list of stair races. Since then it has grown into the home of a global ranking and tour.',
 'News'),
(30, '2026-05-09', 'Tea Faber & Ryoji Watanabe are 101 Champions',
 'Tea Faber (CRO, 14:07) and Ryoji Watanabe (JPN, 11:25) won the Towerrunning 200 Taipei 101 Run Up on May 9, 2026.',
 'Race Report');

-- ---------------------------------------------------------------------
-- Tours and Championships
-- ---------------------------------------------------------------------
INSERT INTO Tour (`Year`, Tour_Name) VALUES
(2021, 'Towerrunning Tour 2021'),
(2022, 'Towerrunning Tour 2022'),
(2023, 'Towerrunning Tour 2023'),
(2024, 'Towerrunning Tour 2024'),
(2025, 'Towerrunning Tour 2025'),
(2026, 'Towerrunning Tour 2026');

INSERT INTO Championship (Name, `Year`, `Level`) VALUES
('Towerrunning World Championships', 2018, 'World'),
('Towerrunning World Championships', 2024, 'World'),
('Towerrunning Asian & Oceanian Championships', 2025, 'Continental'),
('Towerrunning European Championships', 2022, 'Continental'),
('Australian Championships', 2025, 'National'),
('US Championships', 2025, 'National'),
('Singapore Championships', 2026, 'National');

-- ---------------------------------------------------------------------
-- Venues (Country_Name, Name, Number_of_Stairs, Special_Info, Street, City, Postal_Code)
-- ---------------------------------------------------------------------
INSERT INTO Venue (Country_Name, Name, Number_of_Stairs, Special_Info, Street, City, Postal_Code) VALUES
('Taiwan',        'Taipei 101',                      2046, '91 floors',                                                         NULL,              'Taipei',         NULL),
('China',         'PingAn Finance Centre',           3201, '116 floors',                                                        NULL,              'Shenzhen',       NULL),
('China',         'Shanghai World Financial Center', 2726, '100 floors',                                                        '100 Shiji Dadao', 'Shanghai',       NULL),
('China',         'Changsha IFS',                    2838, '95 floors; height difference 452 m',                                NULL,              'Changsha',       NULL),
('Austria',       'DC Tower',                        1412, 'Race goes from the lobby to floor 58. Male course record: Ryoji Watanabe (JPN) 5:47.2 (2024).', NULL, 'Vienna', NULL),
('Austria',       'Stadtturm Enns',                   157, NULL,                                                                NULL,              'Enns',           NULL),
('Germany',       'Schlosstreppe Sachsenburg',        230, NULL,                                                                NULL,              'Sachsenburg',    NULL),
('Germany',       'Testturm',                        1390, NULL,                                                                NULL,              'Rottweil',       NULL),
('Mexico',        'Asta Bandera -> Ocotlan',         1499, 'Outdoor stair trail',                                               NULL,              'Tlaxcala',       NULL),
('Malaysia',      'Komtar Tower',                    1381, '68 floors',                                                         NULL,              'Penang',         NULL),
('United States', 'Stratosphere Observation Tower',  1391, '108 floors',                                                        NULL,              'Las Vegas',      NULL),
('Switzerland',   'Stairways to Heaven',             4261, NULL,                                                                NULL,              'Ambri-Piotta',   NULL),
('Spain',         'Torre Glories',                    686, '34 floors',                                                         NULL,              'Barcelona',      NULL);

-- ---------------------------------------------------------------------
-- Races (inserted in an order that keeps Previous_Race_ID valid)
-- ---------------------------------------------------------------------
INSERT INTO Race
  (Race_ID, Race_Name, Race_Date, Edition_Number, Race_Link, Factor, Last_Factor,
   Result_Link, Result_Link_Old, Category, Additional_Info, Previous_Race_ID,
   Venue_Country, Venue_Name, Tour_Year, Position, Championship_Name, Championship_Year) VALUES
( 1, 'Taipei 101 Run Up', '2014-05-04', 10, NULL, 120, NULL,
  'http://www.taipei-101.com.tw/runup2014/perfor.asp', NULL, 'Grand Prix', 'Grand Prix of Taiwan', NULL,
  'Taiwan', 'Taipei 101', NULL, NULL, NULL, NULL),
( 2, 'Towerrunning World Championships - Taipei 101 Run Up', '2018-05-05', 14, NULL, 280, NULL,
  'https://towerrunning.com/results2018/TWAWCH18Results.xlsx', NULL, 'T', 'World Championships 2018', NULL,
  'Taiwan', 'Taipei 101', NULL, NULL, 'Towerrunning World Championships', 2018),
( 3, 'Sky Marathon SWFC', '2023-10-21', 6, 'http://www.swfc-observatory.com/', 40, NULL,
  NULL, NULL, 'R', NULL, NULL,
  'China', 'Shanghai World Financial Center', NULL, NULL, NULL, NULL),
( 4, 'Carrera Towerrunning Trail Tlaxcala', '2023-08-06', 8,
  'https://www.towerrunningmx.com/index.php/proximos-eventos/nacionales/towerrunning-trail-tlaxcala', 40, 40,
  'https://asdeporte.com/evento/carrera-towerrunning-trail-tlaxcala-2023-7ji0/resultados/1400%20Escalones', NULL, 'R', NULL, NULL,
  'Mexico', 'Asta Bandera -> Ocotlan', NULL, NULL, NULL, NULL),
( 5, 'Towerrunning World Championships - Taipei 101 Run Up', '2024-05-04', 17, NULL, 280, 280,
  NULL, 'https://towerrunning.com/results2018/TWAWCH18Results.xlsx', 'T', 'World Championships 2024', 2,
  'Taiwan', 'Taipei 101', NULL, NULL, 'Towerrunning World Championships', 2024),
( 6, 'DC Tower Run', '2024-06-08', 1, 'https://dctowerrun.com/dc-tower-run.html', 160, NULL,
  'https://time-now-sports.at/dc-towerrun-2024/', NULL, 'T', 'Towerrunning Tour', NULL,
  'Austria', 'DC Tower', 2024, 1, NULL, NULL),
( 7, 'International Vertical Marathon Open Changsha IFS Station', '2024-08-24', 4, NULL, 60, 40,
  'https://www.towerrunning.com/results2024/changshaIFS24.xlsx', 'https://www.towerrunning.com/results2023/changshaifs23.xlsx', 'R', 'Towerrunning Tour', NULL,
  'China', 'Changsha IFS', 2024, 2, NULL, NULL),
( 8, 'International Vertical Marathon PingAn', '2025-01-11', 6, NULL, 200, NULL,
  NULL, NULL, 'T', 'Towerrunning Tour', NULL,
  'China', 'PingAn Finance Centre', 2025, 1, NULL, NULL),
( 9, 'Taipei 101 Run Up', '2025-05-03', 18, NULL, 200, 280,
  'https://www.towerrunning.com/results2025/taipei2025.xlsx', NULL, 'T', 'Towerrunning Tour', 5,
  'Taiwan', 'Taipei 101', 2025, 2, NULL, NULL),
(10, 'DC Tower Run', '2025-05-24', 2, 'https://dctowerrun.com/dc-tower-run.html', 160, 160,
  'https://my.raceresult.com/305965/', 'https://my.raceresult.com/258112/#0_E9925C', 'T', 'Towerrunning Tour', 6,
  'Austria', 'DC Tower', 2025, 3, NULL, NULL),
(11, 'Sky Marathon SWFC', '2025-10-26', 7, 'https://verticalrun.saihuitong.com/m/event?id=717628', 160, 40,
  'https://www.towerrunning.com/results2025/shanghaiSWCF25.xlsx', NULL, 'T', 'Towerrunning Tour', 3,
  'China', 'Shanghai World Financial Center', 2025, 4, NULL, NULL),
(12, 'Sachsenburger Schlosstreppenlauf', '2025-04-27', 6, NULL, 40, NULL,
  NULL, NULL, 'R', NULL, NULL,
  'Germany', 'Schlosstreppe Sachsenburg', NULL, NULL, NULL, NULL),
(13, 'International Vertical Marathon PingAn', '2026-01-10', 7, NULL, 200, 200,
  'https://www.towerrunning.com/results2026/shenzhenpingan26.xlsx', 'https://nx.racetigertiming.com/live/portal?raceId=102692&partner=000001&portalId=4', 'T', 'Towerrunning Tour', 8,
  'China', 'PingAn Finance Centre', 2026, 1, NULL, NULL),
(14, 'Taipei 101 Run Up', '2026-05-09', 19, NULL, 200, 200,
  NULL, 'https://www.towerrunning.com/results2025/taipei2025.xlsx', 'T', 'Towerrunning 200 series (WFGT Towerrunning Challenge 2026, race 4)', 9,
  'Taiwan', 'Taipei 101', 2026, 2, NULL, NULL),
(15, 'DC Tower Run', '2026-05-29', 3, 'https://dctowerrun.com/dc-tower-run.html', 160, 160,
  NULL, NULL, 'T', 'Towerrunning Tour', 10,
  'Austria', 'DC Tower', 2026, 3, NULL, NULL);

INSERT INTO Race_Distances_Offered (Race_ID, Distance) VALUES
( 1, '2046 stairs'),
( 2, '2046 stairs'),
( 4, '1499 stairs'),
( 5, '2046 stairs'),
( 6, '1412 stairs'),
( 7, '2838 stairs'),
( 8, '3201 stairs'),
( 9, '2046 stairs'),
(10, '1412 stairs'),
(11, '2726 stairs'),
(12, '230 stairs'),
(13, '3201 stairs'),
(14, '2046 stairs'),
(15, '1412 stairs');

-- ---------------------------------------------------------------------
-- Race_Result  (the AFTER INSERT trigger also fills Participates_In)
-- ---------------------------------------------------------------------
INSERT INTO Race_Result (Athlete_ID, Race_ID, Place, Finish_Time, Category, Points) VALUES
-- Race 7: Changsha IFS, 2024-08-24 (factor 60)
('CHN1990M001',  7, 1, '00:17:08.00', 'Men Open',   60.00),
('CHN1984M001',  7, 2, '00:17:37.00', 'Men Open',   48.00),
('TPE1997M003',  7, 3, '00:18:33.00', 'Men Open',   40.00),
('CHN1990F001',  7, 1, '00:22:35.00', 'Women Open', 60.00),
('HKG1986F001',  7, 2, '00:22:46.00', 'Women Open', 48.00),
('CHN1988F001',  7, 3, '00:24:08.00', 'Women Open', 40.00),
-- Race 11: Sky Marathon SWFC Shanghai, 2025-10-26 (factor 160)
('MAS1987M001', 11, 1, '00:15:20.00', 'Men Open',  160.00),
('AUS1983M001', 11, 2, '00:15:31.00', 'Men Open',  128.00),
('JPN1989M001', 11, 3, '00:15:32.00', 'Men Open',  106.67),
('ITA1984F001', 11, 1, '00:18:38.00', 'Women Open', 160.00),
('JPN1988F001', 11, 2, '00:19:46.00', 'Women Open', 128.00),
('CHN1992F001', 11, 3, '00:20:04.00', 'Women Open', 106.67),
-- Race 14: Taipei 101 Run Up, 2026-05-09 (factor 200)
('JPN1989M001', 14, 1, '00:11:25.00', 'Men Open',  200.00),
('ITA1992M001', 14, 2, '00:11:31.00', 'Men Open',  160.00),
('AUS1983M001', 14, 3, '00:11:37.00', 'Men Open',  133.33),
('CRO1993F001', 14, 1, '00:14:07.00', 'Women Open', 200.00),
('AUT1990F001', 14, 2, '00:14:14.00', 'Women Open', 160.00),
('JPN1988F001', 14, 3, '00:14:29.00', 'Women Open', 133.33),
('TPE1991F001', 14, 6, '00:14:56.00', 'Women Open',   0.00);

-- ---------------------------------------------------------------------
-- Participates_In: entries without a time in the table above
-- (winners named on the site, no finish times available)
-- ---------------------------------------------------------------------
INSERT IGNORE INTO Participates_In (Athlete_ID, Race_ID) VALUES
('POL1985M001',  2),   -- 2018 World Champion (men)
('AUS1979F001',  2),   -- 2018 World Champion (women)
('ITA1984F001',  5),   -- 2024 World Champion (women)
('MAS1987M001',  5),   -- 2024 World Champion (men)
('JPN1989M001',  6),   -- DC Tower Run 2024, male course record
('CRO1993F001',  8),
('JPN1989M001',  8),
('JPN1989M001',  9),
('MAS1987M001', 10),
('CRO1993F001', 10),
('MAS1987M001', 13),
('CRO1993F001', 13);

-- ---------------------------------------------------------------------
-- TWA_Ranking: derived from the Race_Result rows above
-- Score = sum of points, Races = number of results, Tour_Points = points
-- from Tour races (all loaded results come from Tour-listed races).
-- Last_Score = score before the athlete's most recent result (only where
-- the athlete has two results). Ties share a Ranking.
-- ---------------------------------------------------------------------
INSERT INTO TWA_Ranking
  (Ranking_ID, Country, Ranking, D_Plus_Minus, Last_Score, Score, Races, Tour_Points, Gender) VALUES
( 1, 'Japan',     1, NULL, 106.67, 306.67, 2, 306.67, 'Male'),
( 2, 'Australia', 2, NULL, 128.00, 261.33, 2, 261.33, 'Male'),
( 3, 'Malaysia',  3, NULL, NULL,   160.00, 1, 160.00, 'Male'),
( 4, 'Italy',     3, NULL, NULL,   160.00, 1, 160.00, 'Male'),
( 5, 'China',     5, NULL, NULL,    60.00, 1,  60.00, 'Male'),
( 6, 'China',     6, NULL, NULL,    48.00, 1,  48.00, 'Male'),
( 7, 'Taiwan',    7, NULL, NULL,    40.00, 1,  40.00, 'Male'),
( 8, 'Japan',     1, NULL, 128.00, 261.33, 2, 261.33, 'Female'),
( 9, 'Croatia',   2, NULL, NULL,   200.00, 1, 200.00, 'Female'),
(10, 'Italy',     3, NULL, NULL,   160.00, 1, 160.00, 'Female'),
(11, 'Austria',   3, NULL, NULL,   160.00, 1, 160.00, 'Female'),
(12, 'China',     5, NULL, NULL,   106.67, 1, 106.67, 'Female'),
(13, 'China',     6, NULL, NULL,    60.00, 1,  60.00, 'Female'),
(14, 'Hong Kong', 7, NULL, NULL,    48.00, 1,  48.00, 'Female'),
(15, 'China',     8, NULL, NULL,    40.00, 1,  40.00, 'Female'),
(16, 'Taiwan',    9, NULL, NULL,     0.00, 1,   0.00, 'Female');

INSERT INTO Ranked_In (Athlete_ID, Ranking_ID) VALUES
('JPN1989M001',  1),
('AUS1983M001',  2),
('MAS1987M001',  3),
('ITA1992M001',  4),
('CHN1990M001',  5),
('CHN1984M001',  6),
('TPE1997M003',  7),
('JPN1988F001',  8),
('CRO1993F001',  9),
('ITA1984F001', 10),
('AUT1990F001', 11),
('CHN1992F001', 12),
('CHN1990F001', 13),
('HKG1986F001', 14),
('CHN1988F001', 15),
('TPE1991F001', 16);

-- ---------------------------------------------------------------------
-- Statistics: country totals computed from the loaded results, and the
-- APPEARED_IN rows that tie every result to its country's statistic.
-- ---------------------------------------------------------------------
INSERT INTO Statistics (Stat_Rank, Score, Country_Name)
SELECT RANK() OVER (ORDER BY SUM(rr.Points) DESC),
       SUM(rr.Points),
       a.Country_Name
FROM Race_Result rr
JOIN Athletes a ON a.Athlete_ID = rr.Athlete_ID
GROUP BY a.Country_Name;

INSERT INTO Appeared_In (Athlete_ID, Race_ID, Stat_ID)
SELECT rr.Athlete_ID, rr.Race_ID, s.Stat_ID
FROM Race_Result rr
JOIN Athletes   a ON a.Athlete_ID   = rr.Athlete_ID
JOIN Statistics s ON s.Country_Name = a.Country_Name;

-- =====================================================================
-- Quick sanity checks (optional):
--   SELECT COUNT(*) FROM Race_Result;      -- 19
--   SELECT COUNT(*) FROM Race;             -- 15
--   SELECT COUNT(*) FROM Athletes;         -- 29
--   SELECT * FROM Statistics ORDER BY Stat_Rank;
-- =====================================================================