"""
sam_column_mapping.py
=====================
Complete mapping from SAM.gov / FPDS-NG CSV dot-notation column headers
  (e.g. "contractId.agencyId.code")
to short, SQL Server-safe column names
  (e.g. "agency_code")

Sources:
  - FPDS Data Element Dictionary v1.5 (GSA/IBM, June 2025)
  - SAM.gov Contract Awards API JSON schema (open.gsa.gov/api/contract-awards/)
  - SAM.gov CSV extract observed headers (fiscal years 2015–2024)

Usage:
    from sam_column_mapping import COLUMN_MAP, rename_dataframe, COLUMN_METADATA

    import pandas as pd
    df = pd.read_csv("dhs_contracts_fy2023.csv")
    df = rename_dataframe(df)      # applies mapping + normalises unmapped cols
"""

from __future__ import annotations
from typing import NamedTuple
import re
import pandas as pd


# ---------------------------------------------------------------------------
# Metadata record for each column
# ---------------------------------------------------------------------------
class ColMeta(NamedTuple):
    short_name: str       # target SQL column name
    sql_type:   str       # recommended SQL Server type
    fpds_id:    str       # FPDS element number (e.g. "1A") or "" if not in dict
    label:      str       # human-readable label
    section:    str       # logical section


# ---------------------------------------------------------------------------
# Master mapping  { raw_csv_header : ColMeta }
# ---------------------------------------------------------------------------
# Key  = exact header string that appears in the SAM.gov CSV extract.
#        The CSV uses the JSON path with dots, e.g. "contractId.PIID"
# Value= ColMeta(short_name, sql_type, fpds_id, label, section)
#
# NOTE: SAM.gov occasionally ships headers in slightly different casing across
# fiscal years.  The rename_dataframe() function does a case-insensitive match
# as a fallback.
# ---------------------------------------------------------------------------

