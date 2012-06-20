DROP TABLE IF EXISTS `feature_has_MSMS_precursor`;
DROP TABLE IF EXISTS `MASCOT_protein`;
DROP TABLE IF EXISTS `MASCOT_peptide`;
DROP TABLE IF EXISTS `feature_has_userParam_names_has_userParam_value`;
DROP TABLE IF EXISTS `feature_has_userParam_names`;
DROP TABLE IF EXISTS `userParam_names`;
DROP TABLE IF EXISTS `userParam_value`;
DROP TABLE IF EXISTS `feature_mapping`;
DROP TABLE IF EXISTS `MSMS_precursor`;
DROP TABLE IF EXISTS `spectrum`;
DROP TABLE IF EXISTS `convexhull_edges`;
DROP TABLE IF EXISTS `convexhull`;
DROP TABLE IF EXISTS `feature`;
DROP TABLE IF EXISTS `msrun`;

-- -----------------------------------------------------
-- Table `msrun`
--
-- Holds the name of the msrun and a description.The start_time is saved as TEXT as ISO8601 strings ("YYYY-MM-DD HH:MM:SS.SSS"). See http://sqlite.org/datatype3.html 1.2
-- -----------------------------------------------------
CREATE TABLE `msrun` (
  `msrun_id` INT PRIMARY KEY NOT NULL ,
  `msrun_name` VARCHAR(40) UNIQUE NOT NULL ,
  `description` VARCHAR(500) NOT NULL ,
  `start_time` TEXT NOT NULL);

