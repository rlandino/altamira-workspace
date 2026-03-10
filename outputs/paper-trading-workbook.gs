/**
 * ============================================================================
 * ALTAMIRA CAPITAL — Paper Trading Workbook Setup Script
 * ============================================================================
 *
 * Version:  1.0
 * Date:     2026-02-18
 * Author:   Ricardo Landino, Founder — Altamira Capital
 *
 * PURPOSE:
 *   Creates a fully configured paper trading workbook with 4 sheets:
 *     1. Trade Log       — Individual trade records with P&L formulas
 *     2. Daily Dashboard  — Daily portfolio snapshots and risk metrics
 *     3. Weekly Summary   — Weekly performance aggregation and Sharpe ratio
 *     4. Risk Limits      — Reference sheet for all risk parameters
 *
 * USAGE:
 *   1. Open a new Google Spreadsheet
 *   2. Go to Extensions > Apps Script
 *   3. Paste this entire script into the editor (replace any existing code)
 *   4. Save (Ctrl+S)
 *   5. Run the function: setupPaperTradingWorkbook()
 *   6. Authorize the script when prompted
 *   7. Wait ~30 seconds for all sheets to be created and formatted
 *
 * NOTES:
 *   - Running this script multiple times will delete and recreate all sheets.
 *   - The script creates ~50 rows of pre-formatted data rows with formulas.
 *   - All formulas use actual cell references and will auto-calculate.
 *   - Conditional formatting is applied automatically.
 *   - Data validation dropdowns are set on the appropriate columns.
 *
 * ============================================================================
 */


// =============================================================================
// MAIN ENTRY POINT
// =============================================================================

/**
 * Main function — run this to create the entire workbook.
 */
function setupPaperTradingWorkbook() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();

  // Delete existing sheets (except the first one, which we'll rename)
  var sheets = ss.getSheets();
  for (var i = sheets.length - 1; i >= 1; i--) {
    ss.deleteSheet(sheets[i]);
  }

  // Rename the first sheet temporarily
  var firstSheet = ss.getSheets()[0];
  firstSheet.setName("_temp_");

  // Create all five sheets
  var tradeLogSheet = ss.insertSheet("Trade Log", 0);
  var dailyDashSheet = ss.insertSheet("Daily Dashboard", 1);
  var positionHistorySheet = ss.insertSheet("Position History", 2);
  var weeklySummarySheet = ss.insertSheet("Weekly Summary", 3);
  var riskLimitsSheet = ss.insertSheet("Risk Limits", 4);

  // Delete the temporary sheet
  ss.deleteSheet(ss.getSheetByName("_temp_"));

  // Build each sheet
  setupTradeLog(tradeLogSheet);
  setupDailyDashboard(dailyDashSheet);
  setupPositionHistory(positionHistorySheet);
  setupWeeklySummary(weeklySummarySheet);
  setupRiskLimits(riskLimitsSheet);

  // Set Trade Log as active sheet
  ss.setActiveSheet(tradeLogSheet);

  SpreadsheetApp.flush();

  // Show completion message
  SpreadsheetApp.getUi().alert(
    "Altamira Capital Paper Trading Workbook",
    "Setup complete.\n\n" +
    "5 sheets created:\n" +
    "  1. Trade Log\n" +
    "  2. Daily Dashboard\n" +
    "  3. Position History\n" +
    "  4. Weekly Summary\n" +
    "  5. Risk Limits\n\n" +
    "Starting capital: $100,000\n" +
    "Allocation: 40% CSP / 40% Momentum / 20% Cash\n\n" +
    "Good luck. Discipline over complexity.",
    SpreadsheetApp.getUi().ButtonSet.OK
  );
}


// =============================================================================
// SHEET 1: TRADE LOG
// =============================================================================

/**
 * Sets up the Trade Log sheet with headers, formulas, dropdowns, and
 * conditional formatting.
 *
 * Columns A-Z:
 *   A: Trade ID (auto PT-001)
 *   B: Date Entry
 *   C: Date Exit
 *   D: Ticker
 *   E: Strategy (dropdown)
 *   F: Direction (dropdown)
 *   G: Strike
 *   H: Expiration
 *   I: DTE at Entry
 *   J: Delta at Entry
 *   K: IV Rank at Entry
 *   L: Contracts/Shares
 *   M: Entry Price
 *   N: Exit Price
 *   O: Raw P&L (formula)
 *   P: Commission (formula)
 *   Q: Est. Slippage (formula)
 *   R: Adjusted P&L (formula)
 *   S: P&L % of Allocated Capital
 *   T: Days Held (formula)
 *   U: Exit Reason (dropdown)
 *   V: Thesis
 *   W: Edge
 *   X: Outcome Notes
 *   Y: Rule Compliance (dropdown)
 *   Z: Lessons
 */
