# Implementation Plan

## Overview

This implementation plan outlines the steps to create a standalone Share Portfolio Dashboard using HTML, Bootstrap 5, and JavaScript. The application will allow users to upload WACC and Share Value CSV files, process them client-side, and display portfolio analysis with calculated metrics.

## Implementation Tasks

### Task 1: Project Setup and Basic Structure

1. Create the basic HTML structure with Bootstrap 5 integration
2. Set up the file upload form with two file inputs
3. Add basic styling and responsive layout
4. Include required external libraries (Bootstrap, Papa Parse)

**Estimated time**: 1 hour

### Task 2: File Upload Handler Implementation

1. Implement file validation for CSV format
2. Create file reading functionality using FileReader API
3. Add error handling for file operations
4. Implement the main handler for processing both files

**Estimated time**: 2 hours

### Task 3: CSV Parser Implementation

1. Integrate Papa Parse library for CSV parsing
2. Implement header validation for required columns
3. Add error handling for parsing issues
4. Create data normalization functions

**Estimated time**: 2 hours

### Task 4: Data Processing Engine Implementation

1. Implement scrip name normalization for case-insensitive matching
2. Create the WACC data mapping functionality
3. Implement data merging between WACC and Share data
4. Add error handling for missing or mismatched data

**Estimated time**: 3 hours

### Task 5: Calculation Engine Implementation

1. Implement Total Cost of Capital calculation (quantity * WACC rate)
2. Implement Current Value calculation (quantity * LTP)
3. Implement Difference calculation (Current Value - Total Cost of Capital)
4. Implement Difference Percentage calculation ((Difference / Total Cost of Capital) * 100)
5. Implement totals calculation for all metrics

**Estimated time**: 2 hours

### Task 6: UI Renderer Implementation

1. Implement table generation with dynamic headers
2. Add color coding for Difference Percentage values (green for positive, red for negative, blue for zero)
3. Implement totals row rendering
4. Add error message display functionality
5. Implement "No data" message display

**Estimated time**: 3 hours

### Task 7: Integration and Testing

1. Connect all components into a complete workflow
2. Test with sample CSV files
3. Implement error handling for edge cases
4. Optimize performance for larger datasets
5. Test responsive design on different screen sizes

**Estimated time**: 3 hours

### Task 8: Final Polishing and Documentation

1. Add loading indicators during file processing
2. Improve UI/UX with better feedback
3. Add sample CSV templates for download
4. Create user documentation
5. Final code cleanup and optimization

**Estimated time**: 2 hours

## Implementation Details

