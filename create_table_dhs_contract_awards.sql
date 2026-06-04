-- =============================================================
-- SQL Server DDL  –  DHS Contract Awards (SAM.gov / FPDS)
-- =============================================================
-- Table covers the full FPDS/SAM contract award schema as of 2024.
-- Columns present in only some fiscal years are nullable by design.
-- The Python pipeline adds source_fiscal_year / source_file tags.
--
-- Tested on: SQL Server 2019 / Azure SQL Database
-- =============================================================

IF OBJECT_ID(N'dbo.dhs_contract_awards', N'U') IS NOT NULL
    DROP TABLE dbo.dhs_contract_awards;
GO

CREATE TABLE dbo.dhs_contract_awards (

    -- -------------------------------------------------------
    -- Surrogate key & pipeline metadata
    -- -------------------------------------------------------
    contract_award_sk               BIGINT          IDENTITY(1,1) NOT NULL,
    source_fiscal_year              SMALLINT        NULL,           -- FY from source CSV (e.g. 2022)
    source_file                     NVARCHAR(100)   NULL,           -- source filename
    load_timestamp                  DATETIME2       NOT NULL DEFAULT SYSUTCDATETIME(),

    -- -------------------------------------------------------
    -- Contract Identification
    -- -------------------------------------------------------
    piid                            NVARCHAR(50)    NULL,   -- Procurement Instrument Identifier
    modification_number             NVARCHAR(25)    NULL,   -- "0" = base; "P0001" etc. = mod
    transaction_number              INT             NULL,
    referenced_idv_piid             NVARCHAR(50)    NULL,   -- parent IDV PIID (if order)
    referenced_idv_agency_id        NVARCHAR(10)    NULL,
    referenced_idv_modification_number NVARCHAR(25) NULL,
    agency_id                       NVARCHAR(10)    NULL,
    solicitation_id                 NVARCHAR(50)    NULL,
    award_id                        NVARCHAR(50)    NULL,   -- alternate award identifier

    -- -------------------------------------------------------
    -- Award Dates
    -- -------------------------------------------------------
    date_signed                     DATE            NULL,
    effective_date                  DATE            NULL,
    last_modified_date              DATE            NULL,
    completion_date                 DATE            NULL,
    period_of_performance_start_date              DATE NULL,
    period_of_performance_current_end_date        DATE NULL,
    period_of_performance_potential_end_date      DATE NULL,
    approved_date                   DATE            NULL,
    fiscal_year                     SMALLINT        NULL,

    -- -------------------------------------------------------
    -- Dollar Values
    -- -------------------------------------------------------
    action_obligation                             DECIMAL(20,2) NULL,   -- obligated this action
    dollars_obligated                             DECIMAL(20,2) NULL,   -- cumulative obligated
    total_dollars_obligated                       DECIMAL(20,2) NULL,
    base_and_all_options_value                    DECIMAL(20,2) NULL,
    base_and_exercised_options_value              DECIMAL(20,2) NULL,
    potential_total_value_of_award                DECIMAL(20,2) NULL,
    current_total_value_of_award                  DECIMAL(20,2) NULL,
    face_value_of_contract                        DECIMAL(20,2) NULL,   -- IDV only

    -- -------------------------------------------------------
    -- Awarding Agency / Office Hierarchy
    -- -------------------------------------------------------
    department_id                   NVARCHAR(10)    NULL,   -- DHS = "7012"
    department_name                 NVARCHAR(255)   NULL,
    sub_tier_id                     NVARCHAR(10)    NULL,
    sub_tier_name                   NVARCHAR(255)   NULL,
    contracting_office_id           NVARCHAR(10)    NULL,
    contracting_office_name         NVARCHAR(255)   NULL,
    contracting_officer_business_size_determination NVARCHAR(100) NULL,

    -- -------------------------------------------------------
    -- Funding Agency / Office Hierarchy
    -- -------------------------------------------------------
    funding_agency_id               NVARCHAR(10)    NULL,
    funding_agency_name             NVARCHAR(255)   NULL,
    funding_sub_tier_id             NVARCHAR(10)    NULL,
    funding_sub_tier_name           NVARCHAR(255)   NULL,
    funding_office_id               NVARCHAR(10)    NULL,
    funding_office_name             NVARCHAR(255)   NULL,

    -- -------------------------------------------------------
    -- Awardee / Vendor
    -- -------------------------------------------------------
    awardee_uei                     NVARCHAR(20)    NULL,   -- Unique Entity Identifier (post-2022)
    awardee_duns                    NVARCHAR(20)    NULL,   -- DUNS (legacy, pre-2022)
    awardee_name                    NVARCHAR(255)   NULL,
    awardee_doing_business_as_name  NVARCHAR(255)   NULL,
    awardee_cage_code                NVARCHAR(10)   NULL,
    awardee_address_line_1          NVARCHAR(255)   NULL,
    awardee_address_line_2          NVARCHAR(255)   NULL,
    awardee_city                    NVARCHAR(100)   NULL,
    awardee_state                   NVARCHAR(50)    NULL,
    awardee_state_code              NVARCHAR(5)     NULL,
    awardee_zip                     NVARCHAR(20)    NULL,
    awardee_country                 NVARCHAR(50)    NULL,
    awardee_country_code            NVARCHAR(5)     NULL,
    awardee_congressional_district  NVARCHAR(10)    NULL,
    awardee_phone_number            NVARCHAR(30)    NULL,
    awardee_fax_number              NVARCHAR(30)    NULL,

    -- Immediate parent
    immediate_parent_uei            NVARCHAR(20)    NULL,
    immediate_parent_duns           NVARCHAR(20)    NULL,
    immediate_parent_name           NVARCHAR(255)   NULL,

    -- Domestic ultimate parent
    domestic_parent_uei             NVARCHAR(20)    NULL,
    domestic_parent_duns            NVARCHAR(20)    NULL,
    domestic_parent_name            NVARCHAR(255)   NULL,

    -- Global ultimate parent
    global_parent_uei               NVARCHAR(20)    NULL,
    global_parent_duns              NVARCHAR(20)    NULL,
    global_parent_name              NVARCHAR(255)   NULL,

    -- -------------------------------------------------------
    -- Place of Performance
    -- -------------------------------------------------------
    place_of_performance_city                     NVARCHAR(100) NULL,
    place_of_performance_state                    NVARCHAR(50)  NULL,
    place_of_performance_state_code               NVARCHAR(5)   NULL,
    place_of_performance_zip                      NVARCHAR(20)  NULL,
    place_of_performance_country                  NVARCHAR(50)  NULL,
    place_of_performance_country_code             NVARCHAR(5)   NULL,
    place_of_performance_congressional_district   NVARCHAR(10)  NULL,

    -- -------------------------------------------------------
    -- Product / Service Classification
    -- -------------------------------------------------------
    psc_code                        NVARCHAR(10)    NULL,   -- Product Service Code
    psc_description                 NVARCHAR(255)   NULL,
    naics_code                      NVARCHAR(10)    NULL,   -- North American Industry Classification
    naics_description               NVARCHAR(255)   NULL,

    -- -------------------------------------------------------
    -- Contract Type & Pricing
    -- -------------------------------------------------------
    type_of_contract_pricing        NVARCHAR(100)   NULL,
    type_of_contract_pricing_description NVARCHAR(255) NULL,
    contract_type                   NVARCHAR(50)    NULL,   -- Award, IDV, etc.
    award_type                      NVARCHAR(50)    NULL,   -- Definitive Contract, BPA Call, etc.
    idv_type                        NVARCHAR(50)    NULL,   -- FSS, GWAC, BOA, IDC, etc.
    multi_year_contract             CHAR(1)         NULL,   -- Y/N
    letter_contract                 CHAR(1)         NULL,   -- Y/N
    purchase_card_as_payment_method CHAR(1)         NULL,   -- Y/N
    undefinitized_action            CHAR(1)         NULL,   -- Y/N
    consolidated_contract           CHAR(1)         NULL,   -- Y/N

    -- -------------------------------------------------------
    -- Competition / Set-Aside
    -- -------------------------------------------------------
    set_aside_type                  NVARCHAR(100)   NULL,
    set_aside_description           NVARCHAR(255)   NULL,
    extent_competed                 NVARCHAR(100)   NULL,
    extent_competed_description     NVARCHAR(255)   NULL,
    solicitation_procedures         NVARCHAR(100)   NULL,
    solicitation_procedures_description NVARCHAR(255) NULL,
    type_of_set_aside               NVARCHAR(100)   NULL,
    number_of_offers_received       INT             NULL,
    local_area_set_aside            CHAR(1)         NULL,
    evaluated_preference            NVARCHAR(100)   NULL,
    evaluated_preference_description NVARCHAR(255)  NULL,
    research                        NVARCHAR(100)   NULL,
    fair_opportunity_limited_sources NVARCHAR(100)  NULL,
    other_than_full_and_open_competition NVARCHAR(100) NULL,

    -- -------------------------------------------------------
    -- Small Business / Socioeconomic Indicators
    -- -------------------------------------------------------
    small_business_competitiveness_demonstration_program CHAR(1) NULL,
    simplified_procedures_for_certain_commercial_items CHAR(1) NULL,
    a76_fair_act_action             CHAR(1)         NULL,
    fed_biz_opps                    CHAR(1)         NULL,

    -- Business type flags (Y/N each)
    small_business                  CHAR(1)         NULL,
    very_small_business             CHAR(1)         NULL,
    large_business                  CHAR(1)         NULL,
    disadvantaged_business          CHAR(1)         NULL,
    woman_owned_business            CHAR(1)         NULL,
    women_owned_small_business      CHAR(1)         NULL,
    economically_disadvantaged_woman_owned_small_business CHAR(1) NULL,
    veteran_owned_business          CHAR(1)         NULL,
    service_disabled_veteran_owned_business CHAR(1) NULL,
    hubzone_firm                    CHAR(1)         NULL,
    sba_certified_8a_program_participant CHAR(1)    NULL,
    minority_owned_business         CHAR(1)         NULL,
    asian_pacific_american_owned    CHAR(1)         NULL,
    black_american_owned            CHAR(1)         NULL,
    hispanic_american_owned         CHAR(1)         NULL,
    native_american_owned           CHAR(1)         NULL,
    subcontinent_asian_american_owned CHAR(1)       NULL,
    other_minority_owned            CHAR(1)         NULL,
    tribal_government               CHAR(1)         NULL,
    alaskan_native_corporation_owned CHAR(1)        NULL,
    native_hawaiian_organization_owned CHAR(1)      NULL,
    indian_tribe_federally_recognized CHAR(1)       NULL,

    -- -------------------------------------------------------
    -- Contracting Officer / Actions
    -- -------------------------------------------------------
    number_of_actions               INT             NULL,
    record_type                     NVARCHAR(20)    NULL,   -- A=Award, B=IDV
    referenced_idv_type             NVARCHAR(50)    NULL,
    major_program                   NVARCHAR(100)   NULL,
    program_acronym                 NVARCHAR(50)    NULL,
    budget_subfunction_title        NVARCHAR(255)   NULL,
    inherently_governmental_functions NVARCHAR(255) NULL,
    cost_or_pricing_data            NVARCHAR(100)   NULL,
    interagency_contracting_authority NVARCHAR(255) NULL,
    other_statutory_authority       NVARCHAR(255)   NULL,
    sea_transportation              NVARCHAR(100)   NULL,
    clinger_cohen_act_planning      NVARCHAR(100)   NULL,
    davis_bacon_act                 NVARCHAR(100)   NULL,
    service_contract_act            NVARCHAR(100)   NULL,
    walsh_healey_act                NVARCHAR(100)   NULL,
    information_technology_commercial_item_category NVARCHAR(100) NULL,
    recovered_materials_sustainability NVARCHAR(100) NULL,
    contingency_humanitarian_or_peacekeeping_operation NVARCHAR(100) NULL,
    multi_year_contract_description NVARCHAR(512)   NULL,

    -- -------------------------------------------------------
    -- Description / Notes
    -- -------------------------------------------------------
    description_of_contract_requirement NVARCHAR(2000) NULL,   -- truncated if needed

    -- -------------------------------------------------------
    -- IDV-specific
    -- -------------------------------------------------------
    number_of_actions_under_idv     INT             NULL,
    total_obligated_amount_for_idv  DECIMAL(20,2)   NULL,
    ordering_period_end_date        DATE            NULL,

    -- -------------------------------------------------------
    -- Catch-all for any additional columns discovered at runtime
    -- (handled by Python pipeline – add columns here as needed)
    -- -------------------------------------------------------
    -- extra_col_1  NVARCHAR(512) NULL,

    CONSTRAINT PK_dhs_contract_awards PRIMARY KEY CLUSTERED (contract_award_sk)
);
GO