function setupTradeLog(sheet) {
  var DATA_ROWS = 200; // Pre-format this many data rows

  // -------------------------------------------------------------------------
  // Headers
  // -------------------------------------------------------------------------
  var headers = [
    "Trade ID",           // A
    "Date Entry",         // B
    "Date Exit",          // C
    "Ticker",             // D
    "Strategy",           // E
    "Direction",          // F
    "Strike",             // G
    "Expiration",         // H
    "DTE at Entry",       // I
    "Delta at Entry",     // J
    "IV Rank at Entry",   // K
    "Contracts/Shares",   // L
    "Entry Price",        // M
    "Exit Price",         // N
    "Raw P&L",            // O
    "Commission",         // P
    "Est. Slippage",      // Q
    "Adjusted P&L",       // R
    "P&L % of Capital",   // S
    "Days Held",          // T
    "Exit Reason",        // U
    "Thesis",             // V
    "Edge",               // W
    "Outcome Notes",      // X
    "Rule Compliance",    // Y
    "Lessons"             // Z
  ];

  sheet.getRange(1, 1, 1, headers.length).setValues([headers]);

  // -------------------------------------------------------------------------
  // Header formatting
  // -------------------------------------------------------------------------
  var headerRange = sheet.getRange(1, 1, 1, headers.length);
  headerRange.setBackground("#1a1a2e")
             .setFontColor("#ffffff")
             .setFontWeight("bold")
             .setFontSize(10)
             .setHorizontalAlignment("center")
             .setVerticalAlignment("middle")
             .setWrap(true);
  sheet.setFrozenRows(1);
  sheet.setRowHeight(1, 40);

  // -------------------------------------------------------------------------
  // Column widths
  // -------------------------------------------------------------------------
  sheet.setColumnWidth(1, 80);    // A: Trade ID
  sheet.setColumnWidth(2, 100);   // B: Date Entry
  sheet.setColumnWidth(3, 100);   // C: Date Exit
  sheet.setColumnWidth(4, 70);    // D: Ticker
  sheet.setColumnWidth(5, 100);   // E: Strategy
  sheet.setColumnWidth(6, 80);    // F: Direction
  sheet.setColumnWidth(7, 80);    // G: Strike
  sheet.setColumnWidth(8, 100);   // H: Expiration
  sheet.setColumnWidth(9, 90);    // I: DTE at Entry
  sheet.setColumnWidth(10, 100);  // J: Delta at Entry
  sheet.setColumnWidth(11, 110);  // K: IV Rank
  sheet.setColumnWidth(12, 120);  // L: Contracts/Shares
  sheet.setColumnWidth(13, 100);  // M: Entry Price
  sheet.setColumnWidth(14, 100);  // N: Exit Price
  sheet.setColumnWidth(15, 100);  // O: Raw P&L
  sheet.setColumnWidth(16, 100);  // P: Commission
  sheet.setColumnWidth(17, 110);  // Q: Est. Slippage
  sheet.setColumnWidth(18, 110);  // R: Adjusted P&L
  sheet.setColumnWidth(19, 120);  // S: P&L %
  sheet.setColumnWidth(20, 90);   // T: Days Held
  sheet.setColumnWidth(21, 120);  // U: Exit Reason
  sheet.setColumnWidth(22, 200);  // V: Thesis
  sheet.setColumnWidth(23, 200);  // W: Edge
  sheet.setColumnWidth(24, 200);  // X: Outcome Notes
  sheet.setColumnWidth(25, 120);  // Y: Rule Compliance
  sheet.setColumnWidth(26, 200);  // Z: Lessons

  // -------------------------------------------------------------------------
  // Trade ID formula (auto-increment: PT-001, PT-002, ...)
  //   Only shows if Date Entry (column B) is not empty
  // -------------------------------------------------------------------------
  for (var row = 2; row <= DATA_ROWS + 1; row++) {
    var tradeNum = row - 1;
    var paddedNum = ("00" + tradeNum).slice(-3);
    // Show Trade ID only when Date Entry is filled in
    sheet.getRange(row, 1).setFormula(
      '=IF(B' + row + '<>"", "PT-' + paddedNum + '", "")'
    );
  }

  // -------------------------------------------------------------------------
  // Formulas for calculated columns (rows 2 to DATA_ROWS+1)
  // -------------------------------------------------------------------------
  for (var row = 2; row <= DATA_ROWS + 1; row++) {
    var r = row;

    // O: Raw P&L
    //   Options (CSP/Hedge): =(Entry - Exit) * Contracts * 100
    //   Equity (Momentum):   =(Exit - Entry) * Shares
    //   Only calculate when Exit Price (N) is present
    sheet.getRange(r, 15).setFormula(
      '=IF(N' + r + '="",' +
        '"",' +
        'IF(E' + r + '="Momentum",' +
          '(N' + r + '-M' + r + ')*L' + r + ',' +
          '(M' + r + '-N' + r + ')*L' + r + '*100' +
        ')' +
      ')'
    );

    // P: Commission
    //   Options: =Contracts * $0.65 * 2 (round-trip)
    //   Equity (Momentum): 0
    //   Only calculate when Contracts/Shares (L) is present
    sheet.getRange(r, 16).setFormula(
      '=IF(L' + r + '="",' +
        '"",' +
        'IF(E' + r + '="Momentum",' +
          '0,' +
          'L' + r + '*0.65*2' +
        ')' +
      ')'
    );

    // Q: Est. Slippage
    //   Options: =Entry Price * 0.02 * Contracts * 100
    //   Equity (Momentum): 0
    sheet.getRange(r, 17).setFormula(
      '=IF(M' + r + '="",' +
        '"",' +
        'IF(E' + r + '="Momentum",' +
          '0,' +
          'M' + r + '*0.02*L' + r + '*100' +
        ')' +
      ')'
    );

    // R: Adjusted P&L = Raw P&L - Commission - Est. Slippage
    sheet.getRange(r, 18).setFormula(
      '=IF(O' + r + '="",' +
        '"",' +
        'O' + r + '-P' + r + '-Q' + r +
      ')'
    );

    // S: P&L % of Allocated Capital
    //   CSP/Hedge: divide by $40,000 (options allocation)
    //   Momentum:  divide by $40,000 (equity allocation)
    //   Fallback:  divide by $100,000 (total portfolio)
    sheet.getRange(r, 19).setFormula(
      '=IF(R' + r + '="",' +
        '"",' +
        'IF(OR(E' + r + '="CSP",E' + r + '="Hedge"),' +
          'R' + r + '/40000,' +
          'IF(E' + r + '="Momentum",' +
            'R' + r + '/40000,' +
            'R' + r + '/100000' +
          ')' +
        ')' +
      ')'
    );

    // T: Days Held = Date Exit - Date Entry
    sheet.getRange(r, 20).setFormula(
      '=IF(OR(B' + r + '="",C' + r + '=""),' +
        '"",' +
        'C' + r + '-B' + r +
      ')'
    );
  }

  // -------------------------------------------------------------------------
  // Number formatting
  // -------------------------------------------------------------------------
  var dataRange = sheet.getRange(2, 1, DATA_ROWS, 26);

  // Dates
  sheet.getRange(2, 2, DATA_ROWS, 1).setNumberFormat("yyyy-mm-dd"); // B: Date Entry
  sheet.getRange(2, 3, DATA_ROWS, 1).setNumberFormat("yyyy-mm-dd"); // C: Date Exit
  sheet.getRange(2, 8, DATA_ROWS, 1).setNumberFormat("yyyy-mm-dd"); // H: Expiration

  // Currency
  sheet.getRange(2, 7, DATA_ROWS, 1).setNumberFormat("$#,##0.00");  // G: Strike
  sheet.getRange(2, 13, DATA_ROWS, 1).setNumberFormat("$#,##0.00"); // M: Entry Price
  sheet.getRange(2, 14, DATA_ROWS, 1).setNumberFormat("$#,##0.00"); // N: Exit Price
  sheet.getRange(2, 15, DATA_ROWS, 1).setNumberFormat("$#,##0.00"); // O: Raw P&L
  sheet.getRange(2, 16, DATA_ROWS, 1).setNumberFormat("$#,##0.00"); // P: Commission
  sheet.getRange(2, 17, DATA_ROWS, 1).setNumberFormat("$#,##0.00"); // Q: Est. Slippage
  sheet.getRange(2, 18, DATA_ROWS, 1).setNumberFormat("$#,##0.00"); // R: Adjusted P&L

  // Percentage
  sheet.getRange(2, 19, DATA_ROWS, 1).setNumberFormat("0.00%");     // S: P&L %

  // Numbers
  sheet.getRange(2, 9, DATA_ROWS, 1).setNumberFormat("0");          // I: DTE
  sheet.getRange(2, 10, DATA_ROWS, 1).setNumberFormat("0.00");      // J: Delta
  sheet.getRange(2, 11, DATA_ROWS, 1).setNumberFormat("0");         // K: IV Rank
  sheet.getRange(2, 12, DATA_ROWS, 1).setNumberFormat("0");         // L: Contracts/Shares
  sheet.getRange(2, 20, DATA_ROWS, 1).setNumberFormat("0");         // T: Days Held

  // -------------------------------------------------------------------------
  // Data Validation — Dropdowns
  // -------------------------------------------------------------------------

  // E: Strategy dropdown
  var strategyRule = SpreadsheetApp.newDataValidation()
    .requireValueInList(["CSP", "Momentum", "Hedge"], true)
    .setAllowInvalid(false)
    .setHelpText("Select strategy: CSP, Momentum, or Hedge")
    .build();
  sheet.getRange(2, 5, DATA_ROWS, 1).setDataValidation(strategyRule);

  // F: Direction dropdown
  var directionRule = SpreadsheetApp.newDataValidation()
    .requireValueInList(["Long", "Short", "STO", "BTC"], true)
    .setAllowInvalid(false)
    .setHelpText("Select direction: Long, Short, STO (Sell to Open), or BTC (Buy to Close)")
    .build();
  sheet.getRange(2, 6, DATA_ROWS, 1).setDataValidation(directionRule);

  // U: Exit Reason dropdown
  var exitReasonRule = SpreadsheetApp.newDataValidation()
    .requireValueInList([
      "Profit Target",
      "Stop Loss",
      "Expiration",
      "Assignment",
      "Manual",
      "MA Signal"
    ], true)
    .setAllowInvalid(false)
    .setHelpText("Select exit reason")
    .build();
  sheet.getRange(2, 21, DATA_ROWS, 1).setDataValidation(exitReasonRule);

  // Y: Rule Compliance dropdown
  var complianceRule = SpreadsheetApp.newDataValidation()
    .requireValueInList(["Yes", "No"], true)
    .setAllowInvalid(false)
    .setHelpText("Were all trading rules followed? Yes or No")
    .build();
  sheet.getRange(2, 25, DATA_ROWS, 1).setDataValidation(complianceRule);

  // -------------------------------------------------------------------------
  // Conditional Formatting
  // -------------------------------------------------------------------------
  var rules = sheet.getConditionalFormatRules();

  // Rule 1: Green background on Adjusted P&L (column R) when positive
  var greenPnlRule = SpreadsheetApp.newConditionalFormatRule()
    .whenNumberGreaterThan(0)
    .setBackground("#d4edda")
    .setFontColor("#155724")
    .setRanges([sheet.getRange(2, 18, DATA_ROWS, 1)])
    .build();
  rules.push(greenPnlRule);

  // Rule 2: Red background on Adjusted P&L (column R) when negative
  var redPnlRule = SpreadsheetApp.newConditionalFormatRule()
    .whenNumberLessThan(0)
    .setBackground("#f8d7da")
    .setFontColor("#721c24")
    .setRanges([sheet.getRange(2, 18, DATA_ROWS, 1)])
    .build();
  rules.push(redPnlRule);

  // Rule 3: Yellow highlight on Rule Compliance (column Y) = "No"
  var yellowComplianceRule = SpreadsheetApp.newConditionalFormatRule()
    .whenTextEqualTo("No")
    .setBackground("#fff3cd")
    .setFontColor("#856404")
    .setBold(true)
    .setRanges([sheet.getRange(2, 25, DATA_ROWS, 1)])
    .build();
  rules.push(yellowComplianceRule);

  // Rule 4: Also color the Raw P&L column (O) for quick scanning
  var greenRawPnlRule = SpreadsheetApp.newConditionalFormatRule()
    .whenNumberGreaterThan(0)
    .setBackground("#d4edda")
    .setFontColor("#155724")
    .setRanges([sheet.getRange(2, 15, DATA_ROWS, 1)])
    .build();
  rules.push(greenRawPnlRule);

  var redRawPnlRule = SpreadsheetApp.newConditionalFormatRule()
    .whenNumberLessThan(0)
    .setBackground("#f8d7da")
    .setFontColor("#721c24")
    .setRanges([sheet.getRange(2, 15, DATA_ROWS, 1)])
    .build();
  rules.push(redRawPnlRule);

  sheet.setConditionalFormatRules(rules);

  // -------------------------------------------------------------------------
  // Alternating row colors for readability
  // -------------------------------------------------------------------------
  var bandingRange = sheet.getRange(1, 1, DATA_ROWS + 1, headers.length);
  // Remove existing banding if any
  var bandings = bandingRange.getBandings();
  for (var i = 0; i < bandings.length; i++) {
    bandings[i].remove();
  }
  bandingRange.applyRowBanding(SpreadsheetApp.BandingTheme.LIGHT_GREY, true, false);

  // -------------------------------------------------------------------------
  // Protect header row
  // -------------------------------------------------------------------------
  var protection = sheet.getRange(1, 1, 1, headers.length).protect();
  protection.setDescription("Header row — do not edit");
  protection.setWarningOnly(true);
}


