ALTER TABLE `truck` CHANGE `oc_ac_validity_date` `oc_validity_date` DATE NOT NULL ;
ALTER TABLE `semitrailer` CHANGE `oc_ac_validity_date` `oc_validity_date` DATE NOT NULL ;
ALTER TABLE `semitrailer` ADD `ac_validity_date` DATE NOT NULL AFTER `oc_validity_date` ;
ALTER TABLE `truck` ADD `ac_validity_date` DATE NOT NULL AFTER `oc_validity_date` ;

INSERT INTO `dictionary`(`key`, `value`, `kind`, `enabled`) VALUES ('TRUCK_MODEL', 'SCANIA', 0, 1), 
('TRUCK_MODEL', 'VOLVO', 0, 1), 
('TRUCK_MODEL', 'RENAULT', 0, 1), 
('TRUCK_MODEL', 'IVECO', 0, 1), 
('TRUCK_MODEL', 'MERCEDES BENZ', 0, 1), 
('TRUCK_MODEL', 'DAF', 0, 1), 
('TRUCK_MODEL', 'MAN', 0, 1), 
('TRUCK_MODEL', 'NISSAN', 0, 1), 
('TRUCK_MODEL', 'FORD', 0, 1), 
('TRUCK_MODEL', 'AVIA', 0, 1), 
('TRUCK_MODEL', 'VOLKSWAGEN', 0, 1), 
('TRUCK_MODEL', 'MAZ', 0, 1), 
('TRUCK_MODEL', 'GINAF', 0, 1), 
('TRUCK_MODEL', 'ISUZU', 0, 1), 
('TRUCK_MODEL', 'MITSUBISHI', 0, 1), 
('TRUCK_MODEL', 'GAZ', 0, 1), 
('TRUCK_MODEL', 'MAGIRUS', 0, 1), 
('TRUCK_MODEL', 'KAMAZ', 0, 1), 
('TRUCK_MODEL', 'TATRA', 0, 1), 
('TRUCK_MODEL', 'ZIL', 0, 1), 
('TRUCK_MODEL', 'INTERNATIONAL', 0, 1), 
('TRUCK_MODEL', 'FREIGHTLINER', 0, 1), 
('TRUCK_MODEL', 'STEYR', 0, 1), 
('TRUCK_MODEL', 'LIAZ', 0, 1), 
('TRUCK_MODEL', 'KRAZ', 0, 1), 
('TRUCK_MODEL', 'KIA', 0, 1), 
('TRUCK_MODEL', 'UNIMOG', 0, 1), 
('TRUCK_MODEL', 'TERBERG', 0, 1), 
('TRUCK_MODEL', 'HOWO', 0, 1), 
('TRUCK_MODEL', 'FAW', 0, 1), 
('TRUCK_MODEL', 'KENWORTH', 0, 1), 
('TRUCK_MODEL', 'ERF', 0, 1), 
('TRUCK_MODEL', 'FOTON', 0, 1), 
('TRUCK_MODEL', 'FIAT', 0, 1), 
('TRUCK_MODEL', 'YUEJIN', 0, 1), 
('TRUCK_MODEL', 'IFA', 0, 1), 
('TRUCK_MODEL', 'HYUNDAI', 0, 1), 
('TRUCK_MODEL', 'SISU', 0, 1), 
('TRUCK_MODEL', 'STERLING', 0, 1), 
('TRUCK_MODEL', 'TOYOTA', 0, 1), 
('TRUCK_MODEL', 'JAC', 0, 1), 
('TRUCK_MODEL', 'TATA', 0, 1), 
('TRUCK_MODEL', 'URAL', 0, 1), 
('TRUCK_MODEL', 'MACK', 0, 1), 
('TRUCK_MODEL', 'CHEVROLET', 0, 1), 
('TRUCK_MODEL', 'GMC', 0, 1), 
('TRUCK_MODEL', 'LDV', 0, 1), 
('TRUCK_MODEL', 'UAZ', 0, 1), 
('TRUCK_MODEL', 'MZKT', 0, 1), 
('TRUCK_MODEL', 'PEGASO', 0, 1), 
('TRUCK_MODEL', 'SAURER', 0, 1), 
('TRUCK_MODEL', 'BEDFORD', 0, 1), 
('TRUCK_MODEL', 'JELCZ', 0, 1), 
('TRUCK_MODEL', 'DODGE', 0, 1), 
('TRUCK_MODEL', 'MAZDA', 0, 1), 
('TRUCK_MODEL', 'MAN-VW', 0, 1), 
('TRUCK_MODEL', 'PETERBILT', 0, 1), 
('TRUCK_MODEL', 'CAMC', 0, 1), 
('TRUCK_MODEL', 'STAR', 0, 1), 
('TRUCK_MODEL', 'FORLAND', 0, 1), 
('TRUCK_MODEL', 'LUBLIN', 0, 1), 
('TRUCK_MODEL', '', 0, 1);