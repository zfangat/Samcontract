-- ============================================================
-- SQL Server DDL  –  DHS Contract Awards (SAM.gov / FPDS v1.5)
-- Generated: 2026-06-04 03:22:26
-- Column mapping source: FPDS Data Element Dictionary v1.5 +
--   SAM.gov Contract Awards API JSON schema
-- Raw CSV headers use dot-notation (e.g. contractId.PIID)
-- mapped to short names via sam_column_mapping.py
-- ============================================================

IF OBJECT_ID(N'dbo.dhs_contract_awards', N'U') IS NOT NULL
    DROP TABLE dbo.dhs_contract_awards;
GO

CREATE TABLE dbo.dhs_contract_awards (

    -- Surrogate key & load metadata
    contract_award_sk   BIGINT        IDENTITY(1,1) NOT NULL,
    load_timestamp      DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME(),

    -- =======================================================
    -- Contract ID
    -- =======================================================
    agency_code                                   NVARCHAR(10)           NULL,  -- FPDS 1F
    agency_name                                   NVARCHAR(255)          NULL,  -- FPDS 1F
    piid                                          NVARCHAR(50)           NULL,  -- FPDS 1A
    mod_number                                    NVARCHAR(25)           NULL,  -- FPDS 1B
    transaction_number                            INT                    NULL,
    ref_idv_agency_code                           NVARCHAR(10)           NULL,  -- FPDS 1H
    ref_idv_agency_name                           NVARCHAR(255)          NULL,  -- FPDS 1H
    ref_idv_piid                                  NVARCHAR(50)           NULL,  -- FPDS 1C
    ref_idv_mod_number                            NVARCHAR(25)           NULL,  -- FPDS 1G
    contracting_subtier_code                      NVARCHAR(10)           NULL,
    contracting_subtier_name                      NVARCHAR(255)          NULL,
    mod_reason_code                               NVARCHAR(5)            NULL,  -- FPDS 12C
    mod_reason_name                               NVARCHAR(255)          NULL,  -- FPDS 12C

    -- =======================================================
    -- Core Data
    -- =======================================================
    core_version                                  NVARCHAR(10)           NULL,
    award_or_idv                                  NVARCHAR(10)           NULL,  -- FPDS 12B
    award_type_code                               NVARCHAR(5)            NULL,  -- FPDS 12B
    award_type_name                               NVARCHAR(100)          NULL,  -- FPDS 12B
    idv_type_code                                 NVARCHAR(5)            NULL,  -- FPDS 12A
    idv_type_name                                 NVARCHAR(100)          NULL,  -- FPDS 12A
    solicitation_id                               NVARCHAR(50)           NULL,

    -- =======================================================
    -- Dates
    -- =======================================================
    date_signed                                   DATE                   NULL,  -- FPDS 2A
    perf_start_date                               DATE                   NULL,  -- FPDS 2B
    current_completion_date                       DATE                   NULL,  -- FPDS 2C
    ultimate_completion_date                      DATE                   NULL,  -- FPDS 2D
    last_modified_date                            DATETIME2              NULL,  -- FPDS 2F
    fiscal_year                                   SMALLINT               NULL,  -- FPDS 2G
    solicitation_date                             DATE                   NULL,  -- FPDS 2H
    created_date                                  DATETIME2              NULL,  -- FPDS 2J
    prepared_by                                   NVARCHAR(50)           NULL,  -- FPDS 2I
    created_via                                   NVARCHAR(5)            NULL,  -- FPDS 2K
    approved_date                                 DATE                   NULL,
    closed_date                                   DATE                   NULL,
    last_modified_user                            NVARCHAR(50)           NULL,  -- FPDS 2L

    -- =======================================================
    -- Dollars
    -- =======================================================
    action_obligation                             DECIMAL(20,2)          NULL,  -- FPDS 3C
    base_and_all_options                          DECIMAL(20,2)          NULL,  -- FPDS 3A
    base_and_exercised_options                    DECIMAL(20,2)          NULL,  -- FPDS 3B
    non_govt_dollars                              DECIMAL(20,2)          NULL,  -- FPDS 3D
    total_obligated                               DECIMAL(20,2)          NULL,  -- FPDS 3CT
    total_base_all_options                        DECIMAL(20,2)          NULL,  -- FPDS 3AT
    total_base_exercised                          DECIMAL(20,2)          NULL,  -- FPDS 3BT
    total_non_govt_dollars                        DECIMAL(20,2)          NULL,  -- FPDS 3DT

    -- =======================================================
    -- Awarding Org
    -- =======================================================
    dept_code                                     NVARCHAR(10)           NULL,  -- FPDS 4A
    dept_name                                     NVARCHAR(255)          NULL,  -- FPDS 4A
    subtier_code                                  NVARCHAR(10)           NULL,  -- FPDS 4A
    subtier_name                                  NVARCHAR(255)          NULL,  -- FPDS 4A
    contracting_office_code                       NVARCHAR(10)           NULL,  -- FPDS 4B
    contracting_office_name                       NVARCHAR(255)          NULL,  -- FPDS 4B
    contracting_office_region                     NVARCHAR(5)            NULL,

    -- =======================================================
    -- Funding Org
    -- =======================================================
    funding_dept_code                             NVARCHAR(10)           NULL,  -- FPDS 4C
    funding_dept_name                             NVARCHAR(255)          NULL,  -- FPDS 4C
    funding_subtier_code                          NVARCHAR(10)           NULL,  -- FPDS 4C
    funding_subtier_name                          NVARCHAR(255)          NULL,  -- FPDS 4C
    funding_office_code                           NVARCHAR(10)           NULL,  -- FPDS 4D
    funding_office_name                           NVARCHAR(255)          NULL,  -- FPDS 4D
    foreign_funding_code                          NVARCHAR(5)            NULL,
    foreign_funding_name                          NVARCHAR(100)          NULL,
    tas_agency_id                                 NVARCHAR(5)            NULL,  -- FPDS 6SC
    tas_main_account                              NVARCHAR(5)            NULL,  -- FPDS 6SG
    tas_sub_account                               NVARCHAR(5)            NULL,  -- FPDS 6SH

    -- =======================================================
    -- Contract Details
    -- =======================================================
    description                                   NVARCHAR(2000)         NULL,  -- FPDS 6M
    letter_contract                               CHAR(1)                NULL,
    multi_year_contract                           CHAR(1)                NULL,
    purchase_card_payment                         CHAR(1)                NULL,
    undefinitized_action                          CHAR(1)                NULL,
    consolidated_contract                         CHAR(1)                NULL,
    cost_pricing_data_code                        NVARCHAR(5)            NULL,
    cost_pricing_data_name                        NVARCHAR(100)          NULL,
    pricing_type_code                             NVARCHAR(5)            NULL,
    pricing_type_name                             NVARCHAR(100)          NULL,
    not_competed_reason_code                      NVARCHAR(5)            NULL,
    not_competed_reason_name                      NVARCHAR(255)          NULL,
    interagency_auth_code                         NVARCHAR(5)            NULL,
    interagency_auth_name                         NVARCHAR(255)          NULL,
    major_program                                 NVARCHAR(100)          NULL,
    program_acronym                               NVARCHAR(50)           NULL,
    national_interest_code                        NVARCHAR(10)           NULL,
    national_interest_name                        NVARCHAR(255)          NULL,
    initiative_code                               NVARCHAR(10)           NULL,  -- FPDS 6SI
    initiative_name                               NVARCHAR(255)          NULL,  -- FPDS 6SI
    co_bus_size_code                              NVARCHAR(5)            NULL,
    co_bus_size_name                              NVARCHAR(100)          NULL,
    sea_transport_code                            NVARCHAR(5)            NULL,
    sea_transport_name                            NVARCHAR(100)          NULL,
    contingency_op_code                           NVARCHAR(5)            NULL,
    contingency_op_name                           NVARCHAR(100)          NULL,
    walsh_healey_act                              NVARCHAR(5)            NULL,
    service_contract_act                          NVARCHAR(5)            NULL,
    davis_bacon_act                               NVARCHAR(5)            NULL,
    clinger_cohen_act                             NVARCHAR(5)            NULL,
    number_of_actions                             INT                    NULL,
    agreement_type_code                           NVARCHAR(5)            NULL,  -- FPDS OT8C
    agreement_type_name                           NVARCHAR(100)          NULL,  -- FPDS OT8C
    dod_acq_program_code                          NVARCHAR(10)           NULL,  -- FPDS 8B
    dod_acq_program_name                          NVARCHAR(255)          NULL,  -- FPDS 8B
    it_commercial_item_code                       NVARCHAR(5)            NULL,
    it_commercial_item_name                       NVARCHAR(100)          NULL,
    recovered_materials_code                      NVARCHAR(5)            NULL,
    recovered_materials_name                      NVARCHAR(100)          NULL,

    -- =======================================================
    -- Product/Service
    -- =======================================================
    psc_code                                      NVARCHAR(10)           NULL,  -- FPDS 8A
    psc_name                                      NVARCHAR(255)          NULL,  -- FPDS 8C
    naics_code                                    NVARCHAR(10)           NULL,
    naics_name                                    NVARCHAR(255)          NULL,
    claimant_program_code                         NVARCHAR(5)            NULL,
    claimant_program_name                         NVARCHAR(100)          NULL,
    contract_bundling_code                        NVARCHAR(5)            NULL,
    contract_bundling_name                        NVARCHAR(100)          NULL,
    system_equipment_code                         NVARCHAR(5)            NULL,
    system_equipment_name                         NVARCHAR(100)          NULL,

    -- =======================================================
    -- Competition
    -- =======================================================
    extent_competed_code                          NVARCHAR(5)            NULL,  -- FPDS 10A
    extent_competed_name                          NVARCHAR(100)          NULL,  -- FPDS 10A
    solicitation_proc_code                        NVARCHAR(5)            NULL,  -- FPDS 10M
    solicitation_proc_name                        NVARCHAR(100)          NULL,  -- FPDS 10M
    set_aside_code                                NVARCHAR(5)            NULL,
    set_aside_name                                NVARCHAR(100)          NULL,
    eval_preference_code                          NVARCHAR(5)            NULL,
    eval_preference_name                          NVARCHAR(100)          NULL,
    research_code                                 NVARCHAR(5)            NULL,
    research_name                                 NVARCHAR(100)          NULL,
    fair_opp_limited_code                         NVARCHAR(5)            NULL,
    fair_opp_limited_name                         NVARCHAR(100)          NULL,
    other_full_open_code                          NVARCHAR(5)            NULL,
    other_full_open_name                          NVARCHAR(100)          NULL,
    offers_received                               SMALLINT               NULL,
    commercial_item_acq_code                      NVARCHAR(5)            NULL,
    commercial_item_acq_name                      NVARCHAR(100)          NULL,
    sb_competitiveness_demo                       CHAR(1)                NULL,
    a76_fair_act                                  CHAR(1)                NULL,
    fed_biz_opps                                  CHAR(1)                NULL,
    local_set_aside                               CHAR(1)                NULL,
    price_eval_pct_diff                           DECIMAL(10,4)          NULL,
    nontrad_entity_code                           NVARCHAR(5)            NULL,  -- FPDS 10T
    nontrad_entity_name                           NVARCHAR(100)          NULL,  -- FPDS 10T

    -- =======================================================
    -- Awardee
    -- =======================================================
    awardee_uei                                   NVARCHAR(20)           NULL,  -- FPDS 9M
    awardee_cage_code                             NVARCHAR(10)           NULL,
    awardee_name                                  NVARCHAR(255)          NULL,  -- FPDS 13GG
    awardee_dba_name                              NVARCHAR(255)          NULL,  -- FPDS 13HH
    awardee_data_source                           NVARCHAR(20)           NULL,
    awardee_alt_site_code                         NVARCHAR(20)           NULL,
    awardee_addr1                                 NVARCHAR(255)          NULL,  -- FPDS 13JJ
    awardee_addr2                                 NVARCHAR(255)          NULL,  -- FPDS 13KK
    awardee_city                                  NVARCHAR(100)          NULL,  -- FPDS 13MM
    awardee_state_code                            NVARCHAR(5)            NULL,  -- FPDS 13NN
    awardee_state_name                            NVARCHAR(50)           NULL,  -- FPDS 13NN
    awardee_zip                                   NVARCHAR(20)           NULL,  -- FPDS 13PP
    awardee_country_code                          NVARCHAR(5)            NULL,  -- FPDS 13QQ
    awardee_country_name                          NVARCHAR(100)          NULL,  -- FPDS 13QQ
    awardee_phone                                 NVARCHAR(30)           NULL,  -- FPDS 13RR
    awardee_fax                                   NVARCHAR(30)           NULL,  -- FPDS 13SS
    awardee_cong_district                         NVARCHAR(10)           NULL,  -- FPDS 9F
    awardee_reg_date                              DATE                   NULL,
    awardee_renewal_date                          DATE                   NULL,
    consortia                                     NVARCHAR(5)            NULL,  -- FPDS 9N
    primary_consortium_uei                        NVARCHAR(20)           NULL,  -- FPDS 9O

    -- =======================================================
    -- Business Types
    -- =======================================================
    is_us_fed_govt                                NVARCHAR(5)            NULL,
    is_federal_agency                             NVARCHAR(5)            NULL,
    is_ffrdc                                      NVARCHAR(5)            NULL,
    is_state_govt                                 NVARCHAR(5)            NULL,
    is_foreign_govt                               NVARCHAR(5)            NULL,
    is_tribal_govt                                NVARCHAR(5)            NULL,
    is_local_govt                                 NVARCHAR(5)            NULL,
    is_small_business                             NVARCHAR(5)            NULL,
    is_very_small_biz                             NVARCHAR(5)            NULL,
    is_large_business                             NVARCHAR(5)            NULL,
    is_veteran_owned                              NVARCHAR(5)            NULL,
    is_sdvosb                                     NVARCHAR(5)            NULL,
    is_woman_owned                                NVARCHAR(5)            NULL,
    is_wosb                                       NVARCHAR(5)            NULL,
    is_edwosb                                     NVARCHAR(5)            NULL,
    is_minority_owned                             NVARCHAR(5)            NULL,
    is_asian_subcontinent                         NVARCHAR(5)            NULL,
    is_asian_pacific                              NVARCHAR(5)            NULL,
    is_black_american                             NVARCHAR(5)            NULL,
    is_hispanic_american                          NVARCHAR(5)            NULL,
    is_native_american                            NVARCHAR(5)            NULL,
    is_other_minority                             NVARCHAR(5)            NULL,
    is_sba_sdb                                    NVARCHAR(5)            NULL,
    is_8a                                         NVARCHAR(5)            NULL,
    is_hubzone                                    NVARCHAR(5)            NULL,
    is_cdc_owned                                  NVARCHAR(5)            NULL,
    is_alaska_native_corp                         NVARCHAR(5)            NULL,
    is_native_hawaiian                            NVARCHAR(5)            NULL,
    is_indian_tribe                               NVARCHAR(5)            NULL,
    is_nonprofit                                  NVARCHAR(5)            NULL,
    is_educational                                NVARCHAR(5)            NULL,
    is_labor_surplus                              NVARCHAR(5)            NULL,

    -- =======================================================
    -- Place of Performance
    -- =======================================================
    pop_location_code                             NVARCHAR(20)           NULL,  -- FPDS 9C
    pop_city_code                                 NVARCHAR(10)           NULL,
    pop_city_name                                 NVARCHAR(100)          NULL,
    pop_state_code                                NVARCHAR(5)            NULL,
    pop_state_name                                NVARCHAR(50)           NULL,
    pop_zip                                       NVARCHAR(20)           NULL,  -- FPDS 9K
    pop_country_code                              NVARCHAR(5)            NULL,
    pop_country_name                              NVARCHAR(100)          NULL,
    pop_cong_district                             NVARCHAR(10)           NULL,  -- FPDS 9G

    -- =======================================================
    -- Parent Entity
    -- =======================================================
    parent_uei                                    NVARCHAR(20)           NULL,
    parent_name                                   NVARCHAR(255)          NULL,
    domestic_parent_uei                           NVARCHAR(20)           NULL,
    domestic_parent_name                          NVARCHAR(255)          NULL,

    -- =======================================================
    -- Pipeline
    -- =======================================================
    source_fiscal_year                            SMALLINT               NULL,
    source_file                                   NVARCHAR(100)          NULL,

    CONSTRAINT PK_dhs_contract_awards PRIMARY KEY CLUSTERED (contract_award_sk)
);
GO