// =============================================================================
// SHEET 2: DAILY DASHBOARD
// =============================================================================

/**
 * Sets up the Daily Dashboard sheet with headers, formulas, and
 * conditional formatting.
 *
 * Columns A-P:
 *   A: Date
 *   B: Portfolio Value
 *   C: Daily P&L ($)
 *   D: Daily P&L (%)
 *   E: Cumulative P&L ($)
 *   F: Cumulative P&L (%)
 *   G: Running Peak
 *   H: Drawdown
 *   I: Net Delta
 *   J: Daily Theta
 *   K: Open CSP Count
 *   L: Open Equity Positions
 *   M: Cash %
 *   N: VIX Close
 *   O: SPY Close
 *   P: Notes
 */
function setupDailyDashboard(sheet) {
  var DATA_ROWS = 300; // ~60 weeks of trading days
  var STARTING_CAPITAL = 100000;

  // -------------------------------------------------------------------------
  // Headers
  // -------------------------------------------------------------------------
  var headers = [
    "Date",                   // A
    "Portfolio Value",        // B
    "Daily P&L ($)",          // C
    "Daily P&L (%)",          // D
    "Cumulative P&L ($)",     // E
    "Cumulative P&L (%)",     // F
    "Running Peak",           // G
    "Drawdown",               // H
    "Net Delta",              // I
    "Daily Theta",            // J
    "Open CSP Count",         // K
    "Open Equity Positions",  // L
    "Cash %",                 // M
    "VIX Close",              // N
    "SPY Close",              // O
    "Notes"                   // P
  ];

  sheet.getRange(1, 1, 1, headers.length).setValues([headers]);

  // -------------------------------------------------------------------------
  // Header formatting
  // -------------------------------------------------------------------------
  var headerRange = sheet.getRange(1, 1, 1, headers.length);
  headerRange.setBackground("#0f3460")
             .setFontColor("#ffffff")
             .setFontWeight("bold")
             .setFontSize(10)
             .setHorizontalAlignment("center")
             .setVerticalAlignment("middle")
             .setWrap(true);
  sheet.setFrozenRows(1);
  sheet.setRowHeight(1, 40);

  // -------------------------------------------------------------------------
  // Column widths
  // -------------------------------------------------------------------------
  sheet.setColumnWidth(1, 100);   // A: Date
  sheet.setColumnWidth(2, 130);   // B: Portfolio Value
  sheet.setColumnWidth(3, 110);   // C: Daily P&L ($)
  sheet.setColumnWidth(4, 110);   // D: Daily P&L (%)
  sheet.setColumnWidth(5, 130);   // E: Cumulative P&L ($)
  sheet.setColumnWidth(6, 130);   // F: Cumulative P&L (%)
  sheet.setColumnWidth(7, 120);   // G: Running Peak
  sheet.setColumnWidth(8, 100);   // H: Drawdown
  sheet.setColumnWidth(9, 90);    // I: Net Delta
  sheet.setColumnWidth(10, 100);  // J: Daily Theta
  sheet.setColumnWidth(11, 120);  // K: Open CSP Count
  sheet.setColumnWidth(12, 150);  // L: Open Equity Positions
  sheet.setColumnWidth(13, 80);   // M: Cash %
  sheet.setColumnWidth(14, 90);   // N: VIX Close
  sheet.setColumnWidth(15, 90);   // O: SPY Close
  sheet.setColumnWidth(16, 250);  // P: Notes

  // -------------------------------------------------------------------------
  // Formulas (rows 2 to DATA_ROWS+1)
  // -------------------------------------------------------------------------
  for (var row = 2; row <= DATA_ROWS + 1; row++) {
    var r = row;

    // C: Daily P&L ($) = Today's portfolio value - yesterday's portfolio value
    //   Row 2 (first day): = Portfolio Value - Starting Capital
    if (r === 2) {
      sheet.getRange(r, 3).setFormula(
        '=IF(B' + r + '="","",B' + r + '-' + STARTING_CAPITAL + ')'
      );
    } else {
      sheet.getRange(r, 3).setFormula(
        '=IF(B' + r + '="","",B' + r + '-B' + (r - 1) + ')'
      );
    }

    // D: Daily P&L (%) = Daily P&L / Previous day's portfolio value
    if (r === 2) {
      sheet.getRange(r, 4).setFormula(
        '=IF(B' + r + '="","",C' + r + '/' + STARTING_CAPITAL + ')'
      );
    } else {
      sheet.getRange(r, 4).setFormula(
        '=IF(B' + r + '="","",IF(B' + (r - 1) + '=0,"",C' + r + '/B' + (r - 1) + '))'
      );
    }

    // E: Cumulative P&L ($) = Portfolio Value - Starting Capital
    sheet.getRange(r, 5).setFormula(
      '=IF(B' + r + '="","",B' + r + '-' + STARTING_CAPITAL + ')'
    );

    // F: Cumulative P&L (%) = Cumulative P&L / Starting Capital
    sheet.getRange(r, 6).setFormula(
      '=IF(B' + r + '="","",E' + r + '/' + STARTING_CAPITAL + ')'
    );

    // G: Running Peak = MAX of all portfolio values from row 2 to current row
    sheet.getRange(r, 7).setFormula(
      '=IF(B' + r + '="","",MAX($B$2:B' + r + '))'
    );

    // H: Drawdown = (Portfolio Value - Running Peak) / Running Peak
    sheet.getRange(r, 8).setFormula(
      '=IF(B' + r + '="","",IF(G' + r + '=0,"",(B' + r + '-G' + r + ')/G' + r + '))'
    );
  }

  // -------------------------------------------------------------------------
  // Number formatting
  // -------------------------------------------------------------------------
  sheet.getRange(2, 1, DATA_ROWS, 1).setNumberFormat("yyyy-mm-dd");      // A: Date
  sheet.getRange(2, 2, DATA_ROWS, 1).setNumberFormat("$#,##0.00");       // B: Portfolio Value
  sheet.getRange(2, 3, DATA_ROWS, 1).setNumberFormat("$#,##0.00");       // C: Daily P&L ($)
  sheet.getRange(2, 4, DATA_ROWS, 1).setNumberFormat("0.00%");           // D: Daily P&L (%)
  sheet.getRange(2, 5, DATA_ROWS, 1).setNumberFormat("$#,##0.00");       // E: Cumulative P&L ($)
  sheet.getRange(2, 6, DATA_ROWS, 1).setNumberFormat("0.00%");           // F: Cumulative P&L (%)
  sheet.getRange(2, 7, DATA_ROWS, 1).setNumberFormat("$#,##0.00");       // G: Running Peak
  sheet.getRange(2, 8, DATA_ROWS, 1).setNumberFormat("0.00%");           // H: Drawdown
  sheet.getRange(2, 9, DATA_ROWS, 1).setNumberFormat("0.00");            // I: Net Delta
  sheet.getRange(2, 10, DATA_ROWS, 1).setNumberFormat("$#,##0.00");      // J: Daily Theta
  sheet.getRange(2, 11, DATA_ROWS, 1).setNumberFormat("0");              // K: Open CSP Count
  sheet.getRange(2, 12, DATA_ROWS, 1).setNumberFormat("0");              // L: Open Equity Positions
  sheet.getRange(2, 13, DATA_ROWS, 1).setNumberFormat("0.0%");           // M: Cash %
  sheet.getRange(2, 14, DATA_ROWS, 1).setNumberFormat("0.00");           // N: VIX Close
  sheet.getRange(2, 15, DATA_ROWS, 1).setNumberFormat("$#,##0.00");      // O: SPY Close

  // -------------------------------------------------------------------------
  // Conditional Formatting
  // -------------------------------------------------------------------------
  var rules = sheet.getConditionalFormatRules();

  // Cash % (column M) — Red if below 15%
  var cashRedRule = SpreadsheetApp.newConditionalFormatRule()
    .whenNumberLessThan(0.15)
    .setBackground("#f8d7da")
    .setFontColor("#721c24")
    .setBold(true)
    .setRanges([sheet.getRange(2, 13, DATA_ROWS, 1)])
    .build();
  rules.push(cashRedRule);

  // Cash % (column M) — Yellow if between 15% and 20%
  var cashYellowRule = SpreadsheetApp.newConditionalFormatRule()
    .whenNumberBetween(0.15, 0.20)
    .setBackground("#fff3cd")
    .setFontColor("#856404")
    .setRanges([sheet.getRange(2, 13, DATA_ROWS, 1)])
    .build();
  rules.push(cashYellowRule);

  // Drawdown (column H) — Red if worse than -5%
  var drawdownRedRule = SpreadsheetApp.newConditionalFormatRule()
    .whenNumberLessThan(-0.05)
    .setBackground("#f8d7da")
    .setFontColor("#721c24")
    .setBold(true)
    .setRanges([sheet.getRange(2, 8, DATA_ROWS, 1)])
    .build();
  rules.push(drawdownRedRule);

  // Daily P&L ($) — Green/Red coloring
  var dailyPnlGreen = SpreadsheetApp.newConditionalFormatRule()
    .whenNumberGreaterThan(0)
    .setBackground("#d4edda")
    .setFontColor("#155724")
    .setRanges([sheet.getRange(2, 3, DATA_ROWS, 1)])
    .build();
  rules.push(dailyPnlGreen);

  var dailyPnlRed = SpreadsheetApp.newConditionalFormatRule()
    .whenNumberLessThan(0)
    .setBackground("#f8d7da")
    .setFontColor("#721c24")
    .setRanges([sheet.getRange(2, 3, DATA_ROWS, 1)])
    .build();
  rules.push(dailyPnlRed);

  // Daily P&L (%) — Green/Red coloring
  var dailyPctGreen = SpreadsheetApp.newConditionalFormatRule()
    .whenNumberGreaterThan(0)
    .setBackground("#d4edda")
    .setFontColor("#155724")
    .setRanges([sheet.getRange(2, 4, DATA_ROWS, 1)])
    .build();
  rules.push(dailyPctGreen);

  var dailyPctRed = SpreadsheetApp.newConditionalFormatRule()
    .whenNumberLessThan(0)
    .setBackground("#f8d7da")
    .setFontColor("#721c24")
    .setRanges([sheet.getRange(2, 4, DATA_ROWS, 1)])
    .build();
  rules.push(dailyPctRed);

  sheet.setConditionalFormatRules(rules);

  // -------------------------------------------------------------------------
  // Alternating row colors
  // -------------------------------------------------------------------------
  var bandingRange = sheet.getRange(1, 1, DATA_ROWS + 1, headers.length);
  bandingRange.applyRowBanding(SpreadsheetApp.BandingTheme.LIGHT_GREY, true, false);

  // -------------------------------------------------------------------------
  // Protect header row
  // -------------------------------------------------------------------------
  var protection = sheet.getRange(1, 1, 1, headers.length).protect();
  protection.setDescription("Header row — do not edit");
  protection.setWarningOnly(true);
}


