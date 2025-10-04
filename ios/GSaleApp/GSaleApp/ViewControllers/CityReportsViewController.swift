import UIKit

class CityReportsViewController: UIViewController, UITableViewDataSource, UITableViewDelegate {

    private let picker = UIPickerView()
    private let summaryLabel = UILabel()
    private let tableView = UITableView(frame: .zero, style: .plain)
    private let loadingIndicator = UIActivityIndicatorView(style: .large)

    private var cityOptions: [CityOption] = []
    private var selectedCityName: String?
    private var purchases: [CityPurchaseRow] = []
    private var summary: CitySummary?

    override func viewDidLoad() {
        super.viewDidLoad()
        title = "City Report"
        view.backgroundColor = .systemBackground
        setupUI()
        loadCityOptions()
    }

    private func setupUI() {
        picker.dataSource = self
        picker.delegate = self
        picker.translatesAutoresizingMaskIntoConstraints = false

        summaryLabel.numberOfLines = 0
        summaryLabel.font = UIFont.systemFont(ofSize: 14)
        summaryLabel.translatesAutoresizingMaskIntoConstraints = false

        tableView.dataSource = self
        tableView.delegate = self
        tableView.translatesAutoresizingMaskIntoConstraints = false

        loadingIndicator.hidesWhenStopped = true
        loadingIndicator.translatesAutoresizingMaskIntoConstraints = false

        view.addSubview(picker)
        view.addSubview(summaryLabel)
        view.addSubview(tableView)
        view.addSubview(loadingIndicator)

        NSLayoutConstraint.activate([
            picker.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor, constant: 8),
            picker.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            picker.trailingAnchor.constraint(equalTo: view.trailingAnchor),

            summaryLabel.topAnchor.constraint(equalTo: picker.bottomAnchor, constant: 8),
            summaryLabel.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 12),
            summaryLabel.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -12),

            tableView.topAnchor.constraint(equalTo: summaryLabel.bottomAnchor, constant: 8),
            tableView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            tableView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            tableView.bottomAnchor.constraint(equalTo: view.bottomAnchor),

            loadingIndicator.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            loadingIndicator.centerYAnchor.constraint(equalTo: view.centerYAnchor)
        ])
    }

    private func loadCityOptions() {
        loadingIndicator.startAnimating()
        Task { [weak self] in
            guard let self = self else { return }
            do {
                self.cityOptions = try await NetworkManager.shared.getCityOptions()
                self.picker.reloadAllComponents()
                if let first = self.cityOptions.first {
                    self.selectedCityName = first.name
                    self.picker.selectRow(0, inComponent: 0, animated: false)
                    await self.loadCityReport(city: first.name)
                }
            } catch {
                self.showError(error)
            }
            self.loadingIndicator.stopAnimating()
        }
    }

    private func loadCityReport(city: String) async {
        loadingIndicator.startAnimating()
        do {
            let result = try await NetworkManager.shared.getCityReport(city: city)
            self.summary = result.summary
            self.purchases = result.purchases
            updateSummary()
            self.tableView.reloadData()
        } catch {
            self.showError(error)
        }
        self.loadingIndicator.stopAnimating()
    }

    private func updateSummary() {
        guard let s = summary else { summaryLabel.text = ""; return }
        var lines: [String] = []
        lines.append("Purchases: \(s.totalPurchases) | Items: \(s.totalItems) | Sold: \(s.soldItems)")
        lines.append("Spent: $\(fmt(s.totalSpent)) | Sales: $\(fmt(s.totalSales)) | Profit: $\(fmt(s.totalProfit))")
        if let first = s.firstPurchase, let last = s.lastPurchase {
            lines.append("From \(first) to \(last)")
        }
        summaryLabel.text = lines.joined(separator: "\n")
    }

    private func showError(_ error: Error) {
        let alert = UIAlertController(title: "Error", message: error.localizedDescription, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "OK", style: .default))
        present(alert, animated: true)
    }

    private func fmt(_ v: Double) -> String { String(format: "%.2f", v) }

    // MARK: UITableViewDataSource
    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return purchases.count
    }
    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: "CityCell") ?? UITableViewCell(style: .subtitle, reuseIdentifier: "CityCell")
        cell.textLabel?.numberOfLines = 1
        cell.detailTextLabel?.numberOfLines = 2
        let r = purchases[indexPath.row]
        cell.textLabel?.text = "\(r.date) - \(r.name)"
        let loc = r.locationName ?? r.locationAddress ?? ""
        cell.detailTextLabel?.text = "Purchase: $\(fmt(r.purchasePrice))  Items: \(r.itemCount)  Sold: \(r.soldCount)\nSales: $\(fmt(r.totalSales))  Profit: $\(fmt(r.profit))  \(loc)"
        return cell
    }
}

extension CityReportsViewController: UIPickerViewDataSource, UIPickerViewDelegate {
    func numberOfComponents(in pickerView: UIPickerView) -> Int { 1 }
    func pickerView(_ pickerView: UIPickerView, numberOfRowsInComponent component: Int) -> Int {
        return cityOptions.count
    }
    func pickerView(_ pickerView: UIPickerView, titleForRow row: Int, forComponent component: Int) -> String? {
        return cityOptions[row].label
    }
    func pickerView(_ pickerView: UIPickerView, didSelectRow row: Int, inComponent component: Int) {
        let city = cityOptions[row].name
        selectedCityName = city
        Task { await self.loadCityReport(city: city) }
    }
}