-- ============================================================
-- Indexes
-- ============================================================

-- Contract PIID + Mod lookup
CREATE NONCLUSTERED INDEX IX_piid
    ON dbo.dhs_contract_awards (piid, mod_number);
GO

-- Fiscal year filtering
CREATE NONCLUSTERED INDEX IX_fiscal_year
    ON dbo.dhs_contract_awards (fiscal_year, source_fiscal_year);
GO

-- Date-range queries
CREATE NONCLUSTERED INDEX IX_date_signed
    ON dbo.dhs_contract_awards (date_signed);
GO

-- Approved date queries
CREATE NONCLUSTERED INDEX IX_approved_date
    ON dbo.dhs_contract_awards (approved_date);
GO

-- Vendor lookup by UEI
CREATE NONCLUSTERED INDEX IX_awardee_uei
    ON dbo.dhs_contract_awards (awardee_uei);
GO

-- Vendor lookup by CAGE
CREATE NONCLUSTERED INDEX IX_cage_code
    ON dbo.dhs_contract_awards (awardee_cage_code);
GO

-- Industry analysis
CREATE NONCLUSTERED INDEX IX_naics
    ON dbo.dhs_contract_awards (naics_code);
GO

-- Product/service analysis
CREATE NONCLUSTERED INDEX IX_psc
    ON dbo.dhs_contract_awards (psc_code);
GO

-- DHS component filtering
CREATE NONCLUSTERED INDEX IX_subtier
    ON dbo.dhs_contract_awards (subtier_code);
GO

-- Competition/set-aside analysis
CREATE NONCLUSTERED INDEX IX_set_aside
    ON dbo.dhs_contract_awards (set_aside_code);
GO

-- Award type filtering
CREATE NONCLUSTERED INDEX IX_award_type
    ON dbo.dhs_contract_awards (award_type_code);
GO

-- ============================================================
-- Summary view
-- ============================================================

CREATE OR ALTER VIEW dbo.vw_dhs_ca_annual_summary AS
SELECT
    COALESCE(source_fiscal_year, fiscal_year)   AS fy,
    subtier_name                                AS dhs_component,
    award_type_name,
    naics_code,
    psc_code,
    set_aside_name,
    COUNT(*)                                    AS contract_actions,
    SUM(action_obligation)                      AS total_action_obligation,
    SUM(base_and_all_options)                   AS total_base_all_options,
    SUM(total_obligated)                        AS total_cumulative_obligated
FROM dbo.dhs_contract_awards
GROUP BY
    COALESCE(source_fiscal_year, fiscal_year),
    subtier_name, award_type_name, naics_code, psc_code, set_aside_name;
GO
