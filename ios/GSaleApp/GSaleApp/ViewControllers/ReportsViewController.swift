import UIKit

private enum ReportTab: Int { case profit = 0, sales = 1, purchases = 2, city = 3 }

class ReportsViewController: UIViewController, UITableViewDataSource, UITableViewDelegate {

    private let segmentedControl = UISegmentedControl(items: ["Profit", "Sales", "Purchases", "Location"])
    private let yearButton = UIButton(type: .system)
    private let cityButton = UIButton(type: .system)
    private let tableView = UITableView(frame: .zero, style: .plain)
    private let loadingIndicator = UIActivityIndicatorView(style: .large)

    private var currentTab: ReportTab = .profit
    private var currentYear: String = String(Calendar.current.component(.year, from: Date()))

    private var profitRows: [ProfitReportRow] = []
    private var salesRows: [SalesReportRow] = []
    private var purchaseRows: [PurchasesReportRow] = []
    private var cityOptions: [CityOption] = []
    private var cityPurchases: [CityPurchaseRow] = []
    private var citySummary: CitySummary?
    private var selectedCityName: String?
    private var stateOptions: [String] = []
    private var selectedState: String?

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

        cityButton.setTitle("Select Location ▾", for: .normal)
        cityButton.addTarget(self, action: #selector(openCityReport), for: .touchUpInside)
        cityButton.translatesAutoresizingMaskIntoConstraints = false
        cityButton.isHidden = true

        tableView.dataSource = self
        tableView.delegate = self
        tableView.translatesAutoresizingMaskIntoConstraints = false

        loadingIndicator.hidesWhenStopped = true
        loadingIndicator.translatesAutoresizingMaskIntoConstraints = false

        view.addSubview(segmentedControl)
        view.addSubview(yearButton)
        view.addSubview(cityButton)
        view.addSubview(tableView)
        view.addSubview(loadingIndicator)

        NSLayoutConstraint.activate([
            segmentedControl.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor, constant: 8),
            segmentedControl.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 12),
            segmentedControl.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -12),

