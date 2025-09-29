import UIKit

enum ItemFilter: String, CaseIterable {
    case all = "All Items"
    case sold = "Sold Items"
    case unsold = "Unsold Items"
}

class ItemsViewController: UIViewController {
    
    private let tableView = UITableView()
    private let searchController = UISearchController(searchResultsController: nil)
    private let refreshControl = UIRefreshControl()
    private let loadingIndicator = UIActivityIndicatorView(style: .large)
    
    // Filter dropdown components
    private let filterLabel = UILabel()
    private let filterButton = UIButton(type: .system)
    private var currentFilter: ItemFilter = .all
    
    private var allItems: [ItemDetail] = []
    private var filteredItems: [ItemDetail] = []
    private var isSearching: Bool {
        return searchController.isActive && !searchBarIsEmpty
    }
    
    private var searchBarIsEmpty: Bool {
        return searchController.searchBar.text?.isEmpty ?? true
    }
    
    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        loadItems()
    }
    
    private func setupUI() {
        view.backgroundColor = .systemBackground
        title = "Manage Items"
        
        // Navigation bar setup
        navigationItem.largeTitleDisplayMode = .always
        navigationController?.navigationBar.prefersLargeTitles = true
        
        // Search controller setup
        searchController.searchResultsUpdater = self
        searchController.obscuresBackgroundDuringPresentation = false
        searchController.searchBar.placeholder = "Search items..."
        navigationItem.searchController = searchController
        definesPresentationContext = true
        
        // Table view setup
        tableView.translatesAutoresizingMaskIntoConstraints = false
        tableView.delegate = self
        tableView.dataSource = self
        tableView.register(UITableViewCell.self, forCellReuseIdentifier: "ItemCell")
        tableView.rowHeight = 80
        tableView.refreshControl = refreshControl
        refreshControl.addTarget(self, action: #selector(refreshItems), for: .valueChanged)
        
        // Filter components setup
        filterLabel.text = "Filter:"
        filterLabel.font = UIFont.systemFont(ofSize: 16, weight: .medium)
        filterLabel.translatesAutoresizingMaskIntoConstraints = false
        
        filterButton.setTitle(currentFilter.rawValue, for: .normal)
        filterButton.titleLabel?.font = UIFont.systemFont(ofSize: 16)
        filterButton.backgroundColor = .systemBlue
        filterButton.setTitleColor(.white, for: .normal)
        filterButton.layer.cornerRadius = 8
        filterButton.contentEdgeInsets = UIEdgeInsets(top: 8, left: 16, bottom: 8, right: 16)
        filterButton.translatesAutoresizingMaskIntoConstraints = false
        filterButton.addTarget(self, action: #selector(filterButtonTapped), for: .touchUpInside)
        
        // Loading indicator setup
        loadingIndicator.translatesAutoresizingMaskIntoConstraints = false
        loadingIndicator.hidesWhenStopped = true
        
        view.addSubview(filterLabel)
        view.addSubview(filterButton)
        view.addSubview(tableView)
        view.addSubview(loadingIndicator)
        
        setupConstraints()
    }
    
    private func setupConstraints() {
        NSLayoutConstraint.activate([
            // Filter components
            filterLabel.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor, constant: 16),
            filterLabel.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 16),
            
            filterButton.centerYAnchor.constraint(equalTo: filterLabel.centerYAnchor),
            filterButton.leadingAnchor.constraint(equalTo: filterLabel.trailingAnchor, constant: 12),
            filterButton.trailingAnchor.constraint(lessThanOrEqualTo: view.trailingAnchor, constant: -16),
            
            // Table view
            tableView.topAnchor.constraint(equalTo: filterButton.bottomAnchor, constant: 16),
            tableView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            tableView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            tableView.bottomAnchor.constraint(equalTo: view.bottomAnchor),
            
            // Loading indicator
            loadingIndicator.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            loadingIndicator.centerYAnchor.constraint(equalTo: view.centerYAnchor)
        ])
    }
    
    @objc private func refreshItems() {
        loadItems()
    }
    
    @objc private func filterButtonTapped() {
        let alertController = UIAlertController(title: "Filter Items", message: "Choose filter option", preferredStyle: .actionSheet)
        
        for filter in ItemFilter.allCases {
            let action = UIAlertAction(title: filter.rawValue, style: .default) { _ in
                self.currentFilter = filter
                self.filterButton.setTitle(filter.rawValue, for: .normal)
                self.applyFilters()
            }
            
            // Mark current selection
            if filter == currentFilter {
                action.setValue(true, forKey: "checked")
            }
            
            alertController.addAction(action)
        }
        
        alertController.addAction(UIAlertAction(title: "Cancel", style: .cancel))
        
        // For iPad support
        if let popover = alertController.popoverPresentationController {
            popover.sourceView = filterButton
            popover.sourceRect = filterButton.bounds
        }
        
        present(alertController, animated: true)
    }
    
    private func loadItems() {
        if !refreshControl.isRefreshing {
            loadingIndicator.startAnimating()
        }
        
        Task {
            do {
                let items = try await NetworkManager.shared.getAllItems()
                await MainActor.run {
                    self.allItems = items
                    self.applyFilters()
                    self.loadingIndicator.stopAnimating()
                    self.refreshControl.endRefreshing()
                }
            } catch {
                await MainActor.run {
                    self.loadingIndicator.stopAnimating()
                    self.refreshControl.endRefreshing()
                    self.showAlert(title: "Error", message: "Failed to load items. Please try again.")
                }
            }
        }
    }
    
    private func applyFilters() {
        
        // Debug: Print all items and their sold status
        for (index, item) in allItems.enumerated() {
        }
        
        // First apply status filter
        var statusFilteredItems: [ItemDetail]
        
        switch currentFilter {
        case .all:
            statusFilteredItems = allItems
        case .sold:
            statusFilteredItems = allItems.filter { $0.sold }
        case .unsold:
            statusFilteredItems = allItems.filter { !$0.sold }
        }
        
        // Then apply search filter if there's search text
        let searchText = searchController.searchBar.text ?? ""
        if searchText.isEmpty {
            filteredItems = statusFilteredItems
        } else {
            filteredItems = statusFilteredItems.filter { item in
                item.name.lowercased().contains(searchText.lowercased()) ||
                item.category.lowercased().contains(searchText.lowercased()) ||
                (item.storage?.lowercased().contains(searchText.lowercased()) ?? false)
            }
        }
        
        tableView.reloadData()
    }
    
    private func filterContentForSearchText(_ searchText: String) {
        // Use the new unified filtering method
        applyFilters()
    }
    
    private func showAlert(title: String, message: String) {
        let alert = UIAlertController(title: title, message: message, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "OK", style: .default))
        present(alert, animated: true)
    }
    
    private func presentItemDetailAlert(_ item: ItemDetail) {
        var message = "Category: \(item.category)\n"
        message += "Storage: \(item.storage ?? "Unknown")\n"
        message += "List Price: $\(item.price)\n"
        message += "Status: \(item.sold ? "Sold" : "Available")\n"
        
        if item.sold {
            if let soldPrice = item.soldPrice {
                message += "Sold Price: $\(soldPrice)\n"
            }
            if let shippingFee = item.shippingFee {
                message += "Shipping Fee: $\(shippingFee)\n"
            }
            if let netPrice = item.netPrice {
                message += "Net: $\(netPrice)\n"
            }
            if let soldDate = item.soldDate {
                message += "Sold Date: \(soldDate)\n"
            }
            if let daysToSell = item.daysToSell {
                message += "Days to Sell: \(daysToSell)\n"
            }
        }
        
        let alert = UIAlertController(title: item.name, message: message, preferredStyle: .alert)
        
        if !item.sold {
            alert.addAction(UIAlertAction(title: "Sell...", style: .default) { _ in
                let vc = SellItemViewController(itemId: item.id, itemName: item.name, groupId: item.groupId)
                self.navigationController?.pushViewController(vc, animated: true)
            })
            alert.addAction(UIAlertAction(title: "Remove Item", style: .destructive) { _ in
                self.confirmRemoveItem(item)
            })
        }
        
        alert.addAction(UIAlertAction(title: "Close", style: .cancel))
        present(alert, animated: true)
    }

    private func promptMarkAsSold(_ item: ItemDetail) {
        let alert = UIAlertController(title: "Mark as Sold", message: "Enter sale details", preferredStyle: .alert)
        alert.addTextField { tf in
            tf.placeholder = "Sale Date (YYYY-MM-DD)"
            tf.text = self.todayString()
            tf.keyboardType = .numbersAndPunctuation
        }
        alert.addTextField { tf in
            tf.placeholder = "Sold Price (e.g., 25.00)"
            tf.keyboardType = .decimalPad
        }
        alert.addTextField { tf in
            tf.placeholder = "Shipping Fee (e.g., 3.50)"
            tf.keyboardType = .decimalPad
        }
        alert.addAction(UIAlertAction(title: "Cancel", style: .cancel))
        alert.addAction(UIAlertAction(title: "Save", style: .default) { _ in
            let date = alert.textFields?[0].text?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
            let price = alert.textFields?[1].text?.trimmingCharacters(in: .whitespacesAndNewlines) ?? "0"
            let shipping = alert.textFields?[2].text?.trimmingCharacters(in: .whitespacesAndNewlines) ?? "0"
            self.markAsSold(item: item, soldDate: date, price: price, shippingFee: shipping)
        })
        present(alert, animated: true)
    }

    private func todayString() -> String {
        let df = DateFormatter()
        df.dateFormat = "yyyy-MM-dd"
        return df.string(from: Date())
    }

    private func markAsSold(item: ItemDetail, soldDate: String, price: String, shippingFee: String) {
        loadingIndicator.startAnimating()
        Task {
            do {
                try await NetworkManager.shared.markItemSold(itemId: item.id, soldDate: soldDate, price: price, shippingFee: shippingFee)
                await MainActor.run {
                    self.loadingIndicator.stopAnimating()
                    // Update local state: mark item as sold
                    if let idx = self.allItems.firstIndex(where: { $0.id == item.id }) {
                        var updated = self.allItems[idx]
                        updated = ItemDetail(
                            id: updated.id,
                            name: updated.name,
                            sold: true,
                            groupId: updated.groupId,
                            categoryId: updated.categoryId,
                            category: updated.category,
                            returned: updated.returned,
                            storage: updated.storage,
                            listDate: updated.listDate,
                            groupName: updated.groupName,
                            purchaseDate: updated.purchaseDate,
                            price: updated.price,
                            soldPrice: Double(price),
                            shippingFee: Double(shippingFee),
                            netPrice: nil,
                            soldDate: soldDate,
                            daysToSell: updated.daysToSell
                        )
                        self.allItems[idx] = updated
                    }
                    self.applyFilters()
                    self.showAlert(title: "Success", message: "Item marked as sold.")
                }
            } catch {
                await MainActor.run {
                    self.loadingIndicator.stopAnimating()
                    self.showAlert(title: "Error", message: "Failed to mark item sold. Please try again.")
                }
            }
        }
    }
    
    private func confirmRemoveItem(_ item: ItemDetail) {
        let alert = UIAlertController(
            title: "Remove Item",
            message: "Are you sure you want to remove '\(item.name)'?",
            preferredStyle: .alert
        )
        
        alert.addAction(UIAlertAction(title: "Cancel", style: .cancel))
        alert.addAction(UIAlertAction(title: "Remove", style: .destructive) { _ in
            self.removeItem(item)
        })
        
        present(alert, animated: true)
    }
    
    private func removeItem(_ item: ItemDetail) {
        loadingIndicator.startAnimating()
        
        Task {
            do {
                try await NetworkManager.shared.removeItem(itemId: item.id)
                await MainActor.run {
                    self.loadingIndicator.stopAnimating()
                    // Remove from local arrays
                    self.allItems.removeAll { $0.id == item.id }
                    self.filterContentForSearchText(self.searchController.searchBar.text ?? "")
                    self.showAlert(title: "Success", message: "Item removed successfully.")
                }
            } catch {
                await MainActor.run {
                    self.loadingIndicator.stopAnimating()
                    self.showAlert(title: "Error", message: "Failed to remove item. Please try again.")
                }
            }
        }
    }
}