### HTML Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Share Portfolio Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        /* Custom styles for color coding */
        .text-success { color: #27ae60 !important; }
        .text-danger { color: #e74c3c !important; }
        .text-info { color: #2980b9 !important; }
        .fw-bold { font-weight: bold; }
    </style>
</head>
<body>
    <div class="container mt-5">
        <h1 class="mb-4">Share Portfolio Dashboard</h1>
        
        <!-- File Upload Form -->
        <div class="card mb-4">
            <div class="card-header">Upload Portfolio Files</div>
            <div class="card-body">
                <form id="portfolioForm">
                    <div class="row g-3">
                        <div class="col-md-5">
                            <label for="waccFile" class="form-label">WACC File (CSV)</label>
                            <input type="file" class="form-control" id="waccFile" accept=".csv">
                        </div>
                        <div class="col-md-5">
                            <label for="shareFile" class="form-label">Share Value File (CSV)</label>
                            <input type="file" class="form-control" id="shareFile" accept=".csv">
                        </div>
                        <div class="col-md-2 d-flex align-items-end">
                            <button type="button" id="analyzeBtn" class="btn btn-primary w-100">Analyze Portfolio</button>
                        </div>
                    </div>
                </form>
            </div>
        </div>
        
        <!-- Alerts Area -->
        <div id="alertArea"></div>
        
        <!-- Results Table -->
        <div id="resultsArea" class="d-none">
            <div class="card">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <span>Portfolio Analysis Results</span>
                    <button id="downloadBtn" class="btn btn-sm btn-outline-secondary">Export CSV</button>
                </div>
                <div class="card-body p-0">
                    <div class="table-responsive">
                        <table id="portfolioTable" class="table table-striped table-hover mb-0">
                            <!-- Table content will be generated dynamically -->
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Scripts -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/papaparse@5.4.1/papaparse.min.js"></script>
    <script src="app.js"></script>
</body>
</html>
```

### JavaScript Implementation (app.js)

```javascript
// Main application class
class PortfolioDashboard {
    constructor() {
        this.waccData = null;
        this.shareData = null;
        this.processedData = null;
        this.totals = null;
        
        // Initialize components
        this.fileHandler = new FileUploadHandler();
        this.csvParser = new CSVParser();
        this.dataProcessor = new DataProcessor();
        this.calculator = new CalculationEngine();
        this.renderer = new UIRenderer();
        
        // Bind event listeners
        this.bindEvents();
    }
    
    bindEvents() {
        document.getElementById('analyzeBtn').addEventListener('click', () => this.handleAnalyzeClick());
        document.getElementById('downloadBtn').addEventListener('click', () => this.handleDownloadClick());
    }
    
    async handleAnalyzeClick() {
        try {
            // Clear previous results
            this.renderer.clearResults();
            
            // Get file inputs
            const waccFileInput = document.getElementById('waccFile');
            const shareFileInput = document.getElementById('shareFile');
            
            // Validate files
            if (!waccFileInput.files[0] || !shareFileInput.files[0]) {
                this.renderer.showError('Please select both WACC and Share Value CSV files.');
                return;
            }
            
            // Show loading
            this.renderer.showLoading('Processing files...');
            
            // Read and parse files
            const [waccContent, shareContent] = await Promise.all([
                this.fileHandler.readFile(waccFileInput.files[0]),
                this.fileHandler.readFile(shareFileInput.files[0])
            ]);
            
            this.waccData = this.csvParser.parseCSV(waccContent);
            this.shareData = this.csvParser.parseCSV(shareContent);
            
            // Process data
            const waccMap = this.dataProcessor.buildScripMap(this.waccData);
            this.processedData = this.dataProcessor.mergeData(waccMap, this.shareData);
            
            // Calculate totals
            this.totals = this.calculator.calculateTotals(this.processedData);
            
            // Render results
            const headers = this.dataProcessor.getResultHeaders(this.shareData, true);
            this.renderer.renderTable(this.processedData, headers, this.totals);
            
            // Hide loading
            this.renderer.hideLoading();
        } catch (error) {
            this.renderer.hideLoading();
            this.renderer.showError(`Error: ${error.message}`);
            console.error(error);
        }
    }
    
    handleDownloadClick() {
        if (!this.processedData || this.processedData.length === 0) {
            this.renderer.showError('No data to export.');
            return;
        }
        
        // Create CSV content
        const headers = this.dataProcessor.getResultHeaders(this.shareData, false);
        const csvContent = this.csvParser.generateCSV(this.processedData, headers, this.totals);
        
        // Create download link
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.setAttribute('href', url);
        link.setAttribute('download', 'portfolio_analysis.csv');
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}

// File Upload Handler
class FileUploadHandler {
    validateFile(file) {
        if (!file) return false;
        return file.type === 'text/csv' || file.name.endsWith('.csv');
    }
    
    readFile(file) {
        return new Promise((resolve, reject) => {
            if (!this.validateFile(file)) {
                reject(new Error(`Invalid file format: ${file.name}. Please upload a CSV file.`));
                return;
            }
            
            const reader = new FileReader();
            reader.onload = (e) => resolve(e.target.result);
            reader.onerror = () => reject(new Error(`Failed to read file: ${file.name}`));
            reader.readAsText(file);
        });
    }
}

// CSV Parser
class CSVParser {
    parseCSV(csvContent) {
        const results = Papa.parse(csvContent, {
            header: true,
            skipEmptyLines: true,
            dynamicTyping: true
        });
        
        if (results.errors && results.errors.length > 0) {
            throw new Error(`CSV parsing error: ${results.errors[0].message}`);
        }
        
        return results.data;
    }
    
    generateCSV(data, headers, totals) {
        // Generate CSV header row
        let csv = headers.join(',') + '\r\n';
        
        // Generate data rows
        data.forEach(row => {
            const rowValues = headers.map(header => {
                const value = row[header];
                // Handle values that might contain commas
                if (typeof value === 'string' && value.includes(',')) {
                    return `"${value}"`;
                }
                return value !== undefined ? value : '';
            });
            csv += rowValues.join(',') + '\r\n';
        });
        
        // Add totals row
        if (totals) {
            const totalRow = headers.map(header => {
                if (header === 'Total Cost of Capital') return totals.totalCostOfCapital;
                if (header === 'Difference') return totals.totalDifference;
                if (header === 'Difference Percentage') return totals.totalDifferencePercentage;
                if (header === 'Scrip Name') return 'TOTAL';
                return '';
            });
            csv += totalRow.join(',') + '\r\n';
        }
        
        return csv;
    }
}

// Data Processor
class DataProcessor {
    normalizeScripName(name) {
        return (name || '').toString().trim().toUpperCase();
    }
    
    buildScripMap(waccData) {
        const map = new Map();
        
        waccData.forEach(row => {
            const scripName = this.normalizeScripName(row['Scrip Name']);
            if (scripName) {
                map.set(scripName, row);
            }
        });
        
        return map;
    }
    
    mergeData(waccMap, shareData) {
        return shareData.map(shareRow => {
            // Determine which field contains the scrip name
            const scripName = this.normalizeScripName(shareRow['Scrip'] || shareRow['Scrip Name']);
            const waccRow = waccMap.get(scripName);
            
            // Get quantity and LTP
            const quantity = parseFloat(shareRow['Current Balance'] || shareRow['WACC Calculated Quantity'] || 0) || 0;
            const ltp = parseFloat(shareRow['Last Transaction Price (LTP)'] || shareRow['LTP'] || 0) || 0;
            
            // Get WACC rate
            const waccRate = waccRow ? parseFloat(waccRow['WACC Rate'] || 0) : 0;
            
            // Calculate values
            const totalCostOfCapital = new CalculationEngine().calculateTotalCostOfCapital(quantity, waccRate);
            const currentValue = new CalculationEngine().calculateCurrentValue(quantity, ltp);
            const difference = new CalculationEngine().calculateDifference(currentValue, totalCostOfCapital);
            const differencePercentage = new CalculationEngine().calculateDifferencePercentage(difference, totalCostOfCapital);
            
            // Return merged row with calculations
            return {
                ...shareRow,
                'WACC Rate': waccRate ? waccRate.toFixed(2) : '',
                'Total Cost of Capital': totalCostOfCapital.toFixed(2),
                'Difference': difference.toFixed(2),
                'Difference Percentage': differencePercentage.toFixed(2)
            };
        });
    }
    
    getResultHeaders(shareData, includeCalculated = true) {
        if (!shareData || shareData.length === 0) return [];
        
        // Get original headers from share data
        const originalHeaders = Object.keys(shareData[0]);
        
        if (!includeCalculated) return originalHeaders;
        
        // Add calculated columns
        return [
            ...originalHeaders,
            'WACC Rate',
            'Total Cost of Capital',
            'Difference',
            'Difference Percentage'
        ];
    }
}

// Calculation Engine
class CalculationEngine {
    calculateTotalCostOfCapital(quantity, waccRate) {
        return quantity * waccRate;
    }
    
    calculateCurrentValue(quantity, ltp) {
        return quantity * ltp;
    }
    
    calculateDifference(currentValue, totalCostOfCapital) {
        return currentValue - totalCostOfCapital;
    }
    
    calculateDifferencePercentage(difference, totalCostOfCapital) {
        if (!totalCostOfCapital) return 0;
        return (difference / totalCostOfCapital) * 100;
    }
    
    calculateTotals(processedData) {
        let totalCostOfCapital = 0;
        let totalCurrentValue = 0;
        
        processedData.forEach(row => {
            totalCostOfCapital += parseFloat(row['Total Cost of Capital']) || 0;
            
            // Calculate current value from quantity and LTP
            const quantity = parseFloat(row['Current Balance'] || row['WACC Calculated Quantity'] || 0) || 0;
            const ltp = parseFloat(row['Last Transaction Price (LTP)'] || row['LTP'] || 0) || 0;
            totalCurrentValue += quantity * ltp;
        });
        
        const totalDifference = totalCurrentValue - totalCostOfCapital;
        const totalDifferencePercentage = totalCostOfCapital ? (totalDifference / totalCostOfCapital) * 100 : 0;
        
        return {
            totalCostOfCapital: totalCostOfCapital.toFixed(2),
            totalDifference: totalDifference.toFixed(2),
            totalDifferencePercentage: totalDifferencePercentage.toFixed(2)
        };
    }
}

// UI Renderer
class UIRenderer {
    showError(message) {
        const alertArea = document.getElementById('alertArea');
        alertArea.innerHTML = `
            <div class="alert alert-danger alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;
    }
    
    showLoading(message) {
        const alertArea = document.getElementById('alertArea');
        alertArea.innerHTML = `
            <div class="alert alert-info" role="alert" id="loadingAlert">
                <div class="d-flex align-items-center">
                    <div class="spinner-border spinner-border-sm me-2" role="status"></div>
                    <span>${message}</span>
                </div>
            </div>
        `;
    }
    
    hideLoading() {
        const loadingAlert = document.getElementById('loadingAlert');
        if (loadingAlert) {
            loadingAlert.remove();
        }
    }
    
    clearResults() {
        document.getElementById('alertArea').innerHTML = '';
        document.getElementById('portfolioTable').innerHTML = '';
        document.getElementById('resultsArea').classList.add('d-none');
    }
    
    renderTable(data, headers, totals) {
        if (!data || data.length === 0) {
            this.showError('No data to display.');
            return;
        }
        
        const table = document.getElementById('portfolioTable');
        table.innerHTML = '';
        
        // Create table header
        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        headers.forEach(header => {
            const th = document.createElement('th');
            th.textContent = header;
            headerRow.appendChild(th);
        });
        thead.appendChild(headerRow);
        table.appendChild(thead);
        
        // Create table body
        const tbody = document.createElement('tbody');
        data.forEach(row => {
            const tr = document.createElement('tr');
            
            headers.forEach(header => {
                const td = document.createElement('td');
                td.textContent = row[header] !== undefined ? row[header] : '';
                
                // Apply color coding to Difference Percentage column
                if (header === 'Difference Percentage') {
                    const value = parseFloat(row[header]);
                    td.classList.add('fw-bold');
                    
                    if (value > 0) {
                        td.classList.add('text-success');
                    } else if (value < 0) {
                        td.classList.add('text-danger');
                    } else {
                        td.classList.add('text-info');
                    }
                    
                    // Add % symbol
                    td.textContent = `${td.textContent}%`;
                }
                
                tr.appendChild(td);
            });
            
            tbody.appendChild(tr);
        });
        table.appendChild(tbody);
        
        // Create table footer with totals
        if (totals) {
            const tfoot = document.createElement('tfoot');
            const footerRow = document.createElement('tr');
            
            headers.forEach((header, index) => {
                const td = document.createElement('td');
                
                if (header === 'Scrip Name' || index === 0) {
                    td.textContent = 'TOTAL';
                    td.classList.add('fw-bold');
                } else if (header === 'Total Cost of Capital') {
                    td.textContent = totals.totalCostOfCapital;
                    td.classList.add('fw-bold');
                } else if (header === 'Difference') {
                    td.textContent = totals.totalDifference;
                    td.classList.add('fw-bold');
                } else if (header === 'Difference Percentage') {
                    td.textContent = `${totals.totalDifferencePercentage}%`;
                    td.classList.add('fw-bold');
                    
                    const value = parseFloat(totals.totalDifferencePercentage);
                    if (value > 0) {
                        td.classList.add('text-success');
                    } else if (value < 0) {
                        td.classList.add('text-danger');
                    } else {
                        td.classList.add('text-info');
                    }
                }
                
                footerRow.appendChild(td);
            });
            
            tfoot.appendChild(footerRow);
            table.appendChild(tfoot);
        }
        
        // Show results area
        document.getElementById('resultsArea').classList.remove('d-none');
    }
}

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new PortfolioDashboard();
});
```

## Testing Plan

### Unit Tests

1. Test file validation with valid and invalid files
2. Test CSV parsing with different formats
3. Test data merging with matching and non-matching scrip names
4. Test calculations with various input values
5. Test color coding logic

### Integration Tests

1. End-to-end test with sample CSV files
2. Test error handling with invalid data
3. Test responsive design on different screen sizes

### Sample Test Data

Use the provided sample CSV files:
- templates/wacc.csv
- templates/sharevalue.csv.csv

## Deployment

1. Create a standalone HTML file with embedded JavaScript
2. Host on any static web server or use locally
3. No server-side dependencies required

## Future Enhancements

1. Add data visualization with charts
2. Implement data persistence using localStorage
3. Add filtering and sorting capabilities
4. Support for additional CSV formats
5. Add portfolio performance tracking over time