// =============================================================================
// SHEET 2.5: POSITION HISTORY (for optimization)
// =============================================================================

/**
 * Sets up the Position History sheet. One row per position per day,
 * appended by n8n Daily Portfolio Snapshot workflow. Used for
 * rebalancing, sector limits, and return optimization.
 *
 * Columns A-L:
 *   A: Date
 *   B: Symbol
 *   C: AssetType (EQ | OPT)
 *   D: Quantity
 *   E: Market Value
 *   F: Weight %
 *   G: Sector
 *   H: Delta
 *   I: Theta
 *   J: Strike
 *   K: Expiration
 *   L: CallPut (C | P)
 */
function setupPositionHistory(sheet) {
  var headers = [
    "Date",
    "Symbol",
    "AssetType",
    "Quantity",
    "Market Value",
    "Weight %",
    "Sector",
    "Delta",
    "Theta",
    "Strike",
    "Expiration",
    "CallPut"
  ];
  sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
  sheet.getRange(1, 1, 1, headers.length).setFontWeight("bold").setBackground("#f0f0f0");
  sheet.setFrozenRows(1);
  sheet.autoResizeColumns(1, headers.length);
  sheet.getRange(2, 1, 5000, 1).setNumberFormat("yyyy-mm-dd");    // Date
  sheet.getRange(2, 5, 5000, 5).setNumberFormat("$#,##0.00");    // Market Value
  sheet.getRange(2, 6, 5000, 6).setNumberFormat("0.00%");         // Weight %
  sheet.getRange(2, 8, 5000, 8).setNumberFormat("0.00");         // Delta
  sheet.getRange(2, 9, 5000, 9).setNumberFormat("0.00");         // Theta
  sheet.getRange(2, 10, 5000, 10).setNumberFormat("$#,##0.00");  // Strike
  sheet.getRange(2, 11, 5000, 11).setNumberFormat("yyyy-mm-dd"); // Expiration
  var protection = sheet.getRange(1, 1, 1, headers.length).protect();
  protection.setDescription("Header row — do not edit");
  protection.setWarningOnly(true);
}


// =============================================================================
// SHEET 3: WEEKLY SUMMARY
// =============================================================================

/**
 * Sets up the Weekly Summary sheet with headers, formulas, and
 * conditional formatting.
 *
 * Columns A-S:
 *   A: Week #
 *   B: Week Start
 *   C: Week End
 *   D: Starting NAV
 *   E: Ending NAV
 *   F: Weekly P&L ($)
 *   G: Weekly P&L (%)
 *   H: Cumulative Return %
 *   I: Trades Opened
 *   J: Trades Closed
 *   K: Winners
 *   L: Losers
 *   M: Win Rate
 *   N: Rolling 4-Week Sharpe
 *   O: Max Drawdown (from Daily Dashboard)
 *   P: Rule Violations
 *   Q: Automation Uptime %
 *   R: Behavioral Score (/7)
 *   S: Notes
 */
