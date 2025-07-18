class PortfolioDashboard {
  constructor() {
    this.bindEvents();
  }

  bindEvents() {
    document
      .getElementById("analyzeBtn")
      .addEventListener("click", () => this.analyze());
  }

  async analyze() {
    try {
      const waccFile = document.getElementById("waccFile").files[0];
      const shareFile = document.getElementById("shareFile").files[0];

      if (!waccFile || !shareFile) {
        this.showAlert(
          "Please select both WACC and Share Value CSV files.",
          "warning"
        );
        return;
      }

      this.showAlert("Processing files...", "info");

      const [waccData, shareData] = await Promise.all([
        this.parseCSV(waccFile),
        this.parseCSV(shareFile),
      ]);

      const processedData = this.processData(waccData, shareData);

      const totals = this.calculateTotals(processedData);

      this.renderTable(processedData, totals);
      this.hideAlert();
    } catch (error) {
      this.showAlert(`Error: ${error.message}`, "danger");
      console.error("Portfolio analysis error:", error);
    }
  }

  parseCSV(file) {
    return new Promise((resolve, reject) => {
      Papa.parse(file, {
        header: true,
        skipEmptyLines: true,
        complete: (results) => {
          if (results.errors.length > 0) {
            reject(
              new Error(`CSV parsing error: ${results.errors[0].message}`)
            );
          } else {
            resolve(results.data);
          }
        },
        error: (error) =>
          reject(new Error(`Failed to parse CSV: ${error.message}`)),
      });
    });
  }

  processData(waccData, shareData) {
    // Build WACC map for efficient lookup
    const waccMap = new Map();
    waccData.forEach((row) => {
      const scripName = this.normalizeScripName(row["Scrip Name"]);
      if (scripName) {
        waccMap.set(scripName, row);
      }
    });

    // Log the last row before removing it
    if (shareData.length > 0) {
      const lastRow = shareData[shareData.length - 1];
      console.log("Last row being removed:", lastRow);
    }

    // Remove the last line from shareData (which is typically the total row)
    const dataWithoutLastLine = shareData.slice(0, -1);

    // Filter out any remaining total rows and empty rows
    const filteredShareData = dataWithoutLastLine.filter((row) => {
      const scripName = (row["Scrip"] || row["Scrip Name"] || "")
        .toString()
        .trim();

      // Only include rows with valid scrip names and exclude any remaining total rows
      const isValidRow =
        scripName &&
        scripName.length > 0 &&
        !scripName.toLowerCase().includes("total");

      if (!isValidRow) {
        console.log("Filtering out row:", scripName);
      }

      return isValidRow;
    });

    console.log(
      `Original rows: ${shareData.length}, After removing last line: ${dataWithoutLastLine.length}, After filtering: ${filteredShareData.length}`
    );

    // Process each share row and add calculated columns
    return filteredShareData.map((shareRow) => {
      const scripName = this.normalizeScripName(
        shareRow["Scrip"] || shareRow["Scrip Name"]
      );
      const waccRow = waccMap.get(scripName);

      // Extract values
      const quantity = this.parseNumber(shareRow["Current Balance"]);
      const ltp = this.parseNumber(
        shareRow["Last Transaction Price (LTP)"] || shareRow["LTP"]
      );
      const lastClosingPrice = this.parseNumber(shareRow["Last Closing Price"]);
      const waccRate = waccRow ? this.parseNumber(waccRow["WACC Rate"]) : 0;

      // Calculate Today's Gain
      const valueAsOfLTP = quantity * ltp;
      const valueAsOfLastClosing = quantity * lastClosingPrice;
      const todaysGain = valueAsOfLTP - valueAsOfLastClosing;

      // Calculate other metrics
      const totalCostOfCapital = quantity * waccRate;
      const difference = valueAsOfLTP - totalCostOfCapital;
      const differencePercentage =
        totalCostOfCapital !== 0 ? (difference / totalCostOfCapital) * 100 : 0;

      // Create new row with calculated columns inserted in the right order
      const newRow = {};

      // Copy original columns first
      Object.keys(shareRow).forEach((key) => {
        newRow[key] = shareRow[key];

        // Insert Today's Gain after Value as of LTP
        if (key === "Value as of LTP") {
          newRow["Today's Gain"] = todaysGain.toFixed(2);
        }
      });

      // Add remaining calculated columns
      newRow["WACC Rate"] = waccRate.toFixed(2);
      newRow["Total Cost of Capital"] = totalCostOfCapital.toFixed(2);
      newRow["Difference"] = difference.toFixed(2);
      newRow["Difference Percentage"] = differencePercentage.toFixed(2);

      return newRow;
    });
  }

  calculateTotals(processedData) {
    let totalValueAsOfLTP = 0;
    let totalValueAsOfLastClosing = 0;
    let totalTodaysGain = 0;
    let totalCostOfCapital = 0;
    let totalDifference = 0;

    processedData.forEach((row) => {
      // Calculate totals for all columns
      const quantity = this.parseNumber(row["Current Balance"]);
      const ltp = this.parseNumber(
        row["Last Transaction Price (LTP)"] || row["LTP"]
      );
      const lastClosingPrice = this.parseNumber(row["Last Closing Price"]);

      totalValueAsOfLTP += quantity * ltp;
      totalValueAsOfLastClosing += quantity * lastClosingPrice;
      totalTodaysGain += this.parseNumber(row["Today's Gain"]);
      totalCostOfCapital += this.parseNumber(row["Total Cost of Capital"]);
      totalDifference += this.parseNumber(row["Difference"]);
    });

    const totalDifferencePercentage =
      totalCostOfCapital !== 0
        ? (totalDifference / totalCostOfCapital) * 100
        : 0;

    return {
      totalValueAsOfLTP: totalValueAsOfLTP.toFixed(2),
      totalValueAsOfLastClosing: totalValueAsOfLastClosing.toFixed(2),
      totalTodaysGain: totalTodaysGain.toFixed(2),
      totalCostOfCapital: totalCostOfCapital.toFixed(2),
      totalDifference: totalDifference.toFixed(2),
      totalDifferencePercentage: totalDifferencePercentage.toFixed(2),
    };
  }

  renderTable(data, totals) {
    if (!data || data.length === 0) {
      this.showAlert("No data to display.", "warning");
      return;
    }

    const headers = Object.keys(data[0]);
    const table = document.getElementById("portfolioTable");

    // Create table header
    let html = '<thead class="table-dark"><tr>';
    headers.forEach((header) => {
      html += `<th style="white-space: nowrap;">${header}</th>`;
    });
    html += "</tr></thead>";

    // Create table body with all data rows
    html += "<tbody>";
    data.forEach((row) => {
      html += "<tr>";
      headers.forEach((header) => {
        const value = row[header] || "";
        let cellClass = "";
        let displayValue = value;

        // Apply color coding to Difference Percentage column
        if (header === "Difference Percentage") {
          const numValue = parseFloat(value);
          cellClass = "fw-bold ";

          if (numValue > 0) {
            cellClass += "text-success";
          } else if (numValue < 0) {
            cellClass += "text-danger";
          } else {
            cellClass += "text-info";
          }

          displayValue = `${value}%`;
        }

        html += `<td class="${cellClass}">${displayValue}</td>`;
      });
      html += "</tr>";
    });
    html += "</tbody>";

    // Create table footer with our calculated totals
    html += '<tfoot class="table-secondary"><tr>';
    headers.forEach((header, index) => {
      let cellValue = "";
      let cellClass = "fw-bold";

      if (index === 0 || header === "Scrip" || header === "Scrip Name") {
        cellValue = "";
      } else if (header === "Value as of Last Closing Price") {
        cellValue = totals.totalValueAsOfLastClosing;
      } else if (header === "Value as of LTP") {
        cellValue = totals.totalValueAsOfLTP;
      } else if (header === "Today's Gain") {
        const numValue = parseFloat(totals.totalTodaysGain);

        if (numValue > 0) {
          cellClass += " text-success";
        } else if (numValue < 0) {
          cellClass += " text-danger";
        } else {
          cellClass += " text-info";
        }

        cellValue = totals.totalTodaysGain;
      } else if (header === "Total Cost of Capital") {
        cellValue = totals.totalCostOfCapital;
      } else if (header === "Difference") {
        cellValue = totals.totalDifference;
      } else if (header === "Difference Percentage") {
        const numValue = parseFloat(totals.totalDifferencePercentage);

        if (numValue > 0) {
          cellClass += " text-success";
        } else if (numValue < 0) {
          cellClass += " text-danger";
        } else {
          cellClass += " text-info";
        }

        cellValue = `${totals.totalDifferencePercentage}%`;
      }

      html += `<td class="${cellClass}">${cellValue}</td>`;
    });
    html += "</tr></tfoot>";

    table.innerHTML = html;
    document.getElementById("resultsArea").classList.remove("d-none");
  }

  normalizeScripName(name) {
    return (name || "").toString().trim().toUpperCase();
  }

  parseNumber(value) {
    const num = parseFloat(value);
    return isNaN(num) ? 0 : num;
  }

  showAlert(message, type = "info") {
    const alertArea = document.getElementById("alertArea");
    const alertId = "alert-" + Date.now();

    alertArea.innerHTML = `
            <div id="${alertId}" class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${
                  type === "info"
                    ? '<div class="spinner-border spinner-border-sm me-2" role="status"></div>'
                    : ""
                }
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;
  }

  hideAlert() {
    document.getElementById("alertArea").innerHTML = "";
  }
}

// Initialize the application when DOM is ready
document.addEventListener("DOMContentLoaded", () => {
  new PortfolioDashboard();
});
