import UIKit

extension Notification.Name {
    static let groupCreated = Notification.Name("groupCreated")
    static let groupDeleted = Notification.Name("groupDeleted")
}

class GroupsViewController: UIViewController {
    
    private let tableView = UITableView()
    private let addButton = UIBarButtonItem(barButtonSystemItem: .add, target: nil, action: nil)
    private let searchButton = UIBarButtonItem(barButtonSystemItem: .search, target: nil, action: nil)
    private let refreshControl = UIRefreshControl()
    private let activityIndicator = UIActivityIndicatorView(style: .large)
    private let yearPickerView = UIPickerView()
    private let yearSelectionView = UIView()
    private let yearLabel = UILabel()
    private let yearButton = UIButton(type: .system)
    
    private var groups: [Group] = []
    private var allGroups: [Group] = [] // Store all groups for search functionality
    private var isLoading = false
    private var isSearching = false
    private var currentSearchTerm = ""
    
    // Year filtering
    private let availableYears: [String] = {
        let currentYear = Calendar.current.component(.year, from: Date())
        var years = ["All"]
        // Add years from 2021 to current year + 1
        for year in 2021...(currentYear + 1) {
            years.append(String(year))
        }
        return years
    }()
    private var selectedYear: String = {
        let currentYear = Calendar.current.component(.year, from: Date())
        return String(currentYear)
    }()
    
    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        loadGroupsForYear(selectedYear)
        