COLUMN_MAP: dict[str, ColMeta] = {

    # ===================================================================
    # SECTION 1 – Contract Identification  (FPDS group 1)
    # ===================================================================
    "contractId.agencyId":
        ColMeta("agency_code",           "NVARCHAR(10)",  "1F",  "Awarding Agency Code",                    "Contract ID"),
    "contractId.agencyId.code":
        ColMeta("agency_code",           "NVARCHAR(10)",  "1F",  "Awarding Agency Code",                    "Contract ID"),
    "contractId.agencyId.name":
        ColMeta("agency_name",           "NVARCHAR(255)", "1F",  "Awarding Agency Name",                    "Contract ID"),
    "contractId.PIID":
        ColMeta("piid",                  "NVARCHAR(50)",  "1A",  "Procurement Instrument Identifier",       "Contract ID"),
    "contractId.piid":
        ColMeta("piid",                  "NVARCHAR(50)",  "1A",  "Procurement Instrument Identifier",       "Contract ID"),
    "contractId.modificationNumber":
        ColMeta("mod_number",            "NVARCHAR(25)",  "1B",  "Modification Number",                     "Contract ID"),
    "contractId.transactionNumber":
        ColMeta("transaction_number",    "INT",           "",    "Transaction Number",                      "Contract ID"),
    "contractId.referencedIDVID.agencyId":
        ColMeta("ref_idv_agency_code",   "NVARCHAR(10)",  "1H",  "Referenced IDV Agency Code",              "Contract ID"),
    "contractId.referencedIDVID.agencyId.code":
        ColMeta("ref_idv_agency_code",   "NVARCHAR(10)",  "1H",  "Referenced IDV Agency Code",              "Contract ID"),
    "contractId.referencedIDVID.agencyId.name":
        ColMeta("ref_idv_agency_name",   "NVARCHAR(255)", "1H",  "Referenced IDV Agency Name",              "Contract ID"),
    "contractId.referencedIDVID.PIID":
        ColMeta("ref_idv_piid",          "NVARCHAR(50)",  "1C",  "Referenced IDV PIID",                     "Contract ID"),
    "contractId.referencedIDVID.piid":
        ColMeta("ref_idv_piid",          "NVARCHAR(50)",  "1C",  "Referenced IDV PIID",                     "Contract ID"),
    "contractId.referencedIDVID.modificationNumber":
        ColMeta("ref_idv_mod_number",    "NVARCHAR(25)",  "1G",  "Referenced IDV Modification Number",      "Contract ID"),
    "contractId.subtier.code":
        ColMeta("contracting_subtier_code",  "NVARCHAR(10)", "", "Contracting Sub-tier Code",               "Contract ID"),
    "contractId.subtier.name":
        ColMeta("contracting_subtier_name",  "NVARCHAR(255)","", "Contracting Sub-tier Name",               "Contract ID"),
    "contractId.reasonForModification.code":
        ColMeta("mod_reason_code",       "NVARCHAR(5)",   "12C", "Reason for Modification Code",            "Contract ID"),
    "contractId.reasonForModification.name":
        ColMeta("mod_reason_name",       "NVARCHAR(255)", "12C", "Reason for Modification Description",     "Contract ID"),

    # ===================================================================
    # SECTION 2 – Core Data / Award Type
    # ===================================================================
    "coreData.coreVersionId":
        ColMeta("core_version",          "NVARCHAR(10)",  "",    "FPDS Schema Version",                     "Core Data"),
    "coreData.awardOrIDV":
        ColMeta("award_or_idv",          "NVARCHAR(10)",  "12B", "Award or IDV",                            "Core Data"),
    "coreData.awardOrIDVType.code":
        ColMeta("award_type_code",       "NVARCHAR(5)",   "12B", "Award/IDV Type Code",                     "Core Data"),
    "coreData.awardOrIDVType.name":
        ColMeta("award_type_name",       "NVARCHAR(100)", "12B", "Award/IDV Type Name",                     "Core Data"),
    "coreData.idvType.code":
        ColMeta("idv_type_code",         "NVARCHAR(5)",   "12A", "IDV Type Code",                           "Core Data"),
    "coreData.idvType.name":
        ColMeta("idv_type_name",         "NVARCHAR(100)", "12A", "IDV Type Name",                           "Core Data"),
    "coreData.solicitationID":
        ColMeta("solicitation_id",       "NVARCHAR(50)",  "",    "Solicitation ID",                         "Core Data"),

    # ===================================================================
    # SECTION 3 – Dates  (FPDS group 2)
    # ===================================================================
    "coreData.dates.signedDate":
        ColMeta("date_signed",           "DATE",          "2A",  "Date Signed",                             "Dates"),
    "coreData.dates.effectiveDate":
        ColMeta("perf_start_date",       "DATE",          "2B",  "Period of Performance Start Date",        "Dates"),
    "coreData.dates.currentCompletionDate":
        ColMeta("current_completion_date","DATE",         "2C",  "Current Completion Date",                 "Dates"),
    "coreData.dates.ultimateCompletionDate":
        ColMeta("ultimate_completion_date","DATE",        "2D",  "Ultimate Completion Date",                "Dates"),
    "coreData.dates.lastModifiedDate":
        ColMeta("last_modified_date",    "DATETIME2",     "2F",  "Last Modified Date/Time Stamp",           "Dates"),
    "coreData.dates.fiscalYear":
        ColMeta("fiscal_year",           "SMALLINT",      "2G",  "Fiscal Year",                             "Dates"),
    "coreData.dates.solicitationDate":
        ColMeta("solicitation_date",     "DATE",          "2H",  "Solicitation Date",                       "Dates"),
    "coreData.dates.createdDate":
        ColMeta("created_date",          "DATETIME2",     "2J",  "Record Created Date",                     "Dates"),
    "coreData.dates.preparedBy":
        ColMeta("prepared_by",           "NVARCHAR(50)",  "2I",  "Prepared By (UserID)",                    "Dates"),
    "coreData.dates.createdVia":
        ColMeta("created_via",           "NVARCHAR(5)",   "2K",  "Created Via (Batch/UI)",                  "Dates"),
    "coreData.dates.approvedDate":
        ColMeta("approved_date",         "DATE",          "",    "Approved Date",                           "Dates"),
    "coreData.dates.closedDate":
        ColMeta("closed_date",           "DATE",          "",    "Closed/Closeout Date",                    "Dates"),
    "coreData.dates.lastModifiedUser":
        ColMeta("last_modified_user",    "NVARCHAR(50)",  "2L",  "Last Modified UserID",                    "Dates"),

    # ===================================================================
    # SECTION 4 – Dollar Values  (FPDS group 3)
    # ===================================================================
    "coreData.dollarValues.obligatedAmount":
        ColMeta("action_obligation",     "DECIMAL(20,2)", "3C",  "Action Obligation (this transaction)",    "Dollars"),
    "coreData.dollarValues.baseAndAllOptionsValue":
        ColMeta("base_and_all_options",  "DECIMAL(20,2)", "3A",  "Base and All Options Value",              "Dollars"),
    "coreData.dollarValues.baseAndExercisedOptionsValue":
        ColMeta("base_and_exercised_options","DECIMAL(20,2)","3B","Base and Exercised Options Value",       "Dollars"),
    "coreData.dollarValues.nonGovernmentDollars":
        ColMeta("non_govt_dollars",      "DECIMAL(20,2)", "3D",  "Non-Government Dollar Share",             "Dollars"),
    "coreData.totalDollarValues.totalObligatedAmount":
        ColMeta("total_obligated",       "DECIMAL(20,2)", "3CT", "Total Dollars Obligated (cumulative)",    "Dollars"),
    "coreData.totalDollarValues.totalBaseAndAllOptionsValue":
        ColMeta("total_base_all_options","DECIMAL(20,2)", "3AT", "Total Base and All Options Value",        "Dollars"),
    "coreData.totalDollarValues.totalBaseAndExercisedOptionsValue":
        ColMeta("total_base_exercised",  "DECIMAL(20,2)", "3BT", "Total Base and Exercised Options Value",  "Dollars"),
    "coreData.totalDollarValues.totalNonGovernmentDollars":
        ColMeta("total_non_govt_dollars","DECIMAL(20,2)", "3DT", "Total Non-Government Dollars",            "Dollars"),

    # ===================================================================
    # SECTION 5 – Federal Organization (Awarding & Funding)  (FPDS group 4)
    # ===================================================================
    # Contracting (Awarding) hierarchy
    "coreData.federalOrganization.contractingInformation.contractingDepartment.code":
        ColMeta("dept_code",             "NVARCHAR(10)",  "4A",  "Contracting Department Code",             "Awarding Org"),
    "coreData.federalOrganization.contractingInformation.contractingDepartment.name":
        ColMeta("dept_name",             "NVARCHAR(255)", "4A",  "Contracting Department Name",             "Awarding Org"),
    "coreData.federalOrganization.contractingInformation.contractingSubtier.code":
        ColMeta("subtier_code",          "NVARCHAR(10)",  "4A",  "Contracting Sub-tier Agency Code",        "Awarding Org"),
    "coreData.federalOrganization.contractingInformation.contractingSubtier.name":
        ColMeta("subtier_name",          "NVARCHAR(255)", "4A",  "Contracting Sub-tier Agency Name",        "Awarding Org"),
    "coreData.federalOrganization.contractingInformation.contractingOffice.code":
        ColMeta("contracting_office_code","NVARCHAR(10)", "4B",  "Contracting Office Code",                 "Awarding Org"),
    "coreData.federalOrganization.contractingInformation.contractingOffice.name":
        ColMeta("contracting_office_name","NVARCHAR(255)","4B",  "Contracting Office Name",                 "Awarding Org"),
    "coreData.federalOrganization.contractingInformation.contractingOffice.regionCode":
        ColMeta("contracting_office_region","NVARCHAR(5)","",    "Contracting Office Region Code",          "Awarding Org"),
    # Funding hierarchy
    "coreData.federalOrganization.fundingInformation.fundingDepartment.code":
        ColMeta("funding_dept_code",     "NVARCHAR(10)",  "4C",  "Funding Department Code",                 "Funding Org"),
    "coreData.federalOrganization.fundingInformation.fundingDepartment.name":
        ColMeta("funding_dept_name",     "NVARCHAR(255)", "4C",  "Funding Department Name",                 "Funding Org"),
    "coreData.federalOrganization.fundingInformation.fundingSubtier.code":
        ColMeta("funding_subtier_code",  "NVARCHAR(10)",  "4C",  "Funding Sub-tier Agency Code",            "Funding Org"),
    "coreData.federalOrganization.fundingInformation.fundingSubtier.name":
        ColMeta("funding_subtier_name",  "NVARCHAR(255)", "4C",  "Funding Sub-tier Agency Name",            "Funding Org"),
    "coreData.federalOrganization.fundingInformation.fundingOffice.code":
        ColMeta("funding_office_code",   "NVARCHAR(10)",  "4D",  "Funding Office Code",                     "Funding Org"),
    "coreData.federalOrganization.fundingInformation.fundingOffice.name":
        ColMeta("funding_office_name",   "NVARCHAR(255)", "4D",  "Funding Office Name",                     "Funding Org"),
    "coreData.federalOrganization.fundingInformation.foreignFunding.code":
        ColMeta("foreign_funding_code",  "NVARCHAR(5)",   "",    "Foreign Funding Code",                    "Funding Org"),
    "coreData.federalOrganization.fundingInformation.foreignFunding.name":
        ColMeta("foreign_funding_name",  "NVARCHAR(100)", "",    "Foreign Funding Description",              "Funding Org"),
    # Treasury Account
    "coreData.federalOrganization.fundingInformation.treasuryAccountSymbol.agencyIdentifier":
        ColMeta("tas_agency_id",         "NVARCHAR(5)",   "6SC", "TAS Agency Identifier",                   "Funding Org"),
    "coreData.federalOrganization.fundingInformation.treasuryAccountSymbol.mainAccountCode":
        ColMeta("tas_main_account",      "NVARCHAR(5)",   "6SG", "TAS Main Account Code",                   "Funding Org"),
    "coreData.federalOrganization.fundingInformation.treasuryAccountSymbol.subAccountCode":
        ColMeta("tas_sub_account",       "NVARCHAR(5)",   "6SH", "TAS Sub Account Code",                    "Funding Org"),

    # ===================================================================
    # SECTION 6 – Contract Details  (FPDS group 6)
    # ===================================================================
    "coreData.contractDetails.descriptionOfContractRequirement":
        ColMeta("description",           "NVARCHAR(2000)","6M",  "Description of Contract Requirement",     "Contract Details"),
    "coreData.contractDetails.letterContract":
        ColMeta("letter_contract",       "CHAR(1)",       "",    "Letter Contract (Y/N)",                   "Contract Details"),
    "coreData.contractDetails.multiYearContract":
        ColMeta("multi_year_contract",   "CHAR(1)",       "",    "Multi-Year Contract (Y/N)",               "Contract Details"),
    "coreData.contractDetails.purchaseCardAsPaymentMethod":
        ColMeta("purchase_card_payment", "CHAR(1)",       "",    "Purchase Card as Payment Method (Y/N)",   "Contract Details"),
    "coreData.contractDetails.undefinitizedAction":
        ColMeta("undefinitized_action",  "CHAR(1)",       "",    "Undefinitized Action (Y/N)",               "Contract Details"),
    "coreData.contractDetails.consolidatedContract":
        ColMeta("consolidated_contract", "CHAR(1)",       "",    "Consolidated Contract (Y/N)",              "Contract Details"),
    "coreData.contractDetails.costOrPricingData.code":
        ColMeta("cost_pricing_data_code","NVARCHAR(5)",   "",    "Cost or Pricing Data Code",               "Contract Details"),
    "coreData.contractDetails.costOrPricingData.name":
        ColMeta("cost_pricing_data_name","NVARCHAR(100)", "",    "Cost or Pricing Data Description",        "Contract Details"),
    "coreData.contractDetails.typeOfContractPricing.code":
        ColMeta("pricing_type_code",     "NVARCHAR(5)",   "",    "Type of Contract Pricing Code",           "Contract Details"),
    "coreData.contractDetails.typeOfContractPricing.name":
        ColMeta("pricing_type_name",     "NVARCHAR(100)", "",    "Type of Contract Pricing Description",    "Contract Details"),
    "coreData.contractDetails.reasonNotCompeted.code":
        ColMeta("not_competed_reason_code","NVARCHAR(5)", "",    "Reason Not Competed Code",                "Contract Details"),
    "coreData.contractDetails.reasonNotCompeted.name":
        ColMeta("not_competed_reason_name","NVARCHAR(255)","",   "Reason Not Competed Description",         "Contract Details"),
    "coreData.contractDetails.interagencyContractingAuthority.code":
        ColMeta("interagency_auth_code", "NVARCHAR(5)",   "",    "Interagency Contracting Authority Code",  "Contract Details"),
    "coreData.contractDetails.interagencyContractingAuthority.name":
        ColMeta("interagency_auth_name", "NVARCHAR(255)", "",    "Interagency Contracting Authority Name",  "Contract Details"),
    "coreData.contractDetails.majorProgram":
        ColMeta("major_program",         "NVARCHAR(100)", "",    "Major Program",                           "Contract Details"),
    "coreData.contractDetails.programAcronym":
        ColMeta("program_acronym",       "NVARCHAR(50)",  "",    "Program Acronym",                         "Contract Details"),
    "coreData.contractDetails.nationalInterestActionCode.code":
        ColMeta("national_interest_code","NVARCHAR(10)",  "",    "National Interest Action Code",           "Contract Details"),
    "coreData.contractDetails.nationalInterestActionCode.name":
        ColMeta("national_interest_name","NVARCHAR(255)", "",    "National Interest Action Description",    "Contract Details"),
    "coreData.contractDetails.initiative.code":
        ColMeta("initiative_code",       "NVARCHAR(10)",  "6SI", "Initiative Code",                         "Contract Details"),
    "coreData.contractDetails.initiative.name":
        ColMeta("initiative_name",       "NVARCHAR(255)", "6SI", "Initiative Description",                  "Contract Details"),
    "coreData.contractDetails.coBusSizeDetermination.code":
        ColMeta("co_bus_size_code",      "NVARCHAR(5)",   "",    "CO Business Size Determination Code",     "Contract Details"),
    "coreData.contractDetails.coBusSizeDetermination.name":
        ColMeta("co_bus_size_name",      "NVARCHAR(100)", "",    "CO Business Size Determination Name",     "Contract Details"),
    "coreData.contractDetails.seaTransportation.code":
        ColMeta("sea_transport_code",    "NVARCHAR(5)",   "",    "Sea Transportation Code",                 "Contract Details"),
    "coreData.contractDetails.seaTransportation.name":
        ColMeta("sea_transport_name",    "NVARCHAR(100)", "",    "Sea Transportation Description",          "Contract Details"),
    "coreData.contractDetails.contingencyHumanitarianPeacekeepingOperation.code":
        ColMeta("contingency_op_code",   "NVARCHAR(5)",   "",    "Contingency/Humanitarian Operation Code", "Contract Details"),
    "coreData.contractDetails.contingencyHumanitarianPeacekeepingOperation.name":
        ColMeta("contingency_op_name",   "NVARCHAR(100)", "",    "Contingency/Humanitarian Operation Name", "Contract Details"),
    "coreData.contractDetails.walshHealeyAct":
        ColMeta("walsh_healey_act",      "NVARCHAR(5)",   "",    "Walsh-Healey Act (Y/N/NA)",               "Contract Details"),
    "coreData.contractDetails.serviceContractAct":
        ColMeta("service_contract_act",  "NVARCHAR(5)",   "",    "Service Contract Act (Y/N/NA)",           "Contract Details"),
    "coreData.contractDetails.davisBaconAct":
        ColMeta("davis_bacon_act",       "NVARCHAR(5)",   "",    "Davis-Bacon Act (Y/N/NA)",                "Contract Details"),
    "coreData.contractDetails.clingerCohenAct":
        ColMeta("clinger_cohen_act",     "NVARCHAR(5)",   "",    "Clinger-Cohen Act (Y/N/NA)",              "Contract Details"),
    "coreData.contractDetails.numberOfActions":
        ColMeta("number_of_actions",     "INT",           "",    "Number of Actions",                       "Contract Details"),
    "coreData.contractDetails.typeOfAgreement.code":
        ColMeta("agreement_type_code",   "NVARCHAR(5)",   "OT8C","Type of Agreement Code (OT)",            "Contract Details"),
    "coreData.contractDetails.typeOfAgreement.name":
        ColMeta("agreement_type_name",   "NVARCHAR(100)", "OT8C","Type of Agreement Description (OT)",     "Contract Details"),
    "coreData.contractDetails.dodAcquisitionProgram.code":
        ColMeta("dod_acq_program_code",  "NVARCHAR(10)",  "8B",  "DoD Acquisition Program Code",            "Contract Details"),
    "coreData.contractDetails.dodAcquisitionProgram.name":
        ColMeta("dod_acq_program_name",  "NVARCHAR(255)", "8B",  "DoD Acquisition Program Description",    "Contract Details"),
    "coreData.contractDetails.informationTechnologyCommercialItemCategory.code":
        ColMeta("it_commercial_item_code","NVARCHAR(5)",  "",    "IT Commercial Item Category Code",        "Contract Details"),
    "coreData.contractDetails.informationTechnologyCommercialItemCategory.name":
        ColMeta("it_commercial_item_name","NVARCHAR(100)","",    "IT Commercial Item Category Name",        "Contract Details"),
    "coreData.contractDetails.recoveredMaterialsClauses.code":
        ColMeta("recovered_materials_code","NVARCHAR(5)", "",    "Recovered Materials/Sustainability Code", "Contract Details"),
    "coreData.contractDetails.recoveredMaterialsClauses.name":
        ColMeta("recovered_materials_name","NVARCHAR(100)","",   "Recovered Materials/Sustainability Name", "Contract Details"),

    # ===================================================================
    # SECTION 7 – Product / Service  (FPDS group 8)
    # ===================================================================
    "coreData.productOrServiceInformation.productOrServiceCode.code":
        ColMeta("psc_code",              "NVARCHAR(10)",  "8A",  "Product or Service Code (PSC)",           "Product/Service"),
    "coreData.productOrServiceInformation.productOrServiceCode.name":
        ColMeta("psc_name",              "NVARCHAR(255)", "8C",  "PSC Description",                         "Product/Service"),
    "coreData.productOrServiceInformation.principalNAICSCode.code":
        ColMeta("naics_code",            "NVARCHAR(10)",  "",    "NAICS Code",                              "Product/Service"),
    "coreData.productOrServiceInformation.principalNAICSCode.name":
        ColMeta("naics_name",            "NVARCHAR(255)", "",    "NAICS Description",                       "Product/Service"),
    "coreData.productOrServiceInformation.claimantProgramCode.code":
        ColMeta("claimant_program_code", "NVARCHAR(5)",   "",    "Claimant Program Code (DoD)",             "Product/Service"),
    "coreData.productOrServiceInformation.claimantProgramCode.name":
        ColMeta("claimant_program_name", "NVARCHAR(100)", "",    "Claimant Program Description (DoD)",      "Product/Service"),
    "coreData.productOrServiceInformation.contractBundling.code":
        ColMeta("contract_bundling_code","NVARCHAR(5)",   "",    "Contract Bundling Code",                  "Product/Service"),
    "coreData.productOrServiceInformation.contractBundling.name":
        ColMeta("contract_bundling_name","NVARCHAR(100)", "",    "Contract Bundling Description",           "Product/Service"),
    "coreData.productOrServiceInformation.systemEquipmentCode.code":
        ColMeta("system_equipment_code", "NVARCHAR(5)",   "",    "System Equipment Code (DoD)",             "Product/Service"),
    "coreData.productOrServiceInformation.systemEquipmentCode.name":
        ColMeta("system_equipment_name", "NVARCHAR(100)", "",    "System Equipment Description (DoD)",      "Product/Service"),

    # ===================================================================
    # SECTION 8 – Competition  (FPDS group 10)
    # ===================================================================
    "coreData.competitionInformation.extentCompeted.code":
        ColMeta("extent_competed_code",  "NVARCHAR(5)",   "10A", "Extent Competed Code",                    "Competition"),
    "coreData.competitionInformation.extentCompeted.name":
        ColMeta("extent_competed_name",  "NVARCHAR(100)", "10A", "Extent Competed Description",             "Competition"),
    "coreData.competitionInformation.solicitationProcedures.code":
        ColMeta("solicitation_proc_code","NVARCHAR(5)",   "10M", "Solicitation Procedures Code",            "Competition"),
    "coreData.competitionInformation.solicitationProcedures.name":
        ColMeta("solicitation_proc_name","NVARCHAR(100)", "10M", "Solicitation Procedures Description",     "Competition"),
    "coreData.competitionInformation.typeOfSetAside.code":
        ColMeta("set_aside_code",        "NVARCHAR(5)",   "",    "Type of Set-Aside Code",                  "Competition"),
    "coreData.competitionInformation.typeOfSetAside.name":
        ColMeta("set_aside_name",        "NVARCHAR(100)", "",    "Type of Set-Aside Description",           "Competition"),
    "coreData.competitionInformation.evaluatedPreference.code":
        ColMeta("eval_preference_code",  "NVARCHAR(5)",   "",    "Evaluated Preference Code",               "Competition"),
    "coreData.competitionInformation.evaluatedPreference.name":
        ColMeta("eval_preference_name",  "NVARCHAR(100)", "",    "Evaluated Preference Description",        "Competition"),
    "coreData.competitionInformation.research.code":
        ColMeta("research_code",         "NVARCHAR(5)",   "",    "Research Code",                           "Competition"),
    "coreData.competitionInformation.research.name":
        ColMeta("research_name",         "NVARCHAR(100)", "",    "Research Description",                    "Competition"),
    "coreData.competitionInformation.fairOpportunityLimitedSources.code":
        ColMeta("fair_opp_limited_code", "NVARCHAR(5)",   "",    "Fair Opportunity Limited Sources Code",   "Competition"),
    "coreData.competitionInformation.fairOpportunityLimitedSources.name":
        ColMeta("fair_opp_limited_name", "NVARCHAR(100)", "",    "Fair Opportunity Limited Sources Desc",   "Competition"),
    "coreData.competitionInformation.otherThanFullAndOpenCompetition.code":
        ColMeta("other_full_open_code",  "NVARCHAR(5)",   "",    "Other Than Full & Open Competition Code", "Competition"),
    "coreData.competitionInformation.otherThanFullAndOpenCompetition.name":
        ColMeta("other_full_open_name",  "NVARCHAR(100)", "",    "Other Than Full & Open Competition Desc", "Competition"),
    "coreData.competitionInformation.numberOfOffersReceived":
        ColMeta("offers_received",       "SMALLINT",      "",    "Number of Offers Received",               "Competition"),
    "coreData.competitionInformation.commercialItemAcquisitionProcedures.code":
        ColMeta("commercial_item_acq_code","NVARCHAR(5)", "",    "Commercial Item Acquisition Procedures Code","Competition"),
    "coreData.competitionInformation.commercialItemAcquisitionProcedures.name":
        ColMeta("commercial_item_acq_name","NVARCHAR(100)","",   "Commercial Item Acquisition Procedures Desc","Competition"),
    "coreData.competitionInformation.smallBusinessCompetitivenessDemonstrationProgram":
        ColMeta("sb_competitiveness_demo","CHAR(1)",      "",    "SB Competitiveness Demo Program (Y/N)",   "Competition"),
    "coreData.competitionInformation.a76FairActAction":
        ColMeta("a76_fair_act",          "CHAR(1)",       "",    "A-76/FAIR Act Action (Y/N)",              "Competition"),
    "coreData.competitionInformation.fedBizOpps":
        ColMeta("fed_biz_opps",          "CHAR(1)",       "",    "FedBizOpps / SAM Posted (Y/N)",           "Competition"),
    "coreData.competitionInformation.localAreaSetAside":
        ColMeta("local_set_aside",       "CHAR(1)",       "",    "Local Area Set-Aside (Y/N)",              "Competition"),
    "coreData.competitionInformation.priceEvaluationPercentDifference":
        ColMeta("price_eval_pct_diff",   "DECIMAL(10,4)", "",    "Price Eval % Difference (HUBZone)",       "Competition"),
    "coreData.competitionInformation.nonTraditionalGovernmentEntityParticipation.code":
        ColMeta("nontrad_entity_code",   "NVARCHAR(5)",   "10T", "Non-Traditional Entity Participation Code","Competition"),
    "coreData.competitionInformation.nonTraditionalGovernmentEntityParticipation.name":
        ColMeta("nontrad_entity_name",   "NVARCHAR(100)", "10T", "Non-Traditional Entity Participation Desc","Competition"),

    # ===================================================================
    # SECTION 9 – Awardee / Entity Data  (FPDS groups 9, 13)
    # ===================================================================
    "awardeeOrRecipient.uniqueEntityIdentifier":
        ColMeta("awardee_uei",           "NVARCHAR(20)",  "9M",  "Awardee Unique Entity Identifier (SAM)", "Awardee"),
    "awardeeOrRecipient.cageCode":
        ColMeta("awardee_cage_code",     "NVARCHAR(10)",  "",    "Awardee CAGE Code",                       "Awardee"),
    "awardeeOrRecipient.legalBusinessName":
        ColMeta("awardee_name",          "NVARCHAR(255)", "13GG","Awardee Legal Business Name",             "Awardee"),
    "awardeeOrRecipient.doingBusinessAsName":
        ColMeta("awardee_dba_name",      "NVARCHAR(255)", "13HH","Awardee DBA Name",                        "Awardee"),
    "awardeeOrRecipient.awardeeDataSource":
        ColMeta("awardee_data_source",   "NVARCHAR(20)",  "",    "Awardee Data Source",                     "Awardee"),
    "awardeeOrRecipient.awardeeAlternateSiteCode":
        ColMeta("awardee_alt_site_code", "NVARCHAR(20)",  "",    "Awardee Alternate Site Code",             "Awardee"),
    # Awardee Location
    "awardeeOrRecipient.awardeeLocation.streetAddress1":
        ColMeta("awardee_addr1",         "NVARCHAR(255)", "13JJ","Awardee Address Line 1",                  "Awardee"),
    "awardeeOrRecipient.awardeeLocation.streetAddress2":
        ColMeta("awardee_addr2",         "NVARCHAR(255)", "13KK","Awardee Address Line 2",                  "Awardee"),
    "awardeeOrRecipient.awardeeLocation.city":
        ColMeta("awardee_city",          "NVARCHAR(100)", "13MM","Awardee City",                            "Awardee"),
    "awardeeOrRecipient.awardeeLocation.state.code":
        ColMeta("awardee_state_code",    "NVARCHAR(5)",   "13NN","Awardee State Code",                      "Awardee"),
    "awardeeOrRecipient.awardeeLocation.state.name":
        ColMeta("awardee_state_name",    "NVARCHAR(50)",  "13NN","Awardee State Name",                      "Awardee"),
    "awardeeOrRecipient.awardeeLocation.zip":
        ColMeta("awardee_zip",           "NVARCHAR(20)",  "13PP","Awardee ZIP Code",                        "Awardee"),
    "awardeeOrRecipient.awardeeLocation.country.code":
        ColMeta("awardee_country_code",  "NVARCHAR(5)",   "13QQ","Awardee Country Code",                    "Awardee"),
    "awardeeOrRecipient.awardeeLocation.country.name":
        ColMeta("awardee_country_name",  "NVARCHAR(100)", "13QQ","Awardee Country Name",                    "Awardee"),
    "awardeeOrRecipient.awardeeLocation.phoneNumber":
        ColMeta("awardee_phone",         "NVARCHAR(30)",  "13RR","Awardee Phone Number",                    "Awardee"),
    "awardeeOrRecipient.awardeeLocation.faxNumber":
        ColMeta("awardee_fax",           "NVARCHAR(30)",  "13SS","Awardee Fax Number",                      "Awardee"),
    "awardeeOrRecipient.awardeeLocation.congressionalDistrict":
        ColMeta("awardee_cong_district", "NVARCHAR(10)",  "9F",  "Awardee Congressional District",          "Awardee"),
    # Awardee Registration
    "awardeeOrRecipient.awardeeRegistrationDetails.registrationDate":
        ColMeta("awardee_reg_date",      "DATE",          "",    "Awardee SAM Registration Date",           "Awardee"),
    "awardeeOrRecipient.awardeeRegistrationDetails.renewalDate":
        ColMeta("awardee_renewal_date",  "DATE",          "",    "Awardee SAM Renewal Date",                "Awardee"),
    # Consortia (OT)
    "awardeeOrRecipient.consortia":
        ColMeta("consortia",             "NVARCHAR(5)",   "9N",  "Consortia (Y/N)",                         "Awardee"),
    "awardeeOrRecipient.primaryConsortiumMemberUEI":
        ColMeta("primary_consortium_uei","NVARCHAR(20)",  "9O",  "Primary Consortia Member UEI",            "Awardee"),

    # ===================================================================
    # SECTION 10 – Awardee Business Types / Socioeconomic Flags
    # ===================================================================
    # Government type flags
    "awardeeOrRecipient.awardeeBusinessTypes.isUsFederalGovernment.usFederalGovernment":
        ColMeta("is_us_fed_govt",        "NVARCHAR(5)",   "",    "US Federal Government (YES/NO)",          "Business Types"),
    "awardeeOrRecipient.awardeeBusinessTypes.isUsFederalGovernment.federalAgency":
        ColMeta("is_federal_agency",     "NVARCHAR(5)",   "",    "Federal Agency (YES/NO)",                 "Business Types"),
    "awardeeOrRecipient.awardeeBusinessTypes.isUsFederalGovernment.federallyFundedResearchAndDevelopmentCorp":
        ColMeta("is_ffrdc",              "NVARCHAR(5)",   "",    "FFRDC (YES/NO)",                          "Business Types"),
    "awardeeOrRecipient.awardeeBusinessTypes.usStateGovernment":
        ColMeta("is_state_govt",         "NVARCHAR(5)",   "",    "US State Government (YES/NO)",            "Business Types"),
    "awardeeOrRecipient.awardeeBusinessTypes.foreignGovernment":
        ColMeta("is_foreign_govt",       "NVARCHAR(5)",   "",    "Foreign Government (YES/NO)",             "Business Types"),
    "awardeeOrRecipient.awardeeBusinessTypes.usTribalGovernment":
        ColMeta("is_tribal_govt",        "NVARCHAR(5)",   "",    "US Tribal Government (YES/NO)",           "Business Types"),
    "awardeeOrRecipient.awardeeBusinessTypes.isUsLocalGovernment.usLocalGovernment":
        ColMeta("is_local_govt",         "NVARCHAR(5)",   "",    "US Local Government (YES/NO)",            "Business Types"),
    # Business size
    "awardeeOrRecipient.awardeeBusinessTypes.isSmallBusiness.smallBusiness":
        ColMeta("is_small_business",     "NVARCHAR(5)",   "",    "Small Business (YES/NO)",                 "Business Types"),
    "awardeeOrRecipient.awardeeBusinessTypes.isSmallBusiness.verySmallBusiness":
        ColMeta("is_very_small_biz",     "NVARCHAR(5)",   "",    "Very Small Business (YES/NO)",            "Business Types"),
    "awardeeOrRecipient.awardeeBusinessTypes.largeBusiness":
        ColMeta("is_large_business",     "NVARCHAR(5)",   "",    "Large Business (YES/NO)",                 "Business Types"),
    # Veteran-owned
    "awardeeOrRecipient.awardeeBusinessTypes.veteranOwnedBusiness":
        ColMeta("is_veteran_owned",      "NVARCHAR(5)",   "",    "Veteran-Owned Business (YES/NO)",         "Business Types"),
    "awardeeOrRecipient.awardeeBusinessTypes.serviceDisabledVeteranOwnedBusiness":
        ColMeta("is_sdvosb",             "NVARCHAR(5)",   "",    "Service-Disabled Veteran-Owned SB (YES/NO)","Business Types"),
    # Woman-owned
    "awardeeOrRecipient.awardeeBusinessTypes.womanOwnedBusiness":
        ColMeta("is_woman_owned",        "NVARCHAR(5)",   "",    "Woman-Owned Business (YES/NO)",           "Business Types"),
    "awardeeOrRecipient.awardeeBusinessTypes.womenOwnedSmallBusiness":
        ColMeta("is_wosb",               "NVARCHAR(5)",   "",    "Women-Owned Small Business (YES/NO)",     "Business Types"),
    "awardeeOrRecipient.awardeeBusinessTypes.economicallyDisadvantagedWOSB":
        ColMeta("is_edwosb",             "NVARCHAR(5)",   "",    "Economically Disadvantaged WOSB (YES/NO)","Business Types"),
    # Minority-owned
    "awardeeOrRecipient.awardeeBusinessTypes.minorityOwnedBusiness":
        ColMeta("is_minority_owned",     "NVARCHAR(5)",   "",    "Minority-Owned Business (YES/NO)",        "Business Types"),
    "awardeeOrRecipient.awardeeBusinessTypes.subContinentAsianAmericanOwnedBusiness":
        ColMeta("is_asian_subcontinent", "NVARCHAR(5)",   "",    "Subcontinent Asian-American Owned (YES/NO)","Business Types"),
    "awardeeOrRecipient.awardeeBusinessTypes.asianPacificAmericanOwnedBusiness":
        ColMeta("is_asian_pacific",      "NVARCHAR(5)",   "",    "Asian-Pacific American Owned (YES/NO)",   "Business Types"),
    "awardeeOrRecipient.awardeeBusinessTypes.blackAmericanOwnedBusiness":
        ColMeta("is_black_american",     "NVARCHAR(5)",   "",    "Black American-Owned Business (YES/NO)",  "Business Types"),
    "awardeeOrRecipient.awardeeBusinessTypes.hispanicAmericanOwnedBusiness":
        ColMeta("is_hispanic_american",  "NVARCHAR(5)",   "",    "Hispanic American-Owned Business (YES/NO)","Business Types"),
    "awardeeOrRecipient.awardeeBusinessTypes.nativeAmericanOwnedBusiness":
        ColMeta("is_native_american",    "NVARCHAR(5)",   "",    "Native American-Owned Business (YES/NO)", "Business Types"),
    "awardeeOrRecipient.awardeeBusinessTypes.otherMinorityOwnedBusiness":
        ColMeta("is_other_minority",     "NVARCHAR(5)",   "",    "Other Minority-Owned Business (YES/NO)",  "Business Types"),
    # SBA programs
    "awardeeOrRecipient.awardeeBusinessTypes.sbaCertifiedSmallDisadvantagedBusiness":
        ColMeta("is_sba_sdb",            "NVARCHAR(5)",   "",    "SBA Certified SDB (YES/NO)",              "Business Types"),
    "awardeeOrRecipient.awardeeBusinessTypes.sbaCertified8AProgramParticipant":
        ColMeta("is_8a",                 "NVARCHAR(5)",   "",    "SBA Certified 8(a) (YES/NO)",             "Business Types"),
    "awardeeOrRecipient.awardeeBusinessTypes.hubZoneFirm":
        ColMeta("is_hubzone",            "NVARCHAR(5)",   "",    "HUBZone Firm (YES/NO)",                   "Business Types"),
    # Native/tribal entities
    "awardeeOrRecipient.awardeeBusinessTypes.communityDevelopmentCorporationOwnedConcern":
        ColMeta("is_cdc_owned",          "NVARCHAR(5)",   "",    "Community Development Corp Owned (YES/NO)","Business Types"),
    "awardeeOrRecipient.awardeeBusinessTypes.alaskanNativeCorporationOwnedFirm":
        ColMeta("is_alaska_native_corp", "NVARCHAR(5)",   "",    "Alaskan Native Corp-Owned Firm (YES/NO)", "Business Types"),
    "awardeeOrRecipient.awardeeBusinessTypes.nativeHawaiianOrganizationOwnedFirm":
        ColMeta("is_native_hawaiian",    "NVARCHAR(5)",   "",    "Native Hawaiian Org-Owned Firm (YES/NO)", "Business Types"),
    "awardeeOrRecipient.awardeeBusinessTypes.indianTribeFederallyRecognized":
        ColMeta("is_indian_tribe",       "NVARCHAR(5)",   "",    "Federally Recognized Indian Tribe (YES/NO)","Business Types"),
    # Other
    "awardeeOrRecipient.awardeeBusinessTypes.nonprofitOrganization":
        ColMeta("is_nonprofit",          "NVARCHAR(5)",   "",    "Nonprofit Organization (YES/NO)",         "Business Types"),
    "awardeeOrRecipient.awardeeBusinessTypes.educationalInstitution":
        ColMeta("is_educational",        "NVARCHAR(5)",   "",    "Educational Institution (YES/NO)",        "Business Types"),
    "awardeeOrRecipient.awardeeBusinessTypes.laborSurplusAreaFirm":
        ColMeta("is_labor_surplus",      "NVARCHAR(5)",   "",    "Labor Surplus Area Firm (YES/NO)",        "Business Types"),

    # ===================================================================
    # SECTION 11 – Place of Performance  (FPDS group 9)
    # ===================================================================
    "placeOfPerformance.principalPlaceOfPerformance.locationCode":
        ColMeta("pop_location_code",     "NVARCHAR(20)",  "9C",  "Place of Performance Location Code",      "Place of Performance"),
    "placeOfPerformance.principalPlaceOfPerformance.city.code":
        ColMeta("pop_city_code",         "NVARCHAR(10)",  "",    "Place of Performance City Code",          "Place of Performance"),
    "placeOfPerformance.principalPlaceOfPerformance.city.name":
        ColMeta("pop_city_name",         "NVARCHAR(100)", "",    "Place of Performance City",               "Place of Performance"),
    "placeOfPerformance.principalPlaceOfPerformance.state.code":
        ColMeta("pop_state_code",        "NVARCHAR(5)",   "",    "Place of Performance State Code",         "Place of Performance"),
    "placeOfPerformance.principalPlaceOfPerformance.state.name":
        ColMeta("pop_state_name",        "NVARCHAR(50)",  "",    "Place of Performance State",              "Place of Performance"),
    "placeOfPerformance.principalPlaceOfPerformance.zip":
        ColMeta("pop_zip",               "NVARCHAR(20)",  "9K",  "Place of Performance ZIP",                "Place of Performance"),
    "placeOfPerformance.principalPlaceOfPerformance.country.code":
        ColMeta("pop_country_code",      "NVARCHAR(5)",   "",    "Place of Performance Country Code",       "Place of Performance"),
    "placeOfPerformance.principalPlaceOfPerformance.country.name":
        ColMeta("pop_country_name",      "NVARCHAR(100)", "",    "Place of Performance Country",            "Place of Performance"),
    "placeOfPerformance.principalPlaceOfPerformance.congressionalDistrict":
        ColMeta("pop_cong_district",     "NVARCHAR(10)",  "9G",  "Place of Performance Congressional District","Place of Performance"),

    # ===================================================================
    # SECTION 12 – Parent Entity (Unrevealed data only)
    # ===================================================================
    "awardeeOrRecipient.immediateParent.uniqueEntityIdentifier":
        ColMeta("parent_uei",            "NVARCHAR(20)",  "",    "Immediate Parent UEI",                    "Parent Entity"),
    "awardeeOrRecipient.immediateParent.legalBusinessName":
        ColMeta("parent_name",           "NVARCHAR(255)", "",    "Immediate Parent Legal Business Name",    "Parent Entity"),
    "awardeeOrRecipient.domesticParent.uniqueEntityIdentifier":
        ColMeta("domestic_parent_uei",   "NVARCHAR(20)",  "",    "Domestic Ultimate Parent UEI",            "Parent Entity"),
    "awardeeOrRecipient.domesticParent.legalBusinessName":
        ColMeta("domestic_parent_name",  "NVARCHAR(255)", "",    "Domestic Ultimate Parent Name",           "Parent Entity"),

    # ===================================================================
    # SECTION 13 – Pipeline metadata (added by sam_contract_awards.py)
    # ===================================================================
    "source_fiscal_year":
        ColMeta("source_fiscal_year",    "SMALLINT",      "",    "Pipeline: Source Fiscal Year",            "Pipeline"),
    "source_file":
        ColMeta("source_file",           "NVARCHAR(100)", "",    "Pipeline: Source CSV Filename",           "Pipeline"),
}


