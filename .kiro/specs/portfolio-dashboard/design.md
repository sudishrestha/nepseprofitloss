# Design Document

## Overview

The Portfolio Dashboard will be a single-page application built with HTML5, Bootstrap 5, and vanilla JavaScript. The application will leverage client-side CSV parsing using Papa Parse library to process financial data entirely in the browser. The design emphasizes simplicity, security (no server-side data transmission), and responsive user experience across devices.

## Architecture

### Client-Side Architecture

```
┌─────────────────────────────────────────┐
│              Browser                    │
├─────────────────────────────────────────┤
│  HTML Structure (Bootstrap Layout)      │
├─────────────────────────────────────────┤
│  JavaScript Application Layer           │
│  ├── File Upload Handler                │
│  ├── CSV Parser (Papa Parse)            │
│  ├── Data Processing Engine             │
│  ├── Calculation Engine                 │
│  └── UI Renderer                        │
├─────────────────────────────────────────┤
│  CSS Styling (Bootstrap + Custom)       │
└─────────────────────────────────────────┘
```

### Data Flow

1. User selects CSV files → File Upload Handler
2. Files validated → CSV Parser processes data
3. Parsed data → Data Processing Engine matches and merges
4. Merged data → Calculation Engine computes metrics
5. Calculated results → UI Renderer displays table

## Components and Interfaces

### 1. File Upload Component

**Purpose:** Handle CSV file selection, validation, and caching
**Interface:**

```javascript
class FileUploadHandler {
  validateFile(file) // Returns boolean
  readFile(file) // Returns Promise<string>
  handleFileSelection(waccFile, shareFile) // Main handler
  saveToLocalStorage(waccData, shareData) // Saves parsed data to browser localStorage
  loadFromLocalStorage() // Retrieves cached data if available
}
```

### 2. CSV Parser Component

**Purpose:** Parse CSV content into JavaScript objects
**Interface:**

```javascript
class CSVParser {
  parseCSV(csvContent) // Returns Array<Object>
  validateHeaders(data, requiredHeaders) // Returns boolean
}
```

### 3. Data Processing Engine

**Purpose:** Match and merge WACC and Share data
**Interface:**

```javascript
class DataProcessor {
  buildScripMap(waccData) // Returns Map<string, Object>
  mergeData(waccMap, shareData) // Returns Array<Object>
  normalizeScripName(name) // Returns string
}
```

### 4. Calculation Engine

**Purpose:** Perform financial calculations
**Interface:**

```javascript
class CalculationEngine {
  calculateTotalCostOfCapital(quantity, waccRate) // Returns number: quantity * waccRate
  calculateCurrentValue(quantity, ltp) // Returns number: quantity * ltp
  calculateDifference(currentValue, totalCostOfCapital) // Returns number: currentValue - totalCostOfCapital
  calculateDifferencePercentage(difference, totalCostOfCapital) // Returns number: (difference / totalCostOfCapital) * 100
  calculateTotals(processedData) // Returns Object with totals for all calculated columns
}
```

### 5. UI Renderer

**Purpose:** Generate and update DOM elements
**Interface:**

```javascript
class UIRenderer {
  renderTable(data, headers) // Updates DOM
  renderTotals(totals) // Updates DOM
  showError(message) // Updates DOM
  showNoDataMessage() // Updates DOM
  applyColorCoding(value, element) // Updates DOM based on value: >0 green, <0 red, =0 blue
}
```

## Data Models

### WACC Data Model

```javascript
{
  "Scrip Name": string,
  "WACC Rate": number,
  // Additional columns as needed
}
```

### Share Data Model

```javascript
{
  "Scrip Name": string, // Main identifier for matching
  "Current Balance": number, // Quantity held
  "Last Transaction Price (LTP)": number, // Current market price
  // Additional columns from sharevalue.csv preserved
}
```

### Processed Data Model

```javascript
{
  // Original share data columns from sharevalue.csv
  ...shareData,
  // New calculated columns added
  "WACC Rate": number, // From wacc.csv
  "Total Cost of Capital": number, // Current Balance * WACC Rate
  "Difference": number, // (Current Balance * LTP) - Total Cost of Capital
  "Difference Percentage": number // (Difference / Total Cost of Capital) * 100
}
```

### Totals Model

```javascript
{
  totalCostOfCapital: number,
  totalDifference: number,
  totalDifferencePercentage: number
}
```

## Color Coding Rules

The application will use the following color coding scheme for the Difference Percentage column:

1. **Positive values (> 0)**: Green color (text-success) - Indicates profit
2. **Negative values (< 0)**: Red color (text-danger) - Indicates loss
3. **Zero values (= 0)**: Blue color (text-info) - Indicates break-even

This color coding will be applied to both individual rows and the total row to provide immediate visual feedback on portfolio performance.

## Error Handling

### File Validation Errors

- Invalid file type (non-CSV)
- Empty files
- Corrupted CSV format
- Missing required files

### Data Processing Errors

- Missing required columns
- Invalid numeric values
- Scrip name mismatches
- Empty datasets

### Calculation Errors

- Division by zero in percentage calculations
- Invalid numeric operations
- Overflow/underflow scenarios

### Error Display Strategy

- Use Bootstrap alert components
- Color-coded error messages (danger, warning, info)
- Specific error descriptions for user guidance
- Non-blocking errors allow partial data display

## Testing Strategy

### Unit Testing Approach

1. **File Upload Handler Tests**

   - Valid CSV file acceptance
   - Invalid file rejection
   - File size limits
   - Multiple file handling

2. **CSV Parser Tests**

   - Various CSV formats
   - Header validation
   - Special characters handling
   - Empty row handling

3. **Data Processing Tests**

   - Scrip name matching (case-insensitive)
   - Data merging accuracy
   - Missing data handling
   - Duplicate scrip handling

4. **Calculation Engine Tests**

   - Mathematical accuracy
   - Edge cases (zero values)
   - Rounding precision
   - Negative value handling

5. **UI Renderer Tests**
   - Table generation
   - Color coding accuracy
   - Responsive behavior
   - Error message display

### Integration Testing

- End-to-end file upload to table display
- Cross-browser compatibility
- Mobile device responsiveness
- Performance with large datasets

### Manual Testing Scenarios

- Upload various CSV formats
- Test with missing columns
- Verify calculations manually
- Test responsive design on different screen sizes
- Validate accessibility features

## Performance Considerations

### Client-Side Optimization

- Lazy loading of Papa Parse library
- Efficient DOM manipulation
- Memory management for large CSV files
- Debounced file processing

### Browser Compatibility

- Modern browser support (ES6+)
- Fallback for older browsers if needed
- Progressive enhancement approach

### File Size Limitations

- Reasonable CSV file size limits
- User feedback for large file processing
- Browser memory considerations