            yearButton.topAnchor.constraint(equalTo: segmentedControl.bottomAnchor, constant: 8),
            yearButton.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 12),

            cityButton.centerYAnchor.constraint(equalTo: yearButton.centerYAnchor),
            cityButton.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -12),

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
            cityButton.isHidden = (tab != .city)
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

    @objc private func openCityReport() {
        loadingIndicator.startAnimating()
        Task { [weak self] in
            guard let self = self else { return }
            do {
                // Try new API first
                self.stateOptions = try await NetworkManager.shared.getStatesFromAPI()
                if !self.stateOptions.isEmpty {
                    self.presentStatePicker()
                } else {
                    // Fallback to legacy HTML city-only
                    self.cityOptions = try await NetworkManager.shared.getCityOptions()
                    if self.cityOptions.isEmpty {
                        self.showError(NSError(domain: "City", code: -1, userInfo: [NSLocalizedDescriptionKey: "No cities found."]))
                    } else {
                        self.presentCityPicker()
                    }
                }
            } catch {
                self.showError(error)
            }
            self.loadingIndicator.stopAnimating()
        }
    }

    private func presentStatePicker() {
        let alert = UIAlertController(title: "Select State", message: nil, preferredStyle: .actionSheet)
        for st in stateOptions {
            alert.addAction(UIAlertAction(title: st, style: .default) { _ in
                self.selectedState = st
                Task { [weak self] in
                    guard let self = self else { return }
                    do {
                        let cities = try await NetworkManager.shared.getCitiesForStateFromAPI(state: st)
                        if cities.isEmpty {
                            self.showError(NSError(domain: "City", code: -2, userInfo: [NSLocalizedDescriptionKey: "No cities returned for \(st)."]))
                        } else {
                            self.cityOptions = cities.map { CityOption(name: $0, label: $0) }
                            self.presentCityPicker()
                        }
                    } catch {
                        self.showError(error)
                    }
                }
            })
        }
        alert.addAction(UIAlertAction(title: "Cancel", style: .cancel))
        present(alert, animated: true)
    }

    private func presentCityPicker() {
        let alert = UIAlertController(title: "Select Location", message: selectedState != nil ? "State: \(selectedState!)" : nil, preferredStyle: .actionSheet)
        for opt in cityOptions {
            alert.addAction(UIAlertAction(title: opt.label, style: .default) { _ in
                Task { [weak self] in
                    guard let self = self else { return }
                    self.selectedCityName = opt.name
                    self.cityButton.setTitle("\(opt.name) ▾", for: .normal)
                    do {
                        try await self.loadCityIfNeeded()
                        self.tableView.reloadData()
                    } catch {
                        self.showError(error)
                    }
                }
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
                case .city:
                    try await self.loadCityIfNeeded()
                }
                self.tableView.reloadData()
            } catch {
                self.showError(error)
            }
            self.loadingIndicator.stopAnimating()
        }
    }

    @discardableResult
    private func loadCityIfNeeded() async throws -> Void {
        if selectedCityName == nil {
            if cityOptions.isEmpty {
                // If we have state options, load first state's cities; else fallback to legacy cities list
                if !stateOptions.isEmpty {
                    selectedState = stateOptions.first
                    let cities = try await NetworkManager.shared.getCitiesForStateFromAPI(state: selectedState!)
                    self.cityOptions = cities.map { CityOption(name: $0, label: $0) }
                } else {
                    self.cityOptions = try await NetworkManager.shared.getCityOptions()
                }
            }
            selectedCityName = cityOptions.first?.name
            if let name = selectedCityName {
                self.cityButton.setTitle("\(name) ▾", for: .normal)
            }
        }
        if let name = selectedCityName {
            let result = try await NetworkManager.shared.getCityReport(city: name, state: selectedState)
            self.citySummary = result.summary
            self.cityPurchases = result.purchases
        }
    }

    private func showError(_ error: Error) {
        let alert = UIAlertController(title: "Error", message: (error as NSError).localizedDescription, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "OK", style: .default))
        present(alert, animated: true)
    }

    // MARK: UITableViewDataSource
    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        switch currentTab {
        case .profit: return profitRows.count + (profitRows.isEmpty ? 0 : 1)
        case .sales: return salesRows.count + (salesRows.isEmpty ? 0 : 1)
        case .purchases: return purchaseRows.count + (purchaseRows.isEmpty ? 0 : 1)
        case .city: return cityPurchases.count + (cityPurchases.isEmpty ? 0 : 1)
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
        case .city:
            if !cityPurchases.isEmpty && indexPath.row == cityPurchases.count {
                if let s = citySummary {
                    var detail = "Purchases: \(s.totalPurchases)  Items: \(s.totalItems)  Sold: \(s.soldItems)"
                    detail += "\nSpent: $\(fmt(s.totalSpent))  Sales: $\(fmt(s.totalSales))  Profit: $\(fmt(s.totalProfit))"
                    cell.textLabel?.text = "Summary"
                    cell.detailTextLabel?.text = detail
                } else {
                    cell.textLabel?.text = "Summary"
                    cell.detailTextLabel?.text = "No summary"
                }
            } else {
                if indexPath.row < cityPurchases.count {
                    let r = cityPurchases[indexPath.row]
                    cell.textLabel?.text = "\(r.date) - \(r.name)"
                    cell.detailTextLabel?.text = "Purchase: $\(fmt(r.purchasePrice))  Items: \(r.itemCount)  Sold: \(r.soldCount)\nSales: $\(fmt(r.totalSales))  Profit: $\(fmt(r.profit))"
                }
            }
        }
        return cell
    }

    // Header for City tab to show extra data label at the top of the list
    func tableView(_ tableView: UITableView, viewForHeaderInSection section: Int) -> UIView? {
        guard currentTab == .city else { return nil }
        let header = UIView()
        header.backgroundColor = .secondarySystemBackground
        let label = UILabel()
        label.text = "Group Name"
        label.font = UIFont.systemFont(ofSize: 14, weight: .semibold)
        label.translatesAutoresizingMaskIntoConstraints = false
        header.addSubview(label)
        NSLayoutConstraint.activate([
            label.topAnchor.constraint(equalTo: header.topAnchor, constant: 6),
            label.bottomAnchor.constraint(equalTo: header.bottomAnchor, constant: -6),
            label.leadingAnchor.constraint(equalTo: header.leadingAnchor, constant: 12),
            label.trailingAnchor.constraint(lessThanOrEqualTo: header.trailingAnchor, constant: -12)
        ])
        return header
    }

    func tableView(_ tableView: UITableView, heightForHeaderInSection section: Int) -> CGFloat {
        return currentTab == .city ? 28 : 0.01
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


