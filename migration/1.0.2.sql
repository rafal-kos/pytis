ALTER TABLE `place` ADD `country_code` VARCHAR( 12 ) NOT NULL DEFAULT 'pl' AFTER `idCompany` ;
ALTER TABLE `country` CHANGE `name` `name` VARCHAR( 200 ) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ;
ALTER TABLE `driver` ADD `employment_date` DATE NOT NULL AFTER `psychology_tests_date`;
ALTER TABLE `driver` ADD `birthday_date` DATE NOT NULL AFTER `phone`;
INSERT INTO `country`(`code`, `name`)
VALUES ('pl', 'Polska'),
('be', 'Belgia'),
('bg', 'Bułgaria'),
('cz', 'Republika Czeska'),
('dk', 'Dania'),
('de', 'Niemcy'),
('ee', 'Estonia'),
('ie', 'Irlandia'),
('el', 'Grecja'),
('es', 'Hiszpania'),
('fr', 'Francja'),
('it', 'Włochy'),
('cy', 'Cypr'),
('lv', 'Łotwa'),
('lt', 'Litwa'),
('lu', 'Luksemburg'),
('hu', 'Węgry'),
('mt', 'Malta'),
('nl', 'Niderlandy'),
('at', 'Austria'),
('pt', 'Portugalia'),
('ro', 'Rumunia'),
('si', 'Słowenia'),
('sk', 'Słowacja'),
('fi', 'Finlandia'),
('se', 'Szwecja'),
('uk', 'Zjednoczone Królestwo (Anglia)');