# ---------------------------------------------------------------------------
# Build a lowercase-key lookup for case-insensitive fallback matching
# ---------------------------------------------------------------------------
_LOWER_MAP: dict[str, str] = {k.lower(): k for k in COLUMN_MAP}


def _resolve_key(raw: str) -> str | None:
    """Return the canonical key for a raw header, or None if not found."""
    if raw in COLUMN_MAP:
        return raw
    low = raw.lower()
    return _LOWER_MAP.get(low)


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def get_short_name(raw_header: str) -> str:
    """
    Return the short SQL column name for a raw CSV header.
    Falls back to a normalized version of the raw header if not in the map.
    """
    key = _resolve_key(raw_header)
    if key:
        return COLUMN_MAP[key].short_name
    # Fallback: strip dots, lowercase, replace special chars
    fallback = re.sub(r"[^a-z0-9]+", "_", raw_header.lower()).strip("_")
    return fallback[:128]   # SQL Server max column name length


def get_sql_type(raw_header: str) -> str:
    """Return the SQL Server type for a raw CSV header."""
    key = _resolve_key(raw_header)
    if key:
        return COLUMN_MAP[key].sql_type
    return "NVARCHAR(512)"


def rename_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rename all columns in *df* from raw SAM.gov dot-notation headers
    to short SQL-safe names.  Duplicate short names get a numeric suffix.
    """
    new_names: list[str] = []
    seen: dict[str, int] = {}

    for col in df.columns:
        short = get_short_name(col)
        if short in seen:
            seen[short] += 1
            short = f"{short}_{seen[short]}"
        else:
            seen[short] = 0
        new_names.append(short)

    df.columns = new_names
    return df


def print_mapping_table(section: str | None = None) -> None:
    """Pretty-print the mapping, optionally filtered by section."""
    header = f"{'Raw CSV Header':<80} {'Short Name':<40} {'SQL Type':<22} {'FPDS ID':<8} {'Label'}"
    print(header)
    print("-" * 200)
    for raw, meta in COLUMN_MAP.items():
        if section and meta.section != section:
            continue
        print(f"{raw:<80} {meta.short_name:<40} {meta.sql_type:<22} {meta.fpds_id:<8} {meta.label}")


def generate_rename_report(df: pd.DataFrame) -> pd.DataFrame:
    """
    Given a loaded raw DataFrame, return a report DataFrame showing:
    raw header | short name | sql type | fpds_id | label | section | in_map (Y/N)
    """
    rows = []
    for col in df.columns:
        key = _resolve_key(col)
        if key:
            m = COLUMN_MAP[key]
            rows.append({
                "raw_header": col,
                "short_name": m.short_name,
                "sql_type":   m.sql_type,
                "fpds_id":    m.fpds_id,
                "label":      m.label,
                "section":    m.section,
                "in_map":     "Y",
            })
        else:
            rows.append({
                "raw_header": col,
                "short_name": get_short_name(col),
                "sql_type":   "NVARCHAR(512)",
                "fpds_id":    "",
                "label":      "(unmapped – auto-normalized)",
                "section":    "Unknown",
                "in_map":     "N",
            })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# CLI: python sam_column_mapping.py --print-all
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse, sys

    parser = argparse.ArgumentParser(description="Print SAM.gov column mapping")
    parser.add_argument("--section", help="Filter by section name (e.g. 'Dollars')")
    parser.add_argument("--csv", help="Path to a raw SAM CSV to generate a rename report for")
    parser.add_argument("--out-report", help="Write rename report CSV to this path")
    args = parser.parse_args()

    if args.csv:
        df_raw = pd.read_csv(args.csv, nrows=0, dtype=str)
        report = generate_rename_report(df_raw)
        print(report.to_string(index=False))
        if args.out_report:
            report.to_csv(args.out_report, index=False)
            print(f"\nReport saved → {args.out_report}")
    else:
        print_mapping_table(section=args.section)
        total = len(COLUMN_MAP)
        sections = sorted({m.section for m in COLUMN_MAP.values()})
        print(f"\nTotal mapped columns: {total}")
        print(f"Sections: {', '.join(sections)}")