-- =============================================================
-- Indexes
-- =============================================================

-- Primary lookup by contract PIID
CREATE NONCLUSTERED INDEX IX_dhs_ca_piid
    ON dbo.dhs_contract_awards (piid, modification_number)
    INCLUDE (date_signed, dollars_obligated, awardee_name);
GO

-- Fiscal year filtering (most common partition dimension)
CREATE NONCLUSTERED INDEX IX_dhs_ca_fiscal_year
    ON dbo.dhs_contract_awards (source_fiscal_year, fiscal_year);
GO

-- Date-range queries
CREATE NONCLUSTERED INDEX IX_dhs_ca_date_signed
    ON dbo.dhs_contract_awards (date_signed)
    INCLUDE (piid, action_obligation, awardee_uei, naics_code);
GO

CREATE NONCLUSTERED INDEX IX_dhs_ca_approved_date
    ON dbo.dhs_contract_awards (approved_date);
GO

-- Vendor lookups
CREATE NONCLUSTERED INDEX IX_dhs_ca_awardee_uei
    ON dbo.dhs_contract_awards (awardee_uei)
    INCLUDE (awardee_name, awardee_duns);
GO

-- Industry / product analysis
CREATE NONCLUSTERED INDEX IX_dhs_ca_naics
    ON dbo.dhs_contract_awards (naics_code)
    INCLUDE (psc_code, action_obligation, date_signed);