function setupWeeklySummary(sheet) {
  var DATA_ROWS = 52; // One year of weeks
  var STARTING_CAPITAL = 100000;
  var RISK_FREE_WEEKLY = 0.000847; // (1+0.045)^(1/52)-1

  // -------------------------------------------------------------------------
  // Headers
  // -------------------------------------------------------------------------
  var headers = [
    "Week #",                  // A
    "Week Start",              // B
    "Week End",                // C
    "Starting NAV",            // D
    "Ending NAV",              // E
    "Weekly P&L ($)",          // F
    "Weekly P&L (%)",          // G
    "Cumulative Return %",     // H
    "Trades Opened",           // I
    "Trades Closed",           // J
    "Winners",                 // K
    "Losers",                  // L
    "Win Rate",                // M
    "Rolling 4-Wk Sharpe",    // N
    "Max Drawdown",            // O
    "Rule Violations",         // P
    "Automation Uptime %",     // Q
    "Behavioral Score (/7)",   // R
    "Notes"                    // S
  ];

  sheet.getRange(1, 1, 1, headers.length).setValues([headers]);

  // -------------------------------------------------------------------------
  // Header formatting
  // -------------------------------------------------------------------------
  var headerRange = sheet.getRange(1, 1, 1, headers.length);
  headerRange.setBackground("#533483")
             .setFontColor("#ffffff")
             .setFontWeight("bold")
             .setFontSize(10)
             .setHorizontalAlignment("center")
             .setVerticalAlignment("middle")
             .setWrap(true);
  sheet.setFrozenRows(1);
  sheet.setRowHeight(1, 40);

  // -------------------------------------------------------------------------
  // Column widths
  // -------------------------------------------------------------------------
  sheet.setColumnWidth(1, 70);    // A: Week #
  sheet.setColumnWidth(2, 100);   // B: Week Start
  sheet.setColumnWidth(3, 100);   // C: Week End
  sheet.setColumnWidth(4, 120);   // D: Starting NAV
  sheet.setColumnWidth(5, 120);   // E: Ending NAV
  sheet.setColumnWidth(6, 120);   // F: Weekly P&L ($)
  sheet.setColumnWidth(7, 120);   // G: Weekly P&L (%)
  sheet.setColumnWidth(8, 140);   // H: Cumulative Return %
  sheet.setColumnWidth(9, 110);   // I: Trades Opened
  sheet.setColumnWidth(10, 110);  // J: Trades Closed
  sheet.setColumnWidth(11, 80);   // K: Winners
  sheet.setColumnWidth(12, 80);   // L: Losers
  sheet.setColumnWidth(13, 90);   // M: Win Rate
  sheet.setColumnWidth(14, 150);  // N: Rolling 4-Wk Sharpe
  sheet.setColumnWidth(15, 120);  // O: Max Drawdown
  sheet.setColumnWidth(16, 120);  // P: Rule Violations
  sheet.setColumnWidth(17, 140);  // Q: Automation Uptime %
  sheet.setColumnWidth(18, 150);  // R: Behavioral Score
  sheet.setColumnWidth(19, 250);  // S: Notes

  // -------------------------------------------------------------------------
  // Formulas (rows 2 to DATA_ROWS+1)
  // -------------------------------------------------------------------------
  for (var row = 2; row <= DATA_ROWS + 1; row++) {
    var r = row;

    // F: Weekly P&L ($) = Ending NAV - Starting NAV
    sheet.getRange(r, 6).setFormula(
      '=IF(OR(D' + r + '="",E' + r + '=""),"",E' + r + '-D' + r + ')'
    );

    // G: Weekly P&L (%) = Weekly P&L / Starting NAV
    sheet.getRange(r, 7).setFormula(
      '=IF(OR(D' + r + '="",E' + r + '=""),"",F' + r + '/D' + r + ')'
    );

    // H: Cumulative Return % = (Ending NAV - $100,000) / $100,000
    sheet.getRange(r, 8).setFormula(
      '=IF(E' + r + '="","",(E' + r + '-' + STARTING_CAPITAL + ')/' + STARTING_CAPITAL + ')'
    );

    // L: Losers = Trades Closed - Winners
    sheet.getRange(r, 12).setFormula(
      '=IF(J' + r + '="","",J' + r + '-K' + r + ')'
    );

    // M: Win Rate = Winners / Trades Closed
    sheet.getRange(r, 13).setFormula(
      '=IF(OR(J' + r + '="",J' + r + '=0),"",K' + r + '/J' + r + ')'
    );

    // N: Rolling 4-Week Sharpe
    //   =IF(COUNT(last 4 weekly returns)>=4,
    //       (AVERAGE(last 4 weekly returns) - risk_free_weekly) / STDEV(last 4 weekly returns) * SQRT(52),
    //       "Need 4+ weeks")
    //
    //   For rows 2-4, always "Need 4+ weeks"
    //   For row 5+, look back 4 rows in column G
    if (r < 5) {
      sheet.getRange(r, 14).setFormula(
        '=IF(G' + r + '="","","Need 4+ weeks")'
      );
    } else {
      var startRow = r - 3;
      sheet.getRange(r, 14).setFormula(
        '=IF(G' + r + '="",' +
          '"",' +
          'IF(COUNT(G' + startRow + ':G' + r + ')>=4,' +
            '(AVERAGE(G' + startRow + ':G' + r + ')-' + RISK_FREE_WEEKLY + ')/STDEV(G' + startRow + ':G' + r + ')*SQRT(52),' +
            '"Need 4+ weeks"' +
          ')' +
        ')'
      );
    }

    // O: Max Drawdown — pulls from Daily Dashboard
    //   Finds the minimum drawdown from the Daily Dashboard sheet
    //   between this week's start and end dates
    sheet.getRange(r, 15).setFormula(
      '=IF(OR(B' + r + '="",C' + r + '=""),' +
        '"",' +
        'IFERROR(' +
          'MINIFS(\'Daily Dashboard\'!H:H,\'Daily Dashboard\'!A:A,">="&B' + r + ',\'Daily Dashboard\'!A:A,"<="&C' + r + '),' +
          'MIN(\'Daily Dashboard\'!H$2:H)' +
        ')' +
      ')'
    );
  }

  // -------------------------------------------------------------------------
  // Number formatting
  // -------------------------------------------------------------------------
  sheet.getRange(2, 1, DATA_ROWS, 1).setNumberFormat("0");              // A: Week #
  sheet.getRange(2, 2, DATA_ROWS, 1).setNumberFormat("yyyy-mm-dd");     // B: Week Start
  sheet.getRange(2, 3, DATA_ROWS, 1).setNumberFormat("yyyy-mm-dd");     // C: Week End
  sheet.getRange(2, 4, DATA_ROWS, 1).setNumberFormat("$#,##0.00");      // D: Starting NAV
  sheet.getRange(2, 5, DATA_ROWS, 1).setNumberFormat("$#,##0.00");      // E: Ending NAV
  sheet.getRange(2, 6, DATA_ROWS, 1).setNumberFormat("$#,##0.00");      // F: Weekly P&L ($)
  sheet.getRange(2, 7, DATA_ROWS, 1).setNumberFormat("0.00%");          // G: Weekly P&L (%)
  sheet.getRange(2, 8, DATA_ROWS, 1).setNumberFormat("0.00%");          // H: Cumulative Return %
  sheet.getRange(2, 9, DATA_ROWS, 1).setNumberFormat("0");              // I: Trades Opened
  sheet.getRange(2, 10, DATA_ROWS, 1).setNumberFormat("0");             // J: Trades Closed
  sheet.getRange(2, 11, DATA_ROWS, 1).setNumberFormat("0");             // K: Winners
  sheet.getRange(2, 12, DATA_ROWS, 1).setNumberFormat("0");             // L: Losers
  sheet.getRange(2, 13, DATA_ROWS, 1).setNumberFormat("0.0%");          // M: Win Rate
  sheet.getRange(2, 14, DATA_ROWS, 1).setNumberFormat("0.00");          // N: Rolling Sharpe
  sheet.getRange(2, 15, DATA_ROWS, 1).setNumberFormat("0.00%");         // O: Max Drawdown
  sheet.getRange(2, 16, DATA_ROWS, 1).setNumberFormat("0");             // P: Rule Violations
  sheet.getRange(2, 17, DATA_ROWS, 1).setNumberFormat("0.0%");          // Q: Automation Uptime %
  sheet.getRange(2, 18, DATA_ROWS, 1).setNumberFormat("0");             // R: Behavioral Score

  // -------------------------------------------------------------------------
  // Conditional Formatting
  // -------------------------------------------------------------------------
  var rules = sheet.getConditionalFormatRules();

  // Win Rate (column M) — Green if > 60%
  var winRateGreen = SpreadsheetApp.newConditionalFormatRule()
    .whenNumberGreaterThan(0.60)
    .setBackground("#d4edda")
    .setFontColor("#155724")
    .setRanges([sheet.getRange(2, 13, DATA_ROWS, 1)])
    .build();
  rules.push(winRateGreen);

  // Win Rate (column M) — Red if < 50%
  var winRateRed = SpreadsheetApp.newConditionalFormatRule()
    .whenNumberLessThan(0.50)
    .setBackground("#f8d7da")
    .setFontColor("#721c24")
    .setRanges([sheet.getRange(2, 13, DATA_ROWS, 1)])
    .build();
  rules.push(winRateRed);

  // Behavioral Score (column R) — Red if < 5
  var behaviorRed = SpreadsheetApp.newConditionalFormatRule()
    .whenNumberLessThan(5)
    .setBackground("#f8d7da")
    .setFontColor("#721c24")
    .setBold(true)
    .setRanges([sheet.getRange(2, 18, DATA_ROWS, 1)])
    .build();
  rules.push(behaviorRed);

  // Weekly P&L ($) — Green/Red
  var weeklyPnlGreen = SpreadsheetApp.newConditionalFormatRule()
    .whenNumberGreaterThan(0)
    .setBackground("#d4edda")
    .setFontColor("#155724")
    .setRanges([sheet.getRange(2, 6, DATA_ROWS, 1)])
    .build();
  rules.push(weeklyPnlGreen);

  var weeklyPnlRed = SpreadsheetApp.newConditionalFormatRule()
    .whenNumberLessThan(0)
    .setBackground("#f8d7da")
    .setFontColor("#721c24")
    .setRanges([sheet.getRange(2, 6, DATA_ROWS, 1)])
    .build();
  rules.push(weeklyPnlRed);

  // Max Drawdown (column O) — Red if worse than -5%
  var maxDDRed = SpreadsheetApp.newConditionalFormatRule()
    .whenNumberLessThan(-0.05)
    .setBackground("#f8d7da")
    .setFontColor("#721c24")
    .setBold(true)
    .setRanges([sheet.getRange(2, 15, DATA_ROWS, 1)])
    .build();
  rules.push(maxDDRed);

  // Rule Violations (column P) — Red if > 0
  var violationsRed = SpreadsheetApp.newConditionalFormatRule()
    .whenNumberGreaterThan(0)
    .setBackground("#f8d7da")
    .setFontColor("#721c24")
    .setBold(true)
    .setRanges([sheet.getRange(2, 16, DATA_ROWS, 1)])
    .build();
  rules.push(violationsRed);

  sheet.setConditionalFormatRules(rules);

  // -------------------------------------------------------------------------
  // Alternating row colors
  // -------------------------------------------------------------------------
  var bandingRange = sheet.getRange(1, 1, DATA_ROWS + 1, headers.length);
  bandingRange.applyRowBanding(SpreadsheetApp.BandingTheme.LIGHT_GREY, true, false);

  // -------------------------------------------------------------------------
  // Protect header row
  // -------------------------------------------------------------------------
  var protection = sheet.getRange(1, 1, 1, headers.length).protect();
  protection.setDescription("Header row — do not edit");
  protection.setWarningOnly(true);
}


// =============================================================================
// SHEET 4: RISK LIMITS
// =============================================================================

/**
 * Sets up the Risk Limits reference sheet with all risk parameters,
 * starting capital, allocation targets, drawdown tiers, and Greeks limits.
 *
 * This is a static reference sheet — no data entry required.
 */