// MARK: - UITableViewDataSource

extension ItemsViewController: UITableViewDataSource {
    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        let count = filteredItems.count
        
        if count == 0 && !loadingIndicator.isAnimating {
            let message = isSearching ? "No items match your search" : "No items found"
            tableView.setEmptyMessage(message)
        } else {
            tableView.restore()
        }
        
        return count
    }
    
    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: "ItemCell", for: indexPath)
        let item = filteredItems[indexPath.row]
        
        // Configure cell
        cell.textLabel?.text = item.name
        cell.textLabel?.font = UIFont.systemFont(ofSize: 16, weight: .medium)
        
        var detailText = "\(item.category) • $\(item.price)"
        if item.sold {
            detailText += " • SOLD"
            if let soldPrice = item.soldPrice {
                detailText += " for $\(soldPrice)"
            }
        }
        cell.detailTextLabel?.text = detailText
        cell.detailTextLabel?.font = UIFont.systemFont(ofSize: 14)
        cell.detailTextLabel?.textColor = .secondaryLabel
        
        // Status indicator
        let statusView = UIView()
        statusView.translatesAutoresizingMaskIntoConstraints = false
        statusView.layer.cornerRadius = 4
        statusView.backgroundColor = item.sold ? .systemGreen : .systemBlue
        
        cell.contentView.addSubview(statusView)
        NSLayoutConstraint.activate([
            statusView.trailingAnchor.constraint(equalTo: cell.contentView.trailingAnchor, constant: -16),
            statusView.centerYAnchor.constraint(equalTo: cell.contentView.centerYAnchor),
            statusView.widthAnchor.constraint(equalToConstant: 8),
            statusView.heightAnchor.constraint(equalToConstant: 8)
        ])
        
        cell.accessoryType = .disclosureIndicator
        return cell
    }
}

// MARK: - UITableViewDelegate

extension ItemsViewController: UITableViewDelegate {
    func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        tableView.deselectRow(at: indexPath, animated: true)
        let item = filteredItems[indexPath.row]
        presentItemDetailAlert(item)
    }
}

// MARK: - UISearchResultsUpdating

extension ItemsViewController: UISearchResultsUpdating {
    func updateSearchResults(for searchController: UISearchController) {
        filterContentForSearchText(searchController.searchBar.text ?? "")
    }
}

// MARK: - UITableView Empty State

extension UITableView {
    func setEmptyMessage(_ message: String) {
        let messageLabel = UILabel(frame: CGRect(x: 0, y: 0, width: self.bounds.size.width, height: self.bounds.size.height))
        messageLabel.text = message
        messageLabel.textColor = .secondaryLabel
        messageLabel.numberOfLines = 0
        messageLabel.textAlignment = .center
        messageLabel.font = UIFont.systemFont(ofSize: 16)
        messageLabel.sizeToFit()
        
        self.backgroundView = messageLabel
        self.separatorStyle = .none
    }
    
    func restore() {
        self.backgroundView = nil
        self.separatorStyle = .singleLine
    }
} 