GO

CREATE NONCLUSTERED INDEX IX_dhs_ca_psc
    ON dbo.dhs_contract_awards (psc_code);
GO

-- DHS sub-tier / office breakdown
CREATE NONCLUSTERED INDEX IX_dhs_ca_sub_tier
    ON dbo.dhs_contract_awards (sub_tier_id, contracting_office_id)
    INCLUDE (action_obligation, date_signed);
GO

-- Competition / set-aside analysis
CREATE NONCLUSTERED INDEX IX_dhs_ca_set_aside
    ON dbo.dhs_contract_awards (set_aside_type, extent_competed);
GO
GO

-- =============================================================
-- Helpful views
-- =============================================================

CREATE OR ALTER VIEW dbo.vw_dhs_ca_summary AS
SELECT
    COALESCE(source_fiscal_year, fiscal_year)               AS fiscal_year,
    sub_tier_name                                           AS dhs_component,
    award_type,
    naics_code,
    naics_description,
    psc_code,
    set_aside_type,
    COUNT(*)                                                AS contract_count,
    SUM(action_obligation)                                  AS total_action_obligation,
    SUM(base_and_all_options_value)                         AS total_base_and_options
FROM dbo.dhs_contract_awards
GROUP BY
    COALESCE(source_fiscal_year, fiscal_year),
    sub_tier_name,
    award_type,
    naics_code,
    naics_description,
    psc_code,
    set_aside_type;
GO