function setupRiskLimits(sheet) {

  // =========================================================================
  // SECTION 1: Title & Starting Parameters
  // =========================================================================

  // Title
  sheet.getRange("A1").setValue("ALTAMIRA CAPITAL — RISK LIMITS & PARAMETERS");
  sheet.getRange("A1:F1").merge()
       .setBackground("#1a1a2e")
       .setFontColor("#ffffff")
       .setFontWeight("bold")
       .setFontSize(14)
       .setHorizontalAlignment("center");
  sheet.setRowHeight(1, 40);

  // Subtitle
  sheet.getRange("A2").setValue("Paper Trading Phase | Version 1.0 | 2026-02-18");
  sheet.getRange("A2:F2").merge()
       .setBackground("#1a1a2e")
       .setFontColor("#aaaaaa")
       .setFontSize(10)
       .setHorizontalAlignment("center");

  // =========================================================================
  // SECTION 2: Starting Parameters
  // =========================================================================

  var startRow = 4;
  sheet.getRange("A" + startRow).setValue("STARTING PARAMETERS");
  sheet.getRange("A" + startRow + ":F" + startRow).merge()
       .setBackground("#0f3460")
       .setFontColor("#ffffff")
       .setFontWeight("bold")
       .setFontSize(11)
       .setHorizontalAlignment("left");

  var paramData = [
    ["Parameter", "Value", "Notes", "", "", ""],
    ["Starting Capital", "$100,000", "Paper trading matches planned live capital", "", "", ""],
    ["CSP Allocation", "$40,000 (40%)", "Cash-secured puts — options premium selling", "", "", ""],
    ["Momentum Allocation", "$40,000 (40%)", "Long equity positions via 50-day MA signal", "", "", ""],
    ["Cash Reserve", "$20,000 (20%)", "Dry powder, margin buffer, drawdown cushion", "", "", ""],
    ["Paper Trading Start", "2026-03-01", "Phase 1: CSP only", "", "", ""],
    ["Minimum Duration", "4 weeks (28 days)", "All go-live criteria must be met before transition", "", "", ""]
  ];

  sheet.getRange(startRow + 1, 1, paramData.length, 6).setValues(paramData);

  // Format parameter header
  sheet.getRange(startRow + 1, 1, 1, 3)
       .setFontWeight("bold")
       .setBackground("#e8e8e8");

  // Format parameter values
  sheet.getRange(startRow + 2, 1, paramData.length - 1, 3)
       .setBorder(true, true, true, true, true, true, "#cccccc", SpreadsheetApp.BorderStyle.SOLID);

  // =========================================================================
  // SECTION 3: Position Risk Limits
  // =========================================================================

  startRow = 13;
  sheet.getRange("A" + startRow).setValue("POSITION RISK LIMITS");
  sheet.getRange("A" + startRow + ":F" + startRow).merge()
       .setBackground("#0f3460")
       .setFontColor("#ffffff")
       .setFontWeight("bold")
       .setFontSize(11)
       .setHorizontalAlignment("left");

  var riskData = [
    ["Risk Parameter", "Limit", "At $100K", "Enforcement", "Breach Action", ""],
    ["Single position", "≤ 5% of portfolio", "$5,000", "Pre-trade check", "Block trade", ""],
    ["Sector exposure", "≤ 25% of portfolio", "$25,000", "Weekly review", "Reduce to limit within 1 day", ""],
    ["Technology sector", "≤ 35% combined", "$35,000", "Weekly review", "Rebalance trigger at 30%", ""],
    ["Options total (notional)", "≤ 30% of portfolio", "$30,000", "Pre-trade check", "Block new options trades", ""],
    ["Cash reserve", "≥ 15% of portfolio", "$15,000", "Continuous", "Block new trades if breached", ""],
    ["Correlated positions", "≤ 3 per sector", "3 names max", "Pre-trade check", "Block correlated trade", ""],
    ["Max correlated (portfolio)", "≤ 5 total", "5 names max", "Pre-trade check", "Block trade", ""]
  ];

  sheet.getRange(startRow + 1, 1, riskData.length, 6).setValues(riskData);

  // Format risk header
  sheet.getRange(startRow + 1, 1, 1, 5)
       .setFontWeight("bold")
       .setBackground("#e8e8e8");

  // Format risk values
  sheet.getRange(startRow + 2, 1, riskData.length - 1, 5)
       .setBorder(true, true, true, true, true, true, "#cccccc", SpreadsheetApp.BorderStyle.SOLID);

  // Highlight critical limits
  sheet.getRange(startRow + 2, 2, riskData.length - 1, 1)
       .setFontWeight("bold")
       .setFontColor("#0f3460");

  // =========================================================================
  // SECTION 4: Greeks Limits
  // =========================================================================

  startRow = 23;
  sheet.getRange("A" + startRow).setValue("PORTFOLIO GREEKS LIMITS (per $100K)");
  sheet.getRange("A" + startRow + ":F" + startRow).merge()
       .setBackground("#0f3460")
       .setFontColor("#ffffff")
       .setFontWeight("bold")
       .setFontSize(11)
       .setHorizontalAlignment("left");

  var greeksData = [
    ["Greek", "Range", "Rationale", "Monitoring", "", ""],
    ["Net Delta", "-30 to +50", "Limits directional exposure; CSP short delta balanced by long equity", "Daily dashboard", "", ""],
    ["Net Gamma", "> -0.05", "Prevents convexity blowup on large moves", "Daily dashboard", "", ""],
    ["Net Theta", "Must be positive (+$50 to +$200)", "Ensures positive time decay from short options", "Daily dashboard", "", ""],
    ["Net Vega", "> -$500", "Limits exposure to volatility expansion", "Daily dashboard", "", ""]
  ];

  sheet.getRange(startRow + 1, 1, greeksData.length, 6).setValues(greeksData);

  sheet.getRange(startRow + 1, 1, 1, 4)
       .setFontWeight("bold")
       .setBackground("#e8e8e8");

  sheet.getRange(startRow + 2, 1, greeksData.length - 1, 4)
       .setBorder(true, true, true, true, true, true, "#cccccc", SpreadsheetApp.BorderStyle.SOLID);

  sheet.getRange(startRow + 2, 2, greeksData.length - 1, 1)
       .setFontWeight("bold")
       .setFontColor("#0f3460");

  // =========================================================================
  // SECTION 5: Drawdown Tiers
  // =========================================================================

  startRow = 30;
  sheet.getRange("A" + startRow).setValue("DRAWDOWN MANAGEMENT TIERS");
  sheet.getRange("A" + startRow + ":F" + startRow).merge()
       .setBackground("#0f3460")
       .setFontColor("#ffffff")
       .setFontWeight("bold")
       .setFontSize(11)
       .setHorizontalAlignment("left");

  var drawdownData = [
    ["Tier", "Trigger", "Position Action", "Sizing Action", "Cash Target", "Duration"],
    [
      "Tier 1 — Yellow",
      "-5% from peak",
      "Review all; close conviction < 3",
      "Reduce new sizes by 25%",
      "25%",
      "Until within 2.5% of peak"
    ],
    [
      "Tier 2 — Orange",
      "-10% from peak",
      "Close lowest-conviction 50%",
      "Reduce sizes by 50%",
      "40%",
      "Minimum 10 trading days"
    ],
    [
      "Tier 3 — Red",
      "-15% from peak",
      "Close ALL options; equity above MA only",
      "No new positions for 20 days",
      "60%",
      "Minimum 20 trading days"
    ]
  ];

  sheet.getRange(startRow + 1, 1, drawdownData.length, 6).setValues(drawdownData);

  sheet.getRange(startRow + 1, 1, 1, 6)
       .setFontWeight("bold")
       .setBackground("#e8e8e8");

  // Color-code drawdown tiers
  sheet.getRange(startRow + 2, 1, 1, 6)
       .setBackground("#fff3cd")   // Yellow
       .setBorder(true, true, true, true, true, true, "#cccccc", SpreadsheetApp.BorderStyle.SOLID);
  sheet.getRange(startRow + 3, 1, 1, 6)
       .setBackground("#ffe0b2")   // Orange
       .setBorder(true, true, true, true, true, true, "#cccccc", SpreadsheetApp.BorderStyle.SOLID);
  sheet.getRange(startRow + 4, 1, 1, 6)
       .setBackground("#f8d7da")   // Red
       .setBorder(true, true, true, true, true, true, "#cccccc", SpreadsheetApp.BorderStyle.SOLID);

  // =========================================================================
  // SECTION 6: Circuit Breakers
  // =========================================================================

  startRow = 36;
  sheet.getRange("A" + startRow).setValue("CIRCUIT BREAKERS");
  sheet.getRange("A" + startRow + ":F" + startRow).merge()
       .setBackground("#0f3460")
       .setFontColor("#ffffff")
       .setFontWeight("bold")
       .setFontSize(11)
       .setHorizontalAlignment("left");

  var circuitData = [
    ["Circuit Breaker", "Trigger", "Action", "", "", ""],
    ["Daily loss limit", "-2% in a single day", "Halt all new trades for remainder of day", "", "", ""],
    ["Weekly loss limit", "-3% in a single week", "No new positions for the following week; reduce sizing 25%", "", "", ""],
    ["Monthly loss limit", "-5% in a calendar month", "Trigger Tier 1 protocol; full position review", "", "", ""],
    ["Consecutive losses", "5 consecutive losing trades", "Halt trading for 3 trading days; review journal", "", "", ""],
    ["Single-day options loss", "Any option loses > 3% of portfolio in one day", "Immediately close the position", "", "", ""]
  ];

  sheet.getRange(startRow + 1, 1, circuitData.length, 6).setValues(circuitData);

  sheet.getRange(startRow + 1, 1, 1, 3)
       .setFontWeight("bold")
       .setBackground("#e8e8e8");

  sheet.getRange(startRow + 2, 1, circuitData.length - 1, 3)
       .setBorder(true, true, true, true, true, true, "#cccccc", SpreadsheetApp.BorderStyle.SOLID);

  // =========================================================================
  // SECTION 7: VIX-Adjusted Sizing
  // =========================================================================

  startRow = 44;
  sheet.getRange("A" + startRow).setValue("VIX-ADJUSTED POSITION SIZING");
  sheet.getRange("A" + startRow + ":F" + startRow).merge()
       .setBackground("#0f3460")
       .setFontColor("#ffffff")
       .setFontWeight("bold")
       .setFontSize(11)
       .setHorizontalAlignment("left");

  var vixData = [
    ["VIX Range", "CSP Sizing", "Momentum Sizing", "Cash Reserve", "Hedge Action", ""],
    ["< 15", "Standard (100%)", "Standard (100%)", "20%", "Increase hedging (cheap protection)", ""],
    ["15 – 25", "Standard (100%)", "Standard (100%)", "15%", "Standard", ""],
    ["25 – 35", "Reduce by 25% (75%)", "Reduce by 25% (75%)", "25%", "Premium selling attractive but size smaller", ""],
    ["> 35", "Reduce by 50% (50%)", "Reduce by 50% (50%)", "40%", "Crisis regime; capital preservation priority", ""]
  ];

  sheet.getRange(startRow + 1, 1, vixData.length, 6).setValues(vixData);

  sheet.getRange(startRow + 1, 1, 1, 5)
       .setFontWeight("bold")
       .setBackground("#e8e8e8");

  sheet.getRange(startRow + 2, 1, vixData.length - 1, 5)
       .setBorder(true, true, true, true, true, true, "#cccccc", SpreadsheetApp.BorderStyle.SOLID);

  // =========================================================================
  // SECTION 8: CSP & Equity Exit Rules
  // =========================================================================

  startRow = 51;
  sheet.getRange("A" + startRow).setValue("EXIT RULES — QUICK REFERENCE");
  sheet.getRange("A" + startRow + ":F" + startRow).merge()
       .setBackground("#0f3460")
       .setFontColor("#ffffff")
       .setFontWeight("bold")
       .setFontSize(11)
       .setHorizontalAlignment("left");

  var exitData = [
    ["Strategy", "Exit Trigger", "Condition", "Action", "", ""],
    ["CSP", "Profit target", "P&L reaches 50% of max credit", "Close (BTC)", "", ""],
    ["CSP", "Stop-loss", "Loss reaches 200% of credit", "Close immediately", "", ""],
    ["CSP", "Delta breach", "Delta exceeds 0.50", "Close or roll within 1 hour", "", ""],
    ["CSP", "DTE threshold", "DTE < 7", "Close all — no exceptions", "", ""],
    ["CSP", "Earnings conflict", "Earnings within DTE", "Close 1 day before earnings", "", ""],
    ["Momentum", "MA crossover", "Price closes below 50-day MA", "Exit at next rebalance or within 2 days", "", ""],
    ["Momentum", "Trailing stop", "Position declines 8% from high", "Exit immediately", "", ""],
    ["Momentum", "Hard stop", "Position declines 10% from entry", "Exit immediately", "", ""],
    ["Momentum", "3 closes below MA", "3 consecutive closes below 50-day MA", "Exit next day — do not wait for rebalance", "", ""]
  ];

  sheet.getRange(startRow + 1, 1, exitData.length, 6).setValues(exitData);

  sheet.getRange(startRow + 1, 1, 1, 4)
       .setFontWeight("bold")
       .setBackground("#e8e8e8");

  sheet.getRange(startRow + 2, 1, exitData.length - 1, 4)
       .setBorder(true, true, true, true, true, true, "#cccccc", SpreadsheetApp.BorderStyle.SOLID);

  // =========================================================================
  // SECTION 9: Go-Live Criteria
  // =========================================================================

  startRow = 63;
  sheet.getRange("A" + startRow).setValue("GO-LIVE CRITERIA (ALL MUST BE MET)");
  sheet.getRange("A" + startRow + ":F" + startRow).merge()
       .setBackground("#0f3460")
       .setFontColor("#ffffff")
       .setFontWeight("bold")
       .setFontSize(11)
       .setHorizontalAlignment("left");

  var goLiveData = [
    ["#", "Criterion", "Target", "Status", "", ""],
    ["1", "Paper trading duration", "≥ 4 weeks", "", "", ""],
    ["2", "Total CSP trades closed", "≥ 20", "", "", ""],
    ["3", "Momentum rebalance cycles", "≥ 4", "", "", ""],
    ["4", "Win rate (all strategies)", "> 60%", "", "", ""],
    ["5", "CSP win rate", "> 65%", "", "", ""],
    ["6", "Sharpe ratio (annualized)", "> 1.0", "", "", ""],
    ["7", "Maximum drawdown", "Better than -10%", "", "", ""],
    ["8", "No single losing week > 3%", "0 violations", "", "", ""],
    ["9", "Adjusted P&L positive", "> $0", "", "", ""],
    ["10", "Automation uptime", "> 95%", "", "", ""],
    ["11", "100% rule compliance", "Zero violations", "", "", ""],
    ["12", "Daily tracking — zero missed days", "0 missed", "", "", ""],
    ["13", "Weekly reviews completed", "4+", "", "", ""],
    ["14", "Pre-trade checklist every trade", "100%", "", "", ""],
    ["15", "Emotional readiness", "Self-assessed \"Yes\"", "", "", ""]
  ];

  sheet.getRange(startRow + 1, 1, goLiveData.length, 6).setValues(goLiveData);

  sheet.getRange(startRow + 1, 1, 1, 4)
       .setFontWeight("bold")
       .setBackground("#e8e8e8");

  sheet.getRange(startRow + 2, 1, goLiveData.length - 1, 4)
       .setBorder(true, true, true, true, true, true, "#cccccc", SpreadsheetApp.BorderStyle.SOLID);

  // Status column — dropdown: Pass / Fail / Pending
  var goLiveStatusRule = SpreadsheetApp.newDataValidation()
    .requireValueInList(["Pass", "Fail", "Pending"], true)
    .setAllowInvalid(false)
    .build();
  sheet.getRange(startRow + 2, 4, goLiveData.length - 1, 1).setDataValidation(goLiveStatusRule);

  // =========================================================================
  // SECTION 10: Pre-Trade Checklist
  // =========================================================================

  startRow = 81;
  sheet.getRange("A" + startRow).setValue("PRE-TRADE CHECKLIST (6-POINT)");
  sheet.getRange("A" + startRow + ":F" + startRow).merge()
       .setBackground("#0f3460")
       .setFontColor("#ffffff")
       .setFontWeight("bold")
       .setFontSize(11)
       .setHorizontalAlignment("left");

  var checklistData = [
    ["#", "Check", "Question", "Required Answer", "", ""],
    ["1", "Thesis", "What is the thesis for this trade?", "Written in 1-2 sentences", "", ""],
    ["2", "Edge", "What is the edge? Why is the market mispricing this?", "Specific: IV rank, catalyst, trend", "", ""],
    ["3", "Risk", "What is the maximum loss? Probability?", "Dollar amount and % of portfolio", "", ""],
    ["4", "Exit", "What is the profit target and stop-loss?", "Specific prices/levels before entry", "", ""],
    ["5", "Portfolio Fit", "Does this trade fit? Sector, correlation, exposure?", "Confirm no limits breached", "", ""],
    ["6", "Buying Power", "Sufficient cash/margin? Cash reserve stays above 15%?", "Yes with specific numbers", "", ""]
  ];

  sheet.getRange(startRow + 1, 1, checklistData.length, 6).setValues(checklistData);

  sheet.getRange(startRow + 1, 1, 1, 4)
       .setFontWeight("bold")
       .setBackground("#e8e8e8");

  sheet.getRange(startRow + 2, 1, checklistData.length - 1, 4)
       .setBorder(true, true, true, true, true, true, "#cccccc", SpreadsheetApp.BorderStyle.SOLID);

  // =========================================================================
  // SECTION 11: Core Universe
  // =========================================================================

  startRow = 90;
  sheet.getRange("A" + startRow).setValue("CORE TICKER UNIVERSE");
  sheet.getRange("A" + startRow + ":F" + startRow).merge()
       .setBackground("#0f3460")
       .setFontColor("#ffffff")
       .setFontWeight("bold")
       .setFontSize(11)
       .setHorizontalAlignment("left");

  var universeData = [
    ["Ticker", "Sector", "CSP Eligible", "Momentum Eligible", "Known Correlations", ""],
    ["AAPL", "Technology", "Yes", "Yes", "MSFT (0.75-0.85)", ""],
    ["MSFT", "Technology", "Yes", "Yes", "AAPL (0.75-0.85)", ""],
    ["GOOGL", "Technology", "Yes", "Yes", "META (0.70-0.80)", ""],
    ["AMZN", "Technology", "Yes", "Yes", "", ""],
    ["META", "Technology", "Yes", "Yes", "GOOGL (0.70-0.80)", ""],
    ["NVDA", "Technology", "Yes", "Yes", "AVGO (0.75-0.85)", ""],
    ["AVGO", "Technology", "Yes", "Yes", "NVDA (0.75-0.85)", ""],
    ["COST", "Consumer Defensive", "Yes", "Yes", "", ""],
    ["V", "Financial Services", "Yes", "Yes", "MA (0.85-0.95)", ""],
    ["MA", "Financial Services", "Yes", "Yes", "V (0.85-0.95)", ""],
    ["SPY", "Index", "Yes (CSP + Hedge)", "No", "", ""]
  ];

  sheet.getRange(startRow + 1, 1, universeData.length, 6).setValues(universeData);

  sheet.getRange(startRow + 1, 1, 1, 5)
       .setFontWeight("bold")
       .setBackground("#e8e8e8");

  sheet.getRange(startRow + 2, 1, universeData.length - 1, 5)
       .setBorder(true, true, true, true, true, true, "#cccccc", SpreadsheetApp.BorderStyle.SOLID);

  // =========================================================================
  // SECTION 12: Footer
  // =========================================================================

  startRow = 104;
  sheet.getRange("A" + startRow).setValue(
    "Discipline over complexity. | Altamira Capital | Risk Management Framework v1.0"
  );
  sheet.getRange("A" + startRow + ":F" + startRow).merge()
       .setFontColor("#888888")
       .setFontSize(9)
       .setFontStyle("italic")
       .setHorizontalAlignment("center");

  // =========================================================================
  // Global formatting for Risk Limits sheet
  // =========================================================================

  // Column widths
  sheet.setColumnWidth(1, 160);
  sheet.setColumnWidth(2, 200);
  sheet.setColumnWidth(3, 220);
  sheet.setColumnWidth(4, 200);
  sheet.setColumnWidth(5, 200);
  sheet.setColumnWidth(6, 50);

  // Default font
  sheet.getRange("A1:F104").setFontFamily("Arial");

  // -------------------------------------------------------------------------
  // Protect entire sheet (warning only — still allows edits for Status column)
  // -------------------------------------------------------------------------
  var protection = sheet.protect();
  protection.setDescription("Risk Limits reference sheet — edit with caution");
  protection.setWarningOnly(true);
}