        // Listen for group creation and deletion notifications
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(groupCreated),
            name: .groupCreated,
            object: nil
        )
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(groupDeleted),
            name: .groupDeleted,
            object: nil
        )
    }
    
    deinit {
        NotificationCenter.default.removeObserver(self)
    }
    
    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        if !isSearching {
            loadGroupsForYear(selectedYear)
        }
    }
    
    private func setupUI() {
        view.backgroundColor = .systemBackground
        title = selectedYear == "All" ? "Groups" : "Groups (\(selectedYear))"
        
        navigationItem.rightBarButtonItems = [addButton, searchButton]
        addButton.target = self
        addButton.action = #selector(addGroupTapped)
        searchButton.target = self
        searchButton.action = #selector(searchGroupTapped)
        
        tableView.delegate = self
        tableView.dataSource = self
        tableView.register(UITableViewCell.self, forCellReuseIdentifier: "GroupCell")
        tableView.translatesAutoresizingMaskIntoConstraints = false
        
        refreshControl.addTarget(self, action: #selector(refreshData), for: .valueChanged)
        tableView.refreshControl = refreshControl
        
        activityIndicator.hidesWhenStopped = true
        activityIndicator.translatesAutoresizingMaskIntoConstraints = false
        
        // Setup year selection view
        setupYearSelectionView()
        
        view.addSubview(yearSelectionView)
        view.addSubview(tableView)
        view.addSubview(activityIndicator)
        
        NSLayoutConstraint.activate([
            yearSelectionView.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor),
            yearSelectionView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            yearSelectionView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            yearSelectionView.heightAnchor.constraint(equalToConstant: 60),
            
            tableView.topAnchor.constraint(equalTo: yearSelectionView.bottomAnchor),
            tableView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            tableView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            tableView.bottomAnchor.constraint(equalTo: view.bottomAnchor),
            
            activityIndicator.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            activityIndicator.centerYAnchor.constraint(equalTo: view.centerYAnchor)
        ])
    }
    
    private func setupYearSelectionView() {
        yearSelectionView.backgroundColor = .systemBackground
        yearSelectionView.translatesAutoresizingMaskIntoConstraints = false
        
        // Setup year label
        yearLabel.text = "Year:"
        yearLabel.font = UIFont.systemFont(ofSize: 16, weight: .medium)
        yearLabel.translatesAutoresizingMaskIntoConstraints = false
        
        // Setup year button
        yearButton.setTitle(selectedYear, for: .normal)
        yearButton.setTitleColor(.systemBlue, for: .normal)
        yearButton.backgroundColor = .systemGray6
        yearButton.layer.cornerRadius = 8
        yearButton.contentEdgeInsets = UIEdgeInsets(top: 8, left: 16, bottom: 8, right: 16)
        yearButton.translatesAutoresizingMaskIntoConstraints = false
        yearButton.addTarget(self, action: #selector(yearButtonTapped), for: .touchUpInside)
        
        yearSelectionView.addSubview(yearLabel)
        yearSelectionView.addSubview(yearButton)
        
        NSLayoutConstraint.activate([
            yearLabel.leadingAnchor.constraint(equalTo: yearSelectionView.leadingAnchor, constant: 16),
            yearLabel.centerYAnchor.constraint(equalTo: yearSelectionView.centerYAnchor),
            
            yearButton.leadingAnchor.constraint(equalTo: yearLabel.trailingAnchor, constant: 12),
            yearButton.centerYAnchor.constraint(equalTo: yearSelectionView.centerYAnchor),
            yearButton.trailingAnchor.constraint(lessThanOrEqualTo: yearSelectionView.trailingAnchor, constant: -16)
        ])
    }
    
    @objc private func addGroupTapped() {
        let addGroupVC = AddGroupViewController()
        let navController = UINavigationController(rootViewController: addGroupVC)
        present(navController, animated: true)
    }
    
    @objc private func searchGroupTapped() {
        let searchAlert = UIAlertController(
            title: "Search Groups",
            message: "Enter group name to search for:",
            preferredStyle: .alert
        )
        
        searchAlert.addTextField { textField in
            textField.placeholder = "Group name"
            textField.autocapitalizationType = .none
            textField.autocorrectionType = .no
        }
        
        searchAlert.addAction(UIAlertAction(title: "Cancel", style: .cancel))
        
        searchAlert.addAction(UIAlertAction(title: "Search", style: .default) { _ in
            guard let searchTerm = searchAlert.textFields?.first?.text,
                  !searchTerm.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
                self.showAlert(title: "Error", message: "Please enter a search term")
                return
            }
            
            self.performSearch(searchTerm: searchTerm.trimmingCharacters(in: .whitespacesAndNewlines))
        })
        
        present(searchAlert, animated: true)
    }
    
    @objc private func yearButtonTapped() {
        let yearAlert = UIAlertController(
            title: "Select Year",
            message: "Choose a year to filter groups:",
            preferredStyle: .actionSheet
        )
        
        for year in availableYears {
            let action = UIAlertAction(title: year, style: .default) { _ in
                self.selectedYear = year
                self.yearButton.setTitle(year, for: .normal)
                self.loadGroupsForYear(year)
            }
            
            // Mark current selection
            if year == selectedYear {
                action.setValue(true, forKey: "checked")
            }
            
            yearAlert.addAction(action)
        }
        
        yearAlert.addAction(UIAlertAction(title: "Cancel", style: .cancel))
        
        // For iPad support
        if let popover = yearAlert.popoverPresentationController {
            popover.sourceView = yearButton
            popover.sourceRect = yearButton.bounds
        }
        
        present(yearAlert, animated: true)
    }
    
    private func performSearch(searchTerm: String) {
        guard !isLoading else { return }
        
        isLoading = true
        isSearching = true
        currentSearchTerm = searchTerm
        activityIndicator.startAnimating()
        
        // Update title to show we're searching
        title = "Searching..."
        
        Task {
            do {
                let searchResults = try await NetworkManager.shared.searchGroups(searchTerm: searchTerm)
                
                await MainActor.run {
                    self.groups = searchResults
                    self.tableView.reloadData()
                    self.isLoading = false
                    self.activityIndicator.stopAnimating()
                    
                    // Update title to show search results
                    self.title = "Search: \"\(searchTerm)\" (\(searchResults.count))"
                    
                    // Add "Show All" button to clear search
                    self.addShowAllButton()
                    
                    print("✅ Search completed: found \(searchResults.count) groups")
                }
            } catch {
                await MainActor.run {
                    self.isLoading = false
                    self.isSearching = false
                    self.currentSearchTerm = ""
                    self.activityIndicator.stopAnimating()
                    self.title = "Groups"
                    
                    let errorMessage: String
                    switch error {
                    case NetworkError.unauthorized:
                        errorMessage = "Please log in again to search groups."
                    case NetworkError.serverError(let message):
                        errorMessage = "Search failed: \(message)"
                    default:
                        errorMessage = "Failed to search groups. Please try again."
                    }
                    
                    self.showAlert(title: "Search Failed", message: errorMessage)
                }
            }
        }
    }
    
    private func addShowAllButton() {
        let showAllButton = UIBarButtonItem(title: "Show All", style: .plain, target: self, action: #selector(showAllGroups))
        navigationItem.leftBarButtonItem = showAllButton
    }
    
    @objc private func showAllGroups() {
        isSearching = false
        currentSearchTerm = ""
        title = selectedYear == "All" ? "Groups" : "Groups (\(selectedYear))"
        navigationItem.leftBarButtonItem = nil
        
        // Restore all groups or reload from server
        if !allGroups.isEmpty {
            groups = allGroups
            tableView.reloadData()
        } else {
            loadGroupsForYear(selectedYear)
        }
    }
    
    @objc private func refreshData() {
        if isSearching {
            loadGroups() // Use default loadGroups for search state
        } else {
            loadGroupsForYear(selectedYear) // Use year filtering for normal state
        }
    }
    
    @objc private func groupCreated() {
        print("📢 Received group created notification - refreshing groups list")
        if isSearching {
            loadGroups()
        } else {
            loadGroupsForYear(selectedYear)
        }
    }
    
    @objc private func groupDeleted() {
        print("📢 Received group deleted notification - refreshing groups list")
        if isSearching {
            loadGroups()
        } else {
            loadGroupsForYear(selectedYear)
        }
    }
    
    private func loadGroupsForYear(_ year: String) {
        guard !isLoading else { return }
        
        isLoading = true
        print("📅 Loading groups for year: \(year)")
        activityIndicator.startAnimating()
        
        Task {
            do {
                let fetchedGroups = try await NetworkManager.shared.getGroupsByYear(year)
                
                await MainActor.run {
                    self.allGroups = fetchedGroups // Store all groups
                    
                    // Only update displayed groups if we're not currently searching
                    if !self.isSearching {
                        self.groups = fetchedGroups
                        self.title = year == "All" ? "Groups" : "Groups (\(year))"
                        self.navigationItem.leftBarButtonItem = nil
                    }
                    
                    print("✅ Loaded \(fetchedGroups.count) groups for year \(year)")
                    self.tableView.reloadData()
                    self.refreshControl.endRefreshing()
                    self.activityIndicator.stopAnimating()
                    self.isLoading = false
                    
                    if fetchedGroups.isEmpty && !self.isSearching {
                        self.showAlert(title: "No Groups", message: "No groups found for \(year). Try selecting a different year or create your first group!")
                    }
                }
            } catch {
                await MainActor.run {
                    print("❌ Failed to load groups for year \(year): \(error)")
                    self.refreshControl.endRefreshing()
                    self.activityIndicator.stopAnimating()
                    self.isLoading = false
                    self.showAlert(title: "Error", message: "Failed to load groups for \(year). Please try again.")
                }
            }
        }
    }
    
    private func loadGroups() {
        guard !isLoading else { return }
        
        isLoading = true
        print("🔄 Loading groups...")
        activityIndicator.startAnimating()
        
        Task {
            do {
                let fetchedGroups = try await NetworkManager.shared.getGroups()
                
                await MainActor.run {
                    self.allGroups = fetchedGroups // Store all groups
                    
                    // Only update displayed groups if we're not currently searching
                    if !self.isSearching {
                        self.groups = fetchedGroups
                        self.title = "Groups"
                        self.navigationItem.leftBarButtonItem = nil
                    }
                    
                    print("✅ Loaded \(fetchedGroups.count) groups")
                    self.tableView.reloadData()
                    self.refreshControl.endRefreshing()
                    self.activityIndicator.stopAnimating()
                    self.isLoading = false
                    
                    if fetchedGroups.isEmpty && !self.isSearching {
                        self.showAlert(title: "No Groups", message: "You don't have any groups yet. Tap the + button to create your first group!")
                    }
                }
            } catch {
                await MainActor.run {
                    print("❌ Failed to load groups: \(error)")
                    self.refreshControl.endRefreshing()
                    self.activityIndicator.stopAnimating()
                    self.isLoading = false
                    self.showAlert(title: "Error", message: "Failed to load groups. Please try again.")
                }
            }
        }
    }
    
    private func showAlert(title: String, message: String) {
        let alert = UIAlertController(title: title, message: message, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "OK", style: .default))
        present(alert, animated: true)
    }
}

