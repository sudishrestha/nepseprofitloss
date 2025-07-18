# Requirements Document

## Introduction

This feature involves creating a standalone Share Portfolio Dashboard using Bootstrap, HTML, and JavaScript. The application will allow users to upload two CSV files (WACC data and Share data) and calculate profit/loss analysis by comparing purchase rates with current market prices. The dashboard will be completely client-side, requiring no backend server, and will provide an intuitive interface for portfolio analysis.

## Requirements

### Requirement 1

**User Story:** As a portfolio investor, I want to upload two CSV files (WACC and Share data) so that I can analyze my portfolio's performance without needing a server.

#### Acceptance Criteria

1. WHEN the user visits the application THEN the system SHALL display a clean interface with two file upload inputs
2. WHEN the user selects a WACC CSV file THEN the system SHALL validate it is a CSV format
3. WHEN the user selects a Share data CSV file THEN the system SHALL validate it is a CSV format
4. WHEN both files are selected and user clicks "Analyze Portfolio" THEN the system SHALL process both files client-side
5. IF either file is missing THEN the system SHALL display an appropriate warning message

### Requirement 2

**User Story:** As a portfolio investor, I want the system to automatically calculate profit/loss metrics so that I can quickly assess my portfolio performance.

#### Acceptance Criteria

1. WHEN both CSV files are processed THEN the system SHALL match scrip names between WACC and Share data
2. WHEN calculating purchase totals THEN the system SHALL multiply quantity by WACC rate
3. WHEN calculating current values THEN the system SHALL multiply quantity by Last Transaction Price (LTP)
4. WHEN calculating profit/loss THEN the system SHALL subtract purchase total from current value
5. WHEN calculating percentage profit/loss THEN the system SHALL divide profit/loss by purchase total and multiply by 100
6. IF a scrip exists in share data but not in WACC data THEN the system SHALL handle it gracefully with empty purchase rate

### Requirement 3

**User Story:** As a portfolio investor, I want to see my portfolio data in a well-formatted table so that I can easily review individual holdings and totals.

#### Acceptance Criteria

1. WHEN data is processed THEN the system SHALL display results in a responsive Bootstrap table
2. WHEN displaying profit/loss values THEN the system SHALL color-code positive values as green and negative as red
3. WHEN displaying the table THEN the system SHALL include all original columns plus calculated columns
4. WHEN displaying totals THEN the system SHALL show total purchase amount, total profit/loss, and total percentage
5. IF no data is available THEN the system SHALL display a "No data uploaded" message

### Requirement 4

**User Story:** As a portfolio investor, I want the application to work entirely in my browser so that my sensitive financial data never leaves my device.

#### Acceptance Criteria

1. WHEN processing CSV files THEN the system SHALL parse them entirely client-side using JavaScript
2. WHEN performing calculations THEN the system SHALL execute all logic in the browser
3. WHEN storing temporary data THEN the system SHALL only use browser memory, not external servers
4. WHEN the page is refreshed THEN the system SHALL clear all previously uploaded data
5. IF the user wants to analyze different files THEN the system SHALL allow re-uploading without page refresh

### Requirement 5

**User Story:** As a portfolio investor, I want the application to be responsive and work on different devices so that I can check my portfolio on mobile or desktop.

#### Acceptance Criteria

1. WHEN accessing the application on mobile devices THEN the system SHALL display properly formatted responsive layout
2. WHEN viewing tables on small screens THEN the system SHALL provide horizontal scrolling for table content
3. WHEN using touch devices THEN the system SHALL support touch interactions for file selection
4. WHEN the screen size changes THEN the system SHALL adapt the layout accordingly
5. IF the device has limited screen space THEN the system SHALL prioritize essential information visibility

### Requirement 6

**User Story:** As a portfolio investor, I want clear error handling and user feedback so that I understand what's happening when something goes wrong.

#### Acceptance Criteria

1. WHEN an invalid CSV file is uploaded THEN the system SHALL display a clear error message
2. WHEN CSV parsing fails THEN the system SHALL show specific error details
3. WHEN required columns are missing THEN the system SHALL identify which columns are needed
4. WHEN calculations encounter invalid data THEN the system SHALL handle errors gracefully
5. IF the browser doesn't support required features THEN the system SHALL display compatibility warnings