-- -----------------------------------------------------
-- Table `feature`
--
-- Holds information on all the features of an msrun.
--
-- intensity_cutoff is the cut-off setting set when feature picking. This way one msrun can have multiple intensity cutoffs. 
-- Because of performance issues feature also contains the outer edges (min and max values of mz and rt) of the convexhull. These are also
-- save in the convexhull but it takes to long to do a join and max(rt), max(mz), min(rt) etc select. 
-- -----------------------------------------------------
CREATE TABLE `feature` (
  `feature_table_id` INT PRIMARY KEY NOT NULL ,
  `feature_id` VARCHAR(40) NOT NULL ,
  `intensity` DOUBLE NOT NULL ,
  `overallquality` DOUBLE NOT NULL ,
  `charge` INT NOT NULL ,
  `content` VARCHAR(45) NOT NULL ,
  `intensity_cutoff` DOUBLE NOT NULL,
  `msrun_msrun_id` INT NOT NULL ,
  CONSTRAINT `fk_feature_msrun1`
    FOREIGN KEY (`msrun_msrun_id` )
    REFERENCES `msrun` (`msrun_id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);

-- -----------------------------------------------------
-- Table `convexhull`
-- 
-- Holds the convexhull m/z and retention time points of each feature
-- -----------------------------------------------------
CREATE TABLE `convexhull` (
  `convexhull_id` INT PRIMARY KEY NOT NULL ,
  `mz` DOUBLE NOT NULL ,
  `rt` DOUBLE NOT NULL ,
  `feature_feature_table_id` INT NOT NULL ,
  CONSTRAINT `fk_convexhull_feature`
    FOREIGN KEY (`feature_feature_table_id` )
    REFERENCES `feature` (`feature_table_id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);

-- -----------------------------------------------------
-- Table `convexhull_edges`
--
-- Contains the edges of the convexhull
--
-- convexhull_edges contains the 4 edge points of the conveshull of the 
-- feature. Although the convexhull table also contains these values 
-- (accesible with max(rt), min(rt), max(mz), min(mz)) this is left in 
-- to be compatible with sqlite's convexhull edges (which uses R*Tree)
-- -----------------------------------------------------
CREATE TABLE convexhull_edges(
  `feature_feature_table_id` INT PRIMARY KEY NOT NULL,             
  `rtMin` DOUBLE NOT NULL, 
  `rtMax` DOUBLE NOT NULL,
  `mzMin` DOUBLE NOT NULL, 
  `mzMax` DOUBLE NOT NULL,
  CONSTRAINT `fk_convexhull_edges_feature`
    FOREIGN KEY (`feature_feature_table_id` )
    REFERENCES `feature` (`feature_table_id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);

-- -----------------------------------------------------
-- Table `spectrum`
--
-- Holds information on each spectrum of an msrun.
-- scan_start_time is in seconds (to be the same as the retention time of features)
-- -----------------------------------------------------
CREATE TABLE `spectrum` (
  `spectrum_id` INT PRIMARY KEY NOT NULL ,
  `spectrum_index` INT NOT NULL ,
  `ms_level` INT NOT NULL ,
  `base_peak_mz` DOUBLE NOT NULL ,
  `base_peak_intensity` DOUBLE NOT NULL ,
  `total_ion_current` DOUBLE NOT NULL ,
  `lowest_observes_mz` DOUBLE NOT NULL ,
  `highest_observed_mz` DOUBLE NOT NULL ,
  `scan_start_time` DOUBLE NOT NULL ,
  `ion_injection_time` DOUBLE,
  `binary_data_mz` LONGBLOB NOT NULL,
  `binary_data_rt` LONGBLOB NOT NULL,
  `msrun_msrun_id` INT NOT NULL ,
  CONSTRAINT `fk_spectrum_msrun1`
    FOREIGN KEY (`msrun_msrun_id` )
    REFERENCES `msrun` (`msrun_id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);


-- -----------------------------------------------------
-- Table `MSMS_precursor`
--
-- Holds information on the MS/MS precursor of a spectrum. A spectrum only has an MS/MS precursor if the MS level of the spectrum is 2+
-- -----------------------------------------------------
CREATE TABLE `MSMS_precursor` (
  `precursor_id` INT PRIMARY KEY NOT NULL ,
  `ion_mz` DOUBLE NOT NULL ,
  `charge_state` INT NOT NULL ,
  `peak_intensity` DOUBLE NOT NULL ,
  `spectrum_spectrum_id` INT NOT NULL,
  CONSTRAINT `fk_MSMS_spectrum_msrun1`
    FOREIGN KEY (`spectrum_spectrum_id`)
    REFERENCES `spectrum` (`spectrum_id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);

-- -----------------------------------------------------
-- Table `MSMS_precursor`
--
-- Holds information on the MS/MS precursor of a spectrum. A spectrum only has an MS/MS precursor if the MS level of the spectrum is 2+
-- -----------------------------------------------------
CREATE TABLE `feature_has_MSMS_precursor` (
  `MSMS_precursor_precursor_id` INT NOT NULL ,
  `feature_feature_table_id` INT NOT NULL ,
  CONSTRAINT `fk_spectrum_has_feature_spectrum1`
    FOREIGN KEY (`MSMS_precursor_precursor_id` )
    REFERENCES `MSMS_precursor` (`precursor_id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_spectrum_has_feature_feature1`
    FOREIGN KEY (`feature_feature_table_id` )
    REFERENCES `feature` (`feature_table_id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);

-- -----------------------------------------------------
-- Table `MASCOT_peptide`
--
-- Holds information on the peptides from mascot results. If they are assigned, MASCOT_protein will be linked to them.  
-- assigned works as a boolean, but because sqlite doesn't know bool type it is an int type. 0 for false, 1 for true. 
-- -----------------------------------------------------
CREATE TABLE `MASCOT_peptide` (
  `peptide_id` INT PRIMARY KEY NOT NULL,
  `pep_exp_mz` DOUBLE NOT NULL, 
  `pep_exp_mr` DOUBLE NOT NULL,
  `pep_exp_z` INT NOT NULL,
  `pep_calc_mr` DOUBLE NOT NULL,
  `pep_delta` DOUBLE NOT NULL,
  `pep_miss` INT NOT NULL,
  `pep_score` DOUBLE NOT NULL,
  `pep_expect` DOUBLE NOT NULL,
  `pep_res_before` VARCHAR(1),
  `pep_seq` VARCHAR(40) NOT NULL,
  `pep_res_after` VARCHAR(1),
  `pep_var_mod` VARCHAR(100),
  `pep_var_mod_pos` VARCHAR(40),
  `pep_num_match` INT,
  `pep_scan_title` VARCHAR(255) NOT NULL,
  `isAssigned` int NOT null,
  `precursor_precursor_id` INT NOT NULL, 
  CONSTRAINT `fk_mascot_peptide_precursor1`
    FOREIGN KEY (`precursor_precursor_id`)
    REFERENCES `MSMS_precursor` (`precursor_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);

-- -----------------------------------------------------
-- Table `MASCOT_protein`
--
-- Holds information on the proteins from mascot results. 
-- -----------------------------------------------------
CREATE TABLE `MASCOT_protein` (
  `mascot_protein_id` INT PRIMARY KEY NOT NULL ,
  `protein_accession` VARCHAR(500) NOT NULL,
  `prot_desc` VARCHAR(200) NOT NULL,
  `prot_score` DOUBLE NOT NULL,
  `prot_mass` DOUBLE NOT NULL,
  `prot_matches` INT NOT NULL,
  `prot_matches_sig` INT NOT NULL,
  `prot_sequences` INT NOT NULL,
  `prot_sequences_sig` INT NOT NULL,
  `mascot_peptide_peptide_id` INT NOT NULL,
  CONSTRAINT `fk_mascot_protein_precursor1`
    FOREIGN KEY (`mascot_peptide_peptide_id`)
    REFERENCES `MASCOT_peptide` (`peptide_id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);

-- -----------------------------------------------------
-- Table `userParam_names`
--
-- Holds the name of user params from features (e.g. spectrum_index, FWHM, etc)
-- -----------------------------------------------------
CREATE TABLE `userParam_names` (
  `userParamName_id` INT PRIMARY KEY NOT NULL ,
  `name` VARCHAR(45) NOT NULL );

-- -----------------------------------------------------
-- Table IF EXISTS `userParam_value`
--
-- The value of the userParam of a feature (see also table userParam_names)
-- -----------------------------------------------------
CREATE TABLE `userParam_value` (
  `userParamValue_id` INT PRIMARY KEY NOT NULL ,
  `value` VARCHAR(45) NOT NULL );

-- -----------------------------------------------------
-- Table IF EXISTS `feature_has_userParam_names`
--
-- Many-to-many link between features and userParam names
-- -----------------------------------------------------
CREATE TABLE `feature_has_userParam_names` (
  `feature_has_userParam_names_id` INT PRIMARY KEY NOT NULL ,
  `feature_feature_table_id` INT NOT NULL ,
  `userParam_names_userParamName_id` INT NOT NULL ,
  CONSTRAINT `fk_feature_has_userParam_names_feature1`
    FOREIGN KEY (`feature_feature_table_id` )
    REFERENCES `feature` (`feature_table_id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_feature_has_names_feature1`
    FOREIGN KEY (`userParam_names_userParamName_id` )
    REFERENCES `userParam_names` (`userParamName_id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);
-- -----------------------------------------------------
-- Table `feature_has_userParam_names_has_userParam_value`
--
-- Many-to-many link  between feature_has_userParam_names and userParam_value
-- -----------------------------------------------------
CREATE TABLE `feature_has_userParam_names_has_userParam_value` (
  `feature_has_userParam_names_feature_has_userParam_names_id` INT NOT NULL, 
  `userParam_value_userParamValue_id` INT NOT NULL ,
  Constraint `fk_feature_has_userParam_names_has_userParam_value_userParam_1`
    FOREIGN KEY (`feature_has_userParam_names_feature_has_userParam_names_id`)
    REFERENCES `feature_has_userParam_names` (`feature_has_userParam_names_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_userParam_value_userParamValue_id`
    FOREIGN KEY (`userParam_value_userParamValue_id` )
    REFERENCES `userParam_value` (`userParamValue_id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);

-- -----------------------------------------------------
-- Table `feature_mapping`
--
-- Information from trafoXML file, from where to where the features retention time shifted during alignment. 
--
-- feature_got_mapped_id is the feature_table_id of the feature that got aligned to the identity file feature (the feature from the linear file).
-- feature_identity_id is the feature_table_id of the feature to which feature_got_mapped_id got aligned (the feature from the identity file).
-- They are both foreign keys. There can be multiple feature_table_id's for one feature_id, the feature_table_id with the same msrun_id is choosen
-- for the foreign keys to point to.
-- -----------------------------------------------------
CREATE TABLE `feature_mapping` (
  `feature_mapping_id` INT PRIMARY KEY NOT NULL ,
  `feature_got_mapped_id` INT NOT NULL,
  `feature_identity_id` INT NOT NULL ,
  `to` DOUBLE NOT NULL ,
  `from` DOUBLE NOT NULL ,
  CONSTRAINT `fk_feature_mapping_feature1`
    FOREIGN KEY (`feature_got_mapped_id` )
    REFERENCES `feature` (`feature_table_id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_feature_mapping_feature2`
    FOREIGN KEY (`feature_identity_id` )
    REFERENCES `feature` (`feature_table_id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);



CREATE INDEX `fk_MSMS_precursor_id_1` ON  `MSMS_precursor` (`precursor_id` ASC);
CREATE INDEX `fk_MSMS_precursor_spectrum_spectrum_id_1` ON  `MSMS_precursor` (`spectrum_spectrum_id` ASC);
CREATE INDEX `fk_convexhull1` ON `convexhull` (`feature_feature_table_id` ASC);
CREATE INDEX `fk_convexhull_edges1` ON `convexhull_edges` (`feature_feature_table_id` ASC);
CREATE INDEX `fk_feature1` ON `feature` (`feature_table_id` ASC);
CREATE INDEX `fk_feature_has_MSMS_precursor_feature1` ON `feature_has_MSMS_precursor` (`feature_feature_table_id` ASC);
CREATE INDEX `fk_feature_has_MSMS_precursor_precursor1` ON `feature_has_MSMS_precursor` (`MSMS_precursor_precursor_id` ASC);
CREATE INDEX `fk_feature_has_userParam_names_feature_fk1` ON `feature_has_userParam_names` (`feature_feature_table_id` ASC);
CREATE INDEX `fk_feature_has_userParam_names_value` ON  `feature_has_userParam_names_has_userParam_value` (`feature_has_userParam_names_feature_has_userParam_names_id` ASC);
CREATE INDEX `fk_feature_has_userParam_names_userParam_names1` ON `feature_has_userParam_names` (`userParam_names_userParamName_id` ASC);
CREATE INDEX `fk_feature_identity_feature2` ON `feature_mapping` (`feature_identity_id` ASC);
CREATE INDEX `fk_feature_map_feature1` ON `feature_mapping` (`feature_got_mapped_id` ASC);
CREATE INDEX `fk_mascot_peptide1` ON `MASCOT_peptide` (`peptide_id` ASC);
CREATE INDEX `fk_mascot_peptide_precursor` ON `MASCOT_peptide` (`precursor_precursor_id` ASC);
CREATE INDEX `fk_mascot_protein_to_precursor1` ON `MASCOT_protein` (`mascot_peptide_peptide_id` ASC);
CREATE INDEX `fk_msrun1` ON `msrun` (`msrun_id` ASC);
CREATE INDEX `fk_spectrum_scahn_start_time_1` ON  `spectrum` (`scan_start_time` ASC);
CREATE INDEX `fk_spectrum_spectrum_id_1` ON  `spectrum` (`spectrum_id` ASC);
CREATE INDEX `fk_userParam_valuue_userParamValue_id` ON  `feature_has_userParam_names_has_userParam_value` (`userParam_value_userParamValue_id` ASC);

