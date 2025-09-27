import UIKit

private enum ReportTab: Int { case profit = 0, sales = 1, purchases = 2 }

class ReportsViewController: UIViewController, UITableViewDataSource, UITableViewDelegate {

    private let segmentedControl = UISegmentedControl(items: ["Profit", "Sales", "Purchases"])
    private let yearButton = UIButton(type: .system)
    private let tableView = UITableView(frame: .zero, style: .plain)
    private let loadingIndicator = UIActivityIndicatorView(style: .large)

    private var currentTab: ReportTab = .profit
    private var currentYear: String = String(Calendar.current.component(.year, from: Date()))

    private var profitRows: [ProfitReportRow] = []
    private var salesRows: [SalesReportRow] = []
    private var purchaseRows: [PurchasesReportRow] = []

    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        loadData()
    }

    private func setupUI() {
        view.backgroundColor = .systemBackground
        title = "Reports"

        segmentedControl.selectedSegmentIndex = currentTab.rawValue
        segmentedControl.addTarget(self, action: #selector(segmentChanged), for: .valueChanged)
        segmentedControl.translatesAutoresizingMaskIntoConstraints = false

        yearButton.setTitle("Year: \(currentYear) ▾", for: .normal)
        yearButton.addTarget(self, action: #selector(selectYear), for: .touchUpInside)
        yearButton.translatesAutoresizingMaskIntoConstraints = false

        tableView.dataSource = self
        tableView.delegate = self
        tableView.translatesAutoresizingMaskIntoConstraints = false

        loadingIndicator.hidesWhenStopped = true
        loadingIndicator.translatesAutoresizingMaskIntoConstraints = false

        view.addSubview(segmentedControl)
        view.addSubview(yearButton)
        view.addSubview(tableView)
        view.addSubview(loadingIndicator)

        NSLayoutConstraint.activate([
            segmentedControl.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor, constant: 8),
            segmentedControl.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 12),
            segmentedControl.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -12),

            yearButton.topAnchor.constraint(equalTo: segmentedControl.bottomAnchor, constant: 8),
            yearButton.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 12),

            tableView.topAnchor.constraint(equalTo: yearButton.bottomAnchor, constant: 8),
            tableView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            tableView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            tableView.bottomAnchor.constraint(equalTo: view.bottomAnchor),

            loadingIndicator.centerXAnchor.constraint(equalTo: tableView.centerXAnchor),
            loadingIndicator.centerYAnchor.constraint(equalTo: tableView.centerYAnchor)
        ])
    }

    @objc private func segmentChanged() {
        if let tab = ReportTab(rawValue: segmentedControl.selectedSegmentIndex) {
            currentTab = tab
            loadData()
        }
    }

    @objc private func selectYear() {
        let years = ["All", "2021", "2022", "2023", "2024", "2025"]
        let alert = UIAlertController(title: "Select Year", message: nil, preferredStyle: .actionSheet)
        years.forEach { y in
            alert.addAction(UIAlertAction(title: y, style: .default) { _ in
                self.currentYear = y
                self.yearButton.setTitle("Year: \(y) ▾", for: .normal)
                self.loadData()
            })
        }
        alert.addAction(UIAlertAction(title: "Cancel", style: .cancel))
        present(alert, animated: true)
    }

    private func loadData() {
        loadingIndicator.startAnimating()
        Task { [weak self] in
            guard let self = self else { return }
            do {
                switch self.currentTab {
                case .profit:
                    self.profitRows = try await NetworkManager.shared.getProfitReport(interval: .year, date: nil, month: nil, year: self.currentYear, day: nil)
                case .sales:
                    self.salesRows = try await NetworkManager.shared.getSalesReport(interval: .year, date: nil, month: nil, year: self.currentYear, day: nil)
                case .purchases:
                    self.purchaseRows = try await NetworkManager.shared.getPurchasesReport(interval: .year, date: nil, month: nil, year: self.currentYear, day: nil)
                }
                self.tableView.reloadData()
            } catch {
                self.showError(error)
            }
            self.loadingIndicator.stopAnimating()
        }
    }

    private func showError(_ error: Error) {
        let alert = UIAlertController(title: "Error", message: error.localizedDescription, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "OK", style: .default))
        present(alert, animated: true)
    }

    // MARK: UITableViewDataSource
    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        switch currentTab {
        case .profit: return profitRows.count + (profitRows.isEmpty ? 0 : 1)
        case .sales: return salesRows.count + (salesRows.isEmpty ? 0 : 1)
        case .purchases: return purchaseRows.count + (purchaseRows.isEmpty ? 0 : 1)
        }
    }

    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: "ReportCell") ?? UITableViewCell(style: .subtitle, reuseIdentifier: "ReportCell")
        cell.textLabel?.numberOfLines = 1
        cell.detailTextLabel?.numberOfLines = 2
        cell.accessoryType = .none
        switch currentTab {
        case .profit:
            if !profitRows.isEmpty && indexPath.row == profitRows.count {
                let totals = totalProfit()
                cell.textLabel?.text = "Total"
                var detail = "Purchase: $\(fmt(totals.purchase))   Profit: $\(fmt(totals.profit))"
                if let roi = totals.roiPercent { detail += "   ROI: \(fmt(roi))%" }
                cell.detailTextLabel?.text = detail
            } else {
                let r = profitRows[indexPath.row]
                cell.textLabel?.text = "\(r.date) (\(r.day))"
                var detail = "Purchase: $\(fmt(r.purchasePrice))   Profit: $\(fmt(r.profit))"
                if let roi = r.roiPercent { detail += "   ROI: \(fmt(roi))%" }
                cell.detailTextLabel?.text = detail
                cell.accessoryType = .disclosureIndicator
            }
        case .sales:
            if !salesRows.isEmpty && indexPath.row == salesRows.count {
                let t = totalSales()
                var s = "Sold: $\(fmt(t.sold))   Ship: $\(fmt(t.ship))"
                if let pct = t.shipPct { s += "   Ship %: \(fmt(pct))%" }
                s += "   Net: $\(fmt(t.net))"
                cell.textLabel?.text = "Total"
                cell.detailTextLabel?.text = s
            } else {
                let r = salesRows[indexPath.row]
                cell.textLabel?.text = "\(r.date) (\(r.day))"
                cell.detailTextLabel?.text = "Sold: $\(fmt(r.soldPrice))   Ship: $\(fmt(r.shippingFee))   Net: $\(fmt(r.net))   Items: \(r.totalItems)"
            }
        case .purchases:
            if !purchaseRows.isEmpty && indexPath.row == purchaseRows.count {
                let t = totalPurchases()
                var s = "Spent: $\(fmt(t.spent))   Days: \(t.days)"
                if let avg = t.avgPerDay { s += "   Avg/Day: $\(fmt(avg))" }
                cell.textLabel?.text = "Total"
                cell.detailTextLabel?.text = s
            } else {
                let r = purchaseRows[indexPath.row]
                cell.textLabel?.text = "\(r.date) (\(r.day))"
                cell.detailTextLabel?.text = "Spent: $\(fmt(r.price))"
            }
        }
        return cell
    }

    // Navigate to groups list for selected profit date
    func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        tableView.deselectRow(at: indexPath, animated: true)
        guard currentTab == .profit else { return }
        if profitRows.isEmpty { return }
        if indexPath.row >= profitRows.count { return } // totals row
        let date = profitRows[indexPath.row].date
        let groupsVC = GroupsViewController()
        navigationController?.pushViewController(groupsVC, animated: true)
        // Strongly-typed call to new helper
        groupsVC.loadGroupsForDate(date)
    }

    // MARK: Totals helpers
    private func fmt(_ v: Double) -> String { String(format: "%.2f", v) }
    private func totalSales() -> (sold: Double, ship: Double, net: Double, shipPct: Double?) {
        let sold = salesRows.reduce(0) { $0 + $1.soldPrice }
        let ship = salesRows.reduce(0) { $0 + $1.shippingFee }
        let net = salesRows.reduce(0) { $0 + $1.net }
        let pct = sold > 0 ? (ship / sold) * 100.0 : nil
        return (sold, ship, net, pct)
    }
    private func totalPurchases() -> (spent: Double, days: Int, avgPerDay: Double?) {
        let spent = purchaseRows.reduce(0) { $0 + $1.price }
        let days = purchaseRows.count
        let avg = days > 0 ? spent / Double(days) : nil
        return (spent, days, avg)
    }
    private func totalProfit() -> (purchase: Double, profit: Double, roiPercent: Double?) {
        let purchase = profitRows.reduce(0) { $0 + $1.purchasePrice }
        let profit = profitRows.reduce(0) { $0 + $1.profit }
        let roi = purchase > 0 ? (profit / purchase) * 100.0 : nil
        return (purchase, profit, roi)
    }
}