// =============================================================================
// UTILITY: Add custom menu to spreadsheet
// =============================================================================

/**
 * Creates a custom menu when the spreadsheet opens.
 * Provides easy access to the setup function and utilities.
 */
function onOpen() {
  var ui = SpreadsheetApp.getUi();
  ui.createMenu("Altamira Capital")
    .addItem("Setup Paper Trading Workbook", "setupPaperTradingWorkbook")
    .addSeparator()
    .addItem("Add Sample Trade (Demo)", "addSampleTrade")
    .addItem("Add Sample Daily Entry (Demo)", "addSampleDailyEntry")
    .addItem("Add Sample Weekly Entry (Demo)", "addSampleWeeklyEntry")
    .addToUi();
}


// =============================================================================
// UTILITY: Sample Data Functions (for testing/demo)
// =============================================================================

/**
 * Adds a sample trade to the Trade Log for demonstration purposes.
 * Useful for verifying formulas and formatting work correctly.
 */
function addSampleTrade() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("Trade Log");

  if (!sheet) {
    SpreadsheetApp.getUi().alert("Trade Log sheet not found. Run setup first.");
    return;
  }

  // Find the first empty row (check column B — Date Entry)
  var lastRow = sheet.getLastRow();
  var targetRow = 2;
  for (var r = 2; r <= lastRow + 1; r++) {
    if (sheet.getRange(r, 2).getValue() === "") {
      targetRow = r;
      break;
    }
  }

  // Sample CSP trade: Sell AAPL $225 put for $3.20, closed at $1.60
  var sampleData = [
    // B: Date Entry
    new Date(2026, 2, 3),   // 2026-03-03
    // C: Date Exit
    new Date(2026, 2, 15),  // 2026-03-15
    // D: Ticker
    "AAPL",
    // E: Strategy
    "CSP",
    // F: Direction
    "STO",
    // G: Strike
    225.00,
    // H: Expiration
    new Date(2026, 3, 4),   // 2026-04-04
    // I: DTE at Entry
    32,
    // J: Delta at Entry
    -0.22,
    // K: IV Rank at Entry
    45,
    // L: Contracts
    1,
    // M: Entry Price (credit)
    3.20,
    // N: Exit Price
    1.60
  ];

  // Write data to columns B through N (columns 2-14)
  sheet.getRange(targetRow, 2, 1, sampleData.length).setValues([sampleData]);

  // Fill in text columns
  sheet.getRange(targetRow, 21).setValue("Profit Target");   // U: Exit Reason
  sheet.getRange(targetRow, 22).setValue("IV elevated (rank 45); AAPL above 50-day MA; strong support at 225"); // V: Thesis
  sheet.getRange(targetRow, 23).setValue("IV overpriced vs. realized; 50-day MA bullish confirmation"); // W: Edge
  sheet.getRange(targetRow, 24).setValue("Closed at 50% profit in 12 days. Thesis played out as expected."); // X: Outcome Notes
  sheet.getRange(targetRow, 25).setValue("Yes");             // Y: Rule Compliance
  sheet.getRange(targetRow, 26).setValue("Entry timing was good. Consider selling at higher IV rank next time."); // Z: Lessons

  SpreadsheetApp.getUi().alert(
    "Sample Trade Added",
    "Added a sample CSP trade on AAPL to row " + targetRow + ".\n\n" +
    "Check that formulas in columns O-T calculated correctly:\n" +
    "  Raw P&L:      Should be $160.00\n" +
    "  Commission:   Should be $1.30\n" +
    "  Slippage:     Should be $6.40\n" +
    "  Adjusted P&L: Should be $152.30\n" +
    "  Days Held:    Should be 12",
    SpreadsheetApp.getUi().ButtonSet.OK
  );
}