extension GroupsViewController: UITableViewDataSource {
    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        print("📊 Table view asking for \(groups.count) rows")
        return groups.count
    }
    
    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: "GroupCell", for: indexPath)
        let group = groups[indexPath.row]
        
        cell.textLabel?.text = group.name
        cell.detailTextLabel?.text = group.description ?? "Created: \(group.created_at)"
        cell.accessoryType = .disclosureIndicator
        
        print("📱 Configuring cell for group: \(group.name) - \(group.description ?? "no description")")
        return cell
    }
    
    func tableView(_ tableView: UITableView, titleForHeaderInSection section: Int) -> String? {
        if groups.isEmpty {
            return "No Groups Found"
        }
        return nil
    }
}

extension GroupsViewController: UITableViewDelegate {
    func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        tableView.deselectRow(at: indexPath, animated: true)
        
        let group = groups[indexPath.row]
        showGroupDetails(groupId: group.id)
    }
    
    private func showGroupDetails(groupId: String) {
        Task {
            do {
                let groupDetail = try await NetworkManager.shared.getGroupDetails(groupId: groupId)
                
                await MainActor.run {
                    let detailVC = GroupDetailViewController(groupDetail: groupDetail)
                    self.navigationController?.pushViewController(detailVC, animated: true)
                }
            } catch {
                await MainActor.run {
                    self.showAlert(title: "Error", message: "Failed to load group details. Please try again.")
                }
            }
        }
    }
} 