/**
 * Adds a sample daily entry to the Daily Dashboard for demonstration.
 */
function addSampleDailyEntry() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("Daily Dashboard");

  if (!sheet) {
    SpreadsheetApp.getUi().alert("Daily Dashboard sheet not found. Run setup first.");
    return;
  }

  // Find the first empty row
  var targetRow = 2;
  for (var r = 2; r <= sheet.getLastRow() + 1; r++) {
    if (sheet.getRange(r, 1).getValue() === "") {
      targetRow = r;
      break;
    }
  }

  // Sample data for first day
  var sampleData;
  if (targetRow === 2) {
    sampleData = [
      new Date(2026, 2, 3),  // A: Date (2026-03-03)
      100250,                 // B: Portfolio Value
      // C-H: formulas already in place
    ];
    sheet.getRange(targetRow, 1).setValue(sampleData[0]);
    sheet.getRange(targetRow, 2).setValue(sampleData[1]);
  } else {
    sampleData = [
      new Date(2026, 2, 4),  // A: Date (2026-03-04)
      100480,                 // B: Portfolio Value
    ];
    sheet.getRange(targetRow, 1).setValue(sampleData[0]);
    sheet.getRange(targetRow, 2).setValue(sampleData[1]);
  }

  // Fill manual columns
  sheet.getRange(targetRow, 9).setValue(12.5);    // I: Net Delta
  sheet.getRange(targetRow, 10).setValue(35.00);  // J: Daily Theta
  sheet.getRange(targetRow, 11).setValue(2);      // K: Open CSP Count
  sheet.getRange(targetRow, 12).setValue(3);      // L: Open Equity Positions
  sheet.getRange(targetRow, 13).setValue(0.22);   // M: Cash %
  sheet.getRange(targetRow, 14).setValue(19.5);   // N: VIX Close
  sheet.getRange(targetRow, 15).setValue(505.25); // O: SPY Close
  sheet.getRange(targetRow, 16).setValue("First day of paper trading. All systems operational."); // P: Notes

  SpreadsheetApp.getUi().alert(
    "Sample Daily Entry Added",
    "Added a sample daily entry to row " + targetRow + ".\n" +
    "Check that formulas in columns C-H calculated correctly.",
    SpreadsheetApp.getUi().ButtonSet.OK
  );
}

/**
 * Adds a sample weekly entry to the Weekly Summary for demonstration.
 */
function addSampleWeeklyEntry() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("Weekly Summary");

  if (!sheet) {
    SpreadsheetApp.getUi().alert("Weekly Summary sheet not found. Run setup first.");
    return;
  }

  // Find first empty row
  var targetRow = 2;
  for (var r = 2; r <= sheet.getLastRow() + 1; r++) {
    if (sheet.getRange(r, 1).getValue() === "") {
      targetRow = r;
      break;
    }
  }

  var weekNum = targetRow - 1;

  // Sample data
  sheet.getRange(targetRow, 1).setValue(weekNum);                   // A: Week #
  sheet.getRange(targetRow, 2).setValue(new Date(2026, 2, 3));      // B: Week Start
  sheet.getRange(targetRow, 3).setValue(new Date(2026, 2, 7));      // C: Week End
  sheet.getRange(targetRow, 4).setValue(100000);                    // D: Starting NAV
  sheet.getRange(targetRow, 5).setValue(100480);                    // E: Ending NAV
  // F, G, H: formulas
  sheet.getRange(targetRow, 9).setValue(3);                         // I: Trades Opened
  sheet.getRange(targetRow, 10).setValue(1);                        // J: Trades Closed
  sheet.getRange(targetRow, 11).setValue(1);                        // K: Winners
  // L: formula (losers)
  // M: formula (win rate)
  // N: formula (Sharpe)
  // O: formula (max drawdown)
  sheet.getRange(targetRow, 16).setValue(0);                        // P: Rule Violations
  sheet.getRange(targetRow, 17).setValue(0.98);                     // Q: Automation Uptime
  sheet.getRange(targetRow, 18).setValue(7);                        // R: Behavioral Score
  sheet.getRange(targetRow, 19).setValue("Week 1: CSP only phase. 3 trades opened, 1 closed at profit target."); // S: Notes

  SpreadsheetApp.getUi().alert(
    "Sample Weekly Entry Added",
    "Added sample Week " + weekNum + " data to row " + targetRow + ".\n" +
    "Check that formulas in columns F, G, H, L, M, N, O calculated correctly.",
    SpreadsheetApp.getUi().ButtonSet.OK
  );
}
